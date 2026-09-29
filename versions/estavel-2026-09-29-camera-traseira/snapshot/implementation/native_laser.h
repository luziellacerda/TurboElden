// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Supplied TURBORAMAx laser, rendered in the same native OpenGL ES context as GuiStore.
#include "laser_assets.h"
struct LaserGL {
#define GL_FN(R,N,A) R(*N)A;
 GL_FN(unsigned,CreateShader,(unsigned)) GL_FN(void,ShaderSource,(unsigned,int,const char*const*,const int*))
 GL_FN(void,CompileShader,(unsigned)) GL_FN(void,GetShaderiv,(unsigned,unsigned,int*))
 GL_FN(void,GetShaderInfoLog,(unsigned,int,int*,char*)) GL_FN(void,DeleteShader,(unsigned))
 GL_FN(unsigned,CreateProgram,()) GL_FN(void,AttachShader,(unsigned,unsigned))
 GL_FN(void,BindAttribLocation,(unsigned,unsigned,const char*)) GL_FN(void,LinkProgram,(unsigned))
 GL_FN(void,GetProgramiv,(unsigned,unsigned,int*)) GL_FN(void,GetProgramInfoLog,(unsigned,int,int*,char*))
 GL_FN(void,DeleteProgram,(unsigned)) GL_FN(B,IsProgram,(unsigned))
 GL_FN(void,UseProgram,(unsigned)) GL_FN(void,GetIntegerv,(unsigned,int*))
 GL_FN(int,GetUniformLocation,(unsigned,const char*)) GL_FN(void,GetUniformfv,(unsigned,int,float*))
 GL_FN(void,UniformMatrix4fv,(int,int,B,const float*)) GL_FN(void,Uniform1f,(int,float))
 GL_FN(void,Uniform2f,(int,float,float)) GL_FN(void,Uniform4f,(int,float,float,float,float))
#undef GL_FN
};
static LaserGL laserGL;static unsigned laserProgram;static bool laserGLLoaded,laserFailed;
static int laserMVP,laserPhase,laserHue,laserCore,laserCanvas,laserRect,laserRadius;
static bool loadLaserGL(){
 if(laserGLLoaded)return true;void*lib=dlopen("libGLESv2.so",2);if(!lib)return false;
#define GL_LOAD(N) laserGL.N=(decltype(laserGL.N))dlsym(lib,"gl" #N);if(!laserGL.N)return false;
 GL_LOAD(CreateShader) GL_LOAD(ShaderSource) GL_LOAD(CompileShader) GL_LOAD(GetShaderiv)
 GL_LOAD(GetShaderInfoLog) GL_LOAD(DeleteShader) GL_LOAD(CreateProgram) GL_LOAD(AttachShader)
 GL_LOAD(BindAttribLocation) GL_LOAD(LinkProgram) GL_LOAD(GetProgramiv) GL_LOAD(GetProgramInfoLog)
 GL_LOAD(DeleteProgram) GL_LOAD(IsProgram) GL_LOAD(UseProgram) GL_LOAD(GetIntegerv)
 GL_LOAD(GetUniformLocation) GL_LOAD(GetUniformfv) GL_LOAD(UniformMatrix4fv) GL_LOAD(Uniform1f)
 GL_LOAD(Uniform2f) GL_LOAD(Uniform4f)
#undef GL_LOAD
 laserGLLoaded=true;return true;
}
static unsigned compileLaserStage(unsigned type,const char*prefix){
 auto&g=laserGL;unsigned shader=g.CreateShader(type);const char*parts[]={prefix,laserShaderSource};
 g.ShaderSource(shader,2,parts,nullptr);g.CompileShader(shader);int ok=0;g.GetShaderiv(shader,0x8b81,&ok);
 if(!ok){char message[768]={};g.GetShaderInfoLog(shader,sizeof(message)-1,nullptr,message);__android_log_print(6,"TurboCarousel","LASER shader error: %s",message);g.DeleteShader(shader);return 0;}return shader;
}
static bool ensureLaser(){
 if(laserFailed)return false;
 if(!loadLaserGL()){laserFailed=true;log("LASER OpenGL ES symbols unavailable");return false;}
 auto&g=laserGL;if(laserProgram&&g.IsProgram(laserProgram))return true;
 unsigned vertex=compileLaserStage(0x8b31,"#version 100\n#define VERTEX\n");
 unsigned fragment=compileLaserStage(0x8b30,"#version 100\n#define FRAGMENT\n");
 if(!vertex||!fragment){if(vertex)g.DeleteShader(vertex);if(fragment)g.DeleteShader(fragment);laserFailed=true;return false;}
 laserProgram=g.CreateProgram();g.AttachShader(laserProgram,vertex);g.AttachShader(laserProgram,fragment);
 // Reuse the native renderer's enabled vertex attributes and VBO, without modifying its layout.
 g.BindAttribLocation(laserProgram,at<unsigned>((void*)base,0x3cf4bc),"VertexCoord");
 g.BindAttribLocation(laserProgram,at<unsigned>((void*)base,0x3cf4c0),"TexCoord");
 g.BindAttribLocation(laserProgram,at<unsigned>((void*)base,0x3cf4c4),"COLOR");
 g.LinkProgram(laserProgram);g.DeleteShader(vertex);g.DeleteShader(fragment);int ok=0;g.GetProgramiv(laserProgram,0x8b82,&ok);
 if(!ok){char message[768]={};g.GetProgramInfoLog(laserProgram,sizeof(message)-1,nullptr,message);__android_log_print(6,"TurboCarousel","LASER link error: %s",message);g.DeleteProgram(laserProgram);laserProgram=0;laserFailed=true;return false;}
 laserMVP=g.GetUniformLocation(laserProgram,"MVPMatrix");laserPhase=g.GetUniformLocation(laserProgram,"laserPhase");
 laserHue=g.GetUniformLocation(laserProgram,"laserHue");laserCore=g.GetUniformLocation(laserProgram,"laserCore");
 laserCanvas=g.GetUniformLocation(laserProgram,"canvasSize");laserRect=g.GetUniformLocation(laserProgram,"coverRect");laserRadius=g.GetUniformLocation(laserProgram,"coverRadius");
 log("LASER supplied shader compiled/linked; native GLES; 2600 ms cycle; brighter core and 7px glow; system colors");return true;
}
static void laserColorUniform(int location,unsigned color){laserGL.Uniform4f(location,((color>>24)&255)/255.f,((color>>16)&255)/255.f,((color>>8)&255)/255.f,(color&255)/255.f);}
static void drawFocusLaser(void*p){
 if(at<int>(p,0x370)!=3||paintedCount==0)return;
 int cursor=at<int>(p,0xf0);const CoverRect*card=nullptr;
 for(int i=0;i<paintedCount;i++)if(painted[i].index==cursor)card=&painted[i];
 if(!card)return;
 const char*key=strData((B*)p+0x150);
 if(systemsMode){U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);if(cursor<0||visible+cursor>=end)return;key=strData(items+visible[cursor]*0xe8+0x60);}
 const LaserConfig*config=nullptr;for(const auto&c:laserConfigs)if(strcmp(key,c.key)==0){config=&c;break;}
 if(!config||!ensureLaser())return;
 static const LaserConfig*previous;static int previousCursor=-1;static bool previousMode;static float start;
 float now=at<float>(p,0x194);
 if(previous!=config||previousCursor!=cursor||previousMode!=systemsMode){previous=config;previousCursor=cursor;previousMode=systemsMode;start=now;
  __android_log_print(4,"TurboCarousel","LASER filter=%s; hue=%08x; core=%08x",key,config->hue,config->core);}
 float elapsed=now-start;if(elapsed<0){start=now;elapsed=0;}
 float opacity=elapsed/180.f;if(opacity>1)opacity=1;
 float phase=elapsed>180?(elapsed-180)/2600.f:0;phase-=(int)phase;
 // Preserve the supplied focus LED position/size in its original template coordinate space.
 // The mask follows the current rounded photo, so no rectangle cuts across its pixels.
 const auto&r=*card;float templateW=r.w/.810f,templateH=r.h/.920f;
 float x=r.x+(.053763441f-.095f)*templateW,y=r.y+(-.031617647f-.045f)*templateH;
 float w=.892473118f*templateW,h=1.063235294f*templateH;
 auto&g=laserGL;int original=0;g.GetIntegerv(0x8b8d,&original);if(!original||(unsigned)original==laserProgram)return;
 float mvp[16];g.GetUniformfv(original,at<int>((void*)base,0x3cf4c8),mvp);
 g.UseProgram(laserProgram);g.UniformMatrix4fv(laserMVP,1,0,mvp);
 g.Uniform1f(laserPhase,phase);laserColorUniform(laserHue,config->hue);laserColorUniform(laserCore,config->core);
 g.Uniform2f(laserCanvas,w,h);g.Uniform4f(laserRect,r.x-x,r.y-y,r.w,r.h);g.Uniform1f(laserRadius,cornerRadius(r.w,r.h));
 unsigned color=fn<unsigned(*)(unsigned)>(3029376)(0xffffff00|(unsigned)(opacity*255));
 Vertex q[4]={{x,y,0,1,color},{x,y+h,0,0,color},{x+w,y,1,1,color},{x+w,y+h,1,0,color}};
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);
 g.UseProgram((unsigned)original);
}
