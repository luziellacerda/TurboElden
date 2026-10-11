"""Reuse frozen R127 recipes with an explicit, closed R128 offline overlay."""
from pathlib import Path
import hashlib
import types

ROOT = Path(__file__).resolve().parents[1]
PSX = ROOT.parent / 'psx-online'
SHARED_ADDITIONS = frozenset(('classes39.dex', 'lib/arm64-v8a/libturbo_carousel.so'))

def load_psx(name, *, r128=False):
    source = PSX / 'recipe' / (name + '.py')
    text = source.read_text(encoding='utf-8')
    if r128:
        text = text.replace('"R127"', '"R128"')
    module = types.ModuleType('r128_parent_' + name)
    module.__file__ = str(source)
    exec(compile(text, str(source), 'exec'), module.__dict__)
    return module

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def offline_sources():
    result = {}
    for name, suffixes in [('java', {'.java'}), ('native', {'.cpp', '.hpp', '.h'}), ('recipe', {'.py'})]:
        for path in sorted((ROOT / name).rglob('*')):
            if path.is_file() and path.suffix in suffixes:
                result['offline/' + path.relative_to(ROOT).as_posix()] = sha(path)
    if not result or not any(n.endswith('.java') for n in result):
        raise ValueError('Complete offline bridge sources must exist before freezing')
    for name in ('catalog-platforms.json', 'contracts.json'):
        contract = ROOT / name
        if contract.exists():
            result['offline/' + name] = sha(contract)
    return result

def assembler():
    module = load_psx('assemble_apk', r128=True)
    module.SHARED |= SHARED_ADDITIONS
    module.REPLACED |= frozenset(('lib/arm64-v8a/libturbo_carousel.so',))
    module.ADDED |= frozenset(('classes39.dex',))
    module.PAYLOADS = module.REPLACED | module.ADDED
    current = module.current_sources
    def sources():
        java, transforms = current()
        return java, {**transforms, **offline_sources()}
    module.current_sources = sources
    return module
