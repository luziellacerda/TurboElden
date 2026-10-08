// Selected game artwork uses the measured TURBORAMAx pixel-light shader.
// The native card owns texture, geometry, animation and alpha. No extra draw loop.
#include "magazine_shader.h"
#include "neogeo_led_profile.h"
struct MagazineProgram {
 unsigned id;void*context;bool failed;
 int mvp,frame,saturation,color,gain,sheen,model,sampler;
};
static MagazineProgram magazineProgram;
static void(*magazineUniform1i)(int,int);
static void*magazineContext(){
 static void*(*get)();if(!get)get=(void*(*)())dlsym(dlopen("libEGL.so",2),"eglGetCurrentContext");
 return get?get():nullptr;
}
static unsigned compileMagazineStage(unsigned type,const char*prefix){
 auto&g=laserGL;unsigned shader=g.CreateShader(type);const char*parts[]={prefix,magazineShaderSource};
 g.ShaderSource(shader,2,parts,nullptr);g.CompileShader(shader);int ok=0;g.GetShaderiv(shader,0x8b81,&ok);
 if(!ok){char message[768]={};g.GetShaderInfoLog(shader,sizeof(message)-1,nullptr,message);
  __android_log_print(6,"TurboCarousel","MAGAZINE shader failed: %s",message);g.DeleteShader(shader);return 0;}
 return shader;
}
static bool ensureMagazineProgram(){
 if(!loadLaserGL())return false;auto&g=laserGL;auto&p=magazineProgram;
 void*context=magazineContext();if(!context)return false;
 if(p.context!=context){p={};p.context=context;}
 if(p.failed)return false;if(p.id&&g.IsProgram(p.id))return true;
 if(!magazineUniform1i)magazineUniform1i=(void(*)(int,int))dlsym(dlopen("libGLESv2.so",2),"glUniform1i");
 if(!magazineUniform1i){p.failed=true;return false;}
 unsigned vertex=compileMagazineStage(0x8b31,"#version 100\n#define VERTEX\n");
 unsigned fragment=compileMagazineStage(0x8b30,"#version 100\n#define FRAGMENT\n");
 if(!vertex||!fragment){if(vertex)g.DeleteShader(vertex);if(fragment)g.DeleteShader(fragment);p.failed=true;return false;}
 p.id=g.CreateProgram();g.AttachShader(p.id,vertex);g.AttachShader(p.id,fragment);
 g.BindAttribLocation(p.id,at<unsigned>((void*)base,0x3cf4bc),"VertexCoord");
 g.BindAttribLocation(p.id,at<unsigned>((void*)base,0x3cf4c0),"TexCoord");
 g.BindAttribLocation(p.id,at<unsigned>((void*)base,0x3cf4c4),"COLOR");
 g.LinkProgram(p.id);g.DeleteShader(vertex);g.DeleteShader(fragment);int linked=0;g.GetProgramiv(p.id,0x8b82,&linked);
 if(!linked){char message[768]={};g.GetProgramInfoLog(p.id,sizeof(message)-1,nullptr,message);
  __android_log_print(6,"TurboCarousel","MAGAZINE link failed: %s",message);g.DeleteProgram(p.id);p.id=0;p.failed=true;return false;}
 p.mvp=g.GetUniformLocation(p.id,"MVPMatrix");p.frame=g.GetUniformLocation(p.id,"FrameCount");
 p.saturation=g.GetUniformLocation(p.id,"saturation");p.color=g.GetUniformLocation(p.id,"ledColor");
 p.gain=g.GetUniformLocation(p.id,"ledGain");p.sheen=g.GetUniformLocation(p.id,"sheenGain");
 p.model=g.GetUniformLocation(p.id,"magazineModel");p.sampler=g.GetUniformLocation(p.id,"u_tex");
 log("MAGAZINE selected game art; measured PC LED pixels and sheen; monotonic 60Hz-equivalent clock; menu pacing unchanged");
 return true;
}
static bool drawMagazineCover(const Vertex*q,unsigned count,int src,int dst,const char*key){
 if(systemsMode||folderMode||count!=4||!key||!gui||modal(gui)||!ensureMagazineProgram())return false;
 auto&g=laserGL;auto&p=magazineProgram;int original=0;g.GetIntegerv(0x8b8d,&original);
 if(!original||(unsigned)original==p.id)return false;
 float matrix[16];g.GetUniformfv(original,at<int>((void*)base,0x3cf4c8),matrix);
 float model=0;unsigned hue=0xFF1826FF;
 if(presentationKeyEqual(key,"MegaDrive")||presentationKeyEqual(key,"MegaDrive - BR")||
    presentationKeyEqual(key,"megadrive")||presentationKeyEqual(key,"megadrivebr")){model=1;hue=0x186CFFFF;}
 else if(presentationKeyEqual(key,"Nintendo 64")||presentationKeyEqual(key,"Nintendo 64 - BR")||
         presentationKeyEqual(key,"n64")||presentationKeyEqual(key,"n64br"))model=2;
 else if(neoMagazineKey(key))model=3;
 else if(presentationKeyEqual(key,"Dreamcast")||presentationKeyEqual(key,"Sega Dreamcast")){model=4;hue=0xFF4204FF;}
 else for(const auto&c:laserConfigs)if(strcmp(c.key,key)==0){hue=c.hue;break;}
 g.UseProgram(p.id);g.UniformMatrix4fv(p.mvp,1,0,matrix);magazineUniform1i(p.sampler,0);
 // 64-bit multiplication preserves whole-millisecond timing through SDL's wrap period.
 unsigned now=fn<unsigned(*)()>(0x39e240)();magazineUniform1i(p.frame,(int)(((U)now*60u)/1000u));
 g.Uniform1f(p.saturation,1.f);g.Uniform1f(p.gain,1.6f);g.Uniform1f(p.sheen,0.f);g.Uniform1f(p.model,model);
 laserColorUniform(p.color,hue);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,count,src,dst);
 g.UseProgram((unsigned)original);return true;
}
