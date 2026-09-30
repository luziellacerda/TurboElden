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
