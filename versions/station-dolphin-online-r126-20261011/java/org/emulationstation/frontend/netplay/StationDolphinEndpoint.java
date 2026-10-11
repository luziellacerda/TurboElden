package org.emulationstation.frontend.netplay;

/** One native ENet endpoint per signed Station link; the session owner closes the shared native transport. */
final class StationDolphinEndpoint implements StationMultiplayerEndpoint {
    private final int remoteSlot;
    private StationDolphinEndpoint(int localSlot, int remoteSlot) {
        if (localSlot < 1 || localSlot > 4 || remoteSlot < 1 || remoteSlot > 4 || localSlot == remoteSlot || (localSlot != 1 && remoteSlot != 1))
            throw new IllegalArgumentException("DPL1_SLOT");
        this.remoteSlot = remoteSlot;
    }
    static Factory factory() { return StationDolphinEndpoint::new; }
    public byte[] takeOutgoing(int timeoutMs) { return StationDolphinBridge.nativeTakeOutgoing(remoteSlot, timeoutMs); }
    public int deliver(long uniqueDeliveryId, byte[] completeFrame) { return StationDolphinBridge.nativeDeliver(remoteSlot, uniqueDeliveryId, completeFrame); }
    public boolean awaitDelivery(long uniqueDeliveryId, int timeoutMs) { return StationDolphinBridge.nativeAwaitDelivery(uniqueDeliveryId, timeoutMs); }
}
