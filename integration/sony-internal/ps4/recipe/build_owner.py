"""Build the isolated PS4 JNI partition and derive private PKG material from a pinned APK.

No phone, external application installation, native binary modification or repository checkout.
Never publish outputs: the descriptor builder consumes the generated private derived.json.
"""
from pathlib import Path
import argparse, hashlib, json, re, struct, subprocess, zipfile

APK_SHA = "4077b0d0b80e354c71eff1ce2c003f122449ac266eb27a6ac26744d3f9809a08"
DEX_SHA = "0b33b62b7663370587fbcf1b14fdb54ba97990d9e7e205f50c8cbf976be56052"
APK_BYTES = 207779222
PRIMITIVES = dict(zip("VZBSCIJFD",["void","boolean","byte","short","char","int","long","float","double"]))

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for data in iter(lambda:f.read(1<<20),b""):h.update(data)
    return h.hexdigest()

def run(*args):
    subprocess.run([str(x) for x in args],check=True)

def types(text):
    result=[]
    while text:
        array=""
        while text[0]=="[":array+="[]";text=text[1:]
        if text[0]=="L":kind,text=text[1:].split(";",1);kind=kind.replace("/",".")
        else:kind=PRIMITIVES[text[0]];text=text[1:]
        result.append(kind+array)
    return result

def generate_declarations(inspected, target):
    rows=[]
    for name,count in [("SDLActivity",44),("SDLInputConnection",2),("SDLAudioManager",3),("SDLControllerManager",10),("HIDDeviceManager",8)]:
        text=(inspected/(name+".smali")).read_text(encoding="utf-8")
        methods=re.findall(r"^\.method (.*?)native ([^ (]+)\(([^)]*)\)(\S+)",text,re.M)
        if len(methods)!=count:raise ValueError("SDL native registration changed: "+name)
        lines=[]
        for flags,method,params,result in methods:
            parameter_types=types(params)
            lines.append("    public "+("static " if "static" in flags else "")+"native "+types(result)[0]+" "+method+"("+", ".join(t+" p"+str(i) for i,t in enumerate(parameter_types))+");")
            rows.append({"class":"org.libsdl.app."+name,"name":method,"descriptor":"("+params+")"+result,"static":"static" in flags})
        out=target/"org/libsdl/app"/(name+".java");out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text("package org.libsdl.app;\n\n/** Exact pinned PS4 JNI_OnLoad declarations; isolated from Station SDL. */\npublic final class "+name+" {\n"+"\n".join(lines)+"\n}\n",encoding="utf-8")
    return rows

def private_rsa_material(smali, output):
    text=smali.read_text(encoding="utf-8")
    values=[]
    for i in range(16):
        match=re.search(r":array_"+format(i,"x")+r"\s+\.array-data 1(.*?)\.end array-data",text,re.S)
        if not match:raise ValueError("Missing pinned PKG array")
        values.append(bytes(int(v[:-1],16)&255 for v in re.findall(r"-?0x[0-9a-f]+t",match.group(1))))
    if [len(v) for v in values]!=[256,256,128,128,128,128,128,4]*2:
        raise ValueError("Pinned PKG array sizes changed")
    output.write_bytes(struct.pack(">II",0x50345231,16)+b"".join(struct.pack(">I",len(v))+v for v in values))

