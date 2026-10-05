package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import org.json.*;

/** One transaction per item. Only a committed receipt makes an item launchable. */
public final class StationInstaller {
    public interface Reader {
        void read(Path archive, Sink sink, StationApi.Cancellation cancel) throws Exception;
    }
    public interface Sink {
        void begin(byte[] utf8Name,long size,boolean directory) throws Exception;
        void data(byte[] bytes,int length) throws Exception;
        void end() throws Exception;
    }
    public static final class Installed {
        public final String itemId,platform;
        public final long revision;
        public final Path launchPath;
        private Installed(String id,String platform,long revision,Path launch){this.itemId=id;this.platform=platform;this.revision=revision;this.launchPath=launch;}
    }
    private final Path roms, records;
    private final Reader reader;
    private static final long RESERVE=256L*1024*1024;
    private static final int MANIFEST_MAX=64*1024*1024;
    public StationInstaller(Path roms,Path privateRecords,Reader reader)throws IOException {
        this.roms=directory(roms);this.records=directory(privateRecords);this.reader=Objects.requireNonNull(reader);
    }
    public synchronized Installed install(StationCatalog.Item item,StationApi.Grant grant,Path artifact,
            StationApi.Cancellation cancel,StationFiles.Progress progress)throws Exception {
        return installInternal(item,grant,artifact,null,cancel,progress,false);
    }
    /** Consume only a complete file from this queue's unique staging transaction. */
    public synchronized Installed installStaged(StationCatalog.Item item,StationApi.Grant grant,Path artifact,StationFiles.Receipt received,
            StationApi.Cancellation cancel,StationFiles.Progress progress)throws Exception {
        return installInternal(item,grant,artifact,received,cancel,progress,true);
    }
    private Installed installInternal(StationCatalog.Item item,StationApi.Grant grant,Path artifact,StationFiles.Receipt received,
            StationApi.Cancellation cancel,StationFiles.Progress progress,boolean consumeStaging)throws Exception {
        if(!item.itemId.equals(grant.itemId)||item.revision!=grant.itemRevision)throw new IOException("Installation authorization mismatch");
        StationArtifact spec=grant.artifact;
        Path source=artifact.toAbsolutePath().normalize();checkParents(source);
        if(consumeStaging)checkStaging(source);
        if(consumeStaging&&(received==null||received.size!=spec.sizeBytes))throw new IOException("Incomplete transfer receipt");
        boolean moveRaw=consumeStaging&&spec.format.equals("raw");
        if(!Files.isRegularFile(source,LinkOption.NOFOLLOW_LINKS))throw new IOException("Missing artifact");
        if(!consumeStaging&&Files.size(source)!=spec.sizeBytes)throw new IOException("Artifact changed before installation");
        // Content hashing of game files is disabled by the user's requested policy.
        // Signed size, format, safe paths and transactional publication remain enforced.
        cancel.check();
        if(!consumeStaging) {
            byte[] prefix=new byte[8];int n;try(InputStream in=Files.newInputStream(source)){n=in.read(prefix);}
            String actual=StationFiles.archiveType(n<0?new byte[0]:Arrays.copyOf(prefix,n));
            if(spec.format.equals("raw")?!actual.isEmpty():!spec.format.equals(actual))throw new IOException("Artifact signature disagrees with descriptor");
        }
        String folder=StationPlatforms.resolve(item.platform).folder;
        StationArtifact.relativePath(folder,120);if(folder.contains("/"))throw new IOException("Invalid platform folder");
        Path owner=directory(roms.resolve(".station-v2").resolve(folder).resolve(item.itemId));
        if(StationStorage.usableBytes(owner)<(moveRaw?0:spec.expandedSizeBytes)+RESERVE)throw new IOException("Espaço insuficiente para preparar o jogo");
        Path generation=Files.createTempDirectory(owner,"install-");
        boolean committed=false;
        try {
            Path content=directory(generation.resolve("content"));
            ManifestSink sink=new ManifestSink(content,spec,cancel,progress);
            try {
                if(spec.format.equals("raw")) {
                    boolean moved=false;
                    if(moveRaw) {
                        cancel.check();
                        Path target=content.resolve(spec.fileName);
                        try {
                            Files.move(source,target,StandardCopyOption.ATOMIC_MOVE);
                            moved=true;
                        }catch(AtomicMoveNotSupportedException unsupported) {
                            // Unusual providers may not support same-volume rename. Copy
                            // transactionally only if another full file fits on storage.
                            if(StationStorage.usableBytes(owner)<spec.expandedSizeBytes+RESERVE)
                                throw new IOException("Espaço insuficiente para preparar o jogo",unsupported);
                        }
                        if(moved) {
                            cancel.check();
                            sink.files.put(spec.fileName,spec.sizeBytes);
                            sink.total=spec.sizeBytes;
                            progress.changed(spec.sizeBytes,spec.expandedSizeBytes);
                        }
                    }
                    if(!moved) {
                    sink.begin(spec.fileName.getBytes(StandardCharsets.UTF_8),spec.sizeBytes,false);
                    try(InputStream in=Files.newInputStream(source)) {
                        byte[] buffer=new byte[65536];int count;
                        while((count=in.read(buffer))!=-1){cancel.check();if(count>0)sink.data(buffer,count);}
                    }
                    cancel.check();
                    sink.end();
                    }
                }else reader.read(source,sink,cancel);
                sink.finish();
            }finally{sink.close();}
            Path launch=content.resolve(spec.launchPath).normalize();
            if(!consumeStaging) {
                if(!Files.isRegularFile(launch,LinkOption.NOFOLLOW_LINKS)||Files.size(launch)<1)throw new IOException("Arquivo inicial ausente ou vazio");
                checkReferences(content,launch,sink.files.keySet());
            }
            JSONObject manifest=new JSONObject().put("schemaVersion",1).put("itemId",item.itemId).put("platform",item.platform)
                .put("revision",item.revision).put("generation",generation.getFileName().toString()).put("artifact",spec.json());
            JSONArray list=new JSONArray();
            for(Map.Entry<String,Long> entry:sink.files.entrySet())list.put(new JSONObject().put("path",entry.getKey()).put("size",entry.getValue()));
            manifest.put("files",list);
            byte[] bytes=manifest.toString().getBytes(StandardCharsets.UTF_8);
            StationFiles.replace(new ByteArrayInputStream(bytes),generation.resolve("manifest.json"),bytes.length,MANIFEST_MAX,cancel,StationFiles.NO_PROGRESS);
            // Atomic private pointer is the sole commit. Old generation stays intact across a failed update.
            StationFiles.replace(new ByteArrayInputStream(bytes),record(item.itemId),bytes.length,MANIFEST_MAX,cancel,StationFiles.NO_PROGRESS);
            committed=true;
            return new Installed(item.itemId,item.platform,item.revision,launch);
        }finally{if(!committed)deleteOwnTree(generation,owner);}
    }
    private void checkStaging(Path source)throws IOException {
        Path transaction=source.getParent(),stage=roms.resolve(".station-v2/staging");
        if(transaction==null||!stage.equals(transaction.getParent())||
                !transaction.getFileName().toString().matches("transfer-[A-Za-z0-9_-]+")||
                !source.getFileName().toString().equals("artifact"))
            throw new IOException("Artifact is not owned by this staging queue");
    }
    public synchronized Installed find(StationCatalog.Item item)throws Exception {
        JSONObject saved=readRecord(item.itemId);if(saved==null||saved.optBoolean("removing",false))return null;
        if(!StationPlatforms.resolve(StationApi.string(saved,"platform")).folder.equals(StationPlatforms.resolve(item.platform).folder))throw new IOException("Stored platform changed");
        Path content=content(saved,item.itemId);
        JSONObject spec=saved.getJSONObject("artifact");StationArtifact descriptor=StationArtifact.parse(spec);
        JSONArray files=saved.getJSONArray("files");
        if(files.length()!=descriptor.fileCount)throw new IOException("Incomplete installation receipt");
        // Returning to the collection checks only the recorded entry point. It must
        // not stat every extracted companion file on each catalog publication.
        Long launchSize=null;
        for(int i=0;i<files.length();i++) {
            JSONObject row=files.getJSONObject(i);
            if(!descriptor.launchPath.equals(row.optString("path","")))continue;
            if(launchSize!=null)throw new IOException("Duplicate launch file in receipt");
            Object size=row.get("size");if(!(size instanceof Integer)&&!(size instanceof Long))throw new IOException("Invalid installed size");
            launchSize=((Number)size).longValue();
        }
        if(launchSize==null)return null;
        Path launch=content.resolve(descriptor.launchPath);checkParents(launch);
        if(!Files.isRegularFile(launch,LinkOption.NOFOLLOW_LINKS)||Files.size(launch)!=launchSize)return null;
        return new Installed(item.itemId,item.platform,StationCatalog.integer(saved,"revision"),launch);
    }
    /** Remove only files listed in our committed receipt. Unknown files and emulator saves remain. */
    public synchronized void uninstall(String itemId)throws Exception {
        JSONObject saved=readRecord(itemId);if(saved==null)return;
        Path content=content(saved,itemId);JSONArray files=saved.getJSONArray("files");
        if(files.length()>StationArtifact.MAX_FILES)throw new IOException("Invalid installation receipt");
        List<Path> owned=new ArrayList<>();
        for(int i=0;i<files.length();i++) {
            Path path=content.resolve(StationArtifact.relativePath(StationApi.string(files.getJSONObject(i),"path"),4096));
            checkParents(path);if(Files.exists(path,LinkOption.NOFOLLOW_LINKS)&&!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS))throw new IOException("Installed file replaced by another type");
            owned.add(path);
        }
        // Keep a private tombstone until removal completes so interruption is retryable.
        saved.put("removing",true);
        byte[] pending=saved.toString().getBytes(StandardCharsets.UTF_8);
        StationFiles.replace(new ByteArrayInputStream(pending),record(itemId),pending.length,MANIFEST_MAX,new StationApi.Cancellation(),StationFiles.NO_PROGRESS);
        for(Path path:owned){Files.deleteIfExists(path);removeEmptyParents(path.getParent(),content);}
        removeEmptyParents(content,content); // Never recursively erase unknown files.
        Path generation=content.getParent();Files.deleteIfExists(generation.resolve("manifest.json"));
        try{Files.delete(generation);}catch(DirectoryNotEmptyException retained) {/* Preserve unrelated data. */}
        Files.deleteIfExists(record(itemId));
    }
    private Path record(String id)throws IOException {return records.resolve(StationCatalog.libraryId(id)+".json");}
    private JSONObject readRecord(String id)throws Exception {
        Path path=record(id);checkParents(path);if(!Files.exists(path,LinkOption.NOFOLLOW_LINKS))return null;
        JSONObject value=new JSONObject(new String(StationFiles.readBounded(path,MANIFEST_MAX),StandardCharsets.UTF_8));
        if(StationCatalog.integer(value,"schemaVersion")!=1||!id.equals(StationApi.string(value,"itemId")))throw new IOException("Invalid installation receipt");return value;
    }
    private Path content(JSONObject value,String id)throws Exception {
        String platform=StationPlatforms.resolve(StationApi.string(value,"platform")).folder;
        String generation=StationApi.string(value,"generation");
        if(!generation.matches("install-[A-Za-z0-9_-]+"))throw new IOException("Invalid installation generation");
        Path result=roms.resolve(".station-v2").resolve(platform).resolve(id).resolve(generation).resolve("content");checkParents(result);return result;
    }
    static Path directory(Path path)throws IOException {
        Path full=path.toAbsolutePath().normalize();checkParents(full);Files.createDirectories(full);checkParents(full);return full;
    }
    static void checkParents(Path path)throws IOException {
        Path full=path.toAbsolutePath().normalize();
        for(Path part=full;part!=null;part=part.getParent())if(Files.isSymbolicLink(part))throw new IOException("Symbolic path refused");
    }
    private static void removeEmptyParents(Path path,Path stop)throws IOException {
        for(Path p=path;p!=null&&p.startsWith(stop);p=p.getParent()) {
            try{Files.deleteIfExists(p);}catch(DirectoryNotEmptyException retained){return;}
            if(p.equals(stop))return;
        }
    }
    private static void deleteOwnTree(Path path,Path owner)throws IOException {
        Path root=path.toAbsolutePath().normalize(),parent=owner.toAbsolutePath().normalize();
        if(!root.getParent().equals(parent)||!root.getFileName().toString().startsWith("install-"))throw new IOException("Unsafe transaction cleanup");
        checkParents(parent);
        Files.walkFileTree(root,new SimpleFileVisitor<Path>() {
            public FileVisitResult visitFile(Path file,java.nio.file.attribute.BasicFileAttributes attrs)throws IOException{Files.delete(file);return FileVisitResult.CONTINUE;}
            public FileVisitResult postVisitDirectory(Path dir,IOException error)throws IOException{if(error!=null)throw error;Files.delete(dir);return FileVisitResult.CONTINUE;}
        });
    }
    private static void checkReferences(Path content,Path launch,Set<String> files)throws Exception {
        String lower=launch.getFileName().toString().toLowerCase(Locale.ROOT);
        if(!lower.endsWith(".cue")&&!lower.endsWith(".m3u"))return;
        String text=new String(StationFiles.readBounded(launch,1024*1024),StandardCharsets.UTF_8);
        Pattern cue=Pattern.compile("(?i)^\\s*FILE\\s+(?:\"([^\"]+)\"|(\\S+))\\s+\\S+\\s*$");
        int refs=0;
        for(String line:text.split("\\r?\\n")) {
            String ref=null;
            if(lower.endsWith(".cue")){Matcher m=cue.matcher(line);if(m.matches())ref=m.group(1)!=null?m.group(1):m.group(2);else if(line.trim().toUpperCase(Locale.ROOT).startsWith("FILE "))throw new IOException("Malformed CUE file reference");}
            else if(!line.trim().isEmpty()&&!line.trim().startsWith("#"))ref=line.trim();
            if(ref==null)continue;
            ref=StationArtifact.relativePath(ref.replace('\\','/'),512);
            Path target=launch.getParent().resolve(ref).normalize();
            String relative=content.relativize(target).toString().replace('\\','/');
            if(!target.startsWith(content)||!files.contains(relative)||!Files.isRegularFile(target,LinkOption.NOFOLLOW_LINKS))throw new IOException("Missing companion game file");refs++;
        }
        if(refs==0)throw new IOException("Game playlist has no usable file references");
    }
    private static final class ManifestSink implements Sink,AutoCloseable {
        final Path root;final StationArtifact spec;final StationApi.Cancellation cancel;final StationFiles.Progress progress;
        final LinkedHashMap<String,Long> files=new LinkedHashMap<>();final Set<String> all=new HashSet<>();
        FileOutputStream output;long total,written,expected;String current;boolean open,directory;
        ManifestSink(Path root,StationArtifact spec,StationApi.Cancellation cancel,StationFiles.Progress progress){this.root=root;this.spec=spec;this.cancel=cancel;this.progress=progress;}
        public void begin(byte[] utf8,long size,boolean dir)throws Exception {
            cancel.check();if(open)throw new IOException("Unfinished archive member");
            String name=StandardCharsets.UTF_8.newDecoder().onMalformedInput(java.nio.charset.CodingErrorAction.REPORT).decode(java.nio.ByteBuffer.wrap(utf8)).toString();
            if(dir&&name.endsWith("/"))name=name.substring(0,name.length()-1);
            StationArtifact.relativePath(name,4096);
            // Android shared storage can be case-insensitive; reject aliases before creating any file.
            String normalized=java.text.Normalizer.normalize(name,java.text.Normalizer.Form.NFC).toLowerCase(Locale.ROOT);
            if(!all.add(normalized)||all.size()>200000)throw new IOException("Duplicate or excessive archive members");
            if(size<0||(!dir&&(files.size()>=spec.fileCount||size>spec.expandedSizeBytes-total)))throw new IOException("Archive exceeds signed limits");
            Path target=root.resolve(name);checkParents(target);
            if(dir){directory(target);}else {
                directory(target.getParent());
                Files.createFile(target);output=new FileOutputStream(target.toFile());
            }
            current=name;expected=size;written=0;directory=dir;open=true;
        }
        public void data(byte[] bytes,int length)throws Exception {
            cancel.check();if(!open||directory||length<0||length>bytes.length||length>expected-written||length>spec.expandedSizeBytes-total)throw new IOException("Archive member size mismatch");
            output.write(bytes,0,length);written+=length;total+=length;progress.changed(total,spec.expandedSizeBytes);
        }
        public void end()throws Exception {
            cancel.check();if(!open)throw new IOException("Missing archive member");
            if(!directory){if(written!=expected)throw new IOException("Truncated archive member");output.getFD().sync();output.close();output=null;files.put(current,written);}
            open=false;
        }
        void finish()throws IOException {cancel.check();if(open||total!=spec.expandedSizeBytes||files.size()!=spec.fileCount||!files.containsKey(spec.launchPath))throw new IOException("Extracted artifact does not match descriptor");}
        public void close()throws IOException{if(output!=null){output.close();output=null;}}
    }
}
