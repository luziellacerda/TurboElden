from pathlib import Path
import subprocess,json
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');W=R/'collections-r11';T=W/'tests';T.mkdir(exist_ok=True)
s=Path('ui-r8/station_folder_navigation_test.cpp').read_text('utf8')
s=s.replace('check(folderCount==4);','check(folderCount==3);')
s=s.replace('select("Jogos desta pasta")','select("RPG")')
s=s.replace('select("Jogos sem subpasta");openSelectedFolder(ui);check(at<U*>(ui,0x100)-visible==1&&visible[0]==0);','''for(int i=0;i<folderCount;i++)check(strcmp(strData(folderItems+i*0xe8+0x18),"Jogos sem subpasta")!=0);
 select("Todos os jogos");char synopsis[2048];describeFolder((U)select("Todos os jogos"),synopsis,sizeof(synopsis));
 check(strstr(synopsis,"biblioteca completa")!=nullptr);check(strstr(synopsis,"id_root")!=nullptr);check(strstr(synopsis,"id_other")==nullptr);
 describeFolder((U)select("RPG"),synopsis,sizeof(synopsis));check(strstr(synopsis,"Coleção RPG.")!=nullptr);check(strstr(synopsis,"id_rpg")!=nullptr);check(strstr(synopsis,"id_deep")!=nullptr);check(strstr(synopsis,"id_root")==nullptr);check(strstr(synopsis,"id_rpg2")==nullptr);
 select("Todos os jogos");openSelectedFolder(ui);check(at<U*>(ui,0x100)-visible==4&&visible[0]==0);''')
s=s.replace('strAssign(storage+i*0xe8,realItems[i].id.c_str());','strAssign(storage+i*0xe8,realItems[i].id.c_str());strAssign(storage+i*0xe8+0x18,realItems[i].id.c_str());')
s=s.replace('folderFreeString(storage+i*0xe8+0x60);','folderFreeString(storage+i*0xe8+0x60);folderFreeString(storage+i*0xe8+0x18);')
(T/'station_collection_navigation_test.cpp').write_text(s,encoding='utf8')
source=r'''#include <cassert>
#include <cstring>
#include <iostream>
#include "collection_presentation.h"
static bool utf8(const char*s){while(*s){unsigned char c=(unsigned char)*s++;unsigned n=c<0x80?0:c<0xe0?1:c<0xf0?2:3;for(unsigned i=0;i<n;i++)if(!*s||((unsigned char)*s++&0xc0)!=0x80)return false;}return true;}
int main(){int count=0;auto check=[&](bool v){assert(v);count++;};
 check(!strcmp(collectionLeafName("RPG/Traduções"),"Traduções"));check(!strcmp(collectionLeafName("RPG"),"RPG"));
 check(collectionHasPath("RPG","RPG/Traduções",false,false));check(!collectionHasPath("RPG","RPG2",false,false));
 check(!collectionHasPath("RPG","RPG/Traduções",false,true));check(collectionHasPath("RPG","RPG",false,true));check(collectionHasPath("","",true,false));
 const char*examples[]={"Ação em português", "Corrida clássica"};char text[2048];
 collectionSynopsis(text,sizeof(text),"Traduções","Super Nintendo",2,0,examples,2);
 check(strstr(text,"Coleção Traduções.")!=nullptr);check(strstr(text,examples[0])!=nullptr);check(strstr(text,"2 jogos")!=nullptr);
 for(unsigned size=1;size<=2048;size++){memset(text,0x55,sizeof(text));collectionSynopsis(text,size,"Traduções","Super Nintendo",2,0,examples,2);check(memchr(text,0,size)!=nullptr);check(utf8(text));if(size<sizeof(text))check(text[size]==0x55);}
 std::cout<<"PASS "<<count<<" collection description, exact path and bounded UTF-8 checks\n";
}'''
(T/'station_collection_description_test.cpp').write_text(source,encoding='utf8')
results=[]
for name in ['station_collection_navigation_test','station_collection_description_test']:
 subprocess.run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-I'+str(R/'native'),'-I'+str(R/'station/src/native'),str(T/(name+'.cpp')),'-o',str(T/(name+'.exe'))],check=True)
 result=subprocess.run([str(T/(name+'.exe'))],capture_output=True,text=True,check=True);print(result.stdout.strip());results.append({'test':name,'result':result.stdout.strip()})
(T/'results.json').write_text(json.dumps({'native':results,'deviceVisualVerified':False,'gameIdsAndDownloadsUnchanged':True},indent=2)+'\n','utf8')
