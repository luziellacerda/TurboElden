"""Actual GLES readback comparisons; uses the existing ANGLE harness, not painted effects."""
from pathlib import Path
import re,json,hashlib,sys,datetime
import numpy as np
from PIL import Image
import test_console_led_angle_R20 as H

W=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005')
B=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\native')
H.OUT=W/'tests'/datetime.datetime.now().strftime('angle-%Y%m%d-%H%M%S');H.OUT.mkdir()
H.REPORT['output']=str(H.OUT)
g=H.Angle();N=W/'native'
new=(N/'premium-magazine-led-android.glsl').read_text('utf8');old=(B/'premium-magazine-led-android.glsl').read_text('utf8')
pv='#version 100\n#define VERTEX\n';pf='#version 100\n#define FRAGMENT\n'
npgr=g.program('new common SNES lamp engine',pv+new,pf+new)
opgr=g.program('R22 magazine reference',pv+old,pf+old)
passthrough=g.program('reference',H.VERTEX,H.PASSTHROUGH)
sq=(N/'native_neogeocd_square.h').read_text('utf8')
raw={key:re.search(r'static const char '+key+r'\[\]=R"NEOSQ\((.*?)\)NEOSQ";',sq,re.S).group(1)
     for key in ('neoSquareVertex','neoSquareFragment','neoSquareExternalFragment')}
sq2=g.program('square sampler2D',raw['neoSquareVertex'],raw['neoSquareFragment'])
sqo=g.program('square external OES',raw['neoSquareVertex'],raw['neoSquareExternalFragment'])
before=(W/'tests/square-before-cull.h').read_text('utf8')
beforeFragment=re.search(r'static const char neoSquareFragment\[\]=R"NEOSQ\((.*?)\)NEOSQ";',before,re.S).group(1)
sqBefore=g.program('square before empty-region optimization',raw['neoSquareVertex'],beforeFragment)
report={'legacy':[],'neo':[],'square':[],'controls':[],'flow':[],'culling':[],'output':str(H.OUT)}
def render(program,texture,size,frame=0,model=3,sheen=.55,external=False):
    # Mirror the real R24 host clock, not the old R20 approximate phase.
    uniform=g.Uniform1f;loc=g.GetUniformLocation(program,b'neoPhase')
    g.Uniform1f=lambda location,value:uniform(location,(frame%625)*.0048 if loc>=0 and location==loc else value)
    try:return g.render(program,texture,size,frame,model,sheen,external)[0]
    finally:g.Uniform1f=uniform
def texture(file):
    with Image.open(file) as image:pixels=np.array(image.convert('RGBA'))
    return g.texture(pixels),pixels
frames=(0,35,60,120,175,208,209,624,625)
refs=[('snes',Path(r'G:\TURBORAMA\RetroBat\roms\snes\media\revista\Arcana (USA).png')),
      ('mega',Path(r'G:\TURBORAMA\RetroBat\roms\megadrive\media\revista\688 Attack Sub (USA, Europe).png')),
      ('n64',Path(r"G:\TURBORAMA\RetroBat\roms\n64\media\revista\Yoshi's Story.png")),
      ('svcplus',W/'refs/neogeo-svcplus.png'),('aof',W/'refs/neogeo-aof.png')]
report['referenceSHA256']={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for _,path in refs}
for name,path in refs:
    tex,pixels=texture(path)
    for model in (0,1,2):
        for frame in frames:
            a=render(opgr,tex,(262,393),frame,model);b=render(npgr,tex,(262,393),frame,model)
            report['legacy'].append({'image':name,'model':model,'frame':frame,**H.differences(a,b)})
    if name in ('svcplus','aof'):
        results=[];base=render(passthrough,tex,(262,393))
        for frame in frames[:5]:
            a=render(npgr,tex,(262,393),frame);results.append(a);H.save(name+'-f'+str(frame),a)
        for frame in (35,120):H.save(name+'-old-f'+str(frame),render(opgr,tex,(262,393),frame))
        smallTex=g.texture(base)
        report['neo'].append({'name':name,'temporal':int(np.max(np.ptp(np.stack(results).astype(np.int16),axis=0))),
                              'smallTextureChanged':H.differences(base,render(npgr,smallTex,(262,393),120)),
                              'newVsOld':H.differences(render(opgr,tex,(262,393),120),results[3])})
    else:H.save(name+'-reference-f120',render(npgr,tex,(262,393),120,{'snes':0,'mega':1,'n64':2}[name]))
    print('magazine '+name,flush=True)
