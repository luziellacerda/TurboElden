"""Create a separate bounded frame probe without altering the load-only probe."""
from pathlib import Path
import argparse
import hashlib

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=ROOT / 'native-core-probe.c')
parser.add_argument('--output', type=Path, default=ROOT / 'native-core-frame-probe.c')
args = parser.parse_args()
base = args.source
original = base.read_bytes()
expected = 'f0c04ab0f65ce5f4baca4498ecf717b86e2aeb856a125cf079a49c241c53ed1c'
if hashlib.sha256(original).hexdigest() != expected:
    raise ValueError('Unexpected load-only probe source')
text = original.decode('utf-8')


def replace(old, new):
    global text
    if text.count(old) != 1:
        raise ValueError('Replacement is not unique: ' + old[:70])
    text = text.replace(old, new)


replace('/* Local load-only probe. This program never runs a frame or writes a save. */',
        '/* Separate local probe: exactly 120 frames, zero input, memory-only serialization. */')
replace('static bool supports_no_game;', '''static bool supports_no_game;
static unsigned video_calls, video_data_calls, video_width, video_height, run_calls;
static uint64_t audio_frames, input_polls;
static const unsigned frame_limit = 120;''')
replace('''static void video(const void *data, unsigned width, unsigned height, size_t pitch) {
    (void)data; (void)width; (void)height; (void)pitch;
}
static void audio_sample(int16_t left, int16_t right) { (void)left; (void)right; }
static size_t audio_batch(const int16_t *data, size_t frames) { (void)data; return frames; }
static void input_poll(void) {}''', '''static void video(const void *data, unsigned width, unsigned height, size_t pitch) {
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
}''')
replace('''    void *handle = NULL, *content = NULL;
    size_t content_size = 0, i;''', '''    void *handle = NULL, *content = NULL, *state_bytes = NULL;
    size_t content_size = 0, state_size = 0, i;
    bool serialized = false;
    uint64_t state_checksum = 0;''')
replace('''    void (*deinitialize)(void) = NULL;''', '''    void (*deinitialize)(void) = NULL;
    void (*run_frame)(void) = NULL;
    size_t (*serialize_size)(void) = NULL;
    bool (*serialize_state)(void *, size_t) = NULL;''')
replace('usage: native-core-probe CORE_PATH ROM_PATH EMPTY_SYSTEM_DIR LLE|HLE [disabled|enabled]',
        'usage: native-core-frame-probe CORE_PATH ROM_PATH EMPTY_SYSTEM_DIR LLE|HLE [disabled|enabled]')
replace('isolated-content-path=true run-frames=0\\n', 'isolated-content-path=true run-frames=120\\n')
replace('''    LOAD_SYMBOL(deinitialize, "retro_deinit");''', '''    LOAD_SYMBOL(deinitialize, "retro_deinit");
    LOAD_SYMBOL(run_frame, "retro_run");
    LOAD_SYMBOL(serialize_size, "retro_serialize_size");
    LOAD_SYMBOL(serialize_state, "retro_serialize");''')
replace('''    result = loaded ? 0 : 1;

cleanup:''', '''    if (loaded) {
        for (i = 0; i < frame_limit; ++i) { run_frame(); ++run_calls; }
        state_size = serialize_size();
        if (state_size > 0 && state_size <= 64 * 1024 * 1024) {
            state_bytes = calloc(1, state_size);
            if (state_bytes) serialized = serialize_state(state_bytes, state_size);
            if (serialized) state_checksum = fnv1a64(state_bytes, state_size);
        }
    }
    printf("frame-probe-result mode=%s violate-accuracy=%s loaded=%s run-calls=%u video-calls=%u video-data-calls=%u width=%u height=%u audio-frames=%" PRIu64 " input-polls=%" PRIu64 " input-state=zero serialized=%s state-bytes=%zu state-fnv1a64=%016" PRIx64 " firmware-errors=%u core-errors=%u\\n",
        chip_mode, violate_accuracy, loaded ? "true" : "false", run_calls,
        video_calls, video_data_calls, video_width, video_height, audio_frames, input_polls,
        serialized ? "true" : "false", state_size, state_checksum, firmware_errors, log_counts[3]);
    result = !loaded ? 1 : (serialized && video_data_calls && audio_frames && !log_counts[3] ? 0 : 3);

cleanup:''')
replace('''    free(synthetic_path); free(content);''', '''    free(state_bytes); free(synthetic_path); free(content);''')
output = args.output
candidate = text.encode('utf-8')
if output.exists() and output.read_bytes() != candidate:
    raise ValueError('Refusing to replace an unexpected existing frame probe')
output.write_bytes(candidate)
if base.read_bytes() != original:
    raise ValueError('Load-only probe was unexpectedly changed')
print('frameProbeSourceSHA256=' + hashlib.sha256(candidate).hexdigest())
