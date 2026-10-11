package org.emulationstation.frontend.netplay;
import java.util.HashMap;
import java.util.Map;

/** One live launch identity in the main process; never a second authentication authority. */
final class StationSessionRegistry<T> {
    private static final class Entry<T>{final String room;final long generation;final T owner;Entry(String r,long g,T o){room=r;generation=g;owner=o;}}
    private final Map<String,Entry<T>> entries=new HashMap<>();
    synchronized void put(String key,String room,long generation,T owner){
        if(key==null||!key.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")||room==null||!room.matches("[0-9a-f]{32}")||generation<0||owner==null||!entries.isEmpty())throw new IllegalArgumentException("Invalid session identity");
        entries.put(key,new Entry<T>(room,generation,owner));
    }
    synchronized T find(String key,String room,long generation){Entry<T> e=entries.get(key);return e!=null&&e.generation==generation&&e.room.equals(room)?e.owner:null;}
    synchronized void remove(String key,T owner){Entry<T> e=entries.get(key);if(e!=null&&e.owner==owner)entries.remove(key);}
    synchronized int size(){return entries.size();}
}
