"""Replace only the blocked free-space invocation in the exact R177 updater."""
from pathlib import Path


def patch(directory):
    relative = 'org/emulationstation/frontend/station/StationAppUpdater.smali'
    path = Path(directory) / relative
    before = path.read_text()
    old = '''    invoke-static {v15}, Ljava/nio/file/Files;->getFileStore(Ljava/nio/file/Path;)Ljava/nio/file/FileStore;

    move-result-object v12

    invoke-virtual {v12}, Ljava/nio/file/FileStore;->getUsableSpace()J'''
    new = '''    invoke-interface {v15}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v12

    invoke-virtual {v12}, Ljava/io/File;->getUsableSpace()J'''
    if before.count(old) != 1 or new in before:
        raise ValueError('Exactly one original storage call required; refuse replay')
    after = before.replace(old, new)
    if '->getFileStore(' in after or after.count(new) != 1:
        raise ValueError('Blocked Android call remains or duplicate replacement')
    path.write_text(after)
    return {relative}
