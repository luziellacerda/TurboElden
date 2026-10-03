"""Tests patch anchoring and fail-closed behavior, not emulator execution."""
from pathlib import Path
import hashlib
import tempfile
import unittest

from apply_patch import EXPECTED, planned_changes, replace_once

UPSTREAM = Path(r"E:\ESTUDO APK\work\station-snes-explus-20261003\source\emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943")


class PatchGuards(unittest.TestCase):
    def test_exact_source_plans_all_files_without_writing(self):
        before = {name: (UPSTREAM / name).read_bytes() for name in EXPECTED}
        changes = planned_changes(UPSTREAM)
        self.assertEqual(len(changes), 8)
        self.assertEqual(changes["EmuFramework/src/EmuApp.cc"].count(b"showStationHud(*this, attach, e);"), 3)
        self.assertIn(b"app.showExitAlert(app.attachParams(), srcEvent);", changes["EmuFramework/src/EmuInput.cc"])
        for name, data in before.items():
            self.assertEqual((UPSTREAM / name).read_bytes(), data)
            self.assertEqual(hashlib.sha256(data).hexdigest(), EXPECTED[name])

    def test_dirty_source_rejected(self):
        with tempfile.TemporaryDirectory(prefix="hud-guard-") as temporary:
            root = Path(temporary)
            for name in EXPECTED:
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes((UPSTREAM / name).read_bytes())
            file = root / "EmuFramework/src/EmuInput.cc"
            file.write_bytes(file.read_bytes() + b"\n// a different local revision\n")
            with self.assertRaisesRegex(ValueError, "Unexpected source SHA-256"):
                planned_changes(root)
            self.assertFalse((root / "EmuFramework/src/gui/StationHudView.cc").exists())

    def test_missing_or_duplicated_anchor_rejected(self):
        for text in ("nothing matches here", "anchor anchor"):
            with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
                replace_once(text, "anchor", "replacement")


if __name__ == "__main__":
    unittest.main()
