package org.emulationstation.frontend.station;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.attribute.BasicFileAttributes;
import java.nio.file.*;
import java.util.*;

/**
 * Read-only migration from the historical station-covers cache.
 *
 * The historical writer stored {@code coverId<TAB>itemRevision} in
 * revisions.tsv and one image named {@code coverId.extension}. A legacy image
 * is never authorized by its filename alone: table revision, a bounded regular
 * file and an image signature must all agree. Diagnostics contain aggregate
 * counters only; identifiers and private paths never leave this class.
 */
public final class ExistingCoverCache implements StationCoverStore.PreviousCovers {
    private static final int TABLE_HARD_BYTES=1024*1024;
    private static final int DIRECTORY_HARD_ENTRIES=32768;
    private static final Set<String> IMAGE_EXTENSIONS=Collections.unmodifiableSet(
        new HashSet<>(Arrays.asList("png","jpg","jpeg","webp","gif")));

    private final Path directory;
    private final Map<String,Long> revisions=new HashMap<>();
    private final Map<String,Path> images=new HashMap<>();
    private final Object statistics=new Object();
    private String tableStatus="not-scanned";
    private long tableBytes;
    private int tableLines,tableInvalidLines,tableDuplicateLines,tableConflicts;
    private int directoryEntries,regularFiles,imageFiles,invalidImageNames,unsupportedExtensions,imageConflicts;
    private int revisionWithoutImage,imageWithoutRevision;
    private int lookups,revisionMissing,revisionMismatch,matchingRevisionNoImage,fileRejected,accepted;

    public ExistingCoverCache(Path directory) throws IOException {
        this.directory=directory.toAbsolutePath().normalize();
        readRevisionTable();
        indexImages();
        for(String id:revisions.keySet())if(!images.containsKey(id))revisionWithoutImage++;
        for(String id:images.keySet())if(!revisions.containsKey(id))imageWithoutRevision++;
    }

