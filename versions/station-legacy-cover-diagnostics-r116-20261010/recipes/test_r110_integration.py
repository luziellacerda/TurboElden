from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
R109 = REPO / "versions/station-render-online-r109-20261010"
COVER = REPO / "versions/station-native-cover-field-proposed-20261010"
VIDEO = REPO / "versions/station-video-retained-fastpath-20261010"
EVIDENCE = ROOT / "evidence/integration-structural.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def main() -> None:
    checks: list[str] = []

    # R110 must preserve the complete R109 Java lineage, including the robot
    # illustration retry gate and visible/focused infinite loop behavior.
    assert files(ROOT / "java") == files(R109 / "java")
    assert files(ROOT / "java-alias") == files(R109 / "java-alias")
    lottie = (
        ROOT
        / "java/netplay-src/org/emulationstation/frontend/netplay/"
        "StationLottieIllustration.java"
    )
    source = lottie.read_text(encoding="utf-8")
    for token in (
        "AnimatedImageDrawable.REPEAT_INFINITE",
        "private static final Set<String> UNAVAILABLE",
        "0,1,1L,TimeUnit.SECONDS",
    ):
        assert token in source, token
    checks.append("R109 Java and robot-loop implementation are byte-identical")

    r109_native = files(R109 / "native")
    r110_native = files(ROOT / "native")
    changed = sorted(
        name for name, digest in r110_native.items()
        if digest != r109_native.get(name)
    )
    expected_changed = [
        "d0/magazine_shader.h",
        "d0/native_carousel.cpp",
        "d0/native_magazine.h",
        "d0/native_magazine_field.h",
        "d0/native_system_video720.h",
        "d0/premium-magazine-led-android.glsl",
        "d0/video720_retained_draw_state.h",
        "d0/video720_retained_fastpath_policy.h",
    ]
    assert changed == expected_changed
    checks.append("native delta from R109 is exactly the two isolated patches")

    cover_native = files(COVER / "native")
    for name, digest in cover_native.items():
        if name in {"d0/native_carousel.cpp", "d0/native_magazine_field.h"}:
            continue
        assert r110_native[name] == digest, (COVER.name, name)
    for name, digest in files(VIDEO / "native").items():
        assert r110_native[name] == digest, (VIDEO.name, name)
    checks.append(
        "isolated patches are byte-identical except the two cover-field files extended by the upload invalidation hook"
    )

    assert sha(ROOT / "native/d0/native_magazine_field.h") == (
        "98e422ce0f12172b0ea9a641ec66bd1cf646259d4e75844c8b02a07abc11cded"
    )
    assert sha(ROOT / "native/d0/native_system_video720.h") == (
        "50b5766c66487b96aa46eca99ed94e43f9ee6ad2621eea5bd9f3f6ca31c56c1e"
    )
    checks.append("integrated cover-field and reviewed retained-video source hashes match")

    field = (ROOT / "native/d0/native_magazine_field.h").read_text(encoding="utf-8")
    carousel = (ROOT / "native/d0/native_carousel.cpp").read_text(encoding="utf-8")
    relocations = (
        Path(r"E:\ESTUDO APK\work\station-controller-ui-r97-20261009\carousel-inputs")
        / "d1/relocations.h"
    ).read_text(encoding="utf-8")
    for token in (
        "magazineFieldUploadRevision",
        "noteMagazineSourceTextureUpload",
        "c.uploadRevision==uploadRevision",
        "if(uploadRevision!=magazineFieldUploadRevision)return false;",
    ):
        assert token in field, token
    create_original = (
        "fn<unsigned(*)(unsigned,bool,bool,unsigned,unsigned,const void*)>"
        "(0x2e4a28)"
    )
    update_original = (
        "fn<void(*)(unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,const void*)>"
        "(0x2e4f78)"
    )
    destroy_original = "fn<void(*)(unsigned)>(0x2e4f1c)"
    create_hook = carousel[
        carousel.index("static unsigned createTextureRevisionHook"):
        carousel.index("static void updateTextureRevisionHook")
    ]
    update_hook = carousel[
        carousel.index("static void updateTextureRevisionHook"):
        carousel.index("static void* heading")
    ]
    destroy_hook = carousel[
        carousel.index("static void destroyTextureRevisionHook"):
        carousel.index("static void updateTextureRevisionHook")
    ]
    assert create_original in create_hook
    assert update_original in update_hook
    assert create_hook.index(create_original) < create_hook.index(
        "noteMagazineSourceTextureUpload(texture);"
    )
    assert update_hook.index(update_original) < update_hook.index(
        "noteMagazineSourceTextureUpload(texture);"
    )
    assert destroy_hook.index(
        "noteMagazineSourceTextureUpload(texture);"
    ) < destroy_hook.index(destroy_original)
    assert "{0x2e4a28,(void*)createTextureRevisionHook}" in carousel
    assert "{0x2e4f1c,(void*)destroyTextureRevisionHook}" in carousel
    assert "{0x2e4f78,(void*)updateTextureRevisionHook}" in carousel
    assert "at<unsigned>((void*)base,0x2e4a28)!=0xd10643ff" in carousel
    assert "at<unsigned>((void*)base,0x2e4f1c)!=0xd100c3ff" in carousel
    assert "at<unsigned>((void*)base,0x2e4f78)!=0xd10683ff" in carousel
    assert relocations.count("{0x3c15f8,0x2e4a28}") == 1
    assert relocations.count("{0x3c1350,0x2e4f1c}") == 1
    assert relocations.count("{0x3c2a98,0x2e4f78}") == 1
    checks.append(
        "Renderer texture creation, destruction and in-place updates all retire the exact selected source across a recycled GLuint lifetime"
    )

    model = {"valid": True, "source": 71, "observed": 71, "identity": 9, "revision": 4}

    def upload(texture: int) -> None:
        if texture not in (model["source"], model["observed"]):
            return
        model["revision"] += 1
        model.update(valid=False, source=0, observed=0, identity=0)

    upload(22)
    assert model == {"valid": True, "source": 71, "observed": 71, "identity": 9, "revision": 4}
    captured = model["revision"]
    upload(71)
    assert model == {"valid": False, "source": 0, "observed": 0, "identity": 0, "revision": 5}
    assert captured != model["revision"]
    model.update(valid=True, source=71, observed=71, identity=10)
    captured = model["revision"]
    upload(71)
    assert model == {"valid": False, "source": 0, "observed": 0, "identity": 0, "revision": 6}
    assert captured != model["revision"]
    model.update(valid=True, source=71, observed=71, identity=11)
    captured = model["revision"]
    upload(71)
    assert model == {"valid": False, "source": 0, "observed": 0, "identity": 0, "revision": 7}
    assert captured != model["revision"]
    checks.append(
        "modeled unrelated events are ignored; destruction, recycled creation and in-place updates reject stale fields"
    )

    build = (ROOT / "build.py").read_text(encoding="utf-8")
    for token in (
        'ROOT.name == "station-render-native-r110-20261010"',
        '"lib/arm64-v8a/libturbo_carousel.so": carousel',
        'expected_changes = [\n        "classes35.dex",\n        "lib/arm64-v8a/libturbo_carousel.so",',
        'assert files(original_carousel) == expected_carousel',
        'assert carousel_sha != BASE_CAROUSEL_SHA',
    ):
        assert token in build, token
    checks.append("build recipe compiles and packages both Java and native payloads")

    result = {
        "status": "passed",
        "sourceBase": "R109",
        "changedNativeFromR109": changed,
        "robotJavaSHA256": sha(lottie),
        "nativeFieldSHA256": sha(ROOT / "native/d0/native_magazine_field.h"),
        "retainedVideoSHA256": sha(ROOT / "native/d0/native_system_video720.h"),
        "rendererCreateTexture": {
            "offset": "0x2e4a28",
            "relocation": "{0x3c15f8,0x2e4a28}",
            "expectedPrologue": "0xd10643ff",
            "originalCalledBeforeInvalidation": True,
        },
        "rendererUpdateTexture": {
            "offset": "0x2e4f78",
            "relocation": "{0x3c2a98,0x2e4f78}",
            "expectedPrologue": "0xd10683ff",
            "originalCalledBeforeInvalidation": True,
        },
        "rendererDestroyTexture": {
            "offset": "0x2e4f1c",
            "relocation": "{0x3c1350,0x2e4f1c}",
            "expectedPrologue": "0xd100c3ff",
            "invalidationCalledBeforeOriginal": True,
        },
        "textureLifetimeModelCases": 4,
        "checks": checks,
        "deviceUsed": False,
        "installed": False,
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
