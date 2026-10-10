package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

/** Persistent cache with per-image exclusion. Different images never serialize their network IO. */
public final class StationCoverStore {
    private static final long LEDGER_HARD_BYTES=8L*1024L*1024L;
    private static final long LEDGER_COMPACT_BYTES=1024L*1024L;
    private static final int LEDGER_HARD_RECORDS=32768,LEDGER_COMPACT_RECORDS=8192;
    private static final int PREINDEX_HARD_ENTRIES=32768;
    // Initial preparation stays bounded even when a remote catalog advertises
    // thousands of covers that the artifact service does not have yet.
    // Successfully persisted files disappear from subsequent passes, so the
    // next launch resumes with the remaining true misses.
    private static final int WARM_REMOTE_ATTEMPTS_PER_LAUNCH=64;
    private static final long WARM_WALL_NANOS=TimeUnit.SECONDS.toNanos(20);
    public interface PreviousCovers {
        byte[] find(String coverId,long revision) throws IOException;
        /** Exact private legacy path; revision and a bounded image signature are already proved. */
        default Path exactPath(String coverId,long revision) throws IOException{return null;}
        /** Creates a cheap canonical view when the legacy cache can prove an exact revision. */
        default boolean link(String coverId,long revision,Path destination) throws IOException{return false;}
        /** Aggregate counters only. Implementations must never expose identifiers or paths. */
        default String diagnostics(){return "provider=opaque";}
    }
    /** Aggregate, identifier-free evidence from the legacy cache adapter. */
    public String legacyDiagnostics(){return previousCovers==null?"provider=none":previousCovers.diagnostics();}
    public interface ImageValidator { void validate(byte[] bytes) throws IOException; }
    public interface Waiter { void waitMillis(long millis) throws InterruptedException; }
    private static final class Checked {
        final long size,modified;final boolean fullyValidated;
        Checked(BasicFileAttributes a) {this(a,true);}
        Checked(BasicFileAttributes a,boolean fullyValidated) {size=a.size();modified=a.lastModifiedTime().toMillis();this.fullyValidated=fullyValidated;}
        Checked(long size,long modified,boolean fullyValidated) {this.size=size;this.modified=modified;this.fullyValidated=fullyValidated;}
        boolean matches(BasicFileAttributes a) {return size==a.size() && modified==a.lastModifiedTime().toMillis();}
        boolean same(Checked other){return other!=null&&size==other.size&&modified==other.modified&&fullyValidated==other.fullyValidated;}
    }
    private final Path directory;
    private final Path validationLedger;
    private final Path legacyValidationLedger;
    private final StationApi api;
    private final StationSessions sessions;
    private final StationApi.Clock clock;

