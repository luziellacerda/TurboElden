// Generated F16 shaders; use prepare_shaders.py.
static const char* space3d_ship_vert=R"SHIP(#version 100
precision highp float;
const float PI=3.14159265359;
uniform float time;
// One CPU-evaluated pose is shared by hull, depth and nozzle volume.
uniform mat4 aircraftPose;
uniform vec4 aircraftWake; // pitch rate, engine spool rate, reserved
uniform vec4 aircraftDynamics; // engine load, heading rate, bank, pitch
float boost(){return aircraftDynamics.x;}
float turnRate(){return aircraftDynamics.y;}
vec3 shipOffset(){return aircraftPose[3].xyz;}
mat3 shipRotation(){return mat3(aircraftPose[0].xyz,aircraftPose[1].xyz,aircraftPose[2].xyz);}
// Third-person rear view: centered behind the single nozzle, slightly above
// the wings, revealing both TURBORAMA wing marks. The aircraft points away.
vec3 camera(){return vec3(.12,1.65,-4.10);}
vec3 target(){return vec3(0.,.03,.18);}
mat3 cameraBasis(){vec3 z=normalize(camera()-target());vec3 x=normalize(cross(vec3(0.,1.,0.),z));return mat3(x,cross(z,x),z);}
mat3 transpose3(mat3 m){return mat3(m[0][0],m[1][0],m[2][0],m[0][1],m[1][1],m[2][1],m[0][2],m[1][2],m[2][2]);}
vec3 worldFromLocal(vec3 p){return shipRotation()*p+shipOffset();}
vec3 localFromWorld(vec3 p){return transpose3(shipRotation())*(p-shipOffset());}
vec4 project(vec3 p){vec3 v=transpose3(cameraBasis())*(p-camera());float near=.1,far=20.;return vec4(v.xy*2.9,-(far+near)/(far-near)*v.z-2.*far*near/(far-near),-v.z);}
vec3 tone(vec3 c){c=max(c,vec3(0.));c=(c*(2.51*c+.03))/(c*(2.43*c+.59)+.14);return pow(clamp(c,0.,1.),vec3(1./2.2));}

attribute vec3 position;
attribute vec3 normal;
attribute vec4 tangent;
attribute vec2 texcoord;
varying vec3 worldPosition;
varying vec3 worldNormal;
varying vec4 worldTangent;
varying vec2 uv;
void main(){mat3 r=shipRotation();worldPosition=r*position+shipOffset();worldNormal=r*normal;worldTangent=vec4(r*tangent.xyz,tangent.w);uv=texcoord;gl_Position=project(worldPosition);}
)SHIP";
static const char* space3d_ship_frag=R"SHIP(#version 100
precision highp float;
const float PI=3.14159265359;
uniform float time;
// One CPU-evaluated pose is shared by hull, depth and nozzle volume.
uniform mat4 aircraftPose;
uniform vec4 aircraftWake; // pitch rate, engine spool rate, reserved
uniform vec4 aircraftDynamics; // engine load, heading rate, bank, pitch
float boost(){return aircraftDynamics.x;}
float turnRate(){return aircraftDynamics.y;}
vec3 shipOffset(){return aircraftPose[3].xyz;}
mat3 shipRotation(){return mat3(aircraftPose[0].xyz,aircraftPose[1].xyz,aircraftPose[2].xyz);}
// Third-person rear view: centered behind the single nozzle, slightly above
// the wings, revealing both TURBORAMA wing marks. The aircraft points away.
vec3 camera(){return vec3(.12,1.65,-4.10);}
vec3 target(){return vec3(0.,.03,.18);}
mat3 cameraBasis(){vec3 z=normalize(camera()-target());vec3 x=normalize(cross(vec3(0.,1.,0.),z));return mat3(x,cross(z,x),z);}
mat3 transpose3(mat3 m){return mat3(m[0][0],m[1][0],m[2][0],m[0][1],m[1][1],m[2][1],m[0][2],m[1][2],m[2][2]);}
vec3 worldFromLocal(vec3 p){return shipRotation()*p+shipOffset();}
vec3 localFromWorld(vec3 p){return transpose3(shipRotation())*(p-shipOffset());}
vec4 project(vec3 p){vec3 v=transpose3(cameraBasis())*(p-camera());float near=.1,far=20.;return vec4(v.xy*2.9,-(far+near)/(far-near)*v.z-2.*far*near/(far-near),-v.z);}
vec3 tone(vec3 c){c=max(c,vec3(0.));c=(c*(2.51*c+.03))/(c*(2.43*c+.59)+.14);return pow(clamp(c,0.,1.),vec3(1./2.2));}

