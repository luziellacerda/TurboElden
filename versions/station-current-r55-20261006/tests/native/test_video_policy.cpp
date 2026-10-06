// Host-only policy regression test. Does not load Android libraries or contact a device.
#include "r53_video_policy.h"
#include <cstdio>
#include <cstdlib>

using namespace r53VideoPolicy;

static unsigned checks;
static void expect(bool value, const char* message) {
    ++checks;
    if (!value) { std::fprintf(stderr, "FAIL: %s\n", message); std::exit(1); }
}

static Frame normal(const char* asset = "platform-snes.mp4") {
    return {{true, false, 3, 8}, 7, true, true, 4, asset};
}

struct Driver {
    Slot slots[slotCount]{};
    unsigned starts = 0, stops = 0;

    int decoders() const {
        int count = 0;
        for (const auto& slot : slots) if (slot.hasTexture) ++count;
        return count;
    }

    Decision apply(const Frame& frame, bool startAllowed = true) {
        const auto decision = decide(frame, slots);
        // Model the required native ordering; Android's physical release is separate.
        for (int i = 0; i < slotCount; ++i) if (decision.retireMask & (1u << i)) {
            slots[i] = {}; ++stops;
        }
        if (decision.startSlot >= 0 && startAllowed) {
            expect(decoders() == 0, "stop every old decoder before starting the focus");
            slots[decision.startSlot] = {decision.wantedAsset, true}; ++starts;
        }
        expect(decoders() <= 1, "at most one decoder after reconciliation");
        for (const auto& slot : slots) if (slot.hasTexture) {
            expect(frameAllowsVideo(frame), "no decoder survives an ineligible frame");
            expect(sameAsset(slot.asset, frame.focusedAsset), "decoder belongs to drawn focus");
        }
        return decision;
    }
};

static void navigationScenarios() {
    Driver driver;
    auto platform = normal();
    driver.apply(platform);
    expect(driver.starts == 1 && driver.stops == 0, "first focus starts one player");
    driver.apply(platform);
    expect(driver.starts == 1 && driver.stops == 0, "steady render does not restart player");

    char sameAssetInCollection[] = "platform-snes.mp4";
    auto collection = normal(sameAssetInCollection);
    collection.menu.visibleCount = 6;
    driver.apply(collection);
    expect(driver.starts == 1 && driver.stops == 0,
           "platform to collection with same clip preserves preparing/live player");

    auto bomberman = normal("collection-bomberman.mp4");
    driver.apply(bomberman);
    expect(driver.starts == 2 && driver.stops == 1, "new collection focus replaces old player");
    expect(cellSource(true, false, true) == CellSource::Preview,
           "poster/retained frame is immediate while new focus prepares");
    expect(cellSource(false, true, true) == CellSource::Preview,
           "side card is static even when its asset matches a live player");
    expect(cellSource(true, true, true) == CellSource::Live, "focus becomes live when frame arrives");

    auto games = bomberman;
    games.menu.systemsMode = false;
    driver.apply(games);
    expect(driver.decoders() == 0, "entering games retires the decoder");
    const unsigned stopped = driver.stops;
    for (int i = 0; i < 100; ++i) driver.apply(games);
    expect(driver.stops == stopped, "repeated hidden renders do not repeat stop work");

    driver.apply(bomberman);
    auto missingCollection = bomberman;
    missingCollection.menu.visibleCount = 0;
    missingCollection.paintedCount = 0;
    missingCollection.focusedCellPainted = false;
    driver.apply(missingCollection);
    expect(driver.decoders() == 0, "catalog removal leaving empty collection stops old focus");

    driver.apply(platform);
    auto animating = normal("platform-nes.mp4");
    animating.focusedCellPainted = false;
    driver.apply(animating);
    expect(driver.decoders() == 0, "do not decode a focus still outside painted bounds");
    animating.focusedCellPainted = true;
    driver.apply(animating);
    expect(driver.decoders() == 1, "start new focus when its cell actually appears");

    auto retry = normal("platform-n64.mp4");
    driver.apply(retry, false);
    expect(driver.decoders() == 0, "retry delay cannot keep the former focus alive");
    expect(cellSource(true, false, true) == CellSource::Preview, "retry delay keeps static preview");
}

