// Static selected-cover lighting field.  The expensive artwork classifier and
// emitter/16-halo kernel are baked once per cover/model/viewport.  Animation,
// palette, gain and compositing remain in the R106 draw shader every frame.
// Any unsupported or incomplete path returns false and executes R106 intact.
struct MagazineFieldGL {
 void(*DeleteTextures)(int,const unsigned*);void(*DeleteFramebuffers)(int,const unsigned*);
 void(*DeleteBuffers)(int,const unsigned*);void(*DeleteVertexArrays)(int,const unsigned*);
 B(*IsTexture)(unsigned);B(*IsFramebuffer)(unsigned);B(*IsBuffer)(unsigned);B(*IsVertexArray)(unsigned);
 void(*GetBufferParameteriv)(unsigned,unsigned,int*);void(*BindSampler)(unsigned,unsigned);void(*Scissor)(int,int,int,int);
};
static MagazineFieldGL magazineFieldGL;
static bool magazineFieldGLLoaded,magazineFieldGLFailed;
struct MagazineFieldCache {
 void*context;unsigned texture,fbo,pendingTexture,pendingFbo,vbo,vao,bakeProgram,drawProgram;
 unsigned source;U identity,uploadRevision;int model,viewport[4],width,height;
 unsigned pendingSource;U pendingIdentity,pendingUploadRevision;int pendingModel,pendingViewport[4],pendingWidth,pendingHeight,pendingRow;unsigned pendingStarted;
 int bakeSampler,bakeModel,drawMvp,drawFrame,drawSaturation,drawColor,drawGain,
     drawSheen,drawModel,drawSampler,drawField;
 bool valid,pending,unsupported,logged,programsLogged;
};
static MagazineFieldCache magazineFieldCache;
static U magazineFieldUploadRevision;
static unsigned magazineFieldObservedSource;
static void invalidateMagazineStaticField(){magazineFieldCache.valid=false;magazineFieldCache.pending=false;magazineFieldCache.source=0;magazineFieldCache.identity=0;magazineFieldCache.pendingSource=0;magazineFieldCache.pendingIdentity=0;magazineFieldObservedSource=0;}
static void noteMagazineSourceTextureUpload(unsigned texture){
 // Renderer can destroy, recycle, or update a GLuint without changing the
 // catalog item. Catalog identity/revision therefore cannot be the only cache
 // key. Invalidate only when that lifetime event targets the exact source used
 // by the committed or currently baking selected cover.
 if(!texture||(texture!=magazineFieldCache.source&&texture!=magazineFieldCache.pendingSource&&texture!=magazineFieldObservedSource))return;
 magazineFieldUploadRevision++;invalidateMagazineStaticField();
}

static bool magazineFieldContains(const char*text,const char*word){
 if(!text||!word||!*word)return false;
 for(;*text;text++){const char*a=text,*b=word;while(*a&&*b&&*a==*b){a++;b++;}if(!*b)return true;}
 return false;
}
static bool loadMagazineFieldGL(){
 if(magazineFieldGLLoaded)return true;if(magazineFieldGLFailed)return false;
 if(!loadSpaceGL())return false;void*lib=dlopen("libGLESv2.so",2);if(!lib){magazineFieldGLFailed=true;return false;}
#define LOAD_MFGL(N) magazineFieldGL.N=(decltype(magazineFieldGL.N))dlsym(lib,"gl" #N);if(!magazineFieldGL.N){magazineFieldGLFailed=true;return false;}
 LOAD_MFGL(DeleteTextures) LOAD_MFGL(DeleteFramebuffers) LOAD_MFGL(DeleteBuffers)
 LOAD_MFGL(IsTexture) LOAD_MFGL(IsFramebuffer) LOAD_MFGL(IsBuffer)
#undef LOAD_MFGL
 magazineFieldGL.DeleteVertexArrays=(decltype(magazineFieldGL.DeleteVertexArrays))dlsym(lib,"glDeleteVertexArrays");
 magazineFieldGL.IsVertexArray=(decltype(magazineFieldGL.IsVertexArray))dlsym(lib,"glIsVertexArray");
 magazineFieldGL.GetBufferParameteriv=(decltype(magazineFieldGL.GetBufferParameteriv))dlsym(lib,"glGetBufferParameteriv");
 magazineFieldGL.BindSampler=(decltype(magazineFieldGL.BindSampler))dlsym(lib,"glBindSampler");
 magazineFieldGL.Scissor=(decltype(magazineFieldGL.Scissor))dlsym(lib,"glScissor");
 if(!magazineFieldGL.Scissor||(spaceUseVAO&&(!magazineFieldGL.DeleteVertexArrays||!magazineFieldGL.IsVertexArray))){magazineFieldGLFailed=true;return false;}
 magazineFieldGLLoaded=true;return true;
}

