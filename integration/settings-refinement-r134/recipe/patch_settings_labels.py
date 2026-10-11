"""Replace two equal-size settings labels in the pinned R133 carousel ELF.

Every other byte is checked by exact inverse, including ELF/LOAD alignment.
No engine, shader, artwork, frame-loop or preference changes are permitted.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import zipfile

DONOR_SHA = "945f7ded35e551d638135a05140c32218eb38277d10eaf21e3f83087d71da112"
DONOR_BYTES = 2714971151
CAROUSEL_SHA = "baf0f07c89b2a0a8e788b211809c389511830805f386647461487706bcdb9709"
LIBRARY_ENTRY = "lib/arm64-v8a/libturbo_carousel.so"
LABELS = (
    ("PS3 • ABRIR EMULADOR", "PS3 • CONFIGURAÇÃO"),
    ("PS4 • ABRIR EMULADOR", "PS4 • CONFIGURAÇÃO"),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def elf_loads(raw):
    require(raw[:7]==b"\x7fELF\x02\x01\x01", "Little-endian ELF64 required")
    require(struct.unpack_from("<H", raw, 18)[0]==183, "AArch64 ELF required")
    offset=struct.unpack_from("<Q",raw,32)[0]
    size,count=struct.unpack_from("<HH",raw,54)
    require(size==56 and 0<count<=128 and offset+size*count<=len(raw), "Valid ELF64 program table required")
    result=[]
    for index in range(count):
        row=struct.unpack_from("<IIQQQQQQ",raw,offset+index*size)
        if row[0]==1:
            result.append(dict(flags=row[1],offset=row[2],virtualAddress=row[3],fileBytes=row[5],memoryBytes=row[6],alignment=row[7]))
    require(result and all(r["alignment"]>=16384 and (r["offset"]-r["virtualAddress"])%16384==0 for r in result),
            "Original 16KiB LOAD alignment required")
    return result


def patch(raw):
    require(digest(raw)==CAROUSEL_SHA,"Exact R133 carousel required")
    loads=elf_loads(raw)
    result=bytearray(raw)
    changes=[]
    for old,new in LABELS:
        before,after=old.encode("utf-8"),new.encode("utf-8")
        require(len(before)==len(after)==22 and raw.count(before)==1,"Exact single equal-size label required")
        at=raw.index(before)
        require(raw[at+22:at+23]==b"\x00", "Label must be a complete C string")
        require(any(r["offset"]<=at and at+22<r["offset"]+r["fileBytes"] and not(r["flags"]&2) for r in loads),
                "Settings label must remain in a read-only LOAD segment")
        result[at:at+22]=after
        changes.append(dict(offset=at,bytes=22,fromText=old,toText=new,fromSha256=digest(before),toSha256=digest(after)))
    final=bytes(result)
    inverse=bytearray(final)
    for row,(old,new) in zip(changes,LABELS):
        at=row["offset"]
        require(final[at:at+22]==new.encode("utf-8"),"Patched label offset differs")
        inverse[at:at+22]=old.encode("utf-8")
    require(bytes(inverse)==raw and len(final)==len(raw),"Exact whole-library inverse required")
    require(final[:64]==raw[:64] and elf_loads(final)==loads,"ELF header/program table changed")
    return final,dict(schema="station.settings.labels.r134.v1",passed=True,baselineCarouselSha256=CAROUSEL_SHA,
        payloadSha256=digest(final),payloadBytes=len(final),changedLabels=changes,exactInversePassed=True,
        allOtherBytesIdentical=True,equalSizeReplacements=True,elfHeaderPreserved=True,elfLoadSegments=loads,
        original16KiBAlignmentPreserved=True,artAndShadersByteIdentical=True,engineCommandsChanged=False,
        decoderRendererPolicyChanged=False,physicalVisualValidated=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--donor",type=Path)
    source.add_argument("--carousel",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--receipt",type=Path,required=True)
    args=parser.parse_args()
    if args.donor is not None:
        require(args.donor.stat().st_size==DONOR_BYTES,"Exact R133 donor bytes required")
        with args.donor.open("rb") as stream:
            require(hashlib.file_digest(stream,"sha256").hexdigest()==DONOR_SHA,"Exact signed R133 donor required")
        with zipfile.ZipFile(args.donor) as archive:
            raw=archive.read(LIBRARY_ENTRY)
    else:
        raw=args.carousel.read_bytes()
    final,receipt=patch(raw)
    output,record=args.output.resolve(),args.receipt.resolve()
    require(output.drive.upper()==record.drive.upper()=="G:" and not output.exists() and not record.exists(),
            "Use new isolated G: payload and receipt paths")
    require(output!=record,"Payload and receipt must differ")
    output.parent.mkdir(parents=True,exist_ok=True);record.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(final)
    receipt["payload"]=dict(name=LIBRARY_ENTRY,path=str(output),bytes=len(final),sha256=digest(final))
    record.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(patched=True,labels=2,exactInversePassed=True,sha256=digest(final))))


if __name__=="__main__":
    main()
