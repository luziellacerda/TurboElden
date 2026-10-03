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
#ifdef GL_ES
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
#endif
varying vec2 v_tex;
varying vec4 v_col;
uniform vec2 canvasSize;
uniform vec4 coverRect;
uniform float coverRadius;
uniform float laserPhase;
uniform vec4 laserHue;
uniform vec4 laserHue2;
uniform vec4 laserCore;
const float HALF_PI=1.57079632679;
// Clockwise true arc length around the same rounded rectangle as the card.
// The old rectangular approximation sped up and jumped through the corner arcs.
float perimeterPosition(vec2 p,vec2 size,float r) {
    float width=size.x-2.0*r,height=size.y-2.0*r,arc=r*HALF_PI;
    if(r>0.01) {
        if(p.y<r && p.x>size.x-r)
            return width+r*atan(max(p.x-size.x+r,0.0001),max(r-p.y,0.0001));
        if(p.y>size.y-r && p.x>size.x-r)
            return width+arc+height+r*atan(max(p.y-size.y+r,0.0001),max(p.x-size.x+r,0.0001));
        if(p.y>size.y-r && p.x<r)
            return 2.0*width+2.0*arc+height+r*atan(max(r-p.x,0.0001),max(p.y-size.y+r,0.0001));
        if(p.y<r && p.x<r)
            return 2.0*width+3.0*arc+2.0*height+r*atan(max(r-p.y,0.0001),max(r-p.x,0.0001));
    }
    float nearest=abs(p.y),along=clamp(p.x-r,0.0,width);
    if(abs(p.x-size.x)<nearest) {
        nearest=abs(p.x-size.x);along=width+arc+clamp(p.y-r,0.0,height);
    }
    if(abs(p.y-size.y)<nearest) {
        nearest=abs(p.y-size.y);along=width+2.0*arc+height+clamp(size.x-r-p.x,0.0,width);
    }
    if(abs(p.x)<nearest)along=2.0*width+3.0*arc+height+clamp(size.y-r-p.y,0.0,height);
    return along;
}
void main(void) {
    vec2 local=vec2(v_tex.x,1.0-v_tex.y)*canvasSize;
    vec2 p=local-coverRect.xy,size=coverRect.zw,halfSize=size*0.5;
    float r=coverRadius,scale=clamp(min(size.x,size.y)/400.0,0.65,1.8);
    vec2 delta=abs(p-halfSize)-(halfSize-vec2(r));
    float sd=length(max(delta,vec2(0.0)))+min(max(delta.x,delta.y),0.0)-r;
    // Outer rim only. Keep a gap so the traveling LED never sits on the artwork.
    if(sd < 1.20*scale || sd > 22.0*scale)discard;
    float mask=smoothstep(1.20*scale,1.80*scale,sd);
    float outward=max(sd,0.0)/scale;
    float perimeter=2.0*(size.x+size.y-4.0*r)+4.0*r*HALF_PI;
    float along=perimeterPosition(p,size,r);
    float behind=fract(laserPhase-along/perimeter)*perimeter;
    float headDistance=min(behind,perimeter-behind);
    float headWidth=14.0*scale;
    float head=exp(-0.5*(headDistance/headWidth)*(headDistance/headWidth));
    // LED on the rim: bright head plus trailing light. Cover interior stays discarded.
    float tail=exp(-behind/(perimeter*0.125))*smoothstep(0.0,4.0*scale,behind);
    tail*=1.0-smoothstep(perimeter*0.25,perimeter*0.40,behind);
    float hot=exp(-0.5*(headDistance/(3.0*scale))*(headDistance/(3.0*scale)));
    vec3 hue=laserHue.a>0.0?laserHue.rgb:vec3(1.0,0.035,0.065);
    if(laserHue2.a>0.0)hue=mix(hue,laserHue2.rgb,smoothstep(0.35,0.65,p.x/size.x));
    // Head stays the cell color. A pale/white core read as a gray pass over the image.
    vec3 core=min(hue*1.38+vec3(0.04),vec3(1.0));
    // Brighter focused light guide, a distinct hot core, and stronger colored halo.
    // All analytic in this pass: no video, texture sample, framebuffer or blur pass.
    float rimDistance=(sd/scale-2.10)/1.15;
    float rim=exp(-0.5*rimDistance*rimDistance);
    float rimAlpha=rim*(0.72+0.22*tail+0.38*head);
    float tightGlow=exp(-outward/4.0)*(0.20+0.45*tail+0.50*head);
    float softGlow=exp(-outward/8.5)*(0.065+0.22*tail+0.30*head);
    float glowAlpha=clamp(tightGlow+softGlow,0.0,0.90);
    glowAlpha*=1.0-smoothstep(16.0,22.0,outward);
    float lineAlpha=clamp(rimAlpha,0.0,0.99);
    vec3 lineColor=mix(hue,core,clamp(0.18+0.32*tail+0.58*head+0.18*hot,0.0,1.0));
    float alpha=lineAlpha+glowAlpha*(1.0-lineAlpha);
    vec3 color=(lineColor*lineAlpha+hue*glowAlpha*(1.0-lineAlpha))/max(alpha,0.0001);
    gl_FragColor=vec4(color,alpha*mask)*v_col;
}
#endif
)LASER";
struct LaserConfig {const char*key;unsigned hue,core,secondary;};
static const LaserConfig laserConfigs[]={
{"3ds",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"Playstation 1",0xDF0024FF,0xFCE6E9FF,0x00000000},
{"Playstation 2",0x153FBFFF,0xE8ECF9FF,0x00000000},
{"Playstation 2 - BR",0x153FBFFF,0xE8ECF9FF,0x00000000},
{"PSP",0x0070FFFF,0xE6F1FFFF,0x00000000},
{"Psvita",0xFFFFFFFF,0xFFFFFFFF,0x0070FFFF},
{"Switch",0x00BCEFFF,0xE6F8FDFF,0xFF303AFF},
{"wii",0xFFFFFFFF,0xFFFFFFFF,0x00000000},
{"wiiu",0x0070FFFF,0xE6F1FFFF,0x00000000},
{"Arcade",0x007BFFFF,0xE6F2FFFF,0x00000000},
{"atari2600",0x965A38FF,0xF4EEEBFF,0x00000000},
{"atari7800",0x965A38FF,0xF4EEEBFF,0x00000000},
{"Atomiswave",0x39EF32FF,0xEBFDEAFF,0x00000000},
{"colecovision",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"cps1",0x27E844FF,0xE9FDECFF,0x00000000},
{"cps2",0xFFD500FF,0xFFFBE6FF,0x0070FFFF},
{"cps3",0x0070FFFF,0xE6F1FFFF,0x00000000},
{"Dreamcast",0xFF6A00FF,0xFFF0E6FF,0x00000000},
{"fds",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"gameandwatch",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"gamegear",0x186CFFFF,0xE6F1FFFF,0x00000000},
{"Gameboy",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"Gba",0x923BFFFF,0xF4EBFFFF,0x00000000},
{"Gameboy Color",0x923BFFFF,0xF4EBFFFF,0x00000000},
{"jaguar",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"mame",0x007BFFFF,0xE6F2FFFF,0x00000000},
{"Master System ",0xFF202AFF,0xFFE9EAFF,0x00000000},
{"MegaDrive",0x186CFFFF,0xE6F1FFFF,0x00000000},
{"MegaDrive - BR",0x186CFFFF,0xE6F1FFFF,0x00000000},
{"model2",0xFF0911FF,0xFFE6E7FF,0x0070FFFF},
{"Nintendo 64",0xFFD500FF,0xFFFBE6FF,0xFFFFFFFF},
{"Nintendo 64 - BR",0xFFD500FF,0xFFFBE6FF,0xFFFFFFFF},
{"Nintendo DS",0xFFFFFFFF,0xFFFFFFFF,0xFF0911FF},
{"Neo Geo",0xE50914FF,0xFCE6E8FF,0x00000000},
{"Neo Geo CD",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"Nintendinho",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"Odyssey 2",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"Pc Engine",0xFF6A00FF,0xFFF0E6FF,0x00000000},
{"Pc Engine cd",0x0070FFFF,0xE6F1FFFF,0x00000000},
{"sega32x",0xFF6A00FF,0xFFF0E6FF,0x00000000},
{"Super Nintendo",0xE50914FF,0xFCE6E8FF,0x00000000},
{"Super Nintendo - BR",0xE50914FF,0xFCE6E8FF,0x00000000},
{"sufami",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"supergrafx",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"fbneo",0xFF0911FF,0xFFE6EBFF,0x00000000},
{"GameCube",0x923BFFFF,0xF4EBFFFF,0x00000000},
{"xbox360",0x39EF32FF,0xEBFDEAFF,0x00000000},
{"saturn",0x186CFFFF,0xE6F1FFFF,0x00000000},
{"xbox",0x39EF32FF,0xEBFDEAFF,0x00000000},
{"Psp - BR",0x0070D1FF,0xE6F1FAFF,0x00000000},
{"naomi",0x186CFFFF,0xE6F1FFFF,0x00000000},
{"naomi2",0xFF0911FF,0xFFE6E7FF,0x0070FFFF},
};
