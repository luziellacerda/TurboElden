// Native action bar: function colors, vector icons and an inset moving rim.
// Uses only the existing visible frame. No timers, images, overlays or workers.
struct GameActionPalette {unsigned accent,top,bottom;};
static GameActionPalette gameActionPalette(int slot,bool disabled,bool confirming){
 static const unsigned accents[]={0x62F49Bff,0x46DDF5ff,0x8EAFFFff,0xFF7F8Bff,0xFFD17Cff,0xB4C2D8ff,0x62F49Bff,0x66C9FFff,0x66C9FFff,0x62F49Bff,0xB699FFFF};
 unsigned a=accents[slot>=0&&slot<11?slot:5];
 if(disabled)return {0x73808Fff,0x171D25ff,0x0D1219ff};
 if(confirming)a=0xFF5566ff;
 return {a,blendColor(0x101923ff,a,confirming?.24f:.14f),blendColor(0x090F17ff,a,.045f)};
}
static float actionLabelInset(float h){return h*.98f;}
struct ActionPoint {float x,y;};
static ActionPoint actionRimPoint(float w,float h,int sample){
 // Four straight edges and four rounded corners, sampled clockwise.
 static const float sn[]={0,.19509032f,.38268343f,.55557023f,.70710678f,.83146961f,.92387953f,.98078528f,1};
 int step=sample%96,side=step/24,t=step%24;float r=h*.24f;
 if(t<=16){float u=t/16.f;
  if(side==0)return {r+(w-2*r)*u,0};
  if(side==1)return {w,r+(h-2*r)*u};
  if(side==2)return {w-r-(w-2*r)*u,h};
  return {0,h-r-(h-2*r)*u};
 }
 int i=t-16;float a=sn[i],b=sn[8-i];
 if(side==0)return {w-r+r*a,r-r*b};
 if(side==1)return {w-r+r*b,h-r+r*a};
 if(side==2)return {r-r*a,h-r+r*b};
 return {r-r*b,r-r*a};
}
struct ActionIconMesh {
 Vertex v[382];unsigned n=0,c;
 explicit ActionIconMesh(unsigned color):c(fn<unsigned(*)(unsigned)>(0x2e3980)(color)){}
 void quad(float ax,float ay,float bx,float by,float cx,float cy,float dx,float dy){
  if(n+6>382)return;
  Vertex q[4]={{ax,ay,0,0,c},{bx,by,0,0,c},{cx,cy,0,0,c},{dx,dy,0,0,c}};
  if(n){v[n]=v[n-1];n++;v[n++]=q[0];}
  for(int i=0;i<4;i++)v[n++]=q[i];
 }
 void line(float x,float y,float xx,float yy,float thickness){
  float dx=xx-x,dy=yy-y,length=squareRoot(dx*dx+dy*dy);if(length<.001f)return;
  float nx=-dy*thickness/(2*length),ny=dx*thickness/(2*length);
  quad(x+nx,y+ny,x-nx,y-ny,xx+nx,yy+ny,xx-nx,yy-ny);
 }
 void box(float x,float y,float w,float h,float t){line(x,y,x+w,y,t);line(x+w,y,x+w,y+h,t);line(x+w,y+h,x,y+h,t);line(x,y+h,x,y,t);}
 void flush(){if(n)fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(v,n,4,5);}
};
static void drawActionIcon(float x,float y,float s,int slot,unsigned color){
 ActionIconMesh m(color);float t=s*.085f;
 auto line=[&](float a,float b,float c,float d){m.line(x+a*s,y+b*s,x+c*s,y+d*s,t);};
 auto box=[&](float a,float b,float w,float h){m.box(x+a*s,y+b*s,w*s,h*s,t);};
 if(slot==8){for(int row=0;row<2;row++)for(int col=0;col<2;col++)box(.12f+col*.46f,.12f+row*.46f,.30f,.30f);}
 else if(slot==9){box(.12f,.12f,.76f,.76f);line(.25f,.5f,.44f,.69f);line(.44f,.69f,.76f,.31f);}
 else if(slot==10){line(.12f,.24f,.43f,.24f);line(.43f,.24f,.55f,.36f);line(.55f,.36f,.88f,.36f);line(.88f,.36f,.88f,.82f);line(.88f,.82f,.12f,.82f);line(.12f,.82f,.12f,.24f);}
 else if(slot==0){m.quad(x+s*.23f,y+s*.10f,x+s*.23f,y+s*.90f,x+s*.85f,y+s*.50f,x+s*.85f,y+s*.50f);}
 else if(slot==7){line(.5f,.08f,.5f,.68f);line(.22f,.44f,.5f,.72f);line(.5f,.72f,.78f,.44f);line(.12f,.76f,.12f,.92f);line(.12f,.92f,.88f,.92f);line(.88f,.92f,.88f,.76f);}
 else if(slot==1){ // Linked player terminals.
  line(.5f,.33f,.5f,.54f);line(.19f,.54f,.81f,.54f);line(.19f,.54f,.19f,.68f);line(.81f,.54f,.81f,.68f);
  box(.34f,.06f,.32f,.26f);box(.04f,.69f,.3f,.25f);box(.66f,.69f,.3f,.25f);
 }
 else if(slot==2){box(.13f,.09f,.74f,.82f);box(.3f,.10f,.38f,.25f);box(.29f,.55f,.42f,.36f);}
 else if(slot==3){line(.14f,.26f,.86f,.26f);line(.33f,.10f,.67f,.10f);line(.33f,.10f,.33f,.25f);line(.67f,.10f,.67f,.25f);line(.22f,.28f,.28f,.91f);line(.28f,.91f,.72f,.91f);line(.72f,.91f,.78f,.28f);line(.41f,.40f,.43f,.75f);line(.59f,.40f,.57f,.75f);}
 else if(slot==4){ // Open circular arrow, drawn as connected vector strokes.
  static const float pts[][2]={{.83f,.47f},{.78f,.26f},{.59f,.12f},{.36f,.14f},{.18f,.30f},{.14f,.54f},{.27f,.76f},{.5f,.85f},{.72f,.77f}};
  for(int i=0;i<8;i++)line(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1]);
  line(.83f,.47f,.60f,.34f);line(.83f,.47f,.95f,.22f);
 }
 else if(slot==6){line(.15f,.18f,.46f,.18f);line(.46f,.18f,.57f,.31f);line(.57f,.31f,.87f,.31f);line(.87f,.31f,.87f,.80f);line(.87f,.80f,.15f,.80f);line(.15f,.80f,.15f,.18f);line(.15f,.40f,.87f,.40f);}
 else{line(.17f,.5f,.87f,.5f);line(.17f,.5f,.48f,.18f);line(.17f,.5f,.48f,.82f);}
 m.flush();
}
static void drawGameAction(float x,float y,float w,float h,int slot,bool disabled,bool focused,bool confirming,bool installed=true){
 if(w<=0||h<=0)return;
 if(slot==0&&!installed)slot=7;
 auto palette=gameActionPalette(slot,disabled,confirming);
 float edge=h*.025f;if(edge<1)edge=1;
 unsigned now=disabled?0:fn<unsigned(*)()>(0x39e240)();
 openButtonFill(x,y,w,h,palette.top,palette.bottom);
 // The entire rim is INSIDE the hit rectangle; bright head with a soft trail.
 Vertex rim[194];unsigned count=0;
 float phase=((now+(unsigned)slot*310u)%4200u)/4200.f;
 for(int i=0;i<=96;i++){
  float p=i/96.f,d=p-phase;if(d<0)d+=1;
  float light=disabled?0:actionEase(actionClamp(1-d/.23f));
  unsigned baseColor=blendColor(palette.bottom,palette.accent,disabled?.32f:focused?.75f:.44f);
  unsigned color=blendColor(baseColor,blendColor(palette.accent,0xffffffff,.7f),light*.95f);
  auto outer=actionRimPoint(w,h,i),inner=actionRimPoint(w-2*edge,h-2*edge,i);
  unsigned packed=fn<unsigned(*)(unsigned)>(0x2e3980)(color);
  rim[count++]={x+outer.x,y+outer.y,0,0,packed};rim[count++]={x+edge+inner.x,y+edge+inner.y,0,0,packed};
 }
 fn<void(*)(unsigned)>(0x2e52e8)(0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(rim,count,4,5);
 float badge=h*.62f,bx=x+h*.17f,by=y+(h-badge)/2;
 openButtonFill(bx,by,badge,badge,blendColor(palette.top,palette.accent,disabled?.04f:.13f),palette.bottom);
 drawActionIcon(bx+badge*.18f,by+badge*.18f,badge*.64f,slot,disabled?0x83909Fff:palette.accent);
}
