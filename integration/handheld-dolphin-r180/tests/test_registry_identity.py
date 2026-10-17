"""Catch runtime/option updates reusing an immutable GBA engine identity."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'recipe'))
from registry_delta import gba_identity, OPTIONS


class RegistryIdentity(unittest.TestCase):
    def test_same_inputs_are_reproducible(self):
        self.assertEqual(gba_identity('a'*64, 'b'*64), gba_identity('a'*64, 'b'*64))

    def test_runtime_update_cannot_reuse_old_id(self):
        self.assertNotEqual(gba_identity('a'*64, 'b'*64), gba_identity('a'*64, 'c'*64))

    def test_core_update_cannot_reuse_old_id(self):
        self.assertNotEqual(gba_identity('a'*64, 'b'*64), gba_identity('c'*64, 'b'*64))

    def test_option_update_cannot_reuse_old_id(self):
        self.assertNotEqual(gba_identity('a'*64, 'b'*64),
                            gba_identity('a'*64, 'b'*64, OPTIONS.replace('auto', 'rfu')))


if __name__ == '__main__':
    unittest.main()
