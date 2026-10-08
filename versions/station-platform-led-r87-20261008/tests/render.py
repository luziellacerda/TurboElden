from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));import angle_gles2 as A
W=Path(r'E:\ESTUDO APK\work\station-platform-led-r87-20261008');s=(W/'carousel-inputs/d0/premium-magazine-led-android.glsl').read_text('utf8');out=W/'visual-tests';out.mkdir(exist_ok=True)
refs=[('dreamcast',4,W/'assets/reference/dreamcast-orange-frame.png'),('gamecube',5,Path(r'G:\TURBORAMA\RetroBat\roms\gamecube\media\images\Blood Rayne.png')),('wiiu',6,Path(r'G:\TURBORAMA\RetroBat\roms\wiiu\media\images\Bayonetta 2.png')),('switch',7,Path(r'G:\TURBORAMA\RetroBat\roms\switch\media\images\Bayonetta 2.png')),('psx',8,Path(r'G:\TURBORAMA\RetroBat\roms\psx\media\images\Alien Trilogy.png'))]
gl=A.Angle();p=gl.program('R87 shared profiles','#version 100\n#define VERTEX\n'+s,'#version 100\n#define FRAGMENT\n'+s);reports=[]
for name,model,src in refs:
 im=Image.open(src).convert('RGBA').resize((344,516),Image.Resampling.BOX);tex=gl.texture(np.array(im));frames=[gl.render(p,tex,(344,516),frame=f,model=model,sheen=0)[0] for f in [0,40,90,150]]
 diff=np.any(frames[0][:,:,:3]!=frames[1][:,:,:3],axis=2);core=diff[85:430,40:304]
 assert diff.sum()>50 and not core.any(),(name,int(diff.sum()),int(core.sum()))
 Image.fromarray(frames[1]).save(out/(name+'-preview.png'))
 reports.append(dict(platform=name,model=model,sha256=hashlib.sha256(src.read_bytes()).hexdigest(),animatedPixels=int(diff.sum()),centerChanged=int(core.sum())))
# The actual 18 Wheeler cover as rendered on Samsung; normalized coordinates only for analysis.
screen=Image.open(r'E:\ESTUDO APK\work\station-online-cover-led-r86-20261008\installation\dreamcast-samsung-private.png').convert('RGBA')
im=screen.crop((59,44,765,977)).resize((344,516),Image.Resampling.BOX);tex=gl.texture(np.array(im));frames=[gl.render(p,tex,(344,516),frame=f,model=4,sheen=0)[0] for f in [0,40]];diff=np.any(frames[0][:,:,:3]!=frames[1][:,:,:3],axis=2)
assert diff.sum()>50,int(diff.sum());reports.append(dict(platform='dreamcast-phone-observed',source='private Samsung screenshot, analytical crop only',animatedPixels=int(diff.sum())))
# Plain and wrong-frame art must remain static under the new models.
for model in range(4,9):
 tex=gl.texture(np.full((516,344,4),[30,30,30,255],dtype=np.uint8));a=gl.render(p,tex,(344,516),frame=0,model=model)[0];b=gl.render(p,tex,(344,516),frame=40,model=model)[0];assert np.array_equal(a,b)
report=dict(passed=True,scope='PC GLES rendering; not phone performance or gameplay',checks=reports);(H.parent/'evidence/render.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))
