/* Separate local probe: exactly 120 frames, zero input, memory-only serialization. */
#define _POSIX_C_SOURCE 200809L
#include <dlfcn.h>
#include <errno.h>
#include <inttypes.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include "libretro.h"

/* Not present in this old pinned header, but used by newer cores. */
#ifndef RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE
#define RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE (47 | 0x10000)
#endif
#ifndef RETRO_ENVIRONMENT_GET_INPUT_BITMASKS
#define RETRO_ENVIRONMENT_GET_INPUT_BITMASKS (51 | 0x10000)
#endif

struct variable_entry { char *key; char *value; };
static struct variable_entry variables[64];
static size_t variable_count;
static const char *system_dir;
static const char *chip_mode;
static const char *violate_accuracy = "disabled";
static unsigned log_counts[4], firmware_errors;
static bool supports_no_game;
static unsigned video_calls, video_data_calls, video_width, video_height, run_calls;
static uint64_t audio_frames, input_polls;
static const unsigned frame_limit = 120;

static const char *firmware_names[] = {
    "dsp1b.program.rom", "dsp1b.data.rom", "dsp1.program.rom", "dsp1.data.rom",
    "dsp2.program.rom", "dsp2.data.rom", "dsp3.program.rom", "dsp3.data.rom",
    "dsp4.program.rom", "dsp4.data.rom", "st010.program.rom", "st010.data.rom",
    "st011.program.rom", "st011.data.rom", "st018.program.rom", "st018.data.rom",
    "st018.boot.rom", "cx4.data.rom", "ipl.rom"
};

static void core_log(enum retro_log_level level, const char *format, ...) {
    char buffer[8192];
    size_t i;
    va_list args;
    if ((unsigned)level < 4) ++log_counts[level];
    va_start(args, format);
    (void)vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    /* Never echo full core messages: they may contain private absolute paths. */
    for (i = 0; i < sizeof(firmware_names) / sizeof(firmware_names[0]); ++i) {
        if (strstr(buffer, firmware_names[i])) {
            printf("core-firmware level=%u name=%s\n", (unsigned)level, firmware_names[i]);
            if (level == RETRO_LOG_ERROR) ++firmware_errors;
        }
    }
}

static bool set_variables(const struct retro_variable *vars) {
    size_t i;
    for (i = 0; vars && vars[i].key; ++i) {
        const char *start, *end;
        size_t length;
        struct variable_entry *entry;
        if (variable_count == 64 || !vars[i].value) return false;
        start = strchr(vars[i].value, ';');
        if (!start) return false;
        ++start;
        while (*start == ' ') ++start;
        end = strchr(start, '|');
        length = end ? (size_t)(end - start) : strlen(start);
        entry = &variables[variable_count];
        entry->key = strdup(vars[i].key);
        entry->value = malloc(length + 1);
        if (!entry->key || !entry->value) return false;
        memcpy(entry->value, start, length);
        entry->value[length] = '\0';
        ++variable_count;
    }
    return true;
}

static bool environment(unsigned command, void *data) {
    size_t i;
    switch (command) {
    case RETRO_ENVIRONMENT_SET_VARIABLES:
        return set_variables((const struct retro_variable *)data);
    case RETRO_ENVIRONMENT_GET_VARIABLE: {
        struct retro_variable *var = data;
        if (!var || !var->key) return false;
        if (!strcmp(var->key, "bsnes_chip_hle")) { var->value = chip_mode; return true; }
        if (!strcmp(var->key, "bsnes_violate_accuracy")) { var->value = violate_accuracy; return true; }
        for (i = 0; i < variable_count; ++i) {
            if (!strcmp(var->key, variables[i].key)) { var->value = variables[i].value; return true; }
        }
        var->value = NULL;
        return false;
    }
    case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:
        *(bool *)data = false; return true;
    case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY:
    case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY:
        *(const char **)data = system_dir; return true;
    case RETRO_ENVIRONMENT_GET_LOG_INTERFACE:
        ((struct retro_log_callback *)data)->log = core_log; return true;
    case RETRO_ENVIRONMENT_GET_CAN_DUPE:
        *(bool *)data = true; return true;
    case RETRO_ENVIRONMENT_GET_LANGUAGE:
        *(unsigned *)data = 0; return true;
    case RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE:
        *(int *)data = 3; return true;
    case RETRO_ENVIRONMENT_GET_INPUT_BITMASKS:
        return false;
    case RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME:
        supports_no_game = *(bool *)data; return true;
    case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT:
        return *(enum retro_pixel_format *)data <= RETRO_PIXEL_FORMAT_RGB565;
    case RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS:
    case RETRO_ENVIRONMENT_SET_CONTROLLER_INFO:
    case RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO:
    case RETRO_ENVIRONMENT_SET_MEMORY_MAPS:
    case RETRO_ENVIRONMENT_SET_GEOMETRY:
        return true;
    default:
        return false;
    }
}

