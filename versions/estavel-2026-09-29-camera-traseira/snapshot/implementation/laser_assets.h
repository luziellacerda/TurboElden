static const char laserShaderSource[]=R"LASER(// Animated highlight on the existing SVG border; never paints over cover pixels.
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
)LASER";
struct LaserConfig {const char*key;unsigned hue,core;};
static const LaserConfig laserConfigs[]={
{"3ds",0xFF0911FF,0xFFE6EBFF},
{"Playstation 1",0xDF0024FF,0xFCE6E9FF},
{"Playstation 2",0x153FBFFF,0xE8ECF9FF},
{"Playstation 2 - BR",0x153FBFFF,0xE8ECF9FF},
{"PSP",0xFF0911FF,0xFFE6EBFF},
{"Psvita",0xFF0911FF,0xFFE6EBFF},
{"Switch",0xE50914FF,0xFCE6E8FF},
{"wii",0xE50914FF,0xFCE6E8FF},
{"wiiu",0xE50914FF,0xFCE6E8FF},
{"Arcade",0xFF0911FF,0xFFE6EBFF},
{"atari2600",0xFF0911FF,0xFFE6EBFF},
{"atari7800",0xFF0911FF,0xFFE6EBFF},
{"Atomiswave",0x186CFFFF,0xE6F1FFFF},
{"colecovision",0xFF0911FF,0xFFE6EBFF},
{"cps1",0xFF0911FF,0xFFE6EBFF},
{"cps2",0xFF0911FF,0xFFE6EBFF},
{"cps3",0xFF0911FF,0xFFE6EBFF},
{"Dreamcast",0x186CFFFF,0xE6F1FFFF},
{"fds",0xFF0911FF,0xFFE6EBFF},
{"gameandwatch",0xFF0911FF,0xFFE6EBFF},
{"gamegear",0x186CFFFF,0xE6F1FFFF},
{"Gameboy",0xFF0911FF,0xFFE6EBFF},
{"Gba",0xFF0911FF,0xFFE6EBFF},
{"Gameboy Color",0xFF0911FF,0xFFE6EBFF},
{"jaguar",0xFF0911FF,0xFFE6EBFF},
{"mame",0xFF0911FF,0xFFE6EBFF},
{"Master System ",0x186CFFFF,0xE6F1FFFF},
{"MegaDrive",0x186CFFFF,0xE6F1FFFF},
{"MegaDrive - BR",0x186CFFFF,0xE6F1FFFF},
{"model2",0xFF0911FF,0xFFE6EBFF},
{"Nintendo 64",0xE50914FF,0xFCE6E8FF},
{"Nintendo 64 - BR",0xE50914FF,0xFCE6E8FF},
{"Nintendo DS",0xFF0911FF,0xFFE6EBFF},
{"Neo Geo",0xE50914FF,0xFCE6E8FF},
{"Neo Geo CD",0xFF0911FF,0xFFE6EBFF},
{"Nintendinho",0xFF0911FF,0xFFE6EBFF},
{"Odyssey 2",0xFF0911FF,0xFFE6EBFF},
{"Pc Engine",0xFF0911FF,0xFFE6EBFF},
{"Pc Engine cd",0xFF0911FF,0xFFE6EBFF},
{"sega32x",0x186CFFFF,0xE6F1FFFF},
{"Super Nintendo",0xE50914FF,0xFCE6E8FF},
{"Super Nintendo - BR",0xE50914FF,0xFCE6E8FF},
{"sufami",0xFF0911FF,0xFFE6EBFF},
{"supergrafx",0xFF0911FF,0xFFE6EBFF},
{"fbneo",0xFF0911FF,0xFFE6EBFF},
};
