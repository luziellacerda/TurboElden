#!/usr/bin/env python3
"""Apply only reviewed capacity edits to the producer's current client sources."""
import argparse, hashlib, json
from pathlib import Path

EDITS = {
    'StationCatalog.java': [('public static final int MAX_ITEMS = 4096;', 'public static final int MAX_ITEMS = 20000;')],
    'StationApi.java': [('"catalog?metadata=1"', '"catalog?metadata=1&maximumItems="+StationCatalog.MAX_ITEMS')],
    'StationCatalogPlayerEvidence.java': [('catalog.length>4096', 'catalog.length>StationCatalog.MAX_ITEMS'),
                                         ('values.size()>4096', 'values.size()>StationCatalog.MAX_ITEMS')],
    'StationCatalogPlayerEvidenceLoader.java': [('rows.length()>4096', 'rows.length()>StationCatalog.MAX_ITEMS')],
    'StationCoverQueue.java': [('MAX_PREFETCH_ITEMS=4096', 'MAX_PREFETCH_ITEMS=StationCatalog.MAX_ITEMS')],
}

def apply(directory, write=False, native_source=None):
    pending=[]; receipt=[]
    for name, edits in EDITS.items():
        path=directory/name
        original=path.read_bytes(); data=original
        for before, after in edits:
            before=before.encode(); after=after.encode()
            if data.count(before)==0 and data.count(after)==1: continue
            if data.count(before)!=1 or data.count(after)!=0:
                raise ValueError('Source differs; review before patching: '+name)
            data=data.replace(before,after)
        pending.append((path,data))
        receipt.append(dict(file=name,beforeSha256=hashlib.sha256(original).hexdigest(),
                            afterSha256=hashlib.sha256(data).hexdigest(),changed=data!=original))
    if native_source is not None:
        original=native_source.read_bytes();data=original
        for before,after in [(b'total>4096',b'total>20000'),
                             (b'GetArrayLength(rows)>4096',b'GetArrayLength(rows)>20000')]:
            if data.count(before)==0 and data.count(after)==1:continue
            if data.count(before)!=1 or data.count(after)!=0:raise ValueError('Native bridge differs; review before patching')
            data=data.replace(before,after)
        pending.append((native_source,data))
        receipt.append(dict(file=native_source.name,beforeSha256=hashlib.sha256(original).hexdigest(),
                            afterSha256=hashlib.sha256(data).hexdigest(),changed=data!=original))
    if write:
        for path,data in pending:
            temporary=path.with_name(path.name+'.nes-capacity.tmp')
            with temporary.open('xb') as target: target.write(data)
            temporary.chmod(path.stat().st_mode & 0o777)
            temporary.replace(path)
    return dict(written=write,maximumItems=20000,files=receipt,
                signatureVerificationPreserved=True,requestProofPreserved=True,
                playerEvidenceBindingsPreserved=True,coverWorkersUnchanged=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('station_sources',type=Path)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--native-source',type=Path,help='Current station_frontend.cpp; required for a complete APK build')
    args=parser.parse_args();print(json.dumps(apply(args.station_sources,args.write,args.native_source),indent=2))
if __name__=='__main__': main()
