#define _GNU_SOURCE
#include <jni.h>
#include <archive.h>
#include <archive_entry.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_TOTAL (32ULL * 1024 * 1024 * 1024)
#define RESERVE (256ULL * 1024 * 1024)
#define MAX_ENTRIES 200000
#define PATH_CAP 4096
#define CHUNK (128 * 1024)
#define MAX_SECONDS (2 * 60 * 60)

typedef struct {
    JNIEnv *env;
    jobject callback;
    jmethodID cancel, progress;
    uint64_t started;
    int percent;
} Callback;

static uint64_t seconds_now(void) {
    struct timespec time;
    if (clock_gettime(CLOCK_MONOTONIC, &time) != 0) return 0;
    return (uint64_t) time.tv_sec;
}

static int cancelled(Callback *cb, char *error, size_t size) {
    if ((*cb->env)->ExceptionCheck(cb->env)) return 1;
    if ((*cb->env)->CallBooleanMethod(cb->env, cb->callback, cb->cancel)) {
        snprintf(error, size, "Preparação cancelada. O download original foi preservado."); return 1;
    }
    if ((*cb->env)->ExceptionCheck(cb->env)) return 1;
    if (seconds_now() - cb->started > MAX_SECONDS) {
        snprintf(error, size, "A preparação excedeu o limite de duas horas. Verifique o pacote Wii U."); return 1;
    }
    return 0;
}

static void notify(Callback *cb, struct archive *archive, uint64_t source_size) {
    la_int64_t consumed = archive_filter_bytes(archive, -1);
    int percent = consumed > 0 && source_size ? (int) ((uint64_t) consumed * 100 / source_size) : 0;
    if (percent > 99) percent = 99;
    if (percent <= cb->percent) return;
    cb->percent = percent;
    jstring message = (*cb->env)->NewStringUTF(cb->env, "Preparando jogo Wii U");
    if (!message) return;
    (*cb->env)->CallVoidMethod(cb->env, cb->callback, cb->progress, percent, message);
    (*cb->env)->DeleteLocalRef(cb->env, message);
}

/* A canonical relative path with a finite component count; no disk extraction API is used. */
static int clean_name(const char *raw, char out[PATH_CAP]) {
    if (!raw || !*raw || strlen(raw) >= PATH_CAP || raw[0] == '/' || raw[0] == '\\') return 0;
    char copy[PATH_CAP];
    size_t raw_len = strlen(raw);
    for (size_t n = 0; n <= raw_len; ++n) {
        unsigned char c = (unsigned char) raw[n];
        if (c == ':' || (c && c < 32) || c == 127) return 0;
        copy[n] = c == '\\' ? '/' : (char) c;
    }
    out[0] = 0;
    size_t used = 0;
    int depth = 0;
    char *part = copy;
    while (*part) {
        char *slash = strchr(part, '/');
        if (slash) *slash = 0;
        size_t len = strlen(part);
        if (!strcmp(part, "..")) return 0;
        if (len && strcmp(part, ".")) {
            if (++depth > 32 || len > 255 || used + len + 2 >= PATH_CAP) return 0;
            if (used) out[used++] = '/';
            memcpy(out + used, part, len); used += len; out[used] = 0;
        }
        if (!slash) break;
        part = slash + 1;
    }
    return used > 0;
}

