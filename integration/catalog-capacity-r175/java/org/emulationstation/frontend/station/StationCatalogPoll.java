package org.emulationstation.frontend.station;

/** Generation gate for foreground-only refresh. No network operation runs under this lock. */
final class StationCatalogPoll {
 static final class Ticket {
  final long generation;final StationApi.Cancellation cancel=new StationApi.Cancellation();
  Ticket(long generation){this.generation=generation;}
 }
 private long generation;private boolean enabled;private Ticket active;
 synchronized void resume(){if(!enabled){enabled=true;generation++;}}
 void pause(){Ticket old;synchronized(this){enabled=false;generation++;old=active;}if(old!=null)old.cancel.cancel();}
 synchronized Ticket begin(){if(!enabled||active!=null)return null;active=new Ticket(generation);return active;}
 synchronized boolean current(Ticket ticket){return enabled&&active==ticket&&ticket.generation==generation&&!ticket.cancel.cancelled();}
 synchronized void finish(Ticket ticket){if(active==ticket)active=null;}
 static boolean changed(long oldRevision,String oldName,long newRevision,String newName){return oldRevision!=newRevision||!oldName.equals(newName);}
 static boolean changed(StationCoordinator.Library old,StationCoordinator.Library next){
  return old==null||changed(old.catalog.revision,old.displayName,next.catalog.revision,next.displayName)
    ||old.catalog.items.size()!=next.catalog.items.size()
    ||old.catalog.totalItems!=next.catalog.totalItems||old.catalog.hasMore!=next.catalog.hasMore;
 }
}
