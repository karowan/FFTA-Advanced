"""Fixed native controls for the two concrete Bard acceptance failures."""
import pathlib,json,struct,runpy,ctypes as C
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-bard.py';ns={'__file__':str(source),'__name__':'diagnostic'}
exec(compile(source.read_text().split('# Native command flags')[0],str(source),'exec'),ns)
m,OUT=ns['m'],ns['OUT'];output=OUT/'bard-native-diagnostic';output.mkdir(exist_ok=True)
results=[]
for action in (11,23,396):
 for undead in (False,True):
  ns['setup'](action,1);ns['hp'](ns['ENEMY'],307,307)
  m.put(ns['ENEMY']+0x29,b'\x80');m.put(ns['ENEMY']+0xe8,bytes((4 if undead else 0,)))
  ns['execute'](action)
  results.append(dict(action=action,undead=undead,hp=ns['half'](ns['ENEMY']+0x18),result=m.read(ns['regs'][0],80).hex()))
(output/'damage.json').write_text(json.dumps(results,indent=2))
source=ROOT/'scripts/test-integrated-reaction-playback.py';ns={'__file__':str(source),'__name__':'diagnostic'}
exec(compile(source.read_text().split('for lesson,job,race,weapon,hidden in ')[0],str(source),'exec'),ns)
e=ns['E'](ns['TEST_ROM']);turns=[]
try:
 e.load(ns['FIX']/'battle-ready.state');e.run(1);ns['menu'](e);ns['fixed_giza_formation'](ns['image'],e)
 before=C.string_at(*e.maps[0x03000000]);(output/'before.iwram').write_bytes(before)
 for turn in range(4):
  previous=ns['active'](e)
  for key in (32,32,256,256):ns['tap'](e,key)
  error=None
  try:ns['menu'](e,previous)
  except AssertionError as ex:error=str(ex)
  after=C.string_at(*e.maps[0x03000000]);(output/f'wait-{turn}.iwram').write_bytes(after)
  e.save(output/f'wait-{turn}.state')
  diffs=[i for i in range(0x6000,0x6d28) if before[i]!=after[i]]
  turns.append(dict(turn=turn,previous=hex(previous),active=hex(ns['active'](e)),error=error,changes=[hex(x) for x in diffs]))
  if error:break
finally:e.close()
(output/'waits.json').write_text(json.dumps(turns,indent=2));print(json.dumps(dict(damage=results,waits=turns),indent=2))
