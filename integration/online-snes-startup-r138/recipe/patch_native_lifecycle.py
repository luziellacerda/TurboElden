"""Derive the lifecycle patch from the exact installed five-player runtime source."""
from pathlib import Path
import argparse
import hashlib
import json
import re

BASELINE_SHA256 = 'baa00df315ba604e1ac5612e2186a685c27b843c20bcaea2f27c6a4036f7e7db'
CORRESPONDING_ARCHIVE_SHA256 = 'b8f7649a5edacbe9e913d5e50f66482c0aa082fbd2237f5fd7800d00723b735a'
INSTALLED_RUNTIME_SHA256 = '81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc'
ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def function_span(text, name):
    pattern = re.compile(r'^static [^\n]*\b' + re.escape(name) + r'\([^;]*?\)\s*\{', re.M)
    match = pattern.search(text)
    if match is None:
        raise ValueError('Missing function definition: ' + name)
    opening = text.index('{', match.start())
    cursor, depth = opening + 1, 1
    while depth:
        depth += (text[cursor] == '{') - (text[cursor] == '}')
        cursor += 1
    return match.start(), cursor


ENTRY = '''static void android_app_entry(void *data)
{
   char arguments[]  = "retroarch";
   char      *argv[] = {arguments,   NULL};
   int          argc = 1;
   int result;

   result = rarch_main(argc, argv, data);
   /* Only a redacted integer result is logged; no content or room identity. */
   __android_log_print(ANDROID_LOG_INFO, "StationNative",
         "runloop-return result=%d", result);
   /* rarch_main may return before frontend deinit when content init fails.
    * android_app_free joins this worker before freeing data. */
   android_app_destroy((struct android_app*)data);
}'''

DESTROY = '''static void android_app_destroy(struct android_app *android_app)
{
   JNIEnv *env = NULL;

   if (!android_app)
      return;
   free_saved_state(android_app);

   slock_lock(android_app->mutex);
   /* The normal frontend deinit and the entry fallback share one cleanup. */
   if (android_app->destroyed)
   {
      slock_unlock(android_app->mutex);
      return;
   }

   env = jni_thread_getenv();

   if (env && android_app->onRetroArchExit)
      CALL_VOID_METHOD(env, android_app->activity->clazz,
            android_app->onRetroArchExit);

#ifdef HAVE_SAF
   if (android_app->have_saf)
      retro_vfs_deinit_saf();
#endif

   if (android_app->inputQueue)
      AInputQueue_detachLooper(android_app->inputQueue);
   android_app->inputQueue = NULL;

   if (android_app->config)
      AConfiguration_delete(android_app->config);
   android_app->config = NULL;
   /* Quit requests hold this same mutex. Clear the borrowed pointer before
    * the worker returns and Android releases its thread-owned looper. */
   android_app->looper = NULL;
   android_app->destroyed = 1;
   scond_broadcast(android_app->cond);
   slock_unlock(android_app->mutex);
   /* data stays allocated until android_app_free joins this worker. */
}'''


def patch_bytes(baseline):
    if digest(baseline) != BASELINE_SHA256:
        raise ValueError('Exact installed five-player source SHA256 mismatch')
    text = baseline.decode('utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    replacements = [('android_app_entry', ENTRY), ('android_app_destroy', DESTROY)]
    spans = []
    for name, replacement in replacements:
        start, end = function_span(text, name)
        spans.append((start, end, replacement.replace('\n', newline), name))
    out = text
    for start, end, replacement, name in sorted(spans, reverse=True):
        out = out[:start] + replacement + out[end:]
    entry_start, _ = function_span(out, 'android_app_entry')
    declaration = 'static void android_app_destroy(struct android_app *android_app);' + newline + newline
    out = out[:entry_start] + declaration + out[entry_start:]

    # Reverse the two function changes and declaration, proving all other bytes.
    projection = out.replace(declaration, '', 1)
    for name, _ in replacements:
        a, b = function_span(projection, name)
        old_a, old_b = function_span(text, name)
        projection = projection[:a] + text[old_a:old_b] + projection[b:]
    if projection != text:
        raise ValueError('Change escaped the two lifecycle functions/declaration')
    return out.encode('utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    baseline = args.baseline.read_bytes()
    if args.archive and digest(args.archive.read_bytes()) != CORRESPONDING_ARCHIVE_SHA256:
        raise ValueError('Installed corresponding-source archive SHA256 mismatch')
    candidate = patch_bytes(baseline)
    output = ROOT / 'native/source/frontend/drivers/platform_unix.c'
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.read_bytes() != candidate:
        raise ValueError('Refusing to replace unexpected existing candidate source')
    output.write_bytes(candidate)
    report = {
        'schemaVersion': 1,
        'baselinePlatformUnixSHA256': digest(baseline),
        'candidatePlatformUnixSHA256': digest(candidate),
        'installedRuntimeSHA256': INSTALLED_RUNTIME_SHA256,
        'correspondingArchiveSHA256': CORRESPONDING_ARCHIVE_SHA256,
        'archiveVerified': bool(args.archive),
        'changedFunctions': ['android_app_entry', 'android_app_destroy'],
        'addedForwardDeclaration': 'android_app_destroy',
        'allOtherSourceBytesPreserved': True,
        'playerCapacityChanged': False,
        'readinessOrProtocolChanged': False,
        'fullNativeCompiled': False,
        'androidExecuted': False,
        'gameplayValidated': False,
    }
    receipt = ROOT / 'native/lifecycle-source.json'
    receipt.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
