static const char magazineShaderSource[]=R"NEOMAG(// Selected magazine only. Reference artwork: 1024x1536, top-left coordinates.
// Pixel color gating follows actual cyan emitters inside the measured frame,
// never the blue illustration. Texture-space bloom rotates/scales with the cover.
#if defined(VERTEX)
#if __VERSION__ >= 130
#define ATTR in
#define VARY out
#else
#define ATTR attribute
#define VARY varying
#endif
uniform mat4 MVPMatrix;
ATTR vec2 VertexCoord;
ATTR vec2 TexCoord;
ATTR vec4 COLOR;
VARY vec2 uv;
VARY vec4 tint;
void main() { gl_Position=MVPMatrix*vec4(VertexCoord,0.0,1.0); uv=TexCoord; tint=COLOR; }
#elif defined(FRAGMENT)
#if __VERSION__ >= 130
#define VARY in
#define TEX texture
out vec4 FragColor;
#else
#define VARY varying
#define TEX texture2D
#define FragColor gl_FragColor
#endif
#ifdef GL_ES
precision highp float;
precision highp int;
#endif
VARY vec2 uv;
VARY vec4 tint;
uniform sampler2D u_tex;
uniform int FrameCount;
uniform float saturation;
uniform vec4 ledColor;
uniform float ledGain;
uniform float sheenGain;
// 0: approved SNES map; 1: measured Mega Drive frame;
// 2: measured Nintendo 64 frame. Models 0/1 keep their original light engine.
uniform float magazineModel;
float activeMagazineModel;

