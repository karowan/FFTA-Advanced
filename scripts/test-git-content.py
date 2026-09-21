"""Exercise ROM exclusion against a disposable real Git index."""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import unittest
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('git_guard', ROOT / 'scripts/check-git-content.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ContentGuardTests(unittest.TestCase):
    def setUp(self):
        self.parent = (ROOT / 'build/git-guard-tests').resolve()
        self.path = self.parent / uuid.uuid4().hex
        self.path.mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(self.path)], check=True)

    def tearDown(self):
        assert self.path.resolve().is_relative_to(self.parent) and self.path != self.parent
        # Git objects may be read-only on Windows. Keep this small diagnostic
        # fixture as evidence rather than weakening ACLs for recursive removal.

    def stage(self, name, data):
        file = self.path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
        subprocess.run(['git', 'add', '--', name], cwd=self.path, check=True)

    def test_source_allowed(self):
        self.stage('source.py', b'print("hello")\n')
        guard.check_index(self.path)

    def test_rom_extension_rejected(self):
        self.stage('game.gba', b'even-text-is-forbidden')
        with self.assertRaises(SystemExit):
            guard.check_index(self.path)

    def test_renamed_binary_rejected(self):
        self.stage('innocent.md', b'\x00\xff\xfe' * 128)
        with self.assertRaises(SystemExit):
            guard.check_index(self.path)

    def test_staged_bytes_checked_instead_of_working_copy(self):
        self.stage('renamed.py', b'\x00\xffROM')
        (self.path / 'renamed.py').write_text('# clean working copy\n')
        with self.assertRaises(SystemExit):
            guard.check_index(self.path)

    def test_private_path_rejected(self):
        self.stage('roms/renamed.md', b'not a source location')
        with self.assertRaises(SystemExit):
            guard.check_index(self.path)

    def test_credential_filename_rejected(self):
        self.stage('credentials.json', b'{}')
        with self.assertRaises(SystemExit):
            guard.check_index(self.path)

    def test_credential_value_rejected_without_disclosing_it(self):
        token = b'gh' + b'p_' + b'A' * 36
        self.stage('settings.json', b'{"token":"' + token + b'"}')
        with self.assertRaises(SystemExit) as caught:
            guard.check_index(self.path)
        self.assertNotIn(token.decode(), str(caught.exception))

    def test_private_key_rejected(self):
        self.stage('notes.txt', b'-----BEGIN ' + b'PRIVATE KEY-----\nprivate')
        with self.assertRaises(SystemExit):
            guard.check_index(self.path)

    def test_registered_artwork_allowed_and_changed_bytes_rejected(self):
        row = json.loads((ROOT / 'artwork/manifest.json').read_bytes())['files'][0]
        raw = (ROOT / row['path']).read_bytes()
        self.stage('artwork/manifest.json', json.dumps({'schema':1,'files':[row]}).encode())
        self.stage(row['path'], raw)
        guard.check_index(self.path)
        self.stage(row['path'], raw + b'private trailing payload')
        with self.assertRaises(SystemExit): guard.check_index(self.path)

    def test_unregistered_png_rejected(self):
        row = json.loads((ROOT / 'artwork/manifest.json').read_bytes())['files'][0]
        self.stage('artwork/characters/unapproved.png', (ROOT / row['path']).read_bytes())
        with self.assertRaises(SystemExit): guard.check_index(self.path)


if __name__ == '__main__':
    unittest.main()
