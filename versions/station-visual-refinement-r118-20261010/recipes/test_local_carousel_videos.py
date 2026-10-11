from pathlib import Path
import hashlib
import json
import os
import zipfile


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
R110 = REPO / "versions/station-render-native-r110-20261010"
BASE = Path(
    r"G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R110-20261010.apk"
)
FINAL = Path(
    r"G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R111-20261010.apk"
)
CAROUSEL_SHA = "56a03756f1cf2877f863e496db26ed8da5cfc7d6c5f063a71d53b9085559d74a"
ROBOT_SHA = "deb59b9105c78765a5aa14dea7ec64ef37032490c578b5ec713481b302f24186"


def native(path: Path) -> Path:
    return Path("\\\\?\\" + str(path.resolve())) if os.name == "nt" else path


def sha(path: Path) -> str:
    with native(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def zip_sha(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def signature(name: str) -> bool:
    return name.startswith("META-INF/") and name.upper().endswith(
        (".MF", ".SF", ".RSA", ".DSA", ".EC")
    )


def tree(root: Path):
    return {
        path.relative_to(root).as_posix(): sha(path)
        for path in sorted(root.rglob("*")) if path.is_file()
    }


def main():
    checks = []

    def check(value, label):
        assert value, label
        checks.append(label)

    android = ROOT / "java/client/src/java/org/emulationstation/frontend/station/StationAndroid.java"
    frontend = ROOT / "java/client/src/java/org/emulationstation/frontend/station/StationFrontend.java"
    video = ROOT / "java/netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java"
    robot = ROOT / "java/netplay-src/org/emulationstation/frontend/netplay/StationLottieIllustration.java"
    media = ROOT / "java/client/src/java/org/emulationstation/frontend/station/StationCarouselMedia.java"
    media_store = ROOT / "java/client/src/java/org/emulationstation/frontend/station/StationMediaStore.java"
    media_catalog = ROOT / "java/client/src/java/org/emulationstation/frontend/station/StationMediaCatalog.java"

    a = android.read_text(encoding="utf-8")
    f = frontend.read_text(encoding="utf-8")
    v = video.read_text(encoding="utf-8")
    check("StationCarouselMedia.install" not in a, "startup install hook removed")
    check("StationCarouselMedia" not in f, "catalog/download lifecycle hooks removed")
    check("assets.openFd(s.asset)" in v, "video opens bundled AssetManager file descriptor")
    check("StationCarouselMedia" not in v and "FileInputStream" not in v,
          "video has no cache lookup or filesystem data source")

    refs = []
    for branch in [ROOT / "java/client", ROOT / "java/netplay-src"]:
        for path in branch.rglob("*.java"):
            if path == media:
                continue
            if "StationCarouselMedia" in path.read_text(encoding="utf-8"):
                refs.append(path.relative_to(ROOT / "java").as_posix())
    check(refs == [], "zero StationCarouselMedia references outside its own class")
    check(media.is_file() and media_store.is_file() and media_catalog.is_file(),
          "remote media compatibility classes remain in source")
    check(sha(robot) == ROBOT_SHA and sha(robot) == sha(R110 / robot.relative_to(ROOT)),
          "looping robot source is byte-identical to R110")
    check(tree(ROOT / "native") == tree(R110 / "native"),
          "complete native source tree is byte-identical to R110")

    with zipfile.ZipFile(BASE) as base:
        base_videos = [n for n in base.namelist()
                       if n.startswith("assets/turbo-system-videos/") and n.endswith(".mp4")]
        check(len(base_videos) == 58, "R110 base contains 58 bundled system videos")
        check(zip_sha(base, "lib/arm64-v8a/libturbo_carousel.so") == CAROUSEL_SHA,
              "R110 native carousel hash matches the frozen reference")

    artifact_checked = FINAL.is_file()
    if artifact_checked:
        changes = []
        with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(FINAL) as final:
            base_names = {n for n in base.namelist() if not signature(n)}
            final_names = {n for n in final.namelist() if not signature(n)}
            check(base_names == final_names, "R111 keeps the complete R110 APK member set")
            for name in sorted(final_names):
                if zip_sha(base, name) != zip_sha(final, name):
                    changes.append(name)
            check(changes == ["classes28.dex", "classes35.dex"],
                  "only client and room DEX differ from R110")
            check(zip_sha(final, "lib/arm64-v8a/libturbo_carousel.so") == CAROUSEL_SHA,
                  "R111 native carousel is byte-identical to R110")
            videos = [n for n in final.namelist()
                      if n.startswith("assets/turbo-system-videos/") and n.endswith(".mp4")]
            check(len(videos) == 58, "R111 packages all 58 local system videos")

    result = {
        "version": "R111-candidate",
        "checksPassed": len(checks),
        "checks": checks,
        "artifactChecked": artifact_checked,
        "behaviorReference": {
            "R90LocalVideoCommit": "58839537f28be3fbf17d012dd764b1431db4acd6",
            "R91RemoteMediaCommit": "4276a5fa0af77a106bca2cab67116a34efe83501",
        },
    }
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "evidence/structural-checks.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
