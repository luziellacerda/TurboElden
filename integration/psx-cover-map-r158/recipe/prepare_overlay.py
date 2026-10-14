"""Map the shared PSX red frame inside the existing selected-cover light pass.

The R151 source is regenerated from its pinned donor before this patch. Only
the PSX branch of the existing magazine shader changes; the supplied images
are references and are never bundled with the application.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE_SHA = "969e422a57e544da7b12ee3855ab9be67169e876357ebe74bddbaa4b3f48da99"
FIELD_SHA = "f223caed4bad8af65b9d3db993b4f56f688045c86cd8e2d18c870b9f415a9f72"


def patch(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != BASE_SHA:
        raise ValueError("Exact R151 magazine shader required")
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    changes: list[tuple[bytes, bytes]] = []

    def replace(old: str, new: str) -> None:
        nonlocal source
        before = old.encode().replace(b"\n", newline)
        after = new.encode().replace(b"\n", newline)
        if source.count(before) != 1:
            raise ValueError("PSX source anchor missing or ambiguous: " + old[:72])
        source = source.replace(before, after, 1)
        changes.append((before, after))

    replace(
        "if(model>7.5)return smoothstep(.55,.90,min(c.r,min(c.g,c.b)))*(1.0-smoothstep(.20,.45,max(c.r,max(c.g,c.b))-min(c.r,min(c.g,c.b))));\n if(model>6.5)return vcBlue(vec3(min(c.g,c.b),c.r,c.r));",
        "if(model>6.5)return vcBlue(vec3(min(c.g,c.b),c.r,c.r));",
    )
    replace(
        "if(model>7.5)return vcBilateral(model,52.,970.,555.,820.,985.);\n if(model>6.5)return vcBilateral(model,34.,989.,350.,510.,675.);",
        "if(model>6.5)return vcBilateral(model,34.,989.,350.,510.,675.);",
    )
    replace(
        " }else if(measuredMode){signature=vcMeasured(activeModel);enabled=signature;}\n}",
        """  }else if(activeModel>7.5){
   // Every PSX premium cover carries the same red frame. The emitter still
   // requires the actual red or white pixel inside the measured frame map.
   signature=1.0;enabled=1.0;
  }else if(measuredMode){signature=vcMeasured(activeModel);enabled=signature;}
}""",
    )
    replace(
        """float psxRegion(vec2 p){
 float m=max(segmentMask(p,vec2(60,104),vec2(115,49),7.0),segmentMask(p,vec2(115,49),vec2(143,49),7.0));
 m=max(m,segmentMask(p,vec2(963,104),vec2(907,49),7.0));m=max(m,segmentMask(p,vec2(907,49),vec2(879,49),7.0));
 m=max(m,box(p,vec2(36,231),vec2(65,343)));m=max(m,box(p,vec2(954,231),vec2(986,343)));
 m=max(m,box(p,vec2(42,531),vec2(61,1058)));m=max(m,box(p,vec2(962,531),vec2(981,1058)));
 m=max(m,box(p,vec2(35,1191),vec2(67,1297)));return max(m,box(p,vec2(956,1191),vec2(987,1297)));
}""",
        """float psxRegion(vec2 p){
 // Exact outer frame and header paths; never sample the CD case interior.
 float m=max(box(p,vec2(8,345),vec2(39,1070)),box(p,vec2(984,345),vec2(1020,1070)));
 m=max(m,box(p,vec2(99,136),vec2(181,168)));
 m=max(m,box(p,vec2(598,136),vec2(683,168)));
 m=max(m,box(p,vec2(828,12),vec2(890,107)));
 m=max(m,box(p,vec2(741,104),vec2(953,173)));
 m=max(m,segmentMask(p,vec2(47,58),vec2(102,66),8.0));
 m=max(m,segmentMask(p,vec2(685,66),vec2(790,0),9.0));
 m=max(m,segmentMask(p,vec2(47,184),vec2(212,189),7.0));
 m=max(m,segmentMask(p,vec2(684,176),vec2(787,182),9.0));
 m=max(m,segmentMask(p,vec2(787,182),vec2(978,228),14.0));
 m=max(m,segmentMask(p,vec2(48,1007),vec2(133,1060),12.0));
 m=max(m,segmentMask(p,vec2(683,1040),vec2(977,1158),15.0));
 return max(m,box(p,vec2(138,1392),vec2(879,1499)));
}""",
    )
    replace(
        "if(activeMagazineModel>7.5)return smoothstep(.55,.90,min(c.r,min(c.g,c.b)))*(1.0-smoothstep(.20,.45,max(c.r,max(c.g,c.b))-min(c.r,min(c.g,c.b))));",
        "if(activeMagazineModel>7.5)return max(psxRed(c),smoothstep(.52,.88,min(c.r,min(c.g,c.b))));",
    )
    replace(
        "float newFrameLamp(vec3 c){",
        """float psxRed(vec3 c){
 return smoothstep(.10,.40,c.r-max(c.g,c.b))*smoothstep(.18,.58,c.r);
}
float newFrameLamp(vec3 c){""",
    )
    replace(
        "vec3 snesMappedColor(vec3 c) {",
        "vec3 snesMappedColor(vec3 c) {\n    if(activeMagazineModel>7.5)return vec3(c.r);",
    )
    replace(
        """bool psxSupport(vec2 p) {
    return supportBox(p,vec2(45,34),vec2(158,119))
        || supportBox(p,vec2(864,34),vec2(978,119))
        || supportBox(p,vec2(30,226),vec2(72,1302))
        || supportBox(p,vec2(949,226),vec2(992,1302));
}""",
        """bool psxSupport(vec2 p) {
    return supportBox(p,vec2(3,340),vec2(44,1075))
        || supportBox(p,vec2(979,340),vec2(1023,1075))
        || supportBox(p,vec2(35,0),vec2(990,250))
        || supportBox(p,vec2(33,992),vec2(145,1075))
        || supportBox(p,vec2(668,1025),vec2(992,1178))
        || supportBox(p,vec2(133,1387),vec2(884,1504));
}""",
    )
    replace(
        "if(activeMagazineModel>7.5)return bilateralSignature(52.,970.,555.,820.,985.);\n if(activeMagazineModel>6.5)return bilateralSignature(34.,989.,350.,510.,675.);",
        "if(activeMagazineModel>6.5)return bilateralSignature(34.,989.,350.,510.,675.);",
    )
    replace(
        "    else if(measuredMode) enabled=measuredFrameSignature();",
        """    else if(activeMagazineModel>7.5) enabled=1.0;
    else if(measuredMode) enabled=measuredFrameSignature();""",
    )
    replace(
        "if(activeMagazineModel>7.5) hue=vec3(1.0);",
        "if(activeMagazineModel>7.5) hue=vec3(1.0,.025,.012);",
    )
    replace(
        "float head=fract(t*0.0048);",
        "float head=fract(t*(activeMagazineModel>7.5?0.008:0.0048));",
    )
    recovered = source
    for before, after in reversed(changes):
        if recovered.count(after) != 1:
            raise ValueError("PSX patch inverse is ambiguous")
        recovered = recovered.replace(after, before, 1)
    if hashlib.sha256(recovered).hexdigest() != BASE_SHA:
        raise ValueError("PSX patch did not invert to exact R151 source")
    if source.count(b"float psxRegion(") != 1 or source.count(b"psxRed(") != 2 or b"8.25" in source:
        raise ValueError("Unified PSX classifier, geometry or emitter is unlinked")
    return source


def prepare(source: Path, output: Path) -> str:
    if output.exists():
        raise FileExistsError(output)
    result = patch(source.read_bytes())
    output.mkdir(parents=True)
    (output / "magazine_shader.h").write_bytes(result)
    return hashlib.sha256(result).hexdigest()


def patch_field(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != FIELD_SHA:
        raise ValueError("Exact R151 static-field source required")
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    changes = (
        (b"// SNES has narrow support. Bake its entire field once so each cover" + newline,
         b"// SNES and PSX bake their selected-cover field once, when it changes." + newline),
        (b"// appears complete immediately, using fewer calls than row parcels." + newline,
         b"// Both keep the same cached field and animation draw." + newline),
        (b"B instantSnes=modelKey==9;g.Uniform1f(c.bakeRegionOnly,instantSnes?0.f:1.f);",
         b"B instantSnesOrPsx=modelKey==9||modelKey==8;g.Uniform1f(c.bakeRegionOnly,instantSnesOrPsx?0.f:1.f);"),
        (b"c.pendingRow=instantSnes?height:0;",
         b"c.pendingRow=instantSnesOrPsx?height:0;"),
    )
    original = source
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("PSX static-field anchor missing or ambiguous")
        source = source.replace(before, after, 1)
    patched = source
    for before, after in reversed(changes):
        if source.count(after) != 1:
            raise ValueError("PSX static-field inverse is ambiguous")
        source = source.replace(after, before, 1)
    if source != original:
        raise ValueError("PSX static-field patch did not invert")
    return patched