uniform sampler2D albedoMap;
uniform sampler2D normalMap;
uniform sampler2D ormMap;
uniform sampler2D emissionMap;
varying vec3 worldPosition;
varying vec3 worldNormal;
varying vec4 worldTangent;
varying vec2 uv;
vec3 brdf(vec3 n,vec3 v,vec3 l,vec3 color,float metal,float rough){
 vec3 h=normalize(v+l);float nl=max(dot(n,l),0.),nv=max(dot(n,v),.001),nh=max(dot(n,h),0.),vh=max(dot(v,h),0.);
 float a=rough*rough,a2=a*a;float d=a2/(PI*pow(nh*nh*(a2-1.)+1.,2.));
 float k=(rough+1.)*(rough+1.)/8.;float g=nv/(nv*(1.-k)+k)*nl/(nl*(1.-k)+k);
 vec3 f0=mix(vec3(.04),color,metal);vec3 f=f0+(1.-f0)*pow(1.-vh,5.);
 return ((1.-f)*(1.-metal)*color/PI+d*g*f/max(4.*nv*nl,.001))*nl;
}
vec3 environment(vec3 r,float rough){
 float spread=mix(130.,4.,rough*rough);vec3 e=vec3(.019,.022,.028);
 e+=vec3(.18,.25,.29)*pow(max(dot(r,normalize(vec3(-.8,.3,1.))),0.),2.);
 e+=vec3(4.8,4.7,4.2)*pow(max(dot(r,normalize(vec3(-2.,3.8,-2.))),0.),spread);
 e+=vec3(.30,.65,.43)*pow(max(dot(r,normalize(vec3(3.,1.,2.))),0.),spread*.55);
 return e;
}
float wordmark(vec2 q){
 if(q.x<0.||q.x>1.||q.y<0.||q.y>1.)return 0.;
 return texture2D(emissionMap,(vec2(0.,1824.)+q*vec2(1024.,192.))/2048.).a;
}
void main(){
 vec3 local=localFromWorld(worldPosition);vec3 localN=transpose3(shipRotation())*normalize(worldNormal);
 float kind=abs(worldTangent.w);vec3 tex=texture2D(albedoMap,uv).rgb;vec3 original=pow(tex,vec3(2.2));
 vec3 orm=texture2D(ormMap,uv).rgb;float rough=clamp(orm.g,.2,.85),metal=orm.b,opacity=1.;vec3 base=original;
 if(kind<1.5){
  // The original UV panel/rivet drawing remains. Graphite livery is applied in material space.
  float shade=dot(tex,vec3(.2126,.7152,.0722));
  base=clamp(original,vec3(.008),vec3(.085))*.85;rough=.23+orm.g*.25;metal=.42;
  // Green leading wing accents and tail-tip cap are paint, never emissive outlines.
  float wing=smoothstep(.17,.23,abs(local.x))*(1.-smoothstep(.005,.010,abs(local.z-(.02-abs(local.x)*.31))))*smoothstep(.30,.70,localN.y);
  float tail=smoothstep(.385,.412,local.y)*(1.-smoothstep(.025,.038,abs(local.x)));
  float stripe=max(wing,tail);base=mix(base,vec3(.015,.155,.045),stripe);metal=mix(metal,.1,stripe);
  // Separate shoulder decals: each side has a complete word, with a clear dorsal gap.
  // The source glyph bounds are 1166 x 142. World dimensions restore that 8.21:1 ratio.
  float flank=local.x<0.?-1.:1.;
  vec2 shoulder=vec2(.5-(local.z-.025)*flank/.45,.5+((abs(local.x)-.060)*.8660254-(local.y-.065)*.5)/.05480);
  float side=wordmark(shoulder)*smoothstep(.65,.82,dot(localN,vec3(flank*.5,.8660254,0.)))*smoothstep(.025,.034,abs(local.x))*(1.-smoothstep(.095,.110,abs(local.x)))*smoothstep(.023,.030,local.y);
  float wingText=wordmark(vec2((.665-abs(local.x))/.45,.5-(local.z+.06+.24*abs(local.x))/.054808))*smoothstep(.5,.8,localN.y)*smoothstep(.20,.23,abs(local.x));
  float tailText=wordmark(vec2((-.47-local.z)/.22,1.-((local.y-.25)/.026793+.5)))*smoothstep(.6,.9,abs(localN.x))*smoothstep(.17,.21,local.y);
  float brand=max(side,max(wingText,tailText));base=mix(base,vec3(.57,.62,.58),brand);rough=mix(rough,.48,brand);metal*=1.-brand;
 }else if(kind<2.5){base=vec3(.008,.020,.022);rough=.09;metal=0.;}
 else if(kind<3.5){base=mix(original,vec3(.18,.145,.098),.38);rough=.26+orm.g*.2;metal=.82;}
 else if(kind<4.5){base=original;rough=.67;metal=.12;}
 else {base=original;rough=.35;metal=.2;}
 vec3 n=normalize(worldNormal),t=normalize(worldTangent.xyz);t=normalize(t-n*dot(t,n));
 if(kind<1.5||kind>2.5)n=normalize(mat3(t,normalize(cross(n,t))*sign(worldTangent.w),n)*(texture2D(normalMap,uv).xyz*2.-1.));
 vec3 v=normalize(camera()-worldPosition);
 vec3 light=brdf(n,v,normalize(vec3(-2.,3.8,-2.)),base,metal,rough)*vec3(5.0,4.8,4.5);
 light+=brdf(n,v,normalize(vec3(3.,1.,2.)),base,metal,rough)*vec3(.65,1.25,.91);
 light+=brdf(n,v,normalize(vec3(-3.,.3,1.)),base,metal,rough)*vec3(.32,.50,.65);
 float nv=max(dot(n,v),0.);vec3 f0=mix(vec3(.04),base,metal);vec3 f=f0+(max(vec3(1.-rough),f0)-f0)*pow(1.-nv,5.);
 light+=(base*(1.-metal)*vec3(.09,.10,.11)+environment(reflect(-v,n),rough)*f)*orm.r;
 if(kind>1.5&&kind<2.5){opacity=.32+.62*pow(1.-nv,3.);light+=environment(reflect(-v,n),.065)*.55;}
 if(kind>4.5&&kind<5.5)light+=vec3(1.8,.025,.007);
 if(kind>5.5&&kind<6.5)light+=vec3(.03,1.5,.15);
 if(kind>6.5)light+=vec3(.22,.33,.24)*(.8+.2*sin(time*3.));
 // Warm engine radiation illuminates the metal petals nearest the single aperture.
 float rear=1.-smoothstep(-.73,-.64,local.z);float bore=1.-smoothstep(.038,.068,length(local.xy));
 if(kind>2.5&&kind<3.5)light+=vec3(1.2,.22,.02)*rear*bore*(1.-smoothstep(-.2,.35,dot(normalize(local.xy+vec2(.00001)),localN.xy)))*(.4+boost()*.6);
 gl_FragColor=vec4(tone(light),opacity);
}
)SHIP";
static const char* space3d_plume_vert=R"SHIP(#version 100
precision highp float;
const float PI=3.14159265359;
uniform float time;
// One CPU-evaluated pose is shared by hull, depth and nozzle volume.
uniform mat4 aircraftPose;
uniform vec4 aircraftWake; // pitch rate, engine spool rate, reserved
uniform vec4 aircraftDynamics; // engine load, heading rate, bank, pitch
float boost(){return aircraftDynamics.x;}
float turnRate(){return aircraftDynamics.y;}
vec3 shipOffset(){return aircraftPose[3].xyz;}
mat3 shipRotation(){return mat3(aircraftPose[0].xyz,aircraftPose[1].xyz,aircraftPose[2].xyz);}
// Third-person rear view: centered behind the single nozzle, slightly above
// the wings, revealing both TURBORAMA wing marks. The aircraft points away.
vec3 camera(){return vec3(.12,1.65,-4.10);}
vec3 target(){return vec3(0.,.03,.18);}
mat3 cameraBasis(){vec3 z=normalize(camera()-target());vec3 x=normalize(cross(vec3(0.,1.,0.),z));return mat3(x,cross(z,x),z);}
mat3 transpose3(mat3 m){return mat3(m[0][0],m[1][0],m[2][0],m[0][1],m[1][1],m[2][1],m[0][2],m[1][2],m[2][2]);}
vec3 worldFromLocal(vec3 p){return shipRotation()*p+shipOffset();}
vec3 localFromWorld(vec3 p){return transpose3(shipRotation())*(p-shipOffset());}
vec4 project(vec3 p){vec3 v=transpose3(cameraBasis())*(p-camera());float near=.1,far=20.;return vec4(v.xy*2.9,-(far+near)/(far-near)*v.z-2.*far*near/(far-near),-v.z);}
vec3 tone(vec3 c){c=max(c,vec3(0.));c=(c*(2.51*c+.03))/(c*(2.43*c+.59)+.14);return pow(clamp(c,0.,1.),vec3(1./2.2));}

