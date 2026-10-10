package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;

/** Host fixture for full-validation proofs and the per-process private-cache snapshot. */
public final class StationCoverWarmStartTest {
    private static int checks;
    private static final String COVER="cover_test_1234";
    private static final long REVISION=7L;
    private static final byte[] PNG=new byte[]{(byte)137,80,78,71,13,10,26,10,1,2,3,4};
    private static void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
    private static StationCoverStore store(Path root,int[] validations)throws IOException{
        return new StationCoverStore(root,null,null,()->0L,millis->{},bytes->{validations[0]++;});
    }
    private static StationCoverStore store(Path root,int[] validations,int preindexLimit)throws IOException{
        return new StationCoverStore(root,null,null,()->0L,millis->{},bytes->{validations[0]++;},null,preindexLimit);
    }
    private static StationCoverStore store(Path root,int[] validations,StationCoverStore.PreviousCovers previous)throws IOException{
        return new StationCoverStore(root,null,null,()->0L,millis->{},bytes->{validations[0]++;},previous);
    }
    private static Path image(Path root){return root.resolve(COVER+"-"+REVISION+".img");}
    private static void clear(Path root)throws IOException{
        if(!Files.exists(root))return;
        Files.walk(root).sorted(Comparator.reverseOrder()).forEach(path->{try{Files.delete(path);}catch(IOException e){throw new UncheckedIOException(e);}});
    }
    public static void main(String[] args)throws Exception{
        Path root=Paths.get(args[0]).toAbsolutePath();clear(root);Files.createDirectories(root);Files.write(image(root),PNG);
        StationApi.Cancellation cancel=new StationApi.Cancellation();int[] first={0};StationCoverStore initial=store(root,first);
        check(initial.validatedCachedPath(COVER,REVISION)==null,"An unproved R112 file cannot hide the first R113 validation");
        check(initial.cached(COVER,REVISION,cancel).equals(image(root)),"Existing image validates through the normal cache path");
        check(first[0]==1,"First R113 process performs exactly one full validation");
        Path ledger=root.resolve(".cover-index-v2.tsv");check(Files.isRegularFile(ledger),"Validation creates the private v2 index");

        int[] restarted={0};StationCoverStore second=store(root,restarted);
        check(second.validatedCachedPath(COVER,REVISION).equals(image(root)),"Second process publishes the warm path immediately");
        check(second.cached(COVER,REVISION,cancel).equals(image(root))&&restarted[0]==0,"Persisted size and mtime avoid a second decode");

        Files.write(image(root),new byte[]{(byte)137,80,78,71,13,10,26,10,1,2,3,4,5});
        check(second.validatedCachedPath(COVER,REVISION)==null,"Changed file cannot use an old ledger proof");
        check(second.cached(COVER,REVISION,cancel).equals(image(root))&&restarted[0]==1,"Changed file returns to the full validation path");

        Files.delete(ledger);int[] missing={0};StationCoverStore withoutLedger=store(root,missing);
        check(withoutLedger.validatedCachedPath(COVER,REVISION)==null,"Missing ledger never authorizes a warm path");
        check(withoutLedger.cached(COVER,REVISION,cancel)!=null&&missing[0]==1,"Missing ledger is rebuilt by normal validation");

        BasicFileAttributes attributes=Files.readAttributes(image(root),BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        String valid=COVER+'\t'+REVISION+'\t'+attributes.size()+'\t'+attributes.lastModifiedTime().toMillis()+"\tV\n";
        Files.write(ledger,("bad\trecord\n"+valid+"cover_test_9999\t7\t12\tnot-a-time\n").getBytes(StandardCharsets.UTF_8));
        int[] corrupt={0};StationCoverStore damaged=store(root,corrupt);
        check(damaged.validatedCachedPath(COVER,REVISION).equals(image(root)),"Damaged records do not invalidate a separate exact proof");
        check(damaged.validatedCachedPath("cover_test_9999",REVISION)==null,"A damaged record cannot authorize another cover");

        Files.delete(image(root));check(damaged.validatedCachedPath(COVER,REVISION)==null,"Ledger proof cannot authorize a missing file");
        Files.write(image(root),PNG);attributes=Files.readAttributes(image(root),BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        valid=COVER+'\t'+REVISION+'\t'+attributes.size()+'\t'+attributes.lastModifiedTime().toMillis()+"\tV\n";
        StringBuilder repeated=new StringBuilder(valid.length()*8192);for(int i=0;i<8192;i++)repeated.append(valid);
        Files.write(ledger,repeated.toString().getBytes(StandardCharsets.UTF_8));
        int[] compact={0};StationCoverStore compacted=store(root,compact);
        check(compacted.validatedCachedPath(COVER,REVISION).equals(image(root)),"Ledger at the compaction threshold keeps its latest exact proof");
        check(Files.readAllLines(ledger,StandardCharsets.UTF_8).size()==1,"Ledger compacts duplicate history to one bounded proof");

        Path outside=root.resolve("outside.tsv");Files.write(outside,"outside\n".getBytes(StandardCharsets.UTF_8));Files.delete(ledger);
        boolean symlink=false;
        try{Files.createSymbolicLink(ledger,outside.getFileName());symlink=true;}
        catch(UnsupportedOperationException|IOException|SecurityException unsupported){/* Windows may withhold symlink creation. */}
        if(symlink){
            int[] linked={0};StationCoverStore refused=store(root,linked);
            check(refused.validatedCachedPath(COVER,REVISION)==null,"Ledger symlink is never trusted");
            check(refused.cached(COVER,REVISION,cancel)!=null&&linked[0]==1,"Cover remains usable through normal validation");
            check(new String(Files.readAllBytes(outside),StandardCharsets.UTF_8).equals("outside\n"),"Persistence never follows the ledger symlink");
        }

        // Large startup fixture: all existing cache files are indexed with one
        // metadata pass and one ledger rewrite, without full reads or decoding.
        clear(root);Files.createDirectories(root);final int fixtureCovers=4096;
        for(int i=0;i<fixtureCovers;i++)Files.write(root.resolve(String.format(Locale.ROOT,"cover_%08d-7.img",i)),PNG);
        Files.write(root.resolve("cover_zero00-1.img"),new byte[0]);
        Files.createDirectory(root.resolve("cover_folder0-1.img"));
        Files.write(root.resolve("not-a-cover.img"),PNG);
        Files.write(root.resolve("cover_invalid0-1.img"),"invalid".getBytes(StandardCharsets.UTF_8));
        Path legacyFile=root.resolve("cover_00000001-7.img");
        BasicFileAttributes legacyAttributes=Files.readAttributes(legacyFile,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        String legacyCurrent="cover_00000001\t7\t"+legacyAttributes.size()+'\t'+legacyAttributes.lastModifiedTime().toMillis()+'\n';
        String legacyStale="cover_stale00\t7\t12\t1\n";
        Path legacyLedger=root.resolve(".validated-covers-v1.tsv");Files.write(legacyLedger,(legacyCurrent+legacyStale).getBytes(StandardCharsets.UTF_8));
        int[] indexedValidations={0};StationCoverStore indexed=store(root,indexedValidations);
        long hostStarted=System.nanoTime();StationCoverStore.PreindexResult result=indexed.preindexCached();
        long hostElapsed=System.nanoTime()-hostStarted;
        check(result.performed,"The startup cache index runs once");
        check(result.accepted==fixtureCovers,"Every canonical cached cover is indexed");
        check(result.rejected==4,"Invalid name, empty file, directory and unsupported image signature are rejected");
        check(indexedValidations[0]==0,"Startup indexing never decodes image bytes");
        check(result.elapsedNanos>0&&hostElapsed<30_000_000_000L,"The bounded 4096-cover metadata fixture completes without an unbounded stall");
        Path sample=root.resolve("cover_00002048-7.img");
        check(indexed.validatedCachedPath("cover_00002048",7).equals(sample),"Indexed metadata is available to the initial catalog publication");
        check(indexed.validatedCachedPath("cover_stale00",7)==null,"A stale R113 proof is removed by the complete directory snapshot");
        check(!indexed.preindexCached().performed,"The directory is scanned only once per process");
        List<String> indexedLedger=Files.readAllLines(root.resolve(".cover-index-v2.tsv"),StandardCharsets.UTF_8);
        check(indexedLedger.size()==fixtureCovers,"The whole fixture is persisted by one compact ledger");
        check(indexedLedger.stream().anyMatch(line->line.endsWith("\tM")),"Startup records are explicitly metadata-only");
        check(indexedLedger.stream().anyMatch(line->line.startsWith("cover_00000001\t7\t")&&line.endsWith("\tV")),"An exact R113 decode proof keeps its stronger meaning");
        check(new String(Files.readAllBytes(legacyLedger),StandardCharsets.UTF_8).equals(legacyCurrent+legacyStale),"R114 never rewrites the R113 ledger used by a downgrade");

        int[] metadataFallback={0};StationCoverStore afterIndexRestart=store(root,metadataFallback);
        check(afterIndexRestart.validatedCachedPath("cover_00002048",7)==null,"A v2 metadata record is not trusted before this process scans the directory");
        check(afterIndexRestart.preindexCached().performed,"A restarted process rebuilds its own exact cache snapshot");
        check(afterIndexRestart.validatedCachedPath("cover_00002048",7).equals(sample),"Metadata index is published after the restarted process completes its scan");
        check(afterIndexRestart.cached("cover_00002048",7,cancel).equals(sample)&&metadataFallback[0]==1,
            "A later explicit cache lookup fully validates metadata-only proof instead of upgrading it implicitly");
        int[] upgraded={0};StationCoverStore afterUpgrade=store(root,upgraded);
        check(afterUpgrade.cached("cover_00002048",7,cancel).equals(sample)&&upgraded[0]==0,
            "The successful fallback upgrades that exact file to a full validation proof");

        // A bounded-scan failure is fail-safe and terminal for this process: it
        // does not publish M proofs and it does not rescan on every catalog refresh.
        clear(root);Files.createDirectories(root);
        Path limitOne=root.resolve("cover_limit001-7.img");Path limitTwo=root.resolve("cover_limit002-7.img");
        Files.write(limitOne,PNG);Files.write(limitTwo,PNG);Files.write(root.resolve("cover_limit003-7.img"),PNG);
        BasicFileAttributes limitOneAttrs=Files.readAttributes(limitOne,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        BasicFileAttributes limitTwoAttrs=Files.readAttributes(limitTwo,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        Files.write(root.resolve(".cover-index-v2.tsv"),("cover_limit001\t7\t"+limitOneAttrs.size()+"\t"+
            limitOneAttrs.lastModifiedTime().toMillis()+"\tM\n").getBytes(StandardCharsets.UTF_8));
        Files.write(root.resolve(".validated-covers-v1.tsv"),("cover_limit002\t7\t"+limitTwoAttrs.size()+"\t"+
            limitTwoAttrs.lastModifiedTime().toMillis()+"\n").getBytes(StandardCharsets.UTF_8));
        int[] overflowValidations={0};StationCoverStore overflow=store(root,overflowValidations,2);
        check(overflow.validatedCachedPath("cover_limit001",7)==null,"A loaded M proof stays private before the process snapshot");
        check(overflow.validatedCachedPath("cover_limit002",7).equals(limitTwo),"A loaded full V proof remains available before the process snapshot");
        boolean overflowThrown=false;
        try{overflow.preindexCached();}catch(IOException expected){overflowThrown=true;}
        check(overflowThrown,"A directory beyond the configured hard bound aborts the snapshot");
        check(overflow.validatedCachedPath("cover_limit001",7)==null,"A partial overflow scan never publishes its loaded metadata proof");
        check(overflow.validatedCachedPath("cover_limit002",7).equals(limitTwo),"A failed snapshot does not discard an existing full proof");
        check(!overflow.preindexCached().performed,"A failed bounded scan is not repeated in the same process");
        check(overflow.cached("cover_limit001",7,cancel)!=null&&overflowValidations[0]==1,
            "After overflow, the retained explicit cache path still performs full validation");

        clear(root);Files.createDirectories(root);
        Path invalidPath=root.resolve(COVER+"-"+REVISION+".img");Files.createDirectory(invalidPath);
        int[] pathValidations={0};StationCoverStore removablePath=store(root,pathValidations);
        check(removablePath.cached(COVER,REVISION,cancel)==null&&!Files.exists(invalidPath,LinkOption.NOFOLLOW_LINKS),
            "An empty directory at the canonical cover path is removed without recursive traversal");
        Files.createDirectory(invalidPath);Files.write(invalidPath.resolve("keep.txt"),new byte[]{1});
        boolean nonEmptyRefused=false;
        try{removablePath.cached(COVER,REVISION,cancel);}catch(IOException expected){nonEmptyRefused=true;}
        check(nonEmptyRefused&&Files.isDirectory(invalidPath,LinkOption.NOFOLLOW_LINKS),
            "A non-empty invalid directory fails closed and is never recursively deleted");

        clear(root);Files.createDirectories(root);Files.write(image(root),PNG);
        Files.createDirectory(root.resolve(".cover-index-v2.tsv"));
        int[] persistFailureValidations={0};StationCoverStore persistFailure=store(root,persistFailureValidations);
        boolean persistFailureThrown=false;
        try{persistFailure.preindexCached();}catch(IOException expected){persistFailureThrown=true;}
        check(persistFailureThrown,"A non-regular v2 ledger makes the startup snapshot fail closed");
        check(persistFailure.validatedCachedPath(COVER,REVISION)==null,"An unpersisted metadata snapshot is never made publishable in memory");

        clear(root);Files.createDirectories(root);
        Path legacy=root.resolveSibling(root.getFileName()+"-legacy");clear(legacy);Files.createDirectories(legacy);
        Path legacyImage=legacy.resolve(COVER+".png");Files.write(legacyImage,PNG);
        Files.write(legacy.resolve("revisions.tsv"),(COVER+"\t"+REVISION+"\n").getBytes(StandardCharsets.UTF_8));
        int[] legacyValidations={0};StationCoverStore legacyStore=store(root,legacyValidations,new ExistingCoverCache(legacy));
        List<StationCoverStore.CoverIdentity> legacyCatalog=Arrays.asList(
            new StationCoverStore.CoverIdentity(COVER,REVISION),new StationCoverStore.CoverIdentity(COVER,REVISION+1));
        int[] progress={0,0};StationCoverStore.PreindexResult legacyResult=legacyStore.preindexCached(legacyCatalog,(done,total)->{progress[0]=done;progress[1]=total;});
        Path canonical=image(root);
        check(legacyResult.legacyCandidates==2&&legacyResult.legacyDirect==1&&legacyResult.legacyLinked==0&&legacyResult.legacyMissed==1,
            "Only the exact legacy identity becomes a direct private-cache warm path");
        check(progress[0]==2&&progress[1]==2,"Legacy migration reports initial-loading progress through the complete catalog");
        check(legacyValidations[0]==0,"Legacy preindex never invokes the bitmap validator");
        check(Files.isRegularFile(legacyImage,LinkOption.NOFOLLOW_LINKS),"Legacy source remains read-only and present");
        check(!Files.exists(canonical,LinkOption.NOFOLLOW_LINKS),"Direct legacy exposure never copies or links the image");
        check(legacyStore.validatedCachedPath(COVER,REVISION).equals(legacyImage),"Exact legacy cover is published from its existing private path");
        Files.delete(legacyImage);
        check(legacyStore.validatedCachedPath(COVER,REVISION)==null,"A deleted direct legacy file is rejected immediately");
        check(!Files.exists(root.resolve(COVER+"-"+(REVISION+1)+".img"),LinkOption.NOFOLLOW_LINKS),"Revision mismatch never links a legacy cover");
        clear(root);clear(legacy);Files.createDirectories(root);

        int[] fallbackValidations={0};StationCoverStore.PreviousCovers fallback=(coverId,revision)->PNG;
        StationCoverStore fallbackStore=store(root,fallbackValidations,fallback);
        StationCoverStore.PreindexResult fallbackResult=fallbackStore.preindexCached(
            Collections.singletonList(new StationCoverStore.CoverIdentity(COVER,REVISION)),null);
        check(fallbackResult.legacyCandidates==1&&fallbackResult.legacyDirect==0&&fallbackResult.legacyLinked==0&&fallbackResult.legacyMissed==1,
            "A provider without an exact private path stays cold without copying during startup");
        check(fallbackStore.validatedCachedPath(COVER,REVISION)==null,"Legacy byte fallback stays on the explicit validation worker");
        check(fallbackStore.cached(COVER,REVISION,cancel).equals(image(root))&&fallbackValidations[0]==1,
            "The retained explicit worker imports and fully validates a legacy cover after direct-path fallback");

        clear(root);System.out.println("PASS "+checks+" cover warm-start checks; ledger-symlink="+(symlink?"executed":"unsupported")+
            "; legacy-direct=executed; preindex4096Ms="+(result.elapsedNanos/1_000_000L));
    }
}
