"""Isolated current native allocator proof; no Android, GL device or decoder."""
from pathlib import Path
import hashlib,json,re,subprocess,zipfile
from datetime import datetime,timezone

SNAP=Path(__file__).resolve().parents[1]
ROOT=SNAP.parents[1]
SOURCE=SNAP/'native/d0/native_system_video720.h'
PRIVATE=SNAP/'.validation-r124/video-budget'
PRIVATE.mkdir(exist_ok=True,parents=True)
CLANG=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
BASELINE='76a8e34a1aa202dd277f0a1ed043beb436629209'
INPUTS=Path(r'E:\ESTUDO APK\work\station-game-menu-controller-audit-r120-20261010\compiled-final\native-inputs')

def raw(path):return Path('\\\\?\\'+str(path.resolve())).read_bytes()
def body(source,name):
    found=re.search(r'static [^\n;]*\b'+re.escape(name)+r'\([^\n]*?\)\{',source)
    assert found,name
    start=source.index('{',found.start());end=start+1;depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[found.start():end]
def run(args):
    result=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf-8')
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    return result.stdout.strip()

source=raw(SOURCE).decode('utf8').replace('\r\n','\n')
legacy=run(['git','-c','core.longpaths=true','-c','safe.directory='+str(ROOT).replace('\\','/'),'-C',ROOT,'show',BASELINE+':versions/station-carousel-diagonal-online-compact-r123-20261011/native/d0/native_system_video720.h'])
legacy_alloc=body(legacy,'video720FrameTexture').replace('video720FrameTexture(', 'legacyVideo720FrameTexture(')
policy=raw(INPUTS/'d1/video720_policy.h')
definitions=raw(INPUTS/'d1/system_video720_assets.h')
manifest=json.loads(raw(SNAP/'CAROUSEL-INPUT-MANIFEST.json'))
assert hashlib.sha256(policy).hexdigest()==manifest['d1/video720_policy.h']
assert hashlib.sha256(definitions).hexdigest()==manifest['d1/system_video720_assets.h']
assert b'video720TextureBudget=8' in policy
posters=raw(SNAP/'native/d0/video720_posters.h')
poster_assets=set(re.findall(rb'\{"(turbo-system-videos/[^\"]+)"',posters))
system_assets=set(re.findall(rb'\{"[^\"]+","(turbo-system-videos/[^\"]+)"',definitions))
collection_assets=set(re.findall(rb'"(turbo-system-videos/[^\"]+)"',raw(SNAP/'native/d0/collection_video_policy.h')))
assert system_assets<=poster_assets,(system_assets-poster_assets)
assert collection_assets<=poster_assets,(collection_assets-poster_assets)
status=json.loads(raw(SNAP/'baseline-r123/STATUS.json'))
with zipfile.ZipFile(status['apk']) as archive:
    names=set(archive.namelist())
    assert all('assets/'+asset.decode() in names for asset in system_assets|collection_assets)

