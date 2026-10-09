package org.emulationstation.frontend.station;

import java.io.IOException;
import java.util.*;

/** Publish verified platform mappings while explicitly accounting for unsupported entries. */
public final class StationPublication {
 public static final class Row {
  public final StationCatalog.Item item;public final StationPlatforms.Platform platform;
  private Row(StationCatalog.Item item,StationPlatforms.Platform platform){this.item=item;this.platform=platform;}
 }
 public final List<Row> rows;
 public final Map<String,Integer> unsupported;
 public final int unsupportedCount;
 public StationPublication(StationCatalog catalog)throws IOException {
  List<Row> supported=new ArrayList<>();Map<String,Integer> missing=new TreeMap<>();int count=0;
  for(StationCatalog.Item item:catalog.items){
   try{supported.add(new Row(item,StationPlatforms.resolve(item.platform)));}
   catch(StationPlatforms.UnsupportedPlatform absent){missing.merge(absent.platform,1,Integer::sum);count++;}
  }
  if(supported.isEmpty()&&!catalog.items.isEmpty())StationPlatforms.resolve(catalog.items.get(0).platform);
  rows=Collections.unmodifiableList(supported);unsupported=Collections.unmodifiableMap(missing);unsupportedCount=count;
 }
 public String warning(){
  if(unsupportedCount==0)return "";
  StringBuilder platforms=new StringBuilder();int shown=0;
  for(String platform:unsupported.keySet()){
   if(shown++==3){platforms.append(", …");break;}
   if(platforms.length()>0)platforms.append(", ");platforms.append(platform);
  }
  return unsupportedCount+(unsupportedCount==1?" jogo aguarda suporte a ":" jogos aguardam suporte a ")+platforms+". Atualize o aplicativo para acessar esses jogos.";
 }
}
