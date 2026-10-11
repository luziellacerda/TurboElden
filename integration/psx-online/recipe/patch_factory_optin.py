#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Select a plain Application only in the exact private PSX process. Offline inverse unchanged."""
import argparse,hashlib,json
from pathlib import Path
BASE_SHA="786d7e2a6a9ded6ef4e116791c67b9b70809f4c62a147b790ae2595e3c92d47c"
DEX_SHA="4d8e479f445396fa052bee5f7489a5748abdbfdccc9db4c7d035c8f2d0c646fa"
SIGNATURE='instantiateApplication(Ljava/lang/ClassLoader;Ljava/lang/String;)Landroid/app/Application;'
ANCHOR="    .line 39\n    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/station/StationComponentFactory;->original(Ljava/lang/ClassLoader;)Landroid/app/AppComponentFactory;"
HOOK="""    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationPsxApplication;->isPrivateProcess()Z
    move-result v0
    if-eqz v0, :station_psx_original_application
    const-string p2, "org.emulationstation.frontend.netplay.StationPsxApplication"
    invoke-super {p0, p1, p2}, Landroid/app/AppComponentFactory;->instantiateApplication(Ljava/lang/ClassLoader;Ljava/lang/String;)Landroid/app/Application;
    move-result-object v0
    return-object v0
    :station_psx_original_application

"""
def patch(source):
    if hashlib.sha256(source).hexdigest()!=BASE_SHA:raise ValueError('Factory donor identity')
    nl='\r\n' if b'\r\n' in source else '\n';s=source.decode().replace('\r\n','\n')
    a=s.index(SIGNATURE);b=s.index('.end method',a)
    m=s[a:b]
    if m.count(ANCHOR)!=1:raise ValueError('Factory exact anchor')
    result=s[:a]+m.replace(ANCHOR,HOOK+ANCHOR)+s[b:]
    if result.replace(HOOK,'',1).replace('\n',nl).encode()!=source:raise ValueError('Factory inverse')
    return result.replace('\n',nl).encode()
def main():
    p=argparse.ArgumentParser();p.add_argument('--smali',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
    if a.smali.resolve()==a.out.resolve():raise ValueError('Never mutate donor')
    source=a.smali.read_bytes();result=patch(source);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(result)
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps({'schema':1,'donorClasses28Sha256':DEX_SHA,'donorSmaliSha256':BASE_SHA,'patchedSmaliSha256':hashlib.sha256(result).hexdigest(),'changedMethod':SIGNATURE,'onlyProcess':'org.turboramastation.frontend:station_psx_online','onlyApi':'>=28','selectedApplication':'org.emulationstation.frontend.netplay.StationPsxApplication','originalManifestUnchanged':True,'inverseByteIdentical':True,'otherProcessesUnchanged':True,'authenticationUnchanged':True},indent=2)+'\n')
if __name__=='__main__':main()
