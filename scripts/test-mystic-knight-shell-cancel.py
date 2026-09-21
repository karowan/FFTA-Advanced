"""Fixed B-button cancellation and re-entry from a real second-spell preview."""
import pathlib,datetime,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
prior=max(p for p in pathlib.Path(meta['path']).parent.glob('shell-playback-*') if (p/'report.json').exists() and (p/'same-reaction/second-forecast.state').exists())
source=ROOT/'scripts/test-mystic-knight-shell-playback.py'
exec(compile(source.read_text(encoding='utf-8').split('e=E(TEST_ROM)\ntry:')[0],str(source),'exec'))
check('matching-instrumentation',TEST_ROM.read_bytes()==(prior/'playback.gba').read_bytes())
e=E(TEST_ROM);steps=[]
try:
 e.load(prior/'same-reaction/second-forecast.state');before=e.memory()
 check('actual-second-selection',before[0xf4e8+0xae]==1 and half(before,0xf4e8+0xdc)==49)
 for index in range(8):
  tap(e,1);r=checkpoint(e,'cancel-'+str(index),OUT)
  steps.append(dict(index=index,phase=half(r,0xf4e8+0xdc),selection=r[0xf4e8+0xae],command=half(r,0xf4e8+0xa6)))
  check('cancel-no-executor',word(r,LOG+4)==0)
  check('cancel-no-HP-MP-change',all(r[u+0x18:u+0x20]==before[u+0x18:u+0x20] for u in (ACTOR,TARGET)))
  check('cancel-no-live-Shell',not(r[TARGET+0xeb]&1))
  if observe['menu_visible'](e) and half(r,0xf4e8+0xdc)==37:break
 else:raise AssertionError(('cancel-did-not-return-to-menu',steps))
 check('cancel-retires-targeter',word(r,0xf4e8+0x60)==0)
 check('cancel-retires-continuation',owned(e)[2]==bytes(16))
 for index,key in enumerate((256,256,256,256,128,256)):
  tap(e,key);checkpoint(e,'reentry-'+str(index),OUT)
 r=checkpoint(e,'reentered-first-forecast',OUT)
 root=word(r,0xf440)-0x02000000;panel=word(r,root+8)-0x02000000
 value=struct.unpack_from('<h',r,panel+0x2e)[0]
 expected=json.loads((prior/'report.json').read_text())['outcomes'][1]['raw']
 check('reentry-is-first-selection',r[0xf4e8+0xae]==0 and half(r,0xf4e8+0xaa)==23 and half(r,0xf4e8+0xa6)==33)
 check('reentry-discards-old-pair-mitigation',value==expected)
 check('reentry-no-execution',word(r,LOG+4)==0)
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],source=str(prior),total=sum(checks.values()),checks=dict(checks),steps=steps,firstForecast=value)
(OUT/'cancel-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
