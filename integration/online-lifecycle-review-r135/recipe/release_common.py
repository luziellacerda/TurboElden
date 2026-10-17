"""Closed R135 source and artifact inputs; preserve the exact signed R134 donor."""
from pathlib import Path
import hashlib, importlib.util, json, re, subprocess, sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE_SHA = 'f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2'
BASE_BYTES = 2714991631
BASE_SOURCE = '4f9039eb9ce13907ce043870bfe1f6e294888556'
FRONTEND_SHA = '4e7ad58e1e8f8a284654120c27280eed8c124ad5301a9e87d769e41f100d8d0d'
BASELINE_DEX_SHA = 'd5a689c7e60df0d3a822f97f17a27875c7c1b38da00f44419735724d4d1dda76'
PREFIX = 'lib/arm64-v8a/'
DEX = frozenset(['classes.dex', *[f'classes{i}.dex' for i in range(2,41)]])
PRESERVED_DEX = DEX - {'classes35.dex'}
DEX_ASSET = 'assets/sony/ps4/upstream/derived/owner.dex'
REPLACED = frozenset({'classes35.dex', 'assets/station-online/engines.json', *[PREFIX+n for n in ('libstation_psx_online.so','libstation_mupen64plus_runtime.so','libstation_dolphin_runtime.so')]})
SCOPES = ['online-explicit-human-exit-lock-order', 'online-explicit-human-leave-stale-generation-confirmed-retry']
FAMILIES = ['Lorg/emulationstation/frontend/netplay/StationDolphinSession;', 'Lorg/emulationstation/frontend/netplay/StationGameSession;', 'Lorg/emulationstation/frontend/netplay/StationHumanDeparture;']
CERT = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
PRODUCTIVE_JAVA = {
    'java/org/emulationstation/frontend/netplay/StationDolphinSession.java':'8dabb51d65313e2a6b2925927163aa1a50d24533a8bcc5ccaa5b1cd1a59c6231',
    'java/org/emulationstation/frontend/netplay/StationGameSession.java':'382066fb971d4fd15005f2e8057271f2148f70e2e295e4cb45ac9088648ec22f',
    'java/org/emulationstation/frontend/netplay/StationHumanDeparture.java':'45eb52fa73d1412589a5f27b6d9cb772cd137c316dd7126873f1e9ce81db3dc7',
}

def require(value,message):
    if not value: raise ValueError(message)

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def write(path,value):
    path=Path(path)
    require(not path.exists(),'Refusing to overwrite a receipt: '+path.name)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:f.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def checked_file(record,label):
    require(isinstance(record,dict) and set(record)=={'path','bytes','sha256'} and type(record['bytes']) is int and record['bytes']>0 and re.fullmatch('[0-9a-f]{64}',record['sha256']) is not None,'Exact artifact record required: '+label)
    original=Path(record['path'])
    actual=original.resolve(strict=True)
    require(original.is_absolute() and not original.is_symlink() and actual.is_file() and actual.stat().st_size==record['bytes'] and sha(actual)==record['sha256'],'Artifact changed: '+label)
    return actual

def source_map():
    result={}
    for directory in ('java','recipe'):
        for p in sorted((ROOT/directory).rglob('*')):
            if p.is_file() and p.suffix in ('.java','.py'):
                require(not p.is_symlink(),'Productive source must be regular')
                result[p.relative_to(ROOT).as_posix()]=sha(p)
    require({k:v for k,v in result.items() if k.startswith('java/')}==PRODUCTIVE_JAVA,'Only the three reviewed productive Java sources may enter R135')
    return result

def verify_source_commit(commit,pins=None):
    require(isinstance(commit,str) and re.fullmatch('[0-9a-f]{40}',commit) is not None,'Explicit full source commit required')
    pins=source_map() if pins is None else pins
    prefix=ROOT.relative_to(REPO).as_posix()
    for name,checksum in pins.items():
        raw=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'show',commit+':'+prefix+'/'+name],stderr=subprocess.PIPE)
        require(digest(raw)==checksum,'Source differs from committed bytes: '+name)
    return pins

def verify_base(path):
    path=Path(path)
    require(path.is_file() and path.stat().st_size==BASE_BYTES and sha(path)==BASE_SHA,'Exact signed R134 donor required')
    return path
