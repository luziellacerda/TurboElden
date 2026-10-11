package org.emulationstation.frontend.sony;

import android.os.ParcelFileDescriptor;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import org.json.JSONObject;

/** Imports the exact private Sony input automatically. No downloader, wizard or fake ready. */
final class Ps3Firmware {
    static final long BYTES = 206197916L;
    static final String SHA256 = "158471fd834f8ea8036136b6aab43cd86c7ba73d79ca30e0af3c0fe0001cf365";
    interface Progress { void update(String message); }
    private Ps3Firmware() {}
    static synchronized void ensure(Ps3Bootstrap.Ready owner, Progress progress) throws Exception {
        File flash = new File(owner.userDirectory, "config/dev_flash");
        File marker = new File(flash, ".installed");
        File receipt = new File(owner.userDirectory, "firmware/installed.json");
        if (marker.isFile() && receipt.isFile() && firmwarePresent(flash)) {
            JSONObject data = new JSONObject(readUtf8(receipt));
            if (SHA256.equals(data.optString("sourceSha256")) && data.optBoolean("nativeImportSucceeded"))
                return;
        }
        progress.update("Preparando o sistema PS3…");
        File pup = owner.assets.assetFile("PS3UPDAT.PUP");
        verifyPup(pup);
        // The native importer takes ownership of the detached descriptor and closes it.
        ParcelFileDescriptor descriptor = ParcelFileDescriptor.open(pup, ParcelFileDescriptor.MODE_READ_ONLY);
        int fd = descriptor.detachFd(); descriptor.close();
        boolean imported = owner.emulator.install_firmware(fd);
        if (!imported || !firmwarePresent(flash)) {
            if (marker.exists() && !marker.delete()) throw new IOException("PS3 firmware import failed; stale marker could not be removed");
            throw new IOException("O motor PS3 recusou a preparação do sistema");
        }
        JSONObject result = new JSONObject();
        result.put("schema", 1); result.put("sourceSha256", SHA256);
        result.put("sourceBytes", BYTES); result.put("firmwareVersion", "4.93");
        result.put("nativeImportSucceeded", true);
        Ps3Bootstrap.writeAtomic(receipt, result.toString().getBytes(StandardCharsets.UTF_8));
        // This is the upstream success marker, written only after native success + files.
        Ps3Bootstrap.writeAtomic(marker, "4.93\n".getBytes(StandardCharsets.UTF_8));
    }
    private static boolean firmwarePresent(File flash) {
        File sys = new File(flash, "sys/external");
        File[] libraries = sys.listFiles();
        if (libraries == null) return false;
        int count = 0;
        for (File library : libraries) if (library.isFile() && library.length() > 0 && library.getName().endsWith(".sprx")) count++;
        return count > 0;
    }
    static void verifyPup(File file) throws Exception {
        if (!file.isFile() || file.length() != BYTES) throw new IOException("PS3 firmware input has an unexpected size");
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        try (FileInputStream input = new FileInputStream(file)) {
            byte[] magic = new byte[5];
            if (input.read(magic) != magic.length || !"SCEUF".equals(new String(magic, StandardCharsets.US_ASCII)))
                throw new IOException("PS3 firmware input is not PUP");
            digest.update(magic); byte[] buffer = new byte[262144]; int count;
            while ((count = input.read(buffer)) != -1) digest.update(buffer, 0, count);
        }
        StringBuilder hex = new StringBuilder(64);
        for (byte value : digest.digest()) hex.append(String.format(java.util.Locale.ROOT, "%02x", value & 255));
        if (!SHA256.equals(hex.toString())) throw new IOException("PS3 firmware input identity mismatch");
    }
    private static String readUtf8(File file) throws IOException {
        if (file.length() > 16384) throw new IOException("PS3 firmware receipt is too large");
        try (FileInputStream input = new FileInputStream(file)) {
            byte[] bytes = new byte[(int) file.length()]; int offset = 0, count;
            while (offset < bytes.length && (count = input.read(bytes, offset, bytes.length - offset)) != -1) offset += count;
            if (offset != bytes.length) throw new IOException("PS3 firmware receipt is incomplete");
            return new String(bytes, StandardCharsets.UTF_8);
        }
    }
}
