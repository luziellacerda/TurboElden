package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import org.json.JSONObject;

/** Application entry point shared by login and the reconstructed native catalog. */
public final class StationCoordinator {
    public static final class Library {
        public final String displayName;
        public final StationCatalog catalog;
        public final boolean cached;
        private Library(String displayName,StationCatalog catalog,boolean cached) {
            this.displayName=displayName;this.catalog=catalog;this.cached=cached;
        }
    }
    private final StationApi api;
    private final StationSessions sessions;
    private final StationCatalogStore catalogs;
    private final StationCoverStore covers;
    private final Path privateFiles;
    private final StationApi.Clock clock;
    private volatile StationApi.Session authorized;
    private volatile Library library;
    public StationCoordinator(StationApi api,StationSessions sessions,StationCatalogStore catalogs,
            StationCoverStore covers,Path privateFiles,StationApi.Clock clock) {
        this.api=api;this.sessions=sessions;this.catalogs=catalogs;this.covers=covers;
        this.privateFiles=privateFiles;this.clock=clock;
    }
    public synchronized Library login(String code,StationApi.Cancellation cancel) throws Exception {
        authorized=null;library=null;
        if(code!=null&&!code.isEmpty())sessions.activate(code,cancel);
        StationApi.Session session=null;
        try(StationSessions.Lease lease=sessions.acquire(cancel)) {
            session=lease.session;
            String name=loadName(session,cancel);
            Library result=loadCatalog(session,name,cancel);
            cancel.check();authorized=session;library=result;return result;
        }catch(Exception failure){if(session!=null)sessions.denied(session);throw failure;}
    }
    public synchronized Library refresh(StationApi.Cancellation cancel) throws Exception {
        StationApi.Session session=null;
        try(StationSessions.Lease lease=sessions.acquire(cancel)) {
            session=lease.session;
            Library result=loadCatalog(session,loadName(session,cancel),cancel);
            authorized=session;library=result;return result;
        }catch(StationApi.Failure failure){if(session!=null&&failure.sessionDenied())invalidate(session);throw failure;}
    }
    /** Session/library snapshot used until the authenticated response has been accepted. */
    public static final class Access implements AutoCloseable {
        public final StationCatalog.Item item;
        final StationSessions.Lease lease;
        private Access(StationCatalog.Item item,StationSessions.Lease lease){this.item=item;this.lease=lease;}
        @Override public void close(){lease.close();}
    }
    public synchronized Access acquireItem(String itemId,StationApi.Cancellation cancel)throws Exception {
        Library current=library;
        if(current==null || current.catalog.find(itemId)==null)throw new IOException("Jogo ausente do catálogo autorizado");
        StationSessions.Lease lease=sessions.acquire(cancel);
        try {
            if(lease.session!=authorized){current=loadCatalog(lease.session,current.displayName,cancel);library=current;authorized=lease.session;}
            StationCatalog.Item item=current.catalog.find(itemId);
            if(item==null)throw new IOException("Jogo ausente após renovar catálogo");
            return new Access(item,lease);
        }catch(Exception failure){lease.close();if(failure instanceof StationApi.Failure && ((StationApi.Failure)failure).sessionDenied())invalidate(lease.session);throw failure;}
    }
    public Path cover(String itemId,StationApi.Cancellation cancel) throws Exception {
        Access access=acquireItem(itemId,cancel);
        try(Access held=access;StationDiagnostics.Scope trace=StationDiagnostics.selection(access.item.itemId,access.item.coverId,access.item.revision)){
            return covers.get(access.lease.session,access.item.coverId,access.item.revision,cancel);
        }catch(StationApi.Failure failure){if(failure.sessionDenied())invalidate(access.lease.session);throw failure;}
    }
    public StationApi.Grant authorize(String itemId,StationApi.Cancellation cancel) throws Exception {
        Access access=acquireItem(itemId,cancel);
        try(Access held=access){return authorize(access,cancel);}
        catch(StationApi.Failure failure){rejected(access,failure);throw failure;}
    }
    void rejected(Access access,StationApi.Failure failure){
        if(access!=null&&failure.sessionDenied())invalidate(access.lease.session);
    }
    StationApi.Grant authorize(Access access,StationApi.Cancellation cancel)throws Exception {
        try(StationDiagnostics.Scope trace=StationDiagnostics.selection(access.item.itemId,access.item.coverId,access.item.revision)){
            return api.authorize(access.lease.session,access.item.itemId,access.item.revision,cancel);
        }catch(StationApi.Failure failure){
            // Caller closes the lease before any subsequent renewal. No global monitor is held for IO.
            if(failure.sessionDenied())sessions.denied(access.lease.session);throw failure;
        }
    }
    public boolean ready() {
        StationApi.Session session=authorized;
        StationApi.Session live=sessions.peek();
        return library!=null && session!=null && live==session && !live.needsRenewal(clock.millis());
    }
    public Library current() {return library;}
    public synchronized void logout() {authorized=null;library=null;sessions.forgetSession();}
    private synchronized void invalidate(StationApi.Session session) {
        if(authorized==session){authorized=null;library=null;}sessions.denied(session);
    }
    private Library loadCatalog(StationApi.Session session,String name,StationApi.Cancellation cancel) throws Exception {
        try{
            StationCatalog catalog=catalogs.refresh(api,session,cancel).catalog;
            StationDiagnostics.record(StationDiagnostics.Event.CATALOG_NETWORK,200,catalog.items.size());
            return new Library(name,catalog,false);
        }
        catch(StationApi.Failure unavailable) {
            if(unavailable.status!=503 || !unavailable.code.equals("STATION_CATALOG_NOT_READY"))throw unavailable;
            StationApi.CatalogSnapshot cached=catalogs.read(api,session);
            if(cached==null)throw unavailable;
            StationDiagnostics.record(StationDiagnostics.Event.CATALOG_CACHE,503,cached.catalog.items.size());
            return new Library(name,cached.catalog,true);
        }
    }
    private String loadName(StationApi.Session session,StationApi.Cancellation cancel) throws Exception {
        try {String name=api.profile(session,cancel);saveName(session,name,cancel);return name;}
        catch(StationApi.Failure unavailable) {
            if(unavailable.status!=503 || !unavailable.code.equals("STATION_PROFILE_NOT_READY"))throw unavailable;
            return readName(session);
        }
    }
    private Path nameFile(StationApi.Session session) {
        String owner=StationProtocol.base64Url(StationProtocol.sha256((session.licenseId+"\n"+session.deviceId).getBytes(StandardCharsets.UTF_8)));
        return privateFiles.resolve("station-v2/profiles").resolve(owner+".json");
    }
    private String readName(StationApi.Session session) {
        try {
            Path file=nameFile(session);
            if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))return "";
            JSONObject data=new JSONObject(new String(StationFiles.readBounded(file,1024),StandardCharsets.UTF_8));
            return StationCatalog.plainText(StationApi.string(data,"displayName"),80);
        }catch(Exception missing){return "";}
    }
    private void saveName(StationApi.Session session,String name,StationApi.Cancellation cancel) throws Exception {
        byte[] bytes=new JSONObject().put("displayName",name).toString().getBytes(StandardCharsets.UTF_8);
        StationFiles.replace(new ByteArrayInputStream(bytes),nameFile(session),bytes.length,1024,cancel,StationFiles.NO_PROGRESS);
        // Existing native header reads this local display string; it never authorizes access.
        byte[] text=name.getBytes(StandardCharsets.UTF_8);
        if(text.length>0)StationFiles.replace(new ByteArrayInputStream(text),privateFiles.resolve("station-display-name.txt"),
            text.length,512,cancel,StationFiles.NO_PROGRESS);
    }
}
