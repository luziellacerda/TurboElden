package org.emulationstation.frontend.station;
import java.nio.charset.StandardCharsets;
public class PlayerFactsTest {
 static int checks;
 static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
 static StationCatalog.Item item(String id,long revision,String platform,String name,String digest){return new StationCatalog.Item(id,revision,platform,name,digest);}
 static String label(String id){return new String(StationGamePlayerFacts.labelFor(id),StandardCharsets.UTF_8);}
 public static void main(String[] args){
  String[][] rows={
   {"station_df50d575815ab105084a79d68e0c8fb3","snes","Super Bomberman 2","4 sim."},
   {"station_46fe7356ab5cc63a1438f720b9c7ce2d","snes","Super Bomberman 3","5 sim."},
   {"station_3f28d41c9e666e0080106eda728e89da","n64","Bomberman Hero","1"},
   {"station_3f0267d082d3d99218768e6f4088960b","dreamcast","Bomberman Online","4 sim."},
   {"cbd83be3e89456758ad7c165907abd12","megadrive","The Lost Vikings","3 sim."}};
  StationCatalog.Item[] all=new StationCatalog.Item[5];
  for(int i=0;i<rows.length;i++){
   String[] r=rows[i];all[i]=item(r[0],4,r[1],r[2],"");StationGamePlayerFacts.Fact f=StationGamePlayerFacts.forItem(all[i]);
   check(f!=null&&f.compact.equals(r[3]),"documented count");check(f.source.startsWith("https://"),"source");check(f.detail.startsWith("Jogo original:"),"scope original");
   check(StationGamePlayerFacts.forItem(item(r[0]+"x",4,r[1],r[2],""))==null,"ID not guessed");
   check(StationGamePlayerFacts.forItem(item(r[0],5,r[1],r[2],""))==null,"revision drift");
   check(StationGamePlayerFacts.forItem(item(r[0],4,r[1]+"br",r[2],""))==null,"translation not inferred");
   check(StationGamePlayerFacts.forItem(item(r[0],4,r[1],r[2]+" (hack)",""))==null,"title drift");
   check(StationGamePlayerFacts.forItem(item("unknown01",4,r[1],r[2],""))==null,"no fuzzy binding");
  }
  check(StationGamePlayerFacts.forItem(null)==null,"null");
  check(StationGamePlayerFacts.forItem(item(rows[1][0],4,"snes",rows[1][2],new String(new char[64]).replace('\0','a')))==null,"conflicting content digest");
  check(StationGamePlayerFacts.forItem(all[1]).detail.contains("1 ou 2")&&StationGamePlayerFacts.forItem(all[1]).detail.contains("máximo 4"),"campaign and app limit");
  StationGamePlayerFacts.publish(new StationCatalog(all));for(String[] r:rows)check(label(r[0]).equals(r[3]),"published facts");
  check(label("missing01").equals("—"),"unknown no default2");check(label(null).equals("—"),"null no default2");
  byte[] b=StationGamePlayerFacts.labelFor(rows[0][0]);b[0]='9';check(label(rows[0][0]).equals("4 sim."),"immutable label");
  StationGamePlayerFacts.publish(new StationCatalog());check(label(rows[1][0]).equals("—"),"removed row");
  StationGamePlayerFacts.publish(new StationCatalog(all));check(label(rows[1][0]).equals("5 sim."),"same binding restored");
  StationGamePlayerFacts.publish(new StationCatalog(item(rows[1][0],5,"snes",rows[1][2],"")));check(label(rows[1][0]).equals("—"),"revision invalidates");
  StationGamePlayerFacts.publish(new StationCatalog(all));check(label(rows[1][0]).equals("—"),"old asynchronous ID cannot revive");
  StationGamePlayerFacts.publish(null);for(String[] r:rows)check(label(r[0]).equals("—"),"clear snapshot");
  System.out.println("checks="+checks);
 }
}
