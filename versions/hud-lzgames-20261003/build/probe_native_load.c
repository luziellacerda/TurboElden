/* Loadability probe only: does not initialize an emulator or open app data. */
#include <dlfcn.h>
#include <stdio.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fputs("usage: station_native_load_probe <absolute-library-path> ...\n", stderr);
        return 2;
    }
    int failures = 0;
    for (int i = 1; i < argc; ++i) {
        dlerror();
        void *handle = dlopen(argv[i], RTLD_NOW | RTLD_LOCAL);
        if (!handle) {
            const char *error = dlerror();
            fprintf(stderr, "FAIL library %d: %s\n", i, error ? error : "dlopen returned null");
            ++failures;
            continue;
        }
        dlerror();
        void *entry = dlsym(handle, "ANativeActivity_onCreate");
        const char *error = dlerror();
        if (error || !entry) {
            fprintf(stderr, "FAIL library %d entry: %s\n", i, error ? error : "null entry point");
            ++failures;
        } else {
            printf("PASS library %d: RTLD_NOW resolved and ANativeActivity_onCreate exists\n", i);
        }
        if (dlclose(handle)) {
            error = dlerror();
            fprintf(stderr, "FAIL library %d unload: %s\n", i, error ? error : "dlclose failed");
            ++failures;
        }
    }
    printf("RESULT libraries=%d failures=%d (loadability only; no emulator initialized)\n", argc - 1, failures);
    return failures ? 1 : 0;
}
