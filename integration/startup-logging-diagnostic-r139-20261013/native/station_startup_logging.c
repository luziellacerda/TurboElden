/* SPDX-License-Identifier: GPL-3.0-or-later */
/* Diagnostic-only bridge to the already loaded, unchanged R139 runtime. */
#define _GNU_SOURCE 1
#include <jni.h>
#include <android/log.h>
#include <dlfcn.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define STATION_LOG_TAG "StationStartupDiagnostics"
#define STATION_RUNTIME_NAME "/libstation_retroarch.so"
#define STATION_PATH_LIMIT 4096U

typedef void (*station_void_fn)(void);
typedef bool (*station_enabled_fn)(void);
typedef void (*station_level_fn)(unsigned);

static void station_diagnostic(const char *stage, const char *category)
{
   /* Both arguments are fixed labels from this source, never runtime input. */
   __android_log_print(ANDROID_LOG_INFO, STATION_LOG_TAG,
         "stage=%s category=%s", stage, category);
}

static bool station_runtime_path_valid(const char *path)
{
   const char *component;
   const char *cursor;
   size_t length;
   const size_t suffix = sizeof(STATION_RUNTIME_NAME) - 1U;

   if (!path || path[0] != '/')
      return false;
   length = strlen(path);
   if (length <= suffix || length >= STATION_PATH_LIMIT
         || strcmp(path + length - suffix, STATION_RUNTIME_NAME) != 0)
      return false;

   component = path + 1;
   for (cursor = component; ; ++cursor)
   {
      unsigned char value = (unsigned char)*cursor;
      if (value && (value < 32U || value == 127U || value == '\\'))
         return false;
      /* A Java embedded NUL is represented by modified UTF-8 C0 80. */
      if (value == 0xc0U && (unsigned char)cursor[1] == 0x80U)
         return false;
      if (value == '/' || value == 0U)
      {
         size_t size = (size_t)(cursor - component);
         if (!size || (size == 1U && component[0] == '.')
               || (size == 2U && component[0] == '.' && component[1] == '.'))
            return false;
         if (!value)
            break;
         component = cursor + 1;
      }
   }
   return true;
}

static bool station_symbol_from_runtime(void *symbol, const char *path)
{
   Dl_info info;
   memset(&info, 0, sizeof(info));
   return symbol && dladdr(symbol, &info) != 0 && info.dli_fname
      && strcmp(info.dli_fname, path) == 0;
}

JNIEXPORT jboolean JNICALL
Java_org_emulationstation_frontend_netplay_StationStartupLogging_enable(
      JNIEnv *env, jclass type, jstring exactRuntimePath)
{
   const char *path = NULL;
   void *handle = NULL;
   void *enable_symbol;
   void *enabled_symbol;
   void *level_symbol;
   jboolean result = JNI_FALSE;
   (void)type;

   if (!exactRuntimePath)
   {
      station_diagnostic("resolve", "PATH_MISSING");
      return JNI_FALSE;
   }
   path = (*env)->GetStringUTFChars(env, exactRuntimePath, NULL);
   if (!path)
   {
      /* A failed optional diagnostic must not throw into the game launch. */
      if ((*env)->ExceptionCheck(env))
         (*env)->ExceptionClear(env);
      station_diagnostic("resolve", "JAVA_STRING_UNAVAILABLE");
      return JNI_FALSE;
   }
   if (!station_runtime_path_valid(path))
   {
      station_diagnostic("resolve", "PATH_INVALID");
      goto cleanup;
   }

   /* Never load a second runtime or search a basename/default namespace. */
   handle = dlopen(path, RTLD_NOLOAD | RTLD_NOW);
   if (!handle)
   {
      station_diagnostic("resolve", "RUNTIME_NOT_LOADED");
      goto cleanup;
   }
   enable_symbol = dlsym(handle, "verbosity_enable");
   enabled_symbol = dlsym(handle, "verbosity_is_enabled");
   level_symbol = dlsym(handle, "verbosity_set_log_level");
   if (!enable_symbol || !enabled_symbol || !level_symbol)
   {
      station_diagnostic("resolve", "EXPORT_MISSING");
      goto cleanup;
   }
   if (!station_symbol_from_runtime(enable_symbol, path)
         || !station_symbol_from_runtime(enabled_symbol, path)
         || !station_symbol_from_runtime(level_symbol, path))
   {
      station_diagnostic("resolve", "SYMBOL_ORIGIN_MISMATCH");
      goto cleanup;
   }

   /* Before NativeActivity starts its worker: INFO exposes pre-config errors. */
   ((station_level_fn)level_symbol)(1U);
   ((station_void_fn)enable_symbol)();
   if (!((station_enabled_fn)enabled_symbol)())
   {
      station_diagnostic("enable", "VERIFY_FAILED");
      goto cleanup;
   }
   station_diagnostic("enable", "INFO_ENABLED");
   result = JNI_TRUE;

cleanup:
   /* Release only this RTLD_NOLOAD reference after all function calls finish. */
   if (handle && dlclose(handle) != 0)
   {
      station_diagnostic("release", "REFERENCE_CLOSE_FAILED");
      result = JNI_FALSE;
   }
   (*env)->ReleaseStringUTFChars(env, exactRuntimePath, path);
   return result;
}