attribute vec2 position;
varying vec2 uv;
void main(){uv=position;gl_Position=vec4(position,0.,1.);}
)SHIP";
static const char* space3d_plume_frag=R"SHIP(#version 100
precision highp float;
const float PI=3.14159265359;
uniform float time;
// One CPU-evaluated pose is shared by hull, depth and nozzle volume.
uniform mat4 aircraftPose;
uniform vec4 aircraftWake; // pitch rate, engine spool rate, reserved
uniform vec4 aircraftDynamics; // engine load, heading rate, bank, pitch
float boost(){return aircraftDynamics.x;}
float turnRate(){return aircraftDynamics.y;}
vec3 shipOffset(){return aircraftPose[3].xyz;}
mat3 shipRotation(){return mat3(aircraftPose[0].xyz,aircraftPose[1].xyz,aircraftPose[2].xyz);}
// Third-person rear view: centered behind the single nozzle, slightly above
// the wings, revealing both TURBORAMA wing marks. The aircraft points away.
vec3 camera(){return vec3(.12,1.65,-4.10);}
vec3 target(){return vec3(0.,.03,.18);}
mat3 cameraBasis(){vec3 z=normalize(camera()-target());vec3 x=normalize(cross(vec3(0.,1.,0.),z));return mat3(x,cross(z,x),z);}
mat3 transpose3(mat3 m){return mat3(m[0][0],m[1][0],m[2][0],m[0][1],m[1][1],m[2][1],m[0][2],m[1][2],m[2][2]);}
vec3 worldFromLocal(vec3 p){return shipRotation()*p+shipOffset();}
vec3 localFromWorld(vec3 p){return transpose3(shipRotation())*(p-shipOffset());}
vec4 project(vec3 p){vec3 v=transpose3(cameraBasis())*(p-camera());float near=.1,far=20.;return vec4(v.xy*2.9,-(far+near)/(far-near)*v.z-2.*far*near/(far-near),-v.z);}
vec3 tone(vec3 c){c=max(c,vec3(0.));c=(c*(2.51*c+.03))/(c*(2.43*c+.59)+.14);return pow(clamp(c,0.,1.),vec3(1./2.2));}

