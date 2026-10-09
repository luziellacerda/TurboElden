package org.emulationstation.frontend.station;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Read-only migration of existing station-covers and its observed revisions.tsv format. */
public final class ExistingCoverCache implements StationCoverStore.PreviousCovers {
    private final Path directory;
    private final Map<String,Long> revisions=new HashMap<>();
    public ExistingCoverCache(Path directory) throws IOException {
        this.directory=directory.toAbsolutePath().normalize();
        Path table=this.directory.resolve("revisions.tsv");
        if(!Files.isRegularFile(table,LinkOption.NOFOLLOW_LINKS))return;
        String text;
        try {text=new String(StationFiles.readBounded(table,1024*1024),StandardCharsets.UTF_8);}
        catch(IOException invalidCache){return;}
        Set<String> ambiguous=new HashSet<>();
        for(String line:text.split("\n")) {
            String[] fields=line.split("\t",-1);if(fields.length!=2)continue;
            if(!StationProtocol.libraryId(fields[0]))continue;
            long revision;
            try {revision=Long.parseLong(fields[1].trim());}catch(NumberFormatException invalid){continue;}
            if(revision<1)continue;
            Long old=revisions.put(fields[0],revision);
            if(old!=null && old.longValue()!=revision)ambiguous.add(fields[0]);
        }
        for(String id:ambiguous)revisions.remove(id);
    }
    @Override public byte[] find(String coverId,long revision) throws IOException {
        StationCatalog.libraryId(coverId);Long stored=revisions.get(coverId);
        if(stored==null || stored.longValue()!=revision)return null;
        for(String extension:new String[]{"png","jpg","jpeg","webp","gif"}) {
            Path file=directory.resolve(coverId+"."+extension);
            if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))continue;
            try {
                byte[] bytes=StationFiles.readBounded(file,StationProtocol.COVER_BODY_BYTES);
                StationFiles.imageExtension(bytes);return bytes;
            }catch(IOException corrupt){ /* Try the next explicitly supported image format. */ }
        }
        return null;
    }
}
