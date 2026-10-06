package org.emulationstation.frontend.netplay;
import android.os.*;

/** Isolated Android framework test. No app data, license, game or server access. */
public final class StationSessionChannelDeviceTest {
    private static int checks, received;
    private static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
    private static Bundle wire(Bundle data){
        Parcel p=Parcel.obtain();
        try{p.writeBundle(data);p.setDataPosition(0);return p.readBundle(null);}
        finally{p.recycle();}
    }
    public static void main(String[] args){
        ResultReceiver local=new ResultReceiver(null){
            @Override protected void onReceiveResult(int code,Bundle data){
                received++;check(code==71,"callback code retained");
                check(data!=null&&"probe".equals(data.getString("message")),"callback payload retained");
            }
        };
        Bundle old=new Bundle();old.putParcelable("reply",local);
        boolean reproduced=false;
        try{wire(old).getParcelable("reply");}catch(BadParcelableException expected){reproduced=true;}
        check(reproduced,"baseline anonymous receiver must reproduce failure with framework loader");
        check(StationSessionChannel.read(wire(old),"reply")==null,"malformed legacy callback cannot crash recipient");
        check(StationSessionChannel.transport(null)==null,"null receiver");
        check(StationSessionChannel.read(null,"reply")==null,"null bundle");
        Bundle wrong=new Bundle();wrong.putString("reply","not a receiver");
        check(StationSessionChannel.read(wire(wrong),"reply")==null,"wrong payload type");
        for(int i=0;i<64;i++){
            ResultReceiver transport=StationSessionChannel.transport(local);
            check(transport.getClass()==ResultReceiver.class,"only framework class leaves sender");
            Bundle forward=new Bundle();forward.putParcelable("station.sessionEvents",transport);
            ResultReceiver atGame=StationSessionChannel.read(wire(forward),"station.sessionEvents");
            check(atGame!=null&&atGame.getClass()==ResultReceiver.class,"forward receiver deserializes");
            Bundle backward=new Bundle();backward.putParcelable("reply",StationSessionChannel.transport(local));
            ResultReceiver atCatalog=StationSessionChannel.read(wire(backward),"reply");
            check(atCatalog!=null,"reply receiver deserializes");
            Bundle payload=new Bundle();payload.putString("message","probe");
            atGame.send(71,payload);atCatalog.send(71,payload);
        }
        check(received==128,"both directions still invoke original receivers");
        System.out.println("PASS "+checks+" Android Parcel/ResultReceiver checks; original failure reproduced; callbacks preserved in both directions.");
    }
}
