from pathlib import Path
import shutil,hashlib,json
w=Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005')
b=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005')
overlay=Path('work/station-native-rate-phase-20261005/frontend-native').resolve()
assert not w.exists();(w/'native').mkdir(parents=True);(w/'before').mkdir();(w/'tests').mkdir()
for name in ('native_carousel.cpp','native_search_download.h'):
 shutil.copy2(overlay/name,w/'native'/name)
p=b/'frontend-native/native_folders.h';shutil.copy2(p,w/'before/native_folders.h')
t=p.read_text('utf8')
t=t.replace('static int folderReturnKind=-1;','''static int folderReturnKind=-1;
// Store only screens actually shown. Auto-skipped paths never create a Back loop.
struct FolderBackEntry {char parent[2049],selected[2049];int kind;};
static FolderBackEntry folderHistory[16];static int folderHistoryCount;
static bool openFolderPath(void*,const char*);''')
t=t.replace('foldersEnabled=folderMode=folderAllGames=false;folderReturnKind=-1;','foldersEnabled=folderMode=folderAllGames=false;folderHistoryCount=0;folderReturnKind=-1;')
t=t.replace('lastSystem=index;foldersEnabled=true;showFolderMenu(p,"");return true;','lastSystem=index;foldersEnabled=true;folderHistoryCount=0;return openFolderPath(p,"");')
anchor='static void openSelectedFolder(void*p){'
insert='''struct OnlyFolderChild {char path[2049];int seen;bool valid;};
static void onlyFolderChild(void*ctx,const char*path,const char*,U,const char*){
 auto&child=*(OnlyFolderChild*)ctx;child.seen++;
 if(child.seen==1)child.valid=folderCopy(child.path,sizeof(child.path),path);
}
static bool openFolderPath(void*p,const char*path){
 char target[2049];if(!folderCopy(target,sizeof(target),path))return false;
 // Signed metadata admits at most eight components; bound malformed bridge data too.
 for(int depth=0;depth<16;depth++){
  U direct=0;int children=visitFolders(folderPlatform,target,&direct,nullptr,nullptr);
  if(children<0)return false;
  if(children==0){enterFolderGames(p,target,!*target,"",0);return true;}
  if(children==1&&direct==0){
   OnlyFolderChild child={{0},0,false};visitFolders(folderPlatform,target,nullptr,onlyFolderChild,&child);
   U length=strlen(target);
   bool descendant=child.valid&&child.seen==1&&*child.path&&strlen(child.path)>length;
   if(length&&descendant){for(U i=0;i<length;i++)if(child.path[i]!=target[i])descendant=false;descendant=descendant&&child.path[length]=='/';}
   if(descendant){folderCopy(target,sizeof(target),child.path);continue;}
  }
  showFolderMenu(p,target);return true;
 }
 showFolderMenu(p,target);return true;
}
'''
assert anchor in t;t=t.replace(anchor,insert+anchor)
a=''' if(meta.kind==2){enterFolderGames(p,"",true,back,2);return;}
 if(meta.kind==1){enterFolderGames(p,target,false,back,1);return;}
 U direct=0;if(visitFolders(folderPlatform,target,&direct,nullptr,nullptr)>0)showFolderMenu(p,target);
 else enterFolderGames(p,target,false,back,0);'''
bcode=''' if(folderHistoryCount>=16)return;
 auto&previous=folderHistory[folderHistoryCount];
 if(!folderCopy(previous.parent,sizeof(previous.parent),back)||!folderCopy(previous.selected,sizeof(previous.selected),target))return;
 previous.kind=meta.kind;folderHistoryCount++;
 if(meta.kind==2){enterFolderGames(p,"",true,back,2);return;}
 if(meta.kind==1){enterFolderGames(p,target,false,back,1);return;}
 if(!openFolderPath(p,target))folderHistoryCount--;'''
assert a in t;t=t.replace(a,bcode)
a=''' if(!systemsMode){showFolderMenu(p,folderReturnPath,folderPath,folderReturnKind);return true;}
 if(folderMode&&*folderPath){char parent[2049];folderCopy(parent,sizeof(parent),folderPath);int n=(int)strlen(parent);while(n>0&&parent[n-1]!='/')--n;parent[n>0?n-1:0]=0;showFolderMenu(p,parent,folderPath,0);return true;}'''
bcode=''' if(folderHistoryCount>0){
  const auto&previous=folderHistory[--folderHistoryCount];
  showFolderMenu(p,previous.parent,previous.selected,previous.kind);return true;
 }'''
assert a in t;t=t.replace(a,bcode)
(w/'native/native_folders.h').write_text(t,'utf8',newline='\n')
(w/'source-base.json').write_text(json.dumps({'base':'R16','nativeBase':str(b/'frontend-native'),'rateOverlay':str(overlay),'baseFolderSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'folderSHA256':hashlib.sha256((w/'native/native_folders.h').read_bytes()).hexdigest(),'baseApkSHA256':'b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1'},indent=2),'utf8')
print('Isolated native navigation prepared; R16 performance overlay preserved')
