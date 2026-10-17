package org.emulationstation.frontend.netplay;

import java.io.IOException;
import java.io.EOFException;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.json.JSONObject;
import org.emulationstation.frontend.station.StationApi;

/** Deterministic network edge. Production StationApi verifies signed replies. */
final class StationOnlineClient {
    enum First { SUCCESS, TIMEOUT, RESET_AFTER_APPLY, EOF_AFTER_APPLY, OFFLINE,
        EOF_BEFORE_SEND, UNKNOWN_HOST, SERVER_FAILURE,
        GENERIC_IO, CANCELLED_TIMEOUT }
    enum Second { SUCCESS, TIMEOUT, UNCONFIRMED }
    static JSONObject own;
    static First first=First.SUCCESS;
    static Second second=Second.SUCCESS;
    static Exception snapshotFailure;
    static Object snapshotRoomOverride;
    static int snapshots;
    static final List<String> mutations=new ArrayList<>();
    static final List<JSONObject> requests=new ArrayList<>();
    static int failureStatus=500;
    static String failureCode="SERVER_ERROR";
    static void reset(JSONObject room){
        own=room;first=First.SUCCESS;second=Second.SUCCESS;snapshotFailure=null;
        snapshotRoomOverride=null;snapshots=0;failureStatus=500;
        failureCode="SERVER_ERROR";mutations.clear();requests.clear();
    }
    static JSONObject command(String action){
        return new JSONObject().put("action",action).put("requestId",UUID.randomUUID().toString());
    }
    JSONObject multiplayer(JSONObject request,StationApi.Cancellation cancel)throws Exception {
        // Match the pinned production client: these fields become part of the
        // server's full StationMultiplayerCommand fingerprint.
        request.put("clientMaximumPlayers",5).put("page",0).put("roomPageSize",32);
        if("snapshot".equals(request.getString("action"))){
            snapshots++;
            if(snapshotFailure!=null)throw snapshotFailure;
            Object room=snapshotRoomOverride!=null?snapshotRoomOverride:own==null?JSONObject.NULL:own;
            return new JSONObject().put("room",room);
        }
        requests.add(new JSONObject(request.toString()));
        mutations.add(request.toString());
        if(mutations.size()==1){
            if(first==First.TIMEOUT)throw new SocketTimeoutException();
            if(first==First.OFFLINE)throw new StationApi.Offline();
            if(first==First.EOF_BEFORE_SEND)throw new EOFException();
            if(first==First.UNKNOWN_HOST)throw new UnknownHostException();
            if(first==First.GENERIC_IO)throw new IOException("signature rejected");
            if(first==First.SERVER_FAILURE)throw new StationApi.Failure(failureStatus,failureCode);
            if(first==First.CANCELLED_TIMEOUT){cancel.cancel();throw new SocketTimeoutException();}
            if(first==First.RESET_AFTER_APPLY){own=null;throw new SocketException("connection reset");}
            if(first==First.EOF_AFTER_APPLY){own=null;throw new EOFException();}
        }else if(second==Second.TIMEOUT)throw new SocketTimeoutException();
        if(own==null||request.getLong("generation")!=own.getLong("generation"))
            throw new StationApi.Failure(409,"STATION_MULTIPLAYER_GENERATION_MISMATCH");
        if(second==Second.UNCONFIRMED&&mutations.size()>1)return new JSONObject().put("room",own);
        own=null;
        return new JSONObject().put("room",JSONObject.NULL);
    }
}
