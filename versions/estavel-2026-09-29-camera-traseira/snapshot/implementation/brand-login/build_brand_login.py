"""Visual-only derivative of the exact stable APK; all engine and auth rules stay intact."""
from pathlib import Path
import argparse, hashlib, io, json, os, re, shutil, subprocess, zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parent
P = ROOT.parent
parser = argparse.ArgumentParser()
parser.add_argument('--base-apk', type=Path, default=P / 'TurboramaStation-ESTAVEL-6727ab7-design.apk')
parser.add_argument('--base-sha256', default='545e9b71e24da653f59ca67e2dd5f716a26fec3a64f5eb39860c87f14303f4e6')
args = parser.parse_args()
BASE = args.base_apk
OUTPUT = P / 'TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk'
JAVA = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
JAVAC = JAVA.with_name('javac.exe')
SDK = Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
BT = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
APKTOOL = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
ORIGINAL = ROOT / 'original-login'
MERGED = ROOT / 'merged-login'
JAVA_PACKAGE = Path('org/emulationstation/frontend/auth')
TMP = ROOT / 'tmp'
os.environ['TEMP'] = os.environ['TMP'] = str(TMP)
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes()) == args.base_sha256
with zipfile.ZipFile(P / 'stable-reference-audit/original-1.0.8-alignment-preserved.apk') as reference, zipfile.ZipFile(BASE) as current:
    for name in reference.namelist():
        if name.startswith('lib/') or (name.endswith('.dex') and name != 'classes5.dex'):
            assert reference.read(name) == current.read(name), 'Nonvisual stable component changed: ' + name
for name in ['classes', 'compile-stubs', 'dex', 'tmp', 'assets/launcher']:
    (ROOT / name).mkdir(parents=True, exist_ok=True)

def run(*args):
    subprocess.run(list(map(str, args)), check=True)

def apktool(*args):
    run(JAVA, '-Djava.io.tmpdir=' + str(TMP), '-jar', APKTOOL, *args)

if not ORIGINAL.exists():
    with zipfile.ZipFile(BASE) as z, zipfile.ZipFile(ROOT / 'original-login.apk', 'w') as out:
        for name in ['AndroidManifest.xml', 'resources.arsc']:
            out.writestr(name, z.read(name))
        out.writestr('classes.dex', z.read('classes8.dex'))
    apktool('d', '-r', '-f', '-p', P / 'framework', '-o', ORIGINAL, ROOT / 'original-login.apk')

# Only a compile-time declaration, excluded from the dex and APK. Existing AuthSession
# and LocalPassword are copied without any source changes from the stable dex below.
stub = ROOT / 'compile-stubs' / JAVA_PACKAGE / 'AuthSession.java'
stub.parent.mkdir(parents=True, exist_ok=True)
stub.write_text('package org.emulationstation.frontend.auth; public final class AuthSession { public static boolean isAuthorized(){ throw new UnsupportedOperationException(); } public static boolean authenticate(String value){ throw new UnsupportedOperationException(); } }', encoding='utf8')
run(JAVAC, '-encoding', 'UTF-8', '-source', '8', '-target', '8', '-cp', SDK,
    '-d', ROOT / 'classes', stub, ROOT / 'java' / JAVA_PACKAGE / 'LoginActivity.java')
classes = sorted((ROOT / 'classes' / JAVA_PACKAGE).glob('LoginActivity*.class'))
assert classes
run(JAVA, '-Djava.io.tmpdir=' + str(TMP), '-cp', BT / 'lib/d8.jar', 'com.android.tools.r8.D8',
    '--min-api', '26', '--lib', SDK, '--output', ROOT / 'dex', *classes)
with zipfile.ZipFile(BASE) as z, zipfile.ZipFile(ROOT / 'new-login.apk', 'w') as out:
    for name in ['AndroidManifest.xml', 'resources.arsc']:
        out.writestr(name, z.read(name))
    out.write(ROOT / 'dex/classes.dex', 'classes.dex')
apktool('d', '-r', '-f', '-p', P / 'framework', '-o', ROOT / 'new-login', ROOT / 'new-login.apk')
if not MERGED.exists():
    shutil.copytree(ORIGINAL, MERGED)

original_smali = ORIGINAL / 'smali' / JAVA_PACKAGE
new_smali = ROOT / 'new-login/smali' / JAVA_PACKAGE
merged_smali = MERGED / 'smali' / JAVA_PACKAGE
for src in new_smali.glob('LoginActivity*.smali'):
    shutil.copy2(src, merged_smali / src.name)

# Keep exact stable implementations of the five authentication/navigation methods.
protected = ['ensureAuthorized(Landroid/app/Activity;)V', 'submit()V',
             'openFrontend()V', 'onNewIntent(Landroid/content/Intent;)V', 'onBackPressed()V']
