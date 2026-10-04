from pathlib import Path
import shutil,json,hashlib
R=Path(r'E:\StationNetplayWork');P=Path(__file__).resolve().parent/'station-online-proposed'
src=R/'netplay/src/org/emulationstation/frontend/netplay'
for p in P.glob('*.java'):shutil.copy2(p,src/p.name)
def patch(p,old,new):
 t=p.read_text('utf-8');assert t.count(old)==1,(p,t.count(old));p.write_text(t.replace(old,new),'utf-8',newline='\n')
p=src/'StationNetplayActivity.java'
patch(p,'private static boolean start(Activity activity){','private static boolean start(Activity activity,String itemId){')
patch(p,'new Intent(activity,StationNetplayActivity.class)','new Intent(activity,itemId==null?StationNetplayActivity.class:StationRoomsActivity.class).putExtra("station.itemId",itemId)')
patch(p,'public static boolean launch(Activity activity){','public static boolean launch(Activity activity){return launchGame(activity,null);}\n    public static boolean launchGame(Activity activity,String itemId){')
t=p.read_text('utf-8').replace('start(activity)','start(activity,itemId)')
t=t.replace('ui.text("Mega Drive e Super Nintendo • jogo local",17,0xff7ef2a0);','ui.action("Salas TurboStations • jogadores e convites",v->startActivity(new Intent(this,StationRoomsActivity.class)),true);\n        ui.text("Mega Drive e Super Nintendo",17,0xff7ef2a0);')
t=t.replace('Os motores atuais dessas plataformas ainda não oferecem partidas pela internet. Seus jogos, controles e saves continuam disponíveis no modo local.','Abra um jogo e toque em Jogar online para conferir a disponibilidade do motor nas salas. A partida é direta entre aparelhos. Seus controles e saves locais são preservados.')
t=t.replace('Em Configurações → Rede, ative WLAN. Pela internet, os participantes escolhem o mesmo servidor relay; na mesma rede Wi-Fi, use o servidor ad hoc. A sala é aberta dentro do jogo.','Em Configurações → Rede, ative WLAN e use o servidor ad hoc no aparelho anfitrião. A sala é aberta dentro do jogo. Não há relay público configurado pela Station.')
p.write_text(t,'utf-8',newline='\n')
patch(R/'netplay/build_netplay.py',"'-cp',ANDROID,'-d',classes", "'-cp',str(ANDROID)+';'+str(ROOT.parent/'station/build/station-client.jar'),'-d',classes")
patch(R/'netplay/build_netplay.py',"'--lib',ANDROID,'--output',dex,jar", "'--lib',ANDROID,'--classpath',ROOT.parent/'station/build/station-client.jar','--output',dex,jar")
manifest=R/'manifest-project/AndroidManifest.xml'
patch(manifest,'    </application>', '''        <activity android:name="org.emulationstation.frontend.netplay.StationRoomsActivity" android:exported="false"
            android:enableOnBackInvokedCallback="false" android:screenOrientation="userLandscape"
            android:configChanges="keyboardHidden|orientation|screenSize" android:theme="@android:style/Theme.Material.NoActionBar"/>
        <activity android:name="org.emulationstation.frontend.netplay.StationRetroActivity" android:exported="false" android:process=":station_netplay"
            android:enableOnBackInvokedCallback="false" android:screenOrientation="userLandscape"
            android:configChanges="keyboardHidden|orientation|screenSize" android:theme="@android:style/Theme.Material.NoActionBar.Fullscreen">
            <meta-data android:name="android.app.lib_name" android:value="station_retroarch"/>
        </activity>
    </application>''')
