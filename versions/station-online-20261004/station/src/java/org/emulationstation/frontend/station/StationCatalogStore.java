package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** Private signed catalog persistence. Cache is never accepted as login authorization. */
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
        return fresh;
    }
    private Path file(StationApi.Session session) throws IOException {
        if (session == null) throw new IOException("Session required for catalog cache");
        String name=StationProtocol.base64Url(StationProtocol.sha256((session.licenseId+"\n"+session.deviceId).getBytes(StandardCharsets.UTF_8)));
        return directory.resolve(name+".json");
    }
}
