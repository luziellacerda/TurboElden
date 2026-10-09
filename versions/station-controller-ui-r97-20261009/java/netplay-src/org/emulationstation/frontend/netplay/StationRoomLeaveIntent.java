package org.emulationstation.frontend.netplay;

import java.util.UUID;

/** A human's exact departure target. Network/lifecycle events never create this intent. */
final class StationRoomLeaveIntent {
    static final String KEY="leaveMultiplayerIntent";
    enum Decision { LEAVE, ACKNOWLEDGED_ABSENT, HOLD_DIFFERENT_GENERATION }
    final String encoded,roomId,protocol,requestId;final long generation;
    private StationRoomLeaveIntent(String room,long generation,String protocol,String request){
        this.roomId=room;this.generation=generation;this.protocol=protocol;this.requestId=request;
        encoded=protocol+"|"+room+"|"+generation+"|"+request;
    }
    static StationRoomLeaveIntent human(String room,long generation,String protocol){
        StationRoomLeaveIntent value=parse(protocol+"|"+room+"|"+generation+"|"+UUID.randomUUID());
        if(value==null)throw new IllegalArgumentException("Invalid room departure");return value;
    }
    static StationRoomLeaveIntent parse(String text){
        if(text==null||text.length()>160)return null;String[] parts=text.split("\\|",-1);
        if(parts.length!=4||!"station-stream.v3".equals(parts[0])||!parts[1].matches("[0-9a-f]{32}")
                ||!parts[2].matches("[1-9][0-9]{0,18}")||!parts[3].matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))return null;
        try{long generation=Long.parseLong(parts[2]);return new StationRoomLeaveIntent(parts[1],generation,parts[0],parts[3]);}catch(NumberFormatException invalid){return null;}
    }
    /** Call only with own-room fields from an authenticated, verified snapshot. */
    Decision decide(String currentRoom,long currentGeneration,String currentProtocol){
        if(currentRoom==null||currentRoom.isEmpty()||!roomId.equals(currentRoom))return Decision.ACKNOWLEDGED_ABSENT;
        return generation==currentGeneration&&protocol.equals(currentProtocol)?Decision.LEAVE:Decision.HOLD_DIFFERENT_GENERATION;
    }
    /** A failed request, or an older completion racing a newer human intent, cannot clear it. */
    String afterResult(String currentlyStored,boolean verifiedSnapshot,String currentRoom,long currentGeneration,String currentProtocol){
        if(!encoded.equals(currentlyStored)||!verifiedSnapshot)return currentlyStored;
        return decide(currentRoom,currentGeneration,currentProtocol)==Decision.ACKNOWLEDGED_ABSENT?"":currentlyStored;
    }
}
