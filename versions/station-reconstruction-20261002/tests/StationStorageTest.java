package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.concurrent.atomic.AtomicInteger;

public final class StationStorageTest {
    static int checks;
    interface Op {void run()throws Exception;}
    static void ok(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
    static void fails(Op op)throws Exception {try{op.run();throw new AssertionError("Expected failure");}catch(IOException|java.security.GeneralSecurityException|org.json.JSONException expected){checks++;}}
    public static void main(String[] args)throws Exception {
        Path dir=Paths.get(args[0]);Files.createDirectories(dir);
        StationApiTest.Fake remote=new StationApiTest.Fake();StationApi api=remote.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
        Path license=dir.resolve("license.txt");Files.write(license,remote.license.getBytes(StandardCharsets.UTF_8));
        StationSessions sessions=new StationSessions(api,remote,license);
        StationApi.Session first=sessions.get(cancel);int requests=remote.requests;
        ok(sessions.get(cancel)==first&&requests==remote.requests,"Reuse unexpired session");
        remote.time+=165000;StationApi.Session second=sessions.get(cancel);
        ok(first!=second&&remote.requests==requests+2,"Renew before expiry");
        sessions.denied(first);ok(sessions.get(cancel)==second,"Late denial cannot clear newer session");
        sessions.denied(second);StationApi.Session third=sessions.get(cancel);ok(third!=second,"Denied session cleared");
        StationCatalogStore catalog=new StationCatalogStore(dir.resolve("catalog"));
        StationApi.CatalogSnapshot saved=catalog.refresh(api,third,cancel);
        requests=remote.requests;ok(catalog.read(api,third).catalog.items.size()==1&&remote.requests==requests,"Signed cache read offline within valid session");
        remote.badSignature=true;fails(()->catalog.refresh(api,third,cancel));remote.badSignature=false;
        ok(Arrays.equals(saved.encoded(),catalog.read(api,third).encoded()),"Bad fresh signature preserves catalog");
        byte[] tampered=saved.encoded();tampered[tampered.length/2]^=1;fails(()->api.restoreCatalog(tampered,third));
        remote.time+=165000;StationApi.Session fourth=sessions.get(cancel);
        ok(catalog.read(api,fourth).catalog.items.size()==1,"Read signed previous-session display cache");
        remote.failedRoute="/v1/station/catalog";remote.status=503;remote.errorCode="STATION_CATALOG_NOT_READY";
        fails(()->catalog.refresh(api,fourth,cancel));remote.failedRoute="";
        ok(Arrays.equals(saved.encoded(),catalog.read(api,fourth).encoded()),"503 preserves signed cache");
        AtomicInteger decoded=new AtomicInteger();
        StationCoverStore store=new StationCoverStore(dir.resolve("covers"),api,sessions,remote,n->remote.time+=n,b->decoded.incrementAndGet());
        Path cover=store.get("cover_12345",1,cancel);requests=remote.requests;
        ok(Files.size(cover)==8,"Cover persisted");
        ok(store.get("cover_12345",1,cancel).equals(cover)&&remote.requests==requests&&decoded.get()==1,"Repeated cover has no network or decode");
        StationCoverStore reopened=new StationCoverStore(dir.resolve("covers"),api,sessions,remote,n->remote.time+=n,b->decoded.incrementAndGet());
        ok(reopened.get("cover_12345",1,cancel).equals(cover)&&remote.requests==requests,"Restart reuses persistent cover");
        store.get("cover_12345",2,cancel);ok(remote.requests==requests+1,"New revision fetches once");
        Files.write(cover,"bad".getBytes(StandardCharsets.UTF_8));store.get("cover_12345",1,cancel);
        ok(Files.size(cover)==8,"Corrupt cover repaired");
        remote.failedRoute="/v1/station/covers/cover_missing";remote.status=404;remote.errorCode="STATION_COVER_NOT_FOUND";
        fails(()->store.get("cover_missing",1,cancel));requests=remote.requests;
        fails(()->store.get("cover_missing",1,cancel));ok(requests==remote.requests,"404 is not retried every frame");remote.failedRoute="";
        StationApi.Cancellation stopped=new StationApi.Cancellation();stopped.cancel();requests=remote.requests;
        fails(()->store.get("cover_12345",3,stopped));ok(requests==remote.requests,"Cancelled cover not requested");
        StationCoverStore rejects=new StationCoverStore(dir.resolve("rejected-covers"),api,sessions,remote,n->remote.time+=n,b->{throw new IOException("Bad bitmap");});
        fails(()->rejects.get("cover_12345",1,cancel));
        try(java.util.stream.Stream<Path> files=Files.list(dir.resolve("rejected-covers"))){ok(files.count()==0,"Invalid bitmap not published");}
        Path previous=dir.resolve("old-covers");Files.createDirectories(previous);
        Files.write(previous.resolve("revisions.tsv"),"cover_old123\t7\n".getBytes(StandardCharsets.UTF_8));
        Files.write(previous.resolve("cover_old123.png"),new byte[]{(byte)137,80,78,71,13,10,26,10});
        ExistingCoverCache existing=new ExistingCoverCache(previous);
        ok(existing.find("cover_old123",6)==null,"Never reuse mismatched revision");
        StationCoverStore migrated=new StationCoverStore(dir.resolve("migrated"),api,sessions,remote,n->remote.time+=n,b->{},existing);
        requests=remote.requests;Path reused=migrated.get("cover_old123",7,cancel);
        ok(Files.size(reused)==8 && requests==remote.requests,"Reuse old authenticated-ID cover without download");
        ok(Files.exists(previous.resolve("cover_old123.png")),"Migration preserves old cover");
        sessions.forgetSession();remote.failedRoute="/v1/station/challenges";remote.status=403;remote.errorCode="STATION_LICENSE_DENIED";
        fails(()->sessions.get(cancel));ok(Files.exists(license),"Revocation does not destroy persisted identity");
        ok(remote.closed==remote.requests,"Storage closes responses");
        ok(StationPlatforms.resolve("snesbr").folder.equals("super-nintendo--br"),"Preserve SNES BR double hyphen");
        ok(StationPlatforms.resolve("MegaDrive - BR").folder.equals("megadrive--br"),"Preserve Mega BR folder");
        ok(StationPlatforms.resolve("Nintendo 64 - BR").folder.equals("nintendo-64--br"),"Preserve N64 BR folder");
        ok(StationPlatforms.resolve("Psp - BR").folder.equals("psp"),"Preserve observed PSP BR path");
        fails(()->StationPlatforms.resolve("../../newplatform"));
        fails(()->StationPlatforms.resolve("Unknown platform"));
        ok(StationPlatforms.resolve("gbc").folder.equals("gameboy-color"),"Server GBC alias");
        System.out.println("PASS "+checks+" cache and session checks");
    }
}
