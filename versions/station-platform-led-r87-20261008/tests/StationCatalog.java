package org.emulationstation.frontend.station;
import java.util.*;
public final class StationCatalog {
 public final List<Item> items;
 public StationCatalog(Item... items){this.items=Arrays.asList(items);}
 public static final class Item {
  public final String itemId,platform,name,contentSha256;public final long revision;
  public Item(String id,long revision,String platform,String name,String digest){itemId=id;this.revision=revision;this.platform=platform;this.name=name;contentSha256=digest;}
 }
}
