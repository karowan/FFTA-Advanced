"""Portable interpreter selection, redaction and history-free source integrity."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid

from historical_sources import ROOT, bundled_files, source_file, source_tree, validate_name
from engine_bootstrap_source import sources as adapt
from source_hygiene import personal_path_lines, secret_findings

spec = importlib.util.spec_from_file_location('public_export', ROOT / 'scripts/export-public-source.py')
export = importlib.util.module_from_spec(spec); spec.loader.exec_module(export)


class CleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ROOT / 'build/source-cleanup-tests' / uuid.uuid4().hex
        cls.root.mkdir(parents=True)

    def test_redaction_preserves_json_content_and_source_hash(self):
        path = 'C:' + '\\Users\\example\\art\\image.png'
        raw = json.dumps(dict(prompt='Keep the same colors.', path=path, sha256='a'*64)).encode()
        cleaned = export.redact(raw)
        self.assertTrue(personal_path_lines(raw))
        self.assertFalse(personal_path_lines(cleaned))
        parsed = json.loads(cleaned)
        self.assertEqual(parsed['prompt'], 'Keep the same colors.')
        self.assertEqual(parsed['sha256'], 'a'*64)
        self.assertTrue(parsed['path'].endswith('art\\image.png'))

    def test_secret_locations_do_not_disclose_values(self):
        token = b'gh' + b'p_' + b'A' * 36
        result = secret_findings(b'\n' + token)
        self.assertEqual(result, [{'rule': 'github-token', 'line': 2}])
        self.assertNotIn(token.decode(), str(result))

    def test_personal_paths_on_all_supported_platforms(self):
        paths = ['C:/' + 'Users/example/art.png', 'C:' + '\\Users\\example\\art.png',
                 '/' + 'Users/example/art.png', '/' + 'home/example/art.png']
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(personal_path_lines(('first\n' + path).encode()), [2])
                raw = json.dumps({'path': path, 'prompt': 'Keep colors.', 'sha256': 'a' * 64}).encode()
                cleaned = export.redact_source('receipt.json', raw)
                self.assertFalse(personal_path_lines(cleaned))
                parsed = json.loads(cleaned)
                self.assertEqual(parsed['prompt'], 'Keep colors.')
                self.assertEqual(parsed['sha256'], 'a' * 64)
                self.assertTrue(parsed['path'].startswith('<LOCAL_USER>'))

    def test_export_refuses_to_rewrite_executable_source(self):
        raw = ('path = ' + repr('/' + 'home/example/art.png') + '\n').encode()
        for name in ('script.py', 'script.mjs', 'script.ps1', 'source.c', 'bootstrap/revision/data.json'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'fix manually'):
                export.redact_source(name, raw)

    def test_export_preserves_its_own_privacy_tools(self):
        for name in ('scripts/source_hygiene.py', 'scripts/export-public-source.py'):
            raw = (ROOT / name).read_bytes()
            with self.subTest(name=name):
                self.assertFalse(personal_path_lines(raw))
                self.assertEqual(export.redact_source(name, raw), raw)
        # Execute the exported detector to catch syntactically valid corruption.
        namespace = {}
        exec(compile(export.redact_source('scripts/source_hygiene.py',
                     (ROOT / 'scripts/source_hygiene.py').read_bytes()), 'exported-checker', 'exec'), namespace)
        for prefix in ('/' + 'Users/', '/' + 'home/', 'C:' + '/Users/'):
            self.assertEqual(namespace['personal_path_lines']((prefix + 'example/a.png').encode()), [1])

    def test_historical_paths_reject_traversal(self):
        for name in ('../a.py', '/absolute.py', 'C:/file.py', 'a\\b.py'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_name(name)

    def test_public_bundle_matches_git_and_rejects_tampering(self):
        commit = json.loads((ROOT / 'notes/engine-bootstrap.json').read_bytes())['sourceCommit']
        expected, _ = source_tree(commit)
        profile = json.loads((ROOT / 'notes/native-art-gameplay-base.json').read_bytes())
        commits = {commit: expected}
        for row in profile['overrides']:
            raw = source_file(row['commit'], row['path'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            commits.setdefault(row['commit'], {})[row['path']] = raw
        index = {'schema': 1, 'commits': {}}
        for revision, entries in commits.items():
            index['commits'][revision] = {}
            for name, raw in entries.items():
                path = self.root / 'bootstrap' / revision / name
                path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
                index['commits'][revision][name] = hashlib.sha256(raw).hexdigest()
        (self.root / 'bootstrap/index.json').write_text(json.dumps(index))
        actual, _ = source_tree(commit, self.root)
        self.assertEqual(actual, expected)
        self.assertEqual(adapt(actual), adapt(expected))
        for row in profile['overrides']:
            self.assertEqual(source_file(row['commit'], row['path'], self.root), commits[row['commit']][row['path']])
        first = next(iter(expected))
        (self.root / 'bootstrap' / commit / first).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            bundled_files(self.root, commit)

    def test_python_selection_explicit_environment_and_missing(self):
        shell = shutil.which('pwsh') or shutil.which('powershell')
        self.assertIsNotNone(shell)
        # Values use PowerShell single-quoted literals, never shell interpolation.
        quote = lambda text: "'" + str(text).replace("'", "''") + "'"
        setup = '. ' + quote(ROOT / 'scripts/resolve-python.ps1') + '; '
        for body in ('Resolve-FftaPython -Python ' + quote(sys.executable),
                     '$env:FFTA_PYTHON=' + quote(sys.executable) + '; Resolve-FftaPython'):
            result = subprocess.run([shell, '-NoProfile', '-Command', setup + body], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(result.stdout.strip()).resolve(), Path(sys.executable).resolve())
        result = subprocess.run([shell, '-NoProfile', '-Command', setup +
                                 "Resolve-FftaPython -Python 'missing-ffta-python-executable'"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
