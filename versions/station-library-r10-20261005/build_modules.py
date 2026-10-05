"""Compile Station DEX/JNI in a private output folder; no signing, installation or credential access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work-root',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True)
    p.add_argument('--ndk',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--android-api',default='36');p.add_argument('--build-tools',default='36.0.0')
    p.add_argument('--jdk',type=Path);p.add_argument('--build-carousel',action='store_true')
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    if out.is_relative_to(a.work_root.resolve()):raise ValueError('Output must be separate from source')
    suffix='.exe' if os.name=='nt' else '';host='windows-x86_64' if os.name=='nt' else 'linux-x86_64'
    cc=a.ndk/'toolchains/llvm/prebuilt'/host/'bin'/('clang++'+suffix)
    javac=a.jdk/('javac'+suffix) if a.jdk else 'javac';java=a.jdk/('java'+suffix) if a.jdk else 'java'
    android=a.sdk/'platforms'/('android-'+a.android_api)/'android.jar'
    classes=out/'classes';classes.mkdir();dex=out/'dex';dex.mkdir()
    subprocess.run([str(javac),'-encoding','UTF-8','--release','8','-Xlint:-options','-cp',str(android),'-d',str(classes),
                    *map(str,sorted((a.work_root/'station/src/java').rglob('*.java')))],check=True)
    jar=out/'station-client.jar'
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(classes.rglob('*.class')):z.write(path,path.relative_to(classes).as_posix())
    subprocess.run([str(java),'-cp',str(a.sdk/'build-tools'/a.build_tools/'lib/d8.jar'),'com.android.tools.r8.D8',
                    '--min-api','26','--lib',str(android),'--output',str(dex),str(jar)],check=True)
    common=[str(cc),'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2',
            '-Wl,-z,max-page-size=16384','-Wl,--no-undefined']
    subprocess.run([*common,'-fvisibility=hidden','-Wall','-Wextra','-Werror','-Wno-return-type-c-linkage',
                    '-static-libstdc++','-Wl,--exclude-libs,ALL',str(a.work_root/'station/src/native/station_frontend.cpp'),
                    '-ldl','-llog','-o',str(out/'libstation_frontend.so')],check=True)
    if a.build_carousel:
        native=a.work_root/'native'
        subprocess.run([*common,'-nostdlib','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin',
                        '-Wl,-soname,libturbo_carousel.so',str(native/'native_carousel.cpp'),str(native/'video720_posters.o'),
                        '-L',str(native),'-lc','-ldl','-llog','-o',str(out/'libturbo_carousel.so')],check=True)
    files=[out/'station-client.jar',dex/'classes.dex',out/'libstation_frontend.so']
    if a.build_carousel:files.append(out/'libturbo_carousel.so')
    report=dict(apkSigned=False,installed=False,androidGameplayVerified=False,
                files={str(file.relative_to(out)):dict(bytes=file.stat().st_size,sha256=hashlib.sha256(file.read_bytes()).hexdigest()) for file in files})
    (out/'compiled-modules.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

if __name__=='__main__':main()
