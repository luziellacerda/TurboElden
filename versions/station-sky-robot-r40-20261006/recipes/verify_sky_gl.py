from pathlib import Path
import sys,re,json,ctypes as C,os
import numpy as np
W=Path(__file__).resolve().parent;os.environ['TEMP']=os.environ['TMP']=str(W/'temp');sys.path.insert(0,str(W/'tests'));import angle_helper as H
if not H.DLL.exists():
 candidates=list(Path(r'C:\Users\Admin\AppData\Local\Programs\Microsoft VS Code').glob('*/libEGL.dll'));assert candidates;H.DLL=candidates[-1].parent
g=H.Angle();src=(W/'native/native_space3d.h').read_text('utf8');old=(Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006')/'native/native_space3d.h').read_text('utf8')
def cpp(s,name):return json.loads('"'+re.search(r'const char\*'+name+r'="(.*?)";',s).group(1)+'"')
p=g.program('R40 neutral white clouds, original black preserved',cpp(src,'cv'),cpp(src,'cf'));o=g.program('R39 black reference',cpp(old,'cv'),cpp(old,'cf'))
pixels=np.zeros((64,64,4),dtype=np.uint8)
for y in range(64):
 for x in range(64):
  alpha=4+x*3;level=y/63
  pixels[y,x]=[int(alpha*level*.9),int(alpha*level),int(alpha*min(level*1.02,1)),alpha]
tex=g.texture(pixels)
def render(program,theme):
 g.UseProgram(program);g.ActiveTexture(0x84c0);g.BindTexture(0x0de1,tex);g.UniformMatrix4fv(g.GetUniformLocation(program,b'MVPMatrix'),1,False,H.IDENTITY);g.Uniform1i(g.GetUniformLocation(program,b'scene'),0);g.Uniform1f(g.GetUniformLocation(program,b'opacity'),1);g.Uniform1f(g.GetUniformLocation(program,b'themeBlue'),theme);g.Viewport(0,0,64,64);g.DrawArrays(5,0,4);g.Finish();out=np.zeros((64,64,4),dtype=np.uint8);g.ReadPixels(0,0,64,64,0x1908,0x1401,out.ctypes.data_as(C.c_void_p));g.check('read theme '+str(theme));return out
baseline=render(o,0);black=render(p,0);white=render(p,1);back=render(p,0)
assert np.array_equal(baseline,black) and np.array_equal(black,back)
assert np.array_equal(white[:,:,3],black[:,:,3]);assert int(white[:,:,:3].min())>=172
assert np.all(white[:,:,0].astype(int)>=white[:,:,2].astype(int)*.85)
assert not np.array_equal(white,black)
result={'passed':True,'renderer':H.REPORT['renderer'],'compile':H.REPORT['compile'],'errors':H.REPORT['gl_errors'],'pixels':4096,'blackMatchesR39ByteForByte':True,'alphaPreserved':True,'blueThemeCloudMinimumRGB':int(white[:,:,:3].min()),'whiteShadingNotBlueTint':True,'androidVisualValidation':False}
(W/'evidence/sky-gles.json').write_text(json.dumps(result,indent=2),'utf8');print('PASS GLES2 actual cloud compositor: 4096 samples; white shading, same alpha, black byte-identical to R39')
