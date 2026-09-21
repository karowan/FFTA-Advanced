"""Deterministic native Pick Abilities choice, cancellation and saved preference."""
import pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/diagnose-auto-potion-menu.py'
exec(compile(source.read_text(encoding='utf-8').split('e=E(ROM)')[0],str(source),'exec'))
checks=collections.Counter()
def check(k,v):
 checks[k]+=1
 assert v,(k,case,steps[-1] if steps else None)
def cold(e,seed):
 e.set_memory(0,seed,0);e.run(3600)
 for key in (8,256,256,256):tap(e,key)
def rows(e):
 r=e.memory();ctx=word(C.string_at(*e.maps[0x03000000]),0x2818)-0x02000000
 p=word(r,ctx+0x2d50)-0x02000000
 assert 0<=p<=0x40000-0x2700
 n=word(r,p);assert n<=460
 return [r[p+0x230+20*i:p+0x230+20*(i+1)] for i in range(n)]
def choose(e,index):
 for _ in range(index):tap(e,32)
def named(row):return word(row,8)
outcomes=[]
for race,ap_count,lesson in ((3,124,121),(5,116,100)):
 case=(race,'setup');e=E(ROM)
 try:
  cold(e,(ROOT/'build/test-lab/early-town.sav').read_bytes())
  r=e.memory();slot=next(i for i in range(6) if r[0x80+264*i+6]==race);unit=0x80+264*slot
  e.set_memory(unit+0x40,bytes([228])*ap_count)
  before=e.memory();capture(e,f'{race}-town')
  keys=[8,256]+([32] if slot>=4 else [])+[128]*(slot%4)+[256,32,256,32,256]
  for key in keys:tap(e,key)
  capture(e,f'{race}-list');rr=rows(e);indexes=[i for i,row in enumerate(rr) if row[14]==lesson]
  check('two-real-reaction-rows',len(indexes)==2 and indexes[1]==indexes[0]+1)
  check('native-AP-help-preserved',rr[indexes[0]][12:15]==rr[indexes[1]][12:15])
  check('distinct-visible-labels',named(rr[indexes[0]])!=named(rr[indexes[1]]))
  check('default-Potion',e.memory()[0x1e80+slot]==0)
  original_names=[named(rr[i]) for i in indexes]
  choose(e,indexes[1]);capture(e,f'{race}-hi-before-cancel');tap(e,1)
  check('cancel-keeps-preference',e.memory()[0x1e80:0x1e98]==before[0x1e80:0x1e98])
  check('cancel-keeps-reaction',e.memory()[unit+0x3a]==before[unit+0x3a])
  tap(e,256);choose(e,indexes[1]);capture(e,f'{race}-hi-before-confirm');tap(e,256)
  capture(e,f'{race}-hi-confirmed')
  check('confirmed-Hi-Potion',e.memory()[0x1e80+slot]==1)
  check('same-native-reaction-lesson',e.memory()[unit+0x3a]==lesson)
  check('other-preferences-unchanged',e.memory()[0x1e80:0x1e80+slot]+e.memory()[0x1e81+slot:0x1e98]==before[0x1e80:0x1e80+slot]+before[0x1e81+slot:0x1e98])
  check('selection-consumes-no-stock',e.memory()[0x1940:0x1b40]==before[0x1940:0x1b40])
  check('selection-preserves-AP',e.memory()[unit+0x40:unit+0x40+ap_count]==before[unit+0x40:unit+0x40+ap_count])
  tap(e,256);capture(e,f'{race}-hi-reopened');rr=rows(e)
  check('saved-choice-visibly-marked',all(named(rr[i])!=old for i,old in zip(indexes,original_names)))
  tap(e,1)
  for key in (1,1,1):tap(e,key)
  if '--menu-only' in sys.argv:
   outcomes.append(dict(race=race,slot=slot,indexes=indexes,scope='Actual relocated list, cancel, confirm, reopen and world return; no cold-save replay'))
   continue
  for key in (8,16,256,256,256,64,256):tap(e,key)
  e.run(600);saved=e.memory(0);expected=e.memory()[0x1e80:0x1e98]
  (OUT/f'{race}-saved.sav').write_bytes(saved);capture(e,f'{race}-saved')
 finally:e.close()
 case=(race,'cold-reload');e=E(ROM)
 try:
  cold(e,saved);capture(e,f'{race}-reloaded')
  check('cold-save-preserves-choice',e.memory()[0x1e80:0x1e98]==expected and expected[slot]==1)
  for key in keys:tap(e,key)
  capture(e,f'{race}-cold-list');choose(e,indexes[0]);tap(e,256)
  capture(e,f'{race}-Potion-confirmed')
  check('confirmed-Potion',e.memory()[0x1e80+slot]==0 and e.memory()[unit+0x3a]==lesson)
  outcomes.append(dict(race=race,slot=slot,indexes=indexes))
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,steps=steps,output=str(OUT))
(OUT/'preference-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='steps'},indent=2))
