// Selected game artwork uses the measured TURBORAMAx pixel-light shader.
// The native card owns texture, geometry, animation and alpha. No extra draw loop.
#include "magazine_shader.h"
#include "neogeo_led_profile.h"
struct MagazineProgram {
 unsigned id;void*context;bool failed;bool vertexClassifier;
 int mvp,frame,saturation,color,gain,sheen,model,sampler;
};
static MagazineProgram magazineProgram;
static void(*magazineUniform1i)(int,int);
static void*magazineContext(){
 static void*(*get)();if(!get)get=(void*(*)())dlsym(dlopen("libEGL.so",2),"eglGetCurrentContext");
 return get?get():nullptr;
}
static unsigned compileMagazineStage(unsigned type,const char*prefix,const char*variant,bool canFallback){
 auto&g=laserGL;unsigned shader=g.CreateShader(type);const char*parts[]={prefix,magazineShaderSource};
 g.ShaderSource(shader,2,parts,nullptr);g.CompileShader(shader);int ok=0;g.GetShaderiv(shader,0x8b81,&ok);
 if(!ok){char message[768]={};g.GetShaderInfoLog(shader,sizeof(message)-1,nullptr,message);
  __android_log_print(canFallback?5:6,"TurboCarousel","MAGAZINE %s shader failed; %s: %s",variant,
   canFallback?"trying R104 fallback":"no usable shader variant",message);g.DeleteShader(shader);return 0;}
 return shader;
}
static unsigned linkMagazineProgram(bool vertexClassifier){
 auto&g=laserGL;
 const char*vertexPrefix=vertexClassifier
  ?"#version 100\n#define MAGAZINE_VERTEX_CLASSIFIER\n#define VERTEX\n"
  :"#version 100\n#define VERTEX\n";
 const char*fragmentPrefix=vertexClassifier
  ?"#version 100\n#define MAGAZINE_VERTEX_CLASSIFIER\n#define FRAGMENT\n"
  :"#version 100\n#define FRAGMENT\n";
 const char*variant=vertexClassifier?"vertex-classifier":"R104-fallback";
 unsigned vertex=compileMagazineStage(0x8b31,vertexPrefix,variant,vertexClassifier);
 unsigned fragment=compileMagazineStage(0x8b30,fragmentPrefix,variant,vertexClassifier);
 if(!vertex||!fragment){if(vertex)g.DeleteShader(vertex);if(fragment)g.DeleteShader(fragment);return 0;}
 unsigned program=g.CreateProgram();g.AttachShader(program,vertex);g.AttachShader(program,fragment);
 g.BindAttribLocation(program,at<unsigned>((void*)base,0x3cf4bc),"VertexCoord");
 g.BindAttribLocation(program,at<unsigned>((void*)base,0x3cf4c0),"TexCoord");
 g.BindAttribLocation(program,at<unsigned>((void*)base,0x3cf4c4),"COLOR");
 g.LinkProgram(program);g.DeleteShader(vertex);g.DeleteShader(fragment);int linked=0;g.GetProgramiv(program,0x8b82,&linked);
 if(!linked){char message[768]={};g.GetProgramInfoLog(program,sizeof(message)-1,nullptr,message);
  __android_log_print(vertexClassifier?5:6,"TurboCarousel","MAGAZINE %s link failed; %s: %s",variant,
   vertexClassifier?"trying R104 fallback":"no usable program variant",message);
  g.DeleteProgram(program);return 0;}
 return program;
}
static bool ensureMagazineProgram(){
 if(!loadLaserGL())return false;auto&g=laserGL;auto&p=magazineProgram;
 void*context=magazineContext();if(!context)return false;
 if(p.context!=context){p={};p.context=context;}
 if(p.failed)return false;if(p.id&&g.IsProgram(p.id))return true;
 if(!magazineUniform1i)magazineUniform1i=(void(*)(int,int))dlsym(dlopen("libGLESv2.so",2),"glUniform1i");
 if(!magazineUniform1i){p.failed=true;return false;}
 // GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS.  A zero value makes the optimized
 // variant invalid by definition; compile/link rejection on quirky drivers
 // is also non-fatal because the expression-equivalent R104 path is compiled next.
 int vertexTextureUnits=0;g.GetIntegerv(0x8b4c,&vertexTextureUnits);
 if(vertexTextureUnits>0){p.id=linkMagazineProgram(true);p.vertexClassifier=p.id!=0;}
 if(!p.id){p.id=linkMagazineProgram(false);p.vertexClassifier=false;}
 if(!p.id){p.failed=true;return false;}
 p.mvp=g.GetUniformLocation(p.id,"MVPMatrix");p.frame=g.GetUniformLocation(p.id,"FrameCount");
 p.saturation=g.GetUniformLocation(p.id,"saturation");p.color=g.GetUniformLocation(p.id,"ledColor");
 p.gain=g.GetUniformLocation(p.id,"ledGain");p.sheen=g.GetUniformLocation(p.id,"sheenGain");
 p.model=g.GetUniformLocation(p.id,"magazineModel");p.sampler=g.GetUniformLocation(p.id,"u_tex");
 __android_log_print(4,"TurboCarousel","MAGAZINE selected game art; %s; vertex texture units=%d; R104 fallback preserved",
  p.vertexClassifier?"vertex classifier active":"fragment classifier active",vertexTextureUnits);
 return true;
}
#include "native_magazine_field.h"
static bool prewarmMagazinePrograms(){
 static void*loggedContext=nullptr;void*context=magazineContext();if(!context)return false;
 unsigned started=fn<unsigned(*)()>(0x39e240)();if(!ensureMagazineProgram())return false;
 forgetMagazineFieldContext(context);if(magazineProgram.vertexClassifier&&loadMagazineFieldGL()&&!ensureMagazineFieldPrograms())return false;
 if(loggedContext!=context){loggedContext=context;__android_log_print(4,"TurboCarousel","MAGAZINE programs ready in carousel GL context elapsedMs=%u",fn<unsigned(*)()>(0x39e240)()-started);}
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
 else if(presentationKeyEqual(key,"GameCube")||presentationKeyEqual(key,"Nintendo GameCube")||presentationKeyEqual(key,"gc")){
  model=5;
  // Reuse the actual SNES palette, not a separate GameCube tuning.
  for(const auto&c:laserConfigs)if(strcmp(c.key,"Super Nintendo")==0){hue=c.hue;break;}
 }
 else if(presentationKeyEqual(key,"Wii U")||presentationKeyEqual(key,"Nintendo Wii U")||presentationKeyEqual(key,"wiiu"))model=6;
 else if(presentationKeyEqual(key,"Switch")||presentationKeyEqual(key,"Nintendo Switch")||presentationKeyEqual(key,"nintendoswitch"))model=7;
 else if(presentationKeyEqual(key,"Playstation 1")||presentationKeyEqual(key,"PlayStation")||presentationKeyEqual(key,"ps1")||presentationKeyEqual(key,"psx"))model=8;
 else for(const auto&c:laserConfigs)if(strcmp(c.key,key)==0){hue=c.hue;break;}
 // The cache is an optimization only.  It requires the already-proven R106
 // vertex classifier; any failure falls through to the integral R106 program.
 if(p.vertexClassifier){MagazineFieldStatus field=drawMagazineStaticField(q,count,src,dst,model,hue,matrix);if(field==MAGAZINE_FIELD_READY)return true;if(field==MAGAZINE_FIELD_PENDING)return false;}
 g.UseProgram(p.id);g.UniformMatrix4fv(p.mvp,1,0,matrix);magazineUniform1i(p.sampler,0);
 // 64-bit multiplication preserves whole-millisecond timing through SDL's wrap period.
 unsigned now=fn<unsigned(*)()>(0x39e240)();magazineUniform1i(p.frame,(int)(((U)now*60u)/1000u));
 g.Uniform1f(p.saturation,1.f);g.Uniform1f(p.gain,1.6f);g.Uniform1f(p.sheen,0.f);g.Uniform1f(p.model,model);
 laserColorUniform(p.color,hue);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,count,src,dst);
 g.UseProgram((unsigned)original);return true;
}
