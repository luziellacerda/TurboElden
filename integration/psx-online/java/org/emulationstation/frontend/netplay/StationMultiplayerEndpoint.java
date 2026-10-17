package org.emulationstation.frontend.netplay;

import java.io.Closeable;
import java.io.IOException;
import java.util.concurrent.atomic.AtomicLong;

/** Explicit opt-in for native datagrams. The ordinary TCP tunnel does not use this interface. */
interface StationMultiplayerEndpoint extends Closeable {
    interface Factory {
        StationMultiplayerEndpoint create(int authenticatedLocalSlot, int authenticatedRemoteSlot) throws Exception;
    }
    byte[] takeOutgoing(int timeoutMs) throws Exception;
    /** Opt-in event wait after an empty read, outside READY's in-flight read.
     * true means this endpoint handled the bounded wait, including timeout;
     * false preserves the ordinary tunnel's existing nativeHint wait. */
    default boolean awaitOutgoingWake(int timeoutMs) throws Exception { return false; }
    int deliver(long uniqueDeliveryId, byte[] completeFrame) throws Exception;
    boolean awaitDelivery(long uniqueDeliveryId, int timeoutMs) throws Exception;
    /** Ordinary Dolphin/ENet framing remains the default; PSX explicitly opts in. */
    default Wire wire() { return Wire.DPL1; }
    /** Release bounded native receipts only AFTER the outer DATA cursor is confirmed. */
    default void deliveryConfirmed(long uniqueDeliveryId) throws Exception {}
    @Override default void close() throws IOException {}

    enum Wire {
        DPL1("DPL1", 4, 1), PXL1("PXL1", 2, 28);
        final String magic;
        final int maxSlot, minimumPayload;
        static final int HEADER = 8, MAX_PAYLOAD = 1392, MAX_FRAME = HEADER + MAX_PAYLOAD;
        Wire(String magic, int maxSlot, int minimumPayload) { this.magic = magic; this.maxSlot = maxSlot; this.minimumPayload = minimumPayload; }
        void binding(int localSlot, int remoteSlot) {
            if (localSlot < 1 || localSlot > maxSlot || remoteSlot < 1 || remoteSlot > maxSlot || localSlot == remoteSlot)
                throw new IllegalArgumentException(magic + "_SLOT");
        }
        int size(byte[] header, int localSlot, int remoteSlot, boolean incoming) throws IOException {
            if (header == null || header.length < HEADER || localSlot < 1 || localSlot > maxSlot || remoteSlot < 1 || remoteSlot > maxSlot || localSlot == remoteSlot ||
                    header[0] != magic.charAt(0) || header[1] != magic.charAt(1) || header[2] != magic.charAt(2) || header[3] != magic.charAt(3) ||
                    (header[4] & 255) != (incoming ? remoteSlot : localSlot) ||
                    (header[5] & 255) != (incoming ? localSlot : remoteSlot)) throw new IOException(magic + "_BINDING");
            int payload = ((header[6] & 255) << 8) | (header[7] & 255);
            if (payload < minimumPayload || payload > MAX_PAYLOAD) throw new IOException(magic + "_LENGTH");
            return HEADER + payload;
        }
        void outgoing(byte[] frame, int localSlot, int remoteSlot) throws IOException {
            if (frame == null || frame.length < HEADER || frame.length > MAX_FRAME || size(frame, localSlot, remoteSlot, false) != frame.length)
                throw new IOException(magic + "_FRAME");
        }
    }

