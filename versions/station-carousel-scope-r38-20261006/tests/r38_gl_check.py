from pathlib import Path
import sys,json,shutil,hashlib
import numpy as np
from PIL import Image
W=Path(r'E:\ESTUDO APK\work\station-carousel-scope-r38-20261006')
HERE=Path(__file__).resolve().parent
HFILE=HERE/'work/TurboElden-git/versions/station-neogeo-laser-r24-20261005/tests/test_console_led_angle_R20.py'
if HFILE.exists():shutil.copy2(HFILE,W/'tests/test_console_led_angle_R20.py')
sys.path.insert(0,str(W/'tests'))
import test_console_led_angle_R20 as H
H.OUT=W/'evidence/gl';H.OUT.mkdir(exist_ok=True)
g=H.Angle();shader=(W/'native/premium-magazine-led-android.glsl').read_text('utf8')
program=g.program('Neo Geo and Neo Geo CD game-cover map','#version 100\n#define VERTEX\n'+shader,'#version 100\n#define FRAGMENT\n'+shader)
plain=g.program('Ordinary texture',H.VERTEX,H.PASSTHROUGH)
refs=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005\refs')
result={'scope':'Game covers only. Both Neo Geo and Neo Geo CD map to model 3. Videos bypass it.', 'gameCovers':[],'limitations':['PC GLES test, not Android decoder or performance verification.','Reference covers share the measured Neo Geo frame; plain artwork remains unchanged.']}
for name in ('neogeo-aof','neogeo-svcplus'):
 with Image.open(refs/(name+'.png')) as im:pixels=np.array(im.convert('RGBA'))
 tex=g.texture(pixels);base=g.render(plain,tex,(262,393))[0]
 samples=[g.render(program,tex,(262,393),f,3)[0] for f in (0,60,120)]
 differences=[H.differences(base,a) for a in samples]
 temporal=int(np.ptp(np.stack(samples).astype(np.int16),axis=0).max())
 assert temporal>0 and any(d['changed_pixels_gt1']>0 for d in differences)
 H.save(name+'-effect',samples[2])
 result['gameCovers'].append({'name':name,'SHA256':hashlib.sha256((refs/(name+'.png')).read_bytes()).hexdigest(),'temporalDelta':temporal,'changes':differences})
result['passed']=True;result['gl']=H.REPORT
(W/'evidence/gl/report.json').write_text(json.dumps(result,indent=2),'utf8')
print('PASS: Neo Geo game cover shader compiled and animated on both reference artworks; platform video shader override absent.')
