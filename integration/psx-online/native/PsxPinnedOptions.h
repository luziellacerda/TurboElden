/* Generated from the exact normal core's compiled option table. */
#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>
namespace station_psx {
struct PinnedOption { const char* key; const char* value; };
inline constexpr PinnedOption compiled_defaults[] = {
    {"pcsx_rearmed_alt_flip", "auto"},
    {"pcsx_rearmed_analog_axis_modifier", "square"},
    {"pcsx_rearmed_analog_combo", "l1+r1+select"},
    {"pcsx_rearmed_bios", "auto"},
    {"pcsx_rearmed_cd_readahead", "12"},
    {"pcsx_rearmed_cd_turbo", "disabled"},
    {"pcsx_rearmed_crosshair1", "disabled"},
    {"pcsx_rearmed_crosshair2", "disabled"},
    {"pcsx_rearmed_display_fps_v2", "disabled"},
    {"pcsx_rearmed_display_info", "enabled"},
    {"pcsx_rearmed_dithering", "enabled"},
    {"pcsx_rearmed_drc", "enabled"},
    {"pcsx_rearmed_drc_thread", "auto"},
    {"pcsx_rearmed_exception_emulation", "disabled"},
    {"pcsx_rearmed_fractional_framerate", "auto"},
    {"pcsx_rearmed_frameskip_interval", "3"},
    {"pcsx_rearmed_frameskip_threshold", "33"},
    {"pcsx_rearmed_frameskip_type", "disabled"},
    {"pcsx_rearmed_gpu_slow_llists", "auto"},
    {"pcsx_rearmed_gpu_thread_rendering", "auto"},
    {"pcsx_rearmed_gteregsunneeded", "disabled"},
    {"pcsx_rearmed_gunconadjustratiox", "1.00"},
    {"pcsx_rearmed_gunconadjustratioy", "1.00"},
    {"pcsx_rearmed_gunconadjustx", "0"},
    {"pcsx_rearmed_gunconadjusty", "0"},
    {"pcsx_rearmed_icache_emulation", "enabled"},
    {"pcsx_rearmed_input_sensitivity", "1.00"},
    {"pcsx_rearmed_konamigunadjustx", "0"},
    {"pcsx_rearmed_konamigunadjusty", "0"},
    {"pcsx_rearmed_memcard1", "libretro"},
    {"pcsx_rearmed_memcard2", "shared"},
    {"pcsx_rearmed_multitap", "disabled"},
    {"pcsx_rearmed_negcon_deadzone", "0"},
    {"pcsx_rearmed_negcon_response", "linear"},
    {"pcsx_rearmed_neon_enhancement_enable", "disabled"},
    {"pcsx_rearmed_neon_enhancement_no_main", "disabled"},
    {"pcsx_rearmed_neon_enhancement_tex_adj_v2", "enabled"},
    {"pcsx_rearmed_neon_interlace_enable_v2", "auto"},
    {"pcsx_rearmed_nocdaudio", "enabled"},
    {"pcsx_rearmed_nocompathacks", "disabled"},
    {"pcsx_rearmed_nogteflags", "disabled"},
    {"pcsx_rearmed_nosmccheck", "disabled"},
    {"pcsx_rearmed_nostalls", "disabled"},
    {"pcsx_rearmed_noxadecoding", "enabled"},
    {"pcsx_rearmed_psxclock", "auto"},
    {"pcsx_rearmed_region", "auto"},
    {"pcsx_rearmed_rgb32_output", "disabled"},
    {"pcsx_rearmed_scale_hires", "disabled"},
    {"pcsx_rearmed_screen_centering", "auto"},
    {"pcsx_rearmed_screen_centering_h_adj", "0"},
    {"pcsx_rearmed_screen_centering_x", "0"},
    {"pcsx_rearmed_screen_centering_y", "0"},
    {"pcsx_rearmed_show_bios_bootlogo", "disabled"},
    {"pcsx_rearmed_show_input_settings", "disabled"},
    {"pcsx_rearmed_show_overscan", "disabled"},
    {"pcsx_rearmed_spu_interpolation", "simple"},
    {"pcsx_rearmed_spu_reverb", "enabled"},
    {"pcsx_rearmed_spu_thread", "disabled"},
    {"pcsx_rearmed_vibration", "enabled"},
};
inline constexpr PinnedOption option_overrides[] = {
    {"pcsx_rearmed_analog_combo", "disabled"},
    {"pcsx_rearmed_bios", "HLE"},
    {"pcsx_rearmed_drc_thread", "disabled"},
    {"pcsx_rearmed_frameskip_type", "disabled"},
    {"pcsx_rearmed_gpu_thread_rendering", "disabled"},
    {"pcsx_rearmed_multitap", "disabled"},
    {"pcsx_rearmed_spu_thread", "disabled"},
};
inline constexpr std::uint32_t input_delay_frames=8; // signed PSX online pipeline, not an emulator speed option.
inline constexpr const char* compiled_defaults_sha256 = "bcbb221ea532b6caffa5c78d807e2264ad6843e18b5e84a433fbd6aff7514d49";
inline constexpr const char* canonical_options = "backend=psx-player-station-v1\nwire=PXL1\nownerSha256=62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6\ncoreSha256=e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9\ncompiledDefaultsSha256=bcbb221ea532b6caffa5c78d807e2264ad6843e18b5e84a433fbd6aff7514d49\noptionsPolicy=compiled-defaults+explicit-overrides-v1\ninputPolicy=standard-two-ports-v1\nsynchronization=host-authoritative-lockstep-v1\ninputDelayFrames=8\nstatePolicy=owner-thread-snapshot-v1\nsaves=session-only-fresh\nhumanExitOnly=true\npcsx_rearmed_analog_combo=disabled\npcsx_rearmed_bios=HLE\npcsx_rearmed_drc_thread=disabled\npcsx_rearmed_frameskip_type=disabled\npcsx_rearmed_gpu_thread_rendering=disabled\npcsx_rearmed_multitap=disabled\npcsx_rearmed_spu_thread=disabled\n";
inline constexpr const char* options_sha256 = "09f7154252899f1e4e3e118154adf2ef3519fd2a7e4a14b301fb6f4070888fd8";
template<std::size_t N> inline const char* lookup(const PinnedOption (&rows)[N], const char* key) {
    if (!key) return nullptr;
    for (const auto& row : rows) if (std::strcmp(row.key, key)==0) return row.value;
    return nullptr;
}
inline const char* pinned_option(const char* key) {
    const char* value=lookup(option_overrides,key);
    return value ? value : lookup(compiled_defaults,key);
}
} // namespace station_psx
