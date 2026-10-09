"""Exercise a software libretro core in two fresh host processes.

Content and serialized states stay in a fresh private directory. This checks
state transfer and input callbacks, never Android performance or WAN gameplay.
Use a host build of the exact delivered upstream revision.
"""
from pathlib import Path
import argparse, ctypes as C, datetime, hashlib, json, os, subprocess, sys

class Game(C.Structure):
    _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
class SystemInfo(C.Structure):
    _fields_=[('name',C.c_char_p),('version',C.c_char_p),('extensions',C.c_char_p),('fullpath',C.c_bool),('block_extract',C.c_bool)]
class Variable(C.Structure):
    _fields_=[('key',C.c_char_p),('value',C.c_char_p)]

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def child(args):
    core=C.CDLL(str(args.core));keep=[];ports=set();video_frames=0;options={}
    if args.platform=='n64':
        options={b'parallel-n64-cpucore':b'cached_interpreter',b'parallel-n64-gfxplugin':b'angrylion',b'parallel-n64-rspplugin':b'cxd4',b'parallel-n64-angrylion-multithread':b'off',b'parallel-n64-rtc-savestate':b'enabled'}
    system=args.work/'system';system.mkdir(exist_ok=True)
    path_buffer=C.create_string_buffer(str(system).encode());keep.append(path_buffer)
    @C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p)
    def environment(cmd,data):
        cmd=cmd&0xffff
        if cmd in (9,30,31):C.cast(data,C.POINTER(C.c_char_p))[0]=C.cast(path_buffer,C.c_char_p);return True
        if cmd==3:C.cast(data,C.POINTER(C.c_bool))[0]=True;return True
        if cmd==10:return True
        if cmd==15:
            var=C.cast(data,C.POINTER(Variable)).contents
            if var.key in options:var.value=options[var.key];return True
            return False
        if cmd==16:
            entries=C.cast(data,C.POINTER(Variable));n=0
            while entries[n].key:
                key,value=entries[n].key,entries[n].value
                if key not in options and value and b';' in value:options[key]=value.split(b';',1)[1].strip().split(b'|',1)[0]
                n+=1
            return True
        if cmd==17:C.cast(data,C.POINTER(C.c_bool))[0]=False;return True
        if cmd==52:C.cast(data,C.POINTER(C.c_uint))[0]=0;return True
        if cmd in (11,18,35,37,44,45,53,62,65536|64):return True
        return False
    @C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t)
    def video(data,width,height,pitch):
        nonlocal video_frames
        if data and width and height:video_frames+=1
    @C.CFUNCTYPE(None,C.c_int16,C.c_int16)
    def audio(left,right):pass
    @C.CFUNCTYPE(C.c_size_t,C.c_void_p,C.c_size_t)
    def audio_batch(data,frames):return frames
    @C.CFUNCTYPE(None)
    def poll():pass
    @C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint)
    def input_state(port,device,index,key):
        ports.add(port);return 0
    keep.extend([environment,video,audio,audio_batch,poll,input_state])
    for name,callback in [('environment',environment),('video_refresh',video),('audio_sample',audio),('audio_sample_batch',audio_batch),('input_poll',poll),('input_state',input_state)]:
        getattr(core,'retro_set_'+name)(callback)
    core.retro_init()
    info=SystemInfo();core.retro_get_system_info(C.byref(info));raw=None
    if not info.fullpath:raw=C.create_string_buffer(args.content.read_bytes());keep.append(raw)
    game=Game(str(args.content).encode(),C.cast(raw,C.c_void_p) if raw else None,args.content.stat().st_size if raw else 0,None)
    core.retro_load_game.argtypes=[C.POINTER(Game)];core.retro_load_game.restype=C.c_bool
    if not core.retro_load_game(C.byref(game)):raise RuntimeError('Core rejected the private fixture')
    for port in range(4 if args.platform=='n64' else 2):core.retro_set_controller_port_device(port,1)
    for _ in range(args.frames):core.retro_run()
    core.retro_serialize_size.restype=C.c_size_t;size=core.retro_serialize_size()
    if not 0<size<=256*(1<<20):raise RuntimeError('No bounded serialized state')
    core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];core.retro_serialize.restype=C.c_bool
    core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];core.retro_unserialize.restype=C.c_bool
    buffer=C.create_string_buffer(size)
    def state():
        if not core.retro_serialize(buffer,size):raise RuntimeError('Core refused serialization')
        return buffer.raw
    statefile=args.work/'initial.state'
    if args.phase=='produce':
        initial=state();statefile.write_bytes(initial);statefile.chmod(0o600)
    else:
        initial=statefile.read_bytes();restored=C.create_string_buffer(initial,len(initial))
        if len(initial)!=size or not core.retro_unserialize(restored,size):raise RuntimeError('Fresh core refused transferred state')
    transferred=state()
    (args.work/(args.phase+'-transferred.state')).write_bytes(transferred)
    for _ in range(20):core.retro_run()
    following=state()
    (args.work/(args.phase+'-following.state')).write_bytes(following)
    result={'stateBytes':size,'transferredStateSHA256':hashlib.sha256(transferred).hexdigest(),'followingStateSHA256':hashlib.sha256(following).hexdigest(),'videoFrames':video_frames,'inputPortsObserved':sorted(ports)}
    (args.work/(args.phase+'.json')).write_text(json.dumps(result)+'\n')
    core.retro_unload_game();core.retro_deinit()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('core','content','work'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--platform',choices=['n64','neogeocd'],required=True);p.add_argument('--frames',type=int,default=120)
    p.add_argument('--phase',choices=['produce','resume'])
    args=p.parse_args()
    if args.phase:child(args);return
    if args.core.is_symlink() or not args.core.is_file() or args.content.is_symlink() or not args.content.is_file():raise ValueError('Regular explicit inputs required')
    args.work.mkdir(mode=0o700,exist_ok=False)
    result={'platform':args.platform,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostCoreSHA256':sha(args.core),'androidGameplayQualified':False,'WANQualified':False,'passed':False}
    for phase in ['produce','resume']:
        command=[sys.executable,__file__,*sys.argv[1:],'--phase',phase]
        with (args.work/(phase+'.private.log')).open('wb') as log:
            try:r=subprocess.run(command,stdout=log,stderr=log,timeout=90)
            except subprocess.TimeoutExpired:result['failure']='core-timeout';break
        if r.returncode:result['failure']='core-process-failed';result['returncode']=r.returncode;break
    else:
        original=json.loads((args.work/'produce.json').read_text());resumed=json.loads((args.work/'resume.json').read_text())
        result.update(stateBytes=original['stateBytes'],inputPortsObserved=original['inputPortsObserved'],
            transferredStateEqual=original['transferredStateSHA256']==resumed['transferredStateSHA256'],followingStateEqual=original['followingStateSHA256']==resumed['followingStateSHA256'],videoProduced=original['videoFrames']>0)
        result['passed']=all(result[k] for k in ['transferredStateEqual','followingStateEqual','videoProduced']) and all(port in original['inputPortsObserved'] for port in range(4 if args.platform=='n64' else 2))
    (args.work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
