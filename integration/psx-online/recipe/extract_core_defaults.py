"""Read the actual normal PCSX core's option table without executing the core.

No ROM/BIOS or extracted binary is written. The table is specific to the
hash-pinned AArch64 core, not a best guess from another revision's defaults.
"""
from pathlib import Path
import argparse, hashlib, json, struct

CORE_SHA256 = "e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9"
V2_SIZE = 6 * 8 + 128 * 16 + 8

class Core:
    def __init__(self, data):
        if hashlib.sha256(data).hexdigest() != CORE_SHA256:
            raise ValueError("PSX_CORE_IDENTITY")
        if data[:6] != b"\x7fELF\x02\x01" or struct.unpack_from("<H", data, 18)[0] != 183:
            raise ValueError("PSX_CORE_ABI")
        self.data, self.loads, self.relocations = data, [], {}
        offset = struct.unpack_from("<Q", data, 32)[0]
        stride, count = struct.unpack_from("<HH", data, 54)
        for i in range(count):
            kind, _, file_at, address, _, file_bytes, _, _ = struct.unpack_from("<IIQQQQQQ", data, offset + i * stride)
            if kind == 1:
                self.loads.append((address, file_at, file_bytes))
        offset = struct.unpack_from("<Q", data, 40)[0]
        stride, count = struct.unpack_from("<HH", data, 58)
        for i in range(count):
            section = struct.unpack_from("<IIQQQQIIQQ", data, offset + i * stride)
            if section[1] != 4:  # SHT_RELA
                continue
            if section[9] != 24:
                raise ValueError("PSX_RELA_ABI")
            for p in range(section[4], section[4] + section[5], 24):
                address, info, addend = struct.unpack_from("<QQq", data, p)
                if (info & 0xffffffff) == 1027 and info >> 32 == 0:
                    self.relocations[address] = addend  # R_AARCH64_RELATIVE

    def at(self, address, size):
        for begin, file_at, length in self.loads:
            if begin <= address and address + size <= begin + length:
                p = file_at + address - begin
                return self.data[p:p+size]
        raise ValueError("PSX_ADDRESS")

    def pointer(self, address):
        return self.relocations.get(address, struct.unpack("<Q", self.at(address, 8))[0])

    def text(self, address):
        if not address:
            return None
        out = bytearray()
        for i in range(4096):
            value = self.at(address+i, 1)[0]
            if not value:
                return out.decode("utf-8")
            out.append(value)
        raise ValueError("PSX_STRING_BOUND")

def extract(data):
    core = Core(data)
    candidates = []
    for address, target in core.relocations.items():
        try:
            if core.text(target) != "pcsx_rearmed_region" or core.text(core.pointer(address+8)) != "Region":
                continue
            if core.text(core.pointer(address+40)) != "system":
                continue
            if core.text(core.pointer(address+V2_SIZE)) != "pcsx_rearmed_bios":
                continue
            candidates.append(address)
        except (ValueError, UnicodeError):
            pass
    if len(candidates) != 1:
        raise ValueError("PSX_OPTION_TABLE_UNIQUE:" + str(len(candidates)))
    options = {}
    address = candidates[0]
    for index in range(256):
        at = address + index * V2_SIZE
        key = core.text(core.pointer(at))
        if key is None:
            break
        if not key.startswith("pcsx_rearmed_") or key in options:
            raise ValueError("PSX_OPTION_KEY")
        values = []
        for i in range(128):
            value = core.text(core.pointer(at+48+i*16))
            if value is None:
                break
            if value in values:
                raise ValueError("PSX_OPTION_VALUES")
            values.append(value)
        default = core.text(core.pointer(at+V2_SIZE-8))
        if not values or default not in values:
            raise ValueError("PSX_OPTION_DEFAULT:" + key)
        options[key] = {"default": default, "values": values}
    else:
        raise ValueError("PSX_OPTION_COUNT")
    canonical = "".join(k+"="+v["default"]+"\n" for k,v in sorted(options.items()))
    return {"schemaVersion":1,"coreSha256":CORE_SHA256,"compiledTableAddress":hex(address),
            "sourceCommit":"ff81ed17a15241d2f3730cdd7585b38e172532ca",
            "optionCount":len(options),"compiledDefaultsSha256":hashlib.sha256(canonical.encode()).hexdigest(),
            "compiledDefaultsCanonical":canonical,"options":options,
            "coreExecuted":False,"physicalGameplayValidated":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("core",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=extract(args.core.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("optionCount","compiledDefaultsSha256","coreExecuted")}))

if __name__=="__main__":
    main()
