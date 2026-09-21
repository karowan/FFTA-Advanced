"""Bounded runner/retention checks. No emulator or player data is used."""
import ctypes as C
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import uuid
from contextlib import contextmanager
from unittest.mock import patch
import resource_guard as guard

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pruner', ROOT/'scripts/prune-build-outputs.py')
pruner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pruner)
checks = []
def check(value, name):
    assert value, name
    checks.append(name)

def rejects(call, name):
    try:
        call()
    except (ValueError, OSError):
        checks.append(name)
    else:
        raise AssertionError(name)

for value in ('0', '-1', 'nan', 'inf'):
    with patch.dict(os.environ, {'FFTA_STEP_MEMORY_LIMIT_GB': value}):
        rejects(lambda: guard.setting('FFTA_STEP_MEMORY_LIMIT_GB'), 'reject limit '+value)
code, peak = guard.run_contained([sys.executable, '-c', 'raise SystemExit(7)'], 10)
check(code == 7 and peak > 0, 'contained exit and memory accounting')
with patch.object(guard.ContainedProcess, '_create_job', side_effect=OSError('injected')):
    with patch.object(subprocess, 'Popen') as spawn:
        rejects(lambda: guard.ContainedProcess([sys.executable]), 'job setup fails closed')
        check(not spawn.called, 'no child starts before job creation')

output = ROOT/'build/resource-tooling'
output.mkdir(parents=True, exist_ok=True)
@contextmanager
def fixture_directory():
    # Normal inherited ACLs are required by sandboxed descendant processes;
    # Python's Windows private-temp ACL can exclude their restricted identity.
    path = output/('fixture-'+uuid.uuid4().hex)
    path.mkdir()
    yield path

with fixture_directory() as temporary:
    base = pathlib.Path(temporary)
    pidfile = base/'child.pid'
    program = ('import subprocess,sys,pathlib,time; '
               'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); '
               'pathlib.Path(sys.argv[1]).write_text(str(p.pid)); time.sleep(30)')
    with guard.ContainedProcess([sys.executable, '-c', program, str(pidfile)],
                                memory_limit_bytes=256*1024**2) as process:
        import time
        deadline = time.monotonic()+5
        while not pidfile.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        check(pidfile.exists(), 'contained child created descendant')
        kernel = C.windll.kernel32
        kernel.OpenProcess.restype = C.c_void_p
        handle = kernel.OpenProcess(0x100000, False, int(pidfile.read_text()))
        check(bool(handle), 'descendant initially alive')
        try:
            try:
                process.wait(.05)
                raise AssertionError('expected timeout')
            except subprocess.TimeoutExpired:
                process.terminate_tree()
            check(kernel.WaitForSingleObject(C.c_void_p(handle), 5000) == 0,
                  'timeout terminates descendant')
        finally:
            kernel.CloseHandle(C.c_void_p(handle))
    with guard.ContainedProcess([sys.executable, '-c', 'x=bytearray(256*1024**2)'],
                                memory_limit_bytes=96*1024**2,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as process:
        check(process.wait(10) != 0, 'memory ceiling rejects excess allocation')

    sandbox = base/'sandbox'
    probes = sandbox/'build/expansion/probes'
    repro = sandbox/'build/reproducibility'
    stale = probes/'example'/('a'*40)
    stale.mkdir(parents=True)
    capture = stale/'test.ram'; capture.write_bytes(b'fixture')
    report = stale/'report.json'; report.write_text('{}')
    with patch.multiple(pruner, ROOT=sandbox, PROBES=probes, REPRODUCIBILITY=repro):
        plan = {'bytes': 0, 'files': 0, 'reasons': {}}
        pruner.remove_files(stale, pruner.CAPTURES, plan, True, 'test')
        check(capture.exists() and plan['files'] == 1, 'dry run preserves capture')
        rejects(lambda: pruner.checked_path(base/'outside.ram'), 'outside path rejected')
        rejects(lambda: pruner.checked_path(probes), 'output root itself rejected')
        with patch.object(pathlib.Path, 'is_junction', lambda p: p == stale):
            rejects(lambda: pruner.remove_files(stale, pruner.CAPTURES, plan, False, 'test'),
                    'junction target rejected before removal')
        check(capture.exists(), 'rejected junction preserves file')
        pruner.remove_files(stale, pruner.CAPTURES, plan, False, 'test')
        check(not capture.exists() and report.exists(), 'only selected fixture capture removed')
result = subprocess.run([sys.executable, str(ROOT/'scripts/rebuild-expansion.py'),
                         '--keep-workspace', '--help'], capture_output=True)
check(result.returncode == 0, 'keep-workspace parses without starting a build')
result = {'passed': True, 'checks': checks, 'scope': __doc__}
(output/'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result))
