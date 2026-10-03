"""Apply the source-only native HUD to an isolated upstream checkout.

Default is a dry run. Explicit --apply is required to write. The script checks
the exact upstream files before making any changes; no APK/phone is touched.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent
UPSTREAM = "1c12fac5ce49badaadff2e2f210dcc30b89f4943"
EXPECTED = {
    "EmuFramework/src/EmuApp.cc": "f915db618884f5001f95983397fddb652d296135ab2cc1a7e67da25fe6f1ecdc",
    "EmuFramework/src/EmuInput.cc": "b18a91bd4207ddc2193b123a13419a6ade1d3a4b7554426244b342757a49be77",
    "EmuFramework/src/CMakeLists.txt": "852ee60132449a83b52f1a8a50fd61ec856877a2ec3fabdab7c466601520fe59",
    "imagine/include/imagine/gfx/GfxText.hh": "d858c19df65e7ad31d57cd38523643aa39a8584e425feec95cdab0f2394654f1",
    "imagine/src/gfx/common/GfxText.cc": "460962a8c8b079471c860493bfce8a0ea6e8d6eac09fafc8b7b00585795f5b8a",
}


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Source anchor is missing or ambiguous: {old[:100]!r}")
    return text.replace(old, new, 1)


def planned_changes(source):
    originals = {}
    for relative, expected in EXPECTED.items():
        data = (source / relative).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise ValueError(f"Unexpected source SHA-256: {relative}: {actual}; expected {expected}")
        originals[relative] = data.decode("utf-8")

    changes = {}
    name = "EmuFramework/src/EmuApp.cc"
    text = originals[name]
    text = replace_once(text, "#include <emuframework/SystemActionsView.hh>",
        "#include <emuframework/SystemActionsView.hh>\n#include <emuframework/StationHudView.hh>")
    text = replace_once(text,
        "void EmuApp::showSystemActionsViewFromSystem(ViewAttachParams attach, const Input::Event &e)\n{\n\tviewController().showSystemActionsView(attach, e);\n}",
        "void EmuApp::showSystemActionsViewFromSystem(ViewAttachParams attach, const Input::Event &e)\n{\n\tif(system().hasContent())\n\t{\n\t\tshowStationHud(*this, attach, e);\n\t\treturn;\n\t}\n\tviewController().showSystemActionsView(attach, e);\n}")
    text = replace_once(text,
        "void EmuApp::showLastViewFromSystem(ViewAttachParams attach, const Input::Event &e)\n{\n\tif(systemActionsIsDefaultMenu)",
        "void EmuApp::showLastViewFromSystem(ViewAttachParams attach, const Input::Event &e)\n{\n\tif(system().hasContent())\n\t{\n\t\tshowStationHud(*this, attach, e);\n\t\treturn;\n\t}\n\tif(systemActionsIsDefaultMenu)")
    text = replace_once(text,
        "void EmuApp::showExitAlert(ViewAttachParams attach, const Input::Event &e)\n{\n\tviewController()",
        "void EmuApp::showExitAlert(ViewAttachParams attach, const Input::Event &e)\n{\n\tif(system().hasContent())\n\t{\n\t\tshowStationHud(*this, attach, e);\n\t\treturn;\n\t}\n\tviewController()")
    changes[name] = text.encode("utf-8")

    name = "EmuFramework/src/EmuInput.cc"
    changes[name] = replace_once(originals[name],
        "\t\t\tviewController.pushAndShowModal(std::make_unique<YesNoAlertView>(app.attachParams(), \"Really Exit?\",\n\t\t\t\tYesNoAlertView::Delegates{.onYes = [&app]{ app.appContext().exit(); }}), srcEvent, false);",
        "\t\t\tapp.showExitAlert(app.attachParams(), srcEvent);").encode("utf-8")

    name = "EmuFramework/src/CMakeLists.txt"
    changes[name] = replace_once(originals[name], "\tgui/StateSlotView.cc\n",
        "\tgui/StateSlotView.cc\n\tgui/StationHudView.cc\n").encode("utf-8")

    # Original files are checked above. The complete edited copies preserve
    # original draw() ABI and route it through the explicit scale=1 code path.
    for relative in ("imagine/include/imagine/gfx/GfxText.hh", "imagine/src/gfx/common/GfxText.cc"):
        changes[relative] = (ROOT / relative).read_bytes()

    for relative in ("EmuFramework/include/emuframework/StationHudView.hh",
            "EmuFramework/include/emuframework/StationHudLayout.hh", "EmuFramework/src/gui/StationHudView.cc"):
        target = source / relative
        data = (ROOT / relative).read_bytes()
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f"Refusing to replace an existing divergent HUD source: {relative}")
        changes[relative] = data
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    changes = planned_changes(source)
    if args.apply:
        for relative, data in changes.items():
            dest = source / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    print(json.dumps({"upstream": UPSTREAM, "applied": args.apply,
        "source": str(source), "files": {p: hashlib.sha256(d).hexdigest() for p, d in changes.items()}}, indent=2))


if __name__ == "__main__":
    main()
