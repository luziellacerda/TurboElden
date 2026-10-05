from pathlib import Path
import shutil
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');N=R/'native';W=R/'navigation-r14b';(W/'before').mkdir(parents=True,exist_ok=False)
for name in ['native_folders.h','native_menu_power.h']:shutil.copyfile(N/name,W/'before'/name)
def edit(name,a,b):
 p=N/name;s=p.read_text('utf8');assert s.count(a)==1,(name,a);p.write_text(s.replace(a,b),'utf8',newline='\n')
edit('native_folders.h','static U folderRevision;','static U folderRevision;\nstatic int folderReturnKind=-1;')
edit('native_folders.h','foldersEnabled=folderMode=folderAllGames=false;folderPlatform','foldersEnabled=folderMode=folderAllGames=false;folderReturnKind=-1;folderPlatform')
edit('native_folders.h','static void showFolderMenu(void*p,const char*path){\n char next[2049];if(!folderCopy(next,sizeof(next),path)||!folderBridge())return;','''static void showFolderMenu(void*p,const char*path,const char*selectedPath=nullptr,int selectedKind=-1){
 char next[2049],selection[2049]={};if(!folderCopy(next,sizeof(next),path)||!folderBridge())return;
 // Copy the stable path/kind BEFORE releasing the old facade. Visible indices
 // and collection_N IDs may change when the server inserts/removes folders.
 if(selectedPath){if(!folderCopy(selection,sizeof(selection),selectedPath))return;}
 else if(folderMode&&strcmp(folderPath,next)==0){
  int cursor=at<int>(p,0xf0);U*begin=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
  if(begin&&cursor>=0&&begin+cursor<end&&begin[cursor]<(U)folderCount){
   const auto&meta=folderMeta[begin[cursor]];folderCopy(selection,sizeof(selection),strData(meta.path));selectedKind=meta.kind;
  }
 }''')
edit('native_folders.h',' invalidate(p);rebuildHook(p);refreshHook(p);folderRevision=foldersRevision();',''' invalidate(p);rebuildHook(p);
 if(selectedKind>=0){
  U*begin=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
  for(U*it=begin;it&&it<end;it++)if(*it<(U)folderCount){
   const auto&meta=folderMeta[*it];
   if(meta.kind==selectedKind&&strcmp(strData(meta.path),selection)==0){
    int cursor=(int)(it-begin);at<int>(p,0xf0)=cursor;at<float>(p,0xf4)=(float)cursor;break;
   }
  }
 }
 refreshHook(p);folderRevision=foldersRevision();''')
edit('native_folders.h','static void enterFolderGames(void*p,const char*path,bool all,const char*returnPath){','static void enterFolderGames(void*p,const char*path,bool all,const char*returnPath,int returnKind){')
edit('native_folders.h',' clearTextures(p);folderMode=false;systemsMode=false;folderAllGames=all;',' clearTextures(p);folderReturnKind=returnKind;folderMode=false;systemsMode=false;folderAllGames=all;')
edit('native_folders.h','enterFolderGames(p,"",true,back);','enterFolderGames(p,"",true,back,2);')
edit('native_folders.h','if(meta.kind==1){enterFolderGames(p,target,false,back);return;}','if(meta.kind==1){enterFolderGames(p,target,false,back,1);return;}')
edit('native_folders.h','else enterFolderGames(p,target,false,back);','else enterFolderGames(p,target,false,back,0);')
edit('native_folders.h','if(!systemsMode){showFolderMenu(p,folderReturnPath);return true;}','if(!systemsMode){showFolderMenu(p,folderReturnPath,folderPath,folderReturnKind);return true;}')
edit('native_folders.h','showFolderMenu(p,parent);return true;}','showFolderMenu(p,parent,folderPath,0);return true;}')
edit('native_menu_power.h','static void paceStoreMenu(void*p){','''static int storeMenuTargetFps(bool dialog,bool interacting,bool loading){
 // A visible carousel has ongoing LED/button/scene animation even without touch.
 // Keep its existing interactive cadence; only a covering idle dialog uses 15.
 // Video clips still decode at their encoded 30 fps. Emulator and background
 // lifecycle are outside this GuiStore-only policy and remain unchanged.
 return !dialog||interacting||loading?60:15;
}
static void paceStoreMenu(void*p){''')
edit('native_menu_power.h',' float cursorDifference=at<float>(p,0xf4)-(float)at<int>(p,0xf0);\n bool transition=!dialog&&(cursorDifference>.002f||cursorDifference<-.002f);\n','')
edit('native_menu_power.h',' int fps=(interacting||transition||at<int>(p,0x370)!=3)?60:\n         (!dialog&&systemsMode&&video720Asset(p,at<int>(p,0xf0))?30:15);',' int fps=storeMenuTargetFps(dialog,interacting,at<int>(p,0x370)!=3);')
print('R14B: stable folder selection and visible-menu cadence applied')
