"""Map the new N64 magazine art onto the existing selected-cover light pass.

The supplied 1080 Snowboarding cover is 1024x1536 RGB, SHA-256
2f8ee5b6d4c91979a7e75658def15f3daabc04b299aa44145f2c9a5efb3fdcc1.
It is also F:/CAPAS N64/001 - 1080° Snowboarding.png. The server's N64 USB
publication listed 1080 source SHA-256 b555c0f6... and served JPEG ec46d4a1...;
both differ from this image. Publishing this exact new art is a separate step.

This recipe edits only a COPY of the active R158 native overlay. The N64 2.0
profile remains for the older artwork; 2.25 is selected by four actual LED
pixels on the new frame. Both profiles use the same shader, field cache, GL
draw, and frame clock. No timer, thread, texture, or per-frame draw is added.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE_OVERLAY = Path(
    r"E:\StationVisualR158UnifiedPsxFinal-20261014\combined-native-v8\overlay"
)
SOURCE_SHA = {
    "magazine_shader.h": "b8821da12ca401b1288685a91a80bc9e91eb069b461b3be28a3cfdcc3a5870ae",
    "native_magazine_field.h": "00fb3ab72b245e705874820e0b89c3ca1ec79abef8e6ca6c51789b1038a512af",
}
REFERENCE_IMAGE_SHA = "2f8ee5b6d4c91979a7e75658def15f3daabc04b299aa44145f2c9a5efb3fdcc1"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(source: bytes, old: str, new: str, changes: list[tuple[bytes, bytes]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    before, after = (part.encode("utf-8").replace(b"\n", newline) for part in (old, new))
    if source.count(before) != 1:
        raise ValueError("N64 source anchor missing or ambiguous: " + old[:96])
    changes.append((before, after))
    return source.replace(before, after, 1)


def patch_shader(source: bytes) -> bytes:
    if digest(source) != SOURCE_SHA["magazine_shader.h"]:
        raise ValueError("Exact active R158 carousel shader required")
    changes: list[tuple[bytes, bytes]] = []

    def change(old: str, new: str) -> None:
        nonlocal source
        source = replace_once(source, old, new, changes)

    change(
        """ }else if(magazineModel<2.5){
  signature=vcN64Lamp(vcSample(vec2(240,14)).rgb)+vcN64Lamp(vcSample(vec2(790,14)).rgb)
      +vcN64Lamp(vcSample(vec2(44,235)).rgb)+vcN64Lamp(vcSample(vec2(980,235)).rgb)
      +vcN64Lamp(vcSample(vec2(975,1454)).rgb);
  float darkHeader=1.0-smoothstep(0.08,0.25,vcLuminance(vcSample(vec2(512,175)).rgb));
  enabled=smoothstep(2.8,4.2,signature)*darkHeader;
 }""",
        """ }else if(magazineModel<2.5){
  // The new 1024x1536 chassis has green left and blue right LEDs. The old
  // probes land on dark metal/sky in that artwork and disable its light.
  float newRails=vcN64Lamp(vcSample(vec2(26,350)).rgb)+vcN64Lamp(vcSample(vec2(997,350)).rgb)
      +vcN64Lamp(vcSample(vec2(26,900)).rgb)+vcN64Lamp(vcSample(vec2(997,900)).rgb);
  if(newRails>3.1){activeModel=2.25;signature=1.0;enabled=1.0;}
  else{
   signature=vcN64Lamp(vcSample(vec2(240,14)).rgb)+vcN64Lamp(vcSample(vec2(790,14)).rgb)
       +vcN64Lamp(vcSample(vec2(44,235)).rgb)+vcN64Lamp(vcSample(vec2(980,235)).rgb)
       +vcN64Lamp(vcSample(vec2(975,1454)).rgb);
   float darkHeader=1.0-smoothstep(0.08,0.25,vcLuminance(vcSample(vec2(512,175)).rgb));
   enabled=smoothstep(2.8,4.2,signature)*darkHeader;
  }
 }""",
    )
    change(
        "float n64Region(vec2 p) {",
        """float n64NewRegion(vec2 p) {
    // Exact new chassis only. The snowboarder, blue sky and cartridge art
    // remain outside the light mask. The existing chroma emitter selects
    // actual lit pixels within each band, including individual logo pixels.
    float m=max(box(p,vec2(16,153),vec2(57,1124)),box(p,vec2(967,153),vec2(1008,1124)));
    m=max(m,box(p,vec2(422,0),vec2(648,20))); // upper blue crown
    m=max(m,box(p,vec2(84,123),vec2(163,137))); // red TURBORAMA underlines
    m=max(m,box(p,vec2(528,123),vec2(591,137)));
    m=max(m,box(p,vec2(788,60),vec2(837,107))); // red 64
    m=max(m,box(p,vec2(846,43),vec2(948,147))); // colored N logo
    m=max(m,box(p,vec2(65,1375),vec2(469,1504))); // green footer
    return max(m,box(p,vec2(543,1375),vec2(955,1504))); // blue footer
}
float n64Region(vec2 p) {""",
    )
    change(
        "    if(activeMagazineModel>1.5) return n64Region(p);",
        "    if(activeMagazineModel>2.125&&activeMagazineModel<2.5) return n64NewRegion(p);\n    if(activeMagazineModel>1.5) return n64Region(p);",
    )
    change(
        """bool n64Support(vec2 p) {
    return supportBox(p,vec2(150,-10),vec2(325,213))""",
        """bool n64Support(vec2 p) {
    // Conservative bounds include both frame designs before texture-based
    // classification; neither one samples the game image interior.
    if(supportBox(p,vec2(10,147),vec2(63,1130))||
       supportBox(p,vec2(961,147),vec2(1014,1130))||
       supportBox(p,vec2(416,-6),vec2(654,26))||
       supportBox(p,vec2(78,117),vec2(169,143))||
       supportBox(p,vec2(522,117),vec2(597,143))||
       supportBox(p,vec2(782,37),vec2(954,153))||
       supportBox(p,vec2(59,1369),vec2(475,1510))||
       supportBox(p,vec2(537,1369),vec2(961,1510)))return true;
    return supportBox(p,vec2(150,-10),vec2(325,213))""",
    )
    change(
        "return (activeMagazineModel>4.5&&activeMagazineModel<5.5)||activeMagazineModel>6.5||(activeMagazineModel>1.125&&activeMagazineModel<1.5);",
        "return (activeMagazineModel>4.5&&activeMagazineModel<5.5)||activeMagazineModel>6.5||(activeMagazineModel>2.125&&activeMagazineModel<2.5)||(activeMagazineModel>1.125&&activeMagazineModel<1.5);",
    )
    change(
        "    if(activeMagazineModel>7.5)return vec3(c.r);",
        "    if(activeMagazineModel>7.5)return vec3(c.r);\n    if(activeMagazineModel>2.125&&activeMagazineModel<2.5)return vec3(max(c.r,max(c.g,c.b)));",
    )
    change(
        """    } else if(magazineModel<2.5) {
        signature=n64Lamp(sampleArt(vec2(240,14)).rgb)+n64Lamp(sampleArt(vec2(790,14)).rgb)
                 +n64Lamp(sampleArt(vec2(44,235)).rgb)+n64Lamp(sampleArt(vec2(980,235)).rgb)
                 +n64Lamp(sampleArt(vec2(975,1454)).rgb);
        darkHeader=1.0-smoothstep(0.08,0.25,dot(sampleArt(vec2(512,175)).rgb,vec3(0.299,0.587,0.114)));
        enabled=smoothstep(2.8,4.2,signature)*darkHeader;
    }""",
        """    } else if(magazineModel<2.5) {
        float newRails=n64Lamp(sampleArt(vec2(26,350)).rgb)+n64Lamp(sampleArt(vec2(997,350)).rgb)
                      +n64Lamp(sampleArt(vec2(26,900)).rgb)+n64Lamp(sampleArt(vec2(997,900)).rgb);
        if(newRails>3.1){activeMagazineModel=2.25;signature=1.0;enabled=1.0;}
        else{
         signature=n64Lamp(sampleArt(vec2(240,14)).rgb)+n64Lamp(sampleArt(vec2(790,14)).rgb)
                  +n64Lamp(sampleArt(vec2(44,235)).rgb)+n64Lamp(sampleArt(vec2(980,235)).rgb)
                  +n64Lamp(sampleArt(vec2(975,1454)).rgb);
         darkHeader=1.0-smoothstep(0.08,0.25,dot(sampleArt(vec2(512,175)).rgb,vec3(0.299,0.587,0.114)));
         enabled=smoothstep(2.8,4.2,signature)*darkHeader;
        }
    }""",
    )
    change(
        "    float n64Mode=step(1.5,activeMagazineModel)*(1.0-step(2.5,activeMagazineModel));",
        "    float n64Mode=step(1.5,activeMagazineModel)*(1.0-step(2.125,activeMagazineModel));",
    )
    change(
        "    else if(activeMagazineModel>1.5) hue=n64LampHue(p);",
        "    else if(activeMagazineModel>2.125&&activeMagazineModel<2.5) hue=base.rgb/max(max(base.r,max(base.g,base.b)),.001);\n    else if(activeMagazineModel>1.5) hue=n64LampHue(p);",
    )

    recovered = source
    for before, after in reversed(changes):
        if recovered.count(after) != 1:
            raise ValueError("N64 patch inverse is ambiguous")
        recovered = recovered.replace(after, before, 1)
    if digest(recovered) != SOURCE_SHA["magazine_shader.h"]:
        raise ValueError("N64 shader patch does not invert to R158")
    if source.count(b"n64NewRegion(") != 2 or source.count(b"activeModel=2.25") != 1 or source.count(b"activeMagazineModel=2.25") != 1:
        raise ValueError("N64 new profile is unlinked")
    return source


def patch_field(source: bytes) -> bytes:
    if digest(source) != SOURCE_SHA["native_magazine_field.h"]:
        raise ValueError("Exact active R158 field cache required")
    changes: list[tuple[bytes, bytes]] = []

    def change(old: str, new: str) -> None:
        nonlocal source
        source = replace_once(source, old, new, changes)

    change(
        "// SNES, PSX and Mega Drive bake their field once on cover change.\n  // Both keep the same cached field and animation draw.",
        "// SNES, PSX, Mega Drive and N64 bake once on cover change.\n  // The cached field and single animation draw remain unchanged.",
    )
    change(
        "B instantSnesOrPsxOrMega=modelKey==9||modelKey==8||modelKey==1;g.Uniform1f(c.bakeRegionOnly,instantSnesOrPsxOrMega?0.f:1.f);",
        "B instantMappedCover=modelKey==9||modelKey==8||modelKey==1||modelKey==2;g.Uniform1f(c.bakeRegionOnly,instantMappedCover?0.f:1.f);",
    )
    change(
        "c.pendingRow=instantSnesOrPsxOrMega?height:0;",
        "c.pendingRow=instantMappedCover?height:0;",
    )

    recovered = source
    for before, after in reversed(changes):
        if recovered.count(after) != 1:
            raise ValueError("N64 field patch inverse is ambiguous")
        recovered = recovered.replace(after, before, 1)
    if digest(recovered) != SOURCE_SHA["native_magazine_field.h"]:
        raise ValueError("N64 field patch does not invert to R158")
    return source


def patch(overlay_dir: Path) -> dict:
    """Patch two files inside an already copied overlay and return their hashes."""
    overlay_dir = overlay_dir.resolve(strict=True)
    if overlay_dir == SOURCE_OVERLAY.resolve(strict=True):
        raise ValueError("Refusing to edit the pinned R158 source overlay")
    originals: dict[str, bytes] = {}
    for name, expected in SOURCE_SHA.items():
        path = overlay_dir / name
        if not path.is_file() or path.is_symlink() or path.resolve().parent != overlay_dir:
            raise ValueError("Overlay file missing or escaped: " + name)
        raw = path.read_bytes()
        if digest(raw) != expected:
            raise ValueError("Copied overlay differs from the pinned R158 source: " + name)
        originals[name] = raw
    results = {
        "magazine_shader.h": patch_shader(originals["magazine_shader.h"]),
        "native_magazine_field.h": patch_field(originals["native_magazine_field.h"]),
    }
    for name, raw in results.items():
        (overlay_dir / name).write_bytes(raw)
    return {
        "referenceImageSha256": REFERENCE_IMAGE_SHA,
        "referenceDimensions": [1024, 1536],
        "changedFiles": [
            {"path": name, "beforeSha256": SOURCE_SHA[name], "afterSha256": digest(raw)}
            for name, raw in results.items()
        ],
        "newThreadsTimersPerFrameDraws": 0,
        "oldN64ArtworkProfilePreserved": True,
    }
