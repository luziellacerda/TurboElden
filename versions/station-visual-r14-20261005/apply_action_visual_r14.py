from pathlib import Path
N=Path(r'E:\ESTUDO APK\work\station-netplay-20261004\native')
def edit(name,a,b):
 p=N/name;s=p.read_text('utf8');assert s.count(a)==1,(name,a);p.write_text(s.replace(a,b),'utf8',newline='\n')
edit('native_skin.h','static constexpr float gameActionTextScale=.60f;','static constexpr float gameActionTextScale=.60f;\nstatic float actionLabelInset(float);')
old='  place((B*)p+labels[i],x,h*(systemsMode?.851f:.908f),width,h*(systemsMode?.094f:.065f),systemsMode?(folderMode?.66f:.92f):gameActionTextScale,1);'
new='''  float buttonH=h*(systemsMode?.094f:.065f);
  bool withIcon=!systemsMode||i==0||(folderMode&&i==4);
  float labelInset=withIcon?actionLabelInset(buttonH):0;
  place((B*)p+labels[i],x+labelInset,h*(systemsMode?.851f:.908f),width-labelInset-(withIcon?buttonH*.16f:0),buttonH,systemsMode?(folderMode?.66f:.92f):gameActionTextScale,1);'''
edit('native_skin.h',old,new)
edit('native_skin.h','if(systemsMode&&offset==0xe00)color=0x0F172Aff; // slate-900, matching the reference login button.','if(systemsMode&&offset==0xe00)color=0xF3FFF6ff;')
edit('native_skin.h','drawGameAction(x,y,bw,bh,action==0?0:action+1,disabled,focused,confirming);continue;','drawGameAction(x,y,bw,bh,action==0?0:action+1,disabled,focused,confirming,installed);continue;')
edit('native_skin.h','  unsigned color=action==0?0x147D32ff:disabled?0x101512ff:0x151D17ff;','  if(folderMode&&action==4){drawGameAction(x,y,bw,bh,5,false,at<float>(p,0x1c4+action*4)>.08f,false);continue;}\n  unsigned color=action==0?0x147D32ff:disabled?0x101512ff:0x151D17ff;')
edit('native_netplay.h',' place(onlineActionText,x,h*.908f,bw,h*.065f,gameActionTextScale,1);',' float labelInset=actionLabelInset(h*.065f);\n place(onlineActionText,x+labelInset,h*.908f,bw-labelInset-h*.065f*.16f,h*.065f,gameActionTextScale,1);')
p=N/'native_action_motion.h';s=p.read_text('utf8');start=s.index('static void drawPrimaryOpen(');end=s.index('#include "native_pause_menu.h"',start)
s=s[:start]+'''static void drawGameAction(float,float,float,float,int,bool,bool,bool,bool);
static void drawPrimaryOpen(void*p,float x,float y,float w,float h){
 drawGameAction(x,y,w,h,6,false,at<float>(p,0x1c4)>.08f,false,true);
}
'''+s[end:];p.write_text(s,'utf8',newline='\n')
print('Native action layout, icons and routes connected')
