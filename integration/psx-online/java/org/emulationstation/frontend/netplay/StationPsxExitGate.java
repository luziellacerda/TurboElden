// SPDX-License-Identifier: GPL-2.0-or-later
package org.emulationstation.frontend.netplay;
/** No native calls or authorization changes: pure teardown prerequisites. */
final class StationPsxExitGate {
    private StationPsxExitGate() {}
    static boolean ended(Thread thread) { return thread == null || thread.getState() == Thread.State.TERMINATED; }
    static boolean ownerEnded(boolean human, Thread sdl, Thread captured) {
        return human && ended(sdl) && ended(captured);
    }
    static boolean mayRetire(boolean human, boolean cleanup, boolean privateProcess, Thread sdl, Thread captured) {
        return cleanup && privateProcess && ownerEnded(human,sdl,captured);
    }
}
