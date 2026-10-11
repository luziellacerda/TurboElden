package org.emulationstation.frontend.netplay;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Private bounded transfer of verified launch paths, without oversized Intent extras. */
public final class NetplayPaths {
    private static final int MAGIC=0x53544e31, MAX_ITEMS=40000, MAX_PATH_BYTES=16384;
    private NetplayPaths() {}
    public static File writeSnapshot(File privateFiles,String[] paths)throws IOException {
        if(paths==null||paths.length>MAX_ITEMS)throw new IOException("Invalid installed path count");
        File directory=new File(privateFiles,"station-netplay");
        if(!directory.isDirectory()&&!directory.mkdirs())throw new IOException("Cannot create private handoff");
        if(Files.isSymbolicLink(directory.toPath()))throw new IOException("Symbolic handoff directory");
        File result=File.createTempFile("dolphin-",".paths",directory);
        try(DataOutputStream out=new DataOutputStream(new BufferedOutputStream(new FileOutputStream(result)))) {
            out.writeInt(MAGIC);out.writeInt(paths.length);
            for(String path:paths){
                if(path==null||!new File(path).isAbsolute()||path.indexOf('\0')>=0)throw new IOException("Invalid installed path");
                byte[] bytes=path.getBytes(java.nio.charset.StandardCharsets.UTF_8);
                if(bytes.length<1||bytes.length>MAX_PATH_BYTES)throw new IOException("Invalid path length");
                out.writeInt(bytes.length);out.write(bytes);
            }
        }catch(IOException|RuntimeException error){Files.deleteIfExists(result.toPath());throw error;}
        return result;
    }
    private static File snapshot(File privateFiles,String name)throws IOException {
        if(name==null||!name.matches("dolphin-[A-Za-z0-9_-]+\\.paths"))throw new IOException("Invalid handoff name");
        File rawDirectory=new File(privateFiles,"station-netplay");
        if(Files.isSymbolicLink(rawDirectory.toPath()))throw new IOException("Symbolic handoff directory");
        File directory=rawDirectory.getCanonicalFile(),file=new File(directory,name);
        if(!file.getCanonicalFile().getParentFile().equals(directory)||Files.isSymbolicLink(file.toPath()))throw new IOException("Invalid handoff location");
        return file;
    }
    public static String[] readSnapshot(File privateFiles,String name)throws IOException {
        try(DataInputStream in=new DataInputStream(new BufferedInputStream(new FileInputStream(snapshot(privateFiles,name))))) {
            if(in.readInt()!=MAGIC)throw new IOException("Invalid handoff format");
            int count=in.readInt();if(count<0||count>MAX_ITEMS)throw new IOException("Invalid installed path count");
            String[] paths=new String[count];
            for(int i=0;i<count;i++){
                int length=in.readInt();if(length<1||length>MAX_PATH_BYTES)throw new IOException("Invalid path length");
                byte[] bytes=new byte[length];in.readFully(bytes);
                String path=new String(bytes,java.nio.charset.StandardCharsets.UTF_8);
                if(!new File(path).isAbsolute()||path.indexOf('\0')>=0)throw new IOException("Invalid installed path");
                paths[i]=path;
            }
            if(in.read()!=-1)throw new IOException("Unexpected handoff data");return paths;
        }
    }
    public static void deleteSnapshot(File privateFiles,String name)throws IOException {Files.deleteIfExists(snapshot(privateFiles,name).toPath());}
    /** Directories of real installed launch files; no guessed roots or recursive disk scan. */
    public static String[] installedFolders(String[] launchPaths)throws IOException {
        LinkedHashSet<String> folders=new LinkedHashSet<>();
        for(String text:launchPaths){
            if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("Preparation cancelled");
            if(text==null||!new File(text).isAbsolute())throw new IOException("Invalid installed path");
            Path path=Paths.get(text).toAbsolutePath().normalize();
            for(Path parent=path;parent!=null;parent=parent.getParent())if(Files.isSymbolicLink(parent))throw new IOException("Symbolic game path");
            // A game removed after the snapshot is no longer eligible for this scan.
            if(Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)&&Files.size(path)>0)folders.add(path.getParent().toString());
        }
        return folders.toArray(new String[0]);
    }
    public static String[] mergeFolders(String[] existing,String[] installed){
        LinkedHashSet<String> merged=new LinkedHashSet<>();
        if(existing!=null)for(String path:existing)if(path!=null&&!path.isEmpty())merged.add(path);
        Collections.addAll(merged,installed);return merged.toArray(new String[0]);
    }
}
