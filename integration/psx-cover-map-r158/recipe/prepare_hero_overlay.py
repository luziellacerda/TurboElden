"""Give every selected game cover the existing SNES 1.8% corner strip.

The native system carousel, animation, texture, and draw count stay unchanged.
"""

from __future__ import annotations

import hashlib


BASE_SHA = "f37992fd3dced2f2eee0eb014a526be417d02264825ffc0677e26dc06351453f"


def patch(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != BASE_SHA:
        raise ValueError("Exact R158 selected-cover geometry required")
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    changes: list[tuple[bytes, bytes]] = []

    def replace(before: str, after: str) -> None:
        nonlocal source
        old = before.encode().replace(b"\n", newline)
        new = after.encode().replace(b"\n", newline)
        if source.count(old) != 1:
            raise ValueError("Selected-cover corner anchor missing or ambiguous: " + before[:64])
        source = source.replace(old, new, 1)
        changes.append((old, new))

    replace("bool snesHero=false;", "bool roundedHero=false;")
    replace("static bool mappingSnesHero;", "static bool mappingRoundedHero;")
    replace(
        ' r.snesHero=mappingHero&&mappingPlatform&&(presentationKeyEqual(mappingPlatform,"Super Nintendo")||\n'
        '  presentationKeyEqual(mappingPlatform,"Super Nintendo - BR")||presentationKeyEqual(mappingPlatform,"snes")||\n'
        '  presentationKeyEqual(mappingPlatform,"snesbr")||presentationKeyEqual(mappingPlatform,"super-nintendo")||\n'
        '  presentationKeyEqual(mappingPlatform,"super-nintendo--br"));',
        " r.roundedHero=mappingHero;",
    )
    replace("mappingSnesHero=r.snesHero;", "mappingRoundedHero=r.roundedHero;")
    replace("mappingSnesHero=false;", "mappingRoundedHero=false;")
    replace("static float snesHeroRadius(", "static float heroRadius(")
    replace("static unsigned snesHeroRoundedStrip(", "static unsigned heroRoundedStrip(")
    replace("float radius=snesHeroRadius(width,height);", "float radius=heroRadius(width,height);")
    replace("if(mappingSnesHero){", "if(mappingRoundedHero){")
    replace("snesHeroRoundedStrip(vertices,rounded)", "heroRoundedStrip(vertices,rounded)")
    replace("r.snesHero?snesHeroRadius(r.w,r.h)", "r.roundedHero?heroRadius(r.w,r.h)")
    recovered = source
    for old, new in reversed(changes):
        if recovered.count(new) != 1:
            raise ValueError("Selected-cover corner patch inverse is ambiguous")
        recovered = recovered.replace(new, old, 1)
    if hashlib.sha256(recovered).hexdigest() != BASE_SHA:
        raise ValueError("Selected-cover corner patch did not invert")
    if source.count(b"mappingRoundedHero") != 4 or source.count(b"heroRoundedStrip(") != 2:
        raise ValueError("Selected-cover drawing path is not linked")
    return source