static void video(const void *data, unsigned width, unsigned height, size_t pitch) {
    (void)pitch;
    ++video_calls;
    if (data) ++video_data_calls;
    video_width = width; video_height = height;
}
static void audio_sample(int16_t left, int16_t right) { (void)left; (void)right; ++audio_frames; }
static size_t audio_batch(const int16_t *data, size_t frames) { (void)data; audio_frames += frames; return frames; }
static void input_poll(void) { ++input_polls; }
static uint64_t fnv1a64(const void *data, size_t length) {
    const uint8_t *bytes = data;
    uint64_t value = UINT64_C(14695981039346656037);
    size_t i;
    for (i = 0; i < length; ++i) { value ^= bytes[i]; value *= UINT64_C(1099511628211); }
    return value;
}
static int16_t input_state(unsigned port, unsigned device, unsigned index, unsigned id) {
    (void)port; (void)device; (void)index; (void)id; return 0;
}

static bool read_content(const char *path, void **bytes, size_t *length) {
    struct stat st;
    FILE *file;
    void *data;
    if (stat(path, &st) || !S_ISREG(st.st_mode) || st.st_size <= 0 || st.st_size > 64 * 1024 * 1024)
        return false;
    file = fopen(path, "rb");
    if (!file) return false;
    data = malloc((size_t)st.st_size);
    if (!data) { fclose(file); return false; }
    if (fread(data, 1, (size_t)st.st_size, file) != (size_t)st.st_size) {
        free(data); fclose(file); return false;
    }
    if (fclose(file)) { free(data); return false; }
    *bytes = data; *length = (size_t)st.st_size;
    return true;
}

#define LOAD_SYMBOL(variable, name) do { \
    void *address = dlsym(handle, name); \
    if (!address) { printf("probe-error missing-symbol=%s\n", name); goto cleanup; } \
    memcpy(&(variable), &address, sizeof(variable)); \
} while (0)

