"""Render unmodified R20 GLES100 shaders in ANGLE. Pillow only decodes/encodes PNGs.

All effect previews come from glDrawArrays/glReadPixels. Sources are never painted,
resized, or otherwise edited with Pillow. Diagnostic masks derive from readback.
"""
from pathlib import Path
import argparse
import ctypes as C
import datetime
import hashlib
import json
import os
import re
import sys
import time
import numpy as np
from PIL import Image

ROOT = Path(r'E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005')
NATIVE = ROOT / 'native'
BASE = Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
DLL = Path(r'C:\Users\Admin\AppData\Local\Programs\Microsoft VS Code\07f806f999')
ORDINARY = Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003\assets\turbo-console\snes.png')
OUT = ROOT / 'led-tests' / datetime.datetime.now().strftime('angle-%Y%m%d-%H%M%S')
P = C.c_void_p
U = C.c_uint
I = C.c_int
F = C.c_float
IDENTITY = (F*16)(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
VERTEX = '#version 100\nattribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;varying vec2 uv;void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;}'
PASSTHROUGH = '#version 100\nprecision highp float;varying vec2 uv;uniform sampler2D frame;void main(){gl_FragColor=texture2D(frame,uv);}'
REPORT = {'environment': 'Windows ANGLE offscreen GLES2; not Android hardware', 'output': str(OUT),
          'compile': [], 'gl_errors': [], 'artifacts': [], 'legacy': [], 'neo': [], 'square': [], 'controls': []}


def sha(data): return hashlib.sha256(data).hexdigest()


def bind(lib, name, result, args):
    fn = getattr(lib, name); fn.restype = result; fn.argtypes = args; return fn


class Angle:
    def __init__(self):
        self.dll_handle = os.add_dll_directory(str(DLL))
        self.egl = C.WinDLL(str(DLL/'libEGL.dll')); self.gl = C.WinDLL(str(DLL/'libGLESv2.dll'))
        self.error = bind(self.egl, 'eglGetError', I, [])
        self.display = bind(self.egl, 'eglGetDisplay', P, [P])(None)
        major=I();minor=I()
        assert bind(self.egl,'eglInitialize',U,[P,C.POINTER(I),C.POINTER(I)])(self.display,C.byref(major),C.byref(minor)),hex(self.error())
        assert bind(self.egl,'eglBindAPI',U,[U])(0x30A0)
        config=P();count=I();attrs=(I*15)(0x3033,1,0x3040,4,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3025,0,0x3038)
        assert bind(self.egl,'eglChooseConfig',U,[P,C.POINTER(I),C.POINTER(P),I,C.POINTER(I)])(self.display,attrs,C.byref(config),1,C.byref(count)) and count.value
        self.context=bind(self.egl,'eglCreateContext',P,[P,P,P,C.POINTER(I)])(self.display,config,None,(I*3)(0x3098,2,0x3038))
        self.surface=bind(self.egl,'eglCreatePbufferSurface',P,[P,P,C.POINTER(I)])(self.display,config,(I*5)(0x3057,1536,0x3056,1536,0x3038))
        assert self.context and self.surface,hex(self.error())
        self.current=bind(self.egl,'eglMakeCurrent',U,[P,P,P,P])
        assert self.current(self.display,self.surface,self.surface,self.context),hex(self.error())
        specs = {
            'GetString':(C.c_char_p,[U]),'GetError':(U,[]),'CreateShader':(U,[U]),
            'ShaderSource':(None,[U,I,C.POINTER(C.c_char_p),C.POINTER(I)]),'CompileShader':(None,[U]),
            'GetShaderiv':(None,[U,U,C.POINTER(I)]),'GetShaderInfoLog':(None,[U,I,C.POINTER(I),C.c_char_p]),
            'CreateProgram':(U,[]),'AttachShader':(None,[U,U]),'BindAttribLocation':(None,[U,U,C.c_char_p]),
            'LinkProgram':(None,[U]),'GetProgramiv':(None,[U,U,C.POINTER(I)]),
            'GetProgramInfoLog':(None,[U,I,C.POINTER(I),C.c_char_p]),'UseProgram':(None,[U]),
            'GetUniformLocation':(I,[U,C.c_char_p]),'Uniform1i':(None,[I,I]),'Uniform1f':(None,[I,F]),
            'Uniform4f':(None,[I,F,F,F,F]),'UniformMatrix4fv':(None,[I,I,C.c_ubyte,C.POINTER(F)]),
            'GenBuffers':(None,[I,C.POINTER(U)]),'BindBuffer':(None,[U,U]),'BufferData':(None,[U,C.c_size_t,P,U]),
            'VertexAttribPointer':(None,[U,I,U,C.c_ubyte,I,P]),'EnableVertexAttribArray':(None,[U]),
            'DisableVertexAttribArray':(None,[U]),'VertexAttrib4f':(None,[U,F,F,F,F]),
            'GenTextures':(None,[I,C.POINTER(U)]),'ActiveTexture':(None,[U]),'BindTexture':(None,[U,U]),
            'TexParameteri':(None,[U,U,I]),'PixelStorei':(None,[U,I]),
            'TexImage2D':(None,[U,I,I,I,I,I,U,U,P]),'Viewport':(None,[I,I,I,I]),
            'ClearColor':(None,[F,F,F,F]),'Clear':(None,[U]),'Disable':(None,[U]),
            'DrawArrays':(None,[U,I,I]),'ReadPixels':(None,[I,I,I,I,U,U,P]),'Finish':(None,[]),
        }
        for name,(result,args) in specs.items(): setattr(self,name,bind(self.gl,'gl'+name,result,args))
        REPORT['renderer']=self.GetString(0x1F01).decode();REPORT['version']=self.GetString(0x1F02).decode()
        REPORT['gl_extensions']=self.GetString(0x1F03).decode().split()
        REPORT['egl_extensions']=bind(self.egl,'eglQueryString',C.c_char_p,[P,I])(self.display,0x3055).decode().split()
        REPORT['egl_version']=[major.value,minor.value]
        getproc=bind(self.egl,'eglGetProcAddress',P,[C.c_char_p])
        def extension(name, result, args):
            address=getproc(name.encode());return C.WINFUNCTYPE(result,*args)(address) if address else None
        self.createImage=extension('eglCreateImageKHR',P,[P,P,U,P,C.POINTER(I)])
        self.imageTarget=extension('glEGLImageTargetTexture2DOES',None,[U,P])
        self.images=[]
        self.buffer=U();self.GenBuffers(1,C.byref(self.buffer));self.BindBuffer(0x8892,self.buffer)
        quad=(F*16)(-1,-1,0,0, 1,-1,1,0, -1,1,0,1, 1,1,1,1)
        self.BufferData(0x8892,C.sizeof(quad),quad,0x88E4)
        self.VertexAttribPointer(0,2,0x1406,False,16,None);self.VertexAttribPointer(1,2,0x1406,False,16,P(8))
        self.EnableVertexAttribArray(0);self.EnableVertexAttribArray(1);self.DisableVertexAttribArray(2)
        self.VertexAttrib4f(2,1,1,1,1)
        for setting in (0x0BE2,0x0B71,0x0BD0): self.Disable(setting)
        self.PixelStorei(0x0CF5,1);self.PixelStorei(0x0D05,1)
        self.check('initialize')

    def check(self,label):
        errors=[]
        while True:
            value=self.GetError()
            if not value:break
            errors.append(hex(value))
        REPORT['gl_errors'].append({'operation':label,'errors':errors})
        if errors: raise RuntimeError(label+': '+str(errors))

    def program(self,name,vertex,fragment):
        stages=[];entry={'name':name,'stages':[]}
        for stage,text in ((0x8B31,vertex),(0x8B30,fragment)):
            shader=self.CreateShader(stage);raw=text.encode();self.ShaderSource(shader,1,(C.c_char_p*1)(raw),None);self.CompileShader(shader)
            ok=I();self.GetShaderiv(shader,0x8B81,C.byref(ok));buf=C.create_string_buffer(32768)
            self.GetShaderInfoLog(shader,len(buf),None,buf)
            entry['stages'].append({'stage':'vertex' if stage==0x8B31 else 'fragment','sha256':sha(raw),'passed':bool(ok.value),'log':buf.value.decode('utf-8','replace')})
            stages.append(shader)
        program=self.CreateProgram()
        for shader in stages:self.AttachShader(program,shader)
        for index,attr in enumerate((b'VertexCoord',b'TexCoord',b'COLOR')):self.BindAttribLocation(program,index,attr)
        self.LinkProgram(program);ok=I();self.GetProgramiv(program,0x8B82,C.byref(ok));buf=C.create_string_buffer(32768)
        self.GetProgramInfoLog(program,len(buf),None,buf);entry['linked']=bool(ok.value);entry['log']=buf.value.decode('utf8','replace')
        REPORT['compile'].append(entry);self.check('compile '+name)
        if not ok.value:raise RuntimeError('Shader failed: '+name+' '+json.dumps(entry))
        return program

    def texture(self,pixels):
        self.ActiveTexture(0x84C0);texture=U();self.GenTextures(1,C.byref(texture));self.BindTexture(0x0DE1,texture)
        for field,value in ((0x2801,0x2601),(0x2800,0x2601),(0x2802,0x812F),(0x2803,0x812F)):self.TexParameteri(0x0DE1,field,value)
        bottom_first=np.ascontiguousarray(pixels[::-1]);h,w=bottom_first.shape[:2]
        self.TexImage2D(0x0DE1,0,0x1908,w,h,0,0x1908,0x1401,bottom_first.ctypes.data_as(P));self.check('upload '+str((w,h)))
        return texture.value

    def external(self,texture):
        if not self.createImage or not self.imageTarget:raise RuntimeError('ANGLE lacks EGLImage/OES interop entry points')
        self.Finish();image=self.createImage(self.display,self.context,0x30B1,P(texture),(I*5)(0x30BC,0,0x30D2,1,0x3038))
        if not image:raise RuntimeError('eglCreateImageKHR '+hex(self.error()))
        self.images.append(image);external=U();self.GenTextures(1,C.byref(external));self.BindTexture(0x8D65,external)
        for field,value in ((0x2801,0x2601),(0x2800,0x2601),(0x2802,0x812F),(0x2803,0x812F)):self.TexParameteri(0x8D65,field,value)
        self.imageTarget(0x8D65,image);self.check('EGLImage external texture');return external.value

    def render(self,program,texture,size,frame=0,model=3,sheen=.55,external=False):
        w,h=size;self.UseProgram(program);self.ActiveTexture(0x84C0);self.BindTexture(0x8D65 if external else 0x0DE1,texture)
        location=lambda name:self.GetUniformLocation(program,name.encode())
        for name in ('MVPMatrix','videoTransform'):self.UniformMatrix4fv(location(name),1,False,IDENTITY)
        self.Uniform1i(location('FrameCount'),frame)
        for name,value in (('saturation',1.),('ledGain',1.6),('sheenGain',sheen),('magazineModel',model),('neoPhase',((round(frame*1000/60)%10417)/10417)*3)):
            self.Uniform1f(location(name),value)
        self.Uniform4f(location('ledColor'),1.,24/255,38/255,1.)
        for name in ('frame','u_tex'):self.Uniform1i(location(name),0)
        self.Viewport(0,0,w,h);self.ClearColor(0,0,0,0);self.Clear(0x4000)
        start=time.perf_counter();self.DrawArrays(0x0005,0,4)
        pixels=np.empty((h,w,4),dtype=np.uint8);self.ReadPixels(0,0,w,h,0x1908,0x1401,pixels.ctypes.data_as(P));elapsed=(time.perf_counter()-start)*1000
        self.check('draw/read '+str(program)+' f'+str(frame)+' '+str(size))
        return pixels[::-1].copy(),elapsed


def save(name,pixels):
    file=OUT/(name+'.png');Image.fromarray(pixels).save(file)
    REPORT['artifacts'].append({'file':str(file),'pixel_sha256':sha(pixels.tobytes()),'size':[pixels.shape[1],pixels.shape[0]]})


def differences(a,b):
    delta=np.abs(a.astype(np.int16)-b.astype(np.int16))
    return {'pixel_byte_equal':bool(np.array_equal(a,b)),'max_channel_delta':int(delta.max()),
            'changed_pixels_gt1':int(np.any(delta[:,:,:3]>1,axis=2).sum()),'mean_channel_delta':float(delta.mean())}


def temporal(name,frames,baseline):
    arrays=np.stack(frames).astype(np.int16);maximum=arrays.max(0)-arrays.min(0)
    mask=np.max(maximum[:,:,:3],axis=2);save(name+'-temporal-mask',np.minimum(mask*8,255).astype(np.uint8))
    return {'frames':[0,60,120],'temporal_changed_pixels_gt1':int((mask>1).sum()),
            'temporal_max_delta':int(mask.max()),'versus_source':[differences(baseline,a) for a in frames]}


def diagnostic(source,main):
    start=source.rindex('void main() {')
    return source[:start]+main+'\n#endif\n'


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    REPORT['harness']={'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__).read_bytes()),
                       'python':sys.version,'numpy':np.__version__,'pillow':Image.__version__}
    REPORT['angle_dll_sha256']={name:sha((DLL/name).read_bytes()) for name in ('libEGL.dll','libGLESv2.dll')}
    shader=(NATIVE/'premium-magazine-led-android.glsl').read_text('utf8')
    old=(BASE/'premium-magazine-led-android.glsl').read_text('utf8')
    square=(NATIVE/'native_neogeocd_square.h').read_text('utf8')
    REPORT['loaded_sources']={str(path):sha(path.read_bytes()) for path in (NATIVE/'premium-magazine-led-android.glsl',BASE/'premium-magazine-led-android.glsl',NATIVE/'native_neogeocd_square.h')}
    start=shader.index('// Neo Geo magazine chassis');end=shader.index('void main() {',start)
    stripped=(shader[:start]+shader[end:]).replace('    if(magazineModel>2.5){FragColor=neoMagazine(base,p)*tint;return;}\n','')
    REPORT['legacy_retained_source_utf8_equal']=stripped.encode()==old.encode()
    REPORT['legacy_retained_source_sha256']=sha(stripped.encode())
    REPORT['legacy_baseline_source_sha256']=sha(old.encode())
    source_bytes=(NATIVE/'premium-magazine-led-android.glsl').read_bytes()
    old_bytes=(BASE/'premium-magazine-led-android.glsl').read_bytes()
    begin_bytes=source_bytes.index(b'// Neo Geo magazine chassis')
    end_bytes=source_bytes.index(b'void main() {',begin_bytes)
    retained=source_bytes[:begin_bytes]+source_bytes[end_bytes:]
    branch=next(line for line in retained.splitlines(True) if b'if(magazineModel>2.5)' in line)
    retained=retained.replace(branch,b'')
    REPORT['legacy_retained_bytes_exact_equal']=retained==old_bytes
    REPORT['legacy_retained_bytes_sha256']=sha(retained)
    gl=Angle();prefixV='#version 100\n#define VERTEX\n';prefixF='#version 100\n#define FRAGMENT\n'
    modern=gl.program('R20 magazine actual GLES100 models0/1/2/3',prefixV+shader,prefixF+shader)
    previous=gl.program('W16 magazine actual GLES100 models0/1/2',prefixV+old,prefixF+old)
    baseline=gl.program('source passthrough',VERTEX,PASSTHROUGH)
    raw={key:re.search(r'static const char '+key+r'\[\]=R"NEOSQ\((.*?)\)NEOSQ";',square,re.S).group(1)
         for key in ('neoSquareVertex','neoSquareFragment','neoSquareExternalFragment')}
    program2D=gl.program('R20 square actual sampler2D',raw['neoSquareVertex'],raw['neoSquareFragment'])
    programOES=gl.program('R20 square actual samplerExternalOES',raw['neoSquareVertex'],raw['neoSquareExternalFragment'])
    signature=gl.program('diagnostic Neo signature',prefixV+shader,prefixF+diagnostic(shader,'void main() { FragColor=vec4(vec3(neoSignature()),1.); }'))
    region=gl.program('diagnostic Neo geometry mask',prefixV+shader,prefixF+diagnostic(shader,'void main() {vec2 p=vec2(uv.x,1.-uv.y)*vec2(1024,1536);FragColor=vec4(vec3(neoRegion(p)),1.);}'))
    counted=shader.replace('vec4 sampleArt(vec2 p) { return TEX','float countedReads;\nvec4 sampleArt(vec2 p) { countedReads+=1.;return TEX')
    counterMain='void main() {countedReads=1.;vec4 b=TEX(u_tex,uv);vec2 p=vec2(uv.x,1.-uv.y)*vec2(1024,1536);vec4 c=neoMagazine(b,p);FragColor=vec4(countedReads/255.,c.a*0.,0.,1.);}'
    counter=gl.program('diagnostic source sampleArt call counter (not hardware fetch counter)',prefixV+counted,prefixF+diagnostic(counted,counterMain))
    refs={name:ROOT/'refs'/file for name,file in (
        ('svcplus','neogeo-svcplus.png'),('aof','neogeo-aof.png'),
        ('neogeocd-square','neogeocd-square.png'),('neogeocd-video','neogeocd-video-frame.png'))}
    refs['ordinary-console-photo']=ORDINARY
    REPORT['reference_inputs']={name:{'path':str(file),'sha256':sha(file.read_bytes())} for name,file in refs.items()}
    for name,file in refs.items():
        with Image.open(file) as image:pixels=np.array(image.convert('RGBA'))
        texture=gl.texture(pixels);h,w=pixels.shape[:2];size=(w,h) if name in ('svcplus','aof') else (min(w,1254),min(h,1254))
        actual,_=gl.render(baseline,texture,size);save(name+'-source-gl',actual)
        sig,_=gl.render(signature,texture,(1,1));sigValue=int(sig[0,0,0])/255
        if name in ('svcplus','aof'):
            frames=[];framesLED=[];times=[]
            for frame in (0,60,120):
                rendered,elapsed=gl.render(modern,texture,size,frame);frames.append(rendered);times.append(elapsed);save(name+'-f'+str(frame),rendered)
                leds,_=gl.render(modern,texture,size,frame,sheen=0);framesLED.append(leds);save(name+'-ledonly-f'+str(frame),leds)
            geometry,_=gl.render(region,texture,size);save(name+'-geometry-mask',geometry[:,:,0])
            reads,_=gl.render(counter,texture,size);counts,frequencies=np.unique(reads[:,:,0],return_counts=True)
            outside=geometry[:,:,0]==0
            # Exclude a three-source-pixel glow fringe around the measured geometry.
            expanded=~outside
            for axis in (0,1):
                originalMask=expanded.copy()
                for offset in range(-4,5): expanded|=np.roll(originalMask,offset,axis=axis)
            ledDelta=np.max(np.abs(np.stack(framesLED).astype(np.int16)-actual.astype(np.int16)),axis=(0,3))
            entry={'name':name,'source':str(file),'source_sha256':sha(file.read_bytes()),'source_dimensions':[w,h],
                   'signature_0_to_1':sigValue,'render_readback_ms':times,
                   'source_sample_calls_per_pixel':dict(zip(map(str,counts.tolist()),map(int,frequencies.tolist()))),
                   'led_changes_outside_expanded_chassis_gt1':int(((ledDelta>1)&~expanded).sum()),
                   **temporal(name,frames,actual),'led_only':temporal(name+'-ledonly',framesLED,actual)}
            # GPU resampling, no Pillow source edits: exercise signatures on a small card texture.
            small,_=gl.render(baseline,texture,(262,393));smallTexture=gl.texture(small)
            smallSig,_=gl.render(signature,smallTexture,(1,1));entry['signature_gpu262x393']=int(smallSig[0,0,0])/255
            smallFrames=[]
            for frame in (0,60,120):
                result,_=gl.render(modern,smallTexture,(262,393),frame);smallFrames.append(result);save(name+'-small-f'+str(frame),result)
            entry['gpu262x393']=temporal(name+'-small',smallFrames,small)
            REPORT['neo'].append(entry)
            cropFragment='#version 100\nprecision highp float;varying vec2 uv;uniform sampler2D frame;void main(){gl_FragColor=texture2D(frame,mix(vec2(.16,.20),vec2(.88,.82),uv));}'
            cropProgram=gl.program('ordinary game-art crop through GLES '+name,VERTEX,cropFragment)
            ordinary,_=gl.render(cropProgram,texture,(320,480));ordinaryTexture=gl.texture(ordinary)
            save(name+'-ordinary-art-gl',ordinary)
            ordinarySig,_=gl.render(signature,ordinaryTexture,(1,1));controlFrames=[]
            for frame in (0,60,120):
                control,_=gl.render(modern,ordinaryTexture,(320,480),frame)
                controlFrames.append(differences(ordinary,control))
            REPORT['controls'].append({'name':name+'-ordinary-game-art-GLES-crop','signature_0_to_1':int(ordinarySig[0,0,0])/255,
                                       'frames':[0,60,120],'versus_source':controlFrames})
            for model in (0,1,2):
                for frame in (0,60,120):
                    oldPixels,_=gl.render(previous,texture,(262,393),frame,model)
                    newPixels,_=gl.render(modern,texture,(262,393),frame,model)
                    REPORT['legacy'].append({'image':name,'model':model,'frame':frame,**differences(oldPixels,newPixels)})
        else:
            controls=[]
            for frame in (0,60,120):
                result,_=gl.render(modern,texture,size,frame);controls.append(differences(actual,result))
            REPORT['controls'].append({'name':name,'signature_0_to_1':sigValue,'frames':[0,60,120],'versus_source':controls})
            if name.startswith('neogeocd-'):
                ext=gl.external(texture);frames=[];equivalence=[]
                for frame in (0,60,120):
                    result,elapsed=gl.render(program2D,texture,size,frame);frames.append(result);save(name+'-2d-f'+str(frame),result)
                    resultOES,_=gl.render(programOES,ext,size,frame,external=True);save(name+'-oes-f'+str(frame),resultOES)
                    equivalence.append({'frame':frame,**differences(result,resultOES)})
                ys=(np.arange(size[1])+.5)*1254/size[1];xs=(np.arange(size[0])+.5)*1254/size[0]
                dots=(ys[:,None]>1205)&(xs[None,:]>460)&(xs[None,:]<765)
                changes=np.max(np.abs(np.stack(frames).astype(np.int16)-actual.astype(np.int16)),axis=(0,3))
                moving=np.max(np.stack(frames).astype(np.int16),axis=0)-np.min(np.stack(frames).astype(np.int16),axis=0)
                moving=np.max(moving[:,:,:3],axis=2)
                icon_counts=[]
                for left,right in ((53,149),(355,444),(635,723),(910,999)):
                    icon=(ys[:,None]>=950)&(ys[:,None]<=1044)&(xs[None,:]>=left)&(xs[None,:]<=right)
                    icon_counts.append(int(((moving>1)&icon).sum()))
                new_white=[int(((np.min(result[:,:,:3],axis=2)>=254)&(np.min(actual[:,:,:3],axis=2)<230)).sum()) for result in frames]
                REPORT['square'].append({'name':name,'source_dimensions':[w,h],
                    'source_texture_reads_static_2d':raw['neoSquareFragment'].count('texture2D('),
                    'source_texture_reads_static_oes':raw['neoSquareExternalFragment'].count('texture2D('),
                    'bottom_dot_region_changed_pixels_gt1':int(((changes>1)&dots).sum()),
                    'four_icons_temporal_changed_pixels_gt1':icon_counts,
                    'new_clipped_white_pixels_by_frame':new_white,
                    'oes_vs_2d':equivalence,**temporal(name,frames,actual)})
        print('rendered '+name+' signature='+str(sigValue),flush=True)
    REPORT['sources_unchanged_during_test']={path:sha(Path(path).read_bytes())==hashvalue for path,hashvalue in REPORT['loaded_sources'].items()}
    REPORT['passed']=(all(s['linked'] and all(t['passed'] for t in s['stages']) for s in REPORT['compile'])
        and REPORT['legacy_retained_source_utf8_equal'] and REPORT['legacy_retained_bytes_exact_equal'] and all(s['pixel_byte_equal'] for s in REPORT['legacy'])
        and all(s['signature_0_to_1']>.85 and s['signature_gpu262x393']>.85 and s['temporal_changed_pixels_gt1']>0 for s in REPORT['neo'])
        and all(s['temporal_changed_pixels_gt1']>0 and s['bottom_dot_region_changed_pixels_gt1']==0
                and all(n>0 for n in s['four_icons_temporal_changed_pixels_gt1'])
                and all(n==0 for n in s['new_clipped_white_pixels_by_frame'])
                and all(e['pixel_byte_equal'] for e in s['oes_vs_2d']) for s in REPORT['square'])
        and all(s['signature_0_to_1']<.01 and all(d['pixel_byte_equal'] for d in s['versus_source']) for s in REPORT['controls']))
    REPORT['limitations']=['ANGLE PC output does not establish Android device performance or visual approval.',
        'OES uses EGLImage-backed copies of real reference pixels, not a running Android MediaPlayer.',
        'Small-card textures are resampled by GLES passthrough; Android ImageIO resampling may differ.',
        'Sample counts are instrumented GLSL call counts, not GPU hardware cache/memory fetch counters.',
        'Preview PNG pixels are unaltered GL readbacks. Temporal masks are separate numerical diagnostics.']


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT,help='R20 directory containing native/ and refs/')
    parser.add_argument('--baseline',type=Path,default=BASE,help='W16 frontend-native directory')
    parser.add_argument('--angle-dll',type=Path,default=DLL,help='Directory containing libEGL.dll and libGLESv2.dll')
    parser.add_argument('--ordinary-control',type=Path,default=ORDINARY,help='Existing PNG without magazine chassis')
    parser.add_argument('--output',type=Path,help='New output directory; defaults to ROOT/led-tests/angle-TIMESTAMP')
    args=parser.parse_args()
    ROOT=args.root.resolve();NATIVE=ROOT/'native';BASE=args.baseline.resolve();DLL=args.angle_dll.resolve();ORDINARY=args.ordinary_control.resolve()
    OUT=args.output.resolve() if args.output else ROOT/'led-tests'/datetime.datetime.now().strftime('angle-%Y%m%d-%H%M%S')
    REPORT['output']=str(OUT)
    try: main()
    except Exception as error:
        REPORT['exception']=repr(error);REPORT['passed']=False
        raise
    finally:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'report.json').write_text(json.dumps(REPORT,indent=2)+'\n',encoding='utf8')
        (ROOT/'led-tests'/'latest.json').write_text(json.dumps({'output':str(OUT),'passed':REPORT.get('passed',False)},indent=2)+'\n',encoding='utf8')
        print(json.dumps({'output':str(OUT),'passed':REPORT.get('passed',False),'exception':REPORT.get('exception')},indent=2),flush=True)