float box(vec2 p, vec2 lo, vec2 hi) {
    vec2 a=smoothstep(lo,lo+vec2(3.0),p);
    vec2 b=1.0-smoothstep(hi-vec2(3.0),hi,p);
    return a.x*a.y*b.x*b.y;
}
float segmentMask(vec2 p, vec2 a, vec2 b, float width) {
    vec2 ab=b-a;
    float t=clamp(dot(p-a,ab)/dot(ab,ab),0.0,1.0);
    return 1.0-smoothstep(width,width+3.0,length(p-a-t*ab));
}
float megaRegion(vec2 p) {
    // Original 1024x1536 artwork, not screen pixels. Sixteen main light bars.
    float m=max(box(p,vec2(164,3),vec2(284,35)),box(p,vec2(738,2),vec2(862,35)));
    m=max(m,box(p,vec2(927,64),vec2(1002,91)));
    m=max(m,box(p,vec2(926,115),vec2(1002,142)));
    m=max(m,box(p,vec2(164,185),vec2(268,203)));
    m=max(m,box(p,vec2(763,185),vec2(860,203)));
    m=max(m,box(p,vec2(34,488),vec2(74,635)));
    m=max(m,box(p,vec2(951,488),vec2(990,635)));
    m=max(m,box(p,vec2(34,808),vec2(74,974)));
    m=max(m,box(p,vec2(951,810),vec2(990,974)));
    // Bent lower rails need a path mask, not a box over blue game artwork.
    m=max(m,segmentMask(p,vec2(86,1106),vec2(85,1125),6.0));
    m=max(m,segmentMask(p,vec2(85,1125),vec2(30,1188),6.0));
    m=max(m,segmentMask(p,vec2(30,1188),vec2(30,1206),6.0));
    m=max(m,segmentMask(p,vec2(937,1106),vec2(938,1125),6.0));
    m=max(m,segmentMask(p,vec2(938,1125),vec2(993,1188),6.0));
    m=max(m,segmentMask(p,vec2(993,1188),vec2(993,1195),6.0));
    m=max(m,box(p,vec2(757,1343),vec2(947,1366)));
    m=max(m,box(p,vec2(46,1387),vec2(84,1481)));
    m=max(m,box(p,vec2(493,1389),vec2(533,1470)));
    m=max(m,box(p,vec2(937,1387),vec2(980,1481)));
    // Same treatment as SNES footer icons, never the badge's blue stars.
    m=max(m,box(p,vec2(104,1392),vec2(207,1483)));
    m=max(m,box(p,vec2(594,1404),vec2(677,1474)));
    return m;
}
float discMask(vec2 p, vec2 center, float radius) {
    return 1.0-smoothstep(radius-3.0,radius+3.0,length(p-center));
}
float n64Region(vec2 p) {
    // Original 1024x1536 N64 artwork. Every region below was measured on the
    // shared chassis; game artwork remains outside the mask.
    float m=max(box(p,vec2(160,0),vec2(315,35)),box(p,vec2(708,0),vec2(865,35)));
    m=max(m,box(p,vec2(174,185),vec2(270,203)));
    m=max(m,box(p,vec2(760,185),vec2(856,203)));
    m=max(m,box(p,vec2(887,114),vec2(941,133)));
    m=max(m,box(p,vec2(946,114),vec2(997,133)));
    m=max(m,box(p,vec2(887,137),vec2(941,156)));
    m=max(m,box(p,vec2(946,137),vec2(997,156)));
    m=max(m,discMask(p,vec2(44,235),31.0));
    m=max(m,discMask(p,vec2(980,235),31.0));
    m=max(m,box(p,vec2(18,317),vec2(57,477)));
    m=max(m,box(p,vec2(967,317),vec2(1006,477)));
    m=max(m,box(p,vec2(18,801),vec2(57,946)));
    m=max(m,box(p,vec2(967,801),vec2(1006,946)));
    m=max(m,box(p,vec2(755,1344),vec2(949,1372)));
    m=max(m,discMask(p,vec2(49,1454),31.0));
    m=max(m,discMask(p,vec2(975,1454),31.0));
    m=max(m,box(p,vec2(101,1392),vec2(220,1498)));
    m=max(m,box(p,vec2(602,1395),vec2(726,1498)));
    return m;
}
float neoRegion(vec2 p);
float neoChroma(vec3 c);
float region(vec2 p) {
    if(activeMagazineModel>2.5) return neoRegion(p);
    if(activeMagazineModel>1.5) return n64Region(p);
    if(activeMagazineModel>0.5) return megaRegion(p);
    float m=max(box(p,vec2(45,26),vec2(157,115)),box(p,vec2(860,23),vec2(975,115)));
    m=max(m,box(p,vec2(36,223),vec2(69,356)));
    m=max(m,box(p,vec2(953,223),vec2(989,356)));
    m=max(m,box(p,vec2(34,515),vec2(72,1065)));
    m=max(m,box(p,vec2(953,515),vec2(986,1065)));
    m=max(m,box(p,vec2(34,1187),vec2(73,1298)));
    m=max(m,box(p,vec2(951,1187),vec2(990,1298)));
    // Only the badge rim, not its white lettering or stars.
    float ring=1.0-smoothstep(7.0,16.0,abs(length((p-vec2(794,1200))*vec2(1.0,0.975))-146.0));
    m=max(m,ring);
    m=max(m,box(p,vec2(737,1285),vec2(852,1304)));
    m=max(m,box(p,vec2(108,1395),vec2(213,1491)));
    m=max(m,box(p,vec2(557,1405),vec2(658,1498)));
    return m;
}
vec4 sampleArt(vec2 p) { return TEX(u_tex,vec2(p.x/1024.0,1.0-p.y/1536.0)); }
float blue(vec3 c) {
    return smoothstep(0.08,0.32,c.b-c.r)*smoothstep(0.28,0.78,c.b)*smoothstep(0.08,0.35,c.g);
}
float n64Lamp(vec3 c) {
    float hi=max(c.r,max(c.g,c.b));
    float lo=min(c.r,min(c.g,c.b));
    return smoothstep(0.10,0.34,hi-lo)*smoothstep(0.20,0.72,hi);
}
float lampSample(vec3 c) {
    if(activeMagazineModel>2.5) return neoChroma(c);
    if(activeMagazineModel>1.5) return n64Lamp(c);
    return blue(c);
}
float emitter(vec2 p) {
    if(region(p)<=0.0) return 0.0; // Equivalent zero mask; saves texture reads.
    vec4 c=sampleArt(p);
    float lamp=lampSample(c.rgb);
    // Recover the almost-white hot core only next to a measured colored pixel.
    float neighbor=max(max(lampSample(sampleArt(p+vec2(3,0)).rgb),lampSample(sampleArt(p-vec2(3,0)).rgb)),
                       max(lampSample(sampleArt(p+vec2(0,3)).rgb),lampSample(sampleArt(p-vec2(0,3)).rgb)));
    float channelCore=activeMagazineModel>1.5 ? max(c.r,max(c.g,c.b)) : min(c.g,c.b);
    float core=smoothstep(0.70,0.95,channelCore)*neighbor;
    return max(lamp,core)*region(p)*c.a;
}
vec4 lightEnvelope(vec2 p) {
    // One head/clock for both effects and both sides of the frame. Keep the
    // approved contour sweep speed; 625 frames are exactly three full passes.
    float t=float(FrameCount-((FrameCount/625)*625));
    float head=fract(t*0.0048);
    float behind=fract(head-(1.0-p.y/1536.0));
    float d=min(behind,1.0-behind);
    // xy: card LEDs use the carousel laser; zw: preserve the approved broad
    // photo sheen. They share position/time, never the same light footprint.
    return vec4(exp(-pow(d/0.007,2.0)),
                exp(-behind/0.100)*(1.0-smoothstep(0.28,0.38,behind)),
                1.0-smoothstep(0.016,0.145,d),
                1.0-smoothstep(0.040,0.330,d));
}
float hash11(float n) {
    return fract(sin(n*127.1)*43758.5453123);
}
float shortPeak(float phase, float center, float width) {
    return 1.0-smoothstep(0.0,width,abs(phase-center));
}
float n64ShortCircuit() {
    // Low unstable current most of the time, followed by short irregular
    // clusters: strong peaks, brief dropouts and no regular breathing rhythm.
    float frame=float(FrameCount);
    float weak=0.105+0.050*(0.5+0.5*sin(frame*0.071))
                       +0.035*(0.5+0.5*sin(frame*0.173+1.7));
    float cycle=floor(frame/211.0);
    float phase=fract(frame/211.0);
    float chaos=0.72+0.28*hash11(cycle+3.0);
    float cluster=max(shortPeak(phase,0.105,0.014),shortPeak(phase,0.148,0.010));
    cluster=max(cluster,shortPeak(phase,0.205,0.018));
    float late=shortPeak(phase,0.628,0.013)*step(0.48,hash11(cycle+17.0));
    float dropout=max(shortPeak(phase,0.286,0.026),shortPeak(phase,0.760,0.035));
    return clamp(weak*(1.0-0.72*dropout)+max(cluster,late)*chaos,0.035,1.0);
}
vec3 n64LampHue(vec2 p) {
    // Four stable 1.5 s states at the frontend's 60 Hz VSync. The existing
    // short-circuit envelope still controls weak current, dropouts and peaks;
    // only the N64 lamp color changes as one electrical bank.
    float colorStep=floor(mod(float(FrameCount),360.0)/90.0);
    if(colorStep<0.5) return vec3(0.035,1.00,0.120); // green
    if(colorStep<1.5) return vec3(1.00,0.035,0.055); // red
    if(colorStep<2.5) return vec3(0.025,0.360,1.00); // blue
    return vec3(1.00);                              // white
}
float luminance(vec3 c) { return dot(c,vec3(0.299,0.587,0.114)); }
float contourSheen(vec2 p,vec2 flow) {
    // Restore hero-neon-edge's moving contour light in cover-local space.
    // Reference offsets match one displayed pixel at 1360x768, not a screen
    // rectangle that could illuminate the back covers when the fan animates.
    vec2 dx=vec2(3.85,0.0),dy=vec2(0.0,3.90);
    float edge=abs(luminance(sampleArt(p+dx).rgb)-luminance(sampleArt(p-dx).rgb))
              +abs(luminance(sampleArt(p+dy).rgb)-luminance(sampleArt(p-dy).rgb));
    float wide=abs(luminance(sampleArt(p+dx*2.5).rgb)-luminance(sampleArt(p-dx*2.5).rgb))
              +abs(luminance(sampleArt(p+dy*2.5).rgb)-luminance(sampleArt(p-dy*2.5).rgb));
    float moving=flow.x;
    float tail=flow.y;
    return smoothstep(0.12,0.52,edge)*(0.14+tail*0.22+moving*0.50)
           +smoothstep(0.08,0.44,wide)*0.40*(0.08+moving*0.16);
}
// Neo Geo magazine chassis measured on original 1024 x 1536 artwork.
// Shared by svcplus.png and the local neogeo/media/revista corpus.
// The CD platform may use this chassis too, but the signature must match.
float neoRegion(vec2 p) {
    float m=max(box(p,vec2(160,0),vec2(316,32)),box(p,vec2(709,0),vec2(865,32)));
    m=max(m,box(p,vec2(170,185),vec2(266,201)));
    m=max(m,box(p,vec2(762,185),vec2(856,201)));
    m=max(m,box(p,vec2(887,116),vec2(992,152)));
    m=max(m,discMask(p,vec2(44,234),24.0));
    m=max(m,discMask(p,vec2(980,234),24.0));
    m=max(m,box(p,vec2(19,319),vec2(59,472)));
    m=max(m,box(p,vec2(965,319),vec2(1008,472)));
    m=max(m,box(p,vec2(23,810),vec2(50,951)));
    m=max(m,box(p,vec2(975,810),vec2(1007,951)));
    m=max(m,box(p,vec2(762,1344),vec2(946,1363)));
    m=max(m,discMask(p,vec2(48,1456),24.0));
    m=max(m,discMask(p,vec2(976,1456),24.0));
    m=max(m,box(p,vec2(107,1398),vec2(206,1484)));
    m=max(m,box(p,vec2(607,1409),vec2(686,1477)));
    return m;
}
float neoChroma(vec3 c) {
    float hi=max(c.r,max(c.g,c.b)),lo=min(c.r,min(c.g,c.b));
    return smoothstep(.06,.28,hi-lo)*smoothstep(.20,.75,hi);
}
float neoSignature() {
    // Measured bright rail interiors stay blue in both 1024x1536 and 262x393
    // textures. Edge probes at (38,406)/(790,12) attenuated the real frame.
    float bars=blue(sampleArt(vec2(240,14)).rgb)+blue(sampleArt(vec2(790,14)).rgb)
        +blue(sampleArt(vec2(34,406)).rgb)+blue(sampleArt(vec2(991,406)).rgb);
    vec3 amber=sampleArt(vec2(942,125)).rgb;
    float arcade=smoothstep(.22,.7,min(amber.r,amber.g)-amber.b);
    float dark=1.0-smoothstep(.10,.27,luminance(sampleArt(vec2(512,208)).rgb));
    return smoothstep(2.6,3.8,bars)*arcade*dark;
}

