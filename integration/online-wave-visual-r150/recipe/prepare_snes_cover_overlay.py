"""Prepare the selected SNES game-cover geometry and LED map on the R149 native base.

Only four SHA-pinned headers are emitted. The source JPEG supplied by the
maintainer is measured but never copied into the repository or APK.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


INPUT_SHA256 = {
    "native_formation.h": "070cd1288c573f508aa25c227db504d7e4eb1eba12a369a18968f02dc63c012e",
    "native_magazine.h": "ec45ed0dda47ed50c7ce194c599028a99a0d829a7625f614e3dc25bff34ff90f",
    "native_magazine_field.h": "8d5704e63acddbeded45282d77caee3ba2677b108421a696b5a40e0e0c5297c0",
    "magazine_shader.h": "4e1aec8892155c966b7a5301ac3e9f6a2b31953152ac9ca01a1fb8d779cb7dda",
}
REFERENCE_ART_SHA256 = "fefec62a6a3a3933973a695764321050952130a263f7a71f02ed47a9276b9f09"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def patch_file(raw: bytes, filename: str) -> tuple[bytes, list[tuple[bytes, bytes]]]:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    patches: list[tuple[bytes, bytes]] = []

    def literal(value: str) -> bytes:
        return value.encode("utf-8").replace(b"\n", newline)

    def change(old: str, new: str) -> None:
        nonlocal raw
        before, after = literal(old), literal(new)
        if raw.count(before) != 1:
            raise ValueError(f"{filename}: expected one original block: {old[:60]!r}")
        raw = raw.replace(before, after, 1)
        patches.append((before, after))

    def section(start: str, end: str, replacement: str) -> None:
        nonlocal raw
        left, right = literal(start), literal(end)
        if raw.count(left) != 1:
            raise ValueError(f"{filename}: expected one section start {start!r}")
        begin = raw.index(left)
        stop = raw.index(right, begin + len(left))
        before, after = raw[begin:stop], literal(replacement)
        raw = raw[:begin] + after + raw[stop:]
        patches.append((before, after))

    if filename == "native_formation.h":
        change(
            "struct CoverRect {float x,y,w,h;int index;bool allGames=false;stationCarouselGeometry::Transform projection{};};",
            "struct CoverRect {float x,y,w,h;int index;bool allGames=false;stationCarouselGeometry::Transform projection{};bool snesHero=false;};",
        )
        change(
            "static bool mappingHero;static const char*mappingPlatform;",
            "static bool mappingHero;static bool mappingSnesHero;static const char*mappingPlatform;",
        )
        change(
            " if(pos>=0&&paintedCount<20&&r.x+r.w>0&&r.x<w){r.index=pos;painted[paintedCount++]=r;}\n mappingHero=!systemsMode&&pos==at<int>(p,0xf0);mappingPlatform=nullptr;",
            " mappingHero=!systemsMode&&pos==at<int>(p,0xf0);mappingPlatform=nullptr;",
        )
        change(
            "  if(begin&&index<(U)(endItems-begin)/0xe8)mappingPlatform=strData(begin+index*0xe8+0x60);\n }\n const auto*previousProjection=formationProjection;",
            "  if(begin&&index<(U)(endItems-begin)/0xe8)mappingPlatform=strData(begin+index*0xe8+0x60);\n"
            " }\n"
            " r.snesHero=mappingHero&&mappingPlatform&&(presentationKeyEqual(mappingPlatform,\"Super Nintendo\")||\n"
            "  presentationKeyEqual(mappingPlatform,\"Super Nintendo - BR\")||presentationKeyEqual(mappingPlatform,\"snes\")||\n"
            "  presentationKeyEqual(mappingPlatform,\"snesbr\")||presentationKeyEqual(mappingPlatform,\"super-nintendo\")||\n"
            "  presentationKeyEqual(mappingPlatform,\"super-nintendo--br\"));\n"
            " mappingSnesHero=r.snesHero;\n"
            " if(pos>=0&&paintedCount<20&&r.x+r.w>0&&r.x<w){r.index=pos;painted[paintedCount++]=r;}\n"
            " const auto*previousProjection=formationProjection;",
        )
        change(
            "mappingCover=false;mappingAllGames=false;mappingHero=false;mappingPlatform=nullptr;",
            "mappingCover=false;mappingAllGames=false;mappingHero=false;mappingSnesHero=false;mappingPlatform=nullptr;",
        )
        change(
            "static float cornerRadius(float w,float h,bool allGames=false){return stationCollectionCorners::radius(systemsMode,folderMode,w,h,allGames);}",
            "static float cornerRadius(float w,float h,bool allGames=false){return stationCollectionCorners::radius(systemsMode,folderMode,w,h,allGames);}\nstatic float snesHeroRadius(float w,float h){return (w<h?w:h)*.018f;}",
        )
        change(
            "static void roundedCoverQuad(const Vertex*q,int src,int dst,const CoverRect&r){",
            """// Sixteen vertices keep the existing single artwork draw and UV/color interpolation.
