from pathlib import Path
import json,re,shutil,subprocess,os,xml.etree.ElementTree as ET,zipfile,hashlib,urllib.request
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-media-refresh/psvita';M=R/'merged';D=R/'donor-decoded';local=Path(__file__).parent
os.environ['TEMP']=os.environ['TMP']=str(R.parent/'tmp')
cm=json.loads((R/'class-map.json').read_text());java=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');bt=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
for name in ['VitaBootstrap.java','VitaEntryActivity.java','vita_archive_bridge.c']:shutil.copy2(local/name,R/name)
registrar=['#include <jni.h>','#include <dlfcn.h>','#include <android/log.h>',
'''JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_VitaBootstrap_bindSdl(JNIEnv *env,jclass ignored){
 (void)ignored;static int ready;if(ready)return JNI_TRUE;
 void *lib=dlopen("libVita3K.so",RTLD_NOW|RTLD_LOCAL);if(!lib)return JNI_FALSE;''']
def jni_name(s):
    return ''.join('_1' if c=='_' else '_2' if c==';' else '_3' if c=='[' else '_' if c=='/' else '_00024' if c=='$' else c for c in s)
native_count=0
exports=subprocess.check_output([r'C:\Program Files\LLVM\bin\llvm-nm.exe','-D','--defined-only',str(D/'lib/arm64-v8a/libVita3K.so')],text=True)
exports={line.split()[-1] for line in exports.splitlines() if line.strip()}
for f in sorted((D/'smali/org/libsdl').rglob('*.smali')):
    old=f.relative_to(D/'smali').as_posix()[:-6];methods=[]
    for name,signature in re.findall(r'^\.method[^\n]*\bnative\s+([^\s(]+)(\([^\n]+)',f.read_text(),re.M):
        symbol='Java_'+jni_name(old)+'_'+jni_name(name)
        if symbol not in exports:symbol+='__'+jni_name(signature[1:signature.index(')')])
        assert symbol in exports,(old,name,symbol)
        methods.append((name,signature,symbol));native_count+=1
    if not methods:continue
    registrar.append('{ jclass c=(*env)->FindClass(env,"'+cm[old]+'");if(!c)return JNI_FALSE;')
    registrar.append('JNINativeMethod methods[]={'+','.join('{"'+n+'","'+sig+'",NULL}' for n,sig,sym in methods)+'};')
    for i,(n,sig,sym) in enumerate(methods):registrar.append(f'methods[{i}].fnPtr=dlsym(lib,"{sym}");if(!methods[{i}].fnPtr){{(*env)->DeleteLocalRef(env,c);return JNI_FALSE;}}')
    registrar.append('if((*env)->RegisterNatives(env,c,methods,sizeof(methods)/sizeof(methods[0]))!=JNI_OK){(*env)->DeleteLocalRef(env,c);return JNI_FALSE;}(*env)->DeleteLocalRef(env,c);}')
registrar+=['ready=1;__android_log_print(4,"TurboVita","Relocated SDL native methods registered");return JNI_TRUE;}']
(R/'vita_sdl_registry.c').write_text('\n'.join(registrar),encoding='utf-8')
arc=json.loads((R/'archive/build-result.json').read_text());ndk=Path(r'E:\TurboEdenEngine\android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64')
native=R/'libturbo_vita_jni.so'
subprocess.run([str(ndk/'bin/clang.exe'),'--target=aarch64-linux-android26','--sysroot='+str(ndk/'sysroot'),'-std=c11','-D_GNU_SOURCE','-O2','-fPIC','-shared','-Wl,-z,max-page-size=16384','-Wl,-z,defs','-Wl,-s','-Wl,-soname,libturbo_vita_jni.so','-I'+str(Path(arc['source_dir'])/'libarchive'),str(R/'vita_sdl_registry.c'),str(R/'vita_archive_bridge.c'),arc['built'],'-lz','-ldl','-llog','-lm','-o',str(native)],check=True)
shutil.copy2(native,M/'lib/arm64-v8a'/native.name)
A='{http://schemas.android.com/apk/res/android}';path=M/'AndroidManifest.xml';tree=ET.parse(path);app=tree.getroot().find('application')
if not any(e.get(A+'name')=='org.emulationstation.frontend.VitaEntryActivity' for e in app):
    ET.SubElement(app,'activity',{A+'name':'org.emulationstation.frontend.VitaEntryActivity',A+'process':':psvita',A+'exported':'false',A+'screenOrientation':'userLandscape',A+'theme':'@android:style/Theme.Material.NoActionBar',A+'taskAffinity':'org.emulationstation.frontend',A+'enableOnBackInvokedCallback':'false'})
tree.write(path,encoding='utf-8',xml_declaration=True)
classes=R/'bridge-classes';classes.mkdir(exist_ok=True)
subprocess.run([str(java/'javac.exe'),'-encoding','UTF-8','-source','8','-target','8','-classpath',r'G:\Android\Sdk\platforms\android-34\android.jar','-d',str(classes),str(R/'VitaBootstrap.java'),str(R/'VitaEntryActivity.java')],check=True)
jar=R/'bridge.jar'
with zipfile.ZipFile(jar,'w') as z:
    for f in classes.rglob('*.class'):z.write(f,f.relative_to(classes).as_posix())
dex=R/'bridge-dex';dex.mkdir(exist_ok=True)
subprocess.run([str(java/'java.exe'),'-cp',str(bt/'lib/d8.jar'),'com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',str(dex),str(jar)],check=True)
release=json.loads((R/'official-release.json').read_text())
notice=M/'assets/psvita-integration';notice.mkdir(exist_ok=True)
license_url='https://raw.githubusercontent.com/Vita3K/Vita3K/master/COPYING.txt'
with urllib.request.urlopen(license_url,timeout=30) as f:(notice/'Vita3K-LICENSE').write_bytes(f.read())
shutil.copy2(Path(arc['source_dir'])/'COPYING',notice/'libarchive-LICENSE')
record={'source':release['html_url'],'release_body':release.get('body'),'donor_sha256':hashlib.sha256((R/'vita3k-official.apk').read_bytes()).hexdigest(),'process':':psvita','engine_rebuilt_from_source':False,'native_bridge_rebuilt':True,'registered_sdl_methods':native_count,'archive_library':arc['release'],'firmware':'Owner setup through official Vita3K UI; not bundled','scope':'internal Vita3K; no engine initialization in carousel process','runtime_verified':False}
(notice/'provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['VitaBootstrap.java','VitaEntryActivity.java','vita_archive_bridge.c','vita_sdl_registry.c']:shutil.copy2(R/name,notice/name)
(R/'integration.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(Path(__file__),R/'integrate.py')
print('Prepared Vita JNI, archive conversion and entry UI. SDL methods:',native_count,flush=True)
