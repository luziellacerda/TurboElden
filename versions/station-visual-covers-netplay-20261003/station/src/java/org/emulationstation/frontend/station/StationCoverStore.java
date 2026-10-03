package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

/** Persistent cache with per-image exclusion. Different images never serialize their network IO. */
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

    private final ImageValidator validator;
    private final PreviousCovers previousCovers;
    private long blockedUntil;
    private final Object state=new Object();
    private static final class KeyLock {final ReentrantLock lock=new ReentrantLock();int users;}
    private final Map<String,KeyLock> keys=new HashMap<>();
    public static final class Deferred extends IOException {
        public final long retryMillis;public final boolean rateLimited;
        Deferred(long retryMillis,boolean rateLimited){super("Cover temporarily unavailable");this.retryMillis=Math.max(1,retryMillis);this.rateLimited=rateLimited;}
    }
    private KeyLock key(String id){synchronized(state){KeyLock value=keys.get(id);if(value==null){value=new KeyLock();keys.put(id,value);}value.users++;return value;}}
    private void release(String id,KeyLock value){synchronized(state){if(--value.users==0)keys.remove(id);}}
    private void remember(String key,Path file)throws IOException {Checked value=new Checked(Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS));synchronized(state){checked.put(key,value);unavailable.remove(key);}}

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
        this.api=api;this.sessions=sessions;this.clock=clock;this.validator=validator;
    }
    public Path get(String coverId,long revision,StationApi.Cancellation cancel) throws Exception {
        try(StationSessions.Lease lease=sessions.acquire(cancel)){return get(lease.session,coverId,revision,cancel);}
    }
    /** Uses the coordinator's session without renewing it while an artifact grant is in flight. */
    public Path get(StationApi.Session session,String coverId,long revision,StationApi.Cancellation cancel) throws Exception {
        StationCatalog.libraryId(coverId);
        if(revision<1)throw new IOException("Invalid cover revision");
        cancel.check();
        String key=coverId+"-"+revision;KeyLock value=key(key);boolean acquired=false;
        try {
            while(!(acquired=value.lock.tryLock(100,TimeUnit.MILLISECONDS)))cancel.check();
            cancel.check();return getLocked(session,coverId,key,revision,cancel);
        }catch(InterruptedException interrupted){Thread.currentThread().interrupt();throw new java.io.InterruptedIOException("Cover cache wait cancelled");}
        finally{if(acquired)value.lock.unlock();release(key,value);}
    }
    private Path getLocked(StationApi.Session session,String coverId,String key,long revision,StationApi.Cancellation cancel)throws Exception {
        Path file=directory.resolve(key+".img");
        if(Files.exists(file,LinkOption.NOFOLLOW_LINKS)) {
            if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid cover cache path");
            BasicFileAttributes attributes=Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
            Checked previous; synchronized(state){previous=checked.get(key);}
            if(previous != null && previous.matches(attributes)){StationDiagnostics.record(StationDiagnostics.Event.COVER_CACHE,0,1);return file;}
            try {
                byte[] bytes=StationFiles.readBounded(file,StationProtocol.COVER_BODY_BYTES);
                StationFiles.imageExtension(bytes);validator.validate(bytes);
                synchronized(state){checked.put(key,new Checked(attributes));}StationDiagnostics.record(StationDiagnostics.Event.COVER_CACHE,0,1);return file;
            } catch(IOException corrupt) {synchronized(state){checked.remove(key);}}
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
                remember(key,file);
                return file;
            }
        }
        synchronized(state){
            long now=clock.millis();Long retryAt=unavailable.get(key);
            if(retryAt!=null&&now<retryAt)throw new Deferred(retryAt-now,false);
            if(now<blockedUntil)throw new Deferred(blockedUntil-now,true);
        }
        cancel.check(); // Success has no pacing delay; other keys transfer concurrently.
        byte[] bytes;
        try {bytes=api.cover(session,coverId,cancel);}
        catch(StationApi.Failure denied) {
            if(denied.sessionDenied())sessions.denied(session);
            synchronized(state){
                if(denied.status==429)blockedUntil=Math.max(blockedUntil,clock.millis()+(denied.retryAfterMillis>0?denied.retryAfterMillis:60000));
                if(denied.status==404)unavailable.put(key,clock.millis()+60000);
            }
            throw denied;
        }
        validator.validate(bytes);
        StationFiles.replace(new ByteArrayInputStream(bytes),file,bytes.length,StationProtocol.COVER_BODY_BYTES,
            cancel,StationFiles.NO_PROGRESS);
        remember(key,file);
        return file;
    }
}