void main() {
    vec4 base=TEX(u_tex,uv);
    vec2 p=vec2(uv.x,1.0-uv.y)*vec2(1024,1536);
    // Require the recognizable premium-frame lamps. Plain game screenshots
    // and covers without this frame must not receive floating lights.
    float signature=blue(sampleArt(vec2(49,565)).rgb)+blue(sampleArt(vec2(963,565)).rgb)
                   +blue(sampleArt(vec2(120,42)).rgb)+blue(sampleArt(vec2(900,42)).rgb);
    float darkHeader=1.0-smoothstep(0.08,0.25,dot(sampleArt(vec2(512,30)).rgb,vec3(0.299,0.587,0.114)));
    float megaSignature=blue(sampleArt(vec2(220,12)).rgb)+blue(sampleArt(vec2(800,12)).rgb)
                 +blue(sampleArt(vec2(47,560)).rgb)+blue(sampleArt(vec2(976,560)).rgb);
    // Stay inside the wide dark separator. At y=215, ImageIO's FILTER_BOX
    // mixes the white rule at y=217 into the 262x393 texture and disables LEDs.
    // y=208 keeps a margin on both sides at native-sized textures, not just
    // when drawing the full-resolution source into a smaller viewport.
    float megaHeader=1.0-smoothstep(0.08,0.25,dot(sampleArt(vec2(512,208)).rgb,vec3(0.299,0.587,0.114)));
    float n64Signature=n64Lamp(sampleArt(vec2(240,14)).rgb)+n64Lamp(sampleArt(vec2(790,14)).rgb)
                 +n64Lamp(sampleArt(vec2(44,235)).rgb)+n64Lamp(sampleArt(vec2(980,235)).rgb)
                 +n64Lamp(sampleArt(vec2(975,1454)).rgb);
    float n64Header=1.0-smoothstep(0.08,0.25,dot(sampleArt(vec2(512,175)).rgb,vec3(0.299,0.587,0.114)));
    // Recognize the actual frame too: grouped systems may inherit the default
    // profile. A plain blue image still fails the dark separator requirement.
    activeMagazineModel=max(magazineModel,step(0.95,smoothstep(2.0,3.2,megaSignature)*megaHeader));
    if(activeMagazineModel>1.5) {
        signature=n64Signature;
        darkHeader=n64Header;
    } else if(activeMagazineModel>0.5) {
        signature=megaSignature;
        darkHeader=megaHeader;
    }
    float enabled=(activeMagazineModel>1.5 ? smoothstep(2.8,4.2,signature) : smoothstep(2.0,3.2,signature))*darkHeader;
    // Neo Geo/CD keeps its measured geometry and its artwork's lamp colors,
    // but uses the exact SNES envelope, emitter recovery, 2/5px halo and compositing.
    bool neoMode=activeMagazineModel>2.5;
    if(neoMode){enabled=neoSignature();if(enabled<.01){FragColor=base*tint;return;}}
    float mask=emitter(p);
    float nearGlow=0.0,wideGlow=0.0;
    for(int i=0;i<8;i++) {
        float angle=float(i)*0.7853981634;
        vec2 dir=vec2(cos(angle),sin(angle));
        nearGlow+=emitter(p+dir*2.0);
        wideGlow+=emitter(p+dir*5.0);
    }
    nearGlow/=8.0; wideGlow/=8.0;
    vec4 flow=lightEnvelope(p);
    float n64Mode=step(1.5,activeMagazineModel)*(1.0-step(2.5,activeMagazineModel));
    float shortCircuit=n64ShortCircuit();
    flow=mix(flow,vec4(pow(shortCircuit,4.0),shortCircuit*0.24,shortCircuit,shortCircuit*0.38),n64Mode);
    float energy=max(flow.x,flow.y);
    vec3 hue=clamp(ledColor.rgb,0.0,1.0);
    if(neoMode) hue=base.rgb/max(max(base.r,max(base.g,base.b)),.001);
    else if(activeMagazineModel>1.5) hue=n64LampHue(p);
    else if(activeMagazineModel>0.5) hue=vec3(24.0,108.0,255.0)/255.0;
    float gain=clamp(ledGain,1.0,2.5);
    // Retint only the existing blue emitter and its baked blue falloff.
    // Positions and pulse stay fixed; preserve source contrast, not max-channel
    // brightness (blue is saturated even in the dim shoulders of these LEDs).
    float chroma=max(base.r,max(base.g,base.b))-min(base.r,min(base.g,base.b));
    float fringe=region(p)*(activeMagazineModel>1.5 ? smoothstep(0.04,0.20,chroma)
                                                   : smoothstep(0.015,0.10,base.b-base.r));
    float recolor=enabled*max(mask,fringe);
    float value=dot(base.rgb,vec3(0.16,0.68,0.16));
    if(activeMagazineModel>1.5 && !neoMode) value=max(base.r,max(base.g,base.b));
    // Cyan cores lose their red channel when reduced to the on-screen cover.
    // Use their green/blue energy instead of requiring already-white RGB.
    // Brighten only the emitter, not the halo or the dark red shoulders.
    float hot=smoothstep(0.48,0.82,min(base.g,base.b))
             *smoothstep(0.30,0.78,flow.x);
    if(activeMagazineModel>1.5 && !neoMode)
        hot=smoothstep(0.62,0.94,max(base.r,max(base.g,base.b)))*smoothstep(0.38,0.82,flow.x);
    if(neoMode) hot=smoothstep(0.48,0.82,max(base.r,max(base.g,base.b)))
                  *smoothstep(0.30,0.78,flow.x);
    vec3 lamp=mix(hue*value*(0.30+0.80*energy),vec3(1.0),hot);
    vec3 rgb=mix(base.rgb,clamp(lamp,0.0,1.0),recolor);
    // Match carousel laser intensity: 2.2 for the red trail, 3.0 for the hot
    // head. Keep the compact 2/5px footprint: only the passing light intensifies.
    float laserPower=0.18+2.2*flow.y+3.0*flow.x;
    if(activeMagazineModel>1.5 && !neoMode)
        laserPower=0.08+0.48*shortCircuit+3.35*pow(shortCircuit,4.0);
    float bloom=enabled*laserPower*gain*(mask*0.05+nearGlow*0.15+wideGlow*0.035);
    vec3 glowColor=mix(hue,vec3(1.0,0.90,0.92),flow.x);
    rgb=1.0-(1.0-rgb)*(1.0-clamp(glowColor*bloom,0.0,1.0));
    // Both effects run together. The old white contour sweep stays out of the
    // measured lamp regions; its head and the LED peak share the same flow.
    float sheen=contourSheen(p,flow.zw)*clamp(sheenGain,0.0,1.0)*(1.0-region(p));
    rgb=clamp(rgb+vec3(sheen),0.0,1.0);
    float luma=dot(rgb,vec3(0.299,0.587,0.114));
    rgb=mix(vec3(luma),rgb,saturation);
    FragColor=vec4(rgb,base.a)*tint;
}
#endif
)NEOMAG";
