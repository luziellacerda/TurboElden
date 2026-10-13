"""Build a standalone Android JNI resource audit; never runs ADB or installs an APK."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parent
SOURCE_SHA256='24420118e5ce94376b077051084a84d4c52f152d00b9e2330333896bced798fb'
FUNCTIONS=['station_jni_key_ensure','jni_thread_getenv','jni_thread_destruct']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--patch-recipe',type=Path,required=True)
    parser.add_argument('--ndk',type=Path,required=True)
    parser.add_argument('--jdk-bin',type=Path,required=True)
    parser.add_argument('--d8-jar',type=Path,required=True)
    parser.add_argument('--android-jar',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output=args.output.resolve()
    repository=ROOT.parents[1].resolve()
    if args.output.exists() or args.output.is_relative_to(repository):
        raise ValueError('Output must be a fresh directory outside the repository')
    if digest(args.source)!=SOURCE_SHA256:
        raise ValueError('Wrong frozen R139 source')
    sys.path.insert(0,str(args.patch_recipe.resolve().parent))
    from patch_resource_lifecycle import function_span
    source=args.source.read_bytes().decode('utf-8')
    functions={}
    for name in FUNCTIONS:
        a,b=function_span(source,name);functions[name]=source[a:b]
    start=source.index('static pthread_key_t thread_key;')
    end=source.index('static JavaVM *station_jni_vm = NULL;',start)+len('static JavaVM *station_jni_vm = NULL;')
    globals=source[start:end]
    template=ROOT/'src/resource_probe.c.in'
    generated=template.read_text().replace('/* @TLS_GLOBALS@ */',globals)
    bodies='static void jni_thread_destruct(void *value);\n\n'+'\n\n'.join(functions.values())
    generated=generated.replace('/* @PRODUCTION_FUNCTIONS@ */',bodies)
    args.output.mkdir(parents=True,exist_ok=False)
    c=args.output/'resource_probe.c';c.write_bytes(generated.encode('utf-8'))
    library=args.output/'libresourceprobe.so'
    compiler=args.ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
    command=[str(compiler),'--target=aarch64-linux-android26','-std=c11','-fPIC','-shared','-O2',
             '-Wall','-Wextra','-Werror','-Wno-unused-function','-Wl,-z,max-page-size=16384',str(c),'-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,timeout=120)
    if run.returncode:raise RuntimeError('NDK probe compilation failed: '+run.stderr)
    classes=args.output/'classes';classes.mkdir()
    java=args.jdk_bin/'java.exe';javac=args.jdk_bin/'javac.exe'
    java_source=ROOT/'src/R139ResourceProbe.java'
    run=subprocess.run([str(javac),'--release','8','-encoding','UTF-8','-d',str(classes),str(java_source)],capture_output=True,text=True,timeout=60)
    if run.returncode:raise RuntimeError('Probe Java compilation failed: '+run.stderr)
    dex=args.output/'dex';dex.mkdir()
    run=subprocess.run([str(java),'-cp',str(args.d8_jar),'com.android.tools.r8.D8','--release','--min-api','26',
                        '--lib',str(args.android_jar),'--output',str(dex),*[str(p) for p in sorted(classes.rglob('*.class'))]],capture_output=True,text=True,timeout=60)
    if run.returncode:raise RuntimeError('Probe D8 failed: '+run.stderr)
    if sorted(p.name for p in dex.iterdir())!=['classes.dex']:raise ValueError('Unexpected D8 output')
    jar=args.output/'probe.jar'
    entry=zipfile.ZipInfo('classes.dex',(2026,10,13,0,0,0));entry.compress_type=zipfile.ZIP_STORED
    with zipfile.ZipFile(jar,'x') as archive:archive.writestr(entry,(dex/'classes.dex').read_bytes())
    report=dict(schemaVersion=1,sourceSha256=SOURCE_SHA256,
                productionFunctions={name:hashlib.sha256(value.encode()).hexdigest() for name,value in functions.items()},
                productionGlobalsSha256=hashlib.sha256(globals.encode()).hexdigest(),
                templateSha256=digest(template),javaSourceSha256=digest(java_source),patchRecipeSha256=digest(args.patch_recipe),
                compilerSha256=digest(compiler),javaSha256=digest(java),javacSha256=digest(javac),
                d8JarSha256=digest(args.d8_jar),androidJarSha256=digest(args.android_jar),
                generatedCSha256=digest(c),librarySha256=digest(library),libraryBytes=library.stat().st_size,
                jarSha256=digest(jar),jarBytes=jar.stat().st_size,
                target='aarch64-linux-android26',minimumLoadAlignment=16384,
                buildOnly=True,apkInstalled=False,androidExecuted=False)
    (args.output/'build-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(libraryBytes=report['libraryBytes'],jarBytes=report['jarBytes'],
                         functions=list(functions),output=str(args.output)),indent=2))


if __name__=='__main__':main()
