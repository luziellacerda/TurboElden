from pathlib import Path
p=Path(__file__).parent
old=(p.parent.parent/'station-pump-wakeup-r76-20261008/recipes/build_candidate.py').read_text('utf8')
a=old.index('def base_sources():');b=old.index('def main():',a)
new='''def verified_sources():
    spec=importlib.util.spec_from_file_location('frozen_r76',PREVIOUS/'recipes/build_candidate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    baseline,overlay,sources,_=module.verified_sources()
    original=dict(sources)
    for f in (SNAPSHOT/'java').rglob('*.java'):
        n=f.relative_to(SNAPSHOT/'java').as_posix();sources[n]=f;overlay[n]=f
    return baseline,overlay,sources,None
'''
old=old[:a]+new+old[b:]
old=old.replace("'station-session-lifecycle-r74-20261007'","'station-pump-wakeup-r76-20261008'")
old=old.replace("DEFAULT_WORK=r'E:\\ESTUDO APK\\work\\station-pump-wakeup-r76-20261008\\compiled-final'","DEFAULT_WORK=r'E:\\ESTUDO APK\\work\\station-multiplayer-r77-20261008\\java-build-01'")
a=old.index('    if a.baseline:');b=old.index('    source_hashes=',a)
old=old[:a]+"    require(not a.baseline,'R76 baseline already preserved; this recipe builds R77 only')\n    _,_,sources,manifest=verified_sources()\n"+old[b:]
old=old.replace("require(hashes['clientDexSHA256']==CLIENT_DEX,'Client DEX must remain identical')","require(hashes['clientDexSHA256']!=CLIENT_DEX,'New fixed multiplayer API required')")
old=old.replace("base='R74'","base='R76'").replace("clientDexUnchanged=True","clientDexUnchanged=False")
old=old.replace("changedDexSlots=[] if a.baseline else ['classes35.dex']","changedDexSlots=['classes28.dex','classes35.dex']")
(p/'build_java.py').write_text(old,'utf8')
print('R77 build recipe prepared')
