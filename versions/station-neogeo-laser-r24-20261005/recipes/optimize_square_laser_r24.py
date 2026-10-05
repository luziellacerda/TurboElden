"""Reject empty square-art neighborhoods before any extra texture sampling."""
from pathlib import Path
import hashlib,json
W=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005');N=W/'native'
p=N/'neogeocd-square.glsl';s=p.read_text('utf8');h=(N/'native_neogeocd_square.h').read_text('utf8')
assert 'neoSquareNeighborhood' not in s
before=W/'tests/square-before-cull.h';assert not before.exists();before.write_text(h,'utf8')
gate='''// Conservative six-source-pixel margin contains every 2/5 reference-pixel tap.
// Empty game/photo pixels cost one source read, as before, not 17 mask gathers.
bool neoSquareNeighborhood(vec2 p){
    if(abs(neoRoundDistance(p,vec2(623.,627.),vec2(614.,609.),83.))<=19.)return true;
    if(abs(length(p-vec2(76.,569.))-40.)<=14.||abs(length(p-vec2(1170.,569.))-40.)<=14.)return true;
    if(p.y<944.||p.y>1050.)return false;
    return (p.x>=47.&&p.x<=155.)||(p.x>=349.&&p.x<=450.)||
           (p.x>=629.&&p.x<=729.)||(p.x>=904.&&p.x<=1005.);
}
'''
t=s.replace('vec3 neoSquareLight(',gate+'vec3 neoSquareLight(')
t=t.replace('    vec2 p=vec2(uv.x,1.-uv.y)*1254.;','    vec2 p=vec2(uv.x,1.-uv.y)*1254.;\n    if(!neoSquareNeighborhood(p))return base;')
assert h.count(s)==2
p.write_text(t,'utf8',newline='\n');(N/'native_neogeocd_square.h').write_text(h.replace(s,t),'utf8',newline='\n')
print('Square empty-space culling prepared; compare actual GL frames before/after.')
