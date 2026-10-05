"""Isolated LED correction. Does not modify frozen bases or package/install an APK."""
from pathlib import Path
import hashlib, json, re, shutil

W=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005')
B=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\native')
R20=Path(r'E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005')
assert not W.exists(), 'Candidate already exists; do not overwrite'
for sub in ('native','refs','evidence','tests','temp'): (W/sub).mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original={p.name:sha(p) for p in B.iterdir() if p.is_file()}
for p in B.iterdir():
    if p.is_file():shutil.copy2(p,W/'native'/p.name)
for p in (R20/'refs').glob('*.png'):shutil.copy2(p,W/'refs'/p.name)

N=W/'native'
s=(B/'premium-magazine-led-android.glsl').read_text('utf8')
# Keep all old model calculations in place; model 3 now uses that same engine.
s=s.replace('float region(vec2 p) {','float neoRegion(vec2 p);\nfloat neoChroma(vec3 c);\nfloat region(vec2 p) {\n    if(activeMagazineModel>2.5) return neoRegion(p);')
s=s.replace('float lampSample(vec3 c) {','float lampSample(vec3 c) {\n    if(activeMagazineModel>2.5) return neoChroma(c);')
start=s.index('float neoEmitter(vec2 p) {');end=s.index('float neoSignature()',start)
s=s[:start]+s[end:]
start=s.index('vec4 neoMagazine(vec4 base,vec2 p) {');end=s.index('\nvoid main() {',start)
s=s[:start]+s[end:]
s=s.replace('    if(magazineModel>2.5){FragColor=neoMagazine(base,p)*tint;return;}\n','')
s=s.replace('    float mask=emitter(p);','''    // Neo Geo/CD keeps its measured geometry and its artwork's lamp colors,
    // but uses the exact SNES envelope, emitter recovery, 2/5px halo and compositing.
    bool neoMode=activeMagazineModel>2.5;
    if(neoMode){enabled=neoSignature();if(enabled<.01){FragColor=base*tint;return;}}
    float mask=emitter(p);''')
s=s.replace('float n64Mode=step(1.5,activeMagazineModel);','float n64Mode=step(1.5,activeMagazineModel)*(1.0-step(2.5,activeMagazineModel));')
s=s.replace('if(activeMagazineModel>1.5) hue=n64LampHue(p);','if(neoMode) hue=base.rgb/max(max(base.r,max(base.g,base.b)),.001);\n    else if(activeMagazineModel>1.5) hue=n64LampHue(p);')
s=s.replace('if(activeMagazineModel>1.5) value=max(base.r,max(base.g,base.b));','if(activeMagazineModel>1.5 && !neoMode) value=max(base.r,max(base.g,base.b));')
s=s.replace('if(activeMagazineModel>1.5)\n        hot=', 'if(activeMagazineModel>1.5 && !neoMode)\n        hot=')
s=s.replace('    vec3 lamp=mix(hue*value', '''    if(neoMode) hot=smoothstep(0.48,0.82,max(base.r,max(base.g,base.b)))
                  *smoothstep(0.30,0.78,flow.x);
    vec3 lamp=mix(hue*value''')
s=s.replace('if(activeMagazineModel>1.5)\n        laserPower=', 'if(activeMagazineModel>1.5 && !neoMode)\n        laserPower=')
(N/'premium-magazine-led-android.glsl').write_text(s,'utf8',newline='\n')
(N/'magazine_shader.h').write_text('static const char magazineShaderSource[]=R"NEOMAG('+s+')NEOMAG";\n','utf8',newline='\n')

# Square artwork: same normalized 0.007 head, .100 tail and .18/2.2/3 powers.
# 1254 source pixels map to the same 1536-high reference space used by SNES.
# Preserve the measured geometry, artwork color, existing 2D/OES draw and player.
old=(B/'neogeocd-square.glsl').read_text('utf8')
geometry=old[:old.index('vec3 neoSquareLight(')]
geometry=geometry.replace('// One source sample; no new player, draw loop, intermediate image or full-frame bloom.',
    '// Same draw/player; texture samples are confined to the measured lamp geometry.\n// 2/5 reference-pixel halo and normalized time/width follow the SNES magazine.')
square=geometry+'''float neoSquareChroma(vec3 c){
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
vec3 neoSquareLight(vec3 base,vec2 uv,float phase){
    vec2 p=vec2(uv.x,1.-uv.y)*1254.;
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
'''
(N/'neogeocd-square.glsl').write_text(square,'utf8',newline='\n')
h=(B/'native_neogeocd_square.h').read_text('utf8')
assert h.count(old)==2
h=h.replace(old,square)
declarations='precision highp float;varying vec2 uv;uniform float neoPhase;'
first=h.index(declarations);second=h.index(declarations,first+len(declarations))
# Edit second first; sampler declarations must precede shared helper functions.
h=h[:second]+h[second:].replace(declarations,declarations+'''
uniform samplerExternalOES frame;uniform mat4 videoTransform;
vec3 squareSample(vec2 coord){vec2 src=(videoTransform*vec4(coord,0.,1.)).xy;return texture2D(frame,src).rgb;}
''',1)
h=h[:first]+h[first:].replace(declarations,declarations+'''
uniform sampler2D frame;
vec3 squareSample(vec2 coord){return texture2D(frame,coord).rgb;}
''',1)
h=h.replace('uniform sampler2D frame;void main(){vec3 b=texture2D(frame,uv).rgb;', 'void main(){vec3 b=squareSample(uv);')
h=h.replace('uniform samplerExternalOES frame;uniform mat4 videoTransform;void main(){vec2 src=(videoTransform*vec4(uv,0.,1.)).xy;vec3 b=texture2D(frame,src).rgb;', 'void main(){vec3 b=squareSample(uv);')
h=h.replace('(now%10417u)/10417.f*3.f', '(float)((((U)now*60u)/1000u)%625u)*.0048f')
(N/'native_neogeocd_square.h').write_text(h,'utf8',newline='\n')
changed=[p.name for p in N.iterdir() if p.is_file() and sha(p)!=original[p.name]]
assert set(changed)=={'premium-magazine-led-android.glsl','magazine_shader.h','neogeocd-square.glsl','native_neogeocd_square.h'}
(W/'evidence/preparation.json').write_text(json.dumps({'baseNative':str(B),'baseNativeFiles':original,'changed':changed,'files':{p.name:sha(p) for p in N.iterdir() if p.is_file()},'apkBuilt':False},indent=2)+'\n','utf8')
print(json.dumps({'prepared':str(W),'changed':changed}))
