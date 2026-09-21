"""Additive theft-family laws without changing command ownership or loot."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-carrier-category-laws.py'
exec(compile(source.read_text().split('\nweapon_actions=')[0],str(source),'exec'))
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
observations=[]
for action in range(347,432):
 owner=next(l for l in registry['lessons'] if l['globalAbilityId']==action and l['type']=='Action')['owners'][0]
 for family,residue in itertools.product(range(1,33),(0,4)):
  case=('native-command-family',action,family,residue);fixture(action)
  ns['job'](A,owner['race'],owner['jobId'])
  command=8 if owner['jobId']==16 else owner['jobId'];m.put(A+0x35,bytes((command,)))
  check('real-command-identity-retained',m.call(0x08133d78,A,action,stack=STACK),command)
  want=family==command or (family==23 and action in (366,367,370))
  check('native-command-family-law',law(action,1,family,residue=residue),int(want))
  check('movement-not-theft',law(action,1,family,move=1,residue=residue),0)
# Actual transactions retain misses, depleted targets and independent damage.
for action,item,seed in itertools.product((366,367,370),(0,288,302,354),range(8)):
 case=('actual-theft-law',action,item,seed);fixture(action,seed);ns['job'](A,2,118)
 m.put(A+0x2a,struct.pack('<5H',399,0,0,0,0));m.put(T+0x2a,struct.pack('<5H',item,0,0,0,0))
 execute(action);native_rows=rows(action,T)
 for _,_,row in native_rows:
  flags=half(row+12)
  check('executed-theft-family',law(action,1,23,mask=row+0x14),1)
  check('executed-theft-preserves-Reaving',law(action,1,118,mask=row+0x14),1)
  m.put(0x08529348,b'\x01\x17');m.put(STACK,struct.pack('<II',0,row+0x14))
  check('native-late-theft-family',m.call(0x08135750,A,T,action,0,stack=STACK),1)
  stolen=bool(item and not half(T+0x2a));damage=500-half(T+0x18)
  if stolen:check('successful-theft-survives-native-late-gate',bool(flags&128) and not bool(flags&64),True)
  observations.append(dict(action=action,item=item,seed=seed,stolen=stolen,damage=damage,flags=flags))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),observations=observations)
(OUT/'carrier-theft-laws.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='observations'},indent=2))
