"""Deterministic expansion test runner. No model, network, or GUI agent calls.

Run the declared commands sequentially, preserve complete per-step logs, and
emit JSON/JUnit reports. Selection is explicit; a selected subset is never
reported as a full regression or proof of the unfinished expansion.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAN = ROOT / 'scripts/expansion-test-plan.json'
RUNS = ROOT / 'build/expansion/test-runs'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def source_identity():
    # Deliberately conservative. Reports can establish which build and harness
    # passed, but are not an automatic cache of unspecified fixture inputs.
    paths = [ROOT / 'Build Engine.ps1', PLAN, pathlib.Path(sys.executable)]
    for folder, suffixes in [('src', None), ('scripts', {'.py', '.mjs', '.json'}),
                             ('notes', {'.json'})]:
        paths += [p for p in (ROOT / folder).rglob('*') if p.is_file()
                  and (suffixes is None or p.suffix in suffixes)]
    paths += [p for p in (ROOT / 'tools/mgba-test-core').glob('*.dll')]
    paths += [ROOT / 'build/expansion' / name for name in
              ('engine.bin', 'engine.symbols', 'registry.json')]
    # These generated files are compiler/data inputs, not test outputs. The
    # private builder also reads content-data.json and the native fixture seed.
    paths += [p for p in (ROOT / 'build/expansion').iterdir()
              if p.is_file() and p.suffix in {'.h', '.inc'}]
    paths += [ROOT / 'build/expansion/probes/content-data.json',
              ROOT / 'roms/clean/FFTA_US_clean.gba',
              ROOT / 'build/test-lab/early-town.sav']
    paths += [ROOT / 'build/expansion/probes' / name for name in
              ('combat.gba', 'combat.json')]
    private = ROOT / 'build/expansion/probes/fell-private/current.json'
    if private.is_file():
        paths.append(private)
        private_rom = pathlib.Path(json.loads(private.read_text())['path'])
        paths += [private_rom, private_rom.with_name('base.gba')]
    result = {}
    for path in sorted(set(paths)):
        key = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        result[key] = digest(path) if path.is_file() else None
    return result


def choose(plan, suite, only):
    steps = plan['steps']
    index = {s['id']: s for s in steps}
    if len(index) != len(steps):
        raise ValueError('Duplicate step IDs')
    requested = set(only or [s['id'] for s in steps if suite in s['suites']])
    unknown = requested - index.keys()
    if unknown:
        raise ValueError('Unknown steps: ' + ', '.join(sorted(unknown)))
    selected = set()
    visiting = set()

    def add(name):
        if name in selected:
            return
        if name in visiting:
            raise ValueError('Dependency cycle: ' + name)
        visiting.add(name)
        for dependency in index[name].get('requires', []):
            if dependency not in index:
                raise ValueError('Unknown dependency: ' + dependency)
            add(dependency)
        visiting.remove(name)
        selected.add(name)

    for name in requested:
        add(name)
    order = {s['id']: i for i, s in enumerate(steps)}
    for s in steps:
        for dependency in s.get('requires', []):
            if order[dependency] >= order[s['id']]:
                raise ValueError('Plan order violates dependency: ' + s['id'])
    return [s for s in steps if s['id'] in selected]


def xml_report(report, path):
    results = report['steps']
    changed = not report.get('inputsUnchanged', True)
    suite = ET.Element('testsuite', name='FFTA expansion ' + report['selection'],
                       tests=str(len(results) + int(changed)),
                       failures=str(sum(s['status'] == 'failed' for s in results) + int(changed)),
                       errors=str(sum(s['status'] in ('timed_out', 'error', 'interrupted') for s in results)),
                       skipped=str(sum(s['status'] == 'not_run' for s in results)),
                       time=str(round(sum(s.get('seconds', 0) for s in results), 3)))
    for step in results:
        case = ET.SubElement(suite, 'testcase', name=step['id'], classname=step['kind'],
                             time=str(round(step.get('seconds', 0), 3)))
        if step['status'] == 'not_run':
            ET.SubElement(case, 'skipped', message='Earlier step failed; not executed')
        elif step['status'] != 'passed':
            tag = 'failure' if step['status'] == 'failed' else 'error'
            ET.SubElement(case, tag, message=step.get('detail', step['status'])).text = step.get('log', '')
        if step.get('log'):
            ET.SubElement(case, 'system-out').text = step['log']
    if changed:
        case = ET.SubElement(suite, 'testcase', name='input-integrity', classname='runner')
        ET.SubElement(case, 'failure', message=report['failure'])
    ET.ElementTree(suite).write(path, encoding='utf-8', xml_declaration=True)


class WorkspaceLock:
    """OS lock releases on process exit; a leftover file is not a live lock."""
    def __enter__(self):
        self.stream = (RUNS / 'runner.lock').open('a+b')
        self.stream.seek(0)
        self.stream.write(b'0')
        self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise RuntimeError('Another expansion test runner owns this workspace') from None
        return self

    def __exit__(self, *args):
        self.stream.close()


def execute(plan, steps, selection):
    RUNS.mkdir(parents=True, exist_ok=True)
    with WorkspaceLock():
        stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        output = RUNS / stamp
        output.mkdir()
        report = dict(schema=1, status='running', selection=selection,
                      scope='Declared implemented-feature regression only; not expansion completion',
                      directory=str(output), inputs=source_identity(), steps=[], started=stamp)
        meta = json.loads((ROOT / 'build/expansion/probes/combat.json').read_text())
        report['romSha1'] = meta['romSha1']
        actual = hashlib.sha1((ROOT / 'build/expansion/probes/combat.gba').read_bytes()).hexdigest()
        if actual != report['romSha1']:
            raise ValueError('Combat ROM does not match its manifest')
        engine = (ROOT / 'build/expansion/engine.bin').read_bytes()
        report['engineSha1'] = hashlib.sha1(engine).hexdigest()
        if report['engineSha1'] != meta['engineSha1']:
            raise ValueError('Engine binary does not match the combat manifest; finish the build first')
        with (ROOT / 'build/expansion/probes/combat.gba').open('rb') as stream:
            stream.seek(0x1100000)
            if stream.read(len(engine)) != engine:
                raise ValueError('Combat ROM does not contain the declared engine')
        for step in steps:
            report['steps'].append(dict(id=step['id'], kind=step['kind'], status='not_run'))
        atomic_json(output / 'report.json', report)
        atomic_json(RUNS / 'latest.json', dict(report=str(output / 'report.json')))
        print(f'{selection}: {len(steps)} steps; ROM {actual}; reports {output}', flush=True)
        environment = dict(os.environ, PYTHONHASHSEED='0', PYTHONUNBUFFERED='1')
        environment.pop('PYTHONOPTIMIZE', None)  # Native checks use assertions.
        for i, (step, result) in enumerate(zip(steps, report['steps'])):
            tool = sys.executable if step['runtime'] == 'python' else shutil.which(step['runtime'])
            if not tool:
                result.update(status='error', detail='Missing runtime: ' + step['runtime'])
                break
            command = [tool, *step['args']]
            log = output / (f'{i + 1:03d}-' + step['id'] + '.log')
            result.update(command=command, log=str(log))
            start = time.monotonic()
            print(f'[{i + 1}/{len(steps)}] {step["id"]}', flush=True)
            try:
                with log.open('wb') as stream:
                    process = subprocess.run(command, cwd=ROOT, env=environment,
                                             stdout=stream, stderr=subprocess.STDOUT,
                                             timeout=step.get('timeoutSeconds', plan['timeoutSeconds']))
                result.update(status='passed' if process.returncode == 0 else 'failed',
                              exitCode=process.returncode)
            except subprocess.TimeoutExpired:
                result.update(status='timed_out', detail='Declared time limit exceeded')
            except KeyboardInterrupt:
                result.update(status='interrupted', detail='Execution interrupted')
            except OSError as error:
                result.update(status='error', detail=str(error))
            result['seconds'] = time.monotonic() - start
            print(f'  {result["status"]} ({result["seconds"]:.1f}s)', flush=True)
            atomic_json(output / 'report.json', report)
            if result['status'] != 'passed':
                print('Details: ' + str(log), flush=True)
                break
        report['inputsUnchanged'] = report['inputs'] == source_identity()
        passed = all(s['status'] == 'passed' for s in report['steps'])
        report['status'] = 'passed' if passed and report['inputsUnchanged'] else 'failed'
        if not report['inputsUnchanged']:
            report['failure'] = 'ROM, engine, source, or harness changed during the run'
        report['finished'] = dt.datetime.now(dt.timezone.utc).isoformat()
        atomic_json(output / 'report.json', report)
        xml_report(report, output / 'junit.xml')
        print(f'{report["status"]}: {output / "report.json"}', flush=True)
        return 0 if report['status'] == 'passed' else 1


def main():
    global PLAN
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', default='full')
    parser.add_argument('--plan', help='Workspace-relative deterministic test plan for an isolated job')
    parser.add_argument('--only', action='append', help='Named step plus declared prerequisites; repeatable')
    parser.add_argument('--list', action='store_true', help='List selection without running or writing')
    options = parser.parse_args()
    if options.plan:
        PLAN = (ROOT / options.plan).resolve()
        if not PLAN.is_relative_to(ROOT / 'scripts') or PLAN.suffix != '.json':
            parser.error('Test plans must be JSON files inside this workspace scripts directory')
    plan = json.loads(PLAN.read_text())
    steps = choose(plan, options.suite, options.only)
    if not steps:
        parser.error('Selection is empty')
    if options.list:
        for step in steps:
            print(step['id'] + ': ' + ' '.join([step['runtime'], *step['args']]))
        return 0
    return execute(plan, steps, 'selected' if options.only else options.suite)


if __name__ == '__main__':
    raise SystemExit(main())
