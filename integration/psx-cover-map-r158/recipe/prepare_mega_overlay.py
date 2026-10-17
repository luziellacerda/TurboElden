"""Add the new Mega Drive artwork map to the completed PSX-only shader."""

from __future__ import annotations

import hashlib


PSX_SHA = "f19d0660b66b12ee76fb5b0aa379ee4d0919a4c5f07d2be7ba5ddfe27788f3d1"
FIELD_SHA = "8655278a6924323427b1ebe178d422d1194091267a9d6e0bf23a475a851fb72b"


def patch(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != PSX_SHA:
        raise ValueError("Exact completed PSX shader required")
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    changes: list[tuple[bytes, bytes]] = []

    def replace(old: str, new: str) -> None:
        nonlocal source
        before = old.encode().replace(b"\n", newline)
        after = new.encode().replace(b"\n", newline)
        if source.count(before) != 1:
            raise ValueError("Mega Drive source anchor missing or ambiguous: " + old[:72])
        source = source.replace(before, after, 1)
        changes.append((before, after))

    replace(
        " }else if(magazineModel<1.5){\n  signature=vcBlue(vcSample(vec2(220,12)).rgb)+vcBlue(vcSample(vec2(800,12)).rgb)",
        """ }else if(magazineModel<1.5){
   // Blue edge LEDs and two blue letters identify the Sonic Mega Drive art.
   // The title is then part of the same existing light field as the rails.
   float newRails=vcBlue(vcSample(vec2(30,350)).rgb)+vcBlue(vcSample(vec2(997,350)).rgb)
       +vcBlue(vcSample(vec2(30,900)).rgb)+vcBlue(vcSample(vec2(997,900)).rgb);
   float title=vcBlue(vcSample(vec2(200,115)).rgb)+vcBlue(vcSample(vec2(450,105)).rgb);
   if(newRails>2.7&&title>1.5){activeModel=1.25;signature=1.0;enabled=1.0;}
   else{
    signature=vcBlue(vcSample(vec2(220,12)).rgb)+vcBlue(vcSample(vec2(800,12)).rgb)""",
    )
    replace(
        "  enabled=smoothstep(2.0,3.2,signature)*darkHeader;\n }else if(magazineModel<2.5){",
        "  enabled=smoothstep(2.0,3.2,signature)*darkHeader;\n  }\n }else if(magazineModel<2.5){",
    )
    replace(
        "float megaRegion(vec2 p) {",
        """float megaNewRegion(vec2 p){
 // Neon blue frame, TURBORAMA, the SEGA name, and footer controls.
 // The blue emitter gates each letter pixel: this is not a solid title box.
 float m=max(box(p,vec2(15,193),vec2(44,1223)),box(p,vec2(983,193),vec2(1012,1223)));
 m=max(m,box(p,vec2(57,22),vec2(704,37)));
 m=max(m,box(p,vec2(101,72),vec2(674,126)));
 m=max(m,box(p,vec2(777,40),vec2(908,89)));
 m=max(m,box(p,vec2(164,1403),vec2(256,1494)));
 return max(m,box(p,vec2(522,1403),vec2(616,1494)));
}
float megaRegion(vec2 p) {""",
    )
    replace(
        "return (activeMagazineModel>4.5&&activeMagazineModel<5.5)||activeMagazineModel>6.5;",
        "return (activeMagazineModel>4.5&&activeMagazineModel<5.5)||activeMagazineModel>6.5||(activeMagazineModel>1.125&&activeMagazineModel<1.5);",
    )
    replace(
        "if(activeMagazineModel>7.5)return vec3(c.r);",
        "if(activeMagazineModel>7.5)return vec3(c.r);\n    if(activeMagazineModel>1.125&&activeMagazineModel<1.5)return vec3(c.b);",
    )
    replace(
        "    if(activeMagazineModel>0.5) return megaRegion(p);",
        "    if(activeMagazineModel>1.125&&activeMagazineModel<1.5) return megaNewRegion(p);\n    if(activeMagazineModel>0.5) return megaRegion(p);",
    )
    replace(
        "bool megaSupport(vec2 p) {\n    return supportBox(p,vec2(154,-8),vec2(294,213))",
        """bool megaSupport(vec2 p) {
    if(supportBox(p,vec2(9,187),vec2(50,1229))||
       supportBox(p,vec2(977,187),vec2(1018,1229))||
       supportBox(p,vec2(51,16),vec2(710,43))||
       supportBox(p,vec2(95,66),vec2(680,132))||
       supportBox(p,vec2(158,1397),vec2(262,1500))||
       supportBox(p,vec2(516,1397),vec2(622,1500)))return true;
    return supportBox(p,vec2(154,-8),vec2(294,213))""",
    )
    replace(
        "    } else if(magazineModel<1.5) {\n        signature=blue(sampleArt(vec2(220,12)).rgb)+blue(sampleArt(vec2(800,12)).rgb)",
        """    } else if(magazineModel<1.5) {
        float newRails=blue(sampleArt(vec2(30,350)).rgb)+blue(sampleArt(vec2(997,350)).rgb)
                       +blue(sampleArt(vec2(30,900)).rgb)+blue(sampleArt(vec2(997,900)).rgb);
        float title=blue(sampleArt(vec2(200,115)).rgb)+blue(sampleArt(vec2(450,105)).rgb);
        if(newRails>2.7&&title>1.5){activeMagazineModel=1.25;enabled=1.0;}
        else{
        signature=blue(sampleArt(vec2(220,12)).rgb)+blue(sampleArt(vec2(800,12)).rgb)""",
    )
    replace(
        "float head=fract(t*(activeMagazineModel>7.5?0.008:0.0048));",
        "float head=fract(t*(activeMagazineModel>7.5?0.008:activeMagazineModel>1.125&&activeMagazineModel<1.5?0.0064:0.0048));",
    )
    replace(
        "    float gain=clamp(ledGain,1.0,2.5);",
        "    float gain=clamp(ledGain,1.0,2.5);\n    if(activeMagazineModel>1.125&&activeMagazineModel<1.5)gain*=0.82+0.88*flow.x;",
    )
    replace(
        "        enabled=smoothstep(2.0,3.2,signature)*darkHeader;\n    } else if(magazineModel<2.5) {",
        "        enabled=smoothstep(2.0,3.2,signature)*darkHeader;\n        }\n    } else if(magazineModel<2.5) {",
    )
    recovered = source
    for before, after in reversed(changes):
        if recovered.count(after) != 1:
            raise ValueError("Mega Drive patch inverse is ambiguous")
        recovered = recovered.replace(after, before, 1)
    if hashlib.sha256(recovered).hexdigest() != PSX_SHA:
        raise ValueError("Mega Drive patch did not invert to PSX-only source")
    if source.count(b"megaNewRegion(") != 2 or source.count(b"activeModel=1.25") != 1 or source.count(b"activeMagazineModel=1.25") != 1:
        raise ValueError("Mega Drive title/LED profile is unlinked")
    return source


def patch_field(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != FIELD_SHA:
        raise ValueError("Exact PSX-completed static-field source required")
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    changes = (
        (b"// SNES and PSX bake their selected-cover field once, when it changes." + newline,
         b"// SNES, PSX and Mega Drive bake their field once on cover change." + newline),
        (b"B instantSnesOrPsx=modelKey==9||modelKey==8;g.Uniform1f(c.bakeRegionOnly,instantSnesOrPsx?0.f:1.f);",
         b"B instantSnesOrPsxOrMega=modelKey==9||modelKey==8||modelKey==1;g.Uniform1f(c.bakeRegionOnly,instantSnesOrPsxOrMega?0.f:1.f);"),
        (b"c.pendingRow=instantSnesOrPsx?height:0;",
         b"c.pendingRow=instantSnesOrPsxOrMega?height:0;"),
    )
    original = source
    for before, after in changes:
        if source.count(before) != 1:
            raise ValueError("Mega Drive static-field anchor missing or ambiguous")
        source = source.replace(before, after, 1)
    patched = source
    for before, after in reversed(changes):
        if source.count(after) != 1:
            raise ValueError("Mega Drive static-field inverse is ambiguous")
        source = source.replace(after, before, 1)
    if source != original:
        raise ValueError("Mega Drive static-field patch did not invert")
    return patched
