from pathlib import Path
import re,json,hashlib,importlib.util
import numpy as np
from PIL import Image
import argparse
parser=argparse.ArgumentParser(description="Render the actual R94/R95 shaders with an explicitly provided local Samsung Switch reference.")
parser.add_argument('--switch-reference',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1];repo=root.parents[1]
old=(repo/'versions/station-gamecube-snes-r94-20261009/native/d0/premium-magazine-led-android.glsl').read_text('utf8')
new=(root/'native/d0/premium-magazine-led-android.glsl').read_text('utf8')
source=args.switch_reference
im=Image.open(source).convert('RGBA');w,h=im.size;crop=(round(w*.025),round(h*.04),round(w*.025+h*.790*.828),round(h*(.04+.865)))
art=im.crop(crop).resize((1024,1536));pixels=np.asarray(art,dtype=float)/255
yy,xx=np.mgrid[0:1536,0:1024];xy=np.stack((xx,yy),axis=-1)
def smooth(lo,hi,value):
 t=np.clip((value-lo)/(hi-lo),0,1);return t*t*(3-2*t)
def geometry(text,name):
 body=text.split('float '+name+'(vec2 p){',1)[1].split('\n}',1)[0];m=np.zeros((1536,1024))
 for a,b,width in re.findall(r'segmentMask\(p,vec2\(([^)]+)\),vec2\(([^)]+)\),([\d.]+)\)',body):
  a=np.array([float(v) for v in a.split(',')]);b=np.array([float(v) for v in b.split(',')]);ab=b-a;t=np.clip(np.sum((xy-a)*ab,axis=-1)/np.dot(ab,ab),0,1)
  m=np.maximum(m,1-smooth(float(width),float(width)+3,np.linalg.norm(xy-a-t[:,:,None]*ab,axis=-1)))
 for a,b in re.findall(r'box\(p,vec2\(([^)]+)\),vec2\(([^)]+)\)\)',body):
  a=np.array([float(v) for v in a.split(',')]);b=np.array([float(v) for v in b.split(',')]);v=smooth(a,a+3,xy)*(1-smooth(b-3,b,xy));m=np.maximum(m,v[:,:,0]*v[:,:,1])
 for a,r in re.findall(r'frameRing\(p,vec2\(([^)]+)\),([\d.]+)\)',body):
  a=np.array([float(v) for v in a.split(',')]);m=np.maximum(m,1-smooth(5,12,np.abs(np.linalg.norm(xy-a,axis=-1)-float(r))))
 return m
previous=geometry(old,'switchRegion');current=geometry(new,'switchSegmentedRegion')
red=(pixels[:,:,0]-np.maximum(pixels[:,:,1],pixels[:,:,2])>.15)&(pixels[:,:,0]>.28)
regions={'upper-left':(0,0,100,415),'upper-right':(935,0,1024,415),'middle-left':(0,515,45,750),'middle-right':(975,515,1024,750),'lower-left':(0,1360,100,1536),'lower-right':(930,1360,1024,1536),'badge':(710,1095,995,1380),'footer':(460,1410,490,1500)}
mapping={}
for name,(x0,y0,x1,y1) in regions.items():
 area=np.zeros(red.shape,dtype=bool);area[y0:y1,x0:x1]=True
 mapping[name]=dict(oldMapColoredPixels=int((area&red&(previous>.05)).sum()),newMapColoredPixels=int((area&red&(current>.05)).sum()))
report=dict(reference='Pokemon Cafe Mix, real Samsung capture, screenshot rather than original cached cover',captureSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),crop=crop,sourcePixelEncoding='8-bit RGBA',normalizedMap=[1024,1536],mapSHA256=hashlib.sha256(current.astype('float32').tobytes()).hexdigest(),regions=mapping,scope='Colored-pixel overlap inside measured geometry; not a claim of catalogue completeness or brightness measured from pristine artwork')
print(json.dumps(report),flush=True)
spec=importlib.util.spec_from_file_location('angle',repo/'versions/station-platform-led-r87-20261008/tests/angle_gles2.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);driver=a.Angle()
programs={}
for key,s in [('before',old),('after',new)]:programs[key]=driver.program('R95 '+key,'#version 100\n#define VERTEX\n'+s,'#version 100\n#define FRAGMENT\n'+s)
# Independent synthetic SNES emitter input: exact same input and color on both shaders.
fixture=np.zeros((1536,1024,4),dtype=np.uint8);fixture[:]=[9,160,255,255];fixture[:200,300:720,:3]=0
texture=driver.texture(fixture);deltas=[]
for frame in [0,37,83,123,190,310]:
 before,_=driver.render(programs['before'],texture,(262,393),frame,model=0,sheen=0)
 after,_=driver.render(programs['after'],texture,(262,393),frame,model=0,sheen=0)
 delta=int(np.max(np.abs(before.astype(int)-after.astype(int))));assert delta<=1,delta;deltas.append(delta)
# The real screen is only used to check mapping/activation, not original source brightness.
texture=driver.texture(np.array(art.resize((262,393),Image.Resampling.BOX)));frames=[]
for frame in [30,80,123,175]:
 result,_=driver.render(programs['after'],texture,(262,393),frame,model=7,sheen=0);frames.append(result)
motion=sum(int(np.count_nonzero(np.any(frames[i][:,:,:3]!=frames[0][:,:,:3],axis=-1))) for i in range(1,len(frames)))
assert motion>100,'Switch remains static'
report.update(snesBeforeAfterMaximumByteDelta=deltas,switchIsolatedChangedPixelsAcrossFrames=motion,compilerRenderer=a.REPORT['renderer'],visualApprovalOnPhone=False)
(root/'evidence/pixel-map-validation.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
(root/'evidence/shader-compile.json').write_text(json.dumps(a.REPORT,indent=2)+'\n','utf8')
print(json.dumps(dict(snesMaximumDelta=max(deltas),switchMotionPixels=motion,compiled=True,linked=True)),flush=True)
