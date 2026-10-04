#pragma once
// Relative flight path: smooth screen travel plus real perspective depth.
// Background travel stays constant; the aircraft moves relative to its chase camera.
// One shared diagonal camera frame for aircraft, stars and cloud rays.
static constexpr float flightVanishingX=.84f,flightVanishingY=.20f;
static constexpr float flightDiagonal=.50f; // Clockwise 28.65 degrees in screen pixels.
static float flightClamp(float x){return x<0?0:(x>1?1:x);}
static float flightLimit(float x,float a,float b){return x<a?a:(x>b?b:x);}
static float flightSin(float x){static float(*f)(float);if(!f)f=(float(*)(float))dlsym(dlopen("libm.so",2),"sinf");return f?f(x):x;}
static float flightCos(float x){static float(*f)(float);if(!f)f=(float(*)(float))dlsym(dlopen("libm.so",2),"cosf");return f?f(x):1;}
static float flightAtan(float x){static float(*f)(float);if(!f)f=(float(*)(float))dlsym(dlopen("libm.so",2),"atanf");return f?f(x):x*(1-x*x/3);}
struct FlightAxis{float position,velocity,acceleration;};
static constexpr float flightKnots[6][3]={
 // Lateral travel in screen-height units, local vertical trim, camera depth.
 {-.08f,.010f,.30f},{.12f,-.010f,.90f},{.23f,.005f,1.10f},
 {.15f,.018f,.60f},{-.12f,.008f,.12f},{-.22f,-.012f,.28f}
};
static FlightAxis flightAxis(float t,int axis){
 constexpr float duration=6.f,cycle=36.f;
 float phase=t-(int)(t/cycle)*cycle;if(phase<0)phase+=cycle;
 int k=(int)(phase/duration);float u=(phase-k*duration)/duration;
 float pm=flightKnots[(k+5)%6][axis],p0=flightKnots[k][axis],p1=flightKnots[(k+1)%6][axis],pp=flightKnots[(k+2)%6][axis];
 float v0=(p1-pm)*.5f,v1=(pp-p0)*.5f,a0=pm-2*p0+p1,a1=p0-2*p1+pp,d=p1-p0;
 // Quintic Hermite: position, velocity and acceleration match at every knot,
 // including the loop seam. There are no stopped endpoints or direction snaps.
 float c0=p0,c1=v0,c2=a0*.5f;
 float c3=10*d-6*v0-4*v1-1.5f*a0+.5f*a1;
 float c4=-15*d+8*v0+7*v1+1.5f*a0-a1;
 float c5=6*d-3*v0-3*v1-.5f*a0+.5f*a1;
 return {c0+u*(c1+u*(c2+u*(c3+u*(c4+u*c5)))),
  (c1+u*(2*c2+u*(3*c3+u*(4*c4+u*5*c5))))/duration,
  (2*c2+u*(6*c3+u*(12*c4+u*20*c5)))/(duration*duration)};
}
static float flightHeading(float t,float&rate){
 auto x=flightAxis(t,0);// The rear camera's screen-right axis points toward negative world X.
 // Negate both yaw and angular rate; the previous sign steered opposite to travel.
 float tangent=-x.velocity*9.f;
 rate=-9.f*x.acceleration/(1.f+tangent*tangent);
 return flightAtan(tangent);
}
static float flightPitch(float t){auto y=flightAxis(t,1);auto z=flightAxis(t,2);return flightLimit(flightAtan(y.velocity*6.f)-.028f*z.velocity,-.15f,.15f);}
static float flightEngineTarget(float t){
 auto depth=flightAxis(t,2);float rate=0;flightHeading(t,rate);
 float turn=rate<0?-rate:rate;
 return flightLimit(.62f+.95f*depth.velocity+.22f*turn,.38f,.96f);
}
static float flightEnginePower(float t){return .18f*flightEngineTarget(t)+.32f*flightEngineTarget(t-.20f)+.32f*flightEngineTarget(t-.45f)+.18f*flightEngineTarget(t-.75f);}
struct NativeFlight{float phase,warp,travel,x,y,scale,alpha;bool visible;};
static NativeFlight nativeFlight(float t,float aspect=1.7777778f){
 if(aspect<.5f)aspect=.5f;
 // Constant composition size; apparent aircraft size changes through real Z
 // translation in the common hull/depth/exhaust pose, not a pulsing bitmap.
 float height=.80f;
 float side=flightAxis(t,0).position,trim=flightAxis(t,1).position,depth=flightAxis(t,2).position;
 float c=flightCos(flightDiagonal),s=flightSin(flightDiagonal);
 // Receding also moves toward the common vanishing point; approaching follows
 // the same ray. Lateral banking remains perpendicular to forward travel.
 float distance=.52f-.055f*depth+trim;
 float x=flightVanishingX+(-s*distance+c*side)/aspect;
 float y=flightVanishingY+c*distance+s*side;
 return {t,0,.9f*t,x,y,height/(.29f*aspect),1,true};
}
struct NativeAircraftPose{float matrix[16],power,turnRate,bank,pitch,pitchRate,powerRate;};
static NativeAircraftPose nativeAircraftPose(float t,float aspect=1.7777778f){
 float rate=0,yaw=flightHeading(t,rate);
 float leadRate=0;flightHeading(t+.12f,leadRate);
 float roll=flightLimit(-flightAtan((30.f/9.80665f)*leadRate),-.55f,.55f);
 float pitch=flightPitch(t),pitchRate=(flightPitch(t+.04f)-flightPitch(t-.04f))/.08f;
 float power=flightEnginePower(t),powerRate=(flightEnginePower(t+.04f)-flightEnginePower(t-.04f))/.08f;
 float c=flightCos(roll),d=flightSin(roll),a=flightCos(yaw),b=flightSin(yaw),e=flightCos(pitch),f=flightSin(pitch);
 float depth=flightAxis(t,2).position;
 // Move along the camera viewing axis: a real near/far perspective change.
 return {{a*c,d,-b*c,0,
          -a*d*e+b*f,c*e,b*d*e+a*f,0,
          a*d*f+b*e,-c*f,-b*d*f+a*e,0,
          0,-.354f*depth,.935f*depth,1},
          power,rate,roll,pitch,pitchRate,powerRate};
}