    private final ImageValidator validator;
    private final PreviousCovers previousCovers;
    private final int preindexHardEntries;
    private long blockedUntil;
    private final Object state=new Object();
    private final Object ledgerState=new Object();
    private int ledgerRecords;
    private boolean cachePreindexAttempted,cachePreindexed;
    private final Map<String,Path> warmPaths=new HashMap<>();
    private final Map<String,Checked> legacyWarmMetadata=new HashMap<>();
    private static final class KeyLock {final ReentrantLock lock=new ReentrantLock();int users;}
    private final Map<String,KeyLock> keys=new HashMap<>();
    public static final class Deferred extends IOException {
        public final long retryMillis;public final boolean rateLimited;
        Deferred(long retryMillis,boolean rateLimited){super("Cover temporarily unavailable");this.retryMillis=Math.max(1,retryMillis);this.rateLimited=rateLimited;}
    }
    /** Startup scan result. No bitmap is decoded by this operation. */
    public static final class PreindexResult {
        public final boolean performed;public final int entries,accepted,rejected,legacyCandidates,legacyLinked,legacyDirect,legacyMissed;public final long elapsedNanos;
        PreindexResult(boolean performed,int entries,int accepted,int rejected,int legacyCandidates,int legacyLinked,int legacyDirect,int legacyMissed,long elapsedNanos){
            this.performed=performed;this.entries=entries;this.accepted=accepted;this.rejected=rejected;
            this.legacyCandidates=legacyCandidates;this.legacyLinked=legacyLinked;this.legacyDirect=legacyDirect;this.legacyMissed=legacyMissed;this.elapsedNanos=elapsedNanos;
        }
    }
    public static final class WarmResult {
        public final int total,alreadyWarm,downloaded;public final boolean stopped;public final long elapsedNanos;
        WarmResult(int total,int alreadyWarm,int downloaded,boolean stopped,long elapsedNanos){this.total=total;this.alreadyWarm=alreadyWarm;this.downloaded=downloaded;this.stopped=stopped;this.elapsedNanos=elapsedNanos;}
    }
    public static final class CoverIdentity {
        public final String coverId;public final long revision;
        public CoverIdentity(String coverId,long revision) throws IOException {
            this.coverId=StationCatalog.libraryId(coverId);if(revision<1)throw new IOException("Invalid cover revision");this.revision=revision;
        }
    }
    public interface PreindexProgress {void update(int done,int total);}
    public interface WarmGuard {void check() throws java.io.InterruptedIOException;}
    private KeyLock key(String id){synchronized(state){KeyLock value=keys.get(id);if(value==null){value=new KeyLock();keys.put(id,value);}value.users++;return value;}}
    private void release(String id,KeyLock value){synchronized(state){if(--value.users==0)keys.remove(id);}}
    private void remember(String coverId,long revision,String key,Path file)throws IOException {
        Checked value=new Checked(Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS));
        synchronized(state){checked.put(key,value);warmPaths.put(key,file);unavailable.remove(key);}
        persistValidation(coverId,revision,key,value);
    }
    private void rememberLegacyWarm(String key,Path path)throws IOException {
        BasicFileAttributes a=Files.readAttributes(path,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        if(!a.isRegularFile()||a.size()<1||a.size()>StationProtocol.COVER_BODY_BYTES||!supportedImagePrefix(path))throw new IOException("Invalid legacy cover");
        synchronized(state){warmPaths.put(key,path);legacyWarmMetadata.put(key,new Checked(a,false));}
    }
    private Path currentWarmPath(String key){
        Path path;Checked legacy;synchronized(state){path=warmPaths.get(key);legacy=legacyWarmMetadata.get(key);}if(path==null)return null;if(legacy==null)return path;
        try{BasicFileAttributes a=Files.readAttributes(path,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);if(a.isRegularFile()&&legacy.matches(a))return path;}catch(IOException missing){}
        synchronized(state){warmPaths.remove(key);legacyWarmMetadata.remove(key);}return null;
    }

    private final Map<String,Checked> checked=new LinkedHashMap<String,Checked>(4096,0.75f,true) {
        protected boolean removeEldestEntry(Map.Entry<String,Checked> e) {return size()>4096;}
    };
    private final Map<String,Checked> persisted=new LinkedHashMap<String,Checked>(4096,0.75f,true) {
        protected boolean removeEldestEntry(Map.Entry<String,Checked> e) {return size()>LEDGER_HARD_RECORDS;}
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
        this(directory,api,sessions,clock,waiter,validator,previousCovers,PREINDEX_HARD_ENTRIES);
    }
    /** Package-private bounded constructor used only by the host overflow fixture. */
    StationCoverStore(Path directory,StationApi api,StationSessions sessions,
            StationApi.Clock clock,Waiter waiter,ImageValidator validator,PreviousCovers previousCovers,
            int preindexHardEntries) throws IOException {
        if(preindexHardEntries<1||preindexHardEntries>PREINDEX_HARD_ENTRIES)throw new IllegalArgumentException("Invalid cover preindex limit");
        this.preindexHardEntries=preindexHardEntries;
        this.previousCovers=previousCovers;
        Files.createDirectories(directory);this.directory=directory.toRealPath();
        // R113's v1 file means "fully decoded". R114 never weakens that
        // contract because an older APK could read it after a downgrade.
        this.legacyValidationLedger=this.directory.resolve(".validated-covers-v1.tsv");
        this.validationLedger=this.directory.resolve(".cover-index-v2.tsv");
        this.api=api;this.sessions=sessions;this.clock=clock;this.validator=validator;
        loadValidationLedger(legacyValidationLedger,true);
        loadValidationLedger(validationLedger,false);
        try {if(ledgerNeedsCompaction())synchronized(ledgerState){compactLedgerLocked();}}
        catch(IOException ignored) {/* A readable ledger remains valid if compaction is unavailable. */}
    }

    /**
     * Returns a path from either a previous full validation or the current
     * process-wide private-cache snapshot. Publication is O(1) after preindex and
     * never reads or decodes image bytes per catalog item.
     */
    public Path validatedCachedPath(String coverId,long revision) {
        try {
            StationCatalog.libraryId(coverId);if(revision<1)return null;
            String key=coverId+"-"+revision;Checked proof;boolean indexed;Path warm=currentWarmPath(key);
            synchronized(state){proof=persisted.get(key);indexed=cachePreindexed;}
            if(warm!=null)return warm;
            if(proof==null)return null;
            // A v2 metadata record is usable only after this process completes
            // its own full directory snapshot. If that scan failed, only the
            // stronger R113/v2-V proof may bypass the four-worker pipeline.
            if(!indexed&&!proof.fullyValidated)return null;
            Path file=directory.resolve(key+".img");
            // The process-wide snapshot just checked every path with NOFOLLOW.
            // All app writes are same-directory atomic replacements and remember()
            // updates the in-memory proof, so publication is O(1) after preindex.
            if(indexed){if(proof.fullyValidated)synchronized(state){checked.put(key,proof);}return file;}
            BasicFileAttributes attributes=Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
            if(!attributes.isRegularFile()||!proof.matches(attributes)){forgetPersisted(key);return null;}
            // A startup proof remains metadata-only for getLocked: any later
            // explicit worker lookup still performs the retained full validation.
            if(proof.fullyValidated)synchronized(state){checked.put(key,proof);}
            return file;
        } catch(NoSuchFileException missing) {forgetPersisted(coverId+"-"+revision);return null;}
        catch(Exception unavailable) {return null;}
    }

    private void forgetPersisted(String key){synchronized(state){persisted.remove(key);checked.remove(key);}}

    private void loadValidationLedger(Path ledger,boolean legacy) {
        if(!Files.isRegularFile(ledger,LinkOption.NOFOLLOW_LINKS))return;
        LinkedHashMap<String,Checked> loaded=new LinkedHashMap<>();
        try {
            long bytes=Files.size(ledger);if(bytes>LEDGER_HARD_BYTES)return;
            try(BufferedReader reader=Files.newBufferedReader(ledger,StandardCharsets.UTF_8)) {
                String line;int count=0;
                while((line=reader.readLine())!=null) {
                    if(++count>LEDGER_HARD_RECORDS){loaded.clear();return;}
                    String[] fields=line.split("\\t",-1);if(legacy?fields.length!=4:fields.length!=5)continue;
                    try {
                        String coverId=StationCatalog.libraryId(fields[0]);
                        long revision=Long.parseLong(fields[1]);
                        long size=Long.parseLong(fields[2]);
                        long modified=Long.parseLong(fields[3]);
                        if(revision<1||size<1||size>StationProtocol.COVER_BODY_BYTES||modified<1)continue;
                        boolean fullyValidated=legacy||fields[4].equals("V");
                        if(!legacy&&!fullyValidated&&!fields[4].equals("M"))continue;
                        loaded.put(coverId+"-"+revision,new Checked(size,modified,fullyValidated));
                    } catch(Exception invalid) {/* A damaged record cannot authorize a path. */}
                }
                if(!legacy)ledgerRecords=count;
            }
        } catch(IOException unreadable) {return;}
        synchronized(state){for(Map.Entry<String,Checked> entry:loaded.entrySet()){
            Checked previous=persisted.get(entry.getKey()),value=entry.getValue();
            if(previous!=null&&previous.fullyValidated&&!value.fullyValidated&&previous.size==value.size&&previous.modified==value.modified)value=previous;
            persisted.put(entry.getKey(),value);if(value.fullyValidated)checked.put(entry.getKey(),value);
        }}
    }

    private void persistValidation(String coverId,long revision,String key,Checked value) {
        synchronized(ledgerState) {
            Checked previous; synchronized(state){previous=persisted.get(key);}
            if(value.same(previous))return;
            String record=coverId+'\t'+Long.toString(revision)+'\t'+Long.toString(value.size)+'\t'+Long.toString(value.modified)+'\t'+(value.fullyValidated?'V':'M')+'\n';
            try {
                if(Files.exists(validationLedger,LinkOption.NOFOLLOW_LINKS)&&
                   !Files.isRegularFile(validationLedger,LinkOption.NOFOLLOW_LINKS))return;
                Set<OpenOption> options=new HashSet<>();
                Collections.addAll(options,StandardOpenOption.CREATE,StandardOpenOption.WRITE,
                    StandardOpenOption.APPEND,LinkOption.NOFOLLOW_LINKS);
                ByteBuffer bytes=ByteBuffer.wrap(record.getBytes(StandardCharsets.UTF_8));
                try(SeekableByteChannel channel=Files.newByteChannel(validationLedger,options)){
                    while(bytes.hasRemaining())channel.write(bytes);
                }
                ledgerRecords++;synchronized(state){persisted.put(key,value);}
                if(ledgerNeedsCompaction())compactLedgerLocked();
            } catch(IOException ignored) {/* The cover remains usable; only warm publication is disabled. */}
        }
    }

    /** Rewrites only the latest bounded proof for each key; caller holds ledgerState. */
    private void compactLedgerLocked() throws IOException {
        LinkedHashMap<String,Checked> snapshot;
        synchronized(state){snapshot=new LinkedHashMap<>(persisted);}
        rewriteLedgerLocked(snapshot);
    }
    /** Persists a supplied complete snapshot before it can become publishable. */
    private void rewriteLedgerLocked(LinkedHashMap<String,Checked> snapshot) throws IOException {
        Path temporary=Files.createTempFile(directory,".cover-index-",".tmp");boolean moved=false;
        try {
            try(BufferedWriter writer=Files.newBufferedWriter(temporary,StandardCharsets.UTF_8,
                    StandardOpenOption.TRUNCATE_EXISTING,StandardOpenOption.WRITE)) {
                for(Map.Entry<String,Checked> entry:snapshot.entrySet()) {
                    String key=entry.getKey();int separator=key.lastIndexOf('-');
                    if(separator<1||separator==key.length()-1)continue;
                    Checked value=entry.getValue();
                    writer.write(key,0,separator);writer.write('\t');writer.write(key.substring(separator+1));writer.write('\t');
                    writer.write(Long.toString(value.size));writer.write('\t');writer.write(Long.toString(value.modified));writer.write('\t');
                    writer.write(value.fullyValidated?'V':'M');writer.write('\n');
                }
            }
            try {Files.move(temporary,validationLedger,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
            catch(AtomicMoveNotSupportedException unsupported){Files.move(temporary,validationLedger,StandardCopyOption.REPLACE_EXISTING);}
            moved=true;ledgerRecords=snapshot.size();
        } finally {if(!moved)Files.deleteIfExists(temporary);}
    }
    private boolean ledgerNeedsCompaction() throws IOException {
        if(!Files.isRegularFile(validationLedger,LinkOption.NOFOLLOW_LINKS))return false;
        int live;synchronized(state){live=persisted.size();}
        long recordLimit=Math.min(LEDGER_HARD_RECORDS,Math.max(LEDGER_COMPACT_RECORDS,(long)live+4096L));
        long byteLimit=Math.max(LEDGER_COMPACT_BYTES,512L*1024L+160L*live);
        return ledgerRecords>=recordLimit||Files.size(validationLedger)>=byteLimit;
    }

    /**
     * Indexes every canonical cover already present in the private cache using
     * directory metadata and a 12-byte format signature only. The complete scan
     * runs once per process while the initial library loading screen is active.
     * It performs no image hash or bitmap decode and persists the whole result
     * with one same-directory replacement that requests atomic move and has a platform fallback.
     */
    public PreindexResult preindexCached() throws IOException {
        return preindexCached(Collections.emptyList(),null);
    }
    public PreindexResult preindexCached(List<CoverIdentity> catalog,PreindexProgress progress) throws IOException {
        if(catalog==null)throw new IllegalArgumentException("Missing cover catalog");
        boolean repeated;synchronized(state){repeated=cachePreindexAttempted;if(!repeated)cachePreindexAttempted=true;}
        if(repeated){
            int candidates=0,direct=0,missed=0,done=0,total=catalog.size();
            if(previousCovers!=null)for(CoverIdentity identity:catalog){String key=identity.coverId+"-"+identity.revision;boolean known=currentWarmPath(key)!=null;
                if(!known){candidates++;try{Path exact=previousCovers.exactPath(identity.coverId,identity.revision);if(exact!=null){rememberLegacyWarm(key,exact);direct++;}else missed++;}catch(IOException unavailable){missed++;}}
                done++;if(progress!=null&&(done==total||(done&31)==0))progress.update(done,total);
            }
            return new PreindexResult(false,0,0,0,candidates,0,direct,missed,0);
        }
        long started=System.nanoTime();int entries=0,rejected=0,legacyCandidates=0,legacyLinked=0,legacyDirect=0,legacyMissed=0;
        if(previousCovers!=null&&!catalog.isEmpty()) {
            HashSet<String> seen=new HashSet<>();int done=0,total=catalog.size();
            for(CoverIdentity identity:catalog) {
                String key=identity.coverId+"-"+identity.revision;Path destination=directory.resolve(key+".img");
                if(seen.add(key)&&!Files.exists(destination,LinkOption.NOFOLLOW_LINKS)) {
                    legacyCandidates++;
                    try {Path exact=previousCovers.exactPath(identity.coverId,identity.revision);if(exact!=null){rememberLegacyWarm(key,exact);legacyDirect++;}else legacyMissed++;}
                    catch(IOException|UnsupportedOperationException|SecurityException unavailable){legacyMissed++;}
                }
                done++;if(progress!=null&&(done==total||(done&31)==0))progress.update(done,total);
            }
        }
        LinkedHashMap<String,Checked> discovered=new LinkedHashMap<>();
        try(DirectoryStream<Path> stream=Files.newDirectoryStream(directory)) {
            for(Path candidate:stream) {
                if(++entries>preindexHardEntries)throw new IOException("Cover cache entry limit exceeded");
                String filename=candidate.getFileName().toString();
                if(!filename.endsWith(".img")){continue;}
                String stem=filename.substring(0,filename.length()-4);int separator=stem.lastIndexOf('-');
                if(separator<1||separator==stem.length()-1){rejected++;continue;}
                try {
                    String coverId=StationCatalog.libraryId(stem.substring(0,separator));
                    long revision=Long.parseLong(stem.substring(separator+1));
                    if(revision<1||!(coverId+"-"+revision).equals(stem)){rejected++;continue;}
                    BasicFileAttributes attributes=Files.readAttributes(candidate,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
                    long size=attributes.size(),modified=attributes.lastModifiedTime().toMillis();
                    if(!attributes.isRegularFile()||size<1||size>StationProtocol.COVER_BODY_BYTES||modified<1||!supportedImagePrefix(candidate)){rejected++;continue;}
                    discovered.put(stem,new Checked(size,modified,false));
                } catch(Exception invalid){rejected++;}
            }
        }
        boolean changed=false;
        synchronized(ledgerState) {
            LinkedHashMap<String,Checked> snapshot=new LinkedHashMap<>();
            synchronized(state) {
                for(Map.Entry<String,Checked> entry:discovered.entrySet()) {
                    Checked existing=persisted.get(entry.getKey()),metadata=entry.getValue();
                    // Preserve the stronger R113 proof when its metadata still matches.
                    snapshot.put(entry.getKey(),existing!=null&&existing.size==metadata.size&&existing.modified==metadata.modified?existing:metadata);
                }
                if(persisted.size()!=snapshot.size())changed=true;
                else for(Map.Entry<String,Checked> entry:snapshot.entrySet())if(!entry.getValue().same(persisted.get(entry.getKey()))){changed=true;break;}
            }
            // Commit the durable snapshot first. If this fails, metadata-only M
            // proofs remain unavailable and the four-worker path stays active.
            if(changed) {
                if(Files.exists(validationLedger,LinkOption.NOFOLLOW_LINKS)&&
                        !Files.isRegularFile(validationLedger,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid cover index path");
                rewriteLedgerLocked(snapshot);
            }
            synchronized(state) {
                // Replace instead of merge: a removed or renamed cache file must
                // never survive as a stale warm path from either ledger version.
                persisted.clear();checked.clear();
                for(Map.Entry<String,Checked> entry:snapshot.entrySet()){
                    persisted.put(entry.getKey(),entry.getValue());warmPaths.put(entry.getKey(),directory.resolve(entry.getKey()+".img"));if(entry.getValue().fullyValidated)checked.put(entry.getKey(),entry.getValue());
                }
                cachePreindexed=true;
            }
        }
        return new PreindexResult(true,entries,discovered.size(),rejected,legacyCandidates,legacyLinked,legacyDirect,legacyMissed,System.nanoTime()-started);
    }

    /** Reads at most the 12-byte format signature; it never decodes a bitmap. */
    private static boolean supportedImagePrefix(Path file) {
        Set<OpenOption> options=new HashSet<>();Collections.addAll(options,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS);
        ByteBuffer prefix=ByteBuffer.allocate(12);
        try(SeekableByteChannel channel=Files.newByteChannel(file,options)) {
            while(prefix.hasRemaining()&&channel.read(prefix)>0){}
            StationFiles.imageExtension(Arrays.copyOf(prefix.array(),prefix.position()));return true;
        } catch(IOException invalid){return false;}
    }
    /**
     * Completes true cache misses in catalog order with one session and one
     * request in flight. The first connectivity/auth/rate failure ends this
     * launch's pass; persisted successes are resumed, never repeated, next run.
     */
    public WarmResult warmCatalogSequential(List<CoverIdentity> catalog,PreindexProgress progress,StationApi.Cancellation cancel) throws Exception {
        return warmCatalogSequential(catalog,progress,cancel,cancel::check);
    }
    public WarmResult warmCatalogSequential(List<CoverIdentity> catalog,PreindexProgress progress,StationApi.Cancellation cancel,WarmGuard guard) throws Exception {
        if(catalog==null||cancel==null||guard==null)throw new IllegalArgumentException("Missing cover warmup input");
        LinkedHashMap<String,CoverIdentity> unique=new LinkedHashMap<>();for(CoverIdentity identity:catalog)unique.put(identity.coverId+"-"+identity.revision,identity);
        long started=System.nanoTime();int done=0,already=0,downloaded=0,remoteAttempts=0;boolean stopped=false;StationSessions.Lease lease=null;
        try {
            for(Map.Entry<String,CoverIdentity> entry:unique.entrySet()) {
                guard.check();cancel.check();CoverIdentity identity=entry.getValue();
                if(validatedCachedPath(identity.coverId,identity.revision)!=null)already++;
                else {
                    if(api==null||sessions==null){stopped=true;break;}
                    if(remoteAttempts>=WARM_REMOTE_ATTEMPTS_PER_LAUNCH||System.nanoTime()-started>=WARM_WALL_NANOS){stopped=true;break;}
                    remoteAttempts++;
                    try {
                        if(lease==null)lease=sessions.acquire(cancel);
                        Path path=get(lease.session,identity.coverId,identity.revision,cancel);
                        if(path==null){stopped=true;break;}downloaded++;
                    } catch(java.io.InterruptedIOException cancelled) {throw cancelled;}
                    catch(StationApi.Failure failure) {if(failure.status!=404){stopped=true;break;}}
                    catch(Deferred deferred) {if(deferred.rateLimited){stopped=true;break;}}
                    catch(IOException network) {stopped=true;break;}
                }
                done++;if(progress!=null&&(done==unique.size()||(done&7)==0))progress.update(done,unique.size());
            }
        } finally {if(lease!=null)lease.close();}
        return new WarmResult(unique.size(),already,downloaded,stopped,System.nanoTime()-started);
    }
    public Path get(String coverId,long revision,StationApi.Cancellation cancel) throws Exception {
        Path cached=cached(coverId,revision,cancel);if(cached!=null)return cached;
        try(StationSessions.Lease lease=sessions.acquire(cancel)){return get(lease.session,coverId,revision,cancel);}
    }
    public Path cached(String coverId,long revision,StationApi.Cancellation cancel)throws Exception {
        return get(null,coverId,revision,cancel);
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
        Path warm=currentWarmPath(key);boolean directLegacy;synchronized(state){directLegacy=legacyWarmMetadata.containsKey(key);}
        // Canonical metadata-only warm paths are publishable after the bounded
        // snapshot, but an explicit cache worker still performs the retained
        // full validation once. Exact legacy paths cannot be rewritten and
        // retain their already-proved revision/type/signature contract.
        if(warm!=null&&directLegacy){StationDiagnostics.record(StationDiagnostics.Event.COVER_CACHE,0,1);return warm;}
        if(Files.exists(file,LinkOption.NOFOLLOW_LINKS)) {
            if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)) {
                // Delete only this canonical private-cache directory entry. Java's
                // delete does not follow a symbolic link; an empty accidental
                // directory is also removable. A non-empty directory stays put
                // and fails closed instead of being recursively removed.
                forgetPersisted(key);Files.delete(file);
            } else {
                BasicFileAttributes attributes=Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
                Checked previous; synchronized(state){previous=checked.get(key);}
                if(previous != null && previous.matches(attributes)){StationDiagnostics.record(StationDiagnostics.Event.COVER_CACHE,0,1);return file;}
                try {
                    byte[] bytes=StationFiles.readBounded(file,StationProtocol.COVER_BODY_BYTES);
                    StationFiles.imageExtension(bytes);validator.validate(bytes);
                    Checked verified=new Checked(attributes);synchronized(state){checked.put(key,verified);}
                    persistValidation(coverId,revision,key,verified);StationDiagnostics.record(StationDiagnostics.Event.COVER_CACHE,0,1);return file;
                } catch(IOException corrupt) {synchronized(state){checked.remove(key);}}
            }
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
                remember(coverId,revision,key,file);
                return file;
            }
        }
        if(session==null)return null; // Cache miss is not authorization to perform a request.
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
        remember(coverId,revision,key,file);
        return file;
    }
}
