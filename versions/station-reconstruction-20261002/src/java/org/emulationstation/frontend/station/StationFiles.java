package org.emulationstation.frontend.station;

import java.io.IOException;
import java.io.InputStream;
import java.io.InterruptedIOException;
import java.io.FileOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/** Transactional file publication shared by catalog, covers and game installation. */
public final class StationFiles {
    public interface Cancellation { boolean cancelled(); }
    public interface Progress { void changed(long received, long total); }
    public static final Cancellation NEVER_CANCELLED = () -> false;
    public static final Progress NO_PROGRESS = (received, total) -> {};
    public static final class Receipt {
        public final long size;
        public final String sha256;
        Receipt(long size, String sha256) { this.size = size; this.sha256 = sha256; }
    }

    private StationFiles() {}

    public static Receipt replace(InputStream source, Path destination, long expected,
                                  long maximum, Cancellation cancellation, Progress progress)
            throws IOException {
        return replace(source, destination, expected, maximum, cancellation, progress, null);
    }

    public static Receipt replace(InputStream source, Path destination, long expected,
                                  long maximum, Cancellation cancellation, Progress progress,
                                  String expectedSha256) throws IOException {
        if (expectedSha256 != null && !expectedSha256.matches("[0-9a-f]{64}"))
            throw new IOException("Invalid expected file digest");
        if (source == null || destination == null || cancellation == null || progress == null)
            throw new IllegalArgumentException("Missing file operation argument");
        if (maximum < 1 || expected < -1 || expected > maximum)
            throw new IOException("Invalid announced file length");
        Path absolute = destination.toAbsolutePath().normalize();
        Path parent = absolute.getParent();
        if (parent == null) throw new IOException("Missing destination directory");
        Files.createDirectories(parent);
        if (Files.isSymbolicLink(absolute)) throw new IOException("Symbolic destination refused");
        Path partial = Files.createTempFile(parent, ".station-", ".part");
        boolean committed = false;
        MessageDigest digest;
        try { digest = MessageDigest.getInstance("SHA-256"); }
        catch (NoSuchAlgorithmException impossible) { throw new AssertionError(impossible); }
        try {
            long received = 0;
            try (FileOutputStream output = new FileOutputStream(partial.toFile())) {
                byte[] buffer = new byte[64 * 1024];
                for (;;) {
                    checkCancelled(cancellation);
                    int count = source.read(buffer);
                    if (count < 0) break;
                    if (count == 0) continue;
                    if (count > maximum - received || (expected >= 0 && count > expected - received))
                        throw new IOException("Received file exceeds announced length");
                    output.write(buffer, 0, count);
                    digest.update(buffer, 0, count);
                    received += count;
                    progress.changed(received, expected);
                }
                if (received == 0 || (expected >= 0 && received != expected))
                    throw new IOException("Received file is incomplete");
                output.getFD().sync();
            }
            checkCancelled(cancellation);
            String calculated = hex(digest.digest());
            if (expectedSha256 != null && !expectedSha256.equals(calculated))
                throw new IOException("File digest does not match the authorized artifact");
            // Same-directory atomic rename keeps the previous complete file on any earlier failure.
            Files.move(partial, absolute, StandardCopyOption.ATOMIC_MOVE,
                       StandardCopyOption.REPLACE_EXISTING);
            committed = true;
            return new Receipt(received, calculated);
        } finally {
            if (!committed) Files.deleteIfExists(partial);
        }
    }

    public static byte[] readBounded(Path file, int maximum) throws IOException {
        long length = Files.size(file);
        if (length < 1 || length > maximum) throw new IOException("Stored file size is invalid");
        try (InputStream input = Files.newInputStream(file)) {
            byte[] bytes = new byte[(int) length];
            int position = 0;
            while (position < bytes.length) {
                int count = input.read(bytes, position, bytes.length - position);
                if (count < 0) throw new IOException("Stored file changed while reading");
                if (count > 0) position += count;
            }
            if (input.read() != -1) throw new IOException("Stored file changed while reading");
            return bytes;
        }
    }

    public static String imageExtension(byte[] bytes) throws IOException {
        if (matches(bytes, 0, new int[]{137,80,78,71,13,10,26,10})) return "png";
        if (matches(bytes, 0, new int[]{255,216,255})) return "jpg";
        if (ascii(bytes, 0, "GIF87a") || ascii(bytes, 0, "GIF89a")) return "gif";
        if (ascii(bytes, 0, "RIFF") && ascii(bytes, 8, "WEBP")) return "webp";
        throw new IOException("Response does not contain a supported image");
    }

    public static String archiveType(byte[] prefix) {
        if (matches(prefix, 0, new int[]{80,75,3,4})
                || matches(prefix, 0, new int[]{80,75,5,6})) return "zip";
        if (matches(prefix, 0, new int[]{82,97,114,33,26,7,0})
                || matches(prefix, 0, new int[]{82,97,114,33,26,7,1,0})) return "rar";
        if (matches(prefix, 0, new int[]{55,122,188,175,39,28})) return "7z";
        return "";
    }

    private static boolean ascii(byte[] data, int at, String value) {
        if (at < 0 || data.length - at < value.length()) return false;
        for (int i = 0; i < value.length(); i++) if (data[at + i] != value.charAt(i)) return false;
        return true;
    }

    private static boolean matches(byte[] data, int at, int[] value) {
        if (at < 0 || data.length - at < value.length) return false;
        for (int i = 0; i < value.length; i++) if ((data[at + i] & 255) != value[i]) return false;
        return true;
    }

    private static void checkCancelled(Cancellation cancellation) throws InterruptedIOException {
        if (cancellation.cancelled() || Thread.currentThread().isInterrupted())
            throw new InterruptedIOException("Transfer cancelled");
    }

    private static String hex(byte[] data) {
        StringBuilder output = new StringBuilder(data.length * 2);
        for (byte b : data) {
            output.append(Character.forDigit((b & 255) >>> 4, 16));
            output.append(Character.forDigit(b & 15, 16));
        }
        return output.toString();
    }
}
