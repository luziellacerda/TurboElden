"""Compile actual GLES100 sources in a local ANGLE pbuffer; never touches a browser."""
from pathlib import Path
import ctypes as C, hashlib, json, os, re
ROOT=Path(__file__).resolve().parent
DLL=Path(r'C:\Users\Admin\AppData\Local\Programs\Microsoft VS Code\07f806f999')
def bind(lib,name,result,args):
 f=getattr(lib,name);f.restype=result;f.argtypes=args;return f
def main():
 handle=os.add_dll_directory(str(DLL))
 egl=C.WinDLL(str(DLL/'libEGL.dll'));gl=C.WinDLL(str(DLL/'libGLESv2.dll'))
 ptr=C.c_void_p;u=C.c_uint;i=C.c_int
 getDisplay=bind(egl,'eglGetDisplay',ptr,[ptr]);initialize=bind(egl,'eglInitialize',u,[ptr,C.POINTER(i),C.POINTER(i)])
 error=bind(egl,'eglGetError',i,[])
 display=getDisplay(None);major=i();minor=i();assert initialize(display,C.byref(major),C.byref(minor)),hex(error())
 api=bind(egl,'eglBindAPI',u,[u]);assert api(0x30A0)
 choose=bind(egl,'eglChooseConfig',u,[ptr,C.POINTER(i),C.POINTER(ptr),i,C.POINTER(i)])
 attrs=(i*15)(0x3033,1,0x3040,4,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3025,0,0x3038)
 config=ptr();count=i();assert choose(display,attrs,C.byref(config),1,C.byref(count)) and count.value
 context=bind(egl,'eglCreateContext',ptr,[ptr,ptr,ptr,C.POINTER(i)])(display,config,None,(i*3)(0x3098,2,0x3038));assert context,hex(error())
 surface=bind(egl,'eglCreatePbufferSurface',ptr,[ptr,ptr,C.POINTER(i)])(display,config,(i*5)(0x3057,1,0x3056,1,0x3038));assert surface,hex(error())
 current=bind(egl,'eglMakeCurrent',u,[ptr,ptr,ptr,ptr]);assert current(display,surface,surface,context),hex(error())
 getString=bind(gl,'glGetString',C.c_char_p,[u])
 precision=bind(gl,'glGetShaderPrecisionFormat',None,[u,u,C.POINTER(i),C.POINTER(i)])
 formats={}
 for stageName,stage in [('vertex',0x8b31),('fragment',0x8b30)]:
  for levelName,level in [('mediump-int',0x8df4),('highp-int',0x8df5)]:
   ranges=(i*2)();bits=i();precision(stage,level,ranges,C.byref(bits))
   formats[stageName+'/'+levelName]={'rangeExponents':list(ranges),'precision':bits.value}
 create=bind(gl,'glCreateShader',u,[u]);source=bind(gl,'glShaderSource',None,[u,i,C.POINTER(C.c_char_p),C.POINTER(i)])
 compile=bind(gl,'glCompileShader',None,[u]);query=bind(gl,'glGetShaderiv',None,[u,u,C.POINTER(i)])
 log=bind(gl,'glGetShaderInfoLog',None,[u,i,C.POINTER(i),C.c_char_p])
 createProgram=bind(gl,'glCreateProgram',u,[]);attach=bind(gl,'glAttachShader',None,[u,u]);link=bind(gl,'glLinkProgram',None,[u])
 attrib=bind(gl,'glBindAttribLocation',None,[u,u,C.c_char_p]);queryProgram=bind(gl,'glGetProgramiv',None,[u,u,C.POINTER(i)])
 programLog=bind(gl,'glGetProgramInfoLog',None,[u,i,C.POINTER(i),C.c_char_p])
 deleteShader=bind(gl,'glDeleteShader',None,[u]);deleteProgram=bind(gl,'glDeleteProgram',None,[u])
 tests=[]
 def program(name,vertex,fragment,probe=False):
  stages=[];report={'name':name,'stages':[]}
  for kind,text in [(0x8b31,vertex),(0x8b30,fragment)]:
   shader=create(kind);raw=text.encode('utf8');source(shader,1,(C.c_char_p*1)(raw),None);compile(shader)
   ok=i();query(shader,0x8b81,C.byref(ok));buf=C.create_string_buffer(16384);log(shader,len(buf),None,buf)
   report['stages'].append({'stage':'vertex' if kind==0x8b31 else 'fragment','sha256':hashlib.sha256(raw).hexdigest(),'passed':bool(ok.value),'log':buf.value.decode('utf8','replace')});stages.append(shader)
  prog=createProgram()
  for shader in stages:attach(prog,shader)
  for index,name in enumerate([b'VertexCoord',b'TexCoord',b'COLOR']):attrib(prog,index,name)
  link(prog);ok=i();queryProgram(prog,0x8b82,C.byref(ok));buf=C.create_string_buffer(16384);programLog(prog,len(buf),None,buf)
  report['linked']=bool(ok.value);report['linkLog']=buf.value.decode('utf8','replace');tests.append(report)
  if probe and ok.value:
   use=bind(gl,'glUseProgram',None,[u]);use(prog)
   uniform=bind(gl,'glGetUniformLocation',i,[u,C.c_char_p])(prog,b'FrameCount')
   setUniform=bind(gl,'glUniform1i',None,[i,i])
   generate=bind(gl,'glGenBuffers',None,[i,C.POINTER(u)]);buffer=u();generate(1,C.byref(buffer))
   bindBuffer=bind(gl,'glBindBuffer',None,[u,u]);bindBuffer(0x8892,buffer)
   triangle=(C.c_float*6)(-1,-1,3,-1,-1,3)
   bind(gl,'glBufferData',None,[u,C.c_size_t,ptr,u])(0x8892,C.sizeof(triangle),triangle,0x88e4)
   bind(gl,'glVertexAttribPointer',None,[u,i,u,C.c_ubyte,i,ptr])(0,2,0x1406,False,8,None)
   bind(gl,'glEnableVertexAttribArray',None,[u])(0)
   bind(gl,'glViewport',None,[i,i,i,i])(0,0,1,1)
   draw=bind(gl,'glDrawArrays',None,[u,i,i]);read=bind(gl,'glReadPixels',None,[i,i,i,i,u,u,ptr])
   getError=bind(gl,'glGetError',u,[]);report['frameSamples']=[]
   for frame in [0,32767,65535,1000000]:
    setUniform(uniform,frame);draw(4,0,3);pixel=(C.c_ubyte*4)();read(0,0,1,1,0x1908,0x1401,pixel)
    expected=[round(frame%625/624*255),round(frame%360/359*255),round((frame//625)%251/250*255),255]
    glerror=getError();good=glerror==0 and all(abs(a-b)<=1 for a,b in zip(pixel,expected))
    report['frameSamples'].append({'frame':frame,'rgba':list(pixel),'expected':expected,'glError':glerror,'passed':good})
   bind(gl,'glDisableVertexAttribArray',None,[u])(0);bindBuffer(0x8892,0)
   bind(gl,'glDeleteBuffers',None,[i,C.POINTER(u)])(1,C.byref(buffer));use(0)
  for shader in stages:deleteShader(shader)
  deleteProgram(prog)
 shader=(ROOT/'native/premium-magazine-led-android.glsl').read_text('utf8')
 program('premium-magazine-led actual GLES100','#version 100\n#define VERTEX\n'+shader,'#version 100\n#define FRAGMENT\n'+shader)
 console=(ROOT/'native/native_console.h').read_text('utf8')
 v,f=[json.loads('"'+re.search('const char\\*'+key+'="(.*?)";',console).group(1)+'"') for key in ['vertex','fragment']]
 program('console actual GLES100',v,f)
 probeVertex='#version 100\nattribute vec2 VertexCoord;void main(){gl_Position=vec4(VertexCoord,0.0,1.0);}'
 probeFragment='#version 100\nprecision highp float;precision highp int;uniform int FrameCount;void main(){float a=float(FrameCount-((FrameCount/625)*625))/624.0;float b=mod(float(FrameCount),360.0)/359.0;int cycles=FrameCount/625;float c=float(cycles-((cycles/251)*251))/250.0;gl_FragColor=vec4(a,b,c,1.0);}'
 program('isolated highp FrameCount arithmetic probe',probeVertex,probeFragment,True)
 report={'environment':'Windows local ANGLE offscreen pbuffer, not Android hardware','dllDirectory':str(DLL),'eglVersion':[major.value,minor.value],'renderer':getString(0x1F01).decode(),'version':getString(0x1F02).decode(),'integerPrecision':formats,'tests':tests,'passed':all(t['linked'] and all(s['passed'] for s in t['stages']) and all(s['passed'] for s in t.get('frameSamples',[])) for t in tests)}
 (ROOT/'evidence/shader-angle-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
 print(json.dumps(report,indent=2));current(display,None,None,None)
 bind(egl,'eglDestroySurface',u,[ptr,ptr])(display,surface);bind(egl,'eglDestroyContext',u,[ptr,ptr])(display,context);bind(egl,'eglTerminate',u,[ptr])(display)
 assert report['passed']
if __name__=='__main__':main()
