// Animated highlight on the existing SVG border; never paints over cover pixels.
#if defined(VERTEX)
#if __VERSION__ >= 130
#define VARYING out
#define ATTRIBUTE in
#else
#define VARYING varying
#define ATTRIBUTE attribute
#endif
uniform mat4 MVPMatrix;
ATTRIBUTE vec2 VertexCoord;
ATTRIBUTE vec2 TexCoord;
ATTRIBUTE vec4 COLOR;
VARYING vec2 v_tex;
VARYING vec4 v_col;
void main(void) {
    gl_Position = MVPMatrix * vec4(VertexCoord, 0.0, 1.0);
    v_tex = TexCoord;
    v_col = COLOR;
}
#elif defined(FRAGMENT)
#if __VERSION__ >= 130
#define VARYING in
#define SAMPLE texture
out vec4 FragColor;
#else
#define VARYING varying
#define SAMPLE texture2D
#define FragColor gl_FragColor
#endif
#ifdef GL_ES
precision mediump float;
#endif
VARYING vec2 v_tex;
VARYING vec4 v_col;
uniform vec2 canvasSize;
uniform vec4 coverRect;
uniform float coverRadius;
// Animated by the focus storyboard, not FrameCount: pause and speed follow UI time.
uniform float laserPhase;
uniform vec4 laserHue;
uniform vec4 laserCore;
void main(void) {
    vec2 local=vec2(v_tex.x,1.0-v_tex.y)*canvasSize;
    vec2 halfSize=coverRect.zw*0.5;
    vec2 delta=abs(local-coverRect.xy-halfSize)-(halfSize-vec2(coverRadius));
    float sd=length(max(delta,vec2(0.0)))+min(max(delta.x,delta.y),0.0)-coverRadius;
    float edge=abs(sd);
    float stroke=1.0-smoothstep(1.1,2.5,edge);
    float glow=exp(-edge/7.0)*0.65;
    // Leave the cover interior clear; only the thin outline and outward glow are painted.
    vec4 border=vec4(1.0,1.0,1.0,max(stroke,glow)*smoothstep(-1.5,-0.25,sd));
    // Original SVG: 400x300, border inset 14, width 372, height 272.
    vec2 p = (local-coverRect.xy)/coverRect.zw*vec2(372.0,272.0);
    vec2 q = clamp(p, vec2(0.0), vec2(372.0,272.0));
    float nearest = abs(p.y);
    float along = q.x;
    if (abs(p.x-372.0) < nearest) {
        nearest=abs(p.x-372.0); along=372.0+q.y;
    }
    if (abs(p.y-272.0) < nearest) {
        nearest=abs(p.y-272.0); along=1016.0-q.x;
    }
    if (abs(p.x) < nearest) along=1288.0-q.y;
    float behind = fract(fract(laserPhase)-along/1288.0);
    float headDistance = min(behind,1.0-behind);
    float head = exp(-pow(headDistance/0.014,2.0));
    // A small hot head leads a longer red afterglow, fading only behind it.
    float tail = exp(-behind/0.160)*(1.0-smoothstep(0.28,0.38,behind));
    vec3 hue=laserHue.a>0.0?laserHue.rgb:vec3(1.0,0.035,0.065);
    vec3 core=laserCore.a>0.0?laserCore.rgb:vec3(1.0,0.90,0.92);
    vec3 laserColor = mix(hue,core,min(1.0,head+0.20*tail));
    float alpha = clamp(border.a*(0.32+2.6*tail+4.0*head),0.0,1.0);
    FragColor = vec4(laserColor,alpha)*v_col;
}
#endif
