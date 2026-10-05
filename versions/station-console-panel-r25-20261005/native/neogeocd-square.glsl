// Artwork-space effect for the confirmed Neo Geo CD square PNG and 720p clip.
// Coordinates measured on original 1254x1254, top-left origin.
// Same draw/player; texture samples are confined to the measured lamp geometry.
// 2/5 reference-pixel halo and normalized time/width follow the SNES magazine.
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
float neoSquareChroma(vec3 c){
    float hi=max(c.r,max(c.g,c.b)),lo=min(c.r,min(c.g,c.b));
    return smoothstep(.06,.28,hi-lo)*smoothstep(.20,.75,hi);
}
vec3 neoSquareArt(vec2 p){return squareSample(vec2(p.x/1254.,1.-p.y/1254.));}
float neoSquareEmitter(vec2 p){
    float mask=neoSquareMask(p);if(mask<=0.)return 0.;
    vec3 c=neoSquareArt(p);
    float lamp=neoSquareChroma(c);
    float tap=3.*1254./1536.;
    float neighbor=max(max(neoSquareChroma(neoSquareArt(p+vec2(tap,0))),neoSquareChroma(neoSquareArt(p-vec2(tap,0)))),
                       max(neoSquareChroma(neoSquareArt(p+vec2(0,tap))),neoSquareChroma(neoSquareArt(p-vec2(0,tap)))));
    float core=smoothstep(.70,.95,max(c.r,max(c.g,c.b)))*neighbor;
    return max(lamp,core)*mask;
}
// Conservative six-source-pixel margin contains every 2/5 reference-pixel tap.
// Empty game/photo pixels cost one source read, as before, not 17 mask gathers.
bool neoSquareNeighborhood(vec2 p){
    if(abs(neoRoundDistance(p,vec2(623.,627.),vec2(614.,609.),83.))<=19.)return true;
    if(abs(length(p-vec2(76.,569.))-40.)<=14.||abs(length(p-vec2(1170.,569.))-40.)<=14.)return true;
    if(p.y<944.||p.y>1050.)return false;
    return (p.x>=47.&&p.x<=155.)||(p.x>=349.&&p.x<=450.)||
           (p.x>=629.&&p.x<=729.)||(p.x>=904.&&p.x<=1005.);
}
vec3 neoSquareLight(vec3 base,vec2 uv,float phase){
    vec2 p=vec2(uv.x,1.-uv.y)*1254.;
    if(!neoSquareNeighborhood(p))return base;
    float region=neoSquareMask(p),mask=neoSquareEmitter(p),nearGlow=0.,wideGlow=0.;
    for(int i=0;i<8;i++){
        float angle=float(i)*.7853981634;
        vec2 dir=vec2(cos(angle),sin(angle))*1254./1536.;
        nearGlow+=neoSquareEmitter(p+dir*2.);
        wideGlow+=neoSquareEmitter(p+dir*5.);
    }
    nearGlow/=8.;wideGlow/=8.;
    if(max(mask,max(nearGlow,wideGlow))<=0.)return base;
    float behind=fract(fract(phase)-(1.-p.y/1254.)),d=min(behind,1.-behind);
    vec2 flow=vec2(exp(-pow(d/.007,2.)),exp(-behind/.100)*(1.-smoothstep(.28,.38,behind)));
    float energy=max(flow.x,flow.y);
    float hi=max(base.r,max(base.g,base.b)),lo=min(base.r,min(base.g,base.b));
    vec3 hue=base/max(hi,.001);
    float fringe=region*smoothstep(.04,.20,hi-lo);
    float value=dot(base,vec3(.16,.68,.16));
    float hot=smoothstep(.48,.82,hi)*smoothstep(.30,.78,flow.x);
    vec3 lamp=mix(hue*value*(.30+.80*energy),vec3(1.),hot);
    vec3 rgb=mix(base,clamp(lamp,0.,1.),max(mask,fringe));
    float laserPower=.18+2.2*flow.y+3.*flow.x;
    float bloom=laserPower*1.6*(mask*.05+nearGlow*.15+wideGlow*.035);
    vec3 glowColor=mix(hue,vec3(1.,.90,.92),flow.x);
    return 1.-(1.-rgb)*(1.-clamp(glowColor*bloom,0.,1.));
}