prelude=r'''
#include <cassert>
#include <cstring>
#include <string>
#include <iostream>
static constexpr unsigned video720TextureBudget=8;
static bool video720Older(unsigned a,unsigned b){return static_cast<int>(a-b)<0;}
struct Video720Frame{const char*asset;unsigned texture,retryAt,lastUse;bool ready;};
static Video720Frame video720Frames[64];
struct Video720Poster{const char*asset;const unsigned char*pixels;};
static Video720Poster video720Posters[64];
static unsigned textureNext=1,allocations=0,deletes=0,uploads=0;
static unsigned video720UseCounter=0,video720CurrentTextureBudget=8;
static int style=2;static bool cellEffects=true;static int paintedCount=0,focused=0;
struct Paint{int index;};static Paint painted[20];
static int contextMarker;static void*gui=&contextMarker;
template<class T>static T at(void*,unsigned){return (T)focused;}
static std::string names[64];static const char* mapped[64];
static int stationCarouselStyle(){return style;}
static bool stationGraphicsEnabled(int){return cellEffects;}
static const char*video720Asset(void*,int i){return mapped[i];}
struct SpaceGL{
 void GenTextures(int,unsigned*t){*t=textureNext++;allocations++;}
 void BindTexture(unsigned,unsigned){}
 void TexImage2D(unsigned,int,int,int,int,int,unsigned,unsigned,const void*p){if(p)uploads++;}
 void TexParameteri(unsigned,unsigned,int){}
 void ActiveTexture(unsigned){}
};static SpaceGL spaceGL;
static void video720DeleteTexture(unsigned texture){if(texture)deletes++;}
static bool video720PaintedAsset(void*,const char*);
'''
functions='\n'.join(body(source,name) for name in ['video720Retained','video720Same','video720FrameTexture','video720PaintedAsset','video720PaintedTextureBudget','trimVideo720Textures','seedVideo720Preview','video720StaticPosterNeeded','video720NextStaticPoster'])
test=r'''
static unsigned checks=0;
static void check(bool value){assert(value);checks++;}
static unsigned countTextures(){unsigned n=0;for(auto&f:video720Frames)if(f.texture)n++;return n;}
static unsigned countReady(){unsigned n=0;for(int k=0;k<paintedCount;k++){auto*f=video720Retained(mapped[painted[k].index]);if(f&&f->ready&&f->texture)n++;}return n;}
static void reset(){for(auto&f:video720Frames)f={};for(int i=0;i<64;i++){names[i]="clip-"+std::to_string(i);mapped[i]=names[i].c_str();video720Posters[i]={mapped[i],(const unsigned char*)1};}style=2;cellEffects=true;paintedCount=0;textureNext=1;allocations=deletes=uploads=video720UseCounter=0;video720CurrentTextureBudget=8;}
static void window(int begin,int cells,int aliasStep=1,bool includeNull=false){paintedCount=cells;focused=begin;for(int k=0;k<cells;k++){painted[k].index=(begin+k)%44;mapped[painted[k].index]=(includeNull&&k%4==3)?nullptr:names[(begin+k/aliasStep)%44].c_str();}}
static void admitBudget(){unsigned next=video720PaintedTextureBudget(gui);if(next<video720CurrentTextureBudget)trimVideo720Textures(gui,next);video720CurrentTextureBudget=next;}
int main(){
 reset();window(0,11);unsigned legacyMissing=0;
 for(int k=0;k<11;k++){auto*f=video720Retained(mapped[k],true);if(legacyVideo720FrameTexture(f))f->ready=true;else legacyMissing++;}
 check(countTextures()==8);check(countReady()==8);check(legacyMissing==3);
 reset();window(0,11);admitBudget();for(int k=0;k<11;k++)seedVideo720Preview(mapped[k]);check(countTextures()==11);check(countReady()==11);check(uploads==11);
 unsigned maxTextures=0;
 for(int mode=0;mode<2;mode++)for(int gfx=0;gfx<2;gfx++)for(int s=0;s<3;s++)for(int aliases=1;aliases<=3;aliases++)for(int nulls=0;nulls<2;nulls++){
  reset();style=s;cellEffects=gfx;int maxCells=(s==2&&gfx)?13:8;
  for(int begin=0;begin<44;begin++)for(int cells=1;cells<=maxCells;cells++){
   window(begin,cells,aliases,nulls);admitBudget();check(video720CurrentTextureBudget>=8&&video720CurrentTextureBudget<=13);
   for(int frame=0;frame<13;frame++){
    unsigned before=uploads;
    if(mode==0){const char*pending=video720NextStaticPoster(gui);if(pending)seedVideo720Preview(pending);check(uploads-before<=1);}
    else for(int k=0;k<paintedCount;k++)seedVideo720Preview(mapped[painted[k].index]);
    check(countTextures()<=video720CurrentTextureBudget);maxTextures=countTextures()>maxTextures?countTextures():maxTextures;
   }
   for(int k=0;k<paintedCount;k++)if(mapped[painted[k].index]){auto*f=video720Retained(mapped[painted[k].index]);check(f&&f->texture&&f->ready);}
   unsigned settledUploads=uploads;if(mode==0)check(video720NextStaticPoster(gui)==nullptr);else for(int k=0;k<paintedCount;k++)seedVideo720Preview(mapped[painted[k].index]);check(uploads==settledUploads);
  }
  style=0;cellEffects=true;window(0,7);admitBudget();check(video720CurrentTextureBudget==8);check(countTextures()<=8);
 }
 reset();window(0,13);admitBudget();for(int k=0;k<13;k++)seedVideo720Preview(mapped[k]);check(countTextures()==13);style=1;window(20,7);admitBudget();check(countTextures()==8);for(int k=0;k<7;k++)seedVideo720Preview(mapped[20+k]);check(countReady()==7);check(countTextures()==8);
 reset();video720UseCounter=0xfffffff0u;window(0,11);admitBudget();for(int k=0;k<11;k++)seedVideo720Preview(mapped[k]);window(10,11);admitBudget();for(int k=0;k<11;k++)seedVideo720Preview(mapped[10+k]);check(countReady()==11);check(countTextures()==11);
 std::cout<<checks<<" "<<legacyMissing<<" "<<maxTextures;
}
'''
fixture=PRIVATE/'native-allocator-probe.cpp'
fixture.write_text(prelude+functions+'\n'+legacy_alloc+'\n'+test,encoding='utf8')
run([CLANG,'-std=c++17','-O2','-Wall','-Wextra',fixture,'-o',PRIVATE/'native-allocator-probe.exe'])
checks,missing,max_textures=map(int,run([PRIVATE/'native-allocator-probe.exe']).split())

