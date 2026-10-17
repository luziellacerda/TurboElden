from pathlib import Path
import hashlib,json,re,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BASE='508480e3671ae924f037bd32f6d71efda7a9d905c45c7b2571bd9f219add83d4'
BASE_BYTES=2715024399
BASE_SOURCE='26257869b59af8ecea44932ab287705990a9acbe'
PARTITION='classes28.dex'
DEX='534653399c359834c04733a18220524cfd95480f23e0f07d49babcc0ef2eb5bd'
CAROUSEL='lib/arm64-v8a/libturbo_carousel.so'
CAROUSEL_SHA='867d86a5dba085fadec1e4b8dee0f8be99467551ba830607d3041b324c02b80e'
PRESERVED_DEX35='0cc5f639202ed3da50c246a9b07eda91c8c8d81bdc9764c67f08f3da459a74c4'
RETRO='ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378'
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
BUILD_NAMESPACE=Path('E:/StationWavePaletteR144-20261013')
ROOT_DEX={'classes.dex',*[f'classes{i}.dex' for i in range(2,41)]}
WRAPPERS={'psx': ('libstation_psx_online.so', 'ab6ca6220719855a80c9060cb9ec6f3dbad3eeac6fe10e54653ba81fb7d8a7c9'), 'n64': ('libstation_mupen64plus_runtime.so', 'f9ecfbf76a3663573802977a66c597d31fc10429542c370254ab92ec141a87d0'), 'dolphin': ('libstation_dolphin_runtime.so', '7f79b9e115244072adbe5521c5b21797885b20a852e707f17a460d1f3fe162e8')}
REPLACED={PARTITION,CAROUSEL,'assets/station-online/engines.json',*['lib/arm64-v8a/'+v[0] for v in WRAPPERS.values()]}
def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

def read(path):
    return json.loads(Path(path).read_text("utf-8"))

def entry_sha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def extract_fingerprint(raw):
    docs = []
    for match in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', raw):
        end = raw.find(b"\0", match.start())
        if end < 0:
            continue
        try:
            value = json.loads(raw[match.start():end].decode("ascii"))
        except (ValueError, UnicodeError):
            continue
        if isinstance(value, dict) and "baseApkSha256" in value and "payloadSha256" in value:
            docs.append(value)
    need(len(docs) == 1, "Exactly one canonical wrapper identity required")
    value = docs[0]
    need(canonical(value) in raw and digest(canonical(value)).encode("ascii") in raw, "Embedded wrapper fingerprint differs")
    return value

def elf_contract(raw):
    need(raw[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<H", raw, 18)[0] == 183, "ARM64 ELF required")
    phoff = struct.unpack_from("<Q", raw, 32)[0]
    phsize, phnum = struct.unpack_from("<HH", raw, 54)
    loads = [struct.unpack_from("<IIQQQQQQ", raw, phoff + i * phsize) for i in range(phnum)]
    aligns = [row[-1] for row in loads if row[0] == 1]
    need(aligns and min(aligns) >= 16384, "16 KiB native load alignment required")
    shoff = struct.unpack_from("<Q", raw, 40)[0]
    shsize, shnum = struct.unpack_from("<HH", raw, 58)
    sections = [struct.unpack_from("<IIQQQQIIQQ", raw, shoff + i * shsize) for i in range(shnum)]
    def string(table, index):
        end = table.find(b"\0", index)
        need(0 <= index < len(table) and end >= index, "Invalid ELF string")
        return table[index:end].decode("ascii")
    exports, needed, sonames = [], [], []
    for row in sections:
        if row[1] not in (6, 11):
            continue
        table = sections[row[6]]
        strings = raw[table[4]:table[4] + table[5]]
        data = raw[row[4]:row[4] + row[5]]
        need(row[9] > 0 and len(data) % row[9] == 0, "Invalid ELF table stride")
        for offset in range(0, len(data), row[9]):
            if row[1] == 11:
                name, info, other, index, _, _ = struct.unpack_from("<IBBHQQ", data, offset)
                if name and index and info >> 4 in (1, 2):
                    exports.append((string(strings, name), info, other))
            else:
                tag, value = struct.unpack_from("<qQ", data, offset)
                if tag == 1:
                    needed.append(string(strings, value))
                elif tag == 14:
                    sonames.append(string(strings, value))
    return dict(exports=sorted(exports), needed=sorted(needed), soname=sonames, minimumLoadAlignment=min(aligns))

def wrapper_contract(before, after, kind, ndk=None):
    old, new = elf_contract(before), elf_contract(after)
    need(old["exports"] == new["exports"] and old["needed"] == new["needed"] and
         old["soname"] == new["soname"] == [WRAPPERS[kind][0]], "Wrapper exports/dependencies/SONAME changed: " + kind)
    return new
def source_map():
 files={p.relative_to(ROOT).as_posix():sha(p) for folder in ('java','native','recipe') for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and p.suffix in {'.py','.java','.cpp','.c','.h','.hpp','.smali'}}
 for n in ('PROPOSED-SCOPE.json','java/evidence/java-source-preservation.json'):files[n]=sha(ROOT/n)
 need('recipe/common.py' in files and 'recipe/build_dex.py' in files and len(REPLACED)==6,'Closed visual recipe required')
 return files
def verify_commit(commit):
 need(isinstance(commit,str) and re.fullmatch('[0-9a-f]{40}',commit),'Full frozen source commit required')
 pins=source_map();prefix=ROOT.relative_to(REPO).as_posix()
 for n,h in pins.items():
  p=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'show',commit+':'+prefix+'/'+n],capture_output=True,timeout=90)
  need(p.returncode==0 and digest(p.stdout)==h,'Frozen source differs: '+n)
 return pins
def isolated(path):
 p=Path(path).resolve();need(not p.exists() and BUILD_NAMESPACE.resolve() in p.parents and REPO not in p.parents,'New isolated R144 output required');return p
def run(command):
 p=subprocess.run(list(map(str,command)),capture_output=True,text=True,timeout=300)
 need(p.returncode==0,'R144 tool failed: '+p.stderr[-1200:]);return p.stdout.strip()
def fingerprints(archive):
 result={}
 for kind,(name,checksum) in WRAPPERS.items():
  raw=archive.read('lib/arm64-v8a/'+name);need(digest(raw)==checksum,'Exact R143 wrapper required')
  value=extract_fingerprint(raw)
  need(len(value['payloadSha256'])==345 and value['payloadSha256'][PARTITION]==DEX and value['payloadSha256'][CAROUSEL]==CAROUSEL_SHA and value['payloadSha256']['classes35.dex']==PRESERVED_DEX35,'R143 payload binding required');result[kind]=value
 need(all(v['payloadSha256']==result['psx']['payloadSha256'] and v['productiveTransforms']==result['psx']['productiveTransforms'] for v in result.values()),'Retained payload/source chain differs')
 return result
def state_fields():
 return dict(revision='R144',candidateOnly=True,diagnosticLoggerIncluded=False,nativeRuntimeRebuilt=False,promoted=False,installed=False,serverRegistered=False,serverRegistrationPending=True,physicalVisualValidated=False)
