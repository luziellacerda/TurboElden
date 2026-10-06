#pragma once
// Pure ribbon mesh, in cover-local pixels. All color stops are RGBA.
// Renderer::convertColor is REV w0 (verified at libmain+0x2e3980).
static unsigned stationRibbonColor(unsigned c){return (c>>24)|((c>>8)&0xff00u)|((c<<8)&0xff0000u)|(c<<24);}
static float stationRibbonClamp(float x){return x<0?0:x>1?1:x;}
static float stationRibbonSmooth(float x){x=stationRibbonClamp(x);return x*x*(3-2*x);}
static float stationRibbonAbs(float x){return x<0?-x:x;}
struct StationRibbonPoint{float x,y;};
template<class V> struct StationRibbonMesh{
 V vertices[448];unsigned count=0;float reach,length,half,fold;
 void vertex(float x,float y,unsigned color){if(count<448)vertices[count++]={x,y,0,0,stationRibbonColor(color)};}
 StationRibbonPoint point(float u,float v)const{return {.707106781f*(u+v),reach+.707106781f*(-u+v)};}
 void quad(StationRibbonPoint a,StationRibbonPoint b,StationRibbonPoint c,StationRibbonPoint d,unsigned ca,unsigned cb,unsigned cc,unsigned cd){
  if(count+6>448)return;
  if(count){vertices[count]=vertices[count-1];count++;vertex(a.x,a.y,ca);}
  vertex(a.x,a.y,ca);vertex(b.x,b.y,cb);vertex(c.x,c.y,cc);vertex(d.x,d.y,cd);
 }
 void triangle(StationRibbonPoint a,StationRibbonPoint b,StationRibbonPoint c,unsigned ca,unsigned cb,unsigned cc){quad(a,b,c,c,ca,cb,cc,cc);}
 void band(float top,float bottom,unsigned a,unsigned b){
  // Ends terminate on the left and top of the cover, even in the shadow.
  quad(point(-top,top),point(-bottom,bottom),point(length+top,top),point(length+bottom,bottom),a,b,a,b);
 }
 void localDiamond(float u,float v,float along,float across,unsigned center,unsigned edge){
  auto p=point(u,v),a=point(u-along,v),b=point(u,v-across),c=point(u+along,v),d=point(u,v+across);
  triangle(p,a,b,center,edge,edge);triangle(p,b,c,center,edge,edge);
  triangle(p,c,d,center,edge,edge);triangle(p,d,a,center,edge,edge);
 }
};
template<class V> static void stationBuildInstalledRibbon(StationRibbonMesh<V>&m,float width,unsigned now){
 m.count=0;if(!(width>0))return;
 m.reach=width*.38f;m.length=m.reach/.707106781f;m.half=width*.055f;m.fold=width*.021f;
 const float h=m.half,f=m.fold,bevel=width*.0032f,far=m.reach+h/.707106781f;
 // The two returns fold behind the cover; separate planes make the crease readable.
 m.triangle({-f,far-f},{0,far},{0,far-2*f},0x031D16eeu,0x0D4933ffu,0x087044ffu);
 m.triangle({-f,far-f},{-f*.18f,far-f*1.45f},{0,far-2*f},0x0C4935ffu,0x189264ffu,0x32C889ffu);
 m.triangle({-f*.12f,far-f*.12f},{0,far},{0,far-2*f},0x031B14ddu,0x031B14ffu,0x031B1440u);
 m.triangle({far-f,-f},{far,0},{far-2*f,0},0x082A1deeu,0x1A8255ffu,0x075539ffu);
 m.triangle({far-f,-f},{far-f*1.45f,-f*.18f},{far-2*f,0},0x25875dffu,0x3BE6A0ffu,0x15905fffu);
 m.triangle({far-f*.12f,-f*.12f},{far,0},{far-2*f,0},0x071F15ddu,0x071F15ffu,0x071F1540u);
 // Soft falloff, close contact, and a narrow physical lower lip.
 m.band(h+f*.45f,h+f*1.45f,0x00000030u,0x00000000u);
 m.band(h+bevel,h+f*.45f,0x00000070u,0x00000030u);
 m.band(h,h+bevel,0x00150ef0u,0x00150e80u);
 // Raised emerald face: top bevel, lit shoulder, dark readable center, bottom bevel.
 m.band(-h,-h+bevel,0x075639ffu,0xA1FFCDffu);
 m.band(-h+bevel,-h+bevel*2.4f,0xA1FFCDffu,0x32E991ffu);
 m.band(-h+bevel*2.4f,-h*.53f,0x32E991ffu,0x0B9D60ffu);
 m.band(-h*.53f,-h*.08f,0x0B9D60ffu,0x057947ffu);
 m.band(-h*.08f,h*.56f,0x057947ffu,0x045C3Dffu);
 m.band(h*.56f,h-bevel*2.6f,0x045C3Dffu,0x03482fffu);
 m.band(h-bevel*2.6f,h-bevel,0x03482fffu,0x19945bffu);
 m.band(h-bevel,h,0x19945bffu,0x042C1effu);
 // Fine light catches on both bevels; the central face remains clear behind the word.
 m.band(-h+bevel*.8f,-h+bevel*1.25f,0xE3FFECD0u,0xB7FFDA90u);
 m.band(-h*.54f,-h*.54f+bevel*.45f,0x60FFB12Au,0x60FFB100u);
 m.band(h-bevel*1.7f,h-bevel*1.25f,0x6FFFAB65u,0xB0FFD9A0u);
 // An oblique softbox reflection traverses the face and fades completely before wrap.
 const float phase=(now%3600u)/3600.f;
 const float center=-h*3+(m.length+h*6)*phase;
 const float broad=h*1.8f,core=h*.43f;
 const unsigned steps=52;
 if(m.count){m.vertices[m.count]=m.vertices[m.count-1];m.count++;}
 for(unsigned i=0;i<=steps;i++){
  float u=-h+(m.length+2*h)*i/steps;
  float low=-h+bevel*1.4f;if(-u>low)low=-u;if(u-m.length>low)low=u-m.length;
  float high=h-bevel*1.4f;if(low>high)low=high;
  for(unsigned side=0;side<2;side++){
   float v=side?high:low;
   float d=stationRibbonAbs(u-center-v*.72f);
   float soft=stationRibbonSmooth(1-d/broad),shine=stationRibbonSmooth(1-d/core);
   unsigned alpha=(unsigned)((soft*42+shine*96)*(side?.70f:1.f));
   auto p=m.point(u,v);unsigned color=0xDAFFE900u|alpha;
   if(!i&&!side)m.vertex(p.x,p.y,color);
   m.vertex(p.x,p.y,color);
  }
 }
 // A small elongated specular catch rides the darker lower chamfer, away from the lettering.
 float edgeU=center-h*.16f;
 float fade=stationRibbonSmooth((edgeU-h*1.8f)/(h*.65f))*stationRibbonSmooth((m.length-h*1.8f-edgeU)/(h*.65f));
 if(fade>0){
  float v=h-bevel*1.8f;
  m.localDiamond(edgeU,v,h*.52f,bevel*1.15f,0xB3FFD800u|(unsigned)(fade*96),0xB3FFD800u);
  m.localDiamond(edgeU,v,h*.20f,bevel*.42f,0xF6FFF800u|(unsigned)(fade*235),0xF6FFF800u);
 }
}
