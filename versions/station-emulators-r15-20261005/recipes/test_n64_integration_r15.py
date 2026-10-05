import os
from pathlib import Path
import zipfile,struct,hashlib,re,json,subprocess,xml.etree.ElementTree as ET
W=Path(os.environ['STATION_N64_WORK']);M=W/'merged';D=W/'donor';T=W/'tests';T.mkdir(exist_ok=True)
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Visual-R14-20261005.apk')
checks=[]
def check(name,result):
 checks.append({'name':name,'passed':bool(result)});assert result,name
def dex_classes(data):
 ns,so=struct.unpack_from('<II',data,56);nt,to=struct.unpack_from('<II',data,64);nc,co=struct.unpack_from('<II',data,96)
 strings=[]
 for i in range(ns):
  off=struct.unpack_from('<I',data,so+4*i)[0]
  while data[off]&128:off+=1
  off+=1;strings.append(data[off:data.index(0,off)].decode('utf8','replace'))
 types=[strings[struct.unpack_from('<I',data,to+4*i)[0]] for i in range(nt)]
 return {types[struct.unpack_from('<I',data,co+32*i)[0]] for i in range(nc)}
with zipfile.ZipFile(BASE) as b,zipfile.ZipFile(W/'n64-resources-dex.apk') as n:
 base_classes=set()
 for name in b.namelist():
  if re.fullmatch(r'classes\d*\.dex',name):base_classes.update(dex_classes(b.read(name)))
 new_classes=set()
 for name in ('classes36.dex','classes37.dex'):
  data=n.read(name);c=dex_classes(data);check(name+' no base class collisions',not c&base_classes);check(name+' no donor collisions',not c&new_classes);new_classes|=c
  check(name+' valid checksum',hashlib.sha1(data[32:]).digest()==data[12:32])
 bridge=dex_classes((W/'classes38.dex').read_bytes());check('bridge unique',not bridge&(base_classes|new_classes));new_classes|=bridge
 # Native filename conflicts are intentional only for renamed C++ runtime.
 for p in (W/'native-libs').glob('*.so'):check('unique native '+p.name,'lib/arm64-v8a/'+p.name not in b.namelist())
 check('runtime init exact base dex',hashlib.sha256(b.read('classes.dex')).hexdigest()==json.loads((W/'application/receipt.json').read_text())['baseDexSHA256'])
 check('UI and controls included',all('L'+s+';' in new_classes for s in ('paulscode/android/mupen64plusae/GalleryActivity','paulscode/android/mupen64plusae/game/GameActivity','paulscode/android/mupen64plusae/persistent/TouchscreenPrefsActivity','paulscode/android/mupen64plusae/persistent/DisplayPrefsActivity')))
check('upstream ZIP verified',hashlib.sha256((W/'mupen64plus-ae-master.zip').read_bytes()).hexdigest()=='76a53ca6edbb076e677368284355063dcca48fb08736d7db9584475d075cfaa1')
A='{http://schemas.android.com/apk/res/android}';manifest=ET.parse(M/'AndroidManifest.xml').getroot();app=manifest.find('application')
for e in app:
 name=e.get(A+'name','')
 if e.tag in ('activity','service','provider') and e.get(A+'process','').startswith(':n64'):
  check('manifest class '+name,'L'+name.replace('.','/')+';' in new_classes)
  check('private component '+name,e.get(A+'exported')=='false')
for p in M.glob('smali_classes3[67]/**/*.smali'):
 s=p.read_text('utf8')
 check_calls=re.findall(r'invoke-virtual(?:/range)? .*Landroid/content/Context;->getSharedPreferences\(Ljava/lang/String;I\)',s)
 assert not check_calls,p
check('all donor SharedPreferences isolated',True)
public={(x.get('type'),x.get('name')):x.get('id') for x in ET.parse(M/'res/values/public.xml').getroot()}
for e in ET.parse(W/'base/res/values/public.xml').getroot():
 if e.tag=='public':
  assert public[(e.get('type'),e.get('name'))]==e.get('id'),e.attrib
