"""Patch only startup allocations and JNI TLS ownership over the exact R138 source."""
from pathlib import Path
import argparse
import hashlib
import json

BASELINE_SHA256 = 'e4811bef12aeacd07947e51badaf8341be6c12c347c4952a9334ba22e56342f2'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def function_span(text, name):
    import re
    found = list(re.finditer(r'(?m)^(?!\s*(?:if|while|for|switch)\b)[^\n;{}]*\b'+re.escape(name)+r'\([^;{}]*\)\s*\{', text))
    if len(found) != 1:
        raise ValueError('Function is not unique: '+name)
    start = found[0].start()
    brace = text.index('{', found[0].start(), found[0].end())
    depth = 1
    end = brace+1
    while depth:
        if text[end] == '{': depth += 1
        if text[end] == '}': depth -= 1
        end += 1
    return start, end


CREATE = '''static struct android_app* android_app_create(ANativeActivity* activity,
        void* savedState, size_t savedStateSize)
{
   int msgpipe[2] = {-1, -1};
   struct android_app *android_app =
      (struct android_app*)calloc(1, sizeof(*android_app));

   if (!android_app)
   {
      RARCH_ERR("Failed to initialize android_app.\\n");
      return NULL;
   }
   android_app->activity = activity;
   android_app->mutex = slock_new();
   android_app->cond = scond_new();
   if (!android_app->mutex || !android_app->cond)
      goto startup_failed;

   if (savedState && savedStateSize)
   {
      android_app->savedState = malloc(savedStateSize);
      if (!android_app->savedState)
         goto startup_failed;
      android_app->savedStateSize = savedStateSize;
      memcpy(android_app->savedState, savedState, savedStateSize);
   }
   if (pipe(msgpipe))
      goto startup_failed;
   android_app->msgread = msgpipe[0];
   android_app->msgwrite = msgpipe[1];
   android_app->thread = sthread_create(android_app_entry, android_app);
   if (!android_app->thread)
      goto startup_failed;

   /* Preserve the normal handshake with the worker. */
   slock_lock(android_app->mutex);
   while (!android_app->running)
      scond_wait(android_app->cond, android_app->mutex);
   slock_unlock(android_app->mutex);
   return android_app;

startup_failed:
   /* No worker exists on these failure branches. Do not wait or join. */
   if (msgpipe[0] >= 0)
      close(msgpipe[0]);
   if (msgpipe[1] >= 0)
      close(msgpipe[1]);
   free(android_app->savedState);
   scond_free(android_app->cond);
   slock_free(android_app->mutex);
   free(android_app);
   RARCH_ERR("Failed to prepare Android native worker.\\n");
   return NULL;
}'''

TLS_GLOBALS = '''static pthread_key_t thread_key;
/* This library is loaded by the Java class loader for the process lifetime.
 * Never delete/reassign a key while a worker's JNI destructor may still use it. */
static pthread_mutex_t station_jni_key_mutex = PTHREAD_MUTEX_INITIALIZER;
static bool station_jni_key_initialized = false;
static JavaVM *station_jni_vm = NULL;'''

ENSURE = '''static void jni_thread_destruct(void *value);

static bool station_jni_key_ensure(JavaVM *vm)
{
   bool ready = false;
   if (!vm)
      return false;
   pthread_mutex_lock(&station_jni_key_mutex);
   if (station_jni_key_initialized)
      ready = station_jni_vm == vm;
   else if (pthread_key_create(&thread_key, jni_thread_destruct) == 0)
   {
      station_jni_vm = vm;
      station_jni_key_initialized = true;
      ready = true;
   }
   pthread_mutex_unlock(&station_jni_key_mutex);
   return ready;
}

'''

