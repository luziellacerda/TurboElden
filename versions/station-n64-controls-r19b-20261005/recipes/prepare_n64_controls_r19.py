from pathlib import Path
import hashlib, json, shutil, subprocess, os

W = Path(r'E:\ESTUDO APK\work\station-n64-controls-r19-20261005')
R17 = Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005')
BASE = Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
N = W / 'native'
N.mkdir(exist_ok=False)
(W / 'before').mkdir()
(W / 'tests').mkdir()
for name in ('native_carousel.cpp', 'native_folders.h', 'native_search_download.h'):
    shutil.copy2(R17 / 'native' / name, N / name)
old = (BASE / 'native_n64.h').read_text('utf8')
(W / 'before/native_n64.h').write_text(old, 'utf8')
end = old.index('static jclass n64Bridge;')
identity = '''// Match catalog identities and the exact names used by the native resolver.
static bool n64PlatformKey(const char* key){
 return presentationKeyEqual(key,"Nintendo 64") ||
        presentationKeyEqual(key,"Nintendo 64 - BR") ||
        presentationKeyEqual(key,"n64") || presentationKeyEqual(key,"n64br") ||
        presentationKeyEqual(key,"nintendo-64") || presentationKeyEqual(key,"nintendo-64--br");
}
static bool n64Core(const void* id){
 const char* s=strData(id);
 if(n64PlatformKey(s))return true;
 // resolveCore adds "lib" to a bundled core. Other existing launch entries
 // can carry its absolute path; compare only the complete filename, not a substring.
 const char* name=s;
 for(const char* p=s;*p;p++)if(*p=='/'||*p=='\\\\')name=p+1;
 if(name[0]=='l'&&name[1]=='i'&&name[2]=='b')name+=3;
 return strcmp(name,"mupen64plus_ae_android.so")==0 ||
        strcmp(name,"mupen64plus_next_gles3_libretro_android.so")==0 ||
        strcmp(name,"mupen64plus_next_gles3")==0;
}
'''
new = identity + old[end:]
a = ''' if(presentationKeyEqual(key,"Nintendo 64")||presentationKeyEqual(key,"Nintendo 64 - BR")||
    presentationKeyEqual(key,"n64")||presentationKeyEqual(key,"n64br")){'''
assert a in new
new = new.replace(a, ' if(n64PlatformKey(key)){')
(N / 'native_n64.h').write_text(new, 'utf8')
manifest = {
    'baseAPK': r'E:\ESTUDO APK\work\station-neogeo-access-20261005\TurboStations-NeoGeo-Pastas-R18-20261005.apk',
    'baseSHA256': 'a29151da312830d826f6ea71ebb61cb8a39fe1c21786f719e26a61568b29b1c4',
    'nativeOverlay': str(R17 / 'native'), 'unchangedDependencies': str(BASE),
    'changedSource': ['native_n64.h'],
    'beforeSHA256': hashlib.sha256((BASE/'native_n64.h').read_bytes()).hexdigest(),
    'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in N.iterdir()},
}
(W/'source-base.json').write_text(json.dumps(manifest, indent=2), 'utf8')
print(json.dumps(manifest, indent=2))
