from pathlib import Path
import importlib.util,json,hashlib,types
import numpy as np
from PIL import Image
import argparse
parser=argparse.ArgumentParser(description='Isolated GameCube GLES2 comparison using privately supplied original art; no device operations.')
parser.add_argument('--art-directory',type=Path,required=True)
parser.add_argument('--output',type=Path)
parser.add_argument('--preview-directory',type=Path)
args=parser.parse_args()
tests=Path(__file__).resolve().parent;root=tests.parent
old=(tests/'fixtures/gamecube-before-r95.glsl').read_text('utf8')
new=(root/'native/d0/premium-magazine-led-android.glsl').read_text('utf8')
for start,end in [('vec3 snesLight','void main() {\n    vec4 base'),('vec4 lightEnvelope','float hash11'),('float switchSegmentedRegion','float psxRegion'),('float region(vec2 p)','vec4 sampleArt')]:
 assert old.split(start,1)[1].split(end,1)[0]==new.split(start,1)[1].split(end,1)[0],start
def sm(lo,hi,v):
 t=np.clip((v-lo)/(hi-lo),0,1);return t*t*(3-2*t)
def lamp(c):
 return sm(.08,.32,c[2]-c[1])*sm(.28,.78,c[2])*sm(.08,.35,c[0])
def sample(a,x,y):
 h,w=a.shape[:2];x=x/1024*w-.5;y=y/1536*h-.5;x0=int(np.floor(x));y0=int(np.floor(y));fx=x-x0;fy=y-y0
 x0=max(0,min(w-2,x0));y0=max(0,min(h-2,y0))
 return (a[y0,x0]*(1-fx)+a[y0,x0+1]*fx)*(1-fy)+(a[y0+1,x0]*(1-fx)+a[y0+1,x0+1]*fx)*fy
signature=[]
source=args.art_directory
for p in sorted(source.glob('*.png')):
 a=np.asarray(Image.open(p).convert('RGB').resize((262,393),Image.Resampling.BOX),dtype=float)/255
 sides=[max(lamp(sample(a,x+offset,y)) for offset in [-10,-5,0,5,10] for y in [558,635,701]) for x in [27,991]]
 enabled=float(sm(.4,.8,min(sides)));assert enabled>.95,(p.name,enabled)
 signature.append({'asset':p.name,'enabled':enabled})
print('GameCube activation probes passed: '+str(len(signature)),flush=True)
# Use the real shared SNES color, rather than the historical harness red default.
harness=tests/'angle_gles2.py'
code=harness.read_text('utf8').replace("self.Uniform4f(location('ledColor'),1.,24/255,38/255,1.)","self.Uniform4f(location('ledColor'),168/255,85/255,247/255,1.)")
mod=types.ModuleType('local_gamecube_angle');exec(compile(code,str(harness),'exec'),mod.__dict__)
driver=mod.Angle();programs={}
for key,shader in [('before',old),('after',new)]:
 print('Compiling isolated shader '+key,flush=True)
 programs[key]=driver.program('R95 GameCube '+key,'#version 100\n#define VERTEX\n'+shader,'#version 100\n#define FRAGMENT\n'+shader)
ref=source/'the Legend of Zelda, The - The Wind Waker.png'
art=Image.open(ref).convert('RGBA').resize((262,393),Image.Resampling.BOX)
texture=driver.texture(np.asarray(art));outputs={};deltas=[]
for frame in [12,60,70,122,180]:
 for key in programs:
  output,_=driver.render(programs[key],texture,(262,393),frame,model=5,sheen=0)
  outputs[key,frame]=output
  if args.preview_directory:
   args.preview_directory.mkdir(parents=True,exist_ok=True)
   Image.fromarray(output).save(args.preview_directory/f'{key}-{frame}.png')
 a=outputs['before',frame];b=outputs['after',frame]
 delta=int(np.max(np.abs(a[60:230,36:177,:3].astype(int)-b[60:230,36:177,:3].astype(int))))
 assert delta<=1,delta;deltas.append(delta)
def patch(a,rect):
 x0,y0,x1,y1=rect;return a[round(y0/1536*393):round(y1/1536*393),round(x0/1024*262):round(x1/1024*262),:3]
checks={}
for name,rect,hot,cold in [('middle_left',(10,625,49,645),122,60),('middle_right',(970,625,1010,645),122,60),('cloud',(132,1437,224,1462),12,70),('folder',(513,1437,590,1462),12,70),('badge_upper_rim_tail',(835,1107,875,1130),60,122)]:
 if hot not in [12,60,70,122,180]:continue
 oldcold=patch(outputs['before',cold],rect).mean();newcold=patch(outputs['after',cold],rect).mean();newhot=patch(outputs['after',hot],rect).mean()
 assert newhot>newcold*1.15,(name,newhot,newcold)
 assert newcold<oldcold,(name,newcold,oldcold)
 checks[name]={'beforeColdMeanRGB':round(float(oldcold),3),'afterColdMeanRGB':round(float(newcold),3),'afterPassingLightMeanRGB':round(float(newhot),3),'passingToColdRatio':round(float(newhot/newcold),3)}
# Exclude the neighboring violet rim from the star-glyph check.
art=np.asarray(Image.open(ref).convert('RGB').resize((262,393),Image.Resampling.BOX))
yy,xx=np.mgrid[0:393,0:262];x=(xx+.5)/262*1024;y=(yy+.5)/393*1536
stars=np.zeros(xx.shape,dtype=bool)
for cx,cy,r in [(820,1179,21),(858,1166,28),(898,1180,21)]:stars|=((x-cx)**2+(y-cy)**2<r*r)
text=(x>773)&(x<947)&(y>1205)&(y<1307)
white=(art.min(axis=-1)>.3*255)&((art.max(axis=-1).astype(float)-art.min(axis=-1))<.2*255)
for name,m in [('badge_stars',stars),('badge_words',text)]:
 ds=[];neutral=[]
 for f in [12,60,70,122,180]:
  diff=np.abs(outputs['before',f][:,:,:3].astype(int)-outputs['after',f][:,:,:3].astype(int)).max(axis=-1)
  ds.append(int(diff[m].max()));neutral.append(int(diff[m&white].max()))
 assert max(ds)<=1 and max(neutral)==0,(name,ds,neutral)
 checks[name]={'maximumRegionByteDelta':max(ds),'maximumWhiteGlyphByteDelta':max(neutral),'whitePixelCount':int((m&white).sum())}
report={'scope':'Isolated GLES2 render of actual GameCube artwork and CPU activation probes; not phone performance/visual acceptance','sourceShaderSHA256':hashlib.sha256(new.encode()).hexdigest(),'referenceSHA256':hashlib.sha256(ref.read_bytes()).hexdigest(),'color':'#A855F7','renderer':mod.REPORT['renderer'],'signature262x393':signature,'centralArtMaximumByteDelta':deltas,'checks':checks,'compiled':True,'linked':True,'snesClockGainFunctionAndSwitchUnchanged':True}
out=args.output or root/'evidence/gamecube-render-validation.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps({'probes':len(signature),'minimumSignature':min(x['enabled'] for x in signature),'centralDelta':max(deltas),'checks':checks},indent=2))