static void everyStopCondition() {
    for (int reason = 0; reason < 14; ++reason) {
        Driver driver;
        driver.apply(normal());
        auto frame = normal();
        switch (reason) {
        case 0: frame.menu.systemsMode = false; break;
        case 1: frame.menu.modal = true; break;
        case 2: frame.menu.phase = 0; break;
        case 3: frame.menu.phase = 1; break;
        case 4: frame.menu.phase = 2; break;
        case 5: frame.menu.phase = 4; break;
        case 6: frame.menu.visibleCount = 0; break;
        case 7: frame.paintedCount = 0; break;
        case 8: frame.focusedCellPainted = false; break;
        case 9: frame.rendererReady = false; break;
        case 10: frame.decoderCapacity = 0; break;
        case 11: frame.decoderCapacity = -1; break;
        case 12: frame.focusedAsset = nullptr; break;
        case 13: frame.focusedAsset = ""; break;
        }
        driver.apply(frame);
        expect(driver.decoders() == 0 && driver.stops == 1,
               "each visibility/loading/resource failure stops prior player");
    }
}

static void legacyPoolAndDuplicates() {
    Driver legacy;
    legacy.slots[0] = {"old-left.mp4", true};
    legacy.slots[1] = {"platform-snes.mp4", true};
    legacy.slots[2] = {"old-right.mp4", true};
    legacy.slots[3] = {"old-scratch.mp4", true};
    const auto kept = legacy.apply(normal());
    expect(kept.keepSlot == 1 && kept.retireMask == 13 && kept.startSlot == -1,
           "collapse warm/scratch pool to existing focus without restarting it");
    expect(legacy.starts == 0 && legacy.stops == 3, "only obsolete legacy players stop");

    Driver duplicates;
    duplicates.slots[0] = {"platform-snes.mp4", false};
    duplicates.slots[1] = {"platform-snes.mp4", true};
    duplicates.slots[2] = {"platform-snes.mp4", true};
    duplicates.slots[3] = {nullptr, true};
    const auto cleaned = duplicates.apply(normal());
    expect(cleaned.keepSlot == 1 && cleaned.startSlot == -1,
           "prefer existing decoder and retire duplicate/orphan entries");
}

static void exhaustivePoolStates() {
    const Slot possibilities[] = {
        {nullptr, false}, {nullptr, true}, {"a.mp4", false},
        {"a.mp4", true}, {"b.mp4", true}, {"c.mp4", true}
    };
    unsigned combinations = 0;
    for (int state = 0; state < 1296; ++state) {
        for (int capacity = -1; capacity <= 5; ++capacity) {
            for (int focus = 0; focus < 4; ++focus) {
                Driver driver;
                int encoded = state;
                for (int i = 0; i < slotCount; ++i) {
                    driver.slots[i] = possibilities[encoded % 6]; encoded /= 6;
                }
                const char* assets[] = {nullptr, "a.mp4", "b.mp4", "new.mp4"};
                auto frame = normal(assets[focus]); frame.decoderCapacity = capacity;
                driver.apply(frame);
                const auto stable = driver.apply(frame);
                expect(stable.startSlot == -1 && stable.retireMask == 0,
                       "reconciliation is stable for every pool state and capacity");
                ++combinations;
            }
        }
    }
    expect(combinations == 36288, "exhaustive pool/capacity/asset combinations visited");
}

int main() {
    navigationScenarios();
    everyStopCondition();
    legacyPoolAndDuplicates();
    exhaustivePoolStates();
    std::printf("PASS: %u checks; 36288 pool/capacity/asset combinations; no Android/device access.\n", checks);
    return 0;
}
