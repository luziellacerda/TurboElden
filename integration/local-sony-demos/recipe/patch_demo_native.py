"""Sony platform artwork fallback only; retains every R128 render method."""
import hashlib

ANCHOR='  if(art)strAssign(item+0xc8,art->path);\n'
ADDITION='''  if(!art&&(presentationKeyEqual(key,"Playstation 3")||presentationKeyEqual(key,"Playstation 4"))){
   const bool ps3=presentationKeyEqual(key,"Playstation 3");
   const char*demoId=ps3?"local-demo-ps3-orbital-v1":"local-demo-ps4-neon-v1";
   const char*demoCover=ps3?
    "/data/user/0/org.turboramastation.frontend/no_backup/station-covers/local-demo-ps3-orbital-v1.png":
    "/data/user/0/org.turboramastation.frontend/no_backup/station-covers/local-demo-ps4-neon-v1.png";
   bool published=false;
   for(B*source=at<B*>(real,0x88);source<at<B*>(real,0x90);source+=0xe8){
    if(strcmp(strData(source+0x60),key)==0&&strcmp(strData(source),demoId)==0){published=true;break;}
   }
   // Only a changed system list reaches here. One private-file check per Sony
   // platform, independent of the bounded game-cover reveal/eviction window.
   if(published){
    void*file=fopen(demoCover,"rb");if(file){fclose(file);strAssign(item+0xc8,demoCover);}
   }
  }
'''

def patch(raw:bytes)->bytes:
    text=raw.decode('utf-8')
    if text.count(ANCHOR)!=1 or ADDITION in text:raise ValueError('R128 platform artwork anchor changed')
    result=text.replace(ANCHOR,ANCHOR+ADDITION,1).encode('utf-8')
    if result.decode('utf-8').replace(ADDITION,'',1).encode('utf-8')!=raw:raise ValueError('Native inverse mismatch')
    return result

def verify(original:bytes,result:bytes)->dict:
    if patch(original)!=result:raise ValueError('Unexpected native delta')
    return {'changedMethods':['syncModel'],'exactInverse':True,
            'renderMethodsChanged':False,'commandRoutesChanged':False,
            'gameWarmWindowChanged':False,'platformArtworkUsesPersistentDemoPath':True,
            'originalSourceSha256':hashlib.sha256(original).hexdigest(),
            'sourceSha256':hashlib.sha256(result).hexdigest()}
