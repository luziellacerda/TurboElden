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
    private int borrowers;
    /** A live bearer cannot be rotated while authenticated headers/grants still use it. */
    public final class Lease implements AutoCloseable {
        public final StationApi.Session session;
        private boolean closed;
        private Lease(StationApi.Session session){this.session=session;}
        @Override public void close(){synchronized(StationSessions.this){if(!closed){closed=true;borrowers--;StationSessions.this.notifyAll();}}}
    }
    private void awaitUnused(StationApi.Cancellation cancel)throws IOException {
        while(borrowers>0){cancel.check();try{wait(100);}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException("Session wait cancelled");}}
        cancel.check();
    }
    public synchronized Lease acquire(StationApi.Cancellation cancel)throws Exception {
        StationApi.Session value=get(cancel);borrowers++;return new Lease(value);
    }
    public StationSessions(StationApi api,StationApi.Clock clock,Path licenseFile) {
        this.api=api;this.clock=clock;this.licenseFile=licenseFile;
    }
    public synchronized StationApi.Session activate(String code,StationApi.Cancellation cancel) throws Exception {
        awaitUnused(cancel);current=null;
        String license=api.activate(code,cancel);
        byte[] bytes=license.getBytes(StandardCharsets.UTF_8);
        // Save the verified license immediately: activation codes are single-use.
        StationFiles.replace(new ByteArrayInputStream(bytes),licenseFile,bytes.length,64,StationFiles.NEVER_CANCELLED,StationFiles.NO_PROGRESS);
        current=api.openSession(license,cancel);return current;
    }
    public synchronized StationApi.Session get(StationApi.Cancellation cancel) throws Exception {
        cancel.check();
        if(current != null && !current.needsRenewal(clock.millis()))return current;
        awaitUnused(cancel);
        if(current != null && !current.needsRenewal(clock.millis()))return current;
        current=null;
        current=api.openSession(savedLicense(),cancel);return current;
    }
    public synchronized void denied(StationApi.Session rejected) {
        if (current == rejected) current=null;
    }
    public String savedLicense()throws IOException {
        if(!Files.isRegularFile(licenseFile,LinkOption.NOFOLLOW_LINKS))throw new IOException("Station activation required");
        String license=new String(StationFiles.readBounded(licenseFile,128),StandardCharsets.UTF_8).trim();
        if(!StationProtocol.licenseId(license))throw new IOException("Stored license invalid");
        return license;
    }
    public StationApi.Session peek() {return current;}
    public synchronized void forgetSession() {current=null;}
}
