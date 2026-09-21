"""Freeze existing acceptance evidence and verify its applicability; no game replay."""
import hashlib
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
ROM_SHA1 = '1b070824a8dad4995434eee3ab40fa08187a6120'
def sha(path, algorithm='sha256'):
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))
manifest = read(ROOT/'build/expansion/probes/integrated-jobs/current.json')
rom = pathlib.Path(manifest['path'])
assert manifest['romSha1'] == sha(rom, 'sha1') == ROM_SHA1
clean_report = ROOT/'build/reproducibility/20260917T094234.898388Z/report.json'
assert sha(clean_report) == '03e00e8fe7ce891bdffba127780d2e28c248ee02580569457aa4030c714d2386'
rebuild = read(clean_report)
assert rebuild['passed'] and rebuild['byteIdentical']
assert rebuild['result']['romSha256'] == sha(rom)
# All current shipping source and current builder inputs remain exactly those
# of the independent clean rebuild. Test/docs/resource tooling may evolve.
shipping = {n: h for n, h in rebuild['sources'].items() if n.startswith('src/') or
            n.startswith('scripts/build-') or
            (n.startswith('scripts/jobs/') and pathlib.Path(n).name == 'build.py') or
            n == 'scripts/engine_bootstrap_source.py'}
assert all(sha(ROOT/n) == h for n, h in shipping.items()), 'Shipping source drift'
assert {p.relative_to(ROOT).as_posix() for p in (ROOT/'src').rglob('*') if p.is_file()} == {
    n for n in shipping if n.startswith('src/')}, 'Shipping source inventory drift'
changes = subprocess.check_output(['git','diff','--name-only','2e32b3a','HEAD','--',
    'src','scripts/build*','scripts/jobs/*/build.py'], cwd=ROOT, text=True).splitlines()
assert sorted(changes) == ['src/engine/geomancer-compositor.c','src/engine/geomancer-renderer.c']
checklist = (ROOT/'IMPLEMENTATION-CHECKLIST.md').read_text(encoding='utf-8')
open_gates = re.findall(r'- \[ \] \*\*([A-Z]\d+)', checklist)
assert set(open_gates) <= {'R02', 'R03'}, open_gates
notes = sorted(set(re.findall(r'`(notes/[\w-]+\.md)`', checklist)))
notes += ['notes/resource-tooling-review.md','notes/release-acceptance.md']
note_hashes = {n: sha(ROOT/n) for n in sorted(set(notes))}
# These exact reports close the changes since the accepted broad job/Combo/
# roster checkpoint and the campaign/ending/clear-save delivery boundary.
reports = {
 'geomancer-renderer-report.json': 'ec1b275077cce434a98e04ee21a184004f1cc8bc',
 'geomancer-playback/report.json': 'ab22eceb90bd952dca1d60fd9e7489f945135deb',
 'geomancer-field-lifecycle/report.json': 'b009d5f044fc8034f74bb26d3e07b03e86a4ec47',
 'geomancer-mixed-playback/report.json': 'daf84a6c47cb83dc3b145c3e221493dd8be8bfbb',
 'campaign-progression-20260917T083905.312061Z/report.json': '8f5325761e1604d2a0c61af665014570cc9eec1f',
 'territory-scenes-20260917T122700.200984Z/report.json': '17471033eb3011b057f9bcc3736fea312d87d4e3',
 'final-condition-20260917T122148.917904Z/report.json': '8da6af9e007e468d6c4a1d94df251b32f9c4ee96',
 'final-departure-20260917T122400.314767Z/report.json': '04ed1fc1849ec463e031d9e22e7f10462e19bf2b',
 'ending-scenes-20260917T110459.056443Z/report.json': '13e138e2c9fc9ab977c4087afb71e293959bbd09',
 'final-battle-bridge-20260917T111936.326292Z/report.json': 'ac0a0981e8ce9cf8ad4598e5c4c442b577e89644',
 'shara-scene-20260917T113132.588453Z/report.json': '261d5cfe666f296fec668444462bf2b642cb05cd',
 'shara-scene-20260917T113427.606778Z/report.json': '82d4dc3840021d8637cc6b4fb8803d0fcacb6d9e',
}
frozen = {}
for name, expected in reports.items():
    path = rom.parent/name
    assert sha(path, 'sha1') == expected, ('Acceptance report drift', name)
    report = read(path)
    assert report.get('passed') is True, ('Report is not a complete pass', name)
    frozen[path.relative_to(ROOT).as_posix()] = sha(path)
for stamp in ('20260917T080703.856021Z','20260917T080830.023332Z',
              '20260917T094234.326368Z','20260917T122656.766531Z',
              '20260917T124457.556144Z'):
    path = ROOT/'build/expansion/test-runs'/stamp/'report.json'
    report = read(path)
    assert report['status'] == 'passed' and report['inputsUnchanged'], stamp
    frozen[path.relative_to(ROOT).as_posix()] = sha(path)
    for step in report['steps']:
        if step.get('log'):
            log = pathlib.Path(step['log'])
            frozen[log.relative_to(ROOT).as_posix()] = sha(log)
result = {'passed': True, 'romSha1': ROM_SHA1, 'romSha256': sha(rom),
          'sourceCommit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'shippingSources': shipping, 'cleanRebuildReportSha256': sha(clean_report),
          'reusedEvidenceNotes': note_hashes, 'frozenReportsAndLogs': frozen,
          'shippingChangesSinceBroadJobAcceptance': changes,
          'scope': 'Root-reviewed union of scoped acceptance; no full-suite rerun or uninterrupted campaign claim.'}
output = ROOT/'build/release-acceptance.json'
output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed': True,'romSha1':ROM_SHA1,'shippingSources':len(shipping),
                  'evidenceNotes':len(note_hashes),'reportsAndLogs':len(frozen), 'report':str(output)}))
