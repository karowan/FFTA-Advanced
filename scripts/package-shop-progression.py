"""Authenticate the shop candidate and its accepted AI parent for local release.

The exact shop ROM is packaged; no player save or running emulator is touched.
The earlier assembled/AI receipts apply to its byte-identical gameplay parent.
"""
import argparse
import hashlib
import json
from pathlib import Path

from mod_release import ROOT, bps, publish, sha


STEPS = ('shop-progression-native', 'shop-progression-ui', 'shop-progression-learning')
PARENT_SHA1 = '7bbd46a45bcaab5482d45cb4d4965bb291045512'
PARENT_RUNS = (
    'build/expansion/test-runs/20260928T020350.355777Z/report.json',
    'build/expansion/test-runs/20260928T020531.578106Z/report.json',
    'build/expansion/test-runs/20260928T015443.784886Z/report.json',
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=ROOT / 'scripts/mod-release.json')
    args = parser.parse_args()
    run = json.loads(args.run.read_text(encoding='utf-8'))
    assert run['status'] == 'passed' and run['inputsUnchanged']
    assert tuple(step['id'] for step in run['steps']) == STEPS
    assert all(step['status'] == 'passed' for step in run['steps'])

    manifest = Path(run['candidateManifest'])
    candidate = json.loads(manifest.read_text(encoding='utf-8'))
    target = Path(candidate['path'])
    raw = target.read_bytes()
    assert hashlib.sha1(raw).hexdigest() == run['romSha1'] == candidate['romSha1']
    assert sha(raw) == candidate['romSha256']
    shop = candidate['shopProgression']
    parent = json.loads(Path(shop['parent']).read_text(encoding='utf-8'))
    before = Path(parent['path']).read_bytes()
    assert hashlib.sha1(before).hexdigest() == parent['romSha1'] == shop['baseSha1'] == PARENT_SHA1
    assert len(before) == len(raw)
    for name, digest in shop['sources'].items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    allowed = set()
    for patch in shop['patches']:
        at = patch['offset']
        old, new = bytes.fromhex(patch['before']), bytes.fromhex(patch['after'])
        assert len(old) == len(new)
        assert before[at:at + len(old)] == old and raw[at:at + len(new)] == new
        allowed.update(range(at, at + len(new)))
    assert all(a == b or i in allowed for i, (a, b) in enumerate(zip(before, raw)))
    assert len(shop['prices']) == 95

    evidence = []
    for step in run['steps']:
        log = Path(step['log'])
        result = json.loads(log.read_text(encoding='utf-8').splitlines()[-1])
        assert result['passed'] is True and result['romSha1'] == candidate['romSha1']
        report_path = Path(result['report']) if 'report' in result else target.parent / 'learning/report.json'
        report = json.loads(report_path.read_text(encoding='utf-8'))
        assert report['passed'] is True and report['romSha1'] == candidate['romSha1']
        assert report_path.is_relative_to(target.parent)
        evidence.append(dict(id=step['id'], path=str(report_path), sha256=sha(report_path.read_bytes()),
                             log=str(log), logSha256=sha(log.read_bytes())))
    for name in PARENT_RUNS:
        path = ROOT / name
        report = json.loads(path.read_text(encoding='utf-8'))
        assert report['status'] == 'passed' and report['romSha1'] == PARENT_SHA1
        assert all(step['status'] == 'passed' for step in report['steps'])
        evidence.append(dict(id='parent-' + path.parent.name, path=str(path), sha256=sha(path.read_bytes())))

    config = json.loads(args.config.read_text(encoding='utf-8'))
    source = ROOT / config['baseRom']
    checks = target.parent / 'package-checks'
    checks.mkdir(exist_ok=True)
    first, second = checks / 'first.bps', checks / 'second.bps'
    bps('create', source, target, first)
    bps('create', source, target, second)
    assert first.read_bytes() == second.read_bytes(), 'Non-deterministic patch'
    restored = checks / 'roundtrip.gba'
    bps('apply', source, first, restored)
    assert restored.read_bytes() == raw, 'Clean-ROM patch roundtrip differs'
    wrong = checks / 'wrong-source.gba'
    bad = bytearray(source.read_bytes())
    bad[-1] ^= 1
    wrong.write_bytes(bad)
    try:
        bps('apply', wrong, first, checks / 'must-not-accept.gba')
    except AssertionError:
        pass
    else:
        raise AssertionError('Wrong source accepted')
    evidence.append(dict(id='clean-base-bps-validation', path=str(first), sha256=sha(first.read_bytes())))

    package = publish(candidate, args.run, evidence, args.config)
    receipt = Path(package['archive']).parent / 'local-build-receipt.json'
    receipt.write_text(json.dumps(dict(package=package, run=str(args.run.resolve()),
                                       runSha256=sha(args.run.read_bytes()), evidence=evidence,
                                       scope='Local shop and AI follow-up release; parent gameplay receipts are retained.'),
                            indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status='passed', romSha1=candidate['romSha1'],
                          archive=package['archive'], report=str(receipt))))


if __name__ == '__main__':
    main()
