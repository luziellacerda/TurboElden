from pathlib import Path
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
s=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003\test_shader_angle.py').read_text('utf8')
s=s.replace('def program(name,vertex,fragment,probe=False):','def program(name,vertex,fragment,probe=False,video=False):')
anchor='  for shader in stages:deleteShader(shader)'
block='''  if video and ok.value:
   bind(gl,'glUseProgram',None,[u])(prog)
   location=bind(gl,'glGetUniformLocation',i,[u,C.c_char_p])
   matrix=(C.c_float*16)(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
   bind(gl,'glUniformMatrix4fv',None,[i,i,C.c_ubyte,C.POINTER(C.c_float)])(location(prog,b'MVPMatrix'),1,False,matrix)
   bind(gl,'glUniform1i',None,[i,i])(location(prog,b'frame'),0)
   bind(gl,'glActiveTexture',None,[u])(0x84c0)
   tex=u();bind(gl,'glGenTextures',None,[i,C.POINTER(u)])(1,C.byref(tex))
   bind(gl,'glBindTexture',None,[u,u])(0x0de1,tex)
   data=(ROOT/'video/previews/720-snes.rgb565').read_bytes();pixels=C.create_string_buffer(data)
   bind(gl,'glTexImage2D',None,[u,i,i,i,i,i,u,u,ptr])(0x0de1,0,0x1907,720,720,0,0x1907,0x8363,pixels)
   texparam=bind(gl,'glTexParameteri',None,[u,u,i])
   for key,val in [(0x2801,0x2600),(0x2800,0x2600),(0x2802,0x812f),(0x2803,0x812f)]:texparam(0x0de1,key,val)
   buffer=u();bind(gl,'glGenBuffers',None,[i,C.POINTER(u)])(1,C.byref(buffer))
   bind(gl,'glBindBuffer',None,[u,u])(0x8892,buffer)
   # A whole-surface triangle, sampling the centre of one exact preview texel.
   uv=360.5/720
   triangle=(C.c_float*12)(-1,-1,uv,uv,3,-1,uv,uv,-1,3,uv,uv)
   bind(gl,'glBufferData',None,[u,C.c_size_t,ptr,u])(0x8892,C.sizeof(triangle),triangle,0x88e4)
   attr=bind(gl,'glVertexAttribPointer',None,[u,i,u,C.c_ubyte,i,ptr])
   attr(0,2,0x1406,False,16,None);attr(1,2,0x1406,False,16,ptr(8))
   enable=bind(gl,'glEnableVertexAttribArray',None,[u]);enable(0);enable(1)
   bind(gl,'glViewport',None,[i,i,i,i])(0,0,1,1)
   bind(gl,'glDrawArrays',None,[u,i,i])(4,0,3)
   pixel=(C.c_ubyte*4)();bind(gl,'glReadPixels',None,[i,i,i,i,u,u,ptr])(0,0,1,1,0x1908,0x1401,pixel)
   offset=(360*720+360)*2;packed=int.from_bytes(data[offset:offset+2],'little')
   expected=[round((packed>>11)*255/31),round(((packed>>5)&63)*255/63),round((packed&31)*255/31),255]
   glerror=bind(gl,'glGetError',u,[])()
   good=glerror==0 and all(abs(a-b)<=2 for a,b in zip(pixel,expected))
   report['frameSamples']=[{'rgba':list(pixel),'expected':expected,'glError':glerror,'passed':good}]
   disable=bind(gl,'glDisableVertexAttribArray',None,[u]);disable(0);disable(1)
   bind(gl,'glDeleteTextures',None,[i,C.POINTER(u)])(1,C.byref(tex));bind(gl,'glDeleteBuffers',None,[i,C.POINTER(u)])(1,C.byref(buffer))
'''
assert anchor in s;s=s.replace(anchor,block+anchor)
anchor=" probeVertex='#version 100"
assert anchor in s
insert=''' video_source=(ROOT/'native/native_system_video720.h').read_text('utf8')
 v,f=[json.loads('"'+re.search('const char\\\\*'+key+'="(.*?)";',video_source).group(1)+'"') for key in ['vertex','fragment']]
 program('video retained preview actual GLES100 and real RGB565 pixel',v,f,video=True)
'''
s=s.replace(anchor,insert+anchor)
(R/'test_shader_angle.py').write_text(s,encoding='utf8')
print('Prepared actual R5 preview shader test')