/* Every directory is opened beneath an already held fd with O_NOFOLLOW. */
static int open_parent(int root, const char *name, char leaf[256]) {
    char copy[PATH_CAP];
    strcpy(copy, name);
    int current = fcntl(root, F_DUPFD_CLOEXEC, 0);
    if (current < 0) return -1;
    char *part = copy;
    for (;;) {
        char *slash = strchr(part, '/');
        if (!slash) { strcpy(leaf, part); return current; }
        *slash = 0;
        if (mkdirat(current, part, 0700) != 0 && errno != EEXIST) { close(current); return -1; }
        int next = openat(current, part, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        close(current);
        if (next < 0) return -1;
        current = next; part = slash + 1;
    }
}

static int enough_space(int root, uint64_t upcoming) {
    struct statvfs space;
    if (fstatvfs(root, &space) != 0) return 0;
    uint64_t block = (uint64_t) space.f_frsize;
    uint64_t available = block && (uint64_t) space.f_bavail > UINT64_MAX / block
        ? UINT64_MAX : (uint64_t) space.f_bavail * block;
    return upcoming <= MAX_TOTAL && available > RESERVE && upcoming <= available - RESERVE;
}

static int64_t modified_ms(const struct stat *s) {
    return (int64_t) s->st_mtim.tv_sec * 1000 + s->st_mtim.tv_nsec / 1000000;
}

JNIEXPORT jstring JNICALL Java_org_emulationstation_frontend_WiiUArchive_extractRar(
        JNIEnv *env, jclass klass, jstring input, jstring destination,
        jlong expected_size, jlong expected_modified, jobject progress) {
    (void) klass;
    const char *source = NULL, *target = NULL;
    struct archive *reader = NULL;
    struct archive_entry *entry = NULL;
    char error[512] = {0}, name[PATH_CAP], leaf[256];
    void *buffer = NULL;
    int source_fd = -1, root_fd = -1, file_fd = -1, parent_fd = -1;
    int status, entries = 0, files = 0;
    uint64_t declared_total = 0, actual_total = 0, checked_at = 0;
    struct stat original, after;
    jclass callback_class = NULL;
    Callback cb = {.env = env, .callback = progress, .started = seconds_now(), .percent = -1};

    if (!input || !destination || !progress) { snprintf(error, sizeof(error), "Preparação Wii U inválida."); goto done; }
    source = (*env)->GetStringUTFChars(env, input, NULL);
    if (!source) goto done;
    target = (*env)->GetStringUTFChars(env, destination, NULL);
    if (!target) goto done;
    callback_class = (*env)->GetObjectClass(env, progress);
    if (!callback_class) goto done;
    cb.cancel = (*env)->GetMethodID(env, callback_class, "isCancelled", "()Z");
    cb.progress = (*env)->GetMethodID(env, callback_class, "onProgress", "(ILjava/lang/String;)V");
    if (!cb.cancel || !cb.progress || (*env)->ExceptionCheck(env)) goto done;
    if (cancelled(&cb, error, sizeof(error))) goto done;

    source_fd = open(source, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    root_fd = open(target, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (source_fd < 0 || root_fd < 0 || fstat(source_fd, &original) != 0 || !S_ISREG(original.st_mode)) {
        snprintf(error, sizeof(error), "Não foi possível abrir o RAR ou a pasta privada de preparação."); goto done;
    }
    if (original.st_size <= 0 || (uint64_t) original.st_size > MAX_TOTAL || original.st_size != expected_size || modified_ms(&original) != expected_modified) {
        snprintf(error, sizeof(error), "O download Wii U foi alterado ou ainda não terminou."); goto done;
    }
    // A ratio cap supplements the absolute budget. It still permits a heavily padded disc image.
    uint64_t expansion_limit = (uint64_t) original.st_size > MAX_TOTAL / 300
        ? MAX_TOTAL : (uint64_t) original.st_size * 300;
    if (expansion_limit < 1024ULL * 1024 * 1024) expansion_limit = 1024ULL * 1024 * 1024;
    if (!enough_space(root_fd, CHUNK)) {
        snprintf(error, sizeof(error), "Espaço insuficiente. A preparação Wii U preserva pelo menos 256 MiB livres."); goto done;
    }
    reader = archive_read_new();
    if (!reader) { snprintf(error, sizeof(error), "Memória insuficiente para ler o pacote."); goto done; }
    archive_read_support_filter_none(reader);
    archive_read_support_format_rar(reader);
    archive_read_support_format_rar5(reader);
    if (archive_read_open_fd(reader, source_fd, CHUNK) != ARCHIVE_OK) {
        snprintf(error, sizeof(error), "O RAR está incompleto, protegido por senha ou não é suportado."); goto done;
    }
    buffer = malloc(CHUNK);
    if (!buffer) { snprintf(error, sizeof(error), "Memória insuficiente para preparar o jogo."); goto done; }
    while ((status = archive_read_next_header(reader, &entry)) == ARCHIVE_OK) {
        if (cancelled(&cb, error, sizeof(error))) goto done;
        if (++entries > MAX_ENTRIES) {
            snprintf(error, sizeof(error), "O pacote excede o limite de 200.000 entradas."); goto done;
        }
        const char *raw_name = archive_entry_pathname_utf8(entry);
        if (!raw_name) raw_name = archive_entry_pathname(entry);
        if (!clean_name(raw_name, name)) {
            snprintf(error, sizeof(error), "O RAR contém um caminho inválido ou profundo demais."); goto done;
        }
        if (archive_entry_symlink(entry) || archive_entry_hardlink(entry) || archive_entry_is_encrypted(entry) == 1) {
            snprintf(error, sizeof(error), "Links internos e arquivos protegidos por senha não são aceitos."); goto done;
        }
        mode_t type = archive_entry_filetype(entry);
        if (type != AE_IFREG && type != AE_IFDIR) {
            snprintf(error, sizeof(error), "O RAR contém uma entrada especial não permitida."); goto done;
        }
        if (!archive_entry_size_is_set(entry) || archive_entry_size(entry) < 0) {
            snprintf(error, sizeof(error), "O RAR não informa um tamanho seguro para seus arquivos."); goto done;
        }
        uint64_t size = (uint64_t) archive_entry_size(entry);
        if (size > MAX_TOTAL || declared_total > MAX_TOTAL - size || declared_total + size > expansion_limit) {
            snprintf(error, sizeof(error), "O RAR excede o limite de 32 GiB ou o limite seguro de expansão."); goto done;
        }
        declared_total += size;
        if (type == AE_IFDIR && size != 0) {
            snprintf(error, sizeof(error), "O RAR contém uma pasta com dados inválidos."); goto done;
        }
        if (!enough_space(root_fd, size)) {
            snprintf(error, sizeof(error), "Espaço insuficiente para extrair o jogo preservando o download e 256 MiB livres."); goto done;
        }
        parent_fd = open_parent(root_fd, name, leaf);
        if (parent_fd < 0) {
            snprintf(error, sizeof(error), "Não foi possível criar uma pasta segura para o jogo."); goto done;
        }
        if (type == AE_IFDIR) {
            if (mkdirat(parent_fd, leaf, 0700) != 0 && errno != EEXIST) {
                snprintf(error, sizeof(error), "Não foi possível criar uma pasta do jogo."); goto done;
            }
            file_fd = openat(parent_fd, leaf, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
            if (file_fd < 0) { snprintf(error, sizeof(error), "O pacote contém uma pasta inválida."); goto done; }
            close(file_fd); file_fd = -1;
        } else {
            // O_EXCL also refuses colliding/duplicated archive entries, never overwriting prior files.
            file_fd = openat(parent_fd, leaf, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
            if (file_fd < 0) {
                snprintf(error, sizeof(error), "O RAR contém nomes repetidos ou não foi possível gravar o jogo."); goto done;
            }
        }
        close(parent_fd); parent_fd = -1;
        uint64_t file_bytes = 0;
        la_ssize_t n;
        while ((n = archive_read_data(reader, buffer, CHUNK)) > 0) {
            if (cancelled(&cb, error, sizeof(error))) goto done;
            if (type != AE_IFREG || (uint64_t) n > size - file_bytes || (uint64_t) n > MAX_TOTAL - actual_total) {
                snprintf(error, sizeof(error), "Os dados do RAR excedem o tamanho declarado."); goto done;
            }
            if (actual_total - checked_at >= 16ULL * 1024 * 1024) {
                if (!enough_space(root_fd, (uint64_t) n)) {
                    snprintf(error, sizeof(error), "A preparação parou para preservar espaço livre no aparelho."); goto done;
                }
                checked_at = actual_total;
            }
            size_t written = 0;
            while (written < (size_t) n) {
                ssize_t result = write(file_fd, (char *) buffer + written, (size_t) n - written);
                if (result < 0 && errno == EINTR) continue;
                if (result <= 0) {
                    snprintf(error, sizeof(error), "Espaço insuficiente ou erro ao gravar o jogo Wii U."); goto done;
                }
                written += (size_t) result;
            }
            file_bytes += (uint64_t) n; actual_total += (uint64_t) n;
            notify(&cb, reader, (uint64_t) original.st_size);
        }
        if (n < 0 || file_bytes != size) {
            snprintf(error, sizeof(error), "O RAR está incompleto, corrompido, dividido em volumes ou protegido por senha."); goto done;
        }
        if (file_fd >= 0) {
            if (fdatasync(file_fd) != 0) {
                snprintf(error, sizeof(error), "Não foi possível concluir a gravação do jogo."); goto done;
            }
            close(file_fd); file_fd = -1; ++files;
        }
        notify(&cb, reader, (uint64_t) original.st_size);
    }
    if (status != ARCHIVE_EOF || !files || archive_read_has_encrypted_entries(reader) == 1) {
        snprintf(error, sizeof(error), "O RAR está incompleto, vazio ou usa um formato não suportado."); goto done;
    }
    if (fstat(source_fd, &after) != 0 || after.st_size != original.st_size || modified_ms(&after) != modified_ms(&original)) {
        snprintf(error, sizeof(error), "O download foi alterado durante a preparação. Tente novamente após terminar."); goto done;
    }
    if (cancelled(&cb, error, sizeof(error))) goto done;
done:
    if (file_fd >= 0) close(file_fd);
    if (parent_fd >= 0) close(parent_fd);
    if (reader) archive_read_free(reader);
    if (source_fd >= 0) close(source_fd);
    if (root_fd >= 0) close(root_fd);
    free(buffer);
    if (source) (*env)->ReleaseStringUTFChars(env, input, source);
    if (target) (*env)->ReleaseStringUTFChars(env, destination, target);
    if (callback_class) (*env)->DeleteLocalRef(env, callback_class);
    // Java removes the incomplete private stage after all native descriptors are closed.
    if ((*env)->ExceptionCheck(env)) return NULL;
    return error[0] ? (*env)->NewStringUTF(env, error) : NULL;
}
