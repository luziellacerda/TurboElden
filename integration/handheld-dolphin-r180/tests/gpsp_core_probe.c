/* Read-only content/core boundary probe. Never linked or packaged into the app. */
#include <dlfcn.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "libretro.h"

static struct retro_netpacket_callback packet;
static const struct retro_core_option_v2_definition *definitions;
static unsigned video_frames, audio_frames, packets;
static const char *directory;

static bool environment(unsigned command, void *data)
{
    switch (command) {
    case RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION: *(unsigned *)data = 2; return true;
    case RETRO_ENVIRONMENT_GET_LANGUAGE: *(unsigned *)data = RETRO_LANGUAGE_ENGLISH; return true;
    case RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2:
        definitions = ((struct retro_core_options_v2 *)data)->definitions; return true;
    case RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2_INTL:
        definitions = ((struct retro_core_options_v2_intl *)data)->us->definitions; return true;
    case RETRO_ENVIRONMENT_GET_VARIABLE: {
        struct retro_variable *variable = data;
        variable->value = NULL;
        if (!strcmp(variable->key, "gpsp_serial")) variable->value = "auto";
        else if (!strcmp(variable->key, "gpsp_rtc_time_source")) variable->value = "deterministic";
        else if (definitions) {
            for (const struct retro_core_option_v2_definition *d = definitions; d->key; ++d)
                if (!strcmp(d->key, variable->key)) { variable->value = d->default_value; break; }
        }
        return variable->value != NULL;
    }
    case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE: *(bool *)data = false; return true;
    case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY:
    case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY: *(const char **)data = directory; return true;
    case RETRO_ENVIRONMENT_GET_CAN_DUPE: *(bool *)data = true; return true;
    case RETRO_ENVIRONMENT_GET_INPUT_BITMASKS: return true;
    case RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE: *(int *)data = 3; return true;
    case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT: return true;
    case RETRO_ENVIRONMENT_SET_NETPACKET_INTERFACE:
        packet = *(struct retro_netpacket_callback *)data; return true;
    default: return false;
    }
}
static void video(const void *pixels, unsigned width, unsigned height, size_t pitch)
{
    if (pixels && width == 240 && height == 160 && pitch >= 480) ++video_frames;
}
static void audio(int16_t left, int16_t right) { (void)left; (void)right; ++audio_frames; }
static size_t audio_batch(const int16_t *samples, size_t count)
{ (void)samples; audio_frames += (unsigned)count; return count; }
static void input_poll(void) {}
static int16_t input_state(unsigned port, unsigned device, unsigned index, unsigned id)
{ (void)port; (void)device; (void)index; (void)id; return 0; }
static void send_packet(int flags, const void *bytes, size_t length, uint16_t client)
{ (void)flags; (void)bytes; (void)length; (void)client; ++packets; }
static void poll_packet(void) {}
static void *required(void *core, const char *name)
{
    void *symbol = dlsym(core, name);
    if (!symbol) { fprintf(stderr, "Missing core ABI symbol: %s\n", name); exit(2); }
    return symbol;
}
#define BIND(result,name,args) result (*name) args = (result (*) args)required(core, #name)

int main(int count, char **arguments)
{
    if (count != 5) return 2;
    directory = arguments[3];
    unsigned maximum = (unsigned)strtoul(arguments[4], NULL, 10);
    if (maximum != 4 && maximum != 32) return 2;
    void *core = dlopen(arguments[1], RTLD_NOW | RTLD_LOCAL);
    if (!core) { fprintf(stderr, "Core load failed: %s\n", dlerror()); return 2; }
    BIND(void, retro_set_environment, (retro_environment_t));
    BIND(void, retro_set_video_refresh, (retro_video_refresh_t));
    BIND(void, retro_set_audio_sample, (retro_audio_sample_t));
    BIND(void, retro_set_audio_sample_batch, (retro_audio_sample_batch_t));
    BIND(void, retro_set_input_poll, (retro_input_poll_t));
    BIND(void, retro_set_input_state, (retro_input_state_t));
    BIND(void, retro_init, (void)); BIND(void, retro_deinit, (void));
    BIND(bool, retro_load_game, (const struct retro_game_info *));
    BIND(void, retro_unload_game, (void)); BIND(void, retro_run, (void));
    BIND(void, retro_get_system_av_info, (struct retro_system_av_info *));
    retro_set_environment(environment); retro_set_video_refresh(video);
    retro_set_audio_sample(audio); retro_set_audio_sample_batch(audio_batch);
    retro_set_input_poll(input_poll); retro_set_input_state(input_state); retro_init();
    FILE *file = fopen(arguments[2], "rb");
    if (!file || fseek(file, 0, SEEK_END)) return 2;
    long size = ftell(file);
    if (size < 192 || size > 33554432 || fseek(file, 0, SEEK_SET)) return 2;
    void *content = malloc((size_t)size);
    if (!content || fread(content, 1, (size_t)size, file) != (size_t)size) return 2;
    fclose(file);
    struct retro_game_info game = {arguments[2], content, (size_t)size, NULL};
    if (!retro_load_game(&game)) { fprintf(stderr, "Exact content refused\n"); return 3; }
    if (!packet.start || !packet.receive || !packet.stop || !packet.connected || !packet.disconnected
        || !packet.protocol_version || strcmp(packet.protocol_version, "gpSP v1.0")) return 3;
    struct retro_system_av_info av;
    retro_get_system_av_info(&av);
    if (av.timing.fps < 59 || av.timing.fps > 60) return 3;
    packet.start(0, send_packet, poll_packet);
    for (unsigned peer = 1; peer < maximum; ++peer)
        if (!packet.connected((uint16_t)peer)) return 4;
    if (packet.connected((uint16_t)maximum)) return 4;
    /* Dispatch invalid lengths to the actual source parser in this isolated
     * process. This is a small boundary check, not a claim of exhaustive fuzzing. */
    uint8_t bytes[257];
    for (size_t length = 0; length <= 256; ++length) {
        memset(bytes, 0xa5, sizeof(bytes));
        packet.receive(bytes, length, 1);
    }
    for (unsigned peer = 1; peer < maximum; ++peer) packet.disconnected((uint16_t)peer);
    packet.stop();
    for (unsigned frame = 0; frame < 120; ++frame) retro_run();
    bool passed = video_frames > 100 && audio_frames > 0;
    printf("{\"passed\":%s,\"videoFrames\":%u,\"audioFrames\":%u,\"reportedFps\":%.8f,"
           "\"nativePacketParticipants\":%u,\"packetProtocol\":\"gpSP v1.0\","
           "\"invalidLengthDispatches\":257,\"actualNetworkMatchTested\":false}\n",
           passed ? "true" : "false", video_frames, audio_frames, av.timing.fps, maximum);
    retro_unload_game(); retro_deinit(); free(content); dlclose(core);
    return passed ? 0 : 5;
}
