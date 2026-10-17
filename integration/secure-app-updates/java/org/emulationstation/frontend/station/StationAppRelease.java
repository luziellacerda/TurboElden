package org.emulationstation.frontend.station;

import java.io.IOException;
import org.json.JSONObject;

/** Parsed only after StationApi has verified the signed, request-bound reply. */
public final class StationAppRelease {
    public static final String PACKAGE="org.turboramastation.frontend";
    public static final long MAXIMUM_BYTES=8L*1024*1024*1024;
    public final String id,sha256,certificateSha256,versionName,notes,abi;
    public final long versionCode,sizeBytes;
    public final int minimumSdk;
    private StationAppRelease(JSONObject value)throws Exception {
        id=text(value,"releaseId");sha256=text(value,"sha256");
        certificateSha256=text(value,"certificateSha256");versionName=text(value,"versionName");
        notes=text(value,"notes");abi=text(value,"abi");
        versionCode=StationCatalog.integer(value,"versionCode");
        sizeBytes=StationCatalog.integer(value,"sizeBytes");
        long sdk=StationCatalog.integer(value,"minimumSdk");
        if(StationCatalog.integer(value,"schemaVersion")!=1||!PACKAGE.equals(text(value,"packageName"))||
            !hex(sha256)||!sha256.equals(id)||!hex(certificateSha256)||
            versionCode<1||versionCode>2100000000L||sizeBytes<1024||sizeBytes>MAXIMUM_BYTES||
            sdk<28||sdk>1000||!"arm64-v8a".equals(abi)||versionName.isEmpty()||versionName.length()>100||
            notes.length()>2000||controls(versionName,false)||controls(notes,true))throw new IOException("UPDATE_METADATA");
        minimumSdk=(int)sdk;
    }
    public static StationAppRelease parse(JSONObject value)throws Exception{return new StationAppRelease(value);}
    public boolean eligible(long installedVersion,int sdk,String installedCertificate,boolean arm64){
        return versionCode>installedVersion&&minimumSdk<=sdk&&arm64&&certificateSha256.equals(installedCertificate);
    }
    public boolean same(StationAppRelease other){
        return other!=null&&id.equals(other.id)&&versionCode==other.versionCode&&sizeBytes==other.sizeBytes&&
            certificateSha256.equals(other.certificateSha256)&&minimumSdk==other.minimumSdk&&abi.equals(other.abi);
    }
    static boolean hex(String value){return value!=null&&value.matches("[0-9a-f]{64}");}
    private static String text(JSONObject value,String key)throws Exception{
        Object result=value.get(key);if(!(result instanceof String))throw new IOException("UPDATE_METADATA");return(String)result;
    }
    private static boolean controls(String value,boolean lines){
        for(int i=0;i<value.length();i++){char c=value.charAt(i);if(Character.isISOControl(c)&&!(lines&&(c=='\r'||c=='\n'||c=='\t')))return true;}
        return false;
    }
}
