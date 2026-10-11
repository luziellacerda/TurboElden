"""Run real native cache functions under strict handle/context mocks.

Row scheduling is also executed independently by the C++/Java test runners.
No Android gameplay, frame pacing or thermal result is implied by these probes.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'station-legacy-cover-diagnostics-r116-20261010'
OUT=ROOT/'evidence/led-isolated'
OUT.mkdir(parents=True,exist_ok=True)

def read(path): return path.read_text(encoding='utf-8')
def part(text,start,end): return text[text.index(start):text.index(end,text.index(start))]
header=read(ROOT/'native/d0/native_magazine_field.h')
unchanged={}
for name in ['native/d0/premium-magazine-led-android.glsl','native/d0/magazine_shader.h',
             'java/netplay-src/org/emulationstation/frontend/netplay/StationCoverLightingShader.java']:
    current=(ROOT/name).read_bytes();assert current==(BASE/name).read_bytes(),name
    unchanged[name]=hashlib.sha256(current).hexdigest()

# Compile the actual production cache, rather than a separately reimplemented model.
program=r'''
#include <cassert>
#include <cstdarg>
#include <cstdio>
#include <set>
#include <vector>
using U=unsigned long long;
using B=unsigned char;
#include "../../native/d0/native_magazine_rows.h"
static void*context=(void*)1;
static void*magazineContext(){return context;}
static int __android_log_print(int,const char*,const char*,...){return 0;}
static std::set<unsigned> deletedTextures,deletedFbos;
static void deleteTextures(int n,const unsigned*p){for(int i=0;i<n;i++)assert(deletedTextures.insert(p[i]).second);}
static void deleteFbos(int n,const unsigned*p){for(int i=0;i<n;i++)assert(deletedFbos.insert(p[i]).second);}
struct MagazineFieldGL {void(*DeleteTextures)(int,const unsigned*)=deleteTextures;void(*DeleteFramebuffers)(int,const unsigned*)=deleteFbos;};
static MagazineFieldGL magazineFieldGL;
'''
program+=part(header,'struct MagazineFieldCache {','static MagazineFieldCache magazineFieldCache;')
program+='static MagazineFieldCache magazineFieldCache;\n'
program+=part(header,'struct MagazineSavedField {','static bool magazineFieldContains')
program+=part(header,'static void deleteMagazineFieldTarget','struct MagazineFieldTemporaryTarget')
program+=part(header,'static void forgetMagazineFieldContext','static void releaseMagazineFieldObjects')
program+=r'''
static unsigned checks;
static void check(bool value){checks++;assert(value);}
static void install(unsigned name,unsigned source,U identity,int model,int width,int height){
 auto&c=magazineFieldCache;c.context=context;c.texture=name;c.fbo=name+100000;c.source=source;c.identity=identity;c.model=model;c.width=width;c.height=height;c.valid=true;
 c.viewport[0]=3;c.viewport[1]=4;c.viewport[2]=1280;c.viewport[3]=720;
}
static bool take(unsigned source,U identity,int model,int width,int height){const int viewport[]={3,4,1280,720};return takeMagazineCompletedField(source,identity,magazineFieldUploadRevision,model,viewport,width,height);}
int main(){
 install(1,7,77,0,200,300);{MagazineFieldRetiredBatch retired;saveMagazineCompletedField(retired);}
 check(magazineSavedBytes()==480000);check(take(7,77,0,200,300));check(magazineFieldCache.texture==1&&magazineFieldCache.valid);
 {MagazineFieldRetiredBatch retired;saveMagazineCompletedField(retired);}
 check(!take(7,78,0,200,300));check(!take(7,77,1,200,300));check(!take(7,77,0,201,300));
 noteMagazineSourceTextureUpload(7);check(magazineSavedBytes()==0);check(deletedTextures.count(1)==1);check(!take(7,77,0,200,300));
 // Complete fields use a bounded LRU: neither count nor bytes can exceed limits.
 for(unsigned i=2;i<402;i++){
  int width=160+(i%5)*96,height=240+(i%7)*80;install(i,i+500,1000+i,i%9,width,height);
  {MagazineFieldRetiredBatch retired;saveMagazineCompletedField(retired);}
  check(magazineSavedBytes()<=8u*1024u*1024u);int count=0;for(const auto&e:magazineSavedFields)if(e.texture)count++;check(count<=3);
 }
 // A field larger than the retained-cache budget is not kept for reuse.
 install(402,999,9999,4,1024,1536);{MagazineFieldRetiredBatch retired;saveMagazineCompletedField(retired);}
 check(deletedTextures.count(402)==1);check(!take(999,9999,4,1024,1536));
 invalidateMagazineStaticField();check(magazineSavedBytes()==0);
 // Do not delete lost-context names through a replacement context; GLuints
 // with those same numbers may now belong to unrelated objects in the new one.
 install(403,999,8888,0,200,300);{MagazineFieldRetiredBatch retired;saveMagazineCompletedField(retired);}
 auto before=deletedTextures.size();context=(void*)2;noteMagazineSourceTextureUpload(999);
 check(deletedTextures.size()==before);check(magazineSavedBytes()==0);forgetMagazineFieldContext(context);
 check(magazineFieldCache.context==context&&magazineFieldCache.texture==0&&!magazineFieldCache.valid);
 // Exact viewport is part of a hit. Catalog invalidation removes saved targets.
 install(404,333,777,8,200,300);{MagazineFieldRetiredBatch retired;saveMagazineCompletedField(retired);}
 const int movedViewport[]={4,4,1280,720};check(!takeMagazineCompletedField(333,777,0,8,movedViewport,200,300));
 invalidateMagazineStaticField();check(deletedTextures.count(404)==1);check(magazineSavedBytes()==0);
 std::printf("PASS %u executed native field-cache lifetime checks\n",checks);
}
'''
source=OUT/'cache_probe.cpp';source.write_text(program,encoding='utf-8')
exe=OUT/'cache_probe.exe'
subprocess.run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-Wall','-Wextra',str(source),'-o',str(exe)],check=True,capture_output=True,text=True)
result=subprocess.run([str(exe)],check=True,capture_output=True,text=True).stdout.strip()
assert result.startswith('PASS ')
online=read(ROOT/'java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineCoverView.java')
for expression in ['fieldReady?fieldTex:pendingFieldTex','pendingFieldRow>0','getGenerationId()',
                   'StationGraphicsPreferences.LED','releaseGraphics();preparing=false;',
                   'for(int slice=0;slice<4;slice++)','GLES20.glClearColor(0,0,0,0)',
                   'worker.preparing','removeListener(graphicsChanged)']:
    assert expression in online,expression
assert 'MAGAZINE_FIELD_VISIBLE' in header
assert 'c.pendingRow<height)return c.pendingRow>0?MAGAZINE_FIELD_VISIBLE' in header
assert 'for(int slice=0;slice<4;slice++)' in header
record={
    'nativeCacheResult':result,
    'shaderBytesUnchanged':unchanged,
    'oldGateExample':{'height':960,'rowsPerMenuFrame':4,'menuFps':30,'fullFieldSeconds':8},
    'newGate':'first successful parcel is displayed; zeros remain the exact base image',
    'quotaRowsPerFrame':4,
    'retainedCacheBudgetBytes':8*1024*1024,
    'retainedCacheEntries':3,
    'budgetScope':'retained fields only; active/candidate targets still use their existing dimensions',
    'physicalValidation':False,
    'thermalClaim':False,
}
(ROOT/'evidence/led-progressive-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(result)
print('PASS unchanged shared shaders and progressive publication guards')
