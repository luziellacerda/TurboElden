"""Pinned, read-only ARM64 owner guards. Never executes or patches an emulator."""
from pathlib import Path
import argparse, hashlib, json, struct

OWNER_SHA = '62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6'
WORDS = {
    0x2a99c4: 0xf9019e95,  # real CoreState published before loading the core
    0x2a9ed4: 0x10045928, 0x2a9edc: 0x1004f769,
    0x2a9ef0: 0x1005c608, 0x2a9ef8: 0x1005c969,
    0x2a9f04: 0x1005cbc8, 0x2a9f0c: 0x10061d29,
    0x2aa148: 0x910c03e0, 0x2aa14c: 0x9105e3e2,
    0x2abe44: 0x910b03e0, 0x2abe48: 0x9403c912,
    0x2ac450: 0x7104011f, 0x2ac454: 0x54ffcf60,
    0x2adc38: 0x396627e8, 0x2adc44: 0x39292bff,
    0x2add08: 0xd00008c8, 0x2add0c: 0xb94b1908,
    0x2add64: 0x9baa7d08, 0x2add68: 0xb8686928,
    0x2ae5fc: 0x9403d829, 0x2ae600: 0x39662be8,
    0x2ae608: 0x37000068, 0x2ae60c: 0x910c03e0,
    0x2ae610: 0x9403d748, 0x2ae618: 0x9403d822,
    0x2aeac4: 0x9403d6fb,  # corrected below by explicit branch-target guard
    0x2b142c: 0x9403b3b9, 0x2b1444: 0x9403b3bf,
    0x2b3424: 0x391d2abf, 0x2b4fdc: 0x391d2b7f,
    0x2b6308: 0x7100041f, 0x2b630c: 0x54000ae8,
    0x2bb250: 0x39408109, 0x2bb25c: 0xb9400108,
    0x2bb26c: 0x71000d1f, 0x2bb340: 0x391d291f,
    0x2bcf9c: 0xf9400000, 0x2bcfa0: 0x14039f20,
    0x2be414: 0x39402008, 0x2be420: 0xf9405000,
    0x2be424: 0xd61f0000,
}
# The source-derived target is stronger than a transcribed audio instruction.
WORDS.pop(0x2aeac4)
CALLS = {'events':(0x2abe48,0x39e290), 'preGateCounter':(0x2ae5fc,0x3a46a0),
    'coreRun':(0x2ae610,0x3a4330),'postCoreCounter':(0x2ae618,0x3a46a0),
    'audio':(0x2aeac4,0x3a47b0),'video':(0x2aec5c,0x3a47d0),
    'stateSize':(0x2add78,0x3a4380),'manualSave':(0x2addac,0x3a4390),
    'manualLoad':(0x2b081c,0x3a43a0),'pacing':(0x2b142c,0x39e310),
    'swap':(0x2b1444,0x39e340),'homeSaves':(0x2a99d4,0x39e050),
    'homeEnvironment':(0x2a9f20,0x39e050)}
RELOCS = {'SDL_PollEvent':0x3bf7f8,'SDL_GetPerformanceCounter':0x3c2a00,
    'dlsym':0x3c2cc0,'_ZN5Utils10FileSystem11getHomePathEv':0x3bf6d8}

SYMBOLS = {0x2bcfc8:'retro_set_environment',0x2bcfe0:'retro_set_video_refresh',
    0x2bcff8:'retro_set_audio_sample',0x2bd010:'retro_set_audio_sample_batch',
    0x2bd028:'retro_set_input_poll',0x2bd040:'retro_set_input_state',
    0x2bd058:'retro_init',0x2bd070:'retro_deinit',0x2bd088:'retro_get_system_info',
    0x2bd0a0:'retro_get_system_av_info',0x2bd0b8:'retro_load_game',
    0x2bd0d0:'retro_unload_game',0x2bd0e8:'retro_run',0x2bd100:'retro_reset',
    0x2bd118:'retro_get_memory_data',0x2bd130:'retro_get_memory_size',
    0x2bd148:'retro_api_version',0x2bd160:'retro_set_controller_port_device',
    0x2bd178:'retro_serialize_size',0x2bd190:'retro_serialize',0x2bd1a8:'retro_unserialize'}

def resolver_names(elf):
    names={};address=None
    for pc in range(0x2bcfa4,0x2bd1a8,4):
        word=struct.unpack('<I',elf.at(pc,4))[0]
        if word&0x9f00001f==0x90000001:
            imm=((word>>5)&0x7ffff)<<2|((word>>29)&3)
            if imm&(1<<20):imm-=1<<21
            address=(pc&~0xfff)+(imm<<12)
        elif word&0xff8003ff==0x91000021:
            if address is None:raise ValueError('ADD before ADRP')
            address+=((word>>10)&0xfff)<<(12 if word&(1<<22) else 0)
        elif word>>26==0x25 and bl(elf,pc)==0x3a4c20:
            if address is None:raise ValueError('Unresolved symbol string')
            names[pc+4]=elf.at(address,128).split(b'\x00')[0].decode('ascii')
    return names

