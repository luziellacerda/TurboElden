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
        StationApi.Session session=(code==null||code.isEmpty())?sessions.get(cancel):sessions.activate(code,cancel);
        try {
            String name=loadName(session,cancel);
            Library result=loadCatalog(session,name,cancel);
            cancel.check();authorized=session;library=result;return result;
        }catch(Exception failure){sessions.denied(session);throw failure;}
    }
    public synchronized Library refresh(StationApi.Cancellation cancel) throws Exception {
        StationApi.Session session=sessions.get(cancel);
        try {
            Library result=loadCatalog(session,loadName(session,cancel),cancel);
            authorized=session;library=result;return result;
        }catch(StationApi.Failure e){if(e.sessionDenied())invalidate(session);throw e;}
    }
    public synchronized Path cover(String itemId,StationApi.Cancellation cancel) throws Exception {
        Library current=library;
        if(current==null)throw new IOException("Catálogo Station ainda não carregado");
        if(current.catalog.find(itemId)==null)throw new IOException("Jogo ausente do catálogo autorizado");
        StationApi.Session session=sessions.get(cancel);
        try{
            if(session!=authorized){current=loadCatalog(session,current.displayName,cancel);library=current;authorized=session;}
            StationCatalog.Item item=current.catalog.find(itemId);
            if(item==null)throw new IOException("Jogo ausente após renovar catálogo");
            try(StationDiagnostics.Scope trace=StationDiagnostics.selection(item.itemId,item.coverId,item.revision)){
                return covers.get(session,item.coverId,item.revision,cancel);
            }
        }
        catch(StationApi.Failure e){if(e.sessionDenied())invalidate(session);throw e;}
    }
    public synchronized StationApi.Grant authorize(String itemId,StationApi.Cancellation cancel) throws Exception {
        Library current=library;
        if(current==null || current.catalog.find(itemId)==null)throw new IOException("Jogo ausente do catálogo autorizado");
        StationApi.Session session=sessions.get(cancel);
        try{
            if(session!=authorized){current=loadCatalog(session,current.displayName,cancel);library=current;authorized=session;}
            StationCatalog.Item item=current.catalog.find(itemId);
            if(item==null)throw new IOException("Jogo ausente após renovar catálogo");
            try(StationDiagnostics.Scope trace=StationDiagnostics.selection(item.itemId,item.coverId,item.revision)){
                return api.authorize(session,itemId,item.revision,cancel);
            }
        }
        catch(StationApi.Failure e){if(e.sessionDenied())invalidate(session);throw e;}
    }
    public boolean ready() {
        StationApi.Session session=authorized;
        StationApi.Session live=sessions.peek();
        return library!=null && session!=null && live==session && !live.needsRenewal(clock.millis());
    }
    public Library current() {return library;}
    public synchronized void logout() {authorized=null;library=null;sessions.forgetSession();}
    private synchronized void invalidate(StationApi.Session session) {
        authorized=null;library=null;sessions.denied(session);
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