n=R/'native/native_carousel.cpp'
patch(n,'#include "native_formation.h"','''static void*onlineActionText;
static void drawOnlineAction(void*,void*);
static bool touchOnlineAction(void*,const void*);
#include "native_formation.h"''')
patch(n,'if(p==settingsBackText||p==settingsNetplayText||isStoreUiLabel(p))return;','if(p==onlineActionText||p==settingsBackText||p==settingsNetplayText||isStoreUiLabel(p))return;')
patch(n,'layoutSkin(p);ButtonScope scope(p);fn<void(*)(void*,void*)>(0x22fb88)(p,matrix);','layoutSkin(p);ButtonScope scope(p);fn<void(*)(void*,void*)>(0x22fb88)(p,matrix);drawOnlineAction(p,matrix);')
patch(n,'gui=p;if(formationTouch(p,event))return true;','gui=p;if(touchOnlineAction(p,event)||formationTouch(p,event))return true;')
patch(R/'native/native_skin.h','float gap=w*.012f,bw=(w*.95f-4*gap)/5;','float gap=w*.010f,bw=(w*.95f-(systemsMode?4:5)*gap)/(systemsMode?5:6);')
patch(R/'native/native_skin.h','float x=w*.025f+i*(bw+gap),width=bw;','float x=w*.025f+(systemsMode?i:(i==0?0:i+1))*(bw+gap),width=bw;')
(R/'native/native_netplay.h').write_text(r'''// Direct JNI dispatch from native controls; no synthetic input or public relay.
static jclass stationNetplayBridge;static jmethodID stationNetplayLaunch,stationNetplayLaunchGame;
static bool dispatchStationNetplay(const char* itemId){
 JNIEnv*env=videoEnv();if(!env)return false;jobject activity=videoActivity();if(!activity)return false;
 if(!stationNetplayBridge){
  jclass ac=env->GetObjectClass(activity);jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.netplay.StationNetplayActivity");jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  if(!env->ExceptionCheck()&&local){stationNetplayBridge=(jclass)env->NewGlobalRef(local);stationNetplayLaunch=env->GetStaticMethodID(stationNetplayBridge,"launch","(Landroid/app/Activity;)Z");stationNetplayLaunchGame=env->GetStaticMethodID(stationNetplayBridge,"launchGame","(Landroid/app/Activity;Ljava/lang/String;)Z");}
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!env->ExceptionCheck()&&stationNetplayBridge){
  if(itemId&&stationNetplayLaunchGame){jstring id=env->NewStringUTF(itemId);ok=env->CallStaticBooleanMethod(stationNetplayBridge,stationNetplayLaunchGame,activity,id);env->DeleteLocalRef(id);}
  else if(stationNetplayLaunch)ok=env->CallStaticBooleanMethod(stationNetplayBridge,stationNetplayLaunch,activity);
 }
 if(env->ExceptionCheck()){env->ExceptionClear();log("NETPLAY menu unavailable");ok=false;}env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log("NETPLAY direct menu dispatched");}return ok;
}
static bool openStationNetplay(){return dispatchStationNetplay(nullptr);}
static void drawOnlineAction(void*p,void*matrix){
 if(systemsMode||modal(p)||at<int>(p,0x370)<2)return;
 static void*owner;
 if(owner!=p){owner=p;onlineActionText=createInfoText(p,0xF3FFF6ff);setLongText(onlineActionText,"JOGAR ONLINE");}
 float w=at<float>(p,0x54),h=at<float>(p,0x58),gap=w*.010f,bw=(w*.95f-5*gap)/6,x=w*.025f+bw+gap;
 fn<void(*)(const void*)>(0x2e5640)(matrix);rounded(x,h*.908f,bw,h*.065f,0x235035ff);
 place(onlineActionText,x,h*.908f,bw,h*.065f,.60f,1);
 if(onlineActionText)fn<void(*)(void*,void*)>(0x2d2dc4)(onlineActionText,matrix);
}
static bool touchOnlineAction(void*p,const void*event){
 static bool pressed;static U finger;
 if(systemsMode||modal(p)||at<int>(p,0x370)<2){pressed=false;return false;}
 float w=at<float>(p,0x54),h=at<float>(p,0x58),gap=w*.010f,bw=(w*.95f-5*gap)/6,x0=w*.025f+bw+gap;
 float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 bool inside=x>=x0&&x<=x0+bw&&y>=h*.908f&&y<=h*.973f;
 if(type==0){pressed=inside;finger=id;return pressed;}
 if(!pressed||id!=finger)return false;
 if(type==1&&!inside){pressed=false;return true;}
 if(type==2){pressed=false;if(inside){int selected=fn<int(*)(void*)>(0x21b0c8)(p);if(selected>=0){void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);if(begin&&selected<(end-begin)/0xe8)dispatchStationNetplay(strData(begin+(U)selected*0xe8));}}}
 return true;
}
''','utf-8',newline='\n')
print('Integrated authenticated rooms sources, native online action and isolated runtime Activity')
