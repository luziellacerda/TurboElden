from pathlib import Path
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
SNAPSHOT=Path(__file__).resolve().parent.parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def composition():
    base=SNAPSHOT.parent/'station-collection-videos-r67-20261007'
    spec=importlib.util.spec_from_file_location('station_r67_baseline',base/'recipes/source_composition.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.verified_composition();baseline={name:sha(path) for name,path in result.items()}
    for prefix in ('client/src/java/','netplay-src/','dependency-src/'):
        for path in (SNAPSHOT/prefix).rglob('*.java'):result[path.relative_to(SNAPSHOT).as_posix()]=path
    return result,baseline
def verified_composition():
    result,baseline=composition();manifest=json.loads((SNAPSHOT/'JAVA-SOURCE-MANIFEST.json').read_text())
    if manifest['baseline']!=baseline or manifest['files']!={name:sha(path) for name,path in result.items()}:raise RuntimeError('Exact R67 recovery sources required')
    return result
