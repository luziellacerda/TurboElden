#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Exercise the ZIP assembly primitives with tiny synthetic archives only.

No APK, emulator, Android signature, final runtime identity or phone is tested.
Productive inputs() is replaced only for the synthetic ZIP-copy fixture; its
freeze schema rejection is tested separately without that replacement.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import struct
import sys
import tempfile
import types
import unittest
import warnings
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "recipe/assemble_apk.py"
package = types.ModuleType("psx_package_probe_module"); package.__file__ = str(source)
raw = Path("\\\\?\\" + str(source)).read_text(encoding="utf-8") if sys.platform == "win32" else source.read_text(encoding="utf-8")
exec(compile(raw, str(source), "exec"), package.__dict__)


class ZipPrimitives(unittest.TestCase):
    def test_allowed_set_and_signatures(self):
        self.assertEqual((len(package.REPLACED), len(package.ADDED), len(package.SHARED)), (7, 1, 4))
        for name in ("META-INF/MANIFEST.MF", "META-INF/CERT.SF", "META-INF/CERT.RSA", "meta-inf/cert.ec"):
            self.assertTrue(package.signature_metadata(name))
        for name in ("META-INF/LICENSE", "assets/CERT.RSA", "META-INF/services/service", "META-INF/nested/CERT.SF"):
            self.assertFalse(package.signature_metadata(name))

    def test_streaming_hash(self):
        raw = bytes(range(256)) * 9216
        result = io.BytesIO()
        self.assertEqual(package.stream_copy(io.BytesIO(raw), result), hashlib.sha256(raw).hexdigest())
        self.assertEqual(result.getvalue(), raw)

    def test_duplicate_and_extras(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicates.zip"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("entry", b"1"); archive.writestr("entry", b"2")
            with zipfile.ZipFile(path) as archive:
                with self.assertRaisesRegex(ValueError, "Duplicate"): package.classic_entries(archive)
            for extra, message in ((struct.pack("<HHQ", 1, 8, 1), "ZIP64"), (b"\x02\x00\x04\x00x", "Truncated")):
                with zipfile.ZipFile(path, "w") as archive:
                    entry = zipfile.ZipInfo("entry"); entry.extra = extra; archive.writestr(entry, b"data")
                with self.assertRaises((ValueError, zipfile.BadZipFile)):
                    with zipfile.ZipFile(path) as archive: package.classic_entries(archive)

    def test_classic_end_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "classic.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.comment = b"pinned comment"; archive.writestr("entry", b"data")
            package.classic_zip(path, b"pinned comment")
            with self.assertRaises(ValueError): package.classic_zip(path, b"wrong comment")
            binary = bytearray(path.read_bytes()); position = len(binary) - 22 - len(b"pinned comment")
            struct.pack_into("<H", binary, position + 10, 0xffff); path.write_bytes(binary)
            with self.assertRaisesRegex(ValueError, "end record|sentinel"): package.classic_zip(path, b"pinned comment")

    def test_schema_rejects_unapproved_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            base, freeze, identity = (directory / name for name in ("base.zip", "freeze.json", "identity.json"))
            base.write_bytes(b"synthetic base")
            identity.write_text(json.dumps({"schemaVersion": 3, "baseApkSha256": package.sha(base)}), encoding="utf-8")
            freeze.write_text(json.dumps({"schemaVersion": 1, "revision": "R127", "sourceFrozen": True,
                "baseApkSha256": package.sha(base), "identityReceiptSha256": package.sha(identity),
                "payloads": {"lib/arm64-v8a/libmain.so": {}}}), encoding="utf-8")
            original_sha = package.BASE_SHA; package.BASE_SHA = package.sha(base)
            try:
                with self.assertRaisesRegex(ValueError, "seven replacements"):
                    package.inputs(base, freeze, identity)
            finally: package.BASE_SHA = original_sha

    def test_stream_assembly_preserves_every_other_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            base, out = directory / "base.zip", directory / "result.zip"
            freeze, identity = directory / "freeze.json", directory / "identity.json"
            freeze.write_text("{}", encoding="utf-8"); identity.write_text("{}", encoding="utf-8")
            preserved = {"lib/arm64-v8a/libmain.so": b"normal owner",
                "lib/arm64-v8a/libpcsx_rearmed_libretro_android.so": b"normal core",
                "classes36.dex": b"unchanged N64 hooks", "assets/videos/video": bytes(range(256)) * 400,
                "META-INF/LICENSE": b"not a signature"}
            paths, expected = {}, {}
            with zipfile.ZipFile(base, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=False) as archive:
                archive.comment = b"same comment"
                for name in sorted(package.REPLACED): archive.writestr(name, b"old " + name.encode())
                for name, value in preserved.items(): archive.writestr(name, value)
                for name in ("META-INF/MANIFEST.MF", "META-INF/CERT.RSA", "META-INF/CERT.SF"):
                    archive.writestr(name, b"old signature")
            for index, name in enumerate(sorted(package.PAYLOADS)):
                value = b"{}" if name == "assets/station-online/engines.json" else b"new " + name.encode()
                path = directory / (str(index) + ".payload"); path.write_bytes(value)
                paths[name], expected[name] = path, hashlib.sha256(value).hexdigest()
            original_inputs, original_sha = package.inputs, package.BASE_SHA
            package.BASE_SHA = package.sha(base)
            package.inputs = lambda *args: ({}, {"engines": []}, paths, expected, {})
            try:
                result = package.package(base, freeze, identity, out)
                self.assertEqual(result["preservedEntryCount"], len(preserved))
                with zipfile.ZipFile(out) as archive:
                    self.assertEqual(set(archive.namelist()), package.PAYLOADS | set(preserved))
                    self.assertEqual(archive.comment, b"same comment")
                    self.assertEqual(archive.getinfo(next(iter(package.ADDED))).compress_type, zipfile.ZIP_STORED)
                    for name, value in preserved.items(): self.assertEqual(archive.read(name), value)
                    for name, checksum in expected.items(): self.assertEqual(package.entry_sha(archive, name), checksum)
                report = json.loads(out.with_suffix(".package.json").read_text(encoding="utf-8"))
                self.assertEqual(set(report["preservedEntrySha256"]), set(preserved))
                self.assertEqual(len(report["removedSignatureMetadata"]), 3)
                self.assertFalse(report["signingPerformed"]); self.assertFalse(report["zipalignPerformed"])
                self.assertFalse(report["installed"]); self.assertFalse(report["physicalGameplayValidated"])
                with self.assertRaises(FileExistsError): package.package(base, freeze, identity, out)
                with self.assertRaises(FileExistsError): package.package(base, freeze, identity, base)
            finally:
                package.inputs, package.BASE_SHA = original_inputs, original_sha


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(ZipPrimitives))
    report = {"schemaVersion": 1, "passed": result.wasSuccessful(), "cases": result.testsRun,
        "scope": "Synthetic classic-ZIP/package primitives and closed payload set only",
        "sourceSha256": package.sha(source), "testSourceSha256": package.sha(Path(__file__).resolve()),
        "realRuntimeFreezeValidated": False, "realApkAssembled": False, "signedApkVerified": False,
        "phoneOperated": False, "physicalGameplayValidated": False}
    package.write(args.receipt, report)
    print(json.dumps(report))
    if not result.wasSuccessful(): raise SystemExit(1)


if __name__ == "__main__": main()
