// Hanging price-tag style from the user's reference. Native vectors, not a
// bitmap or a separate overlay. Only the selected installed game gets a tag.
static void*installedTagText;
static void drawInstalledTag(void*p){
 if(systemsMode||folderMode||modal(p)||at<int>(p,0x370)<2)return;
 int selected=fn<int(*)(void*)>(0x21b0c8)(p);if(selected<0)return;
 void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);
 if(!begin||!end||end<begin||(U)selected>=(U)(end-begin)/0xe8||!begin[(U)selected*0xe8+0xa8])return;
 // Follow the actual selected cell during the native carousel movement.
 float distance=at<int>(p,0xf0)-at<float>(p,0xf4);auto cover=coverSlot(p,distance);
 if(absolute(distance)>.30f)return;
 float width=cover.w*.73f,height=width*.225f;
 float x=cover.x+cover.w*.04f,y=cover.y+cover.h*.12f;
 constexpr float co=.990268069f,si=-.139173101f; // Same tilt for art and lettering.
 NativeMatrix local{{co,si,0,0,-si,co,0,0,0,0,1,0,x,y,0,1}};
 NativeMatrix matrix=fn<NativeMatrix(*)(const void*,const void*)>(3019156)(&formationMatrix,&local);
 fn<void(*)(const void*)>(0x2e5640)(&matrix);fn<void(*)(unsigned)>(0x2e52e8)(0);
 auto shape=[&](float inset,float dy,unsigned left,unsigned right){
  unsigned a=fn<unsigned(*)(unsigned)>(0x2e3980)(left),b=fn<unsigned(*)(unsigned)>(0x2e3980)(right);
  Vertex v[5]={{inset,inset+dy,0,0,a},{inset,height-inset+dy,0,0,a},
   {width*.82f,inset+dy,0,0,b},{width*.82f,height-inset+dy,0,0,b},{width-inset,height*.5f+dy,0,0,b}};
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(v,5,4,5);
 };
 shape(0,height*.075f,0x00000088u,0x00000088u);
 shape(0,0,0xA6FFBDffu,0x43D590ffu);
 shape(height*.026f,0,0x08784Cffu,0x142D28ffu);
 // Contained highlight slides through the tag face; no continuous CPU task.
 unsigned now=fn<unsigned(*)()>(0x39e240)();float phase=(now%5200u)/5200.f;
 Vertex sheen[86];unsigned count=0;float edge=height*.04f;
 for(int i=0;i<=42;i++){
  float xx=edge+(width-2*edge)*i/42.f;
  float inset=xx>width*.82f?(xx-width*.82f)/(width*.18f)*(height*.5f):edge;
  if(inset<edge)inset=edge;if(inset>height*.5f)inset=height*.5f;
  float light=actionClamp(1-absolute(xx/width-(phase*1.5f-.25f))/.14f);
  unsigned c=fn<unsigned(*)(unsigned)>(0x2e3980)(0xD7FFE800u|(unsigned)(light*36));
  sheen[count++]={xx,inset,0,0,c};sheen[count++]={xx,height-inset,0,0,c};
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(sheen,count,4,5);
 // Eyelet, with a short fabric loop extending from the pointed end.
 constexpr float circle[][2]={{1,0},{.9238795f,.3826834f},{.7071068f,.7071068f},{.3826834f,.9238795f},{0,1},{-.3826834f,.9238795f},{-.7071068f,.7071068f},{-.9238795f,.3826834f},{-1,0},{-.9238795f,-.3826834f},{-.7071068f,-.7071068f},{-.3826834f,-.9238795f},{0,-1},{.3826834f,-.9238795f},{.7071068f,-.7071068f},{.9238795f,-.3826834f}};
 float hx=width*.88f,hy=height*.5f,hr=height*.103f;
 ActionIconMesh hole(0x08110Effu);
 for(int i=0;i<16;i++){auto a=circle[i];auto b=circle[(i+1)%16];hole.quad(hx,hy,hx+hr*a[0],hy+hr*a[1],hx+hr*b[0],hy+hr*b[1],hx+hr*b[0],hy+hr*b[1]);}hole.flush();
 ActionIconMesh metal(0xC4D3CEffu);
 for(int i=0;i<16;i++){auto a=circle[i];auto b=circle[(i+1)%16];metal.line(hx+hr*a[0],hy+hr*a[1],hx+hr*b[0],hy+hr*b[1],height*.028f);}metal.flush();
 // Cubic loop starts and ends at the eyelet, as in the hanging label reference.
 auto loop=[&](unsigned color,float thickness,float offset){
  ActionIconMesh m(color);float px=hx,py=hy;
  for(int i=1;i<=44;i++){
   float t=i/44.f,u=1-t;
   float xx=u*u*u*hx+3*u*u*t*(width*1.37f)+3*u*t*t*(width*1.29f)+t*t*t*hx;
   float yy=u*u*u*hy+3*u*u*t*(-height*.87f)+3*u*t*t*(height*1.22f)+t*t*t*hy;
   m.line(px,py+offset,xx,yy+offset,thickness);px=xx;py=yy;
  }m.flush();
 };
 loop(0x06100Cdd,height*.072f,height*.02f);loop(0xB5C7BEff,height*.032f,0);
 // Small Turborama red stitch, leaving the main badge green/black.
 rect(width*.04f,height*.18f,width*.012f,height*.64f,0xF15B62ffu);
 static void*owner;static float oldW,oldH;
 if(owner!=p){owner=p;installedTagText=createInfoText(p,0xF4FFF6ffu);setLongText(installedTagText,"INSTALADO");oldW=0;}
 if(oldW!=width||oldH!=height){oldW=width;oldH=height;fitInfoText(installedTagText,{width*.085f,height*.10f,width*.68f,height*.80f},1.45f,1);}
 fn<void(*)(void*,void*)>(0x2d2dc4)(installedTagText,&matrix);
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
}
