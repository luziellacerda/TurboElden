package org.emulationstation.frontend.station;
import java.text.*;
import java.util.*;
/** Optional standard response header; no new endpoint or server field is assumed. */
public final class StationRetryAfter {
 private StationRetryAfter(){}
 public static long parse(String value,long wallMillis){
  if(value==null||value.length()>128)return 0;
  value=value.trim();
  try{if(value.matches("[0-9]{1,9}"))return Math.min(86400000L,Math.max(1000L,Long.parseLong(value)*1000L));
   SimpleDateFormat format=new SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss zzz",Locale.US);format.setLenient(false);format.setTimeZone(TimeZone.getTimeZone("GMT"));
   ParsePosition position=new ParsePosition(0);Date date=format.parse(value,position);
   if(date==null||position.getIndex()!=value.length())return 0;
   return Math.min(86400000L,Math.max(1000L,date.getTime()-wallMillis));
  }catch(RuntimeException invalid){return 0;}
 }
}