preserved=['ensureVideo720Jni','video720Asset','retainVideo720Frame','retireVideo720Slot','pauseSystemVideo720','drawRetainedSystemVideo720','video720StaticPosterNeeded','video720NextStaticPoster','paintStaticSystemVideo720','drawStaticSystemVideo720']
for name in preserved:assert body(source,name)==body(legacy,name),name
assert 'for(int k=0;k<paintedCount;k++)seedVideo720Preview(video720Asset(p,painted[k].index));' in source
assert 'r53VideoPolicy::decide(frame,policySlots)' in source
receipt={'version':'R124','utc':datetime.now(timezone.utc).isoformat(),'passed':True,'scope':'Isolated host extraction of actual native frame allocator/budget/trim/poster methods; no physical Android/GL/decoder/gameplay/thermal proof','baselineSourceCommit':BASELINE,'checks':{'actualAllocatorHostChecks':checks,'unchangedCriticalVideoMethods':len(preserved)},'cause':{'legacyTextureBudget':8,'drawnCells':11,'reproducedMissingCells':missing,'legacyReadyCells':8},'fix':{'minimumTextureBudget':8,'maximumTextureBudget':13,'enabledOnlyFor':'De lado plus CELL_EFFECTS','budgetMatchesUniqueVisibleAssets':True,'pruneNonVisibleLRUOnShrink':True,'liveDecoders':1,'quality':'720x720 RGB565','menuFPS':30,'staticModeOneUploadPerFramePreserved':True,'liveModeExistingPosterAdmissionPreserved':True,'maximumHostObservedTextures':max_textures,'elevenFrameExtraBytes':3*720*720*2,'maximumTransitionalExtraBytes':5*720*720*2},'assetCoverage':{'systemMappedAssets':len(system_assets),'collectionMappedAssets':len(collection_assets),'packagedPosterAssets':len(poster_assets),'allMappedAssetsHavePackagedPoster':True,'allMappedVideosPresentInCandidateAPK':True,'candidateAPKHashFromVerifiedPackageReceipt':status['apkSHA256'],'inspection':'ZIP entry names only; this host probe does not rehash or operate the installed phone'},'sources':{'native/d0/native_system_video720.h':hashlib.sha256(raw(SOURCE)).hexdigest(),'privatePolicyMatchesManifest':True,'privateVideoDefinitionsMatchManifest':True}}
(SNAP/'evidence/video-visible-budget-r124.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps(receipt,ensure_ascii=False))
