// SPDX-License-Identifier: GPL-2.0-or-later
package org.emulationstation.frontend.netplay;

import java.io.IOException;

/** PXL1 for the exact two Standard-pad ports. DATA receipt is never retro_run proof. */
final class StationPsxEndpoint implements StationMultiplayerEndpoint {
    private final int localSlot, remoteSlot;
    private volatile boolean closed;
    private StationPsxEndpoint(int localSlot, int remoteSlot) {
        Wire.PXL1.binding(localSlot, remoteSlot);
        this.localSlot = localSlot; this.remoteSlot = remoteSlot;
    }
    static Factory factory() { return StationPsxEndpoint::new; }
    @Override public Wire wire() { return Wire.PXL1; }
    public byte[] takeOutgoing(int timeoutMs) throws IOException {
        if (closed) return null;
        byte[] frame = StationPsxBridge.nativeTakeOutgoing();
        if (frame != null && frame.length != 0) wire().outgoing(frame, localSlot, remoteSlot);
        return frame;
    }
    public int deliver(long id, byte[] frame) throws IOException {
        if (closed || id <= 0) return -1;
        wire().size(frame, localSlot, remoteSlot, true);
        int result = StationPsxBridge.nativeDeliver(remoteSlot, id, frame);
        // Superseded8 is a guarded epoch drop with a real copied receipt.
        // It is NOT an Executed gameplay commit; never discard unadmitted data.
        if (result == 0 || result == 1 || result == 8) return StationPsxBridge.nativeCopied(id) ? 1 : -1;
        if (result == 2 || result == 4) return 0;
        return -1;
    }
    public boolean awaitDelivery(long id, int timeoutMs) {
        return !closed && id > 0 && StationPsxBridge.nativeCopied(id);
    }
    @Override public void deliveryConfirmed(long id) throws IOException {
        if (closed) return;
        int result = StationPsxBridge.nativeReleaseReceipt(id);
        if (result == 0 || result == 1 && StationPsxBridge.nativeCopied(id)) return;
        throw new IOException("PXL1_RECEIPT_RELEASE");
    }
    // Closing a link never authorizes a core STOP; the session owns human exit.
    @Override public void close() { closed = true; }
}