uniform sampler2D hullDepthMap;
varying vec2 uv;
float hash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
vec2 intersectBox(vec3 ro,vec3 rd,vec3 low,vec3 high){vec3 a=(low-ro)/rd,b=(high-ro)/rd;vec3 mn=min(a,b),mx=max(a,b);return vec2(max(max(mn.x,mn.y),mn.z),min(min(mx.x,mx.y),mx.z));}
void main(){
 mat3 inv=transpose3(shipRotation());vec3 ro=localFromWorld(camera()),rd=normalize(inv*cameraBasis()*normalize(vec3(uv/2.9,-1.)));
 vec2 hit=intersectBox(ro,rd,vec3(-.32,-.30,-1.92),vec3(.32,.30,-.700));
 float hullDistance=dot(texture2D(hullDepthMap,uv*.5+.5).rgb,vec3(1.,1./255.,1./65025.))*20.;hit.y=min(hit.y,hullDistance-.0007);
 if(hit.y<=max(hit.x,0.))discard;
 float start=max(hit.x,0.),stepSize=(hit.y-start)/48.;vec3 sum=vec3(0.);float trans=1.;
 float power=clamp(boost(),.25,1.);
 float reach=.30+.56*power;
 // The exit stays attached to the nozzle. Turbulence and older wake bend only
 // downstream; power is the same delayed engine load used by the flight path.
 for(int i=0;i<48;i++){
  vec3 p=ro+rd*(start+(float(i)+.5)*stepSize);float z=-.70681-p.z;
  if(z<0.)continue;
  float broad=noise(p*vec3(23.,23.,15.)+vec3(.4*time,-.2*time,time*5.4));
  float fine=noise(p*vec3(61.,61.,38.)+vec3(-time*.6,time*.3,time*9.));
  float age=z/(1.45+power);
  vec2 delayed=vec2(-turnRate(),aircraftWake.x)*age*z*.62;
  vec2 eddy=vec2(sin(z*17.-time*4.7+broad*3.),cos(z*13.-time*3.8+fine*2.))*z*z*.035;
  vec2 offset=delayed+eddy;
  float radius=(.033+z*.082)*(.83+.28*power)*(1.+(.42*broad-.21)*smoothstep(.03,.25,z));
  float radial=length(p.xy-offset)/max(radius,.001);
  float core=exp(-radial*radial*2.0);
  float diamonds=.88+.12*cos(z*(58.-9.*power)+broad*.55);
  float tail=1.-smoothstep(reach*.46,reach,z);
  float breakup=mix(1.,smoothstep(.13,.78,broad*.68+fine*.32),smoothstep(.10,.58,z));
  float jet=core*diamonds*tail*(.36+.64*breakup);
  float sheath=exp(-radial*radial*.82)*tail*(.35+.65*fine)*.19;
  float smokeRadius=.044+z*.18;
  float r=length(p.xy-offset*1.45);
  float smoke=exp(-r*r/(smokeRadius*smokeRadius)*2.0)*smoothstep(.28,.60,z)*(1.-smoothstep(.72,1.12,z))*smoothstep(.27,.77,broad)*.12;
  float density=jet*24.+sheath*12.+smoke*5.;
  float alpha=1.-exp(-density*stepSize);
  vec3 blue=vec3(.20,.37,1.18),amber=vec3(1.50,.37,.045);
  vec3 fire=mix(amber,blue,smoothstep(.015,.18,z))*(.57+.45*power);
  fire=mix(fire,vec3(1.70,1.50,1.12),.34*smoothstep(.38,.94,jet));
  vec3 haze=vec3(.075,.09,.12);
  float luminous=jet+sheath;
  vec3 color=mix(haze,fire,luminous/max(luminous+smoke,.001));
  sum+=trans*alpha*color;trans*=1.-alpha;
 }
 float alpha=1.-trans;if(alpha<.003)discard;
 gl_FragColor=vec4(tone(sum/max(alpha,.001)),alpha);
}
)SHIP";
static const char* space3d_depth_vert=R"SHIP(#version 100
precision highp float;
const float PI=3.14159265359;
uniform float time;
// One CPU-evaluated pose is shared by hull, depth and nozzle volume.
uniform mat4 aircraftPose;
uniform vec4 aircraftWake; // pitch rate, engine spool rate, reserved
uniform vec4 aircraftDynamics; // engine load, heading rate, bank, pitch
float boost(){return aircraftDynamics.x;}
float turnRate(){return aircraftDynamics.y;}
vec3 shipOffset(){return aircraftPose[3].xyz;}
mat3 shipRotation(){return mat3(aircraftPose[0].xyz,aircraftPose[1].xyz,aircraftPose[2].xyz);}
// Third-person rear view: centered behind the single nozzle, slightly above
// the wings, revealing both TURBORAMA wing marks. The aircraft points away.
vec3 camera(){return vec3(.12,1.65,-4.10);}
vec3 target(){return vec3(0.,.03,.18);}
mat3 cameraBasis(){vec3 z=normalize(camera()-target());vec3 x=normalize(cross(vec3(0.,1.,0.),z));return mat3(x,cross(z,x),z);}
mat3 transpose3(mat3 m){return mat3(m[0][0],m[1][0],m[2][0],m[0][1],m[1][1],m[2][1],m[0][2],m[1][2],m[2][2]);}
vec3 worldFromLocal(vec3 p){return shipRotation()*p+shipOffset();}
vec3 localFromWorld(vec3 p){return transpose3(shipRotation())*(p-shipOffset());}
vec4 project(vec3 p){vec3 v=transpose3(cameraBasis())*(p-camera());float near=.1,far=20.;return vec4(v.xy*2.9,-(far+near)/(far-near)*v.z-2.*far*near/(far-near),-v.z);}
vec3 tone(vec3 c){c=max(c,vec3(0.));c=(c*(2.51*c+.03))/(c*(2.43*c+.59)+.14);return pow(clamp(c,0.,1.),vec3(1./2.2));}