// The four fixed offsets approximate a circle for a small 1.8% corner radius;
// no square roots, bitmap masks, texture allocations or extra GL calls per frame.
static unsigned snesHeroRoundedStrip(const Vertex*q,Vertex out[16]){
 float width=q[2].x-q[0].x,height=q[1].y-q[0].y;if(width<=0||height<=0)return 0;
 float radius=snesHeroRadius(width,height);
 static const float rise[4]={0.f,.33333333f,.66666667f,1.f};
 static const float inset[4]={1.f,.25464401f,.05719096f,0.f};
 unsigned count=0;
 for(int half=0;half<2;half++)for(int i=0;i<4;i++){
  float yy=half?height-radius+radius*rise[i]:radius*rise[i];
  float xx=radius*inset[half?3-i:i];
  Vertex left=blendVertex(q[0],q[1],yy/height),right=blendVertex(q[2],q[3],yy/height);
  out[count++]=blendVertex(left,right,xx/width);
  out[count++]=blendVertex(left,right,1.f-xx/width);
 }
 return count;
}
static void roundedCoverQuad(const Vertex*q,int src,int dst,const CoverRect&r){""",
        )
        change(
            "   if(mappingHero&&drawMagazineCover(vertices,count,src,dst,mappingPlatform))return;\n   roundedQuad(vertices,src,dst,mappingAllGames);return;",
            """   if(mappingSnesHero){
    Vertex rounded[16];unsigned roundedCount=snesHeroRoundedStrip(vertices,rounded);
    if(roundedCount){
     if(drawMagazineCover(rounded,roundedCount,src,dst,mappingPlatform))return;
     drawFormationStrip(rounded,roundedCount,src,dst);return;
    }
   }
   if(mappingHero&&drawMagazineCover(vertices,count,src,dst,mappingPlatform))return;
   roundedQuad(vertices,src,dst,mappingAllGames);return;""",
        )
        change(
            "  float radius=cornerRadius(r.w,r.h,r.allGames),dx=",
            "  float radius=r.snesHero?snesHeroRadius(r.w,r.h):cornerRadius(r.w,r.h,r.allGames),dx=",
        )
    elif filename == "native_magazine.h":
        change(
            "if(systemsMode||folderMode||count!=4||!key||!gui||modal(gui)||!ensureMagazineProgram())return false;",
            "if(systemsMode||folderMode||(count!=4&&count!=16)||!key||!gui||modal(gui)||!ensureMagazineProgram())return false;",
        )
        change(
            " if(presentationKeyEqual(key,\"MegaDrive\")||presentationKeyEqual(key,\"MegaDrive - BR\")||",
            " // Keep the old model-zero map for non-SNES fallback covers. The new\n"
            " // SNES artwork uses a distinct uniform subprofile within that model.\n"
            " if(presentationKeyEqual(key,\"Super Nintendo\")||presentationKeyEqual(key,\"Super Nintendo - BR\")||\n"
            "    presentationKeyEqual(key,\"snes\")||presentationKeyEqual(key,\"snesbr\")||\n"
            "    presentationKeyEqual(key,\"super-nintendo\")||presentationKeyEqual(key,\"super-nintendo--br\")){\n"
            "  model=.25f;for(const auto&c:laserConfigs)if(strcmp(c.key,key)==0){hue=c.hue;break;}\n"
            " }\n"
            " else if(presentationKeyEqual(key,\"MegaDrive\")||presentationKeyEqual(key,\"MegaDrive - BR\")||",
        )
    elif filename == "native_magazine_field.h":
        change(
            "int modelKey=(int)(model+.5f);if(!source||!identity)return MAGAZINE_FIELD_UNSUPPORTED;",
            "int modelKey=model>.125f&&model<.5f?9:(int)(model+.5f);if(!source||!identity)return MAGAZINE_FIELD_UNSUPPORTED;",
        )
    elif filename == "magazine_shader.h":
        change(
            "   signature=vcBlue(vcSample(vec2(49,565)).rgb)+vcBlue(vcSample(vec2(963,565)).rgb)\n       +vcBlue(vcSample(vec2(120,42)).rgb)+vcBlue(vcSample(vec2(900,42)).rgb);",
            "   if(magazineModel>0.125){\n"
            "    signature=vcBlue(vcSample(vec2(22,460)).grb)+vcBlue(vcSample(vec2(1002,460)).grb)\n"
            "        +vcBlue(vcSample(vec2(22,850)).grb)+vcBlue(vcSample(vec2(1002,850)).grb);\n"
            "   }else{\n"
            "    signature=vcBlue(vcSample(vec2(49,565)).rgb)+vcBlue(vcSample(vec2(963,565)).rgb)\n"
            "        +vcBlue(vcSample(vec2(120,42)).rgb)+vcBlue(vcSample(vec2(900,42)).rgb);\n"
            "   }",
        )
        change(
            "    float m=max(box(p,vec2(45,26),vec2(157,115)),box(p,vec2(860,23),vec2(975,115)));",
            "    if(activeMagazineModel>0.125){\n"
            "     // UV coordinates measured on the new 5120x7680 SNES cover.\n"
            "     float violet=max(box(p,vec2(10,395),vec2(38,918)),box(p,vec2(987,395),vec2(1017,918)));\n"
            "     violet=max(violet,box(p,vec2(118,1428),vec2(235,1507)));\n"
            "     return max(violet,box(p,vec2(571,1428),vec2(690,1507)));\n"
            "    }\n"
            "    float m=max(box(p,vec2(45,26),vec2(157,115)),box(p,vec2(860,23),vec2(975,115)));",
        )
        change(
            "bool snesSupport(vec2 p) {",
            "bool snesNewSupport(vec2 p) {\n"
            "    return supportBox(p,vec2(7,392),vec2(41,921))\n"
            "        || supportBox(p,vec2(984,392),vec2(1020,921))\n"
            "        || supportBox(p,vec2(115,1425),vec2(238,1510))\n"
            "        || supportBox(p,vec2(568,1425),vec2(693,1510));\n"
            "}\n"
            "bool snesSupport(vec2 p) {",
        )
        change(
            "    return snesSupport(p)||megaSupport(p);",
            "    return (model>0.125?snesNewSupport(p):snesSupport(p))||megaSupport(p);",
        )
        change(
            "    if(activeMagazineModel>1.5) return n64Lamp(c);\n    return blue(c);",
            "    if(activeMagazineModel>1.5) return n64Lamp(c);\n    if(activeMagazineModel>0.125&&activeMagazineModel<0.5) return blue(c.grb);\n    return blue(c);",
        )
        change(
            "            signature=blue(sampleArt(vec2(49,565)).rgb)+blue(sampleArt(vec2(963,565)).rgb)\n                     +blue(sampleArt(vec2(120,42)).rgb)+blue(sampleArt(vec2(900,42)).rgb);",
            "            if(magazineModel>0.125){\n"
            "                signature=blue(sampleArt(vec2(22,460)).grb)+blue(sampleArt(vec2(1002,460)).grb)\n"
            "                         +blue(sampleArt(vec2(22,850)).grb)+blue(sampleArt(vec2(1002,850)).grb);\n"
            "            }else{\n"
            "                signature=blue(sampleArt(vec2(49,565)).rgb)+blue(sampleArt(vec2(963,565)).rgb)\n"
            "                         +blue(sampleArt(vec2(120,42)).rgb)+blue(sampleArt(vec2(900,42)).rgb);\n"
            "            }",
        )
    else:
        raise ValueError(filename)

    inverse = raw
    for before, after in reversed(patches):
        if inverse.count(after) != 1:
            raise ValueError(f"{filename}: inverse patch is ambiguous")
        inverse = inverse.replace(after, before, 1)
    return raw, patches, inverse


def prepare(donor: Path, output: Path) -> dict[str, object]:
    if output.exists():
        raise FileExistsError(output)
    prepared = {}
    for filename, expected in INPUT_SHA256.items():
        original = (donor / filename).read_bytes()
        if sha(original) != expected:
            raise ValueError(f"Unexpected source header {filename}")
        changed, patches, inverse = patch_file(original, filename)
        if inverse != original:
            raise ValueError(f"Byte-for-byte inverse failed {filename}")
        prepared[filename] = (changed, len(patches))
    output.mkdir(parents=True)
    receipt = {
        "schema": "station.r150.snes-cover-geometry-led.v1",
        "parentRevision": "R149; native carousel unchanged from R148",
        "sourceArtSha256": REFERENCE_ART_SHA256,
        "sourceArtDimensions": [5120, 7680],
        "shaderCoordinateDimensions": [1024, 1536],
        "ledBarsMeasured": [[14, 401, 32, 910], [994, 401, 1011, 910]],
        "inputSha256": INPUT_SHA256,
        "outputSha256": {},
        "patchCounts": {},
        "fullInversePassed": True,
        "selectedSnesHeroOnly": True,
        "systemCardsOrSmallThumbnailsChanged": False,
        "drawCallsAddedPerFrame": 0,
        "sourceTexturesAdded": 0,
        "selectedCoverVerticesBeforeAfter": [4, 16],
        "snesNewStaticFieldCacheKey": 9,
        "existingStaticFieldCacheKeysChanged": False,
        "effectCadenceGainAndBakeQuotaChanged": False,
        "compiled": False,
    }
    for filename, (changed, count) in prepared.items():
        (output / filename).write_bytes(changed)
        receipt["outputSha256"][filename] = sha(changed)
        receipt["patchCounts"][filename] = count
    (output / "overlay-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor-native", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.donor_native, args.out), ensure_ascii=False))


if __name__ == "__main__":
    main()
