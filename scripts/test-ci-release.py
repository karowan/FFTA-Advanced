"""Deterministic packaging and rejection checks without a game ROM."""
import copy
import json
import struct
import unittest
import zlib

from ci_release import build, verify_patch, number
from mod_release import ROOT, record, sha, read_archive


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        # A declared one-byte SourceRead BPS fixture, constructed in memory.
        # It is never a game ROM, never published and never a release input.
        source = b'A'
        raw = b'BPS1' + bytes([0x81, 0x81, 0x80, 0x80])
        raw += struct.pack('<II', zlib.crc32(source), zlib.crc32(source))
        self.patch = raw + struct.pack('<I', zlib.crc32(raw))
        self.config = dict(schema=1, name='FFTA Advanced', version='0.7.0', tag='v0.7.0', source=record(source),
                           target=dict(file='test.gba', **record(source)),
                           patch=dict(file='FFTA_Expansion.bps', format='BPS', bytes=len(self.patch), sha256=sha(self.patch)),
                           localAcceptance={'scope': 'Synthetic packaging test only'})
        self.template = (ROOT / 'MOD-README.md').read_text(encoding='utf-8')

    def package(self, config=None, patch=None, template=None, tag='v0.7.0'):
        return build(config or self.config, patch or self.patch, template or self.template, 'Release notes\n', tag)

    def test_deterministic_archive_and_exact_contents(self):
        first, files = self.package(); second, _ = self.package()
        self.assertEqual(first, second)
        manifest, unpacked = read_archive(first)
        self.assertEqual(unpacked, files)
        self.assertEqual(set(files), {'FFTA_Expansion.bps', 'README.md', 'CHANGELOG.md', 'manifest.json'})
        self.assertEqual(files['FFTA_Expansion.bps'], self.patch)
        self.assertNotIn(b'{{', files['README.md'])
        self.assertIn('no game compilation', manifest['validation']['ci']['scope'])

    def test_wrong_patch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'accepted input'):
            self.package(patch=self.patch[:-1] + b'!')

    def test_patch_crc_independent_of_sha(self):
        patch = self.patch[:-1] + bytes([self.patch[-1] ^ 1])
        config = copy.deepcopy(self.config); config['patch']['sha256'] = sha(patch)
        with self.assertRaisesRegex(ValueError, 'patch CRC'):
            self.package(config=config, patch=patch)

    def test_source_target_identity_rejected(self):
        for field in ('source', 'target'):
            for key, value in (('bytes', 2), ('crc32', '00000000')):
                with self.subTest(field=field, key=key):
                    config = copy.deepcopy(self.config); config[field][key] = value
                    with self.assertRaises(ValueError): self.package(config=config)

    def test_tag_and_template_rejected(self):
        for tag in ('v9.0.0', '../bad', 'v0.7.0;echo bad'):
            with self.subTest(tag=tag), self.assertRaises(ValueError): self.package(tag=tag)
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            self.package(template=self.template + '{{UNEXPECTED}}')

    def test_truncated_header_rejected(self):
        with self.assertRaises(ValueError): number(b'BPS1' + bytes(12), 4)


if __name__ == '__main__':
    unittest.main()
