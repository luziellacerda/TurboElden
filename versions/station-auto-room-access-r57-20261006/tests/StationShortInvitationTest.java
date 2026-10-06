package org.emulationstation.frontend.netplay;

public final class StationShortInvitationTest {
    static int checks;
    static void check(boolean condition,String message){checks++;if(!condition)throw new AssertionError(message);}
    static void reject(String value){try{StationInvitationCode.parse(value);throw new AssertionError("Invalid invitation accepted");}catch(IllegalArgumentException expected){checks++;}}
    public static void main(String[] args){
        String code="7KPM4XRT";
        for(String value:new String[]{code,"7KPM-4XRT","7kpm-4xrt","  7KPM-4XRT  ","7kpm4xrt"}){
            StationInvitationCode parsed=StationInvitationCode.parse(value);
            check(parsed.shortCode.equals(code),"accepted human input");
            check(parsed.roomId.isEmpty()&&parsed.itemId.isEmpty()&&parsed.instance.isEmpty(),"short code requires authenticated server lookup");
        }
        check(StationInvitationCode.display(code).equals("7KPM-4XRT"),"readable 4+4 grouping");
        for(String value:new String[]{"", "ABCD", "IIIIIIII", "OOOOOOOO", "01234567", "7KPM--4XRT", "7KPM 4XRT", "7KPM-4XR!", "7KPM\n4XRT", "7KPM\u00004XRT", "https://evil.test/7KPM4XRT"})reject(value);
        String instance="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",room="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
        StationInvitationCode old=StationInvitationCode.parse(StationInvitationCode.encode(instance,room,"station_item"));
        check(old.shortCode.isEmpty()&&old.instance.equals(instance)&&old.roomId.equals(room)&&old.itemId.equals("station_item"),"legacy TS1 unchanged");
        System.out.println("PASS "+checks+" checks: short invitations, manual input, authenticated resolution and TS1 compatibility");
    }
}
