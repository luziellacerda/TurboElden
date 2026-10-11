package org.emulationstation.frontend.netplay;
import android.app.Service;
import android.content.Intent;
import android.os.*;
import java.util.*;

/** Private bound service: the foreground native client keeps its HTTP owner executable. */
public final class StationSessionService extends Service {
    static final int ATTACH=1,DETACH=2,ATTACHED=3,REJECTED=4;
    private final Handler handler=new Handler(Looper.getMainLooper(),this::receive);
    private final Messenger endpoint=new Messenger(handler);
    private final Map<IBinder,Claim> clients=new HashMap<>();
    private final Map<String,IBinder> sessions=new HashMap<>();
    private final class Claim implements IBinder.DeathRecipient {
        final String key;final StationGameSession owner;final IBinder client;
        Claim(String key,StationGameSession owner,IBinder client){this.key=key;this.owner=owner;this.client=client;}
        @Override public void binderDied(){handler.post(()->release(client,true));}
    }
    @Override public IBinder onBind(Intent intent){return endpoint.getBinder();}
    private boolean receive(Message message){
        // Messenger preserves the Binder sender UID in sendingUid; Handler.getCallingUid does not.
        if(message.sendingUid!=android.os.Process.myUid()||message.replyTo==null)return true;
        Bundle data=message.getData();String key=data.getString("session"),room=data.getString("room");long generation=data.getLong("generation",-1);int attempt=data.getInt("attempt",-1);
        IBinder peer=message.replyTo.getBinder();
        if(message.what==DETACH){Claim claim=clients.get(peer);if(claim!=null&&claim.key.equals(key))release(peer,true);return true;}
        if(message.what!=ATTACH||attempt<1)return true;
        StationGameSession owner=StationGameSession.anchorOwner(key,room,generation);
        IBinder existing=sessions.get(key);Claim same=clients.get(peer);
        if(owner==null||(existing!=null&&!existing.equals(peer))||(same!=null&&(same.owner!=owner||!same.key.equals(key)))){reply(message,REJECTED,data);return true;}
        if(same==null){Claim claim=new Claim(key,owner,peer);try{peer.linkToDeath(claim,0);}catch(RemoteException dead){owner.anchorEnded();return true;}clients.put(peer,claim);sessions.put(key,peer);}
        reply(message,ATTACHED,data);return true;
    }
    private void reply(Message request,int what,Bundle data){
        Message response=Message.obtain(null,what);Bundle value=new Bundle();value.putString("session",data.getString("session"));value.putString("room",data.getString("room"));value.putLong("generation",data.getLong("generation",-1));value.putInt("attempt",data.getInt("attempt",-1));response.setData(value);
        try{request.replyTo.send(response);}catch(RemoteException gone){release(request.replyTo.getBinder(),true);}
    }
    private void release(IBinder peer,boolean ended){Claim claim=clients.remove(peer);if(claim==null)return;sessions.remove(claim.key);try{peer.unlinkToDeath(claim,0);}catch(NoSuchElementException alreadyGone){}if(ended)claim.owner.anchorEnded();}
    private void releaseAll(){for(IBinder peer:new ArrayList<>(clients.keySet()))release(peer,true);}
    @Override public boolean onUnbind(Intent intent){releaseAll();return false;}
    @Override public void onDestroy(){releaseAll();handler.removeCallbacksAndMessages(null);super.onDestroy();}
}
