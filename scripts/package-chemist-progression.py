"""Authenticate the complete new-job gate before promoting a LOCAL package.

This never uploads anything. The intermediate builders intentionally continue
to call their files test-only; this adapter owns the playable acceptance gate.
Player saves are not opened or copied. The stable launcher keeps their path.
"""
import argparse,hashlib,json
from pathlib import Path
from mod_release import ROOT,bps,publish,sha

STEPS=('cp-state-codec','cp-effects','cp-fixture','cp-periodic','cp-movement',
       'cp-ai','cp-save','cp-ui','cp-learning','cp-laws','cp-status-records')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True)
 parser.add_argument('--config',type=Path,default=ROOT/'scripts/mod-release.json')
 args=parser.parse_args();run=json.loads(args.run.read_text())
 assert run['status']=='passed' and run['inputsUnchanged']
 assert tuple(s['id'] for s in run['steps'])==STEPS
 assert all(s['status']=='passed' for s in run['steps'])
 manifest=Path(run['candidateManifest']);candidate=json.loads(manifest.read_text())
 assert candidate['romSha1']==run['romSha1']
 for name,digest in run['candidateInputs'].items():assert sha((ROOT/name).read_bytes())==digest
 evidence=[]
 for step in run['steps']:
  p=Path(step['log'])
  result=json.loads((Path(candidate['path']).parent/'fixture/report.json').read_text()) if step['id']=='cp-fixture' else json.loads(p.read_text().splitlines()[-1])
  assert result.get('passed') is True
  if 'report' in result:result=json.loads(Path(result['report']).read_text())
  # The independent codec test uses a purpose-built ARM image. Every other
  # gate must execute this exact assembled candidate, not a prior probe.
  if step['id']!='cp-state-codec':assert result['romSha1']==candidate['romSha1']
  evidence.append(dict(id=step['id'],path=str(p),sha256=sha(p.read_bytes())))
 code=json.loads((ROOT/'build/expansion/chemist-progressions/code/manifest.json').read_text())
 for group in ('sourceSha256','headerSha256'):
  for name,digest in code[group].items():assert sha((ROOT/name).read_bytes())==digest, name
 target=Path(candidate['path']);raw=target.read_bytes()
 assert hashlib.sha1(raw).hexdigest()==candidate['romSha1']
 candidate['romSha256']=sha(raw)
 config=json.loads(args.config.read_text());source=ROOT/config['baseRom']
 checks=target.parent/'package-checks';checks.mkdir(exist_ok=True)
 first,second=checks/'first.bps',checks/'second.bps'
 bps('create',source,target,first);bps('create',source,target,second)
 assert first.read_bytes()==second.read_bytes(),'Non-deterministic patch'
 restored=checks/'roundtrip.gba';bps('apply',source,first,restored)
 assert restored.read_bytes()==raw,'Clean-ROM patch roundtrip differs'
 wrong=checks/'wrong-source.gba';bad=bytearray(source.read_bytes());bad[-1]^=1;wrong.write_bytes(bad)
 try:bps('apply',wrong,first,checks/'must-not-accept.gba')
 except AssertionError:pass
 else:raise AssertionError('Wrong source accepted')
 evidence.append(dict(id='clean-base-bps-validation',path=str(first),sha256=sha(first.read_bytes())))
 package=publish(candidate,args.run,evidence,args.config)
 receipt=Path(package['archive']).parent/'local-build-receipt.json'
 receipt.write_text(json.dumps(dict(package=package,run=str(args.run.resolve()),
  runSha256=sha(args.run.read_bytes()),evidence=evidence,
  scope='Local first playable balance pass; no upload, launch or campaign completion claim.'),indent=2)+'\n')
 print(json.dumps(dict(status='passed',romSha1=candidate['romSha1'],archive=package['archive'],report=str(receipt))))

if __name__=='__main__':main()
