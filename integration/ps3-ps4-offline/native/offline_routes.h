// Offline entry only. The bridge owns external URI grants and failure handling.
// The normal route of every other system falls through unchanged.
static bool stationOfflineSonyCommand(const char* key,UiString* out){
 const bool ps3=presentationKeyEqual(key,"ps3")||presentationKeyEqual(key,"Playstation 3")||
  presentationKeyEqual(key,"PlayStation3")||presentationKeyEqual(key,"playstation-3");
 const bool ps4=presentationKeyEqual(key,"ps4")||presentationKeyEqual(key,"Playstation 4")||
  presentationKeyEqual(key,"PlayStation4")||presentationKeyEqual(key,"playstation-4");
 if(!ps3&&!ps4)return false;
 strAssign(out,ps3?
  "android: package=org.turboramastation.frontend class=org.emulationstation.frontend.offline.StationSonyOfflineActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1 e:station.platform=ps3":
  "android: package=org.turboramastation.frontend class=org.emulationstation.frontend.offline.StationSonyOfflineActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1 e:station.platform=ps4");
 return true;
}