attribute vec3 position;
varying vec3 worldPosition;
void main(){worldPosition=worldFromLocal(position);gl_Position=project(worldPosition);}
)SHIP";
static const char* space3d_depth_frag=R"SHIP(#version 100
precision highp float;
const float PI=3.14159265359;
uniform float time;
// One CPU-evaluated pose is shared by hull, depth and nozzle volume.
uniform mat4 aircraftPose;
uniform vec4 aircraftWake; // pitch rate, engine spool rate, reserved
uniform vec4 aircraftDynamics; // engine load, heading rate, bank, pitch
float boost(){return aircraftDynamics.x;}
float turnRate(){return aircraftDynamics.y;}
vec3 shipOffset(){return aircraftPose[3].xyz;}
mat3 shipRotation(){return mat3(aircraftPose[0].xyz,aircraftPose[1].xyz,aircraftPose[2].xyz);}
// Third-person rear view: centered behind the single nozzle, slightly above
// the wings, revealing both TURBORAMA wing marks. The aircraft points away.
vec3 camera(){return vec3(.12,1.65,-4.10);}
vec3 target(){return vec3(0.,.03,.18);}
mat3 cameraBasis(){vec3 z=normalize(camera()-target());vec3 x=normalize(cross(vec3(0.,1.,0.),z));return mat3(x,cross(z,x),z);}
mat3 transpose3(mat3 m){return mat3(m[0][0],m[1][0],m[2][0],m[0][1],m[1][1],m[2][1],m[0][2],m[1][2],m[2][2]);}
vec3 worldFromLocal(vec3 p){return shipRotation()*p+shipOffset();}
vec3 localFromWorld(vec3 p){return transpose3(shipRotation())*(p-shipOffset());}
vec4 project(vec3 p){vec3 v=transpose3(cameraBasis())*(p-camera());float near=.1,far=20.;return vec4(v.xy*2.9,-(far+near)/(far-near)*v.z-2.*far*near/(far-near),-v.z);}
vec3 tone(vec3 c){c=max(c,vec3(0.));c=(c*(2.51*c+.03))/(c*(2.43*c+.59)+.14);return pow(clamp(c,0.,1.),vec3(1./2.2));}

