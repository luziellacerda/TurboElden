"""Read the pinned official aPS3e APK. No extraction, phone or build operation."""
from pathlib import Path
import argparse, hashlib, json, struct, zipfile

APK_SHA256 = "c5a58fb056ae333b8bd6ed69e6bfacdd1e5bf7e0ac2134456a0622bd94a3e466"
APK_BYTES = 40122859

def sha(data):
    return hashlib.sha256(data).hexdigest()

def uleb(data, offset):
    value = shift = 0
    while True:
        byte = data[offset]; offset += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, offset
        shift += 7
        if shift > 35:
            raise ValueError("Invalid DEX ULEB")

def dex_contract(data):
    if data[:4] != b"dex\n":
        raise ValueError("Expected normal DEX")
    def table(offset):
        return struct.unpack_from("<II", data, offset)
    count, offset = table(56)
    strings = []
    for index in range(count):
        pos = struct.unpack_from("<I", data, offset + index*4)[0]
        _, pos = uleb(data, pos)
        end = data.index(0, pos)
        strings.append(data[pos:end].decode("utf-8", errors="replace"))
    count, offset = table(64)
    types = [strings[struct.unpack_from("<I", data, offset+i*4)[0]] for i in range(count)]
    count, offset = table(72)
    protos = []
    for index in range(count):
        _, return_index, params = struct.unpack_from("<III", data, offset+index*12)
        values = []
        if params:
            n = struct.unpack_from("<I", data, params)[0]
            values = [types[struct.unpack_from("<H", data, params+4+i*2)[0]] for i in range(n)]
        protos.append("("+"".join(values)+")"+types[return_index])
    count, offset = table(80)
    fields = []
    for index in range(count):
        owner, kind, name = struct.unpack_from("<HHI", data, offset+index*8)
        fields.append({"owner":types[owner], "name":strings[name], "type":types[kind]})
    count, offset = table(88)
    methods = []
    for index in range(count):
        owner, proto, name = struct.unpack_from("<HHI", data, offset+index*8)
        methods.append({"owner":types[owner], "name":strings[name], "descriptor":protos[proto]})
    count, offset = table(96)
    owners = []
    for index in range(count):
        owner_index, flags, super_index, _, _, _, class_data, static_values = struct.unpack_from("<8I", data, offset+index*32)
        owner = types[owner_index]
        if not (owner in ("Laenu/aps3e/Emulator;", "Laenu/emulator/Emulator;", "Laenu/lang/System;", "Laenu/hardware/ProcessorInfo;", "Lorg/vita3k/emulator/overlay/InputOverlay$ControlId;") or owner.startswith(("Laenu/aps3e/Emulator$", "Laenu/emulator/Emulator$"))):
            continue
        row = {"class":owner,"super":types[super_index] if super_index != 0xffffffff else None,"nativeMethods":[],"methods":[],"fields":[]}
        if class_data:
            counts = []; pos = class_data
            for _ in range(4):
                n, pos = uleb(data, pos); counts.append(n)
            for n in counts[:2]:
                field_index = 0
                for _ in range(n):
                    delta,pos=uleb(data,pos); access,pos=uleb(data,pos);field_index+=delta
                    item=dict(fields[field_index]); item["accessFlags"]=access; row["fields"].append(item)
            for n in counts[2:]:
                method_index = 0
                for _ in range(n):
                    delta,pos=uleb(data,pos);access,pos=uleb(data,pos);_,pos=uleb(data,pos);method_index+=delta
                    item=dict(methods[method_index]);item["accessFlags"]=access;row["methods"].append(item)
                    if access & 0x100:
                        row["nativeMethods"].append(item)
            if owner == "Lorg/vita3k/emulator/overlay/InputOverlay$ControlId;" and static_values:
                n,pos=uleb(data,static_values)
                for field_index in range(n):
                    kind=data[pos];pos+=1;size=(kind >> 5)+1
                    if kind & 31 != 4:
                        raise ValueError("Unexpected non-integer ControlId constant")
                    value=int.from_bytes(data[pos:pos+size],"little",signed=True);pos+=size
                    row["fields"][field_index]["constantValue"]=value
        owners.append(row)
    return owners

def elf_contract(data):
    if data[:5] != b"\x7fELF\x02" or data[5] != 1:
        raise ValueError("Expected ELF64 little-endian")
    machine=struct.unpack_from("<H",data,18)[0]
    section_offset=struct.unpack_from("<Q",data,40)[0]
    section_size,section_count=struct.unpack_from("<HH",data,58)
    sections=[struct.unpack_from("<IIQQQQIIQQ",data,section_offset+i*section_size) for i in range(section_count)]
    needed=[]; soname=None
    for section in sections:
        if section[1] != 6:
            continue
        strings=sections[section[6]]; table=data[strings[4]:strings[4]+strings[5]]
        for pos in range(section[4],section[4]+section[5],section[9] or 16):
            tag,value=struct.unpack_from("<qQ",data,pos)
            if tag in (1,14):
                name=table[value:table.index(0,value)].decode("ascii")
                if tag==1:needed.append(name)
                else:soname=name
    return {"elfMachine":machine,"soname":soname,"dtNeeded":needed}

def inspect(apk):
    if apk.stat().st_size != APK_BYTES:
        raise ValueError("Pinned APK length mismatch")
    with apk.open("rb") as stream:
        digest=hashlib.file_digest(stream,"sha256").hexdigest()
    if digest != APK_SHA256:
        raise ValueError("Pinned APK hash mismatch")
    with zipfile.ZipFile(apk) as package:
        libraries=[]
        for name in sorted(package.namelist()):
            if name.startswith("lib/arm64-v8a/") and name.endswith(".so"):
                data=package.read(name)
                libraries.append({"entry":name,"bytes":len(data),"sha256":sha(data),**elf_contract(data)})
        dex=package.read("classes.dex")
        asset_names=("assets/config/config.yml","assets/licenses.html")
        assets=[{"entry":name,"bytes":len(package.read(name)),"sha256":sha(package.read(name))} for name in asset_names]
    return {"schema":"station.sony.ps3.official-contract.v1","officialAPK":{"sha256":digest,"bytes":APK_BYTES,"versionName":"2.43","versionCode":43},"nativeLibraries":libraries,"configurationAssets":assets,"dex":{"sha256":sha(dex),"bytes":len(dex),"jniClasses":dex_contract(dex)},"operation":"read-only inspection; no build or gameplay proof"}

if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--apk",type=Path,required=True);parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();result=inspect(args.apk)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"libraries":len(result["nativeLibraries"]),"jniClasses":len(result["dex"]["jniClasses"]),"outputSHA256":sha(args.out.read_bytes())}))
