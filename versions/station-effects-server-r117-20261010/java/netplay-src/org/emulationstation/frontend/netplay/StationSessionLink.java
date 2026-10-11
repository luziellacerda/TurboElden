package org.emulationstation.frontend.netplay;
import android.app.Activity;
import android.content.*;
import android.os.*;

/** Real Messenger IPC; no local-Binder cast across :station_netplay/main processes. */
final class StationSessionLink implements AutoCloseable {
    interface Listener{void ready();void unavailable(String category);}
    private final Activity activity;private final String key,room;private final long generation;private final Listener listener;
    private final Handler handler=new Handler(Looper.getMainLooper(),this::receive);
    private final Messenger replies=new Messenger(handler);
    private Messenger service;private Connection connection;private boolean closed,ready;private int attempt;
    StationSessionLink(Activity activity,String key,String room,long generation,Listener listener){if(key==null||room==null||generation<0)throw new IllegalArgumentException("Missing session identity");this.activity=activity;this.key=key;this.room=room;this.generation=generation;this.listener=listener;}
    void bind(){
        if(closed||connection!=null)return;
        Connection next=new Connection(++attempt);connection=next;next.bound=true;
        try{boolean accepted=activity.bindService(new Intent(activity,StationSessionService.class),next,Context.BIND_AUTO_CREATE|Context.BIND_IMPORTANT);if(!accepted){connection=null;unbind(next);listener.unavailable("BIND_UNAVAILABLE");}}
        catch(RuntimeException error){connection=null;unbind(next);listener.unavailable("BIND_FAILED");}
    }
    private Bundle identity(){Bundle data=new Bundle();data.putString("session",key);data.putString("room",room);data.putLong("generation",generation);data.putInt("attempt",attempt);return data;}
    private void send(int what)throws RemoteException{if(service==null)throw new RemoteException("Session service unavailable");Message request=Message.obtain(null,what);request.replyTo=replies;request.setData(identity());service.send(request);}
    private boolean receive(Message message){
        if(closed||connection==null||!connection.bound||service==null||message.sendingUid!=android.os.Process.myUid())return true;
        Bundle data=message.getData();if(!key.equals(data.getString("session"))||!room.equals(data.getString("room"))||generation!=data.getLong("generation",-1)||attempt!=data.getInt("attempt",-1))return true;
        if(message.what==StationSessionService.ATTACHED){if(!ready){ready=true;listener.ready();}}
        else if(message.what==StationSessionService.REJECTED){ready=false;listener.unavailable("SESSION_IDENTITY");}
        return true;
    }
    private void unbind(Connection target){if(target==null||!target.bound)return;target.bound=false;try{activity.unbindService(target);}catch(IllegalArgumentException ignored){}}
    private final class Connection implements ServiceConnection {
        final int number;boolean bound;Connection(int number){this.number=number;}
        private boolean current(){return !closed&&connection==this&&number==attempt;}
        @Override public void onServiceConnected(ComponentName name,IBinder binder){if(!current())return;service=new Messenger(binder);try{send(StationSessionService.ATTACH);}catch(RemoteException error){ready=false;listener.unavailable("BINDER_UNAVAILABLE");}}
        @Override public void onServiceDisconnected(ComponentName name){if(!current())return;service=null;ready=false;listener.unavailable("BINDER_DISCONNECTED");/* Keep binding: Android may reconnect it. */}
        @Override public void onBindingDied(ComponentName name){if(!current())return;service=null;ready=false;connection=null;unbind(this);listener.unavailable("BINDING_DIED");bind();}
        @Override public void onNullBinding(ComponentName name){if(!current())return;service=null;ready=false;connection=null;unbind(this);listener.unavailable("NULL_BINDING");}
    }
    @Override public void close(){if(closed)return;closed=true;ready=false;try{send(StationSessionService.DETACH);}catch(RemoteException ignored){}Connection old=connection;connection=null;service=null;unbind(old);handler.removeCallbacksAndMessages(null);}
}
