#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Two opt-in SDL hooks; verify exact donor and exact inverse. No offline change."""
import argparse,hashlib,json,re
from pathlib import Path
BASE_SHA="ba8023df8f9d7bff74be26f7bbef90c01b91b5feeb0332ec646634e3eb3ece85"
READY_OLD="""    invoke-static {}, Lorg/emulationstation/frontend/auth/StationLogin;->ready()Z

    move-result v0
"""
READY_NEW="""    sget-object v0, Lorg/libsdl/app/SDLActivity;->mSingleton:Lorg/libsdl/app/SDLActivity;
    instance-of v0, v0, Lorg/emulationstation/frontend/netplay/StationPsxOnlineActivity;
    if-eqz v0, :station_psx_original_auth
    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationPsxSession;->authorizedToStart()Z
    move-result v0
    goto :station_psx_auth_checked
    :station_psx_original_auth
"""+READY_OLD+"""    :station_psx_auth_checked
"""
DESTROY="""
    instance-of v0, p0, Lorg/emulationstation/frontend/netplay/StationPsxOnlineActivity;
    if-eqz v0, :station_psx_original_destroy
    move-object v0, p0
    check-cast v0, Lorg/emulationstation/frontend/netplay/StationPsxOnlineActivity;
    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationPsxOnlineActivity;->canFinishSdlOwner()Z
    move-result v0
    if-nez v0, :station_psx_original_destroy
    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationPsxSession;->unexpectedDestroy()V
    invoke-super {p0}, Landroid/app/Activity;->onDestroy()V
    return-void
    :station_psx_original_destroy
"""
def patch(source):
    if hashlib.sha256(source).hexdigest()!=BASE_SHA:raise ValueError("SDL donor identity")
    newline='\r\n' if b'\r\n' in source else '\n'
    text=source.decode('utf8').replace('\r\n','\n')
    def method(signature):
        a=text.index(signature);b=text.index('.end method',a)+len('.end method')
        return a,b,text[a:b]
    a,b,m=method('.method public static handleNativeState()V')
    if m.count(READY_OLD)!=1:raise ValueError("SDL ready exact anchor")
    text=text[:a]+m.replace(READY_OLD,READY_NEW)+text[b:]
    a,b,m=method('.method protected onDestroy()V')
    anchor='.locals 4\n'
    if m.count(anchor)!=1:raise ValueError("SDL destroy exact locals")
    text=text[:a]+m.replace(anchor,anchor+DESTROY,1)+text[b:]
    inverse=text.replace(READY_NEW,READY_OLD,1).replace(DESTROY,'',1)
    if inverse.replace('\n',newline).encode('utf8')!=source:raise ValueError("SDL inverse identity")
    return text.replace('\n',newline).encode('utf8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--smali',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True)
    args=ap.parse_args()
    if args.smali.resolve()==args.out.resolve():raise ValueError("Never mutate donor")
    source=args.smali.read_bytes();result=patch(source)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_bytes(result)
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps({'schema':1,'donorClasses6Sha256':'f19dd92662fd066611c0e9feefd5c814bc06110f27fda50c2b3a63565965ba95','donorSmaliSha256':BASE_SHA,'patchedSmaliSha256':hashlib.sha256(result).hexdigest(),'changedMethods':['handleNativeState()V','onDestroy()V'],'optInClass':'org.emulationstation.frontend.netplay.StationPsxOnlineActivity','offlineReadyUnchanged':True,'offlineDestroyUnchanged':True,'inverseByteIdentical':True,'notPackaged':True},indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
