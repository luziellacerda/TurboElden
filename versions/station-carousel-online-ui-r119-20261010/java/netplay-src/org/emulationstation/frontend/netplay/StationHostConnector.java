package org.emulationstation.frontend.netplay;

import java.io.IOException;
import java.io.InterruptedIOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;

/** Keep the first successful connection as the game stream; no disposable probe. */
final class StationHostConnector {
    static Socket connect(int port, long deadline, BooleanSupplier cancelled,
                          Consumer<Socket> pending, Semaphore nativeHint)
            throws IOException, InterruptedException {
        InetSocketAddress address = new InetSocketAddress(InetAddress.getByName("127.0.0.1"), port);
        while (System.nanoTime() < deadline) {
            if (cancelled.getAsBoolean() || Thread.currentThread().isInterrupted())
                throw new InterruptedIOException("Host connection cancelled");
            Socket candidate = new Socket();
            boolean retained = false;
            pending.accept(candidate);
            try {
                long remaining = deadline - System.nanoTime();
                if (remaining <= 0) break;
                candidate.connect(address, (int)Math.max(1, Math.min(250,
                        TimeUnit.NANOSECONDS.toMillis(remaining))));
                if (cancelled.getAsBoolean()) throw new InterruptedIOException("Host connection cancelled");
                candidate.setTcpNoDelay(true);
                retained = true;
                return candidate;
            } catch (IOException unavailable) {
                if (cancelled.getAsBoolean() || Thread.currentThread().isInterrupted())
                    throw new InterruptedIOException("Host connection cancelled");
            } finally {
                if (!retained) candidate.close();
            }
            long pause = Math.min(TimeUnit.MILLISECONDS.toNanos(50), deadline - System.nanoTime());
            if (pause > 0) nativeHint.tryAcquire(pause, TimeUnit.NANOSECONDS);
        }
        throw new IOException("Native listener unavailable");
    }
}
