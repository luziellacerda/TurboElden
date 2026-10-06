from pathlib import Path
import sys,re,json,shutil,ctypes as C
import numpy as np
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');T=W/'tests'
helper=Path('work/TurboElden-git/versions/station-neogeo-laser-r24-20261005/tests/test_console_led_angle_R20.py')
shutil.copy2(helper,T/'angle_helper.py');sys.path.insert(0,str(T));import angle_helper as H
# Locate installed runtime libraries; no install or download needed.
if not H.DLL.exists():
 candidates=list(Path(r'C:\Users\Admin\AppData\Local\Programs\Microsoft VS Code').glob('*/libEGL.dll'))
 assert candidates;H.DLL=candidates[-1].parent
g=H.Angle();src=(W/'native/native_space3d.h').read_text('utf8')
def cpp(name):return json.loads('"'+re.search(r'const char\*'+name+r'="(.*?)";',src).group(1)+'"')
p=g.program('R39 existing cloud composite with theme uniform',cpp('cv'),cpp('cf'));g.UseProgram(p)
g.UniformMatrix4fv(g.GetUniformLocation(p,b'MVPMatrix'),1,False,H.IDENTITY)
g.Uniform1i(g.GetUniformLocation(p,b'scene'),0);g.Uniform1f(g.GetUniformLocation(p,b'opacity'),1)
texture=H.U();g.GenTextures(1,C.byref(texture));g.ActiveTexture(0x84C0);g.BindTexture(0x0DE1,texture)
for name,value in [(0x2801,0x2600),(0x2800,0x2600),(0x2802,0x812F),(0x2803,0x812F)]:g.TexParameteri(0x0DE1,name,value)
pixel=(C.c_ubyte*4)(30,60,90,128);g.TexImage2D(0x0DE1,0,0x1908,1,1,0,0x1908,0x1401,pixel);g.Viewport(0,0,8,8)
readbacks=[]
for theme in [0,1,0]:
 g.Uniform1f(g.GetUniformLocation(p,b'themeBlue'),theme);g.DrawArrays(5,0,4);g.Finish();out=np.zeros((8,8,4),dtype=np.uint8);g.ReadPixels(0,0,8,8,0x1908,0x1401,out.ctypes.data_as(C.c_void_p));g.check('theme-'+str(theme));readbacks.append(out)
assert np.array_equal(readbacks[0],readbacks[2]);assert np.all(readbacks[0][:,:,3]==readbacks[1][:,:,3]);assert np.all(readbacks[1][:,:,2]>readbacks[1][:,:,1]);assert np.all(readbacks[1][:,:,1]>readbacks[1][:,:,0]);assert not np.array_equal(readbacks[0],readbacks[1])
report={'environment':H.REPORT['renderer'],'compile':H.REPORT['compile'],'errors':H.REPORT['gl_errors'],'pixels':[a[0,0].tolist() for a in readbacks],'roundTripByteExact':True,'alphaPreserved':True,'phoneGPUTest':False}
(W/'evidence/theme-gles-test.json').write_text(json.dumps(report,indent=2),'utf8');print('PASS actual GLES2 cloud composite: blue tint, unchanged alpha and byte-identical black round trip')
