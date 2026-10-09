package org.emulationstation.frontend.station;

import android.content.Context;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import org.json.JSONArray;
import org.json.JSONObject;

/** Small, reviewed application asset; research candidates are deliberately not packaged here. */
final class StationCatalogPlayerEvidenceLoader {
    private static Map<String,StationCatalogPlayerEvidence.Evidence> reviewed;
    private StationCatalogPlayerEvidenceLoader() {}
    static void publish(Context context,StationCatalog catalog) {
        Map<String,StationCatalogPlayerEvidence.Result> confirmed=new LinkedHashMap<>();
        StationCatalogPlayerEvidence.CatalogBinding[] bindings=new StationCatalogPlayerEvidence.CatalogBinding[catalog.items.size()];
        int index=0;
        for(StationCatalog.Item item:catalog.items)bindings[index++]=new StationCatalogPlayerEvidence.CatalogBinding(item.itemId,item.revision,item.contentSha256);
        try {
            Map<String,StationCatalogPlayerEvidence.Evidence> evidence=load(context);
            for(StationCatalog.Item item:catalog.items) {
                StationCatalogPlayerEvidence.Result result=StationCatalogPlayerEvidence.evaluate(
                        item.itemId,item.revision,item.contentSha256,evidence.get(item.itemId));
                if(result.confirmed)confirmed.put(item.itemId,result);
            }
        } catch(Exception unavailable) { confirmed.clear(); }
        StationCatalogPlayerEvidence.publish(bindings,confirmed);
    }
    private static synchronized Map<String,StationCatalogPlayerEvidence.Evidence> load(Context context)throws Exception {
        if(reviewed!=null)return reviewed;
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();
        try(InputStream input=context.getAssets().open("station-catalog/player-evidence-v1.json")) {
            byte[] buffer=new byte[4096];int n;
            while((n=input.read(buffer))!=-1){if(bytes.size()+n>1048576)throw new IllegalArgumentException("Evidence size");bytes.write(buffer,0,n);}
        }
        JSONObject root=new JSONObject(new String(bytes.toByteArray(),StandardCharsets.UTF_8));
        if(root.getInt("schemaVersion")!=1||!"reviewed-player-evidence".equals(root.getString("kind")))throw new IllegalArgumentException("Evidence schema");
        JSONArray rows=root.getJSONArray("records");if(rows.length()>4096)throw new IllegalArgumentException("Evidence count");
        Map<String,StationCatalogPlayerEvidence.Evidence> result=new LinkedHashMap<>();
        for(int i=0;i<rows.length();i++) {
            JSONObject row=rows.getJSONObject(i);String id=row.getString("itemId");
            JSONArray modes=row.getJSONArray("modes");if(modes.length()>16)throw new IllegalArgumentException("Mode count");
            StationCatalogPlayerEvidence.Mode[] parsed=new StationCatalogPlayerEvidence.Mode[modes.length()];
            for(int m=0;m<parsed.length;m++) {
                JSONObject mode=modes.getJSONObject(m);JSONArray counts=mode.getJSONArray("allowedHumanCounts"),sources=mode.getJSONArray("sourceRefs");
                if(counts.length()>16||sources.length()>16)throw new IllegalArgumentException("Mode limits");
                int[] c=new int[counts.length()];String[] s=new String[sources.length()];
                for(int j=0;j<c.length;j++){Object v=counts.get(j);if(!(v instanceof Integer))throw new IllegalArgumentException("Human count");c[j]=(Integer)v;}
                for(int j=0;j<s.length;j++)s[j]=sources.getString(j);
                parsed[m]=new StationCatalogPlayerEvidence.Mode(mode.getString("modeId"),mode.getString("playStyle"),c,s);
            }
            Object revision=row.get("itemRevision");if(!(revision instanceof Integer)&&!(revision instanceof Long))throw new IllegalArgumentException("Revision");
            if(result.put(id,new StationCatalogPlayerEvidence.Evidence(id,((Number)revision).longValue(),row.getString("contentSha256"),row.getString("evidenceStatus"),parsed))!=null)throw new IllegalArgumentException("Duplicate evidence");
        }
        reviewed=Collections.unmodifiableMap(result);return reviewed;
    }
}
