"""Real fields beside Doublecast/Spellweave/Absorb and native summon effects.

Reuse current accepted field-cast states. Jobs, mastery, formation and initial
stats are declared before inputs. Fixed inputs then perform Move, casts, native
queued reaction playback, facing and the next turn. The control disables only
field graphics; field mechanics and all native allocation/execution stay live.
"""
import pathlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-doublecast-playback.py'
prefix=source.read_text(encoding='utf-8').split('e=E(TEST_ROM)\ntry:')[0]
prefix=prefix.replace('doublecast-playback','geomancer-mixed-playback')
exec(compile(prefix,'<shared deterministic queue recorder>','exec'))
from geomancer_render_observation import observe as field_display
heap=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))['heap']
SCRIPT_SHA=hashlib.sha1(pathlib.Path(__file__).read_bytes()).hexdigest()
(OUT/('test-source-'+SCRIPT_SHA+'.py')).write_bytes(pathlib.Path(__file__).read_bytes())
PLAY=LAB/'geomancer-playback'
proof=json.loads((PLAY/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==meta['romSha1']
control=bytearray(TEST_ROM.read_bytes());off=(meta['symbols']['ffta_geo_renderer_update']&~1)-0x08000000
patch=(bytes.fromhex('c046') if off&3 else b'')+bytes.fromhex('004b1847')+struct.pack('<I',meta['symbols']['ffta_geo_renderer_retire']|1)
control[off:off+len(patch)]=patch
CONTROL=OUT/'display-disabled.gba';CONTROL.write_bytes(control)
controls=dict(playback=hashlib.sha1(TEST_ROM.read_bytes()).hexdigest(),control=hashlib.sha1(control).hexdigest())
scenarios=[dict(name='rime-doublecast-thunder',field=380,job=30,lessons=[23,24,29],actions=[23,26],seed=18),
 dict(name='refuge-doublecast-blizzard',field=382,job=30,lessons=[23,25,29],actions=[23,29],seed=18),
 dict(name='rime-madeen',field=380,job=32,lessons=[51],actions=[75]),
 dict(name='refuge-shiva',field=382,job=32,lessons=[47],actions=[71],seed=18)]
checks=collections.Counter();outcomes=[];failures=[];case=None
def field_records(r):return bytes(r[0x3f410+i*22+j] for i in range(36) for j in (15,16,17))
def display_owner(r):
 manager=word(r,0xf4b0)-0x02000000
 if not 0<=manager<=len(r)-0x440:return 0
 pool=word(r,manager+0x438)-0x02000000
 return word(r,pool+12) if 0<=pool<=len(r)-0x2660 else 0
def setup(s):
 global case
 case=(s['name'],'prepare');folder=OUT/s['name'];folder.mkdir(exist_ok=True)
 input_state=PLAY/str(s['field'])/'0'/'occupied'/'0'/'next-turn.state'
 state_hash=hashlib.sha1(input_state.read_bytes()).hexdigest()
 script_text=pathlib.Path(__file__).read_text(encoding='utf-8')
 setup_node=next(n for n in ast.parse(script_text).body if isinstance(n,ast.FunctionDef) and n.name=='setup')
 setup_source=ast.get_source_segment(script_text,setup_node)
 inputs=dict(romSha1=meta['romSha1'],scenario=s,sourceSha1=state_hash,playbackSha1=controls['playback'],setupSha1=hashlib.sha1(setup_source.encode()).hexdigest())
 cache=folder/'ready-proof.json'
 if '--resume' in sys.argv and cache.exists():
  saved=json.loads(cache.read_text())
  if saved['inputs']==inputs and all(hashlib.sha1((folder/name).read_bytes()).hexdigest()==value for name,value in saved['outputs'].items()):
   return folder,state_hash
 e=E(TEST_ROM)
 try:
  e.load(input_state);e.run(1);menu(e);fixed_giza_formation(image,e)
  check('accepted-live-field-input',any(field_records(e.memory())[2::3]))
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((s['job'],)))
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(0x90))
  bank=word(image,word(image,0xcd538)-0x08000000+4*4)-0x08000000
  want=s['actions']+([33] if len(s['actions'])==2 else [])
  for index,action in zip(s['lessons'],want):
   check('authenticated-native-racial-lesson',half(image,bank+index*8+4)==action and image[bank+index*8+6]==1)
   e.set_memory(ACTOR+0x40+index,b'\xff')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',88 if s['job']==30 else 0,0,0,0,0))
  for unit in (ACTOR,TARGET,0x80,0x188):
   e.set_memory(unit+0x18,struct.pack('<4H',500,500,99,99));e.set_memory(unit+0xe8,bytes(8))
   e.set_memory(unit+0x20,struct.pack('<4H',70,40,40,40));e.set_memory(unit+0x3a,bytes(2))
  formation(e,from_emulator(image,e))
  for turn in range(20):
   if active(e)==0x02000000+ACTOR:break
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  check('native-Viera-turn',active(e)==0x02000000+ACTOR)
  check('field-survives-until-caster-turn',any(field_records(e.memory())[2::3]))
  fixed_giza_formation(image,e)
  formation(e,from_emulator(image,e))
  units=from_emulator(image,e);r=e.memory()
  positions=[r[unit+0xf6:unit+0xf8] for unit in units if half(r,unit+0x18)]
  check('declared-formation-has-no-overlapping-occupants',len(positions)==len(set(positions)))
  for unit in (ACTOR,TARGET,0x80,0x188):
   e.set_memory(unit+0x18,struct.pack('<4H',500,500,99,99));e.set_memory(unit+0xe8,bytes(8))
  e.set_memory(TARGET+0x29,b'\x80');e.set_memory(TARGET+0x2a,bytes(10))
  equip(e,TARGET,'VIK-R1',2,True)
  lesson=next(l for l in registry['lessons'] if l['id']=='MYK-S1')
  index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==4)
  e.set_memory(ACTOR+0x3b,bytes((index,)));e.set_memory(ACTOR+0x40+index,b'\xff')
  state,_,_=owned(e);e.set_memory(state+20,struct.pack('<H',1<<13))
  e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
  e.set_memory(LOG+148,struct.pack('<II',1,s.get('seed',3)))
  field_display(e);checkpoint(e,'ready',folder)
  cache.write_text(json.dumps(dict(inputs=inputs,outputs={name:hashlib.sha1((folder/name).read_bytes()).hexdigest() for name in ('ready.state','ready.ram')}),indent=2),encoding='utf-8')
  return folder,state_hash
 except BaseException:
  e.save(folder/'preparation-failure.state');e.screenshot(folder/'preparation-failure.png');raise
 finally:e.close()
