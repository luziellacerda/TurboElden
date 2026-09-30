/*
 * AndroidX DataStore shared counter integration for relocated Cemu.
 * Derived from AndroidX datastore-core shared_counter.cc and
 * jni/androidx_datastore_core_SharedCounter.cc (Apache License 2.0).
 * https://android.googlesource.com/platform/frameworks/support/+/HEAD/datastore/datastore-core/src/androidMain/cpp/
 */
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>
#include <jni.h>

namespace {
constexpr size_t kCounterBytes = sizeof(uint32_t);
static_assert(sizeof(std::atomic<uint32_t>) == kCounterBytes);
static_assert(std::atomic<uint32_t>::is_always_lock_free);

jint ThrowIo(JNIEnv* env, int error) {
    jclass type = env->FindClass("java/io/IOException");
    return type ? env->ThrowNew(type, std::strerror(error)) : -1;
}
}

extern "C" JNIEXPORT jint JNICALL
Java_twiiucor_datastore_core_NativeSharedCounter_nativeTruncateFile(
    JNIEnv* env, jobject, jint fd) {
    return ftruncate(fd, kCounterBytes) == 0 ? 0 : ThrowIo(env, errno);
}

extern "C" JNIEXPORT jlong JNICALL
Java_twiiucor_datastore_core_NativeSharedCounter_nativeCreateSharedCounter(
    JNIEnv* env, jobject, jint fd) {
    void* address = mmap(nullptr, kCounterBytes, PROT_READ | PROT_WRITE,
                         MAP_SHARED | MAP_POPULATE, fd, 0);
    if (address == MAP_FAILED) return ThrowIo(env, errno);
    return reinterpret_cast<jlong>(address);
}

extern "C" JNIEXPORT jint JNICALL
Java_twiiucor_datastore_core_NativeSharedCounter_nativeGetCounterValue(
    JNIEnv*, jobject, jlong address) {
    auto* value = reinterpret_cast<std::atomic<uint32_t>*>(address);
    return static_cast<jint>(value->load());
}

extern "C" JNIEXPORT jint JNICALL
Java_twiiucor_datastore_core_NativeSharedCounter_nativeIncrementAndGetCounterValue(
    JNIEnv*, jobject, jlong address) {
    auto* value = reinterpret_cast<std::atomic<uint32_t>*>(address);
    return static_cast<jint>(value->fetch_add(1) + 1);
}
