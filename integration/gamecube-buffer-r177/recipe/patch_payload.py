"""Minimal changes to the exact R176/R173-effective Dolphin bytecode.

Keep every existing launch check and session instruction. Replace only the
platform-dependent expected options and insert the CurrentRun buffer policy
after nativeConfigure, before nativeConnect/Host reads the setting.
"""
from pathlib import Path
import re

PREFIX = 'org/emulationstation/frontend/netplay/'
POLICY = 'L' + PREFIX + 'StationDolphinBufferPolicy;'
OLD_OPTIONS = r'backend=dolphin-station-v1\nwire=DPL1\nsettingsPolicy=official-pinned-gameini+host-synchronized-strict-v1\ntraversal=direct\nupnp=false\nindex=false\nqos=false\nchunkedUploadLimit=false\nnetworkMode=fixeddelay\npadBuffer=5\nclientBuffer=1\nsaveLoad=true\nsaveWrite=true\nsyncAllWii=false\nsyncCodes=false\ncheats=false\nrecordInputs=false\nstrictSettingsSync=true\ngolfMode=false\nremoteGbas=false\nsaves=session-only\n'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def json_options(obj, register):
    return (f'    const-string {register}, "platform"\n\n'
            f'    invoke-virtual {{{obj}, {register}}}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;\n\n'
            f'    move-result-object {register}\n\n'
            f'    invoke-static {{{register}}}, {POLICY}->options(Ljava/lang/String;)Ljava/lang/String;\n\n'
            f'    move-result-object {register}')

def replace_method_literal(text, method_name, register, replacement):
    pattern = re.compile(r'(?ms)^\.method [^\n]*' + re.escape(method_name) + r'\([^\n]*\n.*?^\.end method$')
    found = list(pattern.finditer(text))
    need(len(found) == 1, 'Exact method required: ' + method_name)
    method = found[0].group()
    anchor = f'    const-string {register}, "{OLD_OPTIONS}"'
    need(method.count(anchor) == 1, 'Exact options register/lifetime: ' + method_name)
    patched = method.replace(anchor, replacement)
    return text[:found[0].start()] + patched + text[found[0].end():]

def patch(root, overlay):
    root, overlay = Path(root), Path(overlay)
    session = root / (PREFIX + 'StationDolphinSession$Session.smali')
    raw = session.read_text()
    anchor = ('    iput-boolean v11, v7, Lorg/emulationstation/frontend/netplay/StationDolphinSession$Session;->configured:Z\n\n'
              '    .line 110\n    iget-boolean v0, v7, Lorg/emulationstation/frontend/netplay/StationDolphinSession$Session;->closing:Z')
    need(raw.count(anchor) == 1 and 'StationDolphinCpuPolicy;' not in raw and POLICY not in raw,
         'Exact R173 configured/closing register lifetime')
    injection = ('    iget-object v0, v7, Lorg/emulationstation/frontend/netplay/StationDolphinSession$Session;->platform:Ljava/lang/String;\n\n'
                 f'    invoke-static {{v0}}, {POLICY}->configure(Ljava/lang/String;)V\n\n')
    session.write_text(raw.replace(anchor, anchor.replace('    .line 110', injection + '    .line 110')))

    launch = root / (PREFIX + 'StationDolphinLaunch.smali')
    raw = launch.read_text()
    raw = replace_method_literal(raw, 'prepare', 'v5',
        '    iget-object v5, v1, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->platform:Ljava/lang/String;\n\n'
        f'    invoke-static {{v5}}, {POLICY}->options(Ljava/lang/String;)Ljava/lang/String;\n\n'
        '    move-result-object v5')
    for method, obj, register in [('validate', 'p0', 'v1'), ('verifyBinaries', 'p1', 'v2'), ('verifyIdentity', 'p0', 'v1')]:
        raw = replace_method_literal(raw, method, register, json_options(obj, register))
    # The unused legacy constant remains byte-for-byte intact; validation and
    # construction now choose the exact platform options from one policy.
    need(raw.count(OLD_OPTIONS) == 1 and raw.count(POLICY + '->options(') == 4, 'All four launch option checks updated')
    launch.write_text(raw)

    profile = root / (PREFIX + 'StationMultiplayerProfile.smali')
    raw = profile.read_text()
    replacement = ('    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->platform:Ljava/lang/String;\n\n'
                   f'    invoke-static {{v0}}, {POLICY}->options(Ljava/lang/String;)Ljava/lang/String;\n\n'
                   '    move-result-object v0')
    profile.write_text(replace_method_literal(raw, '<init>', 'v0', replacement))

    helper = PREFIX + 'StationDolphinBufferPolicy.smali'
    need(not (root / helper).exists(), 'New policy already present')
    (root / helper).write_bytes((overlay / helper).read_bytes())
    return {PREFIX + n for n in ('StationDolphinSession$Session.smali',
                                'StationDolphinLaunch.smali',
                                'StationMultiplayerProfile.smali')}, {helper}
