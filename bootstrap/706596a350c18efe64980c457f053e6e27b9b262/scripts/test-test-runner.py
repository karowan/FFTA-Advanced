"""Exercise the runner's real child-process failure and reporting contracts."""
import contextlib
import importlib.util
import io
import json
import pathlib
import shutil
import unittest
import uuid
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runner', ROOT / 'scripts/run-expansion-tests.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


@contextlib.contextmanager
def scratch_case():
    scratch = (ROOT / 'build/runner-self-tests').resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    root = (scratch / ('case-' + uuid.uuid4().hex)).resolve()
    assert root.is_relative_to(scratch) and root != scratch
    # Use inherited workspace ACLs. Python's private temporary-directory mode
    # removes the additional Windows sandbox identity from its new directory.
    root.mkdir()
    try:
        yield root
    finally:
        assert root.resolve().is_relative_to(scratch) and root.resolve() != scratch
        shutil.rmtree(root)


class RunnerTests(unittest.TestCase):
    def step(self, name, code='', **kwargs):
        return dict(id=name, runtime='python', args=['-c', code], kind='test', suites=['full'], **kwargs)

    def test_dependency_closure(self):
        a, b, c = self.step('a'), self.step('b', requires=['a']), self.step('c')
        self.assertEqual([s['id'] for s in runner.choose({'steps': [a, b, c]}, 'full', ['b'])], ['a', 'b'])

    def test_invalid_plans_rejected(self):
        for steps, requested in [([self.step('a')], ['missing']),
                                 ([self.step('a'), self.step('a')], ['a']),
                                 ([self.step('a', requires=['b']), self.step('b', requires=['a'])], ['a']),
                                 ([self.step('a', requires=['b']), self.step('b')], ['a'])]:
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                runner.choose({'steps': steps}, 'full', requested)

    def run_steps(self, steps):
        with scratch_case() as root:
            probes = root / 'build/expansion/probes'
            probes.mkdir(parents=True)
            engine = b'isolated runner contract fixture'
            rom = bytes(0x1100000) + engine
            (probes / 'combat.gba').write_bytes(rom)
            (root / 'build/expansion/engine.bin').write_bytes(engine)
            (probes / 'combat.json').write_text(json.dumps({
                'romSha1': runner.hashlib.sha1(rom).hexdigest(),
                'engineSha1': runner.hashlib.sha1(engine).hexdigest()}))
            (root / 'input.txt').write_text('unchanged')
            saved = runner.ROOT, runner.RUNS, runner.source_identity
            runner.ROOT, runner.RUNS = root, root / 'runs'
            runner.source_identity = lambda: {'input.txt': runner.digest(root / 'input.txt')}
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = runner.execute({'timeoutSeconds': 10}, steps, 'self-test')
                latest = json.loads((runner.RUNS / 'latest.json').read_text())
                report_path = pathlib.Path(latest['report'])
                report = json.loads(report_path.read_text())
                xml = ET.parse(report_path.with_name('junit.xml')).getroot()
                logs = [pathlib.Path(s['log']).read_text() for s in report['steps'] if s.get('log')]
                return code, report, xml, logs, (root / 'should-not-run').exists()
            finally:
                runner.ROOT, runner.RUNS, runner.source_identity = saved

    def test_real_process_success_and_environment(self):
        code, report, xml, logs, _ = self.run_steps([self.step('pass',
            "import os; assert os.environ['PYTHONHASHSEED']=='0'; assert __debug__; print('fixed inputs')")])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'passed')
        self.assertEqual(xml.attrib['failures'], '0')
        self.assertIn('fixed inputs', logs[0])

    def test_failure_stops_dependents_and_preserves_error(self):
        code, report, xml, logs, marker = self.run_steps([
            self.step('fail', "import sys; print('expected failure'); sys.exit(7)"),
            self.step('later', "from pathlib import Path; Path('should-not-run').touch()")])
        self.assertEqual(code, 1)
        self.assertEqual([s['status'] for s in report['steps']], ['failed', 'not_run'])
        self.assertEqual(report['steps'][0]['exitCode'], 7)
        self.assertEqual((xml.attrib['failures'], xml.attrib['skipped']), ('1', '1'))
        self.assertIn('expected failure', logs[0])
        self.assertFalse(marker)

    def test_timeout_fails_instead_of_hanging(self):
        code, report, xml, _, _ = self.run_steps([self.step('timeout',
            'import time; time.sleep(3)', timeoutSeconds=0.1)])
        self.assertEqual(code, 1)
        self.assertEqual(report['steps'][0]['status'], 'timed_out')
        self.assertEqual(xml.attrib['errors'], '1')

    def test_changed_inputs_invalidate_pass(self):
        code, report, xml, _, _ = self.run_steps([self.step('mutate',
            "from pathlib import Path; Path('input.txt').write_text('changed')")])
        self.assertEqual(code, 1)
        self.assertEqual(report['steps'][0]['status'], 'passed')
        self.assertFalse(report['inputsUnchanged'])
        self.assertEqual(report['status'], 'failed')
        self.assertEqual(xml.attrib['failures'], '1')

    def test_current_plan_is_valid_and_has_expected_coverage(self):
        plan = json.loads((ROOT / 'scripts/expansion-test-plan.json').read_text())
        chosen = runner.choose(plan, 'full', None)
        self.assertEqual(len(chosen), len([s for s in plan['steps'] if 'full' in s['suites']]))
        fell = runner.choose(plan, 'fell', None)
        self.assertIn('test-fell-retaliation', [s['id'] for s in fell])
        self.assertFalse(set(s['id'] for s in chosen) & set(s['id'] for s in fell))
        for name in ('test-quin-lifecycle-in-game', 'test-combo-weapon-visuals-in-game',
                     'test-grace-in-game', 'test-dark-sword-resource-edges'):
            self.assertIn(name, [s['id'] for s in chosen])
        for step in plan['steps']:
            self.assertTrue((ROOT / step['args'][0]).is_file(), step['id'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
