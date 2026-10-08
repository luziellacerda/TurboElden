package org.emulationstation.frontend.station;

import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/** Display-only evidence. It never grants a room, an engine or a controller. */
public final class StationCatalogPlayerEvidence {
    public static final String VERIFIED = "verified-exact-content";
    static final int MAX_HISTORY = 40000;
    private static final byte[] UNKNOWN = "—".getBytes(StandardCharsets.UTF_8);
    private static volatile Map<String, Result> published = Collections.emptyMap();
    private static final Map<String, RememberedBinding> history = new LinkedHashMap<>();
    private static boolean historyExhausted;
    private StationCatalogPlayerEvidence() {}

    public static final class Mode {
        public final String id, style;
        private final int[] counts;
        private final String[] sources;
        public Mode(String id, String style, int[] counts, String[] sources) {
            this.id=id; this.style=style;
            this.counts=counts==null?new int[0]:counts.clone();
            this.sources=sources==null?new String[0]:sources.clone();
        }
    }
    public static final class Evidence {
        public final String itemId, contentSha256, status;
        public final long itemRevision;
        private final Mode[] modes;
        public Evidence(String itemId,long itemRevision,String contentSha256,String status,Mode[] modes) {
            this.itemId=itemId;this.itemRevision=itemRevision;this.contentSha256=contentSha256;this.status=status;
            this.modes=modes==null?new Mode[0]:modes.clone();
        }
    }
    public static final class Result {
        public final boolean confirmed;
        public final String compact, detail;
        private final String itemId, contentSha256;
        private final long itemRevision;
        private Result(boolean confirmed,String compact,String detail,String itemId,long revision,String digest) {
            this.confirmed=confirmed;this.compact=compact;this.detail=detail;
            this.itemId=itemId;this.itemRevision=revision;this.contentSha256=digest;
        }
    }
    public static Result pending() { return new Result(false,"—","Jogadores a confirmar para esta edição.",null,0,""); }
    public static boolean digest(String value) { return value!=null&&value.matches("[0-9a-f]{64}"); }

    /** All three binding fields come from the already authenticated catalogue. */
    public static Result evaluate(String itemId,long itemRevision,String catalogContentSha256,Evidence evidence) {
        if(itemId==null||!itemId.matches("[A-Za-z0-9_-]{8,64}")||itemRevision<1||!digest(catalogContentSha256)
                ||evidence==null||!VERIFIED.equals(evidence.status)||!itemId.equals(evidence.itemId)
                ||itemRevision!=evidence.itemRevision||!catalogContentSha256.equals(evidence.contentSha256)
                ||evidence.modes.length<1||evidence.modes.length>16)return pending();
        int simultaneous=0,alternating=0;boolean solo=false;
        Map<String,Boolean> ids=new LinkedHashMap<>();StringBuilder details=new StringBuilder();
        for(Mode mode:evidence.modes) {
            if(mode==null||mode.id==null||!mode.id.matches("[a-z0-9][a-z0-9-]{0,63}")
                    ||ids.put(mode.id,Boolean.TRUE)!=null||mode.counts.length<1||mode.counts.length>16
                    ||mode.sources.length<1||mode.sources.length>16)return pending();
            for(String source:mode.sources)if(source==null||!source.matches("[a-z0-9][a-z0-9-]{0,95}"))return pending();
            int previous=0;
            for(int count:mode.counts){if(count<=previous||count>16)return pending();previous=count;}
            String label;
            if("single-player".equals(mode.style)) {
                if(previous!=1||mode.counts.length!=1)return pending();solo=true;label="Individual: 1 jogador";
            } else if("simultaneous".equals(mode.style)) {
                if(previous<2)return pending();simultaneous=Math.max(simultaneous,previous);
                label="Simultâneo: "+counts(mode.counts)+" jogadores";
            } else if("alternating".equals(mode.style)) {
                if(previous<2)return pending();alternating=Math.max(alternating,previous);
                label="Alternado: "+counts(mode.counts)+" jogadores";
            } else return pending();
            if(details.length()>0)details.append("\n");details.append(label);
        }
        // Keep the style beside the number: alternating maxima are never simultaneous capacity.
        String compact=simultaneous>0?simultaneous+" sim.":alternating>0?alternating+" alt.":solo?"1":"—";
        return new Result(true,compact,details.toString(),itemId,itemRevision,catalogContentSha256);
    }
    private static String counts(int[] values) {
        StringBuilder out=new StringBuilder();for(int i=0;i<values.length;i++){if(i>0)out.append(i==values.length-1?" ou ":", ");out.append(values[i]);}return out.toString();
    }
    public static final class CatalogBinding {
        public final String itemId, contentSha256;
        public final long itemRevision;
        public CatalogBinding(String itemId,long itemRevision,String contentSha256) {
            this.itemId=itemId;this.itemRevision=itemRevision;this.contentSha256=contentSha256;
        }
    }
    private static final class RememberedBinding {
        final long revision;final String digest;boolean invalidated;
        RememberedBinding(CatalogBinding value){revision=value.itemRevision;digest=value.contentSha256;}
        boolean same(CatalogBinding value){return revision==value.itemRevision&&digest.equals(value.contentSha256);}
    }
    /** The native catalogue applies asynchronously and has no per-row content digest.
     * Reused IDs that change binding stay unknown for the rest of this process, even
     * after removal/reinsertion or a later rollback. Bounded history fails closed. */
    public static synchronized void publish(CatalogBinding[] catalog,Map<String,Result> values) {
        if(historyExhausted||catalog==null||catalog.length>4096||values==null||values.size()>4096) {
            published=Collections.emptyMap();return;
        }
        Map<String,CatalogBinding> bindings=new LinkedHashMap<>();
        for(CatalogBinding value:catalog) {
            if(value==null||value.itemId==null||!value.itemId.matches("[A-Za-z0-9_-]{8,64}")
                    ||value.itemRevision<1||value.contentSha256==null
                    ||!value.contentSha256.isEmpty()&&!digest(value.contentSha256)
                    ||bindings.put(value.itemId,value)!=null){published=Collections.emptyMap();return;}
        }
        int additions=0;for(String id:bindings.keySet())if(!history.containsKey(id))additions++;
        if(additions>MAX_HISTORY-history.size()) {historyExhausted=true;published=Collections.emptyMap();return;}
        for(CatalogBinding value:bindings.values()) {
            RememberedBinding previous=history.get(value.itemId);
            if(previous==null)history.put(value.itemId,new RememberedBinding(value));
            else if(!previous.same(value))previous.invalidated=true;
        }
        Map<String,Result> safe=new LinkedHashMap<>();
        for(CatalogBinding binding:bindings.values()) {
            Result result=values.get(binding.itemId);RememberedBinding remembered=history.get(binding.itemId);
            if(!remembered.invalidated&&result!=null&&result.confirmed&&binding.itemId.equals(result.itemId)
                    &&binding.itemRevision==result.itemRevision&&binding.contentSha256.equals(result.contentSha256))safe.put(binding.itemId,result);
        }
        published=Collections.unmodifiableMap(safe);
    }
    /** JNI read: bounded, immutable in-memory snapshot; no file, hash, network or Android work. */
    public static byte[] labelFor(String itemId) {
        Result result=published.get(itemId);return result==null?UNKNOWN.clone():result.compact.getBytes(StandardCharsets.UTF_8);
    }
}
