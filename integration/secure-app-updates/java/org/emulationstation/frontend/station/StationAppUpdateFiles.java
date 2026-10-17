package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;

/** Private APK staging. SHA256 is calculated while receiving, with no game-file changes. */
public final class StationAppUpdateFiles {
    private StationAppUpdateFiles(){}
    static void regular(Path path)throws IOException {
        for(Path p=path.toAbsolutePath();p!=null;p=p.getParent())if(Files.isSymbolicLink(p))throw new IOException("UPDATE_STORAGE_LINK");
    }
    static Path root(Path directory)throws IOException {
        regular(directory);Files.createDirectories(directory);regular(directory);return directory;
    }
    static Path cached(Path directory,StationAppRelease release,StationApi.Cancellation cancel)throws Exception {
        Path file=root(directory).resolve(release.sha256+".apk");regular(file);
        if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))return null;
        if(Files.size(file)!=release.sizeBytes){Files.delete(file);return null;}
        // Recovery after a process exit checks the retained APK. Fresh downloads
        // are hashed once during receipt, never read again just for this check.
        MessageDigest digest=MessageDigest.getInstance("SHA-256");
        try(InputStream input=Files.newInputStream(file,LinkOption.NOFOLLOW_LINKS)){
            byte[] buffer=new byte[256*1024];int n;while((n=input.read(buffer))>=0){cancel.check();if(n>0)digest.update(buffer,0,n);}
        }
        if(!hex(digest.digest()).equals(release.sha256)){Files.delete(file);return null;}
        return file;
    }
    static void prune(Path directory,String keep)throws IOException {
        if(!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS))return;
        regular(directory);
        try(DirectoryStream<Path> files=Files.newDirectoryStream(directory)){
            for(Path file:files){String name=file.getFileName().toString();
                if(name.matches("[0-9a-f]{64}\\.(apk|part)")&&!name.equals(keep)){regular(file);Files.deleteIfExists(file);}
            }
        }
    }
    public static Path receive(InputStream input,Path directory,StationAppRelease release,
            StationApi.Cancellation cancel,StationFiles.Progress progress)throws Exception {
        root(directory);Path temporary=directory.resolve(release.sha256+".part"),complete=directory.resolve(release.sha256+".apk");
        regular(temporary);regular(complete);Files.deleteIfExists(temporary);
        boolean published=false;
        try{
            MessageDigest digest=MessageDigest.getInstance("SHA-256");long received=0;
            try(FileChannel output=FileChannel.open(temporary,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
                byte[] buffer=new byte[256*1024];int n;
                while(true){cancel.check();n=input.read(buffer);if(n<0)break;if(n==0)continue;
                    if(n>release.sizeBytes-received)throw new IOException("UPDATE_LENGTH");
                    digest.update(buffer,0,n);ByteBuffer bytes=ByteBuffer.wrap(buffer,0,n);while(bytes.hasRemaining())output.write(bytes);
                    received+=n;progress.changed(received,release.sizeBytes);
                }
                if(received!=release.sizeBytes||!hex(digest.digest()).equals(release.sha256))throw new IOException("UPDATE_DIGEST");
                cancel.check();output.force(true);
            }
            Files.move(temporary,complete,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
            published=true;return complete;
        }finally{if(!published)Files.deleteIfExists(temporary);}
    }
    static String hex(byte[] value){StringBuilder result=new StringBuilder();for(byte b:value)result.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return result.toString();}
}