GETENV = '''JNIEnv *jni_thread_getenv(void)
{
   JNIEnv *env = NULL;
   JavaVM *vm;
   pthread_key_t key;
   int status;

   /* Callers still require the active native Activity context. The worker
    * publishes g_android before using JNI and clears it only after join. */
   if (!g_android)
      return NULL;

   /* A separate mutex avoids the Activity -> app cleanup lock order.
    * All VM calls happen after this short snapshot has released its lock. */
   pthread_mutex_lock(&station_jni_key_mutex);
   vm = station_jni_vm;
   if (station_jni_key_initialized)
      key = thread_key;
   else
      vm = NULL;
   pthread_mutex_unlock(&station_jni_key_mutex);
   if (!vm)
      return NULL;

   status = (*vm)->GetEnv(vm, (void**)&env, JNI_VERSION_1_6);
   if (status == JNI_OK)
      return env; /* Do not detach a thread attached by Java or another owner. */
   if (status != JNI_EDETACHED)
   {
      RARCH_ERR("jni_thread_getenv: Failed to query current thread.\\n");
      return NULL;
   }
   status = (*vm)->AttachCurrentThread(vm, &env, 0);
   if (status < 0)
   {
      RARCH_ERR("jni_thread_getenv: Failed to attach current thread.\\n");
      return NULL;
   }
   /* JavaVM lives for the process, unlike Activity/app/another thread's env. */
   if (pthread_setspecific(key, (void*)vm) != 0)
   {
      (*vm)->DetachCurrentThread(vm);
      RARCH_ERR("jni_thread_getenv: Failed to register thread cleanup.\\n");
      return NULL;
   }
   return env;
}'''

DESTRUCT = '''static void jni_thread_destruct(void *value)
{
   JavaVM *vm = (JavaVM*)value;
   /* The TLS implementation clears this thread's value before this callback.
    * Only threads attached by jni_thread_getenv have a registered VM value. */
   if (vm)
      (*vm)->DetachCurrentThread(vm);
}'''


def patch_bytes(data):
    if digest(data) != BASELINE_SHA256:
        raise ValueError('Wrong R138 platform_unix.c source')
    text = data.decode('utf-8')
    newline = '\r\n' if b'\r\n' in data else '\n'
    nl = lambda value: value.replace('\n', newline)
    undo = []
    for name, replacement in [('android_app_create', CREATE),
                              ('jni_thread_getenv', GETENV),
                              ('jni_thread_destruct', DESTRUCT)]:
        a, b = function_span(text, name)
        before = text[a:b]
        after = nl(replacement)
        text = text[:a]+after+text[b:]
        undo.append((after, before))
    anchors = [
        ('static pthread_key_t thread_key;', nl(TLS_GLOBALS)),
        (nl(GETENV), nl(ENSURE)+nl(GETENV)),
        ('   if (pthread_key_create(&thread_key, jni_thread_destruct))'+newline+
         '      RARCH_ERR("Error initializing pthread_key.\\n");',
         nl('''   if (!station_jni_key_ensure(activity->vm))
   {
      RARCH_ERR("Failed to initialize Android JNI thread cleanup.\\n");
      station_activity_release(activity);
      ANativeActivity_finish(activity);
      return;
   }''')),
        ('   if (!activity->instance)'+newline+'      station_activity_release(activity);',
         nl('''   if (!activity->instance)
   {
      station_activity_release(activity);
      ANativeActivity_finish(activity);
   }''')),
    ]
    for before, after in anchors:
        if text.count(before) != 1:
            raise ValueError('Unexpected R138 patch anchor')
        text = text.replace(before, after)
        undo.append((after, before))
    inverse = text
    for after, before in reversed(undo):
        if inverse.count(after) != 1:
            raise ValueError('Patch inverse is ambiguous')
        inverse = inverse.replace(after, before)
    if inverse.encode('utf-8') != data:
        raise ValueError('Unexpected source changes outside the patch')
    return text.encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.baseline = args.baseline.resolve()
    args.output = args.output.resolve()
    overlay = Path(__file__).resolve().parents[1]
    repository = overlay.parents[1]
    if args.output.is_relative_to(repository) and not args.output.is_relative_to(overlay/'native'):
        raise ValueError('Output inside the repository must stay in this new native overlay')
    if args.output.exists():
        raise ValueError('Output must not already exist')
    before = args.baseline.read_bytes()
    after = patch_bytes(before)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(after)
    print(json.dumps(dict(baselineSha256=digest(before), candidateSha256=digest(after),
                         onlyChangedSource='frontend/drivers/platform_unix.c',
                         inversePreservationVerified=True), indent=2))


if __name__ == '__main__':
    main()
