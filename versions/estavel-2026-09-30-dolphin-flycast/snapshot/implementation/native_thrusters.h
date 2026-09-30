// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// GPU exhaust: soft plasma, shock cells and advected smoke behind the two native ship nozzles.
static unsigned thrusterProgram;static int thrusterMVP,thrusterParams;static bool thrusterFailed;
static const char*thrusterVertex=R"GLSL(#version 100
attribute vec4 VertexCoord;
attribute vec2 TexCoord;
uniform mat4 MVPMatrix;
varying vec2 uv;
void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;}
)GLSL";
static const char*thrusterFragment=R"GLSL(#version 100
precision highp float;
varying vec2 uv;
uniform vec4 motion;
float hash3(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float noise3(vec3 p){
 vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(hash3(i),hash3(i+vec3(1,0,0)),f.x),mix(hash3(i+vec3(0,1,0)),hash3(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash3(i+vec3(0,0,1)),hash3(i+vec3(1,0,1)),f.x),mix(hash3(i+vec3(0,1,1)),hash3(i+vec3(1,1,1)),f.x),f.y),f.z);
}
void main(){
 float x=(uv.x-.5)*2.,y=uv.y,t=motion.x,boost=motion.y;
 float jetEnd=.52+boost*.14;
 float entry=smoothstep(0.,.018,y),endFade=1.-smoothstep(.79,1.,y);
 vec3 radiance=vec3(0.);float transmittance=1.;
 // Integrate an actual three-dimensional density field front to back through the plume.
 for(int step=0;step<22;step++){
  float z=-1.05+(float(step)+.5)*.10;
  float bend=sin(y*9.-t*4.)*.08*y;
  vec3 samplePoint=vec3(x+bend,y,z);
  vec3 flow=vec3(samplePoint.x*4.,y*10.-t*4.,z*4.+t*.25);
  float turbulence=noise3(flow)*.72+noise3(flow*2.03+vec3(7.1,2.8,9.3))*.28;
  float radial=length(samplePoint.xz);
  float radius=.25+y*.13+(turbulence-.5)*.12*y;
  float envelope=exp(-radial*radial/(radius*radius)*2.4);
  float shock=.80+.20*sin(y*57.-t*14.);
  float jet=envelope*(1.-smoothstep(jetEnd*.42,jetEnd,y))*shock;
  float core=exp(-radial*radial/.014)*(1.-smoothstep(.18,jetEnd*.78,y));
  float smokeRadius=.29+y*.76;
  float smoke=smoothstep(.32,.75,turbulence)*exp(-radial*radial/(smokeRadius*smokeRadius)*2.2);
  smoke*=smoothstep(.18,.49,y)*endFade;
  float density=(jet*4.0+core*3.0+smoke*2.5)*entry;
  float segmentAlpha=1.-exp(-density*.20);
  float edgeLight=clamp(.48-z*.28+turbulence*.20,0.,1.);
  vec3 cloud=mix(vec3(.045,.065,.085),vec3(.43,.51,.58),edgeLight);
  cloud+=vec3(.04,.22,.35)*jet;
  vec3 plasma=mix(vec3(.05,.40,.88),vec3(.52,.91,1.),shock);
  plasma=mix(plasma,vec3(.94,.99,1.),clamp(core*1.8,0.,1.));
  vec3 light=mix(cloud,plasma,clamp(jet*2.+core,0.,1.));
  radiance+=transmittance*segmentAlpha*light;
  transmittance*=1.-segmentAlpha;
  if(transmittance<.015)break;
 }
 float opacity=(1.-transmittance)*motion.z;
 if(opacity<.002)discard;
 gl_FragColor=vec4(radiance/max(1.-transmittance,.001),opacity);
}
)GLSL";
static bool ensureThruster(){
 if(thrusterFailed||!loadLaserGL())return false;auto&g=laserGL;
 if(thrusterProgram&&g.IsProgram(thrusterProgram))return true;
 unsigned shaders[2]={};const char*texts[2]={thrusterVertex,thrusterFragment};
 for(int i=0;i<2;i++){
  shaders[i]=g.CreateShader(i?0x8b30:0x8b31);g.ShaderSource(shaders[i],1,&texts[i],nullptr);g.CompileShader(shaders[i]);
  int ok=0;g.GetShaderiv(shaders[i],0x8b81,&ok);
  if(!ok){char msg[512]={};g.GetShaderInfoLog(shaders[i],511,nullptr,msg);__android_log_print(6,"TurboCarousel","SPACE thruster shader: %s",msg);for(int j=0;j<=i;j++)g.DeleteShader(shaders[j]);thrusterFailed=true;return false;}
 }
 thrusterProgram=g.CreateProgram();for(auto shader:shaders)g.AttachShader(thrusterProgram,shader);
 g.BindAttribLocation(thrusterProgram,at<unsigned>((void*)base,0x3cf4bc),"VertexCoord");
 g.BindAttribLocation(thrusterProgram,at<unsigned>((void*)base,0x3cf4c0),"TexCoord");g.LinkProgram(thrusterProgram);
 for(auto shader:shaders)g.DeleteShader(shader);int ok=0;g.GetProgramiv(thrusterProgram,0x8b82,&ok);
 if(!ok){g.DeleteProgram(thrusterProgram);thrusterProgram=0;thrusterFailed=true;log("SPACE thruster link failed");return false;}
 thrusterMVP=g.GetUniformLocation(thrusterProgram,"MVPMatrix");thrusterParams=g.GetUniformLocation(thrusterProgram,"motion");
 log("SPACE volumetric twin exhaust compiled; 22-step 3D density raymarch; plasma core and expanding smoke");return true;
}
static void drawNativeThruster(float x,float y,float width,float length,float bank,float time,float throttle,float alpha){
 if(alpha<=.01f||!ensureThruster())return;auto&g=laserGL;int original=0;g.GetIntegerv(0x8b8d,&original);if(!original)return;
 float mvp[16];g.GetUniformfv(original,at<int>((void*)base,0x3cf4c8),mvp);
 g.UseProgram(thrusterProgram);g.UniformMatrix4fv(thrusterMVP,1,0,mvp);g.Uniform4f(thrusterParams,time,throttle,alpha,0);
 float cs=spaceCos(bank),sn=spaceSin(bank);Vertex q[4];
 for(int i=0;i<4;i++){float dx=(i<2?-.5f:.5f)*width,dy=(i&1)?length:0;q[i]={x+dx*cs-dy*sn,y+dx*sn+dy*cs,i<2?0.f:1.f,(i&1)?1.f:0.f,0xffffffff};}
 fn<void(*)(unsigned)>(3035880)(0);fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);g.UseProgram((unsigned)original);
}
