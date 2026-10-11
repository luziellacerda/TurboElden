package org.emulationstation.frontend.station;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/** Installs the packaged resource bundle once per bundle content revision. */
public final class StationResourceBundle {
    public static final String BUNDLE_ID=
        "resources-sha256:b2725c79238a1da67ab1d485cb86dd7875b618ad5fb4b63a7f0acb829a02a9ee";
    private static final String MARKER_NAME=".installed-version";
    private static final int MAX_MARKER_BYTES=256;

    private StationResourceBundle() {}

    public static int install(StationBundledFiles.Source source,Path resources)throws IOException {
        Path marker=resources.resolve(MARKER_NAME);
        String installed=readMarker(marker);
        boolean current=BUNDLE_ID.equals(installed);
        boolean replace=installed==null||(!current&&!legacyTimestamp(installed));
        // Current and legacy markers repair only missing/empty files. A new bundle
        // revision replaces every packaged path while preserving user additions.
        int copied=StationBundledFiles.install(source,"resources",resources,replace);
        if(!current)writeMarker(resources,marker);
        return copied;
    }

    static boolean legacyTimestamp(String value) {
        if(value==null||value.isEmpty())return false;
        for(int i=0;i<value.length();i++)if(value.charAt(i)<'0'||value.charAt(i)>'9')return false;
        return true;
    }

    static String readMarker(Path marker)throws IOException {
        if(!Files.isRegularFile(marker,LinkOption.NOFOLLOW_LINKS))return null;
        long size=Files.size(marker);
        if(size<=0||size>MAX_MARKER_BYTES)return null;
        return new String(Files.readAllBytes(marker),StandardCharsets.UTF_8).trim();
    }

    private static void writeMarker(Path resources,Path marker)throws IOException {
        StationInstaller.directory(resources);
        Path temporary=Files.createTempFile(resources,".station-resource-marker-",".tmp");
        try{
            Files.write(temporary,BUNDLE_ID.getBytes(StandardCharsets.UTF_8),
                StandardOpenOption.WRITE,StandardOpenOption.TRUNCATE_EXISTING);
            try{Files.move(temporary,marker,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
            catch(AtomicMoveNotSupportedException unsupported){
                Files.move(temporary,marker,StandardCopyOption.REPLACE_EXISTING);
            }
        }finally{Files.deleteIfExists(temporary);}
    }
}
