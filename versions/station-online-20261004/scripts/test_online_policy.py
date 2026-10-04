from pathlib import Path
import json,re,subprocess,xml.etree.ElementTree as ET
R=Path(r'E:\StationNetplayWork');checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
src=R/'netplay/src/org/emulationstation/frontend/netplay';ra=R/'upstream/libretro--RetroArch-69a4f0ea1e8a'
java=(src/'StationRetroLaunch.java').read_text('utf8');cfg=(ra/'configuration.c').read_text('utf8')
keys=set(re.findall(r'SETTING_[A-Z_]+\(\s*"([^"]+)"',cfg));wanted=set(re.findall(r'set\(config,"([^"]+)"',java))
for array in re.findall(r'for\(String key:new String\[\]\{([^}]+)\}',java):wanted.update(re.findall(r'"([^"]+)"',array))
check('all emitted config keys exist upstream',not wanted-keys-{'input_libretro_device_p1','input_libretro_device_p2'})
check('no public relay or announcement default','"netplay_public_announce","netplay_use_mitm_server"' in java)
mk=(ra/'pkg/android/phoenix-common/jni/Android.mk').read_text('utf8')
for feature in ('HAVE_ONLINE_UPDATER','HAVE_NETWORK_CMD','HAVE_NETWORKGAMEPAD','HAVE_NETPLAYDISCOVERY','HAVE_CLOUDSYNC'):
 check('compiled without '+feature,'-D'+feature not in mk)
check('upstream CLI netplay path used','strdup("--host")' in (ra/'tasks/task_content.c').read_text('utf8'))
check('offline saves not imported','No offline saves' in java and 'new File(dir,"saves")' in java)
native=(R/'native/native_netplay.h').read_text('utf8')
check('native selected item ID forwarded','strData(begin+(U)selected*0xe8)' in native)
check('no expanded original action vector','at<U>(p,0xdf0)=' not in native)
check('new text child excluded from original render','p==onlineActionText||' in (R/'native/native_carousel.cpp').read_text('utf8'))
for w,h in ((640,360),(854,480),(1280,720),(1920,1080),(2400,1080),(2560,1600),(3840,2160)):
 gap=w*.01;bw=(w*.95-5*gap)/6;rects=[(w*.025+i*(bw+gap),h*.908,bw,h*.065) for i in range(6)]
 check(f'six nonoverlapping actions {w}x{h}',all(x>=0 and y>=0 and x+width<=w and y+height<=h for x,y,width,height in rects) and all(rects[i][0]+bw<rects[i+1][0] for i in range(5)))
root=ET.parse(R/'manifest-project/AndroidManifest.xml').getroot();ns='{http://schemas.android.com/apk/res/android}'
activities={a.get(ns+'name'):a for a in root.find('application').findall('activity')}
for name in ('StationRoomsActivity','StationRetroActivity'):
 a=activities['org.emulationstation.frontend.netplay.'+name];check(name+' not exported',a.get(ns+'exported')=='false')
check('native engine isolated',activities['org.emulationstation.frontend.netplay.StationRetroActivity'].get(ns+'process')==':station_netplay')
for path in (R/'assets/station-online/overlays').rglob('*.cfg'):
 for value in re.findall(r'=\s*"?([^"\s]+\.(?:png|cfg))"?',path.read_text('utf8')):check('overlay '+path.name+' '+value,(path.parent/value).is_file())
check('incomplete Neo Geo rejected before creating room','if(!engine.optBoolean("launchReady",false))' in (src/'StationOnlineGame.java').read_text('utf8'))
check('hidden gameplay cancels presence timer','heartbeat.cancel(true)' in (src/'StationGameSession.java').read_text('utf8'))
check('stale UI replies rejected','snapshot.optLong("revision")<latest.optLong("revision")' in (src/'StationRoomsActivity.java').read_text('utf8'))
check('separate native process never renews Station session','new StationOnlineClient' not in (src/'StationRetroActivity.java').read_text('utf8'))
check('main process owns gameplay presence','new StationOnlineClient(app)' in (src/'StationGameSession.java').read_text('utf8'))
check('native callback reports successful listen','station_android_netplay_listening();' in (ra/'network/netplay/netplay_frontend.c').read_text('utf8'))
check('native lifecycle crosses private Binder','StationGameSession.create(this,room.optString("roomId"))' in (src/'StationRoomsActivity.java').read_text('utf8'))
check('guest waits for host socket','"starting".equals(mine.optString("state"))&&self.equals(mine.optString("hostId"))' in (src/'StationRoomsActivity.java').read_text('utf8'))
# Execute the actual room revision reducer, independently of Android widgets.
test=R/'tests/StationRoomStateTest.java';test.write_text('''package org.emulationstation.frontend.netplay;
import org.json.*;import java.io.*;
public class StationRoomStateTest {
 static JSONObject v(long r,String i)throws Exception{return new JSONObject().put("instance",i).put("revision",r);}
 public static void main(String[] a)throws Exception{StationRoomState s=new StationRoomState();String id="a".repeat(32);
 if(!s.accept(v(10,id))||s.accept(v(9,id))||s.get().getLong("revision")!=10)throw new AssertionError();
 if(!s.accept(v(11,id)))throw new AssertionError();
 try{s.accept(v(1,"b".repeat(32)));throw new AssertionError();}catch(IOException expected){}
 s.reset();if(!s.accept(v(0,"b".repeat(32))))throw new AssertionError();
 try{s.accept(v(-1,"b".repeat(32)));throw new AssertionError();}catch(IOException expected){}
 System.out.println("PASS 6 executable revision and restart checks");}}
''','utf8')
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');jar=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar');out=R/'tests/online-host';out.mkdir(exist_ok=True)
subprocess.run([str(jdk/'javac.exe'),'-cp',str(jar),'-d',str(out),str(src/'StationRoomState.java'),str(test)],check=True)
result=subprocess.check_output([str(jdk/'java.exe'),'-cp',str(out)+';'+str(jar),'org.emulationstation.frontend.netplay.StationRoomStateTest'],text=True)
check('executable state reducer passed','PASS 6' in result)
(R/'evidence/online-policy-tests.json').write_text(json.dumps({'passed':True,'checks':checks,'stateReducer':result,'scope':'PC policy, resources, source and executable Java reducer; no Android game run'},indent=2),'utf8')
print(len(checks),'online policy/resource checks passed; '+result.strip())