    /** DPL1 frames form a byte stream on each authenticated TSR3 link. */
    final class Dpl1 {
        static final int HEADER = 8, MAX_DATAGRAM = 1392, MAX_FRAME = HEADER + MAX_DATAGRAM;
        private static final AtomicLong DELIVERY_IDS = new AtomicLong(1);
        private Dpl1() {}
        static int size(byte[] header, int localSlot, int remoteSlot, boolean incoming) throws IOException {
            if (header.length < HEADER || localSlot < 1 || localSlot > 4 || remoteSlot < 1 || remoteSlot > 4 || localSlot == remoteSlot ||
                    header[0] != 'D' || header[1] != 'P' || header[2] != 'L' || header[3] != '1' ||
                    (header[4] & 255) != (incoming ? remoteSlot : localSlot) ||
                    (header[5] & 255) != (incoming ? localSlot : remoteSlot)) throw new IOException("DPL1_BINDING");
            int payload = ((header[6] & 255) << 8) | (header[7] & 255);
            if (payload < 1 || payload > MAX_DATAGRAM) throw new IOException("DPL1_LENGTH");
            return HEADER + payload;
        }
        static void outgoing(byte[] frame, int localSlot, int remoteSlot) throws IOException {
            if (frame == null || frame.length < HEADER || frame.length > MAX_FRAME || size(frame, localSlot, remoteSlot, false) != frame.length)
                throw new IOException("DPL1_FRAME");
        }
        static long nextDeliveryId() throws IOException {
            for (;;) {
                long id = DELIVERY_IDS.get();
                if (id <= 0) throw new IOException("DPL1_DELIVERY_ID_EXHAUSTED");
                if (DELIVERY_IDS.compareAndSet(id, id == Long.MAX_VALUE ? 0 : id + 1)) return id;
            }
        }
    }

    /** Reads ahead without confirming partial bytes. Confirmation follows real native consumption. */
    final class Receiver {
        interface Source {
            byte[] read(long offset, int maximum) throws Exception;
            void confirm(long offset) throws Exception;
            boolean cancelled();
            void retryWait(int timeoutMs) throws Exception;
        }
        private final StationMultiplayerEndpoint endpoint;
        private final int localSlot, remoteSlot;
        private final Wire wire;
        private long cursor;
        Receiver(StationMultiplayerEndpoint endpoint, int localSlot, int remoteSlot, long deliveredOffset) {
            if (endpoint == null || localSlot < 1 || localSlot > 4 || remoteSlot < 1 || remoteSlot > 4 || localSlot == remoteSlot || deliveredOffset < 0)
                throw new IllegalArgumentException("DPL1_RECEIVER");
            wire = endpoint.wire();
            if (wire == null) throw new IllegalArgumentException("ENDPOINT_WIRE");
            wire.binding(localSlot, remoteSlot);
            this.endpoint = endpoint; this.localSlot = localSlot; this.remoteSlot = remoteSlot; cursor = deliveredOffset;
        }
        private boolean read(Source source, byte[] target, int at, int length) throws Exception {
            int end = at + length;
            while (at < end && !source.cancelled()) {
                byte[] part = source.read(cursor, end - at);
                if (part == null) return false;
                if (part.length < 1 || part.length > end - at || cursor > Long.MAX_VALUE - part.length) throw new IOException("DPL1_SOURCE");
                System.arraycopy(part, 0, target, at, part.length); at += part.length; cursor += part.length;
            }
            return at == end && !source.cancelled();
        }
        void run(Source source) throws Exception {
            while (!source.cancelled()) {
                byte[] header = new byte[Wire.HEADER];
                if (!read(source, header, 0, header.length)) return;
                int size = wire.size(header, localSlot, remoteSlot, true);
                byte[] frame = new byte[size]; System.arraycopy(header, 0, frame, 0, header.length);
                if (!read(source, frame, header.length, size - header.length)) return;
                long delivery = Dpl1.nextDeliveryId();
                for (;;) {
                    if (source.cancelled()) return;
                    int accepted = endpoint.deliver(delivery, frame);
                    if (accepted == 1) break;
                    if (accepted != 0) throw new IOException("DPL1_NATIVE_REJECT");
                    source.retryWait(25);
                }
                while (!source.cancelled() && !endpoint.awaitDelivery(delivery, 100)) source.retryWait(10);
                if (source.cancelled()) return;
                source.confirm(cursor);
                endpoint.deliveryConfirmed(delivery);
            }
        }
    }
}
