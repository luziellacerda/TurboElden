from pathlib import Path
import shutil
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');N=R/'native';W=R/'collections-r11'
(W/'before').mkdir(parents=True,exist_ok=False)
for name in ['native_folders.h','native_info.h','native_carousel.cpp','native_formation.h']:shutil.copyfile(N/name,W/'before'/name)
shutil.copyfile('collection_presentation.h',N/'collection_presentation.h')
def edit(name,old,new):
 p=N/name;s=p.read_text('utf8');assert old in s,name;p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
edit('native_folders.h','// Presentation-only folders.','#include "collection_presentation.h"\n// Presentation-only folders.')
edit('native_folders.h','if(direct&&(*next||children))appendFolder(next,*next?"Jogos desta pasta":"Jogos sem subpasta",direct,folderArt(),1);','if(direct&&*next&&children)appendFolder(next,collectionLeafName(next),direct,folderArt(),1);')
edit('native_folders.h','static void appendFolderVisitor(','''static void describeFolder(U index,char*body,U size){
 if(index>=(U)folderCount){if(size)body[0]=0;return;}
 const FolderMeta&meta=folderMeta[index];const char*path=strData(meta.path);
 const char*examples[3]={};unsigned count=0;
 void*real=fn<void*(*)()>(0x1887dc)();B*end=at<B*>(real,0x90);
 for(B*it=at<B*>(real,0x88);it&&it<end&&count<3;it+=0xe8){
  if(strcmp(strData(it+0x60),folderPlatform)!=0)continue;
  const char*itemPath=itemFolderPath?itemFolderPath(strData(it)):"";
  if(!collectionHasPath(path,itemPath?itemPath:"",meta.kind==2,meta.kind==1))continue;
  const char*name=strData(it+0x18);if(!*name)continue;
  bool duplicate=false;for(unsigned j=0;j<count;j++)if(strcmp(examples[j],name)==0)duplicate=true;
  if(!duplicate)examples[count++]=name;
 }
 collectionSynopsis(body,size,strData(folderItems+index*0xe8+0x18),folderPlatform,meta.count,meta.kind,examples,count);
}
static void appendFolderVisitor(''')
old='''  char amount[24];folderNumber(amount,folderMeta[index].count);
  U n=0;const char*parts[]={folderPlatform,"\\n",*folderPath?folderPath:"Todas as subpastas","\\n\\n",amount," jogos\\nAbra para ver os jogos desta seleção."};
  for(int i=0;i<7;i++)for(const char*t=parts[i];*t&&n<sizeof(pageText)-1;t++)pageText[n++]=*t;body=pageText;'''
edit('native_info.h',old,'''  describeFolder(index,pageText,sizeof(pageText));body=pageText;''')
edit('native_info.h','static bool isSystemInfoText(void*t){return t==infoTitle||t==infoDescription;}', '''static void*folderLabels[20];static void*folderLabelOwner;
static bool isSystemInfoText(void*t){if(t==infoTitle||t==infoDescription)return true;for(int i=0;i<20;i++)if(t==folderLabels[i])return true;return false;}
static void drawFolderLabels(void*p){
 if(!folderMode)return;
 if(folderLabelOwner!=p){folderLabelOwner=p;for(int i=0;i<20;i++)folderLabels[i]=nullptr;}
 U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);if(!visible||!end)return;
 for(int k=0;k<paintedCount&&k<20;k++){
  const CoverRect&r=painted[k];if(r.index<0||visible+r.index>=end||visible[r.index]>=(U)folderCount)continue;
  if(!folderLabels[k])folderLabels[k]=createInfoText(p,0xF3FFF6ff);
  const char*name=strData(folderItems+visible[r.index]*0xe8+0x18);void*label=folderLabels[k];
  if(strcmp(strData((B*)label+0xd0),name)!=0)setLongText(label,name);
  const float band=r.h*.25f,scale=r.w/420.f;
  fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
  rect(r.x+r.w*.025f,r.y+r.h-band-r.h*.035f,r.w*.95f,band,0x031008ee);
  place(label,r.x+r.w*.065f,r.y+r.h-band-r.h*.025f,r.w*.87f,band,scale<.30f?.30f:scale>.90f?.90f:scale,1);
  fn<void(*)(void*,void*)>(0x2d2dc4)(label,&formationMatrix);
 }
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
}''')
edit('native_formation.h','static void drawSystemInfoLayer(void*);','static void drawSystemInfoLayer(void*);\nstatic void drawFolderLabels(void*);')
edit('native_formation.h',' drawSystemVideo720(p);\n drawFocusLaser(p);',' drawSystemVideo720(p);\n drawFolderLabels(p);\n drawFocusLaser(p);')
edit('native_formation.h','   if(systemsMode){\n    // No colored loading flash.','   if(systemsMode&&!folderMode){\n    // No colored loading flash.')
edit('native_carousel.cpp','replacement=systemsMode?"PLATAFORMAS":"LOJA";','replacement=folderMode?"COLEÇÕES":systemsMode?"PLATAFORMAS":"LOJA";')
print('Collection names/descriptions and root navigation adjusted; no game IDs or routes changed')
