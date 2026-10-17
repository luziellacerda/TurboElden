// SPDX-License-Identifier: GPL-2.0-or-later
package org.emulationstation.frontend.netplay;

import static org.emulationstation.frontend.netplay.StationPsxSessionProbe.*;

/** Real Java resume decision + real C++ protocol, synthetic owner, no game/Android. */
public final class StationPsxResumeRaceProbe {
    private static int assertions;
    private static native void initializePair(long epoch);
    private static native long[] protocolStatus(int slot);
    private static native int protocolResume(int slot,long epoch,long serial);
    private static native int advanceOwner(int slot);
    private static native int pendingPeerPackets(int slot);

    private static void require(boolean value,String message) {
        assertions++;
        if(!value)throw new AssertionError(message);
    }
    private static Object javaSession(long epoch)throws Exception {
        Object s=session(new StationPsxOnlineActivity());
        for(String field:new String[]{"descriptorValid","visible","ownerReady","configured","loaded"})set(s,field,true);
        ((StationMultiplayerSession.Listener)s).nativeControl(epoch,false,true);
        require(serial(s)==2,"test and native exact control serial agree");
        return s;
    }
    private static void select(int slot) {
        StationPsxBridge.beforeStatus=()->StationPsxBridge.status=protocolStatus(slot);
        StationPsxBridge.resumeHook=(epoch,serial)->protocolResume(slot,epoch,serial);
    }
    private static void tick(Object s,int slot)throws Exception {
        select(slot);
        call(s,"update",new Class<?>[]{});
    }
    private static void race(int first,long epoch)throws Exception {
        StationPsxBridge.reset();
        initializePair(epoch);
        Object host=javaSession(epoch),guest=javaSession(epoch);
        try {
            for(int slot=1;slot<=2;slot++) {
                select(slot);
                require((((StationMultiplayerSession.Listener)(slot==1?host:guest)).nativeStatus()&3)==3,
                    "both owners satisfy drained synchronization barrier before PLAYING");
            }
            int second=3-first;
            tick(first==1?host:guest,first);
            require(advanceOwner(first)==(first==1?0:2),"first owner runs or waits for canonical host frame");
            long[] pending=protocolStatus(second);
            require(pending[StationPsxBridge.INITIAL_STATE_SYNCED]==1,"peer traffic preserves applied snapshot");
            require(pending[StationPsxBridge.ACK_VALID]==1,"second owner has genuine pause ACK for exact serial");
            if(first==2) {
                require(pending[StationPsxBridge.DRAINED]==0,"real INPUT arrived before second Java tick");
                select(second);
                require((((StationMultiplayerSession.Listener)host).nativeStatus()&3)!=3,
                    "queued gameplay still prevents a fresh READY barrier");
            } else {
                require(pendingPeerPackets(2)==1,"early FRAME retained in bounded receiver for genuine bootstrap prime");
                require(pending[StationPsxBridge.NEXT_FRAME]==0,"unresumed guest has executed no frame");
            }
            for(int attempt=0;attempt<20;attempt++)tick(second==1?host:guest,second);
            if(first==2)require((((Long)get(host,"reportedStatus"))&3)!=3,"cached transport status never invents drained READY");
            require(protocolStatus(second)[StationPsxBridge.PAUSED]==0,
                "resume deadlock: second owner must consume valid queued gameplay after PLAYING; first="+first+" epoch="+epoch);
            for(int n=0;n<240;n++) {
                advanceOwner(1);
                advanceOwner(2);
                tick(host,1);
                tick(guest,2);
            }
            require(protocolStatus(1)[StationPsxBridge.NEXT_FRAME]>=240,"host keeps advancing after staggered resume");
            require(protocolStatus(2)[StationPsxBridge.NEXT_FRAME]>=240,"guest keeps advancing after staggered resume");
            System.out.println("PASS staggered-resume first="+first+" epoch="+epoch+" hostFrame="+
                protocolStatus(1)[StationPsxBridge.NEXT_FRAME]+" guestFrame="+protocolStatus(2)[StationPsxBridge.NEXT_FRAME]);
        } finally {
            StationPsxBridge.beforeStatus=null;
            StationPsxBridge.resumeHook=null;
            end(host);
            end(guest);
        }
    }
    private static void guards()throws Exception {
        StationPsxBridge.reset();
        Object s=javaSession(1);
        try {
            long serial=serial(s);
            for(int field:new int[]{StationPsxBridge.CORE_READY,StationPsxBridge.ACK_VALID,StationPsxBridge.INITIAL_STATE_SYNCED}) {
                status(1,serial);StationPsxBridge.status[StationPsxBridge.DRAINED]=0;
                StationPsxBridge.status[field]=0;int before=StationPsxBridge.resumeCalls;
                call(s,"update",new Class<?>[]{});
                require(StationPsxBridge.resumeCalls==before,"nonempty queue never bypasses required proof "+field);
            }
            for(int field:new int[]{StationPsxBridge.LOCAL_PAUSED,StationPsxBridge.CLOSED,StationPsxBridge.IN_FRAME,StationPsxBridge.APPLYING_STATE}) {
                status(1,serial);StationPsxBridge.status[StationPsxBridge.DRAINED]=0;
                StationPsxBridge.status[field]=1;int before=StationPsxBridge.resumeCalls;
                call(s,"update",new Class<?>[]{});
                require(StationPsxBridge.resumeCalls==before,"nonempty queue never bypasses native guard "+field);
            }
            for(String field:new String[]{"visible","ownerReady"}) {
                status(1,serial);StationPsxBridge.status[StationPsxBridge.DRAINED]=0;
                set(s,field,false);int before=StationPsxBridge.resumeCalls;call(s,"update",new Class<?>[]{});
                require(StationPsxBridge.resumeCalls==before,"nonempty queue never bypasses Java authority "+field);set(s,field,true);
            }
            status(1,serial);StationPsxBridge.status[StationPsxBridge.DRAINED]=0;
            StationPsxBridge.status[StationPsxBridge.ACK_SERIAL]--;int before=StationPsxBridge.resumeCalls;call(s,"update",new Class<?>[]{});
            require(StationPsxBridge.resumeCalls==before,"stale ACK cannot resume a nonempty queue");
            ((StationMultiplayerSession.Listener)s).nativeControl(1,true,true);serial=serial(s);
            status(1,serial);StationPsxBridge.status[StationPsxBridge.DRAINED]=0;before=StationPsxBridge.resumeCalls;
            call(s,"update",new Class<?>[]{});
            require(StationPsxBridge.resumeCalls==before,"pending traffic never overrides relay pause");
        } finally {end(s);}
    }
    public static void main(String[] args)throws Exception {
        if(args.length!=1)throw new IllegalArgumentException("host-only JNI probe library required");
        System.load(args[0]);
        int failures=0;
        for(long epoch:new long[]{1,3})for(int first:new int[]{1,2})try {race(first,epoch);}
        catch(AssertionError error) {failures++;System.out.println("FAIL first="+first+" epoch="+epoch+" "+error.getMessage());}
        guards();
        if(failures!=0)throw new AssertionError("staggered resume failures="+failures);
        System.out.println("PASS PSX resume race checks="+assertions+" actualJavaAndProtocol=true syntheticOwner=true physicalGameplay=false");
    }
}