varying vec3 worldPosition;
void main(){
 // Store ray distance in RGB8, so this also works with GLES2 without depth-texture extensions.
 float distanceToHull=clamp(length(worldPosition-camera())/20.,0.,.9999);
 vec3 encodedDepth=fract(distanceToHull*vec3(1.,255.,65025.));encodedDepth.xy-=encodedDepth.yz/255.;
 gl_FragColor=vec4(encodedDepth,1.);
}
)SHIP";
static const char* space3d_clouds_vert=R"SHIP(#version 100
precision highp float;
const float PI=3.14159265359;
uniform float time;
// One CPU-evaluated pose is shared by hull, depth and nozzle volume.
uniform mat4 aircraftPose;
uniform vec4 aircraftWake; // pitch rate, engine spool rate, reserved
uniform vec4 aircraftDynamics; // engine load, heading rate, bank, pitch
float boost(){return aircraftDynamics.x;}
float turnRate(){return aircraftDynamics.y;}
vec3 shipOffset(){return aircraftPose[3].xyz;}
mat3 shipRotation(){return mat3(aircraftPose[0].xyz,aircraftPose[1].xyz,aircraftPose[2].xyz);}
// Third-person rear view: centered behind the single nozzle, slightly above
// the wings, revealing both TURBORAMA wing marks. The aircraft points away.
vec3 camera(){return vec3(.12,1.65,-4.10);}
vec3 target(){return vec3(0.,.03,.18);}
mat3 cameraBasis(){vec3 z=normalize(camera()-target());vec3 x=normalize(cross(vec3(0.,1.,0.),z));return mat3(x,cross(z,x),z);}
mat3 transpose3(mat3 m){return mat3(m[0][0],m[1][0],m[2][0],m[0][1],m[1][1],m[2][1],m[0][2],m[1][2],m[2][2]);}
vec3 worldFromLocal(vec3 p){return shipRotation()*p+shipOffset();}
vec3 localFromWorld(vec3 p){return transpose3(shipRotation())*(p-shipOffset());}
vec4 project(vec3 p){vec3 v=transpose3(cameraBasis())*(p-camera());float near=.1,far=20.;return vec4(v.xy*2.9,-(far+near)/(far-near)*v.z-2.*far*near/(far-near),-v.z);}
vec3 tone(vec3 c){c=max(c,vec3(0.));c=(c*(2.51*c+.03))/(c*(2.43*c+.59)+.14);return pow(clamp(c,0.,1.),vec3(1./2.2));}

