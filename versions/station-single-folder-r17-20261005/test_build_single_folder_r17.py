from pathlib import Path
import subprocess,json,hashlib,os
w=Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005');base=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005')
n=w/'native';tests=w/'tests';os.environ['TEMP']=os.environ['TMP']=str(tests)
nav=Path(r'E:\ESTUDO APK\work\station-netplay-20261004\navigation-r14b\tests\navigation.cpp').read_text('utf8')
a='check(folderMode&&folderCount==1);check(folderMeta[select("Todos os jogos")].count==0);'
b='check(!folderMode&&!systemsMode);check(at<U*>(ui,0x100)==visible);'
assert a in nav;nav=nav.replace(a,b)
needle=' showSystems(ui);for(size_t i=0;i<realItems.size();i++)'
extra=r'''
 // Flat platforms bypass the synthetic one-cell "Todos os jogos" screen.
 showSystems(ui);paths.clear();revision++;
 check(enterFolderRoot(ui,"Super Nintendo",2));check(!systemsMode&&!folderMode&&folderAllGames);
 check(at<U*>(ui,0x100)-visible==4);check(folderHistoryCount==0);
 check(backFromFolder(ui));check(systemsMode&&!foldersEnabled&&lastSystem==2);
 // A root with one real child and no direct games has no meaningful choice.
 for(auto&it:realItems)paths[it.id]="Coleção única/Traduções/Seleção";
 revision++;check(enterFolderRoot(ui,"Super Nintendo",2));check(!systemsMode&&!folderMode);
 check(!strcmp(folderPath,"Coleção única/Traduções/Seleção"));check(at<U*>(ui,0x100)-visible==4);
 check(backFromFolder(ui));check(systemsMode&&!foldersEnabled); // Never re-enter a hidden chain.
 // Keep the menu when direct games coexist with one child.
 paths["id_root"]="";revision++;check(enterFolderRoot(ui,"Super Nintendo",2));check(folderMode&&folderCount==2);
 select("Coleção única");openSelectedFolder(ui);check(!systemsMode);check(at<U*>(ui,0x100)-visible==3);
 check(backFromFolder(ui));check(folderMode&&!*folderPath);check(!strcmp(selectedName(),"Coleção única"));
 select("Todos os jogos");openSelectedFolder(ui);check(at<U*>(ui,0x100)-visible==4);check(backFromFolder(ui));
 // A single-child chain can end at a genuine two-way menu.
 paths["id_rpg"]="Coleção única/Traduções/A";paths["id_rpg2"]="Coleção única/Traduções/B";
 paths["id_deep"]="Coleção única/Traduções/B";revision++;refreshFolderNavigation(ui);
 select("Coleção única");openSelectedFolder(ui);check(folderMode&&!strcmp(folderPath,"Coleção única/Traduções"));check(folderCount==2);
 select("B");openSelectedFolder(ui);check(!systemsMode&&at<U*>(ui,0x100)-visible==2);
 check(backFromFolder(ui));check(!strcmp(folderPath,"Coleção única/Traduções"));check(!strcmp(selectedName(),"B"));
 check(backFromFolder(ui));check(!*folderPath&&!strcmp(selectedName(),"Coleção única"));
 check(backFromFolder(ui));check(!foldersEnabled);
 // An automatically opened root branch returns directly to platforms.
 paths["id_root"]="Coleção única/Traduções/A";revision++;
 check(enterFolderRoot(ui,"Super Nintendo",2));check(folderMode&&!strcmp(folderPath,"Coleção única/Traduções"));
 check(backFromFolder(ui));check(!foldersEnabled&&systemsMode);
 // Mixed direct+child games inside a collection must not be hidden.
 paths["id_root"]="";paths["id_rpg"]="Coleção única/Traduções";revision++;
 check(enterFolderRoot(ui,"Super Nintendo",2));select("Coleção única");openSelectedFolder(ui);
 check(folderMode&&!strcmp(folderPath,"Coleção única/Traduções")&&folderCount==2);
 select("Traduções");openSelectedFolder(ui);check(!systemsMode&&at<U*>(ui,0x100)-visible==1);
 check(backFromFolder(ui));check(folderMeta[visible[at<int>(ui,0xf0)]].kind==1);
 check(backFromFolder(ui));check(!strcmp(selectedName(),"Coleção única"));
 // Stable original selection survives refresh and sibling insertion after auto-forward.
 for(int round=0;round<100;round++){
  select("Coleção única");openSelectedFolder(ui);select("B");openSelectedFolder(ui);
  check(at<U*>(ui,0x100)-visible==2);revision++;refreshFolderNavigation(ui);
  check(backFromFolder(ui));check(!strcmp(selectedName(),"B"));
  check(backFromFolder(ui));check(!strcmp(selectedName(),"Coleção única"));
 }
 showSystems(ui);
'''
assert needle in nav;nav=nav.replace(needle,extra+needle);(tests/'navigation.cpp').write_text(nav,'utf8')
cc=r'C:\Program Files\LLVM\bin\clang++.exe'
def run(args,name,success=True):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(w/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');assert (p.returncode==0)==success,(name,p.stdout+p.stderr);print(name,(p.stdout+p.stderr)[-400:],flush=True);return p.stdout+p.stderr
includes=['-I'+str(n),'-I'+str(base/'frontend-native'),'-I'+str(base/'client/src/native')]
run([cc,'-std=c++17',*includes,tests/'navigation.cpp','-o',tests/'navigation.exe'],'navigation-compile')
result=run([tests/'navigation.exe'],'navigation')
# Old code must reject the changed behavior (flat platform and automatic chain).
old=nav.replace('check(folderHistoryCount==0);','')
(tests/'navigation-old.cpp').write_text(old,'utf8')
run([cc,'-std=c++17','-I'+str(w/'before'),*includes,tests/'navigation-old.cpp','-o',tests/'navigation-old.exe'],'old-compile')
run([tests/'navigation-old.exe'],'old-rejected',False)
clang=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe')
command=[clang,'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-nostdlib','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-soname,libturbo_carousel.so','-I',base/'frontend-native',n/'native_carousel.cpp',base/'frontend-native/video720_posters.o','-L',base/'frontend-native','-lc','-ldl','-llog','-o',w/'libturbo_carousel.so']
run(command,'android-build')
(w/'tests.json').write_text(json.dumps({'navigation':result.strip(),'oldRejected':True,'androidCompiled':True,'command':list(map(str,command)),'soSHA256':hashlib.sha256((w/'libturbo_carousel.so').read_bytes()).hexdigest()},indent=2),'utf8')
