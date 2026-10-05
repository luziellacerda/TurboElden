// Folded corner ribbon, replacing the previous hanging label completely.
// Existing native renderer only; state is still taken from the installed item.
static void*installedTagText;
static void drawInstalledTag(void*p){
 if(systemsMode||folderMode||modal(p)||at<int>(p,0x370)<2)return;
 int selected=fn<int(*)(void*)>(0x21b0c8)(p);if(selected<0)return;
 void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);
 if(!begin||!end||end<begin||(U)selected>=(U)(end-begin)/0xe8||!begin[(U)selected*0xe8+0xa8])return;
 float distance=at<int>(p,0xf0)-at<float>(p,0xf4);if(absolute(distance)>.30f)return;
 auto cover=coverSlot(p,distance);
 // A 45 degree ribbon between the left and top edges of the selected cover.
 constexpr float c=.707106781f;
 float reach=cover.w*.61f,length=reach/c,half=cover.w*.055f,fold=cover.w*.021f;
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);fn<void(*)(unsigned)>(0x2e52e8)(0);
 float far=reach+half/c;
 // Dark folded ends wrap behind the cover, within the existing outer margin.
 ActionIconMesh folds(0x032E20ffu);
 folds.quad(cover.x-fold,cover.y+far-fold,cover.x,cover.y+far,
            cover.x,cover.y+far-2*fold,cover.x,cover.y+far-2*fold);
 folds.quad(cover.x+far-fold,cover.y-fold,cover.x+far,cover.y,
            cover.x+far-2*fold,cover.y,cover.x+far-2*fold,cover.y);
 folds.flush();
 NativeMatrix local{{c,-c,0,0,c,c,0,0,0,0,1,0,cover.x,cover.y+reach,0,1}};
 NativeMatrix matrix=fn<NativeMatrix(*)(const void*,const void*)>(3019156)(&formationMatrix,&local);
 fn<void(*)(const void*)>(0x2e5640)(&matrix);
 auto band=[&](float top,float bottom,unsigned a,unsigned b){
  unsigned ca=fn<unsigned(*)(unsigned)>(0x2e3980)(a),cb=fn<unsigned(*)(unsigned)>(0x2e3980)(b);
  // u=-v and u=length+v terminate exactly on the left/top cover edges.
  Vertex q[4]={{-top,top,0,0,ca},{-bottom,bottom,0,0,cb},
               {length+top,top,0,0,ca},{length+bottom,bottom,0,0,cb}};
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);
 };
 // Soft contact shadow falls only inside the cover, followed by the satin face.
 band(half,half+fold*.90f,0x00000080u,0x00000000u);
 band(-half,0,0x39D791ffu,0x0A9A61ffu);
 band(0,half,0x0A9A61ffu,0x04553Bffu);
 float seam=cover.w*.0028f;
 band(-half,-half+seam,0xC7FFE7ddu,0xA4FFDB88u);
 band(half-seam,half,0x052D23ccu,0x062A21ffu);
 band(-half+seam*2,-half+seam*3,0x72F6BB44u,0x72F6BB44u);
 // A broad, low-opacity highlight stays inside the ribbon. No extra timers.
 unsigned now=fn<unsigned(*)()>(0x39e240)();float phase=(now%6400u)/6400.f;
 Vertex sheen[130];unsigned count=0;
 for(int i=0;i<=64;i++){
  float u=-half+(length+2*half)*i/64.f;
  float vmin=-half+seam;if(-u>vmin)vmin=-u;if(u-length>vmin)vmin=u-length;
  float vmax=half-seam;if(vmin>vmax)vmin=vmax;
  float light=actionClamp(1-absolute(u/length-(phase*1.5f-.25f))/.16f);
  unsigned color=fn<unsigned(*)(unsigned)>(0x2e3980)(0xDFFFF100u|(unsigned)(light*38));
  sheen[count++]={u,vmin,0,0,color};sheen[count++]={u,vmax,0,0,color};
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(sheen,count,4,5);
 static void*owner;static float oldLength,oldHalf;
 if(owner!=p){owner=p;installedTagText=createInfoText(p,0xF5FFF9ffu);setLongText(installedTagText,"INSTALADO");oldLength=0;}
 if(oldLength!=length||oldHalf!=half){
  oldLength=length;oldHalf=half;
  fitInfoText(installedTagText,{half*1.55f,-half*.82f,length-half*3.10f,half*1.64f},1.22f,1);
 }
 fn<void(*)(void*,void*)>(0x2d2dc4)(installedTagText,&matrix);
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
}
