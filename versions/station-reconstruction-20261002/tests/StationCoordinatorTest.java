package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

public final class StationCoordinatorTest {
    static int checks;
    interface Op {void run()throws Exception;}
    static void ok(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
    static void fails(Op op)throws Exception{try{op.run();throw new AssertionError("Expected failure");}catch(IOException|java.security.GeneralSecurityException expected){checks++;}}
    public static void main(String[] args)throws Exception{
        Path dir=Paths.get(args[0]);Files.createDirectories(dir);
        StationApiTest.Fake server=new StationApiTest.Fake();StationApi api=server.api();
        Path license=dir.resolve("station-license-id.txt");Files.write(license,server.license.getBytes(StandardCharsets.UTF_8));
        StationSessions sessions=new StationSessions(api,server,license);
        StationCatalogStore catalogs=new StationCatalogStore(dir.resolve("catalog"));
        StationCoverStore covers=new StationCoverStore(dir.resolve("covers"),api,sessions,server,n->server.time+=n,bytes->{});
        StationCoordinator owner=new StationCoordinator(api,sessions,catalogs,covers,dir,server);
        StationApi.Cancellation cancel=new StationApi.Cancellation();
        ok(!owner.ready(),"No UI authorization before session");
        StationCoordinator.Library library=owner.login("",cancel);
        ok(owner.ready()&&library.displayName.equals("Comprador")&&!library.cached,"Login and catalog integrated");
        ok(library.catalog.items.size()==1,"Catalog delivered to frontend");
        ok(Files.readString(dir.resolve("station-display-name.txt")).equals("Comprador"),"Native header name published");
        ok(Files.size(owner.cover("item_12345",cancel))==8,"Cover resolved by item ID");
        int requests=server.requests;fails(()->owner.cover("item_unknown",cancel));ok(requests==server.requests,"Unknown item not requested");
        owner.logout();ok(!owner.ready()&&owner.current()==null,"Logout clears ready state");
        server.failedRoute="/v1/station/me";server.status=503;server.errorCode="STATION_PROFILE_NOT_READY";
        library=owner.login("",cancel);ok(owner.ready()&&library.displayName.equals("Comprador"),"Cached name only after valid session");
        server.failedRoute="/v1/station/catalog";server.errorCode="STATION_CATALOG_NOT_READY";
        library=owner.refresh(cancel);ok(library.cached&&library.catalog.items.size()==1,"503 shows verified cache");
        server.status=403;server.errorCode="STATION_LICENSE_DENIED";
        fails(()->owner.refresh(cancel));ok(!owner.ready()&&owner.current()==null,"Revoked license closes frontend authorization");
        server.failedRoute="";owner.login(null,cancel);
        ok(owner.ready(),"Resume with saved license does not require code again");
        server.time+=165000;ok(!owner.ready(),"Expired ready state not accepted");
        owner.refresh(cancel);ok(owner.ready(),"Refresh renews session");
        server.failedRoute="/v1/station/downloads/authorize";server.status=403;server.errorCode="STATION_LICENSE_DENIED";
        fails(()->owner.authorize("item_12345",cancel));ok(!owner.ready(),"Download denial invalidates session");
        server.failedRoute="";
        StationApi.Cancellation stopped=new StationApi.Cancellation();stopped.cancel();requests=server.requests;
        fails(()->owner.login("",stopped));ok(server.requests==requests&&!owner.ready(),"Cancelled login does not authorize");
        ok(server.closed==server.requests,"All integration responses closed");
        System.out.println("PASS "+checks+" frontend integration checks");
    }
}
