// Dreamcast TURBORAMA chassis: measured from 26 original 1024x1536 covers.
// Coordinates refer to the source image, never the screen or game illustration.
// The color gate admits only the lamps already painted inside these regions.
float dreamcastRegion(vec2 p) {
    float m=max(box(p,vec2(177,185),vec2(270,205)),box(p,vec2(762,185),vec2(852,205)));
    m=max(m,box(p,vec2(883,122),vec2(1002,138)));
    m=max(m,discMask(p,vec2(44,239),24.0));
    m=max(m,discMask(p,vec2(980,239),24.0));
    m=max(m,box(p,vec2(15,367),vec2(47,474)));
    m=max(m,box(p,vec2(979,367),vec2(1011,475)));
    m=max(m,box(p,vec2(12,675),vec2(38,757)));
    m=max(m,box(p,vec2(987,668),vec2(1013,760)));
    m=max(m,box(p,vec2(14,807),vec2(40,916)));
    m=max(m,box(p,vec2(986,807),vec2(1012,918)));
    // Lower warm rails follow their curved chassis; leave orange logos alone.
    m=max(m,segmentMask(p,vec2(27,1383),vec2(24,1421),8.0));
    m=max(m,segmentMask(p,vec2(24,1421),vec2(32,1455),8.0));
    m=max(m,segmentMask(p,vec2(32,1455),vec2(42,1472),8.0));
    m=max(m,segmentMask(p,vec2(997,1383),vec2(1000,1421),8.0));
    m=max(m,segmentMask(p,vec2(1000,1421),vec2(992,1455),8.0));
    m=max(m,segmentMask(p,vec2(992,1455),vec2(982,1472),8.0));
    // Existing blue footer glyphs, as in the SNES treatment; text is excluded.
    m=max(m,box(p,vec2(93,1377),vec2(198,1479)));
    m=max(m,box(p,vec2(207,1380),vec2(222,1468)));
    m=max(m,box(p,vec2(609,1382),vec2(694,1466)));
    m=max(m,box(p,vec2(710,1380),vec2(725,1468)));
    return m;
}
float dreamcastSignature() {
    float rails=blue(sampleArt(vec2(29,415)).rgb)+blue(sampleArt(vec2(997,415)).rgb)
               +blue(sampleArt(vec2(24,711)).rgb)+blue(sampleArt(vec2(993,711)).rgb);
    vec3 orange=sampleArt(vec2(42,236)).rgb;
    float warm=smoothstep(.35,.48,min(orange.r,orange.g)-orange.b);
    float separator=1.0-smoothstep(.14,.28,luminance(sampleArt(vec2(512,208)).rgb));
    float white=smoothstep(.80,.88,luminance(sampleArt(vec2(10,180)).rgb));
    return smoothstep(3.2,3.9,rails)*warm*separator*white;
}
vec4 dreamcastShade(vec4 base,vec2 p) {
    // The illustration and other unlit zones need no signature or texture taps.
    // Bounds include the 5px halo and smoothing radius around measured emitters.
    bool side=(p.x<82.0||p.x>942.0)&&p.y>202.0&&p.y<940.0;
    bool header=(p.y>115.0&&p.y<146.0&&p.x>875.0)
                ||(p.y>177.0&&p.y<213.0&&(p.x<278.0||p.x>754.0));
    bool footer=p.y>1358.0&&p.y<1495.0;
    if(!side&&!header&&!footer)return base;
    float enabled=dreamcastSignature();
    if(enabled<.01)return base;
    float mask=emitter(p),nearGlow=0.0,wideGlow=0.0;
    for(int i=0;i<8;i++) {
        float angle=float(i)*0.7853981634;
        vec2 dir=vec2(cos(angle),sin(angle));
        nearGlow+=emitter(p+dir*2.0);
        wideGlow+=emitter(p+dir*5.0);
    }
    nearGlow/=8.0;wideGlow/=8.0;
    // Same passing head, tail, speed and compact halo as the approved SNES LEDs.
    vec4 flow=lightEnvelope(p);
    float energy=max(flow.x,flow.y);
    float hi=max(base.r,max(base.g,base.b));
    vec3 hue=base.rgb/max(hi,.001); // Keep blue and warm lamps from the artwork.
    float chroma=hi-min(base.r,min(base.g,base.b));
    float recolor=enabled*max(mask,dreamcastRegion(p)*smoothstep(.04,.20,chroma));
    float value=dot(base.rgb,vec3(.16,.68,.16));
    float hot=smoothstep(.48,.82,hi)*smoothstep(.30,.78,flow.x);
    vec3 lamp=mix(hue*value*(.30+.80*energy),vec3(1.0),hot);
    vec3 rgb=mix(base.rgb,clamp(lamp,0.0,1.0),recolor);
    float laserPower=.18+2.2*flow.y+3.0*flow.x;
    float bloom=enabled*laserPower*clamp(ledGain,1.0,2.5)*(mask*.05+nearGlow*.15+wideGlow*.035);
    vec3 glowColor=mix(hue,vec3(1.0,.90,.92),flow.x);
    rgb=1.0-(1.0-rgb)*(1.0-clamp(glowColor*bloom,0.0,1.0));
    return vec4(rgb,base.a);
}