original_text = (original_smali / 'LoginActivity.smali').read_text(encoding='utf8')
merged_file = merged_smali / 'LoginActivity.smali'
merged_text = merged_file.read_text(encoding='utf8')
method_hashes = {}
for method in protected:
    pattern = r'(?m)^\.method [^\n]*' + re.escape(method) + r'\n[\s\S]*?^\.end method'
    old = re.search(pattern, original_text)
    assert old and len(re.findall(pattern, merged_text)) == 1, method
    merged_text = re.sub(pattern, lambda _: old.group(), merged_text)
    method_hashes[method] = sha(old.group().encode())
merged_file.write_text(merged_text, encoding='utf8')
for original in (ORIGINAL / 'smali').rglob('*.smali'):
    relative = original.relative_to(ORIGINAL)
    if not original.name.startswith('LoginActivity'):
        assert original.read_bytes() == (MERGED / relative).read_bytes(), relative
apktool('b', '-p', P / 'framework', '-o', ROOT / 'merged-login.apk', MERGED)
with zipfile.ZipFile(ROOT / 'merged-login.apk') as z:
    dex = z.read('classes.dex')

master = Image.open(ROOT / 'assets/turborama-icon-master.png').convert('RGB')
replacements = {'classes8.dex': dex}
with zipfile.ZipFile(BASE) as z:
    icon_names = [n for n in z.namelist() if n == 'res/drawable/ic_launcher_foreground.png'
                  or re.fullmatch(r'res/mipmap-[^/]+/ic_launcher.png', n)]
    assert len(icon_names) == 6, icon_names
    for name in icon_names:
        with Image.open(io.BytesIO(z.read(name))) as previous:
            size = previous.size
        # Mechanical Android density sizing. Adaptive foreground keeps the entire
        # generated emblem inside the 66/108 safe area regardless of launcher mask.
        fraction = 0.74 if name.endswith('ic_launcher_foreground.png') else 1.15
        side = round(min(size) * fraction)
        icon = Image.new('RGB', size, (0, 0, 0))
        icon.paste(master.resize((side, side), Image.Resampling.LANCZOS),
                   ((size[0] - side) // 2, (size[1] - side) // 2))
        buf = io.BytesIO()
        icon.save(buf, format='PNG', optimize=True)
        replacements[name] = buf.getvalue()
        (ROOT / 'assets/launcher' / (name.split('/')[1] + '.png')).write_bytes(buf.getvalue())

unsigned, aligned = ROOT / 'brand-unsigned.apk', ROOT / 'brand-aligned.apk'
asset_name = 'assets/turborama-brand/turborama-icon-master.png'
with zipfile.ZipFile(BASE) as src, zipfile.ZipFile(unsigned, 'w', allowZip64=True) as out:
    for info in src.infolist():
        if info.filename.startswith('META-INF/'):
            continue
        out.writestr(info, replacements.get(info.filename, src.read(info.filename)))
    out.write(ROOT / 'assets/turborama-icon-master.png', asset_name, compress_type=zipfile.ZIP_DEFLATED)
run(BT / 'zipalign.exe', '-f', '-P', '16', '4', unsigned, aligned)
run(JAVA, '-jar', BT / 'lib/apksigner.jar', 'sign', '--alignment-preserved', 'true',
    '--ks', r'C:\Users\Admin\.android\debug.keystore', '--ks-key-alias', 'androiddebugkey',
    '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--out', OUTPUT, aligned)
run(JAVA, '-jar', BT / 'lib/apksigner.jar', 'verify', '--verbose', '--print-certs', OUTPUT)
with zipfile.ZipFile(BASE) as a, zipfile.ZipFile(OUTPUT) as b:
    old = {n for n in a.namelist() if not n.startswith('META-INF/')}
    new = {n for n in b.namelist() if not n.startswith('META-INF/')}
    changed = sorted(n for n in old & new if sha(a.read(n)) != sha(b.read(n)))
    assert changed == sorted(replacements), changed
    assert not old - new
    assert new - old == {asset_name}
report = dict(apk=str(OUTPUT), sha256=sha(OUTPUT.read_bytes()), bytes=OUTPUT.stat().st_size,
    base=str(BASE), base_sha256=sha(BASE.read_bytes()), stable_commit='6727ab7',
    changed=changed, added=[asset_name], removed=[], all_native_libraries_identical=True,
    manifest_and_resources_table_identical=True, stable_auth_methods=method_hashes,
    non_login_classes_preserved=True, emulator_and_catalog_settings_unchanged=True,
    installed=False)
(ROOT / 'build-result.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))

