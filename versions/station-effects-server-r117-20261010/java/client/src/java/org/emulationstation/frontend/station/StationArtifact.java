package org.emulationstation.frontend.station;

import java.io.IOException;
import java.util.Locale;
import org.json.JSONObject;

/** Signed artifact contract of Servidor-pix 1bfb619, never inferred from a URL. */
public final class StationArtifact {
    public static final long MAX_BYTES = 1L << 40;
    public static final long MAX_EXPANDED_BYTES = 4L << 40;
    public static final int MAX_FILES = 100000;
    public final String fileName, sha256, format, launchPath;
    public final long sizeBytes, expandedSizeBytes;
    public final int fileCount;
    private StationArtifact(String name,long size,String hash,String format,String launch,long expanded,int count) {
        this.fileName=name;this.sizeBytes=size;this.sha256=hash;this.format=format;
        this.launchPath=launch;this.expandedSizeBytes=expanded;this.fileCount=count;
    }
    static StationArtifact parse(JSONObject value) throws Exception {
        String name=relativePath(StationApi.string(value,"fileName"),255);
        if(name.indexOf('/')>=0)throw new IOException("Artifact filename is not a basename");
        String launch=relativePath(StationApi.string(value,"launchPath"),512);
        long size=bounded(value,"sizeBytes",MAX_BYTES),expanded=bounded(value,"expandedSizeBytes",MAX_EXPANDED_BYTES);
        int count=(int)bounded(value,"fileCount",MAX_FILES);
        String hash=StationApi.string(value,"sha256"),format=StationApi.string(value,"format");
        if(!hash.matches("[0-9a-f]{64}"))throw new IOException("Invalid artifact digest");
        String lower=name.toLowerCase(Locale.ROOT);
        if(format.equals("raw")) {
            if(!launch.equals(name)||expanded!=size||count!=1||lower.endsWith(".zip")||lower.endsWith(".rar")||lower.endsWith(".7z"))
                throw new IOException("Invalid raw artifact descriptor");
        } else if(!format.equals("zip")&&!format.equals("rar")&&!format.equals("7z")) {
            throw new IOException("Unsupported artifact format");
        } else if(!lower.endsWith("."+format))throw new IOException("Artifact extension disagrees with format");
        return new StationArtifact(name,size,hash,format,launch,expanded,count);
    }
    static long bounded(JSONObject value,String key,long maximum)throws Exception {
        long number=StationCatalog.integer(value,key);
        if(number>maximum)throw new IOException("Artifact limit exceeded: "+key);
        return number;
    }
    /** Relative paths only; validate before touching disk on any supported host filesystem. */
    public static String relativePath(String value,int maximum)throws IOException {
        StationCatalog.plainText(value,maximum);
        if(value.indexOf('\\')>=0||value.indexOf(':')>=0)throw new IOException("Invalid artifact path");
        for(String part:value.split("/",-1)) {
            if(part.isEmpty()||part.equals(".")||part.equals(".."))throw new IOException("Unsafe artifact path");
        }
        return value;
    }
    JSONObject json() throws Exception {
        return new JSONObject().put("fileName",fileName).put("sizeBytes",sizeBytes).put("sha256",sha256)
            .put("format",format).put("launchPath",launchPath).put("expandedSizeBytes",expandedSizeBytes).put("fileCount",fileCount);
    }
}
