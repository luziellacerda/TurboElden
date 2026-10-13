"""Exercise the guard with the actual inherited Java and R132 frontend sources."""
from pathlib import Path
import argparse
import importlib.util
import json
import shutil
from verify_nes_preservation import EDITS, NATIVE_EDITS, apply_allowed, verify

REPO = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out = args.out.resolve()
    if args.out == REPO or REPO in args.out.parents:
        raise ValueError("Test output must be outside the repository and frozen sources")
    if args.out.exists():
        raise ValueError("Choose a fresh test directory")
    args.out.mkdir(parents=True)
    inherited = REPO / "versions/station-video-room-footer-r124-20261011"
    before, after = args.out / "before-station", args.out / "after-station"
    source = inherited / "java/client/src/java/org/emulationstation/frontend/station"
    shutil.copytree(source, before)
    shutil.copytree(source, after)
    for name, edits in EDITS.items():
        (after / name).write_bytes(apply_allowed((before / name).read_bytes(), edits))
    loading = REPO / "integration/startup-cleanup-r132/recipe/patch_loading.py"
    spec = importlib.util.spec_from_file_location("loading", loading)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    current_frontend = module.transform((inherited / "frontend/station_frontend.cpp").read_bytes(),
                                         (module.FRONTEND_SHA,), module.FRONTEND_REPLACEMENTS)
    pre, post = args.out / "before.cpp", args.out / "after.cpp"
    pre.write_bytes(current_frontend)
    correct = apply_allowed(current_frontend, NATIVE_EDITS)
    post.write_bytes(correct)
    accepted = verify(before, after, pre, post)
    rejected = []

    def refuse(label):
        try:
            verify(before, after, pre, post)
        except ValueError as error:
            rejected.append({"case": label, "error": str(error)})
        else:
            raise AssertionError("Unsafe composition accepted: " + label)

    old_snapshot = REPO / "integration/station-nes-catalogo-20261012/native/station_frontend.cpp"
    post.write_bytes(old_snapshot.read_bytes())
    refuse("complete-old-NES-frontend-snapshot")
    post.write_bytes(correct)
    queue = after / "StationCoverQueue.java"
    queue_correct = queue.read_bytes()
    anchor = b"new ThreadPoolExecutor(1,1,10"
    assert queue_correct.count(anchor) == 1
    queue.write_bytes(queue_correct.replace(anchor, b"new ThreadPoolExecutor(2,2,10"))
    refuse("extra-cover-workers")
    queue.write_bytes(queue_correct)
    unchanged = after / "StationCoverStore.java"
    store_correct = unchanged.read_bytes()
    unchanged.write_bytes(store_correct + b"\n// unrelated change\n")
    refuse("unrelated-store-edit")
    unchanged.write_bytes(store_correct)
    queue.write_bytes(queue_correct.replace(b"\r\n", b"\n") if b"\r\n" in queue_correct else queue_correct.replace(b"\n", b"\r\n"))
    refuse("whole-file-line-ending-rewrite")
    queue.write_bytes(queue_correct)
    (after / "Unexpected.java").write_bytes(b"class Unexpected {}")
    refuse("extra-java-source")
    (after / "Unexpected.java").unlink()
    verify(before, after, pre, post)
    report = {"acceptedCurrentComposition": accepted, "rejectedUnsafeCompositions": rejected,
              "allFiveNegativeCasesRejected": len(rejected) == 5,
              "frozenSourcesChanged": False, "apkBuilt": False, "androidExecuted": False}
    (args.out / "receipt.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
