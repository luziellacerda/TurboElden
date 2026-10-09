package org.emulationstation.frontend.station;

import java.io.*;
import java.net.*;
import javax.net.ssl.*;

/** Retry only transport failures and explicitly temporary HTTP statuses. */
public final class StationDownloadRetry {
 private StationDownloadRetry(){}
 public static boolean transientFailure(Throwable error){
  for(Throwable cause=error;cause!=null;cause=cause.getCause())
   if(cause instanceof SSLHandshakeException||cause instanceof SSLPeerUnverifiedException||cause instanceof java.security.cert.CertificateException)return false;
  if(error instanceof StationApi.Failure){int s=((StationApi.Failure)error).status;return s==408||s==429||s==500||s==502||s==503||s==504;}
  return error instanceof StationApi.Offline||error instanceof StationApi.ArtifactNetworkFailure||error instanceof SocketException
   ||error instanceof SocketTimeoutException||error instanceof UnknownHostException||error instanceof EOFException;
 }
 public static long delayMillis(int failures,long retryAfterMillis){
  long base=Math.min(30000L,2000L<<Math.min(4,Math.max(0,failures-1)));
  return Math.max(base,Math.min(3600000L,Math.max(0L,retryAfterMillis)));
 }
}