class Elf:
    def __init__(self, data):
        if data[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H',data,18)[0]!=183:
            raise ValueError('Expected ELF64 little-endian AArch64')
        self.data=data
        po=struct.unpack_from('<Q',data,32)[0]; es,n=struct.unpack_from('<HH',data,54)
        self.loads=[]
        for i in range(n):
            t,_,off,va,_,sz,_,_=struct.unpack_from('<IIQQQQQQ',data,po+i*es)
            if t==1:self.loads.append((va,off,sz))
        so=struct.unpack_from('<Q',data,40)[0];es,n=struct.unpack_from('<HH',data,58)
        self.sections=[struct.unpack_from('<IIQQQQIIQQ',data,so+i*es) for i in range(n)]
    def at(self,va,size):
        for start,off,n in self.loads:
            if start<=va and va+size<=start+n:return self.data[off+va-start:off+va-start+size]
        raise ValueError('Unmapped virtual address')
    def relocs(self):
        found={}
        for sec in self.sections:
            if sec[1]!=4:continue
            syms=self.sections[sec[6]];st=self.sections[syms[6]]
            strings=self.data[st[4]:st[4]+st[5]]
            for p in range(sec[4],sec[4]+sec[5],sec[9]):
                off,info,addend=struct.unpack_from('<QQq',self.data,p)
                if info&0xffffffff!=1026:continue
                sym=info>>32;name=struct.unpack_from('<I',self.data,syms[4]+sym*syms[9])[0]
                text=strings[name:strings.index(0,name)].decode()
                found[text]=off
        return found

def bl(elf,site):
    w=struct.unpack('<I',elf.at(site,4))[0]
    if w>>26!=0x25:raise ValueError('Expected BL')
    imm=w&0x3ffffff
    if imm&0x2000000:imm-=0x4000000
    return site+imm*4

def main():
    ap=argparse.ArgumentParser();ap.add_argument('owner',type=Path);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); data=args.owner.read_bytes();elf=Elf(data);results=[]
    def check(name,cond):
        results.append({'name':name,'passed':bool(cond)})
        if not cond:raise ValueError(name)
    check('ownerIntegralSha',hashlib.sha256(data).hexdigest()==OWNER_SHA)
    for va,word in WORDS.items():check('word:'+hex(va),elf.at(va,4)==struct.pack('<I',word))
    for name,(site,target) in CALLS.items():check('BL:'+name,bl(elf,site)==target)
    actual=resolver_names(elf)
    for pc,name in SYMBOLS.items():check("resolvedSymbol:"+hex(pc)+":"+name,actual.get(pc)==name)
    rs=elf.relocs()
    for name,off in RELOCS.items():check('GOT:'+name,rs.get(name)==off)
    # Legacy environment switch command7 leads to the native automatic shutdown.
    jump=struct.unpack('<H',elf.at(0xe5be2+(7-1)*2,2))[0]
    check('environmentShutdown7',0x2b2a68+jump*4==0x2b3424)
    result={'schemaVersion':1,'scope':'PSX original SDL owner exact ABI, no execution or patch',
        'ownerSha256':OWNER_SHA,'checks':len(results),'passed':True,
        'binding':{'eventStackOffset':'0x2c0','coreStackOffset':'0x300',
            'coreFromEvent':'0x40','pauseCoreOffset':'0x68a','runningCoreOffset':'0x74a',
            'originalCoreGlobal':'0x3cf338','manualActionGlobal':'0x3c7b18',
            'menuRowsGlobal':'0x3cf2d0','rowBytes':56,'rowActionOffset':0,'rowEnabledOffset':32,
            'checkpointReturnPC':'0x2ae600','restoreReturnPC':'0x2ae61c',
            'maximumPorts':2,'standardPadBits':'0x3fff'},
        'calls':{n:{'site':hex(a),'target':hex(b)} for n,(a,b) in CALLS.items()},
        'relocations':{n:hex(v) for n,v in RELOCS.items()},
        'resolvedSymbols':{hex(pc):name for pc,name in actual.items()},
        'limits':['No Android/core/gameplay execution','No emulator binary or APK patched',
            'No CPU/GPU pause ACK validated in a physical emulator','Hash/ABI guards do not prove deterministic gameplay'],
        'results':results}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'checks':len(results)}))

if __name__=='__main__':main()
