// Same draw and same video texture. Applied only to focused Neo Geo CD.
struct NeoSquareProgram{unsigned id;void*context;bool failed;int mvp,phase,transform;};
static NeoSquareProgram neoSquarePrograms[2];
static const char neoSquareVertex[]=R"NEOSQ(#version 100
attribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;varying vec2 uv;void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;})NEOSQ";
static const char neoSquareFragment[]=R"NEOSQ(#version 100
precision highp float;varying vec2 uv;uniform float neoPhase;
// Artwork-space effect for the confirmed Neo Geo CD square PNG and 720p clip.
// Coordinates measured on original 1254x1254, top-left origin.
// One source sample; no new player, draw loop, intermediate image or full-frame bloom.
float neoRoundDistance(vec2 p,vec2 center,vec2 halfSize,float radius){
    vec2 d=abs(p-center)-halfSize+vec2(radius);
    return length(max(d,vec2(0.)))+min(max(d.x,d.y),0.)-radius;
}
float neoSquareMask(vec2 p){
    float rim=1.-smoothstep(5.,13.,abs(neoRoundDistance(p,vec2(623.,627.),vec2(614.,609.),83.)));
    // Printed carousel dots occupy a break in the bottom rail, not an emitter.
    if(p.y>1205.&&p.x>460.&&p.x<765.)rim=0.;
    float left=1.-smoothstep(3.,8.,abs(length(p-vec2(76.,569.))-40.));
    float right=1.-smoothstep(3.,8.,abs(length(p-vec2(1170.,569.))-40.));
    float icons=0.;
    if(p.y>=950.&&p.y<=1044.){
        if((p.x>=53.&&p.x<=149.)||(p.x>=355.&&p.x<=444.)||
           (p.x>=635.&&p.x<=723.)||(p.x>=910.&&p.x<=999.))icons=1.;
    }
    return max(icons,max(rim,max(left,right)));
}
vec3 neoSquareLight(vec3 base,vec2 uv,float phase){
    vec2 p=vec2(uv.x,1.-uv.y)*1254.;
    float mask=neoSquareMask(p);if(mask<=0.)return base;
    float hi=max(base.r,max(base.g,base.b)),lo=min(base.r,min(base.g,base.b));
    float colored=smoothstep(.08,.30,hi-lo)*smoothstep(.20,.75,hi);
    float core=smoothstep(.65,.95,lo);
    float emitter=mask*max(colored,core);
    // Matching SNES/Mega 3.472s vertical travelling light in texture space.
    float behind=fract(phase-(1.-p.y/1254.));
    float d=min(behind,1.-behind);
    float head=exp(-pow(d/.018,2.));
    float tail=exp(-behind/.10)*(1.-smoothstep(.28,.38,behind));
    vec3 hue=base/max(hi,.001);
    vec3 light=mix(hue,vec3(1.),head*.30);
    float power=emitter*(.15+1.45*tail+2.4*head);
    // Smooth highlight shoulder avoids clipped white blocks on compressed video.
    float gain=.85*(1.-exp(-power*.75));
    return 1.-(1.-base)*(1.-light*gain);
}

uniform sampler2D frame;void main(){vec3 b=texture2D(frame,uv).rgb;gl_FragColor=vec4(neoSquareLight(b,uv,neoPhase),1.);})NEOSQ";
static const char neoSquareExternalFragment[]=R"NEOSQ(#version 100
#extension GL_OES_EGL_image_external : require
precision highp float;varying vec2 uv;uniform float neoPhase;
// Artwork-space effect for the confirmed Neo Geo CD square PNG and 720p clip.
// Coordinates measured on original 1254x1254, top-left origin.
// One source sample; no new player, draw loop, intermediate image or full-frame bloom.
float neoRoundDistance(vec2 p,vec2 center,vec2 halfSize,float radius){
    vec2 d=abs(p-center)-halfSize+vec2(radius);
    return length(max(d,vec2(0.)))+min(max(d.x,d.y),0.)-radius;
}
float neoSquareMask(vec2 p){
    float rim=1.-smoothstep(5.,13.,abs(neoRoundDistance(p,vec2(623.,627.),vec2(614.,609.),83.)));
    // Printed carousel dots occupy a break in the bottom rail, not an emitter.
    if(p.y>1205.&&p.x>460.&&p.x<765.)rim=0.;
    float left=1.-smoothstep(3.,8.,abs(length(p-vec2(76.,569.))-40.));
    float right=1.-smoothstep(3.,8.,abs(length(p-vec2(1170.,569.))-40.));
    float icons=0.;
    if(p.y>=950.&&p.y<=1044.){
        if((p.x>=53.&&p.x<=149.)||(p.x>=355.&&p.x<=444.)||
           (p.x>=635.&&p.x<=723.)||(p.x>=910.&&p.x<=999.))icons=1.;
    }
    return max(icons,max(rim,max(left,right)));
}
vec3 neoSquareLight(vec3 base,vec2 uv,float phase){
    vec2 p=vec2(uv.x,1.-uv.y)*1254.;
    float mask=neoSquareMask(p);if(mask<=0.)return base;
    float hi=max(base.r,max(base.g,base.b)),lo=min(base.r,min(base.g,base.b));
    float colored=smoothstep(.08,.30,hi-lo)*smoothstep(.20,.75,hi);
    float core=smoothstep(.65,.95,lo);
    float emitter=mask*max(colored,core);
    // Matching SNES/Mega 3.472s vertical travelling light in texture space.
    float behind=fract(phase-(1.-p.y/1254.));
    float d=min(behind,1.-behind);
    float head=exp(-pow(d/.018,2.));
    float tail=exp(-behind/.10)*(1.-smoothstep(.28,.38,behind));
    vec3 hue=base/max(hi,.001);
    vec3 light=mix(hue,vec3(1.),head*.30);
    float power=emitter*(.15+1.45*tail+2.4*head);
    // Smooth highlight shoulder avoids clipped white blocks on compressed video.
    float gain=.85*(1.-exp(-power*.75));
    return 1.-(1.-base)*(1.-light*gain);
}

uniform samplerExternalOES frame;uniform mat4 videoTransform;void main(){vec2 src=(videoTransform*vec4(uv,0.,1.)).xy;vec3 b=texture2D(frame,src).rgb;gl_FragColor=vec4(neoSquareLight(b,uv,neoPhase),1.);})NEOSQ";
static bool useNeoSquareProgram(bool external,const float*mvp,const float*transform,unsigned now){
 auto&p=neoSquarePrograms[external?1:0];auto&g=laserGL;
 void*context=videoGLContext();if(!context)return false;
 if(p.context!=context){p={};p.context=context;}
 if(p.failed)return false;
 if(!p.id||!g.IsProgram(p.id)){
  p.id=compileSpaceProgram(neoSquareVertex,external?neoSquareExternalFragment:neoSquareFragment,true);
  if(!p.id){p.failed=true;return false;}
  p.mvp=g.GetUniformLocation(p.id,"MVPMatrix");p.phase=g.GetUniformLocation(p.id,"neoPhase");
  p.transform=g.GetUniformLocation(p.id,"videoTransform");
  g.UseProgram(p.id);spaceGL.Uniform1i(g.GetUniformLocation(p.id,"frame"),0);
 }
 g.UseProgram(p.id);g.UniformMatrix4fv(p.mvp,1,0,mvp);
 g.Uniform1f(p.phase,(now%10417u)/10417.f*3.f);
 if(external)g.UniformMatrix4fv(p.transform,1,0,transform);
 return true;
}
