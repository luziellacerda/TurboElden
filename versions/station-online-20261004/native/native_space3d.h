// Uso autorizado: consulte AGENTS.md; direitos de terceiros preservados.
// Clouds-only background. No aircraft model, material maps, hull/depth passes or exhaust.
#include "space3d_shaders.h"
#include "native_flight.h"
struct SpaceGL {
#define SGL(R,N,A) R(*N)A;
 SGL(void,GenBuffers,(int,unsigned*)) SGL(void,BindBuffer,(unsigned,unsigned)) SGL(void,BufferData,(unsigned,long,const void*,unsigned))
 SGL(void,GenTextures,(int,unsigned*)) SGL(void,BindTexture,(unsigned,unsigned)) SGL(void,ActiveTexture,(unsigned))
 SGL(void,TexImage2D,(unsigned,int,int,int,int,int,unsigned,unsigned,const void*)) SGL(void,TexParameteri,(unsigned,unsigned,int)) SGL(void,GenerateMipmap,(unsigned))
 SGL(void,GenFramebuffers,(int,unsigned*)) SGL(void,BindFramebuffer,(unsigned,unsigned)) SGL(void,FramebufferTexture2D,(unsigned,unsigned,unsigned,unsigned,int)) SGL(unsigned,CheckFramebufferStatus,(unsigned))
 SGL(void,GenRenderbuffers,(int,unsigned*)) SGL(void,BindRenderbuffer,(unsigned,unsigned)) SGL(void,RenderbufferStorage,(unsigned,unsigned,int,int)) SGL(void,FramebufferRenderbuffer,(unsigned,unsigned,unsigned,unsigned))
 SGL(void,Viewport,(int,int,int,int)) SGL(void,Enable,(unsigned)) SGL(void,Disable,(unsigned)) SGL(B,IsEnabled,(unsigned))
 SGL(void,GetBooleanv,(unsigned,B*)) SGL(void,GetFloatv,(unsigned,float*)) SGL(const B*,GetString,(unsigned))
 SGL(void,ClearColor,(float,float,float,float)) SGL(void,ClearDepthf,(float)) SGL(void,Clear,(unsigned)) SGL(void,DepthMask,(B)) SGL(void,DepthFunc,(unsigned)) SGL(void,ColorMask,(B,B,B,B))
 SGL(void,BlendColor,(float,float,float,float)) SGL(void,BlendFuncSeparate,(unsigned,unsigned,unsigned,unsigned)) SGL(void,BlendEquationSeparate,(unsigned,unsigned))
 SGL(void,VertexAttribPointer,(unsigned,int,unsigned,B,int,const void*)) SGL(void,EnableVertexAttribArray,(unsigned)) SGL(void,DisableVertexAttribArray,(unsigned))
 SGL(void,GetVertexAttribiv,(unsigned,unsigned,int*)) SGL(void,GetVertexAttribPointerv,(unsigned,unsigned,void**))
 SGL(void,DrawElements,(unsigned,int,unsigned,const void*)) SGL(void,DrawArrays,(unsigned,int,int)) SGL(void,Uniform1i,(int,int))
 SGL(void,GenVertexArrays,(int,unsigned*)) SGL(void,BindVertexArray,(unsigned))
#undef SGL
};
static SpaceGL spaceGL;static bool spaceGLLoaded,space3DFailed,spaceUseVAO;
// Legacy compositor names are also used by retained system-video frames.
static unsigned shipCompositeProgram;static int shipCompositeMVP,shipCompositeOpacity;
static unsigned cloudProgram,cloudFBO,cloudColor,cloudQuadVBO,cloudVAO;
static int cloudLastFrame=-1;
static int cloudTime,cloudAspect,cloudVanishingPoint,cloudTravel,cloudDiagonal;static float cloudLastAspect=0;
static void*space3DContext;
static void*currentSpace3DContext(){
 static void*(*get)();
 if(!get)get=(void*(*)())dlsym(dlopen("libEGL.so",2),"eglGetCurrentContext");
 return get?get():nullptr;
}
static bool loadSpaceGL(){
 if(spaceGLLoaded)return true;if(!loadLaserGL())return false;void*lib=dlopen("libGLESv2.so",2);if(!lib)return false;
#define LOAD_SGL(N) spaceGL.N=(decltype(spaceGL.N))dlsym(lib,"gl" #N);if(!spaceGL.N)return false;
 LOAD_SGL(GenBuffers) LOAD_SGL(BindBuffer) LOAD_SGL(BufferData) LOAD_SGL(GenTextures) LOAD_SGL(BindTexture) LOAD_SGL(ActiveTexture)
 LOAD_SGL(TexImage2D) LOAD_SGL(TexParameteri) LOAD_SGL(GenerateMipmap) LOAD_SGL(GenFramebuffers) LOAD_SGL(BindFramebuffer) LOAD_SGL(FramebufferTexture2D) LOAD_SGL(CheckFramebufferStatus)
 LOAD_SGL(GenRenderbuffers) LOAD_SGL(BindRenderbuffer) LOAD_SGL(RenderbufferStorage) LOAD_SGL(FramebufferRenderbuffer)
 LOAD_SGL(Viewport) LOAD_SGL(Enable) LOAD_SGL(Disable) LOAD_SGL(IsEnabled) LOAD_SGL(GetBooleanv) LOAD_SGL(GetFloatv) LOAD_SGL(GetString)
 LOAD_SGL(ClearColor) LOAD_SGL(ClearDepthf) LOAD_SGL(Clear) LOAD_SGL(DepthMask) LOAD_SGL(DepthFunc) LOAD_SGL(ColorMask)
 LOAD_SGL(BlendColor) LOAD_SGL(BlendFuncSeparate) LOAD_SGL(BlendEquationSeparate) LOAD_SGL(VertexAttribPointer) LOAD_SGL(EnableVertexAttribArray) LOAD_SGL(DisableVertexAttribArray)
 LOAD_SGL(GetVertexAttribiv) LOAD_SGL(GetVertexAttribPointerv) LOAD_SGL(DrawElements) LOAD_SGL(DrawArrays) LOAD_SGL(Uniform1i)
#undef LOAD_SGL
 spaceGL.GenVertexArrays=(decltype(spaceGL.GenVertexArrays))dlsym(lib,"glGenVertexArrays");spaceGL.BindVertexArray=(decltype(spaceGL.BindVertexArray))dlsym(lib,"glBindVertexArray");
 const char*version=(const char*)spaceGL.GetString(0x1f02);spaceUseVAO=version&&starts(version,"OpenGL ES 3")&&spaceGL.GenVertexArrays&&spaceGL.BindVertexArray;
 spaceGLLoaded=true;return true;
}
struct SpaceState {
 int program,fbo,rbo,array,element,active,texture[4],viewport[4],vao;int blend[6],depthFunc;float clear[4],clearDepth,blendColor[4];B depthWrite,colorWrite[4],enabled[6];
 struct Attribute{int enable,size,type,normalized,stride,buffer;void*pointer;}attributes[4];
 static constexpr unsigned caps[6]={0x0b71,0x0be2,0x0b44,0x0c11,0x809e,0x0bd0};
 SpaceState(){auto&g=laserGL;auto&s=spaceGL;
  g.GetIntegerv(0x8b8d,&program);g.GetIntegerv(0x8ca6,&fbo);g.GetIntegerv(0x8ca7,&rbo);g.GetIntegerv(0x8894,&array);g.GetIntegerv(0x8895,&element);g.GetIntegerv(0x84e0,&active);g.GetIntegerv(0x0ba2,viewport);
  for(int i=0;i<4;i++){s.ActiveTexture(0x84c0+i);g.GetIntegerv(0x8069,&texture[i]);}s.ActiveTexture(active);
  for(int i=0;i<6;i++)enabled[i]=s.IsEnabled(caps[i]);
  unsigned blendNames[]={0x80c9,0x80c8,0x80cb,0x80ca,0x8009,0x883d};for(int i=0;i<6;i++)g.GetIntegerv(blendNames[i],&blend[i]);
  g.GetIntegerv(0x0b74,&depthFunc);s.GetBooleanv(0x0b72,&depthWrite);s.GetBooleanv(0x0c23,colorWrite);s.GetFloatv(0x0c22,clear);s.GetFloatv(0x0b73,&clearDepth);s.GetFloatv(0x8005,blendColor);
  if(spaceUseVAO)g.GetIntegerv(0x85b5,&vao);else for(int i=0;i<4;i++){auto&a=attributes[i];s.GetVertexAttribiv(i,0x8622,&a.enable);s.GetVertexAttribiv(i,0x8623,&a.size);s.GetVertexAttribiv(i,0x8625,&a.type);s.GetVertexAttribiv(i,0x886a,&a.normalized);s.GetVertexAttribiv(i,0x8624,&a.stride);s.GetVertexAttribiv(i,0x889f,&a.buffer);s.GetVertexAttribPointerv(i,0x8645,&a.pointer);}
 }
 ~SpaceState(){auto&g=laserGL;auto&s=spaceGL;
  if(spaceUseVAO)s.BindVertexArray(vao);else for(int i=0;i<4;i++){auto&a=attributes[i];s.BindBuffer(0x8892,a.buffer);s.VertexAttribPointer(i,a.size,a.type,(B)a.normalized,a.stride,a.pointer);if(a.enable)s.EnableVertexAttribArray(i);else s.DisableVertexAttribArray(i);}
  s.BindBuffer(0x8892,array);s.BindBuffer(0x8893,element);
  for(int i=0;i<4;i++){s.ActiveTexture(0x84c0+i);s.BindTexture(0x0de1,texture[i]);}s.ActiveTexture(active);
  s.BindFramebuffer(0x8d40,fbo);s.BindRenderbuffer(0x8d41,rbo);s.Viewport(viewport[0],viewport[1],viewport[2],viewport[3]);
  for(int i=0;i<6;i++)if(enabled[i])s.Enable(caps[i]);else s.Disable(caps[i]);
  s.BlendColor(blendColor[0],blendColor[1],blendColor[2],blendColor[3]);s.BlendFuncSeparate(blend[0],blend[1],blend[2],blend[3]);s.BlendEquationSeparate(blend[4],blend[5]);s.DepthFunc(depthFunc);s.DepthMask(depthWrite);s.ColorMask(colorWrite[0],colorWrite[1],colorWrite[2],colorWrite[3]);s.ClearColor(clear[0],clear[1],clear[2],clear[3]);s.ClearDepthf(clearDepth);g.UseProgram(program);
 }
};
static unsigned compileSpaceProgram(const char*vert,const char*frag,bool composite=false){
 auto&g=laserGL;unsigned stages[2]={};const char*sources[2]={vert,frag};
 for(int i=0;i<2;i++){stages[i]=g.CreateShader(i?0x8b30:0x8b31);g.ShaderSource(stages[i],1,&sources[i],nullptr);g.CompileShader(stages[i]);int ok=0;g.GetShaderiv(stages[i],0x8b81,&ok);if(!ok){char msg[1024]={};g.GetShaderInfoLog(stages[i],1023,nullptr,msg);__android_log_print(6,"TurboCarousel","SPACE3D shader error %s",msg);for(int j=0;j<=i;j++)g.DeleteShader(stages[j]);return 0;}}
 unsigned program=g.CreateProgram();for(auto stage:stages)g.AttachShader(program,stage);
 if(composite){g.BindAttribLocation(program,at<unsigned>((void*)base,0x3cf4bc),"VertexCoord");g.BindAttribLocation(program,at<unsigned>((void*)base,0x3cf4c0),"TexCoord");}
 else{g.BindAttribLocation(program,0,"position");g.BindAttribLocation(program,1,"normal");g.BindAttribLocation(program,2,"tangent");g.BindAttribLocation(program,3,"texcoord");}
 g.LinkProgram(program);for(auto stage:stages)g.DeleteShader(stage);int ok=0;g.GetProgramiv(program,0x8b82,&ok);if(!ok){char msg[1024]={};g.GetProgramInfoLog(program,1023,nullptr,msg);__android_log_print(6,"TurboCarousel","SPACE3D link error %s",msg);g.DeleteProgram(program);return 0;}return program;
}
static bool ensureCloudScene(){
 auto&g=laserGL;auto&s=spaceGL;
 if(cloudProgram&&g.IsProgram(cloudProgram)&&shipCompositeProgram&&g.IsProgram(shipCompositeProgram))return true;
 cloudProgram=compileSpaceProgram(space3d_clouds_vert,space3d_clouds_frag);
 const char*cv="#version 100\nattribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;varying vec2 uv;void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;}";
 const char*cf="#version 100\nprecision mediump float;uniform sampler2D scene;uniform float opacity;varying vec2 uv;void main(){vec4 c=texture2D(scene,uv);if(c.a*opacity<.002)discard;gl_FragColor=vec4(c.rgb/max(c.a,.001),c.a*opacity);}";
 shipCompositeProgram=compileSpaceProgram(cv,cf,true);if(!cloudProgram||!shipCompositeProgram)return false;
 cloudTime=g.GetUniformLocation(cloudProgram,"time");cloudAspect=g.GetUniformLocation(cloudProgram,"aspect");
 cloudVanishingPoint=g.GetUniformLocation(cloudProgram,"vanishingPoint");cloudTravel=g.GetUniformLocation(cloudProgram,"travelDistance");cloudDiagonal=g.GetUniformLocation(cloudProgram,"diagonalBasis");
 shipCompositeOpacity=g.GetUniformLocation(shipCompositeProgram,"opacity");shipCompositeMVP=g.GetUniformLocation(shipCompositeProgram,"MVPMatrix");
 g.UseProgram(shipCompositeProgram);s.Uniform1i(g.GetUniformLocation(shipCompositeProgram,"scene"),0);
 if(spaceUseVAO){s.GenVertexArrays(1,&cloudVAO);s.BindVertexArray(cloudVAO);}
 float quad[]={-1,-1,1,-1,-1,1,1,1};s.GenBuffers(1,&cloudQuadVBO);s.BindBuffer(0x8892,cloudQuadVBO);s.BufferData(0x8892,sizeof(quad),quad,0x88e4);
 s.ActiveTexture(0x84c0);s.GenTextures(1,&cloudColor);s.BindTexture(0x0de1,cloudColor);s.TexImage2D(0x0de1,0,0x1908,320,180,0,0x1908,0x1401,nullptr);
 s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);
 s.GenFramebuffers(1,&cloudFBO);s.BindFramebuffer(0x8d40,cloudFBO);s.FramebufferTexture2D(0x8d40,0x8ce0,0x0de1,cloudColor,0);
 if(s.CheckFramebufferStatus(0x8d40)!=0x8cd5){log("SPACE CLOUDS framebuffer incomplete");return false;}
 cloudLastFrame=-1;log("SPACE CLOUDS ready; 320x180 at 15Hz; aircraft and exhaust removed");return true;
}
static bool renderNativeClouds(float t,float aspect){
 if(space3DFailed||!loadSpaceGL())return false;
 void*context=currentSpace3DContext();int frame=(int)(t*15);
 // Reuse a complete atmosphere frame before capturing GL state.
 if(context&&context==space3DContext&&frame==cloudLastFrame&&aspect==cloudLastAspect&&cloudProgram&&laserGL.IsProgram(cloudProgram))return true;
 SpaceState restore;
 if(context&&context!=space3DContext){cloudProgram=shipCompositeProgram=0;cloudLastFrame=-1;space3DContext=context;}
 if(!ensureCloudScene()){space3DFailed=true;return false;}
 if(frame==cloudLastFrame&&aspect==cloudLastAspect)return true;
 auto&g=laserGL;auto&s=spaceGL;float cloudT=frame/15.f;
 if(spaceUseVAO)s.BindVertexArray(cloudVAO);
 s.BindFramebuffer(0x8d40,cloudFBO);s.Viewport(0,0,320,180);
 s.Disable(0x0c11);s.Disable(0x0be2);s.Disable(0x0b71);s.Disable(0x0b44);s.Disable(0x809e);s.Disable(0x0bd0);s.ColorMask(1,1,1,1);
 g.UseProgram(cloudProgram);g.Uniform1f(cloudTime,cloudT);g.Uniform1f(cloudAspect,aspect);
 // nativeFlight(t) returns travel=.9f*t regardless of its aircraft pose/aspect.
 // Clouds need only that scalar; avoid evaluating the removed aircraft path.
 g.Uniform2f(cloudVanishingPoint,flightVanishingX,flightVanishingY);g.Uniform2f(cloudDiagonal,flightCos(flightDiagonal),flightSin(flightDiagonal));g.Uniform1f(cloudTravel,.9f*cloudT);
 s.BindBuffer(0x8892,cloudQuadVBO);s.EnableVertexAttribArray(0);s.VertexAttribPointer(0,2,0x1406,0,8,nullptr);for(int i=1;i<4;i++)s.DisableVertexAttribArray(i);
 s.DrawArrays(5,0,4);cloudLastFrame=frame;cloudLastAspect=aspect;return true;
}
static void drawNativeClouds(float w,float h,float t){
 if(w<=0||h<=0||!renderNativeClouds(t,w/h))return;auto&g=laserGL;auto&s=spaceGL;int original=0;g.GetIntegerv(0x8b8d,&original);if(!original)return;
 float mvp[16];g.GetUniformfv(original,at<int>((void*)base,0x3cf4c8),mvp);
 int active=0;g.GetIntegerv(0x84e0,&active);s.ActiveTexture(0x84c0);fn<void(*)(unsigned)>(3035880)(0);int texture=0;g.GetIntegerv(0x8069,&texture);s.BindTexture(0x0de1,cloudColor);
 g.UseProgram(shipCompositeProgram);g.UniformMatrix4fv(shipCompositeMVP,1,0,mvp);
 g.Uniform1f(shipCompositeOpacity,1.f);
 Vertex q[4]={{0,0,0,1,0xffffffff},{0,h,0,0,0xffffffff},{w,0,1,1,0xffffffff},{w,h,1,0,0xffffffff}};
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);s.BindTexture(0x0de1,texture);s.ActiveTexture(active);g.UseProgram(original);
}
