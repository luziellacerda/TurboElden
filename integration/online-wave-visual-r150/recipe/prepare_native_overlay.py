"""Prepare R150 presentation headers from exact R149 carousel inputs.

Only the blue sky literals and the fixed native wave presentation are changed.
The R148 system-synopsis header survives unchanged in R149 and must retain priority
in the native build. This recipe never edits the pinned donor files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


BASE_SHA256 = {
    "native_space.h": "2ac9e649e27f8ed4259f01cf5116186f76b4481019f5181c36c3956ed4eb7f65",
    "station_theme_palette.h": "e32a61fcbbd24f522b14d78ec138ebb8edaa7a80f1f31c39b9cb03f77f516ef3",
    "station_wave_palette.h": "c63c0725f8446fb1cfa434a89a9bdc6f04da44280dd61fd323b0ec95b9397a97",
}

OLD_WAVES = b"""static void drawNativeWaves(float w,float h,float t){
 fn<void(*)(unsigned)>(3035880)(0);
 const auto*palette=stationWaveCurrentPalette();unsigned bands=palette?palette->count:3u;
 Vertex strip[66];
 for(unsigned wave=0;wave<bands;wave++){
  unsigned color=fn<unsigned(*)(unsigned)>(3029376)(stationWaveColor((int)wave,palette));
  for(int i=0;i<=32;i++){
   float u=i/32.f,x=w*u,y=h*(.47f+wave*.065f+flightSin(u*5.5f+t*.32f+wave*.7f)*.075f+flightSin(u*2.1f-t*.19f)*.025f);
   float half=h*(.007f+wave*.002f)*(palette?palette->widthMultipliers[wave]:1.f);strip[i*2]={x,y-half,0,0,color};strip[i*2+1]={x,y+half,0,0,color};
  }
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,66,4,5);
 }
}
"""

NEW_WAVES = b"""static void drawNativeWaves(float w,float h,float t){
 fn<void(*)(unsigned)>(3035880)(0);
 const auto*palette=stationWaveCurrentPalette();unsigned bands=palette?palette->count:3u;
 // The online-room four-curve composition is mapped to the existing animated
 // strips. Keep the same 32 samples, two flightSin calls and clock per band.
 static const float stroke3[3]={14.f,4.6f,1.3f};
 static const float stroke4[4]={14.f,7.f,2.2f,1.3f};
 static const float stroke5[5]={14.f,10.5f,7.f,2.2f,1.3f};
 const float*strokes=bands==5?stroke5:bands==4?stroke4:stroke3;
 Vertex strip[66];
 for(unsigned wave=0;wave<bands;wave++){
  float position=(float)wave/(float)(bands-1u);
  float center=.48f+.18f*position;
  float amplitude=position<=.6666667f?.055f+.06f*position:.095f-.075f*(position-.6666667f);
  float half=h*(strokes[wave]/1440.f)*(palette?palette->widthMultipliers[wave]:1.f);
  unsigned color=fn<unsigned(*)(unsigned)>(3029376)(stationWaveColor((int)wave,palette));
  for(int i=0;i<=32;i++){
   float u=i/32.f,x=w*u,y=h*(center+flightSin(u*6.8f+t*.32f+2.675f)*amplitude+flightSin(u*2.1f-t*.19f)*.015f);
   strip[i*2]={x,y-half,0,0,color};strip[i*2+1]={x,y+half,0,0,color};
  }
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,66,4,5);
 }
}
"""

SNES_OLD = b"{3,{0xFF4058B0u,0xEE5B67A0u,0xA7B3C390u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // SNES: red, red, gray"
SNES_NEW = b"{4,{0xFFDA52B0u,0x369DFFA0u,0x44D98A90u,0xFF405880u,0u},{1.f,1.f,1.f,1.f,1.f}}, // SNES: yellow, blue, green, red"
TOP_OLD = b"0x287EB5ffu"
TOP_NEW = b"0x226FA7ffu"
BOTTOM_OLD = b"0x5DAEDEffu"
BOTTOM_NEW = b"0x509ACCffu"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_exact(raw: bytes, before: bytes, after: bytes, count: int) -> bytes:
    if raw.count(before) != count or after in raw:
        raise ValueError(f"Expected {count} occurrences of pinned presentation anchor")
    result = raw.replace(before, after)
    if result.replace(after, before) != raw:
        raise ValueError("Presentation patch does not invert to the exact input")
    return result


def prepare(donor: Path, output: Path) -> dict[str, object]:
    if output.exists():
        raise FileExistsError(output)
    sources = {name: (donor / name).read_bytes() for name in BASE_SHA256}
    if {name: sha(raw) for name, raw in sources.items()} != BASE_SHA256:
        raise ValueError("R149 native visual input differs from the pinned source")

    space = replace_exact(sources["native_space.h"], OLD_WAVES, NEW_WAVES, 1)
    space = replace_exact(space, TOP_OLD, TOP_NEW, 1)
    space = replace_exact(space, BOTTOM_OLD, BOTTOM_NEW, 1)
    theme = replace_exact(sources["station_theme_palette.h"], TOP_OLD, TOP_NEW, 1)
    theme = replace_exact(theme, BOTTOM_OLD, BOTTOM_NEW, 1)
    palette = replace_exact(sources["station_wave_palette.h"], SNES_OLD, SNES_NEW, 1)
    changed = {"native_space.h": space,
               "station_theme_palette.h": theme,
               "station_wave_palette.h": palette}

    # An independent, explicit inverse audit covers every byte of each header.
    recovered = {
        "native_space.h": space.replace(TOP_NEW, TOP_OLD).replace(BOTTOM_NEW, BOTTOM_OLD).replace(NEW_WAVES, OLD_WAVES),
        "station_theme_palette.h": theme.replace(TOP_NEW, TOP_OLD).replace(BOTTOM_NEW, BOTTOM_OLD),
        "station_wave_palette.h": palette.replace(SNES_NEW, SNES_OLD),
    }
    if recovered != sources:
        raise ValueError("R150 inverse audit did not recover all native sources")
    output.mkdir(parents=True)
    for name, raw in changed.items():
        (output / name).write_bytes(raw)
    receipt = {
        "schema": "station.r150.visual.native-overlay.v1",
        "parentRevision": "R149",
        "inputSha256": BASE_SHA256,
        "outputSha256": {name: sha(raw) for name, raw in changed.items()},
        "inverseByteExact": True,
        "blueArgb": {"top": "#226FA7", "bottom": "#509ACC"},
        "onlineRoomSourceChanged": False,
        "nativeWaveSamplesPerStrip": 33,
        "nativeWaveVerticesPerStrip": 66,
        "trigonometricCallsPerSample": 2,
        "waveBands": {"SNES": 4, "otherSystems": "unchanged"},
        "newTimersThreadsHeapAllocations": 0,
        "systemCoverRadiusChanged": False,
        "snesVideoChanged": False,
        "systemSynopsisR148Changed": False,
        "compiled": False,
        "installed": False,
    }
    (output / "overlay-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor-native", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.donor_native, args.out), ensure_ascii=False))


if __name__ == "__main__":
    main()