def main():
    p=argparse.ArgumentParser();p.add_argument("--apk",type=Path,required=True);p.add_argument("--jdk",type=Path,required=True)
    p.add_argument("--android-jar",type=Path,required=True);p.add_argument("--d8-jar",type=Path,required=True)
    p.add_argument("--apktool",type=Path,required=True);p.add_argument("--decoder-java",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True);p.add_argument("--generate-public-bindings",action="store_true")
    p.add_argument("--include-pkg-material",action="store_true",help="Requires specific approval for private PKG key derivation")
    a=p.parse_args();root=Path(__file__).resolve().parents[1];out=a.out.resolve()
    approved=Path(r"G:\StationNormalOwnersR127\sony-internal\ps4").resolve()
    if not out.is_relative_to(approved):raise ValueError("PS4 outputs must stay inside the approved active PS4 directory")
    if a.apk.stat().st_size!=APK_BYTES or sha(a.apk)!=APK_SHA:raise ValueError("Official APK pin mismatch")
    with zipfile.ZipFile(a.apk) as z:
        if hashlib.sha256(z.read("classes.dex")).hexdigest()!=DEX_SHA:raise ValueError("Official DEX pin mismatch")
    out.mkdir(parents=True,exist_ok=True);inspect=out/"inspect";inspect.mkdir(exist_ok=True)
    run(a.jdk/"bin/javac.exe","-cp",a.apktool,"-d",inspect,a.decoder_java)
    cp=str(inspect)+";"+str(a.apktool)
    for name in ["SDLActivity","SDLInputConnection","SDLAudioManager","SDLControllerManager","HIDDeviceManager"]:
        run(a.jdk/"bin/java.exe","-cp",cp,"DecodeOneClass",a.apk,"classes.dex","Lorg/libsdl/app/"+name+";",inspect/(name+".smali"))
    if a.include_pkg_material:
        run(a.jdk/"bin/java.exe","-cp",cp,"DecodeOneClass",a.apk,"classes.dex","Lcom/bachatas4/android/runtime/pkg/PkgRsa;",inspect/"PkgRsa.smali")
    if a.generate_public_bindings:declarations=generate_declarations(inspect,root/"child-java")
    else:
        temporary=out/"registration-check";declarations=generate_declarations(inspect,temporary)
        for source in temporary.rglob("*.java"):
            original=root/"child-java"/source.relative_to(temporary)
            if original.read_bytes()!=source.read_bytes():raise ValueError("JNI declarations differ from pinned APK: "+source.name)
    classes=out/"child-classes";classes.mkdir(exist_ok=True);dex=out/"child-dex";dex.mkdir(exist_ok=True)
    sources=sorted((root/"child-java").rglob("*.java"))
    run(a.jdk/"bin/javac.exe","--release","8","-cp",a.android_jar,"-d",classes,*sources)
    run(a.jdk/"bin/java.exe","-cp",a.d8_jar,"com.android.tools.r8.D8","--min-api","31","--lib",a.android_jar,"--output",dex,*sorted(classes.rglob("*.class")))
    if sorted(x.name for x in dex.glob("*.dex"))!=["classes.dex"]:raise ValueError("Expected one isolated DEX")
    owner=out/"owner.dex";owner.write_bytes((dex/"classes.dex").read_bytes())
    artifacts=[("owner.dex",owner)]
    if a.include_pkg_material:
        rsa=out/"pkg-rsa.bin";private_rsa_material(inspect/"PkgRsa.smali",rsa);artifacts.append(("pkg-rsa.bin",rsa))
    receipt={"schemaVersion":1,"sourceApkSha256":APK_SHA,"sourceDexSha256":DEX_SHA,"nativeRegistration":declarations,
             "recipeSha256":sha(Path(__file__)),
             "toolchain":[{"role":role,"sha256":sha(path)} for role,path in [
                 ("javac",a.jdk/"bin/javac.exe"),("java",a.jdk/"bin/java.exe"),
                 ("androidJar",a.android_jar),("d8Jar",a.d8_jar),("apktoolJar",a.apktool),
                 ("decoderSource",a.decoder_java)]],
             "sourceFiles":[{"path":str(x.relative_to(root)).replace("\\","/"),"sha256":sha(x)} for x in sources],
             "ownerDexSha256":sha(owner),"pkgMaterialSha256":sha(rsa) if a.include_pkg_material else None,
             "pkgMaterialIncluded":a.include_pkg_material,"nativeLibrariesModified":False,"phoneOperation":False}
    receipt_file=out/"owner-derivation.json";receipt_file.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    derived={"schema":"station.sony.ps4.derived.v1","sourceApkSha256":APK_SHA,"files":[{"path":"upstream/derived/"+name,"file":str(file),"bytes":file.stat().st_size,"sha256":sha(file),
             "sourceApkSha256":APK_SHA,"derivationReceiptSha256":sha(receipt_file)} for name,file in artifacts]}
    (out/"derived.json").write_text(json.dumps(derived,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"ownerDex":sha(owner),"nativeDeclarations":len(declarations),"derived":str(out/"derived.json")}))

if __name__=="__main__":main()
