"""Exercise DEX slot preservation, duplicate refusal and protected-client presence."""
import importlib.util,io,json,struct,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('dex_gates',root/'recipes/dex_gates.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
def dex(names):
    n=len(names);so=112;to=so+n*4;co=to+n*4;string_start=co+n*32
    data=bytearray(string_start);data[:8]=b'dex\n035\x00';pos=string_start
    for i,name in enumerate(names):
        encoded=name.encode();data+=bytes([len(encoded)])+encoded+b'\x00'
        struct.pack_into('<I',data,so+i*4,pos);struct.pack_into('<I',data,to+i*4,i)
        struct.pack_into('<I',data,co+i*32,i);pos=len(data)
    struct.pack_into('<III',data,32,len(data),112,0x12345678)
    struct.pack_into('<II',data,56,n,so);struct.pack_into('<II',data,64,n,to);struct.pack_into('<II',data,96,n,co)
    return bytes(data)
protected='Lorg/emulationstation/frontend/station/StationRequestProof;'
old='Lorg/emulationstation/frontend/station/StationApi;';net='Lorg/emulationstation/frontend/netplay/StationOnlineClient;'
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w') as z:
    z.writestr('classes.dex',dex(['LUnrelated;']));z.writestr('classes28.dex',dex([old]));z.writestr('classes35.dex',dex([net]))
with zipfile.ZipFile(buf) as z:
    replacements={'classes28.dex':dex([old,protected]),'classes35.dex':dex([net])}
    assert g.verify_modules(z,replacements)['noDuplicateClasses']
    cases=[dict(replacements,**{'classes28.dex':dex([protected])}),
           dict(replacements,**{'classes28.dex':dex([old])}),
           dict(replacements,**{'classes35.dex':dex([net,'LUnrelated;'])})]
    for changed in cases:
        try:g.verify_modules(z,changed)
        except ValueError:pass
        else:raise AssertionError('Unsafe APK accepted')
try:g.definitions(b'bad')
except ValueError:pass
else:raise AssertionError('Invalid DEX accepted')
print(json.dumps(dict(passed=True,positiveComposition=True,refusedMissingOriginalClass=True,
    refusedUnprotectedClient=True,refusedCrossModuleDuplicate=True,refusedInvalidDex=True,apkBuilt=False)))
