package org.emulationstation.frontend.station;

import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/** Reviewed original-game descriptions, independent of online admission.
 * Exact catalog ID, revision, platform and title only. Never fuzzy title matching.
 * These facts do not prove downloaded bytes, controller readiness or online seats.
 */
public final class StationGamePlayerFacts {
    private StationGamePlayerFacts() {}
    public static final class Fact {
        public final String compact, summary, detail, source;
        private Fact(int maximum,String text,String source) {
            compact=maximum==1?"1":maximum+" sim.";
            summary=maximum==1?"Jogo: 1 jogador":"Jogo: até "+maximum;
            detail="Jogo original: "+text;
            this.source=source;
        }
    }
    private static final class Entry {
        final String id,platform,name,contentDigest; final long revision; final Fact fact;
        Entry(String id,String platform,String name,String digest,int maximum,String detail,String source) {
            this.id=id;this.platform=platform;this.name=name;contentDigest=digest;revision=4;
            fact=new Fact(maximum,detail,source);
        }
        boolean matches(StationCatalog.Item item) {
            return item!=null&&id.equals(item.itemId)&&revision==item.revision&&platform.equals(item.platform)&&name.equals(item.name)
                &&(item.contentSha256.isEmpty()||contentDigest.isEmpty()||contentDigest.equals(item.contentSha256));
        }
    }
    // Only five reviewed catalog editions. Translations, conflicts, DAT guesses and
    // region-mismatched manual candidates from the audit are not promoted here.
    private static final Entry[] ENTRIES={
        new Entry("station_df50d575815ab105084a79d68e0c8fb3","snes","Super Bomberman 2",
            "0a4b4a783a7faf6ada3e1326ecf85de77e8c2a171659b42a78a1fae43f806ca6",4,
            "campanha para 1 jogador; batalha para até 4 simultâneos. Para 3 ou 4, o jogo exige Multitap e posições humanas configuradas.",
            "https://www.videogamemanual.com/snes/Super%20Bomberman%202%20(USA).pdf"),
        new Entry("station_46fe7356ab5cc63a1438f720b9c7ce2d","snes","Super Bomberman 3",
            "3c665283c14f050b60fe9693b12e437288bcd4aa3e56ef25106d503c44e0fda5",5,
            "campanha para 1 ou 2; batalha para até 5 simultâneos, incluindo partidas com 3 ou 4. Acima de 2, exige Multitap. O online deste aplicativo comporta no máximo 4, nos modos liberados.",
            "https://www.retrogames.cz/manualy/SNES/Super_Bomberman_3_-_SNES_-_Manual.pdf"),
        new Entry("station_3f28d41c9e666e0080106eda728e89da","n64","Bomberman Hero","",1,
            "aventura individual, para 1 jogador. Não oferece um modo de batalha multiplayer.",
            "https://www.nintendo.com/en-gb/Games/Nintendo-64/Bomberman-Hero-276445.html"),
        new Entry("station_3f0267d082d3d99218768e6f4088960b","dreamcast","Bomberman Online","",4,
            "campanha para 1; batalha local para até 4 simultâneos. O modo de rede original do Dreamcast é separado das salas deste aplicativo.",
            "https://www.digitpress.com/library/manuals/dreamcast/bomberman_online.pdf"),
        new Entry("cbd83be3e89456758ad7c165907abd12","megadrive","The Lost Vikings","",3,
            "versão Mega Drive para 1, 2 ou 3 em cooperação. O terceiro exige Sega Team Player e seleção de 3 jogadores nas opções. Essa regra não se aplica automaticamente à versão SNES.",
            "https://manualzz.com/doc/22466256/sega-genesis--the-lost-vikings-video-game-instruction-manual")
    };
    public static Fact forItem(StationCatalog.Item item) {
        for(Entry entry:ENTRIES)if(entry.matches(item))return entry.fact;
        return null;
    }
    private static final class Binding {
        final long revision;final String platform,name,digest;
        Binding(StationCatalog.Item item){revision=item.revision;platform=item.platform;name=item.name;digest=item.contentSha256;}
        boolean matches(StationCatalog.Item item){return revision==item.revision&&platform.equals(item.platform)&&name.equals(item.name)&&digest.equals(item.contentSha256);}
    }
    private static final Map<String,Binding> history=new LinkedHashMap<>();
    private static final java.util.Set<String> invalidated=new java.util.HashSet<>();
    private static volatile Map<String,Fact> published=Collections.emptyMap();
    private static volatile int generation;
    public static int generation(){return generation;}
    private static String diagnostic="";
    /** Only five possible history entries. Called off the render thread after catalog verification. */
    public static synchronized void publish(StationCatalog catalog) {
        Map<String,Fact> values=new LinkedHashMap<>();
        if(catalog!=null)for(StationCatalog.Item item:catalog.items) {
            for(Entry entry:ENTRIES)if(entry.id.equals(item.itemId)) {
                Binding old=history.get(item.itemId);
                if(old==null)history.put(item.itemId,new Binding(item));
                else if(!old.matches(item))invalidated.add(item.itemId);
                if(!invalidated.contains(item.itemId)&&entry.matches(item))values.put(item.itemId,entry.fact);
            }
        }
        published=Collections.unmodifiableMap(values);
        generation++;
        StringBuilder state=new StringBuilder("facts="+values.size());
        if(catalog!=null)for(int i=0;i<ENTRIES.length;i++)for(StationCatalog.Item item:catalog.items)if(ENTRIES[i].id.equals(item.itemId)){
            Entry e=ENTRIES[i];state.append(" row").append(i).append(":rev=").append(item.revision)
              .append(",title=").append(e.name.equals(item.name)).append(",platform=").append(e.platform.equals(item.platform))
              .append(",digest=").append(item.contentSha256.isEmpty()||e.contentDigest.isEmpty()||e.contentDigest.equals(item.contentSha256))
              .append(",invalidated=").append(invalidated.contains(item.itemId));
        }
        String next=state.toString();if(!next.equals(diagnostic)){diagnostic=next;android.util.Log.i("StationPlayers",next);}
    }
    /** Immutable memory lookup used by the existing native label bridge. */
    public static byte[] labelFor(String id) {
        Fact fact=published.get(id);
        return (fact==null?"—":fact.compact).getBytes(StandardCharsets.UTF_8);
    }
}
