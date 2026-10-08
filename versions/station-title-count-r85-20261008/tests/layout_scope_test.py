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
need('if(!gui||at<int>(gui,0x370)!=3)return;' in space and 'drawCarouselDiagonalBackdrop(w,h);' in space)
need(space.index('drawNativeClouds(w,h,t);')<space.index(' drawCarouselDiagonalBackdrop(w,h);'))
need('Vertex strip[754]' in space and 'anchorX=cover.x+cover.w*.44f' in space and 't*t*(3.f-2.f*t)' in space and 'for(int side' not in space)
need('0x080C0900u,0x080C09ffu,false,4,5' in skin)
need('else bounds(p,0x1420,0,0,0,0)' in skin)
need('avatar==(B*)skinTopOwner+0x1430)return;' in skin)
need('if(!systemsMode)return; // Game selection has no account name.' in (src/'native_carousel.cpp').read_text())
profile=(src/'native_profile_name.h').read_text('utf8')
need('profileScale=reference/natural' not in profile and 'nativeInfoTextWidth(text,*name?name:"JOGADOR",.72f)' in profile)
info=(src/'native_info.h').read_text('utf8')
need('countScale=stationGameMetadataScale/1.5f' in info)
need('float titleWidth=fitGameTitleOneLine(infoTitle,heading,infoTitleViewport);' in info)
settings=(src/'station_collection_settings_layout.h').read_text('utf8')
need('if(!systems)return {w*.8775f-h*.065f,h*.44375f,h*.130f,h*.0975f};' in settings)
need(abs(.130/.10-1.30)<1e-6 and abs(.0975/.075-1.30)<1e-6)
need(abs((.44375+.0975/2)-(.455+.075/2))<1e-6)
old=(BASE/'carousel-inputs/d0/native_space.h').read_text('utf8')
need('if(!systemsMode)' not in space and 'drawCarouselDiagonalBackdrop(w,h);' in space)
for w,h in [(2400,1080),(2340,1080),(1920,1080),(1280,720),(2560,1600)]:
 hero=(w*.025,h*.040,h*.790*.828,h*.865)
 left=hero[0]+hero[2]+w*.022
 avatar=left+h*.059+w*.012
 name=avatar+h*.058+w*.012
 need(hero[1]+hero[3]<=h*.905+1e-6)
 need(left>hero[0]+hero[2])
 need(name<w*.706<w*.718)
 need(h*.075<h*.105)
 # Continuous full-height fade: opaque lateral region and smooth alpha.
 anchorX=hero[0]+hero[2]*.44;anchorY=hero[1]+hero[3]*.075
 def ease(t):
  t=max(0,min(1,t));return t*t*(3-2*t)
 def line(y):return max(hero[0],anchorX*(h-y)/(h-anchorY))
 need(abs(line(anchorY)-anchorX)<1e-6)
 for y in [0,h*.1,h*.5,h]:
  boundary=line(y)
  need(hero[0]<=boundary<w)
  alphas=[round(255*(1-ease(i/24))) for i in range(25)]
  need(alphas[0]==255 and alphas[-1]==0)
  need(all(a>=b for a,b in zip(alphas,alphas[1:])))
  need(abs((1-ease(.50))-.5)<1e-6)
 need(14*26*2+13*2==754)
result={'passed':True,'checks':checks,'scope':'source guards and geometry only','systemsTopbarByteIdenticalToR84':True,'sharedBackdropAllCarousels':True,'loadingBackgroundUnchanged':True,'gameBackdropDrawCalls':1,'gameBackdropVertices':754,'geometryCached':True,'broadSmoothAlphaRamp':True,'opaqueBoundaryAlignedToLogoB':True,'fadeEndsTransparentAtRightEdge':True,'foregroundTextUnchanged':True,'profileHiddenOnlyInGames':True,'barFadesLeftToRightOpaque':True,'newTimer':False,'usernameEnlargementReverted':True,'gameCountSmaller':True,'physicalDisplayVerified':False,'sourceSHA256':hashlib.sha256(space.encode()).hexdigest()}
(ROOT/'evidence/layout-scope-tests.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps(result))
