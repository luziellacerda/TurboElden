package org.emulationstation.frontend.station;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import org.json.JSONArray;
import org.json.JSONObject;

/** Parser fixture only: a verified payload is supplied by the separate signed HTTP proof. */
public final class StationCatalogCapacityTest {
    private static JSONObject fixture(int count) throws Exception {
        JSONArray items=new JSONArray();
        for(int i=0;i<count;i++) items.put(new JSONObject().put("itemId",String.format("station_test_%05d",i))
            .put("name","Synthetic NES "+i).put("platform","nes").put("revision",1)
            .put("coverId",String.format("cover_test_%05d",i)));
        return new JSONObject().put("revision",1).put("items",items);
    }
    public static void main(String[] args) throws Exception {
        int checks=0;
        for(int count:new int[]{4096,4435,20000}) {
            if(StationCatalog.fromVerifiedPayload(fixture(count)).items.size()!=count)throw new AssertionError("Count differs");checks++;
        }
        try {StationCatalog.fromVerifiedPayload(fixture(20001));throw new AssertionError("Oversized catalog accepted");}
        catch(IOException expected) {checks++;}
        JSONObject duplicate=fixture(2);duplicate.getJSONArray("items").getJSONObject(1).put("itemId","station_test_00000");
        try {StationCatalog.fromVerifiedPayload(duplicate);throw new AssertionError("Duplicate accepted");}
        catch(IOException expected) {checks++;}
        if(StationPlatforms.resolve("nes").folder==null)throw new AssertionError("NES mapping missing");checks++;
        if(args.length==1) {
            JSONObject actual=new JSONObject(new String(Files.readAllBytes(Paths.get(args[0])),java.nio.charset.StandardCharsets.UTF_8));
            StationCatalog parsed=StationCatalog.fromVerifiedPayload(actual);
            if(parsed.items.size()!=4435||parsed.items.stream().filter(i->"nes".equals(i.platform)).count()!=750)throw new AssertionError("Actual catalog differs");checks++;
            StationCatalog restored=StationCatalog.fromVerifiedPayload(new JSONObject(new String(parsed.localPayload(),java.nio.charset.StandardCharsets.UTF_8)));
            if(restored.items.size()!=4435)throw new AssertionError("Cache round trip differs");checks++;
        }
        System.out.println("PASS "+checks+" catalog capacity, duplicate refusal, NES mapping and signed-payload/cache parser checks");
    }
}