int main(int argc, char **argv) {
    void *handle = NULL, *content = NULL, *state_bytes = NULL;
    size_t content_size = 0, state_size = 0, i;
    bool serialized = false;
    uint64_t state_checksum = 0;
    char *synthetic_path = NULL;
    struct stat st;
    struct retro_system_info system_info = {0};
    struct retro_game_info game_info = {0};
    bool initialized = false, loaded = false;
    int result = 2;
    void (*set_environment)(retro_environment_t) = NULL;
    void (*set_video)(retro_video_refresh_t) = NULL;
    void (*set_audio)(retro_audio_sample_t) = NULL;
    void (*set_batch)(retro_audio_sample_batch_t) = NULL;
    void (*set_poll)(retro_input_poll_t) = NULL;
    void (*set_state)(retro_input_state_t) = NULL;
    void (*get_system_info)(struct retro_system_info *) = NULL;
    void (*initialize)(void) = NULL;
    bool (*load_game)(const struct retro_game_info *) = NULL;
    void (*unload_game)(void) = NULL;
    void (*deinitialize)(void) = NULL;
    void (*run_frame)(void) = NULL;
    size_t (*serialize_size)(void) = NULL;
    bool (*serialize_state)(void *, size_t) = NULL;

    setvbuf(stdout, NULL, _IONBF, 0);
    if ((argc != 5 && argc != 6) || (strcmp(argv[4], "LLE") && strcmp(argv[4], "HLE")) ||
        (argc == 6 && strcmp(argv[5], "enabled") && strcmp(argv[5], "disabled"))) {
        puts("usage: native-core-frame-probe CORE_PATH ROM_PATH EMPTY_SYSTEM_DIR LLE|HLE [disabled|enabled]"); return 2;
    }
    chip_mode = argv[4]; system_dir = argv[3];
    if (argc == 6) violate_accuracy = argv[5];
    if (stat(system_dir, &st) || !S_ISDIR(st.st_mode)) {
        puts("probe-error system-directory-unavailable"); return 2;
    }
    if (!read_content(argv[2], &content, &content_size)) {
        puts("probe-error content-read-failed"); return 2;
    }
    synthetic_path = malloc(strlen(system_dir) + sizeof("/probe-content.sfc"));
    if (!synthetic_path) goto cleanup;
    sprintf(synthetic_path, "%s/probe-content.sfc", system_dir);
    printf("probe-start mode=%s violate-accuracy=%s content-bytes=%zu isolated-content-path=true run-frames=120\n", chip_mode, violate_accuracy, content_size);
    handle = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!handle) { puts("probe-error core-open-failed"); goto cleanup; }
    LOAD_SYMBOL(set_environment, "retro_set_environment");
    LOAD_SYMBOL(set_video, "retro_set_video_refresh");
    LOAD_SYMBOL(set_audio, "retro_set_audio_sample");
    LOAD_SYMBOL(set_batch, "retro_set_audio_sample_batch");
    LOAD_SYMBOL(set_poll, "retro_set_input_poll");
    LOAD_SYMBOL(set_state, "retro_set_input_state");
    LOAD_SYMBOL(get_system_info, "retro_get_system_info");
    LOAD_SYMBOL(initialize, "retro_init");
    LOAD_SYMBOL(load_game, "retro_load_game");
    LOAD_SYMBOL(unload_game, "retro_unload_game");
    LOAD_SYMBOL(deinitialize, "retro_deinit");
    LOAD_SYMBOL(run_frame, "retro_run");
    LOAD_SYMBOL(serialize_size, "retro_serialize_size");
    LOAD_SYMBOL(serialize_state, "retro_serialize");
    set_environment(environment);
    set_video(video); set_audio(audio_sample); set_batch(audio_batch);
    set_poll(input_poll); set_state(input_state);
    get_system_info(&system_info);
    if (system_info.need_fullpath) { puts("probe-error fullpath-core-not-supported"); goto cleanup; }
    initialize(); initialized = true;
    game_info.path = synthetic_path; game_info.data = content; game_info.size = content_size;
    loaded = load_game(&game_info);
    printf("probe-result mode=%s violate-accuracy=%s loaded=%s firmware-errors=%u log-debug=%u log-info=%u log-warn=%u log-error=%u supports-no-game=%s\n",
        chip_mode, violate_accuracy, loaded ? "true" : "false", firmware_errors,
        log_counts[0], log_counts[1], log_counts[2], log_counts[3], supports_no_game ? "true" : "false");
    if (loaded) {
        for (i = 0; i < frame_limit; ++i) { run_frame(); ++run_calls; }
        state_size = serialize_size();
        if (state_size > 0 && state_size <= 64 * 1024 * 1024) {
            state_bytes = calloc(1, state_size);
            if (state_bytes) serialized = serialize_state(state_bytes, state_size);
            if (serialized) state_checksum = fnv1a64(state_bytes, state_size);
        }
    }
    printf("frame-probe-result mode=%s violate-accuracy=%s loaded=%s run-calls=%u video-calls=%u video-data-calls=%u width=%u height=%u audio-frames=%" PRIu64 " input-polls=%" PRIu64 " input-state=zero serialized=%s state-bytes=%zu state-fnv1a64=%016" PRIx64 " firmware-errors=%u core-errors=%u\n",
        chip_mode, violate_accuracy, loaded ? "true" : "false", run_calls,
        video_calls, video_data_calls, video_width, video_height, audio_frames, input_polls,
        serialized ? "true" : "false", state_size, state_checksum, firmware_errors, log_counts[3]);
    result = !loaded ? 1 : (serialized && video_data_calls && audio_frames && !log_counts[3] ? 0 : 3);

cleanup:
    if (loaded) unload_game();
    if (initialized) deinitialize();
    if (handle) dlclose(handle);
    for (i = 0; i < variable_count; ++i) { free(variables[i].key); free(variables[i].value); }
    free(state_bytes); free(synthetic_path); free(content);
    return result;
}
