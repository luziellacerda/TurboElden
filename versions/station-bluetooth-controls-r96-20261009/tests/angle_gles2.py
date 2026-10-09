"""Offscreen GLES2 ctypes infrastructure copied from the existing ANGLE harness.
No historical shader, recipe, APK or reference path is loaded here.
The R80 driver supplies the candidate and frozen R79 baseline explicitly.
"""
from pathlib import Path
import ctypes as C
import hashlib
import json
import os
import time
import numpy as np
DLL = Path(r'C:\Users\Admin\AppData\Local\Programs\Microsoft VS Code\07f806f999')
P = C.c_void_p
U = C.c_uint
I = C.c_int
F = C.c_float
IDENTITY = (F*16)(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
VERTEX = '#version 100\nattribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;varying vec2 uv;void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;}'
PASSTHROUGH = '#version 100\nprecision highp float;varying vec2 uv;uniform sampler2D frame;void main(){gl_FragColor=texture2D(frame,uv);}'
REPORT = {'compile': [], 'gl_errors': []}


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
