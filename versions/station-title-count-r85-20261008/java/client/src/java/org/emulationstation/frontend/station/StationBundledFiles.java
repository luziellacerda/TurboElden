package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;

/** Installs only packaged files, repairing missing files without erasing user additions. */
public final class StationBundledFiles {
    public interface Source { String[] list(String path)throws IOException; InputStream open(String path)throws IOException; }
    private StationBundledFiles() {}
    public static int install(Source source,String assetPath,Path target,boolean replaceExisting)throws IOException {
        return install(source,assetPath,target,replaceExisting,0);
    }
    private static int install(Source source,String assetPath,Path target,boolean replace,int depth)throws IOException {
        if(depth>32)throw new IOException("Packaged resource nesting limit");
        StationInstaller.checkParents(target);
        String[] children=source.list(assetPath);
        if(children!=null&&children.length>0){
            StationInstaller.directory(target);int copied=0;
            for(String child:children){
                if(child.isEmpty()||child.equals(".")||child.equals("..")||child.indexOf('/')>=0||child.indexOf('\\')>=0)
                    throw new IOException("Invalid packaged resource name");
                copied+=install(source,assetPath+"/"+child,target.resolve(child),replace,depth+1);
            }
            return copied;
        }
        if(Files.exists(target,LinkOption.NOFOLLOW_LINKS)){
            if(!Files.isRegularFile(target,LinkOption.NOFOLLOW_LINKS))throw new IOException("Packaged resource path conflict");
            if(!replace&&Files.size(target)>0)return 0;
        }
        Path parent=StationInstaller.directory(target.getParent());
        Path temporary=Files.createTempFile(parent,".station-resource-",".tmp");
        try{
            try(InputStream input=source.open(assetPath);OutputStream output=Files.newOutputStream(temporary)){
                byte[] buffer=new byte[65536];int count;
                while((count=input.read(buffer))!=-1)if(count>0)output.write(buffer,0,count);
            }
            StationInstaller.checkParents(target);
            try{Files.move(temporary,target,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
            catch(AtomicMoveNotSupportedException unsupported){Files.move(temporary,target,StandardCopyOption.REPLACE_EXISTING);}
            return 1;
        }finally{Files.deleteIfExists(temporary);}
    }
}
