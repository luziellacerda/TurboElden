from pathlib import Path
import hashlib, json, struct, subprocess
W=Path(r'E:\ESTUDO APK\work\station-n64-controls-r19-20261005')
lib=W/'libmain.so'; b=lib.read_bytes()
assert hashlib.sha256(b).hexdigest()=='62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6'
phoff=struct.unpack_from('<Q',b,32)[0];size,count=struct.unpack_from('<HH',b,54)
def offset(address):
 for i in range(count):
  kind,flags,off,va,pa,files,mem,align=struct.unpack_from('<II6Q',b,phoff+i*size)
  if kind==1 and va<=address<va+files:return off+address-va
 raise ValueError(hex(address))
assert b[offset(0xc6477):offset(0xc6477)+4]==b'lib\0'
# Confirm exact instructions in the inspected R18 binary, not a guessed resolver.
for address,value in {0x2a8e2c:0xd0fff0e2,0x2a8e30:0x9111dc42,0x2335a4:0x910183e0,0x2335ac:0x9405a9b1}.items():
 assert struct.unpack_from('<I',b,offset(address))[0]==value
tool=r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\llvm-objdump.exe'
evidence={}
for name,lo,hi in [('bundled-prefix','0x2a8e14','0x2a8e68'),('resolved-run','0x233540','0x2335b0')]:
 p=subprocess.run([tool,'-d','--start-address='+lo,'--stop-address='+hi,str(lib)],capture_output=True,text=True)
 assert p.returncode==0
 (W/(name+'.txt')).write_text(p.stdout,'utf8');evidence[name]={'start':lo,'end':hi}
receipt={'libmainSHA256':hashlib.sha256(b).hexdigest(),'prefixAddress':'0xc6477','prefix':'lib','verifiedInstructions':True,'disassembly':evidence,'oldRouteRegressionTest':'Fails at check 1 for libmupen64plus_ae_android.so','catalogFolders':['nintendo-64','nintendo-64--br']}
(W/'resolver-evidence.json').write_text(json.dumps(receipt,indent=2),'utf8')
print(json.dumps(receipt,indent=2))
