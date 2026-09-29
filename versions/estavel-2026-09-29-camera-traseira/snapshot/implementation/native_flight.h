#pragma once
// Chase view: forward travel is conveyed by the existing stars and clouds.
static constexpr float flightVanishingX=.65f,flightVanishingY=.32f;
static float flightClamp(float x){return x<0?0:(x>1?1:x);}
static float flightSin(float x){static float(*f)(float);if(!f)f=(float(*)(float))dlsym(dlopen("libm.so",2),"sinf");return f?f(x):x;}
static float flightCos(float x){static float(*f)(float);if(!f)f=(float(*)(float))dlsym(dlopen("libm.so",2),"cosf");return f?f(x):1;}
static float flightAtan(float x){static float(*f)(float);if(!f)f=(float(*)(float))dlsym(dlopen("libm.so",2),"atanf");return f?f(x):x*(1-x*x/3);}
static float flightTurn(float phase,float start,float end,float change,float&rate){
 float u=flightClamp((phase-start)/(end-start)),u2=u*u,u3=u2*u;
 rate+=change*30*u2*(u-1)*(u-1)/(end-start);
 return change*u3*(10+u*(-15+6*u));
}
static float flightHeading(float t,float&rate){
 float phase=t-(int)(t/48.f)*48.f;if(phase<0)phase+=48.f;
 rate=0;
 // Small left/right corrections only: the tail stays toward the viewer.
 // Smooth endpoints join the straight segments without position/roll jumps.
 float heading=flightTurn(phase,3,10,.11f,rate);
 heading+=flightTurn(phase,15,27,-.22f,rate);
 heading+=flightTurn(phase,33,41,.11f,rate);
 return heading;
}
struct NativeFlight{float phase,warp,travel,x,y,scale,alpha;bool visible;};
static NativeFlight nativeFlight(float t,float aspect=1.7777778f){
 if(aspect<.5f)aspect=.5f;
 float rate=0,heading=flightHeading(t,rate);
 float height=.34f*aspect;if(height>.72f)height=.72f;
 // Rear camera follows forward. Only the aircraft's lane changes across the
 // screen, synchronised with its modest yaw and bank. No circle/vertical bob.
 return NativeFlight{t,0,.9f*t,flightVanishingX-.9f*heading,.60f,
                     height/(.29f*aspect),1,true};
}
struct NativeAircraftPose{float matrix[16],power,turnRate,bank,pitch;};
static NativeAircraftPose nativeAircraftPose(float t,float aspect=1.7777778f){
 float rate=0,yaw=flightHeading(t,rate);
 float roll=-flightAtan((110.f/9.80665f)*rate);
 float c=flightCos(roll),d=flightSin(roll),load=1.f/c;
 float pitch=-.012f-.10f*(load-1.f);
 float a=flightCos(yaw),b=flightSin(yaw),e=flightCos(pitch),f=flightSin(pitch);
 // One modest correction drives the hull, depth and nozzle together. Camera
 // looks down the aircraft's forward axis; yaw never exceeds +/-6.31 degrees.
 return NativeAircraftPose{{a*c,d,-b*c,0,
                            -a*d*e+b*f,c*e,b*d*e+a*f,0,
                            a*d*f+b*e,-c*f,-b*d*f+a*e,0,
                            0,0,0,1},
                           .73f+.18f*(load-1.f),rate,roll,pitch};
}
