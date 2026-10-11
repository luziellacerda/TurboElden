package org.emulationstation.frontend.offline;

import java.util.Locale;

/** Official audited Android artifacts only; this is never a Station online engine. */
public final class StationSonyOfflinePolicy {
    public static final String PS3_PACKAGE="aenu.aps3e";
    public static final String PS3_ACTIVITY="aenu.aps3e.EmulatorActivity";
    public static final String PS3_ACTION="aenu.intent.action.APS3E";
    public static final String PS3_CERT="7acaebec9e121cf269d2654a40423463456dd3bde8219a4d1359bf38138690ca";
    public static final String PS3_VERSION="2.43";
    public static final long PS3_VERSION_CODE=43;
    public static final String PS4_PACKAGE="com.bachatas4.android.github";
    public static final String PS4_ACTIVITY="com.bachatas4.android.MainActivity";
    public static final String PS4_CERT="a1d6e9aa7b3ff5ae3354f082b133b4d37b156be8aeaf704b0bfaaaee625761ee";
    public static final String PS4_VERSION="0.2.4";
    public static final long PS4_VERSION_CODE=26100114;
    private StationSonyOfflinePolicy() {}
    public static boolean supportedPlatform(String platform){return "ps3".equals(platform)||"ps4".equals(platform);}
    public static String lowerExtension(String displayName){
        if(displayName==null)return "";
        int at=displayName.lastIndexOf('.');
        return at<0?"":displayName.substring(at).toLowerCase(Locale.ROOT);
    }
    public static boolean supportedPs3Image(String displayName){return ".iso".equals(lowerExtension(displayName));}
    public static boolean signerMatches(String actual,String expected){return actual!=null&&actual.equals(expected);}
    public static boolean versionMatches(String actual,String expected){return expected.equals(actual);}
}
