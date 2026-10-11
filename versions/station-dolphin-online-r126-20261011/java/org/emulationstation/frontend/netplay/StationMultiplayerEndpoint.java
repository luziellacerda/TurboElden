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
    int deliver(long uniqueDeliveryId, byte[] completeFrame) throws Exception;
    boolean awaitDelivery(long uniqueDeliveryId, int timeoutMs) throws Exception;
    @Override default void close() throws IOException {}

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
        private long cursor;
        Receiver(StationMultiplayerEndpoint endpoint, int localSlot, int remoteSlot, long deliveredOffset) {
            if (endpoint == null || localSlot < 1 || localSlot > 4 || remoteSlot < 1 || remoteSlot > 4 || localSlot == remoteSlot || deliveredOffset < 0)
                throw new IllegalArgumentException("DPL1_RECEIVER");
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
                byte[] header = new byte[Dpl1.HEADER];
                if (!read(source, header, 0, header.length)) return;
                int size = Dpl1.size(header, localSlot, remoteSlot, true);
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
            }
        }
    }
}
