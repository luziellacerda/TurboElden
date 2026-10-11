package org.emulationstation.frontend.netplay;
import org.emulationstation.frontend.station.StationConfig;
import javax.net.ssl.*;
import java.net.URI;
import java.security.*;
import java.security.cert.*;

final class StationRelayTls {
 static URI endpoint()throws Exception {
  URI base=new URI(StationConfig.BASE_URL);
  if(!"https".equals(base.getScheme())||base.getRawUserInfo()!=null||base.getRawQuery()!=null||base.getRawFragment()!=null||!base.getPath().isEmpty()||base.getHost()==null)throw new GeneralSecurityException("Invalid Station authority");
  return new URI("wss",null,base.getHost(),base.getPort(),"/v1/station/online/relay",null,null);
 }
 static URI multiplayerEndpoint()throws Exception {
  URI base=endpoint();return new URI("wss",null,base.getHost(),base.getPort(),"/v1/station/online/multiplayer/relay",null,null);
 }
 static SSLSocketFactory create()throws Exception {
  TrustManagerFactory f=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());f.init((KeyStore)null);
  X509TrustManager system=null;for(TrustManager t:f.getTrustManagers())if(t instanceof X509TrustManager)system=(X509TrustManager)t;
  if(system==null)throw new GeneralSecurityException("System trust unavailable");
  String hex=StationConfig.TLS_SPKI_SHA256;if(!hex.matches("[0-9a-f]{64}"))throw new GeneralSecurityException("Invalid Station pin");
  byte[] pin=new byte[32];for(int i=0;i<32;i++)pin[i]=(byte)Integer.parseInt(hex.substring(i*2,i*2+2),16);
  return pinned(system,pin);
 }
 static SSLSocketFactory pinned(final X509TrustManager trust,final byte[] pin)throws Exception {
  X509TrustManager pinned=new X509TrustManager(){
   public X509Certificate[] getAcceptedIssuers(){return trust.getAcceptedIssuers();}
   public void checkClientTrusted(X509Certificate[] chain,String type)throws CertificateException{trust.checkClientTrusted(chain,type);}
   public void checkServerTrusted(X509Certificate[] chain,String type)throws CertificateException{
    trust.checkServerTrusted(chain,type);
    try{if(chain==null||chain.length==0||!MessageDigest.isEqual(pin,MessageDigest.getInstance("SHA-256").digest(chain[0].getPublicKey().getEncoded())))throw new CertificateException("Station pin mismatch");}
    catch(GeneralSecurityException e){throw new CertificateException("Station TLS rejected",e);}
   }
  };
  SSLContext tls=SSLContext.getInstance("TLS");tls.init(null,new TrustManager[]{pinned},null);return tls.getSocketFactory();
 }
}
