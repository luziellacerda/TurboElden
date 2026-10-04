from pathlib import Path
import hashlib,shutil,json,subprocess,re
R=Path(r'E:\StationNetplayWork');out=R/'runtime';out.mkdir(exist_ok=True)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[('snes','bsnes-mercury-performance-79d7f9de','bsnes/lib/arm64-v8a/libretro.so','libstation_bsnes.so','libretro--bsnes-mercury-79d7f9de218b','GPL-3.0-or-later',['sfc','smc'],'snes.cfg'),('megadrive','clownmdemu-d43c2708','clownmdemu/clownmdemu_libretro.so','libstation_clownmdemu.so','Clownacy--clownmdemu-libretro-d43c2708b0a3','AGPL-3.0-or-later',['bin','md','gen'],'genesis.cfg'),('neogeo','geolith-19402493','geolith/lib/arm64-v8a/libretro.so','libstation_geolith.so','libretro--geolith-libretro-194024931935','BSD-3-Clause',['neo'],'neogeo.cfg')]
ra=out/'libstation_retroarch.so';shutil.copy2(R/'engine-build/retroarch/lib/arm64-v8a/libretroarch-activity.so',ra)
assets=R/'assets/station-online';(assets/'licenses').mkdir(parents=True,exist_ok=True);engines=[];elf=[]
tools=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin')
for platform,id,input,name,source,license,extensions,overlay in rows:
 dest=out/name;shutil.copy2(R/'engine-build'/input,dest)
 subprocess.run([str(tools/'llvm-strip.exe'),'--strip-debug',str(dest)],check=True)
 options=''
 if platform=='snes':options='bsnes_violate_accuracy = "disabled"\nbsnes_chip_hle = "LLE"\nbsnes_superfx_overclock = "100%"\nbsnes_region = "auto"\nbsnes_aspect_ratio = "auto"\nbsnes_crop_overscan = "disabled"\nbsnes_gamma_ramp = "disabled"\n'
 # Empty options is intentional upstream default policy, hashed identically on both peers.
 e=dict(engineId=id,platform=platform,library=name,coreSha256=sha(dest),runtimeSha256=sha(ra),extensions=extensions,overlay='gamepads/flat/'+overlay,options=options,launchReady=platform!='neogeo',license=license,sourceDirectory=source)
 engines.append(e)
 sourcepath=R/'upstream'/source
 candidates=list(sourcepath.glob('LICENSE*'))+list(sourcepath.glob('COPYING*'))+list(sourcepath.glob('License*'))+list(sourcepath.glob('LICENCE*'))
 if not candidates:
  candidates=list(sourcepath.glob('snes/License*'))+list(sourcepath.glob('licenses/*'))
 assert candidates,(platform,'license file missing')
 for p in candidates:
  if p.is_file():shutil.copy2(p,assets/'licenses'/(id+'-'+p.name))
for name in ('COPYING','COPYING.libretro'):
 p=R/'upstream/libretro--RetroArch-69a4f0ea1e8a'/name
 if p.is_file():shutil.copy2(p,assets/'licenses'/('RetroArch-'+name))
for p in out.glob('*.so'):
 headers=subprocess.check_output([str(tools/'llvm-readelf.exe'),'-h','-l','-d',str(p)],text=True)
 assert 'AArch64' in headers
 aligns=[int(line.split()[-1],16) for line in headers.splitlines() if line.strip().startswith('LOAD ')]
 assert aligns and min(aligns)>=16384,(p.name,aligns)
 symbols=subprocess.check_output([str(tools/'llvm-nm.exe'),'--defined-only','--dynamic',str(p)],text=True)
 for symbol in (['ANativeActivity_onCreate'] if p==ra else ['retro_init','retro_run','retro_load_game','retro_serialize','retro_unserialize','retro_serialize_size']):assert re.search(r'\b'+symbol+r'\b',symbols),(p.name,symbol)
 elf.append(dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size,minimumLoadAlignment=min(aligns),architecture='AArch64',requiredExportsPresent=True))
(assets/'engines.json').write_text(json.dumps({'schemaVersion':1,'androidPeerPlayValidated':False,'engines':engines},ensure_ascii=False,indent=2),'utf-8')
(R/'evidence/engine-build-validation.json').write_text(json.dumps({'androidExecuted':False,'peerPlayValidated':False,'elf':elf},indent=2),'utf-8')
(R/'server/engine-registry-candidate.json').write_text(json.dumps([dict(id=e['engineId'],platform=e['platform'],coreSha256=e['coreSha256'],runtimeSha256=e['runtimeSha256']) for e in engines if e['launchReady']],indent=2),'utf-8')
(assets/'NOTICES.txt').write_text('Motores online compilados de fontes oficiais fixadas em commit.\nRetroArch: GPL-3.0-or-later. bsnes-mercury: GPL-3.0-or-later. ClownMDEmu: AGPL-3.0-or-later. Geolith: BSD-3-Clause.\nControles Flat: libretro/common-overlays, CC-BY-4.0. Atribuição e licença em overlays/.\nAs licenças completas estão nesta pasta em licenses/. Corresponding source, alterações e receitas de compilação são publicadas no repositório TurboElden, versions/station-online-20261004/.\nNeo Geo requer preparação adicional de BIOS e formato .neo, ainda não ativada. Não há redistribuição nova de BIOS ou jogos neste módulo.\nEstas licenças dos motores novos não comprovam a conformidade de todos os motores anteriores do aplicativo.\n','utf-8')
print(json.dumps({'engines':len(engines),'elfValidated':len(elf),'registryCandidates':2,'androidPeerPlayValidated':False}))
