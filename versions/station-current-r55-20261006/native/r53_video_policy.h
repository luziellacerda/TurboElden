#pragma once

// Review candidate only. Pure policy: no JNI, GL, IO, downloads or emulator calls.
// Keep the existing four native entries so every obsolete entry can be retired.
// This policy requests at most one decoder; Java must release stops before starts.
namespace r53VideoPolicy {

static constexpr int slotCount = 4;

struct Menu {
    bool systemsMode; // Both platform and collection menus set this to true.
    bool modal;
    int phase;
    int visibleCount;
};

inline bool menuAllowsVideo(const Menu& menu) {
    return menu.systemsMode && !menu.modal && menu.phase == 3 &&
           menu.visibleCount > 0;
}

struct Frame {
    Menu menu;
    int paintedCount;
    bool focusedCellPainted;
    // True only after current-context GL, JNI, MVP and both shaders are usable.
    bool rendererReady;
    int decoderCapacity;
    const char* focusedAsset;
};

struct Slot {
    const char* asset;
    bool hasTexture; // Includes a player still preparing its first frame.
};

struct Decision {
    const char* wantedAsset;
    int keepSlot;
    unsigned retireMask;
    int startSlot;
};

inline bool sameAsset(const char* a, const char* b) {
    if (!a || !b || !*a || !*b) return false;
    while (*a && *a == *b) { ++a; ++b; }
    return *a == *b;
}

inline bool frameAllowsVideo(const Frame& frame) {
    return menuAllowsVideo(frame.menu) && frame.paintedCount > 0 &&
           frame.focusedCellPainted && frame.rendererReady &&
           frame.decoderCapacity > 0 && frame.focusedAsset && *frame.focusedAsset;
}

// The caller must retire every bit in retireMask BEFORE considering startSlot.
// Keep/start identity is the asset text, not the screen type or string address.
// Existing retry/backoff logic still decides whether a proposed start is attempted.
inline Decision decide(const Frame& frame, const Slot (&slots)[slotCount]) {
    Decision result{nullptr, -1, 0, -1};
    if (frameAllowsVideo(frame)) {
        result.wantedAsset = frame.focusedAsset;
        for (int i = 0; i < slotCount; ++i) {
            if (!sameAsset(slots[i].asset, result.wantedAsset)) continue;
            // Prefer a preparing/live player over an unused matching reservation.
            if (result.keepSlot < 0 ||
                (!slots[result.keepSlot].hasTexture && slots[i].hasTexture)) {
                result.keepSlot = i;
            }
        }
    }
    for (int i = 0; i < slotCount; ++i) {
        if (i != result.keepSlot && (slots[i].asset || slots[i].hasTexture)) {
            result.retireMask |= 1u << i;
        }
    }
    if (result.wantedAsset) {
        if (result.keepSlot < 0) result.startSlot = 0;
        else if (!slots[result.keepSlot].hasTexture) result.startSlot = result.keepSlot;
    }
    return result;
}

enum class CellSource { None, Preview, Live };

// previewReady means an existing retained frame OR an uploaded packaged poster.
// An adjacent cell stays static even if it maps to the same asset as the focus.
inline CellSource cellSource(bool focusedCell, bool liveFrameReady, bool previewReady) {
    if (focusedCell && liveFrameReady) return CellSource::Live;
    return previewReady ? CellSource::Preview : CellSource::None;
}

} // namespace r53VideoPolicy
