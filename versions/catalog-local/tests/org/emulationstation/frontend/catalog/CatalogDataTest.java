package org.emulationstation.frontend.catalog;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

public final class CatalogDataTest {
    private static int checks;
    private static void check(boolean condition, String label) {
        if (!condition) throw new AssertionError(label);
        checks++;
    }
    private static void rejects(InputStream input, String label) throws Exception {
        try { CatalogData.readVerified(input); throw new AssertionError(label); }
        catch (IOException expected) { checks++; }
    }
    public static void main(String[] args) throws Exception {
        String root = "https://samboxmanager.squareweb.app";
        for (String url : new String[] {root + "/drawers.json", root + "/drawers.json/TEST/android",
                "https://SAMBOXMANAGER.SQUAREWEB.APP:443/drawers.json",
                "http://samboxmanager.squareweb.app:80/drawers.json"}) {
            check(CatalogData.matches(url, null), "Catalogue route should be local");
            check(!CatalogData.matches(url, "download.zip"), "File downloads must stay original");
        }
        for (String url : new String[] {null, "", "not a url", "/drawers.json",
                root + "/drawers.json/", root + "/drawers.json/android", root + "/drawers.json//android",
                root + "/drawers.json/a/b/android", root + "/drawers.json/a/other",
                root + "/telemetry/android", root + "/drawers.json?refresh=1",
                root + "/drawers.json#x", root + "/%64rawers.json",
                "https://samboxmanager.squareweb.app:444/drawers.json",
                "https://user@samboxmanager.squareweb.app/drawers.json",
                "https://samboxmanager.squareweb.app.evil.test/drawers.json",
                "https://other.test/drawers.json", "ftp://samboxmanager.squareweb.app/drawers.json",
                "https://miami.sambox.buzz/game.zip",
                "https://buildbot.libretro.com/assets/system/Dolphin.zip"}) {
            check(!CatalogData.matches(url, null), "Other routes must not be intercepted");
        }
        rejects(null, "Null input must fail locally");
        rejects(new ByteArrayInputStream(new byte[0]), "Empty input must fail locally");
        rejects(new ByteArrayInputStream("[]".getBytes(StandardCharsets.UTF_8)), "Modified catalogue must fail locally");
        rejects(new InputStream() { public int read() throws IOException { throw new IOException("test"); } }, "Read errors must propagate");
        try (InputStream large = new ByteArrayInputStream(new byte[CatalogData.MAX_BYTES + 1])) {
            rejects(large, "Oversize input must fail locally");
        }
        check(args.length == 1, "Pass the authorized snapshot path");
        byte[] bytes;
        try (InputStream input = new FileInputStream(args[0])) { bytes = CatalogData.readVerified(input); }
        check(bytes.length == new File(args[0]).length(), "Entire snapshot must be returned unchanged");
        check(new String(bytes, StandardCharsets.UTF_8).trim().startsWith("["), "Snapshot must retain its original root array");
        bytes[0] ^= 1;
        rejects(new ByteArrayInputStream(bytes), "A single corrupt byte must fail locally");
        System.out.println("PASS: " + checks + " local catalogue checks (no network).");
    }
}