check('all existing public resource IDs unchanged',True)
s=(M/'smali_classes36/paulscode/android/mupen64plusae/GalleryActivity.smali').read_text('utf8');a=s.index('.method private launchGameOnCreation(');b=s.index('.end method',a)
check('does not close result recipient on launch','->finishAffinity()V' not in s[a:b])
check('upstream exit callback remains','->finishAffinity()V' in s[:a])
s=(M/'smali_classes36/paulscode/android/mupen64plusae/SplashActivity.smali').read_text('utf8')
check('no clearing logs','->clearLogCat()V' not in s)
check('no startup TV scanning','->scheduleSyncingProgramsForChannel' not in s)
check('no file URI boundary','Uri.fromFile' not in Path('N64EntryActivity.java').read_text('utf8'))
# Execute exact native routing code with a mock Java boundary, not a rewritten routing table.
h=Path('native_n64.h').read_text('utf8');a=h.index('static jclass n64Bridge');b=h.index('static UiString n64RunHook');h=h[:a]+h[b:]
cpp=r'''#include <string>
#include <cstring>
#include <cassert>
#include <cstdio>
struct UiString{std::string value;}; static int calls=0,delegated=0;static bool setting=false;static std::string game;
static const char*strData(const void*p){return ((const std::string*)p)->c_str();}
static void strAssign(void*p,const char*s){((UiString*)p)->value=s;}
static bool presentationKeyEqual(const char*a,const char*b){return strcmp(a,b)==0;}
static bool openN64(const char*p,bool s){calls++;game=p;setting=s;return true;}
static void requestSettingsClose(void*){delegated++;}
static UiString megaRunHook(const void*,const void*){delegated++;return {};}
static bool megaDefinitionsHook(const void*,void*,void*){delegated++;return false;}
static void megaSettingsHook(void*,const void*){delegated++;}
static UiString megaCommandHook(const void*){delegated++;return {};}
static bool megaFreshHook(const void*){delegated++;return true;}
static bool megaBundledHook(const void*){delegated++;return false;}
static bool megaInstalledHook(void*,const void*){delegated++;return false;}
static bool megaAssetsHook(void*,const void*){delegated++;return false;}
static bool megaPackHook(const void*,void*,void*){delegated++;return true;}
'''+h+r'''
int main(){int cases=0;
 for(const char* name:{"Nintendo 64","Nintendo 64 - BR","n64","n64br"}){
  std::string key=name;assert(n64CommandHook(&key).value=="libretro: core=mupen64plus_ae_android.so");cases++;
 }
 for(const char*name:{"Nintendo 64","Nintendo 64 - BR","n64","n64br","mupen64plus_ae_android.so","mupen64plus_next_gles3_libretro_android.so"}){
  std::string key=name,rom="/storage/emulated/0/EmulationStation/roms/.station-v2/n64/content/game.z64";UiString title,u,p;
  assert(n64Core(&key));n64RunHook(&key,&rom);assert(!setting&&game==rom);n64SettingsHook(nullptr,&key);assert(setting&&game.empty());
  assert(!n64FreshHook(&key));assert(n64BundledHook(&key));assert(n64InstalledHook(nullptr,&key));assert(n64AssetsHook(nullptr,&key));
  assert(!n64DefinitionsHook(&key,&title,nullptr));assert(title.value.find("Mupen64Plus AE")!=std::string::npos);assert(!n64PackHook(&key,&u,&p));cases+=10;
 }
 for(const char*name:{"Super Nintendo","MegaDrive","MAME","Neo Geo","Nintendo DS","GameCube","PSP","Flycast",""}){
  std::string key=name;UiString t,u,p;int start=delegated;assert(!n64Core(&key));n64CommandHook(&key);n64RunHook(&key,&key);n64SettingsHook(nullptr,&key);n64DefinitionsHook(&key,&t,nullptr);n64FreshHook(&key);n64BundledHook(&key);n64InstalledHook(nullptr,&key);n64AssetsHook(nullptr,&key);n64PackHook(&key,&u,&p);assert(delegated-start==9);cases+=10;
 }
 printf("PASS %d N64 routing checks: official settings/controls launch; all unrelated platforms delegated\n",cases);
}'''
(T/'routes.cpp').write_text(cpp,'utf8')
for args in ([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17',T/'routes.cpp','-o',T/'routes.exe'],[T/'routes.exe']):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr
 if p.stdout:print(p.stdout.strip());(T/'routes.log').write_text(p.stdout,'utf8')
(T/'integration.json').write_text(json.dumps({'passed':True,'checks':checks,'newClassCount':len(new_classes),'androidGameplayVerified':False},indent=2),'utf8')
print('PASS',len(checks),'integration checks; no claim of Android gameplay')