static void deleteMagazineFieldTarget(unsigned texture,unsigned fbo){
 if(texture)magazineFieldGL.DeleteTextures(1,&texture);if(fbo)magazineFieldGL.DeleteFramebuffers(1,&fbo);
}
// Declared before SpaceState so a retired target is deleted only after the
// caller's bindings have been restored.  Candidate targets are declared after
// SpaceState and are therefore deleted before restoration on every failure.
struct MagazineFieldRetiredTarget {
 unsigned texture=0,fbo=0;
 ~MagazineFieldRetiredTarget(){deleteMagazineFieldTarget(texture,fbo);}
};
struct MagazineFieldTemporaryTarget {
 unsigned texture=0,fbo=0;bool owned=false;
 ~MagazineFieldTemporaryTarget(){if(owned)deleteMagazineFieldTarget(texture,fbo);}
 void commit(){owned=false;}
};
struct MagazineFieldReadFramebufferRestore {
 int read=0;B active=0;
 MagazineFieldReadFramebufferRestore(B enabled):active(enabled){if(active)laserGL.GetIntegerv(0x8caa,&read);}
 ~MagazineFieldReadFramebufferRestore(){if(active)spaceGL.BindFramebuffer(0x8ca8,(unsigned)read);}
};
static unsigned compileMagazineFieldStage(unsigned type,const char*prefix,const char*variant){
 auto&g=laserGL;unsigned shader=g.CreateShader(type);if(!shader){__android_log_print(5,"TurboCarousel","MAGAZINE %s shader allocation failed; using integral R106",variant);return 0;}const char*parts[]={prefix,magazineShaderSource};
 g.ShaderSource(shader,2,parts,nullptr);g.CompileShader(shader);int ok=0;g.GetShaderiv(shader,0x8b81,&ok);
 if(!ok){char message[768]={};g.GetShaderInfoLog(shader,sizeof(message)-1,nullptr,message);
  __android_log_print(5,"TurboCarousel","MAGAZINE %s shader failed; using integral R106: %s",variant,message);g.DeleteShader(shader);return 0;}
 return shader;
}
static unsigned linkMagazineFieldProgram(bool bake){
 auto&g=laserGL;
 const char*vertexPrefix=bake
  ?"#version 100\n#define MAGAZINE_VERTEX_CLASSIFIER\n#define MAGAZINE_FIELD_BAKE\n#define VERTEX\n"
  :"#version 100\n#define MAGAZINE_VERTEX_CLASSIFIER\n#define MAGAZINE_STATIC_FIELD\n#define VERTEX\n";
 const char*fragmentPrefix=bake
  ?"#version 100\n#define MAGAZINE_VERTEX_CLASSIFIER\n#define MAGAZINE_FIELD_BAKE\n#define FRAGMENT\n"
  :"#version 100\n#define MAGAZINE_VERTEX_CLASSIFIER\n#define MAGAZINE_STATIC_FIELD\n#define FRAGMENT\n";
 const char*variant=bake?"field-bake":"field-draw";
 unsigned vertex=compileMagazineFieldStage(0x8b31,vertexPrefix,variant);
 unsigned fragment=compileMagazineFieldStage(0x8b30,fragmentPrefix,variant);
 if(!vertex||!fragment){if(vertex)g.DeleteShader(vertex);if(fragment)g.DeleteShader(fragment);return 0;}
 unsigned program=g.CreateProgram();if(!program){g.DeleteShader(vertex);g.DeleteShader(fragment);return 0;}g.AttachShader(program,vertex);g.AttachShader(program,fragment);
 g.BindAttribLocation(program,at<unsigned>((void*)base,0x3cf4bc),"VertexCoord");
 g.BindAttribLocation(program,at<unsigned>((void*)base,0x3cf4c0),"TexCoord");
 g.BindAttribLocation(program,at<unsigned>((void*)base,0x3cf4c4),"COLOR");
 g.LinkProgram(program);g.DeleteShader(vertex);g.DeleteShader(fragment);int linked=0;g.GetProgramiv(program,0x8b82,&linked);
 if(!linked){char message[768]={};g.GetProgramInfoLog(program,sizeof(message)-1,nullptr,message);
  __android_log_print(5,"TurboCarousel","MAGAZINE %s link failed; using integral R106: %s",variant,message);
  g.DeleteProgram(program);return 0;}
 return program;
}
static void forgetMagazineFieldContext(void*context){
 auto&c=magazineFieldCache;
 if(c.context==context)return;
 // GL objects from a lost context are already invalid and must not be deleted
 // through the replacement context.  Reset every identity and program handle.
 c={};c.context=context;
}
static void releaseMagazineFieldObjects(){
 auto&c=magazineFieldCache;if(!c.context||c.context!=magazineContext()||!loadMagazineFieldGL())return;
 if(c.texture)magazineFieldGL.DeleteTextures(1,&c.texture);
 if(c.fbo)magazineFieldGL.DeleteFramebuffers(1,&c.fbo);
 if(c.pendingTexture)magazineFieldGL.DeleteTextures(1,&c.pendingTexture);
 if(c.pendingFbo)magazineFieldGL.DeleteFramebuffers(1,&c.pendingFbo);
 if(c.vbo)magazineFieldGL.DeleteBuffers(1,&c.vbo);
 if(c.vao&&magazineFieldGL.DeleteVertexArrays)magazineFieldGL.DeleteVertexArrays(1,&c.vao);
 if(c.bakeProgram)laserGL.DeleteProgram(c.bakeProgram);if(c.drawProgram)laserGL.DeleteProgram(c.drawProgram);
 void*context=c.context;c={};c.context=context;
}
static U magazineFieldIdentity(){
 if(!gui)return 0;int cursor=at<int>(gui,0xf0);U*visible=at<U*>(gui,0xf8),*end=at<U*>(gui,0x100);
 if(cursor<0||!visible||visible+cursor>=end)return 0;
 void*catalog=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(catalog,0x88),*finish=at<B*>(catalog,0x90);
 U index=visible[cursor];if(!begin||index>=(U)((finish-begin)/0xe8))return 0;
 B*item=begin+index*0xe8;U hash=1469598103934665603UL;const U offsets[]={0,0x48,0x60,0xc8};
 for(U offset:offsets){for(const char*s=strData(item+offset);*s;s++){hash^=(B)*s;hash*=1099511628211UL;}hash^=0xff;hash*=1099511628211UL;}
 hash^=index;hash*=1099511628211UL;hash^=(U)(unsigned)syncedRevision;hash*=1099511628211UL;return hash?hash:1;
}
static unsigned magazineFieldSourceTexture(){
 auto&g=laserGL;auto&s=spaceGL;int source=0,active=0;g.GetIntegerv(0x84e0,&active);
 s.ActiveTexture(0x84c0);g.GetIntegerv(0x8069,&source);s.ActiveTexture((unsigned)active);
 return (unsigned)source;
}
static bool ensureMagazineFieldPrograms(){
 auto&g=laserGL;auto&c=magazineFieldCache;if(c.unsupported)return false;
 if(c.bakeProgram&&c.drawProgram&&g.IsProgram(c.bakeProgram)&&g.IsProgram(c.drawProgram))return true;
 unsigned started=fn<unsigned(*)()>(0x39e240)();
 c.bakeProgram=linkMagazineFieldProgram(true);c.drawProgram=linkMagazineFieldProgram(false);
 if(!c.bakeProgram||!c.drawProgram){if(c.bakeProgram)g.DeleteProgram(c.bakeProgram);if(c.drawProgram)g.DeleteProgram(c.drawProgram);c.bakeProgram=c.drawProgram=0;c.unsupported=true;return false;}
 c.bakeSampler=g.GetUniformLocation(c.bakeProgram,"u_tex");c.bakeModel=g.GetUniformLocation(c.bakeProgram,"magazineModel");
 c.drawMvp=g.GetUniformLocation(c.drawProgram,"MVPMatrix");c.drawFrame=g.GetUniformLocation(c.drawProgram,"FrameCount");
 c.drawSaturation=g.GetUniformLocation(c.drawProgram,"saturation");c.drawColor=g.GetUniformLocation(c.drawProgram,"ledColor");
 c.drawGain=g.GetUniformLocation(c.drawProgram,"ledGain");c.drawSheen=g.GetUniformLocation(c.drawProgram,"sheenGain");
 c.drawModel=g.GetUniformLocation(c.drawProgram,"magazineModel");c.drawSampler=g.GetUniformLocation(c.drawProgram,"u_tex");
 c.drawField=g.GetUniformLocation(c.drawProgram,"magazineStaticField");
 if(c.bakeSampler<0||c.bakeModel<0||c.drawMvp<0||c.drawFrame<0||c.drawSaturation<0||c.drawColor<0||c.drawGain<0||c.drawModel<0||c.drawSampler<0||c.drawField<0){
  g.DeleteProgram(c.bakeProgram);g.DeleteProgram(c.drawProgram);c.bakeProgram=c.drawProgram=0;c.unsupported=true;
  __android_log_print(5,"TurboCarousel","MAGAZINE static field uniforms incomplete; using integral R106");return false;
 }
 if(!c.programsLogged){c.programsLogged=true;__android_log_print(4,"TurboCarousel","MAGAZINE field programs precompiled elapsedMs=%u",fn<unsigned(*)()>(0x39e240)()-started);}
 return true;
}
static bool magazineFieldDimensions(const int*viewport,int&width,int&height){
 if(!gui||viewport[2]<=0||viewport[3]<=0)return false;
 float guiWidth=at<float>(gui,0x54),guiHeight=at<float>(gui,0x58);if(guiWidth<=0||guiHeight<=0)return false;
 CoverRect target=coverSlot(gui,0);float scaledWidth=target.w*viewport[2]/guiWidth,scaledHeight=target.h*viewport[3]/guiHeight;
 width=(int)(scaledWidth+.999f);height=(int)(scaledHeight+.999f);
 if(width<32)width=32;if(height<32)height=32;if(width>1024)width=1024;if(height>1536)height=1536;
 return true;
}
static void resetMagazineFieldGeometry(){
 auto&c=magazineFieldCache;if(c.vbo)magazineFieldGL.DeleteBuffers(1,&c.vbo);
 if(c.vao&&magazineFieldGL.DeleteVertexArrays)magazineFieldGL.DeleteVertexArrays(1,&c.vao);c.vbo=c.vao=0;
}
static bool magazineFieldQuad(){
 auto&s=spaceGL;auto&c=magazineFieldCache;auto&m=magazineFieldGL;
 unsigned position=at<unsigned>((void*)base,0x3cf4bc),texcoord=at<unsigned>((void*)base,0x3cf4c0),color=at<unsigned>((void*)base,0x3cf4c4);
 if(position>3||texcoord>3||color>3||position==texcoord||position==color||texcoord==color)return false;
 if(spaceUseVAO){if(!c.vao)s.GenVertexArrays(1,&c.vao);if(!c.vao)return false;s.BindVertexArray(c.vao);if(!m.IsVertexArray(c.vao)){resetMagazineFieldGeometry();return false;}}
 if(!c.vbo){const Vertex quad[4]={{-1,-1,0,0,0xffffffff},{-1,1,0,1,0xffffffff},{1,-1,1,0,0xffffffff},{1,1,1,1,0xffffffff}};
  s.GenBuffers(1,&c.vbo);if(!c.vbo)return false;s.BindBuffer(0x8892,c.vbo);if(!m.IsBuffer(c.vbo)){resetMagazineFieldGeometry();return false;}s.BufferData(0x8892,sizeof(quad),quad,0x88e4);}
 else s.BindBuffer(0x8892,c.vbo);
 if(!m.IsBuffer(c.vbo)){resetMagazineFieldGeometry();return false;}
 int bufferBytes=0;m.GetBufferParameteriv(0x8892,0x8764,&bufferBytes);if(bufferBytes!=(int)(sizeof(Vertex)*4)){resetMagazineFieldGeometry();return false;}
 s.EnableVertexAttribArray(position);s.VertexAttribPointer(position,2,0x1406,0,sizeof(Vertex),(const void*)0);
 s.EnableVertexAttribArray(texcoord);s.VertexAttribPointer(texcoord,2,0x1406,0,sizeof(Vertex),(const void*)8);
 s.EnableVertexAttribArray(color);s.VertexAttribPointer(color,4,0x1401,1,sizeof(Vertex),(const void*)16);
 s.DrawArrays(5,0,4);
 return true;
}
struct MagazineFieldCapabilityRestore {
 B stencil,sampleCoverage,rasterDiscard;
 MagazineFieldCapabilityRestore():stencil(spaceGL.IsEnabled(0x0b90)),sampleCoverage(spaceGL.IsEnabled(0x80a0)),rasterDiscard(spaceUseVAO?spaceGL.IsEnabled(0x8c89):0){
  spaceGL.Disable(0x0b90);spaceGL.Disable(0x80a0);if(spaceUseVAO)spaceGL.Disable(0x8c89);
 }
 ~MagazineFieldCapabilityRestore(){
  if(stencil)spaceGL.Enable(0x0b90);else spaceGL.Disable(0x0b90);
  if(sampleCoverage)spaceGL.Enable(0x80a0);else spaceGL.Disable(0x80a0);
  if(spaceUseVAO){if(rasterDiscard)spaceGL.Enable(0x8c89);else spaceGL.Disable(0x8c89);}
 }
};
enum MagazineFieldStatus {MAGAZINE_FIELD_UNSUPPORTED=-1,MAGAZINE_FIELD_PENDING=0,MAGAZINE_FIELD_READY=1};
static bool sameMagazineFieldKey(unsigned source,U identity,U uploadRevision,int modelKey,const int*viewport,int width,int height,bool pending){
 auto&c=magazineFieldCache;bool same=pending?c.pending&&c.pendingSource==source&&c.pendingIdentity==identity&&c.pendingUploadRevision==uploadRevision&&c.pendingModel==modelKey&&c.pendingWidth==width&&c.pendingHeight==height:
  c.valid&&c.source==source&&c.identity==identity&&c.uploadRevision==uploadRevision&&c.model==modelKey&&c.width==width&&c.height==height;
 const int*stored=pending?c.pendingViewport:c.viewport;for(int i=0;i<4&&same;i++)same=stored[i]==viewport[i];return same;
}
static MagazineFieldStatus prepareMagazineStaticField(float model){
 if(!loadMagazineFieldGL())return MAGAZINE_FIELD_UNSUPPORTED;void*context=magazineContext();if(!context)return MAGAZINE_FIELD_UNSUPPORTED;forgetMagazineFieldContext(context);
 auto&g=laserGL;auto&s=spaceGL;auto&c=magazineFieldCache;auto&m=magazineFieldGL;if(c.unsupported||!ensureMagazineFieldPrograms())return MAGAZINE_FIELD_UNSUPPORTED;
 const char*version=(const char*)s.GetString(0x1f02);bool es3=version&&starts(version,"OpenGL ES 3");
 if(!es3||!m.GetBufferParameteriv||!m.BindSampler||!m.Scissor){c.unsupported=true;return MAGAZINE_FIELD_UNSUPPORTED;}
 int viewport[4]={};g.GetIntegerv(0x0ba2,viewport);int width=0,height=0;if(!magazineFieldDimensions(viewport,width,height))return MAGAZINE_FIELD_UNSUPPORTED;
 unsigned source=magazineFieldSourceTexture();U identity=magazineFieldIdentity(),uploadRevision=magazineFieldUploadRevision;int modelKey=(int)(model+.5f);if(!source||!identity)return MAGAZINE_FIELD_UNSUPPORTED;magazineFieldObservedSource=source;
 if(sameMagazineFieldKey(source,identity,uploadRevision,modelKey,viewport,width,height,false))return MAGAZINE_FIELD_READY;
 c.valid=false;c.source=0;c.identity=0;c.model=-1;

 MagazineFieldRetiredTarget retired,failedTarget;MagazineFieldReadFramebufferRestore readRestore(es3);SpaceState restore;MagazineFieldCapabilityRestore extraRestore;
 if(!sameMagazineFieldKey(source,identity,uploadRevision,modelKey,viewport,width,height,true)){
  retired.texture=c.pendingTexture;retired.fbo=c.pendingFbo;c.pendingTexture=c.pendingFbo=0;c.pending=false;
  MagazineFieldTemporaryTarget target;target.owned=true;s.GenTextures(1,&target.texture);s.GenFramebuffers(1,&target.fbo);
  if(!target.texture||!target.fbo){c.unsupported=true;return MAGAZINE_FIELD_UNSUPPORTED;}
  s.ActiveTexture(0x84c1);s.BindTexture(0x0de1,target.texture);if(!m.IsTexture(target.texture)){c.unsupported=true;return MAGAZINE_FIELD_UNSUPPORTED;}
  s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);
  s.TexImage2D(0x0de1,0,0x881a,width,height,0,0x1908,0x140b,nullptr);
  s.BindFramebuffer(0x8d40,target.fbo);if(!m.IsFramebuffer(target.fbo)){c.unsupported=true;return MAGAZINE_FIELD_UNSUPPORTED;}
  s.FramebufferTexture2D(0x8d40,0x8ce0,0x0de1,target.texture,0);if(s.CheckFramebufferStatus(0x8d40)!=0x8cd5){c.unsupported=true;return MAGAZINE_FIELD_UNSUPPORTED;}
  s.Viewport(0,0,width,height);for(unsigned cap:SpaceState::caps)s.Disable(cap);s.ColorMask(1,1,1,1);s.DepthMask(0);s.ClearColor(0,0,0,0);s.Clear(0x00004000);
  c.pendingTexture=target.texture;c.pendingFbo=target.fbo;target.commit();c.pendingSource=source;c.pendingIdentity=identity;c.pendingUploadRevision=uploadRevision;c.pendingModel=modelKey;c.pendingWidth=width;c.pendingHeight=height;c.pendingRow=0;c.pendingStarted=fn<unsigned(*)()>(0x39e240)();c.pending=true;
  for(int i=0;i<4;i++)c.pendingViewport[i]=viewport[i];
  __android_log_print(4,"TurboCarousel","MAGAZINE incremental field start %dx%d model=%d",width,height,modelKey);
 }
 if(!sameMagazineFieldKey(source,identity,uploadRevision,modelKey,viewport,width,height,true))return MAGAZINE_FIELD_PENDING;
 if(c.pendingRow<height){
  int oldScissor[4]={};g.GetIntegerv(0x0c10,oldScissor);B oldScissorEnabled=s.IsEnabled(0x0c11);
  s.BindFramebuffer(0x8d40,c.pendingFbo);s.FramebufferTexture2D(0x8d40,0x8ce0,0x0de1,c.pendingTexture,0);
  if(s.CheckFramebufferStatus(0x8d40)!=0x8cd5){failedTarget.texture=c.pendingTexture;failedTarget.fbo=c.pendingFbo;c.pendingTexture=c.pendingFbo=0;c.pending=false;c.unsupported=true;return MAGAZINE_FIELD_UNSUPPORTED;}
  s.Viewport(0,0,width,height);for(unsigned cap:SpaceState::caps)s.Disable(cap);s.Enable(0x0c11);s.ColorMask(1,1,1,1);s.DepthMask(0);
  const int rows=(height-c.pendingRow)>4?4:(height-c.pendingRow);m.Scissor(0,c.pendingRow,width,rows);
  s.ActiveTexture(0x84c0);s.BindTexture(0x0de1,source);g.UseProgram(c.bakeProgram);s.Uniform1i(c.bakeSampler,0);g.Uniform1f(c.bakeModel,model);
  if(!magazineFieldQuad()){m.Scissor(oldScissor[0],oldScissor[1],oldScissor[2],oldScissor[3]);if(oldScissorEnabled)s.Enable(0x0c11);else s.Disable(0x0c11);resetMagazineFieldGeometry();failedTarget.texture=c.pendingTexture;failedTarget.fbo=c.pendingFbo;c.pendingTexture=c.pendingFbo=0;c.pending=false;c.unsupported=true;return MAGAZINE_FIELD_UNSUPPORTED;}
  m.Scissor(oldScissor[0],oldScissor[1],oldScissor[2],oldScissor[3]);if(oldScissorEnabled)s.Enable(0x0c11);else s.Disable(0x0c11);c.pendingRow+=rows;
 }
 if(magazineFieldUploadRevision!=uploadRevision||!sameMagazineFieldKey(source,identity,uploadRevision,modelKey,viewport,width,height,true)){c.pending=false;return MAGAZINE_FIELD_PENDING;}
 if(c.pendingRow<height)return MAGAZINE_FIELD_PENDING;
 bool captured=c.fbo&&(restore.fbo==(int)c.fbo||(readRestore.active&&readRestore.read==(int)c.fbo));for(int i=0;c.texture&&i<4&&!captured;i++)captured=restore.texture[i]==(int)c.texture;
 if(captured)return MAGAZINE_FIELD_PENDING;
 retired.texture=c.texture;retired.fbo=c.fbo;c.texture=c.pendingTexture;c.fbo=c.pendingFbo;c.pendingTexture=c.pendingFbo=0;c.pending=false;
 c.source=source;c.identity=identity;c.uploadRevision=uploadRevision;c.model=modelKey;c.width=width;c.height=height;c.valid=true;for(int i=0;i<4;i++)c.viewport[i]=viewport[i];
 __android_log_print(4,"TurboCarousel","MAGAZINE incremental field committed slices=%d elapsedMs=%u",(height+3)/4,fn<unsigned(*)()>(0x39e240)()-c.pendingStarted);
 if(!c.logged){c.logged=true;__android_log_print(4,"TurboCarousel","MAGAZINE static RGBA16F field active; animation/color exactly retained");}
 return MAGAZINE_FIELD_READY;
}
static MagazineFieldStatus drawMagazineStaticField(const Vertex*q,unsigned count,int src,int dst,float model,unsigned hue,const float*matrix){
 auto&c=magazineFieldCache;MagazineFieldStatus status=prepareMagazineStaticField(model);if(status!=MAGAZINE_FIELD_READY)return status;
 auto&g=laserGL;auto&s=spaceGL;auto&m=magazineFieldGL;int original=0,active=0,fieldBinding=0,samplerBinding=0;g.GetIntegerv(0x8b8d,&original);g.GetIntegerv(0x84e0,&active);
 s.ActiveTexture(0x84c1);g.GetIntegerv(0x8069,&fieldBinding);g.GetIntegerv(0x8919,&samplerBinding);
 m.BindSampler(1,0);s.BindTexture(0x0de1,c.texture);s.ActiveTexture(0x84c0);g.UseProgram(c.drawProgram);
 g.UniformMatrix4fv(c.drawMvp,1,0,matrix);s.Uniform1i(c.drawSampler,0);s.Uniform1i(c.drawField,1);
 unsigned now=fn<unsigned(*)()>(0x39e240)();s.Uniform1i(c.drawFrame,(int)(((U)now*60u)/1000u));
 g.Uniform1f(c.drawSaturation,1.f);g.Uniform1f(c.drawGain,1.6f);g.Uniform1f(c.drawSheen,0.f);g.Uniform1f(c.drawModel,model);laserColorUniform(c.drawColor,hue);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,count,src,dst);
 s.ActiveTexture(0x84c1);s.BindTexture(0x0de1,(unsigned)fieldBinding);m.BindSampler(1,(unsigned)samplerBinding);s.ActiveTexture((unsigned)active);g.UseProgram((unsigned)original);return MAGAZINE_FIELD_READY;
}
