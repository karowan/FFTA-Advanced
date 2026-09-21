"""Fixed Passing Step player flows through the actual409 production hooks.

Formation/job/learning and cast seeds are explicit fixture inputs. Occupancy
and Immobilize cases alter declared inputs at final confirmation, not attack
results; they test invalidation, not actual reaction delivery. Native attacks,
maps, routes, animations, payments and subsequent turns are never replaced.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
preparation=(ROOT/'scripts/test-dancer-choice-playback.py').read_text().split('# Actual selected player casts')[0]
preparation=preparation.replace('dancer-choice-playback','passing-step-playback').replace("'DNC-A6'","'DNC-A9'")
exec(compile(preparation,'<shared fixed Viera preparation>','exec'))
samples=[];fixed_inputs=[];failures=[]
(OUT/'report.json').write_text(json.dumps(dict(passed=False,status='running',romSha1=meta['romSha1'])))

def key(e,k,wait=180):fixed_inputs.append((k,8,wait));tap(e,k,wait)
def phase(r):return word(r,0x3f004) if word(r,0x3f000)==0x50535450 else 0
def xy(r,w):return half(r,w+8)//32,half(r,w+12)//32
def snap(e,label,folder):
 r=checkpoint(e,label,folder)
 (folder/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 row=dict(case=case,label=label,passingPhase=phase(r),ownerWords=list(struct.unpack_from('<13I',r,0x3f000)),
          battlePhase=half(r,0xf5c4),actorXY=list(r[ACTOR+0xf6:ACTOR+0xf8]),
          wrapperXY=xy(r,wrappers[ACTOR]),actorHP=half(r,ACTOR+0x18),actorMP=half(r,ACTOR+0x1c),
          loggedCasts=word(r,LOG+4),loggedAction=word(r,LOG+8),
          cursorXY=(half(r,0xf3b8),half(r,0xf3bc)),mode=mode(e))
 samples.append(row);(OUT/'partial.json').write_text(json.dumps(samples,indent=2));return r

for flow,seed in [('route',0),('route',3),('route',18),('decline',0),('cancel',0),
                  ('out-of-range',0),('occupied-after-selection',0),('immobilized-after-selection',0),
                  ('no-approach-route',0),('no-approach-decline',0)]:
 case=(flow,seed);folder=OUT/(flow+'-'+str(seed));folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(OUT/'start.state');e.run(1)
  no_approach=flow.startswith('no-approach');origin=(0,14 if no_approach else 13)
  if no_approach:key(e,32) # Act follows the unspent Move command.
  else:
   for k in (256,16,256):key(e,k)
  approach=snap(e,'approach',folder);check('native-approach',xy(approach,wrappers[ACTOR])==origin)
  for k in (256,32,256,256):key(e,k)
  targeting=snap(e,'targeting',folder)
  cursor_xy=(half(targeting,0xf3b8),half(targeting,0xf3bc))
  check('fixed-adjacent-target-domain',cursor_xy in (origin,(1,origin[1])))
  if cursor_xy==origin:key(e,128)
  key(e,256)
  # Native target preview differs between single-target and area actions.
  # At most one additional preview confirmation is allowed before the modal.
  if phase(e.memory())!=2:key(e,256)
  before=snap(e,'route-selection',folder)
  check('native-route-selection',phase(before)==2)
  check('native-blue-range',before[0x8168:0x816a]==bytes((1,3)))
  check('no-early-cast',word(before,LOG+4)==0)
  initial_mp=half(before,ACTOR+0x1c)
  if flow in ('decline','no-approach-decline'):key(e,1)
  else:
   for k in (16,16):key(e,k)
   if flow=='out-of-range':
    key(e,16);key(e,256);rejected=snap(e,'rejected',folder)
    check('reject-destination-over-budget',phase(rejected)==2)
    key(e,1)
   else:key(e,256)
  selected=snap(e,'final-confirmation',folder)
  check('native-final-confirmation',phase(selected)==3 and mode(e)==11)
  check('preview-never-moves-actor',xy(selected,wrappers[ACTOR])==origin)
  if flow=='cancel':
   key(e,1,600);cancelled=snap(e,'cancelled',folder)
   check('cancel-retires-route',phase(cancelled)==7)
   check('cancel-does-not-pay-or-cast',half(cancelled,ACTOR+0x1c)==initial_mp and word(cancelled,LOG+4)==0)
   check('cancel-does-not-move',xy(cancelled,wrappers[ACTOR])==(0,13))
   continue
  if flow=='occupied-after-selection':
   e.set_memory(SECOND+0xf6,bytes((0,11)));e.set_memory(wrappers[SECOND]+8,struct.pack('<3H',16,48,11*32+16))
  if flow=='immobilized-after-selection':e.set_memory(ACTOR+0xeb,bytes((e.memory()[ACTOR+0xeb]|64,)))
  e.set_memory(LOG+148,struct.pack('<II',1,seed));key(e,256,1);e.run(2400)
  after=snap(e,'after-playback',folder)
  check('one-Passing-Step-cast',word(after,LOG+4)==1 and word(after,LOG+8)==409)
  check('once-only-six-MP',half(after,ACTOR+0x1c)==initial_mp-6)
  expected=(0,origin[1]-2) if flow in ('route','no-approach-route') else origin
  check('native-finishing-endpoint',xy(after,wrappers[ACTOR])==expected)
  check('committed-finishing-endpoint',tuple(after[ACTOR+0xf6:ACTOR+0xf8])==expected)
  check('route-owner-retired',phase(after)==7)
  if flow=='no-approach-decline':
   check('decline-preserves-ordinary-Move',half(after,0xf5c4)==37)
   # Spend three ordinary movement points, exceeding the optional step cap.
   for k in (256,16,16,16,256):key(e,k)
   e.run(600)
   after=snap(e,'ordinary-Move-after-decline',folder);expected=(0,11)
   check('decline-does-not-cap-ordinary-Move',xy(after,wrappers[ACTOR])==expected)
   check('ordinary-Move-does-not-repeat-attack',word(after,LOG+4)==1 and half(after,ACTOR+0x1c)==initial_mp-6)
  check('native-facing-no-extra-Move',half(after,0xf5c4)==47)
  check('AP-inventory-unchanged',after[0x1940:0x1e70]==before[0x1940:0x1e70])
  check('learning-unchanged',after[ACTOR+0x40:ACTOR+0xd0]==before[ACTOR+0x40:ACTOR+0xd0])
  if flow in ('route','no-approach-route') and seed==0:
   key(e,1);after_cancel=snap(e,'cancel-after-completed-step',folder)
   check('completed-step-cannot-be-undone',xy(after_cancel,wrappers[ACTOR])==expected)
   check('completed-step-keeps-Move-spent',bool(after_cancel[0x1f70]&16))
   check('completed-step-keeps-facing-prompt',half(after_cancel,0xf5c4)==47)
  previous=active(e);previous_wrapper=word(after,0xf4ec);key(e,256,1)
  for frame in range(3000):
   if word(e.memory(),0xf4ec) not in (0,previous_wrapper):break
   e.run(1)
  else:raise AssertionError('native turn handoff timed out')
  handoff=snap(e,'turn-handoff',folder)
  check('handoff-precedes-next-attack',word(handoff,LOG+4)==1)
  check('owner-cleared-on-next-turn',handoff[0x3f000:0x3f008]==bytes(8))
  check('turn-handoff-retains-position',tuple(handoff[ACTOR+0xf6:ACTOR+0xf8])==expected)
  # Later native AI attacks may knock the dancer back. Position persistence
  # is checked at the first turn handoff, before those subsequent actions.
  menu(e,previous);snap(e,'next-player-menu',folder)
 except AssertionError as error:
  failures.append(dict(case=case,error=str(error)));snap(e,'failure',folder)
 finally:e.close()
# Native suspend and cold boot after the successful finishing-move turn.
# Only emulator-owned test SRAM is used; no player save is opened.
case=('cold-resume',0);folder=OUT/'cold-resume';folder.mkdir(exist_ok=True)
e=E(TEST_ROM)
try:
 e.load(OUT/'route-0/next-player-menu.state');expected=e.memory()
 for k in (1,8,16,256,256):key(e,k)
 old=e.memory(0);key(e,256,300);saved=e.memory(0)
 check('native-suspend-write',saved!=old);(folder/'suspended.sav').write_bytes(saved)
finally:e.close()
e=E(ROM)
try:
 e.set_memory(0,saved,0);e.run(3600)
 for k,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):key(e,k,wait)
 menu(e);actual=e.memory();e.save(folder/'resumed.state');e.screenshot(folder/'resumed.png')
 (folder/'resumed.ram').write_bytes(actual)
 check('cold-native-code-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
 check('cold-action-roots-empty',actual[0x3ff44:0x3ff4c]==bytes(8))
 check('cold-position-retained',actual[ACTOR+0xf6:ACTOR+0xf8]==expected[ACTOR+0xf6:ACTOR+0xf8])
 check('cold-HP-MP-retained',actual[ACTOR+0x18:ACTOR+0x20]==expected[ACTOR+0x18:ACTOR+0x20])
 check('cold-AP-inventory-retained',actual[0x1940:0x1e70]==expected[0x1940:0x1e70])
 check('cold-pending-route-empty',actual[0x3f000:0x3f008]==bytes(8))
finally:e.close()
report=dict(passed=not failures,failures=failures,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
 checks=dict(checks),total=sum(checks.values()),fixedInputs=fixed_inputs,samples=samples,
 limits=['Reaction-delivered interruption, actual movement laws/traps and AI route choice need separate acceptance.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert not failures,failures
