package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** Private server-signed catalog. Local access after activation is independent of online sessions. */
public final class StationCatalogStore {
    private final Path directory;
    public StationCatalogStore(Path directory) throws IOException {
        Files.createDirectories(directory);this.directory=directory.toRealPath();
    }
    public synchronized StationApi.CatalogSnapshot read(StationApi api,StationApi.Session session) throws Exception {
        Path path=file(session);
        if (!Files.exists(path,LinkOption.NOFOLLOW_LINKS)) return null;
        if (!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)) throw new IOException("Invalid catalog cache path");
        return api.restoreCatalog(StationFiles.readBounded(path,StationProtocol.CATALOG_BODY_BYTES),session);
    }
    public synchronized StationApi.CatalogSnapshot refresh(StationApi api,StationApi.Session session,
            StationApi.Cancellation cancel) throws Exception {
        StationApi.CatalogSnapshot fresh=api.catalogSnapshot(session,cancel);
        StationApi.CatalogSnapshot old=null;
        try {old=read(api,session);} catch (IOException|java.security.GeneralSecurityException|org.json.JSONException badCache) {
            // An authenticated fresh response may repair corrupt cached display data.
        }
        if (old != null && fresh.catalog.revision < old.catalog.revision)
            throw new IOException("Station catalog revision decreased");
        byte[] bytes=fresh.encoded();
        StationFiles.replace(new ByteArrayInputStream(bytes),file(session),bytes.length,StationProtocol.CATALOG_BODY_BYTES,
            cancel,StationFiles.NO_PROGRESS);
        Files.deleteIfExists(blocked(session.licenseId,session.deviceId));
        return fresh;
    }
    public synchronized StationApi.CatalogSnapshot readLocal(StationApi api,String licenseId)throws Exception {
        if(Files.exists(blocked(licenseId,api.deviceId()),LinkOption.NOFOLLOW_LINKS))return null;
        Path path=file(licenseId,api.deviceId());
        if(!Files.exists(path,LinkOption.NOFOLLOW_LINKS))return null;
        if(!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid catalog cache path");
        return api.restoreLocalCatalog(StationFiles.readBounded(path,StationProtocol.CATALOG_BODY_BYTES),licenseId);
    }
    /** Remember explicit license/device denial across process death, including offline restart. */
    public synchronized void block(String licenseId,String deviceId)throws IOException {
        byte[] marker={1};
        try {StationFiles.replace(new ByteArrayInputStream(marker),blocked(licenseId,deviceId),1,1,
            StationFiles.NEVER_CANCELLED,StationFiles.NO_PROGRESS);}
        catch(IOException failure){Files.deleteIfExists(file(licenseId,deviceId));throw failure;}
    }
    private Path blocked(String licenseId,String deviceId)throws IOException {return directory.resolve(owner(licenseId,deviceId)+".blocked");}
    private static String owner(String licenseId,String deviceId)throws IOException {
        if(!StationProtocol.licenseId(licenseId))throw new IOException("Invalid local license");
        return StationProtocol.base64Url(StationProtocol.sha256((licenseId+"\n"+deviceId).getBytes(StandardCharsets.UTF_8)));
    }
    private Path file(String licenseId,String deviceId)throws IOException {return directory.resolve(owner(licenseId,deviceId)+".json");}
    private Path file(StationApi.Session session) throws IOException {
        if (session == null) throw new IOException("Session required for catalog cache");
        return file(session.licenseId,session.deviceId);
    }
}
