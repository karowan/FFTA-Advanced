"""Bounded native mixed-pair audit, including first healing/buff applications."""
import pathlib,json,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-shell-menu.py'
exec(compile(source.read_text(encoding='utf-8').split('# The first confirmed cross')[0],str(source),'exec'))
rows=[]
for first in (1,2,3,52,53,55,68,8,12,73):
 pair=[]
 for enabled in (False,True):
  case=(first,enabled);q=configure(first,23,5,99,255,enabled,False,'normal')
  raw_first=invoke(first,'generic');context=m.read(0x0200f3f0,52);descriptor=m.read(m.word(0x0200f420),4).hex()
  preview=invoke(23);outputs=[];states=[]
  for index in (0,1):
   outputs.append(ns['cast'](index));states.append(dict(hp=half(T+0x18),shell=bool(m.read(T+0xeb,1)[0]&1)))
  ns['finish']();ns['dispose'](outputs);release(q)
  pair.append(dict(enabled=enabled,firstForecast=raw_first,firstDescriptor=descriptor,secondForecast=preview,states=states))
 rows.append(dict(first=first,pair=pair))
# Independent native ordinary-Shell controls at the projected decision HP.
# These are exact average forecast comparisons, not claims about future RNG.
for first,center,mp,hp,condition,residue in itertools.product((1,2,3,52,53,68),(5,9),(11,99),(100,255,270,490),('normal','ward'),(0,4)):
 case=('heal-threshold',first,center,mp,hp,condition,residue)
 q=configure(first,23,center,mp,hp,False,False,condition)
 healing=invoke(first,'generic');raw=invoke(23,'generic')
 costs=m.call(0x0812ed98,A,first,stack=STACK)+m.call(0x0812ed98,A,23,stack=STACK)
 projected=min(500,hp+max(0,-healing)) if center==5 and mp>=costs else hp
 expected=raw>0 and 2*(projected-raw)<=500
 release(q)
 q=configure(first,23,center,mp,hp,False,expected,condition);oracle=invoke(23,residue=residue);release(q)
 q=configure(first,23,center,mp,hp,True,False,condition)
 before=live();controller=m.read(B,0x140);code=m.read(0x03006170,0xbf8)
 check('prior-heal-native-threshold',invoke(23,residue=residue),oracle)
 check('prior-heal-live-state-RNG-pure',live(),before)
 check('prior-heal-controller-pure',m.read(B,0x140),controller)
 check('prior-heal-code-preserved',m.read(0x03006170,0xbf8),code)
 check('prior-heal-roots-retired',m.read(0x0203ff44,8),bytes(8));release(q)
# The observed255-HP actual controls are comfortably outside variance ambiguity.
for row in rows:
 if row['first'] in (1,2,3,52,53,68):
  check('heal-first-does-not-predict-Shell',row['pair'][1]['secondForecast'],row['pair'][0]['secondForecast'])
  check('heal-first-actual-no-Shell',row['pair'][1]['states'],row['pair'][0]['states'])
 if row['first'] in (8,12,73):
  check('buff-first-actual-results-preserved',row['pair'][1]['states'],row['pair'][0]['states'])
# Positive-hit buff/reflect controls: first Shell must not gain a second
# application, and original reflection/target routing stays native.
buff_rows=[]
for first,seed in itertools.product((8,12,73),(0,3,18)):
 pair=[]
 for enabled in (False,True):
  case=('first-buff',first,seed,enabled);q=configure(first,23,5,99,255,enabled,False,'normal')
  m.put(0x030034b0,struct.pack('<I',seed));outputs=[]
  for index in (0,1):outputs.append(ns['cast'](index))
  ns['finish']();ns['dispose'](outputs);release(q)
  pair.append(dict(targetHP=half(T+0x18),actorHP=half(A+0x18),statuses=m.read(T+0xdd,19).hex(),
   grants=len(ns['grants']),rng=m.read(0x030034b0,4).hex()))
 check('first-buff-reaction-does-not-change-native-results',pair[1],pair[0])
 if first in (8,12):check('first-buff-no-Shell-refresh',pair[1]['grants'],1)
 buff_rows.append(dict(first=first,seed=seed,pair=pair))
check('nonvacuous-first-buff-followed-by-damage',any(x['first'] in (8,12) and x['pair'][0]['targetHP']<255 for x in buff_rows),True)
report=dict(passed=not failures,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),failures=failures,rows=rows,buffRows=buff_rows,
 scope='Pure mixed-spell HP forecast with original native healing; actual non-damage buff controls retain native outcome rules')
(OUT/'mystic-knight-shell-mixed.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=not failures,romSha1=meta['romSha1'],total=report['total'],failureCounts=dict(collections.Counter(x['check'] for x in failures)),failures=failures[:6]),indent=2));assert not failures
