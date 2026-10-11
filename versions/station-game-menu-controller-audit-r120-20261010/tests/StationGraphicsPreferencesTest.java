package org.emulationstation.frontend.station;

/** Executable pure-state checks; no Android runtime is invoked. */
public final class StationGraphicsPreferencesTest {
    private static int checks;
    private static void check(boolean value, String reason) {
        checks++;
        if (!value) throw new AssertionError(reason);
    }
    public static void main(String[] args) {
        StationGraphicsPreferences.State initial = StationGraphicsPreferences.State.defaults();
        check(initial.effectiveMask() == 63, "R116 visual defaults must stay enabled");
        check(initial.backgroundMode == StationGraphicsPreferences.SKY, "default background remains sky");
        check(initial.backgroundAllowed(), "default sky is permitted");
        int[] effects = { 1, 2, 4, 8, 16, 32 };
        for (int effect : effects) {
            StationGraphicsPreferences.State disabled = initial.withEffect(effect, false);
            check(!disabled.isEnabled(effect), "individual effect must turn off");
            check(disabled.effectiveMask() == (63 & ~effect), "unrelated flags must be retained");
            check(disabled.revision == 1L, "changed revision must advance once");
            check(disabled.withEffect(effect, false) == disabled, "idempotent setter must not trigger callbacks");
            check(disabled.withEffect(effect, true).effectiveMask() == 63, "reenable restores only chosen flag");
        }
        StationGraphicsPreferences.State choices = initial.withEffect(StationGraphicsPreferences.LED, false)
                .withEffect(StationGraphicsPreferences.ICONS, false).withBackgroundMode(StationGraphicsPreferences.WAVES);
        StationGraphicsPreferences.State minimal = choices.withMasterDisabled(true);
        check(minimal.effectiveMask() == 0, "master disables every effect");
        check(!minimal.backgroundAllowed(), "master prevents wave/cloud work");
        check(minimal.effectiveBackgroundMode() == StationGraphicsPreferences.OFF, "renderer receives OFF while disabled");
        check(minimal.individualMask == choices.individualMask, "master must retain individual choices");
        check(minimal.backgroundMode == StationGraphicsPreferences.WAVES, "master must retain selected background");
        StationGraphicsPreferences.State restored = minimal.withMasterDisabled(false);
        check(restored.effectiveMask() == choices.effectiveMask(), "restore retained choices");
        check(restored.effectiveBackgroundMode() == StationGraphicsPreferences.WAVES, "restore selected waves");
        check(!restored.isEnabled(StationGraphicsPreferences.LED), "restore cannot enable a manually disabled LED");
        StationGraphicsPreferences.State noBackground = choices.withBackgroundMode(StationGraphicsPreferences.OFF);
        check(!noBackground.backgroundAllowed(), "OFF prevents background work even when background flag is on");
        check(noBackground.isEnabled(StationGraphicsPreferences.VIDEO), "OFF affects only background");
        StationGraphicsPreferences.State cloudOff = choices.withEffect(StationGraphicsPreferences.CLOUDS, false);
        check(cloudOff.effectiveBackgroundMode() == StationGraphicsPreferences.OFF, "background switch dominates saved wave mode");
        check(cloudOff.withEffect(StationGraphicsPreferences.CLOUDS, true).effectiveBackgroundMode() == StationGraphicsPreferences.WAVES, "restore background switch preserves mode");
        StationGraphicsPreferences.State stale = new StationGraphicsPreferences.State(-1, false, 88, -6L);
        check(stale.individualMask == 63, "unknown persisted bits must be removed");
        check(stale.backgroundMode == StationGraphicsPreferences.SKY, "unknown persisted mode falls back to default");
        check(stale.revision == 0L, "negative revision is rejected");
        check(!stale.isEnabled(0), "zero flags are never an enabled effect");
        check(stale.withEffect(1 << 12, false) == stale, "unknown flags do not trigger a save");
        check(new StationGraphicsPreferences.State(63, false, 0, Long.MAX_VALUE).withEffect(1, false).revision == 1L,
                "revision wrap cannot become negative");
        System.out.println("PASS " + checks + " graphics state checks");
    }
}
