"""Restore the exact pre-trial GC policy and add narrowly bounded GBA/Wii paths."""
from pathlib import Path
import hashlib
import re

PREFIX = 'org/emulationstation/frontend/netplay/'
GBA = 'L' + PREFIX + 'StationGbaLinkPolicy;'
RESTORE = ('StationDolphinSession$Session.smali', 'StationDolphinLaunch.smali',
           'StationMultiplayerProfile.smali')

def need(ok, why):
    if not ok:
        raise ValueError(why)

def projection(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*.smali')}

def patch(root, rollback, overlay):
    root, rollback, overlay = map(Path, (root, rollback, overlay))
    original = projection(root)
    for name in RESTORE:
        target = root / (PREFIX + name)
        need(target.exists() and (rollback / (PREFIX + name)).exists(), 'Pinned GC rollback type')
        target.write_bytes((rollback / (PREFIX + name)).read_bytes())
    policy = root / (PREFIX + 'StationDolphinBufferPolicy.smali')
    need(policy.exists(), 'Eight-frame policy must be present before restoration')
    policy.unlink()

    # Recompile only the pure presentation family and one new, actually called
    # GBA policy. No fixture or old Java session replaces the productive DEX.
    for p in list((root / PREFIX).glob('StationGamePlayerInfo*.smali')):
        p.unlink()
    added = projection(overlay)
    need(added and all(n.startswith(PREFIX + 'StationGamePlayerInfo')
                      or n == PREFIX + 'StationGbaLinkPolicy.smali' for n in added), 'Scoped overlay only')
    for name in added:
        (root / name).write_bytes((overlay / name).read_bytes())

    profile = root / (PREFIX + 'StationMultiplayerProfile.smali')
    raw = profile.read_text()
    anchor = '    packed-switch v3, :pswitch_data_0\n\n    .line 39\n'
    need(raw.count(anchor) == 1, 'Exact unknown-controller branch')
    insertion = ('    iget-object v0, p0, L' + PREFIX + 'StationMultiplayerProfile;->platform:Ljava/lang/String;\n\n'
                 '    iget-object v1, p0, L' + PREFIX + 'StationMultiplayerProfile;->controllerProfile:Ljava/lang/String;\n\n'
                 '    iget v3, p0, L' + PREFIX + 'StationMultiplayerProfile;->maximumPlayers:I\n\n'
                 '    invoke-static {v0, v1, v3, p2}, ' + GBA +
                 '->devices(Ljava/lang/String;Ljava/lang/String;ILorg/json/JSONObject;)[I\n\n'
                 '    move-result-object p2\n\n'
                 '    if-nez p2, :goto_5\n\n')
    profile.write_text(raw.replace(anchor, anchor.replace('    .line 39\n', insertion + '    .line 39\n')))

    platform = root / (PREFIX + 'StationOnlinePlatformPolicy.smali')
    raw = platform.read_text()
    pattern = r'(?ms)(^\.method static maximum\(Ljava/lang/String;\)I\n    \.locals [1-9][0-9]*\n)'
    matches = list(re.finditer(pattern, raw))
    need(len(matches) == 1, 'Exact platform ceiling method')
    insertion = ('\n    const-string v0, "gba"\n\n'
                 '    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z\n\n'
                 '    move-result v0\n\n'
                 '    if-eqz v0, :gba_existing_platforms\n\n'
                 '    const/4 v0, 0x5\n\n'
                 '    return v0\n\n'
                 '    :gba_existing_platforms\n')
    index = matches[0].end()
    platform.write_text(raw[:index] + insertion + raw[index:])

    launch = root / (PREFIX + 'StationRetroLaunch.smali')
    raw = launch.read_text()
    anchor = ('    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n\n'
              '    move-result-object v2\n\n'
              '    invoke-static {v5, v2}, L' + PREFIX + 'StationRetroLaunch;->write(Ljava/io/File;Ljava/lang/String;)V')
    need(raw.count(anchor) == 1 and '    .locals 57\n' in raw, 'Pinned final config write and register lifetimes')
    # v5 is the newly constructed private config file. v6 is its just-consumed
    # name; v9 is replaced by the original elapsedRealtime wide value below.
    insertion = ('    iget-object v6, v1, L' + PREFIX + 'StationOnlineGame;->platform:Ljava/lang/String;\n\n'
                 '    iget-object v9, v1, L' + PREFIX + 'StationOnlineGame;->contentSha256:Ljava/lang/String;\n\n'
                 '    invoke-static {v5, v6, v9, v2}, ' + GBA +
                 '->configure(Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;\n\n'
                 '    move-result-object v2\n\n')
    launch.write_text(raw.replace(anchor, anchor.replace('    invoke-static {v5, v2}', insertion + '    invoke-static {v5, v2}')))
    final = projection(root)
    before = {n for n in original if final.get(n) != original[n]}
    after = {n for n in final if original.get(n) != final[n]}
    need(not any('StationDolphinBufferPolicy;' in p.read_text() for p in root.rglob('*.smali')),
         'No stale buffer policy or call remains')
    need((root / (PREFIX + RESTORE[0])).read_bytes() == (rollback / (PREFIX + RESTORE[0])).read_bytes(),
         'Session instructions must match the exact pre-trial reference')
    return before, after