    private void readRevisionTable() {
        if(!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS)){tableStatus="directory-missing";return;}
        Path table=directory.resolve("revisions.tsv");
        if(!Files.exists(table,LinkOption.NOFOLLOW_LINKS)){tableStatus="table-missing";return;}
        if(!Files.isRegularFile(table,LinkOption.NOFOLLOW_LINKS)){tableStatus="table-not-regular";return;}
        try {
            tableBytes=Files.size(table);
            if(tableBytes>TABLE_HARD_BYTES){tableStatus="table-too-large";return;}
            String text=new String(StationFiles.readBounded(table,TABLE_HARD_BYTES),StandardCharsets.UTF_8);
            HashSet<String> ambiguous=new HashSet<>();
            for(String line:text.split("\n",-1)) {
                if(line.isEmpty())continue;
                tableLines++;
                String[] fields=line.split("\t",-1);
                if(fields.length!=2){tableInvalidLines++;continue;}
                String id;
                try {id=StationCatalog.libraryId(fields[0]);}
                catch(IOException invalid){tableInvalidLines++;continue;}
                long revision;
                try {revision=Long.parseLong(fields[1].trim());}
                catch(NumberFormatException invalid){tableInvalidLines++;continue;}
                if(revision<1){tableInvalidLines++;continue;}
                Long old=revisions.put(id,revision);
                if(old!=null&&old.longValue()==revision)tableDuplicateLines++;
                else if(old!=null){ambiguous.add(id);tableConflicts++;}
            }
            for(String id:ambiguous)revisions.remove(id);
            tableStatus="parsed";
        } catch(IOException unreadable) {
            revisions.clear();tableStatus="table-unreadable";
        }
    }

    /** Indexes names and metadata once. The signature remains checked at use. */
    private void indexImages() {
        if(!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS))return;
        HashSet<String> ambiguous=new HashSet<>();
        try(DirectoryStream<Path> stream=Files.newDirectoryStream(directory)) {
            for(Path candidate:stream) {
                if(++directoryEntries>DIRECTORY_HARD_ENTRIES){tableStatus="directory-too-large";images.clear();return;}
                String filename=candidate.getFileName().toString();
                if(filename.equals("revisions.tsv")||filename.startsWith("."))continue;
                BasicFileAttributes attributes;
                try {attributes=Files.readAttributes(candidate,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);}
                catch(IOException unreadable){continue;}
                if(!attributes.isRegularFile())continue;
                regularFiles++;
                int dot=filename.lastIndexOf('.');
                if(dot<1||dot==filename.length()-1){invalidImageNames++;continue;}
                String id=filename.substring(0,dot),extension=filename.substring(dot+1).toLowerCase(Locale.ROOT);
                try {StationCatalog.libraryId(id);}catch(IOException invalid){invalidImageNames++;continue;}
                if(!IMAGE_EXTENSIONS.contains(extension)){unsupportedExtensions++;continue;}
                if(attributes.size()<1||attributes.size()>StationProtocol.COVER_BODY_BYTES){invalidImageNames++;continue;}
                Path normalized=candidate.toAbsolutePath().normalize();
                if(!directory.equals(normalized.getParent())){invalidImageNames++;continue;}
                imageFiles++;
                Path old=images.put(id,normalized);
                if(old!=null&&!old.equals(normalized)){ambiguous.add(id);imageConflicts++;}
            }
        } catch(IOException unreadable) {
            images.clear();tableStatus="directory-unreadable";
        }
        for(String id:ambiguous)images.remove(id);
    }

    @Override public byte[] find(String coverId,long revision) throws IOException {
        Path file=exactPath(coverId,revision);if(file==null)return null;
        byte[] bytes=StationFiles.readBounded(file,StationProtocol.COVER_BODY_BYTES);
        StationFiles.imageExtension(bytes);return bytes;
    }

    /** Returns the exact legacy private file after proving revision, type, size and signature. */
    @Override public Path exactPath(String coverId,long revision) throws IOException {
        StationCatalog.libraryId(coverId);Long stored=revisions.get(coverId);
        synchronized(statistics){lookups++;}
        if(stored==null){synchronized(statistics){revisionMissing++;}return null;}
        if(stored.longValue()!=revision){synchronized(statistics){revisionMismatch++;}return null;}
        Path file=images.get(coverId);
        if(file==null){synchronized(statistics){matchingRevisionNoImage++;}return null;}
        try {
            BasicFileAttributes a=Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
            if(!a.isRegularFile()||a.size()<1||a.size()>StationProtocol.COVER_BODY_BYTES||
                    !directory.equals(file.getParent())||!supportedPrefix(file)) {
                synchronized(statistics){fileRejected++;}return null;
            }
        } catch(IOException invalid) {synchronized(statistics){fileRejected++;}return null;}
        synchronized(statistics){accepted++;}return file;
    }

    @Override public boolean link(String coverId,long revision,Path destination) throws IOException {
        Path source=exactPath(coverId,revision);if(source==null)return false;
        Path target=destination.toAbsolutePath().normalize();
        if(Files.exists(target,LinkOption.NOFOLLOW_LINKS))return false;
        BasicFileAttributes before=Files.readAttributes(source,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        boolean created=false,acceptedLink=false;
        try {
            Files.createLink(target,source);created=true;
            BasicFileAttributes linked=Files.readAttributes(target,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
            if(linked.isRegularFile()&&linked.size()==before.size()&&supportedPrefix(target)){acceptedLink=true;return true;}
        } catch(FileAlreadyExistsException race) {return false;}
        catch(UnsupportedOperationException|SecurityException unavailable){return false;}
        catch(IOException unavailable){return false;}
        finally {if(created&&!acceptedLink)try{Files.deleteIfExists(target);}catch(IOException ignored){}}
        return false;
    }

    /** Aggregate, identifier-free evidence suitable for Android logs. */
    @Override public String diagnostics() {
        synchronized(statistics) {
            return "tableStatus="+tableStatus+" tableBytes="+tableBytes+" tableLines="+tableLines+
                " tableValid="+revisions.size()+" tableInvalid="+tableInvalidLines+
                " tableDuplicates="+tableDuplicateLines+" tableConflicts="+tableConflicts+
                " directoryEntries="+directoryEntries+" regularFiles="+regularFiles+
                " imageFiles="+imageFiles+" indexedImages="+images.size()+
                " invalidNames="+invalidImageNames+" unsupportedExtensions="+unsupportedExtensions+
                " imageConflicts="+imageConflicts+" revisionWithoutImage="+revisionWithoutImage+
                " imageWithoutRevision="+imageWithoutRevision+" lookups="+lookups+
                " revisionMissing="+revisionMissing+" revisionMismatch="+revisionMismatch+
                " matchingRevisionNoImage="+matchingRevisionNoImage+" fileRejected="+fileRejected+
                " accepted="+accepted;
        }
    }

    private static boolean supportedPrefix(Path file) {
        Set<OpenOption> options=new HashSet<>();Collections.addAll(options,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS);
        ByteBuffer prefix=ByteBuffer.allocate(12);
        try(SeekableByteChannel channel=Files.newByteChannel(file,options)) {
            while(prefix.hasRemaining()&&channel.read(prefix)>0){}
            StationFiles.imageExtension(Arrays.copyOf(prefix.array(),prefix.position()));return true;
        } catch(IOException invalid){return false;}
    }
}
