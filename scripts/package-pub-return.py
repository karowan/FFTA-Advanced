"""Authenticate the focused pub return run and package v0.7.4."""
import argparse
import hashlib
import json
from pathlib import Path
from mod_release import publish

ROOT = Path(__file__).resolve().parents[1]
STEPS = ('build-pub-return', 'test-pub-return')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def last(path):
    return json.loads(Path(path).read_text().splitlines()[-1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--config', type=Path, default=ROOT / 'scripts/mod-release.json')
    args = parser.parse_args()
    run = json.loads(args.run.read_text())
    assert run['status'] == 'passed' and run['inputsUnchanged']
    assert tuple(step['id'] for step in run['steps']) == STEPS
    assert all(step['status'] == 'passed' for step in run['steps'])
    build, test_output = (last(step['log']) for step in run['steps'])
    test = json.loads(Path(test_output['report']).read_text())
    candidate = json.loads(Path(build['manifest']).read_text())
    assert build['status'] == test['status'] == 'passed'
    assert build['romSha1'] == candidate['romSha1']
    assert test['cases'][2]['romSha1'] == candidate['romSha1']
    assert test['cases'][0]['returnHeaderSha256'] == test['cases'][2]['returnHeaderSha256']
    assert test['cases'][0]['returnHeaderSha256'] != test['cases'][1]['returnHeaderSha256']
    assert sha(Path(candidate['path'])) == candidate['romSha256']
    assert sha(Path(candidate['pubReturn']['parent'])) == candidate['pubReturn']['parentSha256']
    assert candidate['pubReturn']['changedBytes'] == [0x5D76C]
    evidence = [dict(id=step['id'], path=step['log'], sha256=sha(Path(step['log']))) for step in run['steps']]
    package = publish(candidate, args.run, evidence, args.config)
    receipt = Path(package['archive']).parent / 'local-build-receipt.json'
    receipt.write_text(json.dumps(dict(package=package, run=str(args.run.resolve()),
                                       runSha256=sha(args.run), evidence=evidence), indent=2) + '\n')
    print(json.dumps(dict(status='passed', romSha1=candidate['romSha1'], archive=package['archive'],
                          patchBytes=package['patchBytes'], report=str(receipt))))


if __name__ == '__main__':
    main()
