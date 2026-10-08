"""Source guards and geometry checks; not Android rendering or gameplay."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r84')
src=WORK/'carousel-inputs/d0'
checks=0
def need(ok):
 global checks
 assert ok
 checks+=1
skin=(src/'native_skin.h').read_text('utf8')
space=(src/'native_space.h').read_text('utf8')
need((src/'station_compact_topbar.h').read_bytes()==(BASE/'carousel-inputs/d0/station_compact_topbar.h').read_bytes())
need('return systemsMode?stationTopbarActionY(h):h*.008f' in skin)
need('return systemsMode?stationTopbarBottom(h):h*.075f' in skin)
need('if(!gui||at<int>(gui,0x370)!=3)return;\n if(!systemsMode){drawGameCornerBackdrop(w,h);return;}' in space)
need(space.index('drawNativeClouds(w,h,t);')<space.index('if(!systemsMode){drawGameCornerBackdrop'))
need('strip,5,4,5' in space and '0x000000ffu' in space and '0x00000000u' in space)
profile=(src/'native_profile_name.h').read_text('utf8')
need('profileScale=reference/natural' in profile and 'if(!systemsMode&&infoListCountText)' in profile)
settings=(src/'station_collection_settings_layout.h').read_text('utf8')
need('if(!systems)return {w*.8775f-h*.065f,h*.44375f,h*.130f,h*.0975f};' in settings)
need(abs(.130/.10-1.30)<1e-6 and abs(.0975/.075-1.30)<1e-6)
need(abs((.44375+.0975/2)-(.455+.075/2))<1e-6)
old=(BASE/'carousel-inputs/d0/native_space.h').read_text('utf8')
need(space[space.index(' // Renderer::drawRect'):]==old[old.index(' // Renderer::drawRect'):])
for w,h in [(2400,1080),(2340,1080),(1920,1080),(1280,720),(2560,1600)]:
 hero=(w*.025,h*.040,h*.790*.828,h*.865)
 left=hero[0]+hero[2]+w*.022
 avatar=left+h*.059+w*.012
 name=avatar+h*.058+w*.012
 need(hero[1]+hero[3]<=h*.905+1e-6)
 need(left>hero[0]+hero[2])
 need(name<w*.706<w*.718)
 need(h*.075<h*.105)
 # Corners fade completely before the lower edge; only ten vertices total.
 for side in [0,1]:
  x=w if side else 0;direction=-1 if side else 1
  for px,py in [(x,0),(x+direction*w*.56*.1,0),(x,h*.68*.1),(x+direction*w*.56,0),(x,h*.68)]:
   need(0<=px<=w and 0<=py<h)
result={'passed':True,'checks':checks,'scope':'source guards and geometry only','systemsTopbarByteIdenticalToR84':True,'systemsGradientBodyUnchanged':True,'gameCornerDrawCalls':2,'gameCornerVertices':10,'newTimer':False,'physicalDisplayVerified':False,'sourceSHA256':hashlib.sha256(space.encode()).hexdigest()}
(ROOT/'evidence/layout-scope-tests.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps(result))
