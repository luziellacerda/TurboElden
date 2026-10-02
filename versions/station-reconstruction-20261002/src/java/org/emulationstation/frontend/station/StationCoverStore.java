package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;

/** Persistent cover cache. Call on an IO worker only for requested visible items. */
public final class StationCoverStore {
    public interface PreviousCovers { byte[] find(String coverId,long revision) throws IOException; }
    public interface ImageValidator { void validate(byte[] bytes) throws IOException; }
    public interface Waiter { void waitMillis(long millis) throws InterruptedException; }
    private static final class Checked {
        final long size,modified;
        Checked(BasicFileAttributes a) {size=a.size();modified=a.lastModifiedTime().toMillis();}
        boolean matches(BasicFileAttributes a) {return size==a.size() && modified==a.lastModifiedTime().toMillis();}
    }
    private final Path directory;
    private final StationApi api;
    private final StationSessions sessions;
    private final StationApi.Clock clock;
    private final Waiter waiter;
    private final ImageValidator validator;
    private final PreviousCovers previousCovers;
    private long nextRequest;
    private final Map<String,Checked> checked=new LinkedHashMap<String,Checked>(256,0.75f,true) {
        protected boolean removeEldestEntry(Map.Entry<String,Checked> e) {return size()>256;}
    };
    private final Map<String,Long> unavailable=new LinkedHashMap<String,Long>(128,0.75f,true) {
        protected boolean removeEldestEntry(Map.Entry<String,Long> e) {return size()>128;}
    };
    public StationCoverStore(Path directory,StationApi api,StationSessions sessions,
            StationApi.Clock clock,Waiter waiter,ImageValidator validator) throws IOException {
        this(directory,api,sessions,clock,waiter,validator,null);
    }
    public StationCoverStore(Path directory,StationApi api,StationSessions sessions,
            StationApi.Clock clock,Waiter waiter,ImageValidator validator,PreviousCovers previousCovers) throws IOException {
        this.previousCovers=previousCovers;
        Files.createDirectories(directory);this.directory=directory.toRealPath();
        this.api=api;this.sessions=sessions;this.clock=clock;this.waiter=waiter;this.validator=validator;
    }
    public synchronized Path get(String coverId,long revision,StationApi.Cancellation cancel) throws Exception {
        StationCatalog.libraryId(coverId);
        if(revision<1)throw new IOException("Invalid cover revision");
        cancel.check();StationApi.Session session=sessions.get(cancel);
        String key=coverId+"-"+revision;Path file=directory.resolve(key+".img");
        if(Files.exists(file,LinkOption.NOFOLLOW_LINKS)) {
            if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid cover cache path");
            BasicFileAttributes attributes=Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
            Checked previous=checked.get(key);
            if(previous != null && previous.matches(attributes))return file;
            try {
                byte[] bytes=StationFiles.readBounded(file,StationProtocol.COVER_BODY_BYTES);
                StationFiles.imageExtension(bytes);validator.validate(bytes);
                checked.put(key,new Checked(attributes));return file;
            } catch(IOException corrupt) {checked.remove(key);}
        }
        if(previousCovers!=null) {
            byte[] imported=null;
            try {
                imported=previousCovers.find(coverId,revision);
                if(imported!=null){StationFiles.imageExtension(imported);validator.validate(imported);}
            }catch(IOException invalid){imported=null;}
            if(imported!=null) {
                StationFiles.replace(new ByteArrayInputStream(imported),file,imported.length,StationProtocol.COVER_BODY_BYTES,
                    cancel,StationFiles.NO_PROGRESS);
                checked.put(key,new Checked(Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS)));
                return file;
            }
        }
        Long retryAt=unavailable.get(key);
        if(retryAt != null && clock.millis()<retryAt)throw new IOException("Cover temporarily unavailable");
        while(clock.millis()<nextRequest) {
            cancel.check();
            try {waiter.waitMillis(Math.min(100,nextRequest-clock.millis()));}
            catch(InterruptedException e){Thread.currentThread().interrupt();cancel.check();}
        }
        cancel.check();nextRequest=clock.millis()+2100;
        byte[] bytes;
        session=sessions.get(cancel);
        try {bytes=api.cover(session,coverId,cancel);}
        catch(StationApi.Failure denied) {
            if(denied.sessionDenied())sessions.denied(session);
            if(denied.status==429)nextRequest=clock.millis()+60000;
            if(denied.status==404 || denied.status==429)unavailable.put(key,clock.millis()+60000);
            throw denied;
        }
        validator.validate(bytes);
        StationFiles.replace(new ByteArrayInputStream(bytes),file,bytes.length,StationProtocol.COVER_BODY_BYTES,
            cancel,StationFiles.NO_PROGRESS);
        checked.put(key,new Checked(Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS)));
        unavailable.remove(key);return file;
    }
}