def execute(s,variant,rom,folder,state_hash):
 global case
 case=(s['name'],variant);dest=folder/variant;dest.mkdir(exist_ok=True)
 result_path=dest/'report.json'
 prepared_hash=hashlib.sha1((folder/'ready.state').read_bytes()).hexdigest()
 if '--resume' in sys.argv and result_path.exists():
  previous=json.loads(result_path.read_text())
  if previous.get('passed') and previous['romSha1']==meta['romSha1'] and previous['scenario']==s and previous['sourceSha1']==state_hash and previous.get('preparedSha1')==prepared_hash and previous['controls']==controls:
   return previous
 e=E(rom)
 try:
  e.load(folder/'ready.state');e.run(120);menu(e)
  field_display(e,expected=variant=='field-display');before=checkpoint(e,'before',dest)
  positions=[before[unit+0xf6:unit+0xf8] for unit in from_emulator(image,e) if half(before,unit+0x18)]
  check('loaded-formation-has-no-overlapping-occupants',len(positions)==len(set(positions)))
  # Move consumes movement so native completion has an unambiguous facing step.
  for key in (256,16,256):tap(e,key)
  menu(e)
  check('movement-keeps-intended-caster',active(e)==0x02000000+ACTOR)
  checkpoint(e,'move-completed',dest)
  for key in (256,32,256):tap(e,key)
  check('native-ability-list',mode(e) in (6,7,8))
  checkpoint(e,'ability-list',dest)
  if len(s['actions'])==2:
   for key in (32,32,256):tap(e,key) # Third learned Red Magic command: Doublecast.
   for key in (256,128,256,256,32,256,128,256,256):tap(e,key)
  else:
   for key in (256,128,256,256):tap(e,key)
  confirmed=checkpoint(e,'confirmation',dest)
  check('native-final-confirmation',mode(e)==11)
  check('no-execution-before-final-confirmation',word(confirmed,LOG+4)==0)
  samples=[];rendered=set();seen={};first=None
  e.run(8,256)
  for frames in range(8,3601,8):
   r=e.memory();n=word(r,LOG+4);rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
   check('native-render-code-during-mixed-playback',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
   h=heap(r);check('native-heap-remains-bounded',h['end']==meta['heapEnd'])
   samples.append(dict(frame=frames,owner=display_owner(r),phase=half(r,0xf5c4),free=h['freePayload'],largest=h['largestFree'],allocated=h['allocatedPayload']))
   if n and n not in seen:
    seen[n]=checkpoint(e,'executed-'+str(n),dest)
    if first is None:first=r
   if frames in (64,184,360,720,1200):e.screenshot(dest/f'frame-{frames:04}.png')
   if n==len(s['actions']) and frames>300 and half(r,0xf4e8+0xdc)==47:break
   if frames<3600:e.run(8)
  after=checkpoint(e,'after-playback',dest)
  check('bounded-mixed-playback-completes',frames<3600 and half(after,0xf4e8+0xdc)==47)
  check('all-native-executors-complete-once',word(after,LOG+4)==len(s['actions']) and len(seen)==len(s['actions']))
  rows=[list(struct.unpack_from('<16I',after,LOG+16+i*64)) for i in range(len(s['actions']))]
  check('native-action-identities',all(row[0]==s['actions'][i] and row[4]==s['actions'][i] for i,row in enumerate(rows)))
  check('bounded-result-counts',all(1<=row[2]<=3 for row in rows))
  reactions=[row[4+j*4] for row in rows for j in range(1,row[2])]
  check('one-final-Absorb-reaction',reactions==[436])
  if len(rows)==2:check('no-Absorb-between-queued-casts',rows[0][2]==1)
  _,sequence,continuation=owned(e)
  check('shared-continuation-retired',continuation==bytes(16))
  check('one-final-Magic-sequence',sequence==2)
  action_table=word(image,0x23320)-0x08000000
  cost=sum(image[action_table+a*28+4] for a in s['actions'])
  check('exact-native-MP-payment',half(confirmed,ACTOR+0x1c)-half(after,ACTOR+0x1c)==cost)
  check('nonzero-hostile-damage',half(after,TARGET+0x18)<half(confirmed,TARGET+0x18))
  check('field-not-ticked-or-mutated-by-other-job',field_records(before)==field_records(after))
  check('AP-and-inventory-preserved',before[0x1940:0x1e70]==after[0x1940:0x1e70])
  check('real-animated-frames',len(rendered)>3)
  field_display(e,expected=variant=='field-display')
  previous=active(e);tap(e,256,900);menu(e,previous);end=checkpoint(e,'next-turn',dest)
  field_display(e,expected=variant=='field-display')
  check('next-turn-keeps-field-records',field_records(end)==field_records(after))
  result=dict(passed=True,romSha1=meta['romSha1'],scriptSha1=SCRIPT_SHA,scenario=s,variant=variant,sourceSha1=state_hash,preparedSha1=prepared_hash,controls=controls,
   frames=frames,renderedFrames=len(rendered),results=rows,reactions=reactions,sequence=sequence,
   stats=[after[u+0x18:u+0x20].hex() for u in (ACTOR,TARGET)],fields=field_records(after).hex(),
   inventoryAP=hashlib.sha1(after[0x1940:0x1e70]).hexdigest(),mpSpent=cost,samples=samples,
   minimumFree=min(v['free'] for v in samples),peakAllocated=max(v['allocated'] for v in samples))
  result_path.write_text(json.dumps(result,indent=2),encoding='utf-8');return result
 except BaseException:
  e.save(dest/'failure.state');e.screenshot(dest/'failure.png');(dest/'failure.ram').write_bytes(e.memory());raise
 finally:e.close()
for s in scenarios:
 try:
  folder,state_hash=setup(s);pair=[]
  for variant,rom in (('native-control',CONTROL),('field-display',TEST_ROM)):
   pair.append(execute(s,variant,rom,folder,state_hash))
  check('display-does-not-change-mixed-gameplay',all(pair[0][k]==pair[1][k] for k in ('stats','fields','inventoryAP','mpSpent','reactions','sequence')))
  check('mixed-display-playback-overhead-within-budget',pair[1]['frames']-pair[0]['frames']<=max(120,pair[0]['frames']//10))
  outcomes.extend(pair)
  print(json.dumps(dict(completedScenario=s['name'],retainedOrNew=[p['scriptSha1'] for p in pair])),flush=True)
 except BaseException as error:failures.append(dict(case=case,error=repr(error)))
report=dict(passed=not failures,romSha1=meta['romSha1'],scriptSha1=SCRIPT_SHA,controls=controls,
 checks=dict(checks),outcomes=outcomes,failures=failures,
 limits=['Declared mastery/stats/formation, not campaign earning.','Frame samples measure real allocations but do not manufacture worst-case pressure; native allocator refusal/retry has separate coverage.','Representative native effects and cross-class queue consumers, not every possible animation.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/('report-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='outcomes'},indent=2))
assert report['passed'],failures
