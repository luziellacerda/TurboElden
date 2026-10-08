from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import angle_gles2 as H
W=Path(r'E:\ESTUDO APK\work\station-online-cover-led-r86-20261008');N=W/'carousel-inputs/d0'
s=(N/'premium-magazine-led-android.glsl').read_text().replace('vec2(35,175)','vec2(30,175)').replace('vec2(988,175)','vec2(992,175)').replace('vec2(35,1030)','vec2(39,1030)').replace('vec2(988,1030)','vec2(983,1030)')
(N/'premium-magazine-led-android.glsl').write_text(s,'utf8');(N/'magazine_shader.h').write_text('static const char magazineShaderSource[]=R"NEOMAG('+s+')NEOMAG";\n','utf8')
source=W/'assets/reference/dreamcast-orange-frame.png'
out=W/'visual-tests';out.mkdir(exist_ok=True)
import shutil
shutil.copyfile(source,out/'dreamcast-reference.png')
gl=H.Angle();program=gl.program('R86 orange Dreamcast', '#version 100\n#define VERTEX\n'+s,'#version 100\n#define FRAGMENT\n'+s)
reports=[]
for size in [(1024,1536),(262,393)]:
 im=Image.open(source).convert('RGBA').resize(size,Image.Resampling.BOX);tex=gl.texture(np.array(im))
 frames=[gl.render(program,tex,size,frame=f,model=4,sheen=0)[0] for f in [0,40,90,150]]
 diff=np.any(frames[0][:,:,:3]!=frames[1][:,:,:3],axis=2);total=int(diff.sum())
 # Center illustration should be byte-identical over time; frame/footer excluded.
 core=diff[round(size[1]*.15):round(size[1]*.88),round(size[0]*.1):round(size[0]*.9)]
 assert total>50 and not core.any(),(size,total,int(core.sum()))
 for i,f in enumerate(frames):Image.fromarray(f).save(out/f'dreamcast-{size[0]}-{i}.png')
 reports.append(dict(size=size,animatedPixels=total,centerArtworkAnimatedPixels=int(core.sum())))
report=dict(passed=True,scope='PC ANGLE shader rendering, not Android performance',sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),reference='User supplied BANG! Gunship Elite orange chassis',checks=reports)
(HERE.parent/'evidence/dreamcast-render.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report))
