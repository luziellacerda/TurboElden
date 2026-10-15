package org.emulationstation.frontend.netplay;

import java.io.IOException;
import java.net.SocketTimeoutException;
import org.json.JSONObject;
import org.emulationstation.frontend.station.StationApi;

public final class StationHumanDepartureR165Test {
    private static int checks;
    private static final String ROOM="0123456789abcdef0123456789abcdef";
    private static final String N64="mupen64plus-ae-33bf7021-n64-v3-bba0ea0d7ff7";
    private static final String PSX="pcsx-rearmed-ff81ed17-player-v3-1b315b86b4a7";
    private interface Action {void run()throws Exception;}
    private static void check(boolean condition,String label){checks++;if(!condition)throw new AssertionError(label);}
    private static void fails(Class<? extends Exception> type,Action action,String label){
        checks++;
        try{action.run();throw new AssertionError(label+": accepted");}
        catch(Exception error){if(!type.isInstance(error))throw new AssertionError(label+": "+error.getClass().getName(),error);}
    }
    private static JSONObject binding(String engine){
        JSONObject value=new JSONObject().put("roomId",ROOM).put("generation",3)
            .put("recoveryProtocol","station-stream.v3").put("engineId",engine);
        for(String key:new String[]{"itemId","coreSha256","runtimeSha256","contentSha256","profileId","profileSha256"})
            value.put(key,key+"-fixture");
        return value;
    }
    private static JSONObject copy(JSONObject value){return new JSONObject(value.toString());}
    private static void leave(JSONObject binding,StationApi.Cancellation cancel)throws Exception{
        StationHumanDeparture.leave(new StationOnlineClient(),binding,cancel);
    }
    private static void leave(JSONObject binding)throws Exception{leave(binding,new StationApi.Cancellation());}
    private static void exactReplay(){
        check(StationOnlineClient.mutations.size()==2,"one bounded replay");
        check(StationOnlineClient.mutations.get(0).equals(StationOnlineClient.mutations.get(1)),
            "full JSON body and requestId unchanged");
        check(StationOnlineClient.requests.get(0).getString("requestId").equals(
            StationOnlineClient.requests.get(1).getString("requestId")),"same idempotency key");
        check(StationOnlineClient.requests.get(0).getInt("clientMaximumPlayers")==5
            &&StationOnlineClient.requests.get(1).getInt("roomPageSize")==32,"production paging fields included");
    }
    public static void main(String[] args)throws Exception{
        JSONObject n64=binding(N64);
        StationOnlineClient.reset(copy(n64));leave(n64);
        check(StationOnlineClient.mutations.size()==1&&StationOnlineClient.snapshots==0&&StationOnlineClient.own==null,
            "normal explicit exit is one request");

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
        leave(n64);exactReplay();check(StationOnlineClient.snapshots==1&&StationOnlineClient.own==null,
            "uncertain send and matching signed own-room snapshot terminate");

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.OFFLINE;
        leave(n64);exactReplay();check(StationOnlineClient.snapshots==1,"offline before send uses one exact replay");

        for(StationOnlineClient.First transport:new StationOnlineClient.First[]{
                StationOnlineClient.First.EOF_BEFORE_SEND,StationOnlineClient.First.UNKNOWN_HOST}){
            StationOnlineClient.reset(copy(n64));StationOnlineClient.first=transport;
            leave(n64);exactReplay();check(StationOnlineClient.snapshots==1,
                "bounded exact replay after "+transport);
        }

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.RESET_AFTER_APPLY;
        leave(n64);check(StationOnlineClient.mutations.size()==1&&StationOnlineClient.snapshots==1,
            "lost response after accepted leave is confirmed absent, not reapplied");

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.EOF_AFTER_APPLY;
        leave(n64);check(StationOnlineClient.mutations.size()==1&&StationOnlineClient.snapshots==1,
            "truncated response after accepted leave is confirmed absent, not reapplied");

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
        StationOnlineClient.second=StationOnlineClient.Second.TIMEOUT;
        fails(SocketTimeoutException.class,()->leave(n64),"second transport error stops");
        exactReplay();check(StationOnlineClient.snapshots==1,"no third request or polling worker");

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
        StationOnlineClient.second=StationOnlineClient.Second.UNCONFIRMED;
        fails(IOException.class,()->leave(n64),"same room after replay remains unconfirmed");exactReplay();

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
        StationOnlineClient.own.put("generation",4);
        fails(IOException.class,()->leave(n64),"uncertain send cannot move to a newer generation");
        check(StationOnlineClient.mutations.size()==1&&StationOnlineClient.snapshots==1,"generation change no replay");

        for(String key:new String[]{"recoveryProtocol","itemId","engineId","coreSha256",
                "runtimeSha256","contentSha256","profileId","profileSha256"}){
            StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
            StationOnlineClient.own.put(key,"different");
            fails(IOException.class,()->leave(n64),"identity change "+key);
            check(StationOnlineClient.mutations.size()==1,"identity change never leaves "+key);
        }

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
        StationOnlineClient.own.put("roomId","fedcba9876543210fedcba9876543210");
        leave(n64);check(StationOnlineClient.mutations.size()==1,"different own room is never left");

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
        StationOnlineClient.snapshotRoomOverride="malformed";
        fails(IOException.class,()->leave(n64),"invalid snapshot shape");
        check(StationOnlineClient.mutations.size()==1,"malformed snapshot no replay");

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
        StationOnlineClient.snapshotFailure=new StationApi.Failure(403,"STATION_LICENSE_DENIED");
        fails(StationApi.Failure.class,()->leave(n64),"snapshot authority failure");
        check(StationOnlineClient.mutations.size()==1,"authority failure no replay");

        for(int status:new int[]{403,409,500}){
            StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.SERVER_FAILURE;
            StationOnlineClient.failureStatus=status;StationOnlineClient.failureCode="OTHER_FAILURE";
            fails(StationApi.Failure.class,()->leave(n64),"server failure "+status);
            check(StationOnlineClient.mutations.size()==1&&StationOnlineClient.snapshots==0,
                "server rejection never interpreted as transport uncertainty "+status);
        }

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.GENERIC_IO;
        fails(IOException.class,()->leave(n64),"signature or protocol error");
        check(StationOnlineClient.mutations.size()==1&&StationOnlineClient.snapshots==0,
            "generic IOException is not a network retry signal");

        StationOnlineClient.reset(copy(n64));StationOnlineClient.first=StationOnlineClient.First.CANCELLED_TIMEOUT;
        fails(SocketTimeoutException.class,()->leave(n64),"cancelled transport");
        check(StationOnlineClient.mutations.size()==1&&StationOnlineClient.snapshots==0,"cancellation blocks replay");

        JSONObject psx=binding(PSX);StationOnlineClient.reset(copy(psx));
        StationOnlineClient.first=StationOnlineClient.First.TIMEOUT;
        fails(SocketTimeoutException.class,()->leave(psx),"other v3 engine unchanged");
        check(StationOnlineClient.mutations.size()==1&&StationOnlineClient.snapshots==0,
            "PSX has original no-retry behavior");

        StationOnlineClient.reset(copy(n64).put("generation",4));leave(n64);
        check(StationOnlineClient.mutations.size()==2&&StationOnlineClient.snapshots==1&&StationOnlineClient.own==null,
            "definite stale-generation rejection retains R135 recovery");
        check(!StationOnlineClient.requests.get(0).getString("requestId").equals(
            StationOnlineClient.requests.get(1).getString("requestId")),
            "definite rejection alone gets a new requestId");

        System.out.println("R165 human departure passed: "+checks+
            " assertions; exact body/receipt, bounded replay and adversarial isolation");
    }
}
