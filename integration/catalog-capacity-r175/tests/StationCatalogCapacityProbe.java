package org.emulationstation.frontend.station;

import java.io.IOException;
import java.lang.reflect.Constructor;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.json.*;

/** Runs the productive parser/API/cache/queue; all keys and identities are synthetic. */
public final class StationCatalogCapacityProbe {
    static int checks;
    interface Op {void run() throws Exception;}
    static void check(boolean value,String message) {checks++;if(!value)throw new AssertionError(message);}
    static void rejects(Op op,String message) throws Exception {
        try {op.run();throw new AssertionError(message);} catch(IOException|java.security.GeneralSecurityException|JSONException expected) {checks++;}
    }
    static JSONObject fixture(int count) throws Exception {
        JSONArray items=new JSONArray();
        for(int i=0;i<count;i++)items.put(new JSONObject().put("itemId",String.format("capacity_item_%05d",i))
            .put("name","Catálogo sintético "+i).put("platform",i>=count-100?"gba":"snes").put("revision",1)
            .put("coverId",String.format("capacity_cover_%05d",i))
            .put("folderPath",new JSONArray().put("Coleção de teste"))
            .put("metadata",new JSONObject().put("description","Descrição sintética de teste; preserva ação, áudio e acentuação.")
                .put("players","1-2").put("developer","Synthetic")));
        return new JSONObject().put("revision",102).put("totalItems",count).put("hasMore",false).put("items",items);
    }
    static StationCoordinator.Library library(StationCatalog catalog) throws Exception {
        Constructor<StationCoordinator.Library> c=StationCoordinator.Library.class.getDeclaredConstructor(String.class,StationCatalog.class,boolean.class);
        c.setAccessible(true);return c.newInstance("Capacity test",catalog,false);
    }
    static void parser() throws Exception {
        check(StationHttp.allowed("GET","/v1/station/catalog?metadata=1&maximumItems=20000"),"Actual HTTP transport permits complete catalogue route");
        check(StationHttp.allowed("GET","/v1/station/catalog?metadata=1"),"Legacy metadata route remains permitted");
        for(String route:new String[]{"/v1/station/catalog?metadata=1&maximumItems=20001","/v1/station/catalog?metadata=1&maximumItems=20000&url=https://invalid","https://invalid/catalog","/v1/station/catalog?metadata=1&maximumItems=20000#fragment"})
            check(!StationHttp.allowed("GET",route),"Unrequested transport route denied");
        check(!StationHttp.allowed("POST","/v1/station/catalog?metadata=1&maximumItems=20000"),"Catalogue remains GET-only");
        for(int count:new int[]{0,4096,12288,20000}) {
            StationCatalog parsed=StationCatalog.fromVerifiedPayload(fixture(count));parsed.requireComplete();
            check(parsed.items.size()==count && parsed.totalItems==count && !parsed.hasMore,"Complete capacity "+count);
            if(count>0)check(parsed.find(String.format("capacity_item_%05d",count-1))!=null,"Final item retained "+count);
            StationCatalog restored=StationCatalog.fromVerifiedPayload(new JSONObject(new String(parsed.localPayload(),StandardCharsets.UTF_8)));
            restored.requireComplete();check(restored.items.size()==count,"Local roundtrip "+count);
        }
        rejects(()->StationCatalog.fromVerifiedPayload(fixture(20001)),"20001 must remain bounded");
        JSONObject partial=fixture(4096).put("totalItems",4588).put("hasMore",true);
        StationCatalog old=StationCatalog.fromVerifiedPayload(partial);
        check(old.items.size()==4096 && old.hasMore,"Legacy offline snapshot retained honestly");
        rejects(old::requireComplete,"A partial response must never replace a full network catalogue");
        StationCatalog local=StationCatalog.fromVerifiedPayload(new JSONObject(new String(old.localPayload(),StandardCharsets.UTF_8)));
        check(local.hasMore && local.totalItems==4588,"Partial cache marker survives roundtrip");
        StationCatalog full=StationCatalog.fromVerifiedPayload(fixture(4588));
        check(StationCatalogPoll.changed(library(old),library(full)),"Same revision must publish the repaired 4588 catalogue");
        check(!StationCatalogPoll.changed(library(full),library(full)),"Unchanged revision/count must not trigger expensive publication");
        check(StationCatalogPoll.changed(null,library(full)),"Missing library publishes");
        rejects(()->StationCatalog.fromVerifiedPayload(fixture(1).put("totalItems",0)),"Total smaller than rows");
        rejects(()->StationCatalog.fromVerifiedPayload(fixture(1).put("totalItems",20001).put("hasMore",true)),"Total bounded");
        rejects(()->StationCatalog.fromVerifiedPayload(fixture(1).put("totalItems",2)),"False completeness refused");
        rejects(()->StationCatalog.fromVerifiedPayload(fixture(1).put("hasMore","false")),"Typed completeness");
        rejects(()->StationCatalog.fromVerifiedPayload(fixture(1).put("totalItems",1.5)),"Integer total");
        JSONObject missingTotal=fixture(1).put("hasMore",true);missingTotal.remove("totalItems");
        rejects(()->StationCatalog.fromVerifiedPayload(missingTotal),"Partial catalogue total required");
        JSONObject duplicate=fixture(2);duplicate.getJSONArray("items").getJSONObject(1).put("itemId","capacity_item_00000");
        rejects(()->StationCatalog.fromVerifiedPayload(duplicate),"Duplicate identity validation preserved");
        JSONObject path=fixture(1);path.getJSONArray("items").getJSONObject(0).put("folderPath",new JSONArray().put(".."));
        rejects(()->StationCatalog.fromVerifiedPayload(path),"Traversal validation preserved");
        JSONObject metadata=fixture(1);metadata.getJSONArray("items").getJSONObject(0).getJSONObject("metadata").put("description","x".repeat(2001));
        rejects(()->StationCatalog.fromVerifiedPayload(metadata),"Description limit preserved");
        check("gba".equals(StationPlatforms.resolve("gba").folder),"Existing GBA mapping");
    }
    static void signedApiAndCache(Path directory) throws Exception {
        CatalogCapacityTransportFixture.Fake f=new CatalogCapacityTransportFixture.Fake();StationApi api=f.api();
        StationApi.Cancellation cancel=new StationApi.Cancellation();StationApi.Session session=api.openSession(f.license,cancel);
        StationCatalogStore store=new StationCatalogStore(directory);
        f.catalogItems=fixture(4096).getJSONArray("items");f.total=4588;f.more=true;
        // Produce an authentic legacy cache through the fixture signing authority.
        StationApi.Response response=f.exchange("GET","/v1/station/catalog?metadata=1&maximumItems=20000",null,f.activeToken,cancel);
        byte[] legacy=response.body.readAllBytes();response.close();
        StationCatalog cached=api.restoreCatalog(legacy,session).catalog;
        check(cached.hasMore && cached.items.size()==4096,"Signed legacy offline cache remains readable");
        String owner=StationProtocol.base64Url(StationProtocol.sha256((f.license+"\n"+api.deviceId()).getBytes(StandardCharsets.UTF_8)));
        Path file=directory.resolve(owner+".json");Files.write(file,legacy);
        rejects(()->api.catalogSnapshot(session,cancel),"Signed truncated network response rejected");
        check(Arrays.equals(Files.readAllBytes(file),legacy),"Network partial cannot overwrite cache");
        for(int count:new int[]{12288,20000}) {
            f.catalogItems=fixture(count).getJSONArray("items");f.total=count;f.more=false;
            StationApi.CatalogSnapshot fresh=store.refresh(api,session,cancel);
            check(fresh.catalog.items.size()==count && "/v1/station/catalog?metadata=1&maximumItems=20000".equals(f.lastCatalogPath),"Actual signed API capacity route "+count);
            check(store.read(api,session).catalog.items.size()==count,"Signed authenticated cache "+count);
            check(store.readLocal(api,f.license).catalog.items.size()==count,"Signed offline cache "+count);
            check(fresh.encoded().length<StationProtocol.CATALOG_BODY_BYTES,"Bounded signed envelope "+count);
        }
        byte[] full=Files.readAllBytes(file);
        for(String field:new String[]{"licenseId","deviceId","sessionId","productId","applicationId","domain","schemaVersion"}) {
            f.tamper=field;rejects(()->store.refresh(api,session,cancel),"Binding validation "+field);f.tamper="";
            check(Arrays.equals(Files.readAllBytes(file),full),"Refused binding preserves full cache");
        }
        f.badSignature=true;rejects(()->store.refresh(api,session,cancel),"Signature validation preserved");f.badSignature=false;
        check(Arrays.equals(Files.readAllBytes(file),full),"Bad signature preserves full cache");
        f.catalogItems=fixture(4096).getJSONArray("items");f.total=4588;f.more=true;
        rejects(()->store.refresh(api,session,cancel),"Later truncated response cannot regress the cache");
        check(Arrays.equals(Files.readAllBytes(file),full),"Complete cache retained after incomplete response");
        check(f.closed==f.requests,"Signed response resources all closed");
    }
    static void coverCapacity() throws Exception {
        AtomicInteger calls=new AtomicInteger(),active=new AtomicInteger(),maximum=new AtomicInteger();CountDownLatch done=new CountDownLatch(1);
        try(StationCoverQueue q=new StationCoverQueue((id,cancel)->{
            maximum.accumulateAndGet(active.incrementAndGet(),Math::max);
            try {cancel.check();calls.incrementAndGet();return Paths.get("synthetic-cover.jpg");} finally {active.decrementAndGet();}
        },(id,path,result,retry)->{},text->{if(text.contains("reason=complete"))done.countDown();})) {
            q.setForeground(false);List<String> ids=new ArrayList<>();
            for(int i=0;i<20000;i++)ids.add("capacity_cover_"+i);
            ids.add(ids.get(0));ids.add("");ids.add(null);q.prefetchCatalog(ids);
            check(calls.get()==0,"Background does not start artwork IO");q.setForeground(true);
            check(done.await(30,TimeUnit.SECONDS),"Full 20000-cover plan completes");
            check(calls.get()==20000,"Every catalogue entry reaches artwork queue, duplicates excluded");
            check(maximum.get()==1,"Exactly one global cover worker preserved");
        }
    }
    public static void main(String[] args) throws Exception {
        parser();signedApiAndCache(Paths.get(args[0]));coverCapacity();
        System.out.println("PASS "+checks+" catalogue capacity, signed API/cache, migration, validation and cover queue checks");
    }
}
