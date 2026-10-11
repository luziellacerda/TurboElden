import java.util.Locale;
import org.emulationstation.frontend.offline.StationSonyOfflinePolicy;

public final class OfflinePolicyProbe {
    private static int checks;
    private static void check(boolean value,String label){checks++;if(!value)throw new AssertionError(label);}
    public static void main(String[] args){
        check(StationSonyOfflinePolicy.supportedPlatform("ps3"),"ps3");
        check(StationSonyOfflinePolicy.supportedPlatform("ps4"),"ps4");
        for(String value:new String[]{null,"", "PS3", "PS4", "psx", "snes", "gamecube", "wii", "switch", "ps3 online", "ps5"})
            check(!StationSonyOfflinePolicy.supportedPlatform(value),"reject platform "+value);
        for(String value:new String[]{"Game.iso","Game.ISO","Game.IsO","folder/game.iso"})
            check(StationSonyOfflinePolicy.supportedPs3Image(value),"valid ISO "+value);
        for(String value:new String[]{null,"", "game", "game.pkg", "game.iso.zip", "game.elf", "game.bin", "game.iso.tmp"})
            check(!StationSonyOfflinePolicy.supportedPs3Image(value),"reject ISO "+value);
        Locale old=Locale.getDefault();
        try{Locale.setDefault(new Locale("tr","TR"));check(StationSonyOfflinePolicy.supportedPs3Image("GAME.ISO"),"locale-independent ISO");}
        finally{Locale.setDefault(old);}
        check(".pkg".equals(StationSonyOfflinePolicy.lowerExtension("Game.PKG")),"PKG extension");
        check(StationSonyOfflinePolicy.signerMatches(StationSonyOfflinePolicy.PS3_CERT,StationSonyOfflinePolicy.PS3_CERT),"PS3 signer");
        check(StationSonyOfflinePolicy.signerMatches(StationSonyOfflinePolicy.PS4_CERT,StationSonyOfflinePolicy.PS4_CERT),"PS4 signer");
        check(!StationSonyOfflinePolicy.signerMatches(null,StationSonyOfflinePolicy.PS3_CERT),"null signer");
        check(!StationSonyOfflinePolicy.signerMatches(StationSonyOfflinePolicy.PS3_CERT,StationSonyOfflinePolicy.PS4_CERT),"wrong signer");
        check(StationSonyOfflinePolicy.versionMatches("2.43",StationSonyOfflinePolicy.PS3_VERSION),"PS3 version");
        check(StationSonyOfflinePolicy.versionMatches("0.2.4",StationSonyOfflinePolicy.PS4_VERSION),"PS4 version");
        check(!StationSonyOfflinePolicy.versionMatches("2.44",StationSonyOfflinePolicy.PS3_VERSION),"future version");
        check(!StationSonyOfflinePolicy.versionMatches(null,StationSonyOfflinePolicy.PS4_VERSION),"null version");
        check(StationSonyOfflinePolicy.PS3_VERSION_CODE==43,"PS3 versionCode");
        check(StationSonyOfflinePolicy.PS4_VERSION_CODE==26100114,"PS4 versionCode");
        System.out.println("passed="+checks);
    }
}
