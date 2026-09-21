"""Fixed real Nu Mou inputs through all Geomancy rows, forecasts and casts.

The private ROM supplies one declared all-material tile to distinguish Move's
old and new neighborhoods. Production terrain is tested by terrain-campaign.
No menu choice, combat result, damage, status or animation is injected.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
support=support.replace("OUT=LAB/'reaction-playback'","OUT=LAB/'geomancer-playback'")
support=support.replace('log[0]=0x504c4159;', 'log[33]=mode;log[34]=(unsigned)out;log[0]=0x504c4159;')
exec(compile(support,'<shared deterministic playback>','exec'))
ACTOR,TARGET,SECOND=0x4a0,0x33e4,0x2fc4
instrumented[0x11f0000+70*256:0x11f0000+71*256]=bytes(256)
instrumented[0x11f0000+70*256+12*16]=31
TEST_ROM.write_bytes(instrumented)
costs={374:4,375:6,376:8,377:8,378:10,379:10,380:12,381:18,382:12}
rows=[(374,0),(375,0)]+[(376,c) for c in (1,2,3,4)]+[(a,0) for a in (377,378,379,380)]+[(381,c) for c in (2,3,4,1,5)]+[(382,0)]
failures=[]

def mode(e):
 r=e.memory();return r[word(r,0xf438)-0x02000000+4]

def checkpoint(e,label,folder):
 r=capture(e,label,folder)
 check('native-code-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
 return r

def formation(e,wrappers):
 # Keep each sprite's actual race. Formation changes are inputs before Move.
 for unit,x,y,height in ((ACTOR,0,14,16),(TARGET,1,13,32),(SECOND,1,14,16),
                         (0x290,2,12,32),(0x398,3,12,32),(0x5a8,1,15,16)):
  e.set_memory(unit+0xf6,bytes((x,y)))
  e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))

e=E(TEST_ROM)
try:
 e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
 check('real-Nu-Mou',e.memory()[ACTOR+6]==3)
 check('declared-Giza-map',half(e.memory(),0x7f10)==70)
 for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x79')
 e.set_memory(ACTOR+8,b'\x00');e.set_memory(ACTOR+0x36,bytes(2))
 e.set_memory(ACTOR+0x40,bytes(0x90))
 for lesson in registry['lessons']:
  if lesson['id'].startswith('GEO-A'):
   index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==3)
   e.set_memory(ACTOR+0x40+index,b'\xff')
 for unit in (ACTOR,TARGET,SECOND):
  e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100))
  e.set_memory(unit+0xe8,bytes(8));e.set_memory(unit+0x20,struct.pack('<4H',70,40,40,40))
  e.set_memory(unit+0x3a,bytes(2))
 e.set_memory(ACTOR+0x2a,bytes(10))
 wrappers=from_emulator(image,e);formation(e,wrappers)
 for turn in range(16):
  if active(e)==0x02000000+ACTOR:break
  previous=active(e)
  for key in (32,32,256,256):tap(e,key)
  menu(e,previous)
 check('native-Nu-Mou-turn',active(e)==0x02000000+ACTOR)
 wrappers=from_emulator(image,e);formation(e,wrappers)
 for unit in (ACTOR,TARGET,SECOND):
  e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100));e.set_memory(unit+0xe8,bytes(8))
 e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
 r=checkpoint(e,'start',OUT)
 grid=word(r,0x7f14)-0x02000000
 check('old-and-new-neighborhoods-no-native-water',not any(r[grid+2*(16*y+x)+1]&2 for x,y in ((0,14),(1,14),(0,15),(0,13),(1,13),(0,12))))
finally:e.close()

casts=[(row,action,choice,False) for row,(action,choice) in enumerate(rows)]+[(9,380,0,True),(15,382,0,True)]
if '--fields-only' in sys.argv:casts=[c for c in casts if c[1] in (380,382)]
display_checks='--display-checks' in sys.argv
if display_checks:
 from geomancer_render_observation import observe as observe_field_display
seeds=(0,) if '--seed-zero' in sys.argv else (0,3,18)
for row,action,choice,empty in casts:
 for seed in seeds:
  case=('Geomancy-player',action,choice,seed,empty);folder=OUT/str(action)/str(choice)/('empty' if empty else 'occupied')/str(seed)
  folder.mkdir(parents=True,exist_ok=True);e=E(TEST_ROM)
  try:
   e.load(OUT/'start.state');e.run(1)
   friendly=action in (377,378)
   for unit in (TARGET,SECOND):e.set_memory(unit+0x29,bytes((0 if friendly else 128,)))
   center=(2,12) if empty else (1,13)
   if empty:
    for unit,x,y in ((0x290,4,14),(0x398,4,13),(0x80,5,14)):
     e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,32,y*32+16))
    r=e.memory()
    check('declared-empty-cross',all(abs(r[u+0xf6]-2)+abs(r[u+0xf7]-12)>1 for u in wrappers))
   # Native Move travels from0,14 to0,13. The material at0,12 only enters the
   # sensed neighborhood after that move; the unit's F6/F7 are still deferred.
   for key in (256,16,256):tap(e,key)
   menu(e) # Observe completed native Move before submitting Act.
   moved=checkpoint(e,'native-movement',folder);w=wrappers[ACTOR]
   check('native-Move-displayed-tile',(half(moved,w+8)//32,half(moved,w+12)//32)==(0,13))
   check('Move-reproduces-deferred-unit-position',moved[ACTOR+0xf6:ACTOR+0xf8]==bytes((0,14)))
   for key in (256,32,256):tap(e,key)
   before_rows=checkpoint(e,'choices',folder)
   check('native-command-mode',mode(e) in (6,7,8))
   for _ in range(row):tap(e,32)
   tap(e,256);selected=checkpoint(e,'targeting',folder)
   manager=word(selected,0xf438)-0x02000000
   check('player-selected-action',word(selected,manager+20)==action)
   if choice:check('player-selected-choice',half(selected,manager+16)==choice)
   check('menu-learning-read-only',selected[ACTOR+0x40:ACTOR+0xd0]==before_rows[ACTOR+0x40:ACTOR+0xd0])
   # Both single-target commands and crosses begin at the caster's cursor.
   # The declared Right input selects the native center/target at1,13.
   tap(e,128)
   if empty:
    tap(e,128);tap(e,16)
   for confirmation in range(3):
    if mode(e)==11:break
    tap(e,256)
   before=checkpoint(e,'confirmation',folder)
   check('native-final-confirmation',mode(e)==11)
   check('no-premature-execution',word(before,LOG+4)==0)
   if not empty:check('forecast-action',half(before,0xf3fc)==action)
   if choice:check('forecast-choice',half(before,0xf3fe)==choice)
   e.set_memory(LOG+148,struct.pack('<II',1,seed));tap(e,256,1)
   rendered=set();executed=None
   for frames in range(0,1801,12):
    r=e.memory();rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
    if word(r,LOG)==0x504c4159 and executed is None:executed=checkpoint(e,'native-result',folder)
    if frames%300==0:e.screenshot(folder/f'frame-{frames:04}.png')
    if frames<1800:e.run(12)
   check('native-cast-completed',executed is not None)
   check('exactly-one-selected-cast',word(executed,LOG+4)==1 and word(executed,LOG+8)==action)
   check('native-caster-identity',word(executed,LOG+24)==0x02000000+ACTOR)
   if choice:check('choice-reached-executor',word(executed,LOG+132)==choice)
   out=word(executed,LOG+136)-0x02000000
   check('native-result-storage',0<=out<0x40000-0x2c4)
   check('native-selected-center',executed[out+10:out+12]==bytes(center))
   if empty:check('empty-cross-zero-recipients',executed[out+0x2c0]==0)
   check('MP-paid-once',half(before,ACTOR+0x1c)-half(executed,ACTOR+0x1c)==costs[action])
   display=observe_field_display(e) if display_checks and action in (380,382) else None
   after=checkpoint(e,'after-playback',folder)
   check('real-rendering',len(rendered)>3)
   check('inventory-AP-unchanged',after[0x1940:0x1e70]==before[0x1940:0x1e70])
   check('caster-learning-unchanged',after[ACTOR+0x40:ACTOR+0xd0]==before[ACTOR+0x40:ACTOR+0xd0])
   check('rendering-no-extra-MP',half(after,ACTOR+0x1c)==half(executed,ACTOR+0x1c))
   loss=half(before,TARGET+0x18)-half(after,TARGET+0x18)
   if action in (377,378,382):check('utility-no-HP-damage',loss==0)
   if action==378:check('rendered-Ward-Protect',bool(after[TARGET+0xeb]&2))
   if action in (380,382):
    state=0x3f410+((ACTOR-0x80)//264)*22
    check('rendered-field-selected-center',after[state+15:state+17]==bytes(center))
    check('rendered-field-kind',after[state+17]&3==(1 if action==380 else 2))
   outcomes.append(dict(action=action,choice=choice,seed=seed,empty=empty,loss=loss,frames=len(rendered),display=display))
   previous=active(e);tap(e,256,900);menu(e,previous)
   if display_checks and action in (380,382):observe_field_display(e)
   checkpoint(e,'next-turn',folder)
  except AssertionError as exc:
   failures.append(dict(case=case,error=str(exc)))
   checkpoint(e,'failure',folder)
  finally:e.close()
for action,choice in {(a,c) for _,a,c,_ in casts}:
 if action not in (377,378,382) and not display_checks:
  try:check('positive-selected-damage-'+str((action,choice)),any(o['action']==action and o['choice']==choice and o['loss']>0 for o in outcomes))
  except AssertionError as exc:failures.append(dict(case=[action,choice],error=str(exc)))
report=dict(passed=not failures,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
 suite='fields-only' if '--fields-only' in sys.argv else 'all-Geomancy',
 checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,failures=failures,
 inputs=dict(map=70,privateMaterialTile=[0,12,31],start=[0,14],move=[0,13],center=[1,13],seeds=list(seeds),displayChecks=display_checks),
 limits=['Private material tile tests choice transport, not production terrain.','Does not prove AI choices, laws, thematic animation or cold saves; field publication is checked only in display mode.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert not failures,('Geomancy playback failures',len(failures))
