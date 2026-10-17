"""Surgical g52 cover fallback over the exact R135 StationOnlineCoverView DEX."""
from pathlib import Path
import hashlib
import shutil
import sys

source, destination = map(Path, sys.argv[1:3])
assert not destination.exists()
shutil.copytree(source, destination)
target = destination / "org/emulationstation/frontend/netplay/StationOnlineCoverView.smali"
raw = target.read_text(encoding="utf-8")
anchor = """    .line 67
    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/netplay/StationOnlineCoverView;->setImportantForAccessibility(I)V

    return-void
.end method"""
replacement = """    .line 67
    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/netplay/StationOnlineCoverView;->setImportantForAccessibility(I)V

    # Moto g52 Adreno stalls in cover GLES glLinkProgram and blocks HWUI.
    # Keep the original ImageView bitmap; suppress only this optional GLES surface.
    const-string v0, "motorola"
    sget-object v1, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;
    invoke-virtual {v0, v1}, Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z
    move-result v2
    if-eqz v2, :cover_ready
    const-string v0, "moto g52"
    sget-object v1, Landroid/os/Build;->MODEL:Ljava/lang/String;
    invoke-virtual {v0, v1}, Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z
    move-result v2
    if-eqz v2, :cover_ready
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationOnlineCoverView;->texture:Landroid/view/TextureView;
    const/4 v1, 0x0
    invoke-virtual {v0, v1}, Landroid/view/TextureView;->setSurfaceTextureListener(Landroid/view/TextureView$SurfaceTextureListener;)V
    const/16 v1, 0x8
    invoke-virtual {v0, v1}, Landroid/view/TextureView;->setVisibility(I)V
    :cover_ready
    return-void
.end method"""
assert raw.count(anchor) == 1
updated = raw.replace(anchor, replacement)
assert updated.count('const-string v0, "moto g52"') == 1
target.write_text(updated, encoding="utf-8", newline="\n")
print("patchedClassSha256=" + hashlib.sha256(target.read_bytes()).hexdigest())