for name in ('neogeocd-square','neogeocd-video-frame'):
    tex,pixels=texture(W/'refs'/(name+'.png'));ext=g.external(tex);size=(393,393)
    base=render(passthrough,tex,size);results=[]
    for frame in frames[:5]:
        a=render(sq2,tex,size,frame);b=render(sqo,ext,size,frame,external=True);results.append(a)
        report['culling'].append({'image':name,'frame':frame,**H.differences(a,render(sqBefore,tex,size,frame))})
        report['square'].append({'name':name,'frame':frame,'oes2d':H.differences(a,b)})
        H.save(name+'-f'+str(frame),a)
    delta=np.max(np.abs(np.stack(results).astype(np.int16)-base.astype(np.int16)),axis=(0,3))
    yy=(np.arange(size[1])+.5)*1254/size[1];xx=(np.arange(size[0])+.5)*1254/size[0]
    dots=(yy[:,None]>1205)&(xx[None,:]>466)&(xx[None,:]<759)
    report['square'][-1]['dotChanges']=int(((delta>1)&dots).sum())
    report['square'][-1]['temporal']=int(np.max(np.ptp(np.stack(results).astype(np.int16),axis=0)))
    for frame in (0,120):report['controls'].append(H.differences(base,render(npgr,tex,size,frame)))
    print('square '+name,flush=True)
# Normalized envelope must match at identical positions and phases, independently of art.
oldflow=H.diagnostic(old,'void main() {vec2 p=vec2(uv.x,1.-uv.y)*vec2(1024,1536);vec4 f=lightEnvelope(p);FragColor=vec4(f.xy,0.,1.);}')
fprog=g.program('SNES reference envelope',pv+oldflow,pf+oldflow)
start=(N/'neogeocd-square.glsl').read_text('utf8').index('    float behind=')
flowcode=(N/'neogeocd-square.glsl').read_text('utf8')[start:].split('    float energy=')[0]
f2g=g.program('square actual envelope',H.VERTEX,'#version 100\nprecision highp float;varying vec2 uv;uniform float neoPhase;void main(){vec2 p=vec2(uv.x,1.-uv.y)*1254.;float phase=neoPhase;'+flowcode+'gl_FragColor=vec4(flow,0.,1.);}')
tex,_=texture(W/'refs/neogeocd-video-frame.png')
for frame in range(0,626,5):
    a=render(fprog,tex,(8,393),frame);b=render(f2g,tex,(8,393),frame)
    report['flow'].append({'frame':frame,**H.differences(a,b)})
# Actual normalized head width is .007 now, not .018. Phase host uses the same 60 Hz clock.
assert '.018' not in (N/'neogeocd-square.glsl').read_text('utf8')
assert '10417' not in sq
report['sourceSHA256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in N.iterdir() if p.is_file()}
report['passed']=(all(x['max_channel_delta']<=1 for x in report['legacy'])
    and all(x['temporal']>0 and x['smallTextureChanged']['changed_pixels_gt1']>0 for x in report['neo'])
    and all(x['oes2d']['pixel_byte_equal'] and x.get('dotChanges',0)==0 for x in report['square'])
    and all(x['pixel_byte_equal'] for x in report['controls'])
    # Different branch optimization may round the final UNORM conversion by 1/255.
    # Retain exact comparisons in the report; permit no visible (>1) difference.
    and all(x['max_channel_delta']<=1 for x in report['culling'])
    and all(x['max_channel_delta']<=1 for x in report['flow']))
report['GL']=H.REPORT
report['cullingTolerancePerChannel']=1
report['legacyTolerancePerChannel']=1
report['limitations']=['ANGLE PC is not Android performance or visual acceptance.','OES input uses EGLImage from reference frame; live decoder not exercised.']
(H.OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
(W/'evidence/led-tests.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps({'passed':report['passed'],'output':str(H.OUT),'legacy':len(report['legacy']),'envelopeComparisons':len(report['flow'])}),flush=True)
sys.exit(0 if report['passed'] else 1)
