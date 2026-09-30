/* Bind the relocated AndroidX counter class to the unchanged upstream JNI.
 * The donor exports Java_androidx_* names. ELF symbol names/hash tables are
 * intentionally left untouched. Registration runs in :wiiu only, on demand.
 */
#include <jni.h>
#include <dlfcn.h>
#include <android/log.h>

static void *counter_library;

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved) {
    (void)reserved;
    JNIEnv *env = 0;
    if ((*vm)->GetEnv(vm, (void **)&env, JNI_VERSION_1_6) != JNI_OK)
        return JNI_ERR;

    counter_library = dlopen("libwiiustore_shared_counter.so", RTLD_NOW | RTLD_LOCAL);
    if (!counter_library) {
        __android_log_print(ANDROID_LOG_ERROR, "TurboWiiU",
                            "Counter bridge dlopen failed: %s", dlerror());
        return JNI_ERR;
    }

    JNINativeMethod methods[] = {
        {"nativeCreateSharedCounter", "(I)J", 0},
        {"nativeGetCounterValue", "(J)I", 0},
        {"nativeIncrementAndGetCounterValue", "(J)I", 0},
        {"nativeTruncateFile", "(I)I", 0}
    };
    const char *symbols[] = {
        "Java_androidx_datastore_core_NativeSharedCounter_nativeCreateSharedCounter",
        "Java_androidx_datastore_core_NativeSharedCounter_nativeGetCounterValue",
        "Java_androidx_datastore_core_NativeSharedCounter_nativeIncrementAndGetCounterValue",
        "Java_androidx_datastore_core_NativeSharedCounter_nativeTruncateFile"
    };
    for (unsigned int i = 0; i < sizeof(methods) / sizeof(methods[0]); ++i) {
        dlerror();
        methods[i].fnPtr = dlsym(counter_library, symbols[i]);
        const char *error = dlerror();
        if (error || !methods[i].fnPtr) {
            __android_log_print(ANDROID_LOG_ERROR, "TurboWiiU",
                                "Counter bridge symbol missing: %s (%s)",
                                symbols[i], error ? error : "null address");
            return JNI_ERR;
        }
    }

    jclass cls = (*env)->FindClass(env, "twiiucor/datastore/core/NativeSharedCounter");
    if (!cls) return JNI_ERR;
    jint result = (*env)->RegisterNatives(env, cls, methods,
                                        sizeof(methods) / sizeof(methods[0]));
    (*env)->DeleteLocalRef(env, cls);
    if (result != JNI_OK) return JNI_ERR;

    /* Keep the donor loaded for the lifetime of registered function pointers. */
    __android_log_print(ANDROID_LOG_INFO, "TurboWiiU",
                        "Counter bridge registered 4 relocated DataStore methods");
    return JNI_VERSION_1_6;
}