attribute vec2 position;
varying vec2 uv;
void main(){uv=position;gl_Position=vec4(position,0.,1.);}
)SHIP";
static const char* space3d_clouds_frag=R"SHIP(#version 100
precision highp float;
const float PI=3.14159265359;
uniform float time;
// One CPU-evaluated pose is shared by hull, depth and nozzle volume.
uniform mat4 aircraftPose;
uniform vec4 aircraftWake; // pitch rate, engine spool rate, reserved
uniform vec4 aircraftDynamics; // engine load, heading rate, bank, pitch
float boost(){return aircraftDynamics.x;}
float turnRate(){return aircraftDynamics.y;}
vec3 shipOffset(){return aircraftPose[3].xyz;}
mat3 shipRotation(){return mat3(aircraftPose[0].xyz,aircraftPose[1].xyz,aircraftPose[2].xyz);}
// Third-person rear view: centered behind the single nozzle, slightly above
// the wings, revealing both TURBORAMA wing marks. The aircraft points away.
vec3 camera(){return vec3(.12,1.65,-4.10);}
vec3 target(){return vec3(0.,.03,.18);}
mat3 cameraBasis(){vec3 z=normalize(camera()-target());vec3 x=normalize(cross(vec3(0.,1.,0.),z));return mat3(x,cross(z,x),z);}
mat3 transpose3(mat3 m){return mat3(m[0][0],m[1][0],m[2][0],m[0][1],m[1][1],m[2][1],m[0][2],m[1][2],m[2][2]);}
vec3 worldFromLocal(vec3 p){return shipRotation()*p+shipOffset();}
vec3 localFromWorld(vec3 p){return transpose3(shipRotation())*(p-shipOffset());}
vec4 project(vec3 p){vec3 v=transpose3(cameraBasis())*(p-camera());float near=.1,far=20.;return vec4(v.xy*2.9,-(far+near)/(far-near)*v.z-2.*far*near/(far-near),-v.z);}
vec3 tone(vec3 c){c=max(c,vec3(0.));c=(c*(2.51*c+.03))/(c*(2.43*c+.59)+.14);return pow(clamp(c,0.,1.),vec3(1./2.2));}

