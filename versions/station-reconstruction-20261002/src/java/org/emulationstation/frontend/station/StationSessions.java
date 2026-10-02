package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/** One session owner, no background polling, no password fallback, no persisted bearer. */
public final class StationSessions {
    private final StationApi api;
    private final StationApi.Clock clock;
    private final Path licenseFile;
    private volatile StationApi.Session current;
    public StationSessions(StationApi api,StationApi.Clock clock,Path licenseFile) {
        this.api=api;this.clock=clock;this.licenseFile=licenseFile;
    }
    public synchronized StationApi.Session activate(String code,StationApi.Cancellation cancel) throws Exception {
        current=null;
        String license=api.activate(code,cancel);
        byte[] bytes=license.getBytes(StandardCharsets.UTF_8);
        // Save the verified license immediately: activation codes are single-use.
        StationFiles.replace(new ByteArrayInputStream(bytes),licenseFile,bytes.length,64,StationFiles.NEVER_CANCELLED,StationFiles.NO_PROGRESS);
        current=api.openSession(license,cancel);return current;
    }
    public synchronized StationApi.Session get(StationApi.Cancellation cancel) throws Exception {
        cancel.check();
        if(current != null && !current.needsRenewal(clock.millis()))return current;
        current=null;
        if (!Files.isRegularFile(licenseFile,LinkOption.NOFOLLOW_LINKS)) throw new IOException("Station activation required");
        String license=new String(StationFiles.readBounded(licenseFile,128),StandardCharsets.UTF_8).trim();
        if (!StationProtocol.licenseId(license)) throw new IOException("Stored license invalid");
        current=api.openSession(license,cancel);return current;
    }
    public synchronized void denied(StationApi.Session rejected) {
        if (current == rejected) current=null;
    }
    public StationApi.Session peek() {return current;}
    public synchronized void forgetSession() {current=null;}
}
