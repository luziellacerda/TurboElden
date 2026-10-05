package org.emulationstation.frontend.netplay;

/** A public room locator, never an authorization token or emulator password. */
final class StationInvitationCode {
    final String instance, roomId, itemId;
    private StationInvitationCode(String instance,String room,String item){this.instance=instance;roomId=room;itemId=item;}
    static String encode(String instance,String room,String item){
        validate(instance,room,item);
        return "TS1:"+instance+":"+room+":"+item;
    }
    static StationInvitationCode parse(String value){
        if(value==null||value.length()>160)throw new IllegalArgumentException("Cole o código completo de uma sala TurboStations.");
        String[] parts=value.trim().split(":",-1);
        if(parts.length!=4||!"TS1".equals(parts[0]))throw new IllegalArgumentException("Este código não é uma sala TurboStations válida.");
        validate(parts[1],parts[2],parts[3]);
        return new StationInvitationCode(parts[1],parts[2],parts[3]);
    }
    private static void validate(String instance,String room,String item){
        if(instance==null||!instance.matches("[0-9a-f]{32}")||room==null||!room.matches("[0-9a-f]{32}")||item==null||!item.matches("[A-Za-z0-9_-]{8,64}"))
            throw new IllegalArgumentException("Código incompleto ou inválido. Copie novamente da sala.");
    }
}