// Original procedural atmosphere. No video, image overlay or external texture.
uniform float aspect;
uniform vec2 vanishingPoint;
uniform vec2 diagonalBasis; // cos/sin of the shared clockwise screen roll
uniform float travelDistance;
varying vec2 uv;
float cloudHash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float cloudNoise(vec3 p){
 vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(cloudHash(i),cloudHash(i+vec3(1,0,0)),f.x),mix(cloudHash(i+vec3(0,1,0)),cloudHash(i+vec3(1,1,0)),f.x),f.y),mix(mix(cloudHash(i+vec3(0,0,1)),cloudHash(i+vec3(1,0,1)),f.x),mix(cloudHash(i+vec3(0,1,1)),cloudHash(i+vec3(1,1,1)),f.x),f.y),f.z);
}
float cloudDensity(vec3 p,float lod){
 float broad=cloudNoise(p*vec3(.32,.24,.32)+vec3(17.1,4.7,8.2));
 float top=-.94+(broad-.48)*2.2;
 float vertical=smoothstep(-3.6,-2.5,p.y)*(1.-smoothstep(top-.65,top+.24,p.y));
 // Exactly empty volume contributes zero regardless of the two detail octaves.
 // Keep the broad octave: it defines the same upper cloud boundary as before.
 if(vertical==0.)return 0.;
 float medium=mix(cloudNoise(p*1.17+vec3(8.3,21.7,3.1)),.5,lod*.65);
 // lod is produced by smoothstep, hence belongs to [0,1]. At one, the original
 // mix is exactly the constant .5; no noise evaluation can affect the result.
 float fine=.5;
 if(lod<1.)fine=mix(cloudNoise(p*2.17),.5,lod);
 return max(broad*.64+medium*.25+fine*.11-.50,0.)*8.5*vertical;
}
void main(){
 // Camera and distant banks share the exact native star-field origin and travel clock.
 // Converting the top-left native coordinates once removes the former sideways drift.
 vec2 radial=uv-vec2(vanishingPoint.x*2.-1.,1.-vanishingPoint.y*2.);
 vec3 ro=vec3(0.,1.8,travelDistance);
 vec2 screenRay=radial*vec2(aspect,1.);
 // Inverse screen roll in the shader's Y-up space. Both cloud volumes and mist
 // use this frame; their horizon and flow match the rolled rear-view aircraft.
 vec2 field=vec2(diagonalBasis.x*screenRay.x-diagonalBasis.y*screenRay.y,
                 diagonalBasis.y*screenRay.x+diagonalBasis.x*screenRay.y);
 vec3 rd=normalize(vec3(field,2.9));
 float near=0.,far=0.;
 if(rd.y<-.025){near=max(0.,(-.20-ro.y)/rd.y);far=min(24.,(-3.6-ro.y)/rd.y);}
 float dt=max(0.,far-near)/64.,trans=1.;vec3 light=vec3(0.);
 float jitter=(cloudHash(vec3(floor(gl_FragCoord.xy),19.3))-.5)*.24;
 if(far>near)for(int i=0;i<64;i++){
  float distance=near+(float(i)+.5+jitter)*dt;vec3 p=ro+rd*distance;
  float lod=smoothstep(6.,20.,distance);
  float density=cloudDensity(p,lod)*(1.-smoothstep(18.,24.,distance));
  // For zero density, alpha=1-exp(0)=0: neither light nor trans changes.
  // This skips only invisible work, not occupied samples or ray-march steps.
  if(density==0.)continue;
  float sun=exp(-cloudDensity(p+vec3(-.35,.72,-.22),lod)*2.8);
  float alpha=1.-exp(-density*dt*1.18);
  vec3 shade=mix(vec3(.095,.13,.14),vec3(.63,.69,.67),sun);
  shade=mix(shade,vec3(.18,.24,.25),smoothstep(8.,30.,distance)*.62);
  light+=trans*alpha*shade;trans*=1.-alpha;
 }
 // Distant sheets expand radially toward the edges, with depth-dependent parallax.
 // The haze uses the same diagonal camera rays and forward travel as the volume.
 float phaseA=fract(travelDistance*.006+.21),phaseB=fract(travelDistance*.006+.71);
 float mistA=cloudNoise(vec3(field*mix(7.,1.5,phaseA),31.7));
 float mistB=cloudNoise(vec3(field*mix(7.,1.5,phaseB),52.4));
 float fadeA=smoothstep(0.,.15,phaseA)*(1.-smoothstep(.83,1.,phaseA));
 float fadeB=smoothstep(0.,.15,phaseB)*(1.-smoothstep(.83,1.,phaseB));
 float veil=(smoothstep(.50,.80,mistA)*fadeA+smoothstep(.50,.80,mistB)*fadeB)*.10;
 light+=trans*veil*vec3(.32,.39,.38);trans*=1.-veil;
 // Keep the central synopsis readable without an opaque rectangle or a hard edge.
 vec2 screen=uv*.5+.5;
 float reading=smoothstep(.30,.43,screen.x)*(1.-smoothstep(.73,.83,screen.y))*smoothstep(.16,.32,screen.y);
 float strength=mix(.78,.44,reading);
 gl_FragColor=vec4(light*strength,(1.-trans)*strength); // Premultiplied for native composition.
}
)SHIP";