"""Execute R117 graphics state and row planners against the final compiled classes.

Host checks only; they do not establish Android appearance, heat or gameplay.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('work', 'build', 'jdk', 'android-jar', 'host-clang'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=False)
    environment = dict(os.environ, TEMP=str(args.work), TMP=str(args.work))
    cp = os.pathsep.join(map(str, (args.work, args.build/'client.jar', args.build/'rooms.jar', args.android_jar)))

    def run(command, label):
        result = subprocess.run(list(map(str, command)), env=environment, capture_output=True, text=True)
        (args.work/(label+'.log')).write_text(result.stdout+result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(label+' failed; inspect private test log')
        return result.stdout.strip()

    names = ('StationGraphicsPreferencesTest', 'StationMagazineRowsTest')
    paths = []
    for name in names:
        path = args.work/(name+'.java')
        shutil.copyfile(ROOT/'tests'/(name+'.java'), path)
        paths.append(path)
    run([args.jdk/'javac.exe', '-encoding', 'UTF-8', '--release', '8', '-proc:none', '-cp', cp,
         '-d', args.work, *paths], 'graphics-javac')
    preferences = run([args.jdk/'java.exe', '-cp', cp,
                       'org.emulationstation.frontend.station.StationGraphicsPreferencesTest'], 'preferences')
    rows = run([args.jdk/'java.exe', '-cp', cp,
                'org.emulationstation.frontend.netplay.StationMagazineRowsTest'], 'java-rows')
    assert preferences == 'PASS 51 graphics state checks', preferences
    assert rows == 'PASS 7978753 executed Java progressive-field row checks', rows
    native_source = args.work/'magazine_rows_test.cpp'
    native_source.write_text((ROOT/'tests/magazine_rows_test.cpp').read_text(encoding='utf-8')
                            .replace('../native/d0/native_magazine_rows.h', str(ROOT/'native/d0/native_magazine_rows.h').replace('\\', '/')),
                            encoding='utf-8')
    native_exe = args.work/'magazine_rows_test.exe'
    run([args.host_clang, '-std=c++17', '-O2', '-Wall', '-Wextra', native_source, '-o', native_exe], 'native-rows-clang')
    native_rows = run([native_exe], 'native-rows')
    assert native_rows.startswith('PASS 2659588 '), native_rows
    result = {'version': 'R117', 'passed': True,
              'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'preferences': preferences, 'javaRows': rows, 'nativeRows': native_rows,
              'compiledJarSHA256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in (args.build/'client.jar', args.build/'rooms.jar')},
              'sourceSHA256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (ROOT/'tests/StationGraphicsPreferencesTest.java',
                                         ROOT/'tests/StationMagazineRowsTest.java',
                                         ROOT/'tests/magazine_rows_test.cpp')},
              'scope': 'host state/row planners using final compiled Java; no Android visual/thermal/gameplay proof',
              'physicalValidation': False, 'thermalClaim': False}
    (ROOT/'evidence/graphics-state-rows-r117.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
