"""Fixed native Move/Act/Status flows with actual Rime/Refuge fields.

Compare against an explicit display-only control: its update entry retires the
optional display cache, leaving actual field mechanics, menus and input intact.
Both sides load the same successful current-candidate player-cast states.
No live battle, field, UI result or allocation is injected by this consumer.
"""
import collections,ctypes as C,hashlib,json,pathlib,runpy,struct,sys
from geomancer_render_observation import observe as display

ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);image=ROM.read_bytes();LAB=ROM.parent
PLAY=LAB/'geomancer-playback';OUT=LAB/'geomancer-field-ui';OUT.mkdir(exist_ok=True)
play=json.loads((PLAY/'report.json').read_text());TEST_ROM=PLAY/'playback.gba'
assert play['passed'] and play['romSha1']==meta['romSha1']==hashlib.sha1(image).hexdigest()
original=TEST_ROM.read_bytes();assert hashlib.sha1(original).hexdigest()==play['instrumentedSha1']
control=bytearray(original);offset=(meta['symbols']['ffta_geo_renderer_update']&~1)-0x08000000
patch=(bytes.fromhex('c046') if offset&3 else b'')+bytes.fromhex('004b1847')+struct.pack('<I',meta['symbols']['ffta_geo_renderer_retire']|1)
control[offset:offset+len(patch)]=patch
CONTROL=OUT/'display-disabled.gba';CONTROL.write_bytes(control)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
checks=collections.Counter();outcomes=[];case=None;failures=[]

def check(label,value):
 checks[label]+=1
 assert value,(case,label)

def active(r):return word(r,word(r,0xf438)-0x02000000+24)-0x02000000

def tap(e,key):e.run(8,key);e.run(240)

def menu(e):menus['wait_for_menu'](e,limit=1200,step=10)

def confirm_move(e):
 # Measure the real input-to-rendered-menu interval rather than the script's
 # fixed release waits. Cursor/range setup is already settled before this key.
 e.run(8,256)
 for frames in range(8,1201):
  if half(e.memory(),0xf5c4)==37 and menus['menu_visible'](e):
   e.run(60) # Stable snapshots use the same release window on both variants.
   return frames
  if frames<1200:e.run(1)
 raise AssertionError('Timed native Move did not return to its rendered menu')

def fields(r):return bytes(r[0x3f410+i*22+j] for i in range(36) for j in (15,16,17))

def ui_pixels(e,label):
 if label!='status-open':return None
 raw,w,h,pitch,pixel=e.frame;size=4 if pixel==1 else 2
 # Static status text excludes the animated unit preview and its platform.
 return hashlib.sha1(b''.join(raw[y*pitch+4*size:y*pitch+94*size] for y in range(72,148))).hexdigest()

def snapshot(e,label,folder):
 r=e.memory();e.screenshot(folder/(label+'.png'));e.save(folder/(label+'.state'))
 check('native-render-code-intact',C.string_at(*e.maps[0x03000000])[0x6170:0x6d68]==image[0xa38d24:0xa3991c])
 p=word(r,0xf438)-0x02000000;unit=active(r)
 return dict(label=label,statusTextPixels=ui_pixels(e,label),phase=half(r,0xf5c4),mode=r[p+4],command=half(r,0xf58e),
  actor=unit,position=list(r[unit+0xf6:unit+0xf8]),
  displayedPosition=[half(r,word(r,0xf4ec)-0x02000000+8)//32,half(r,word(r,0xf4ec)-0x02000000+12)//32],cursor=[half(r,0xf3b8),half(r,0xf3bc)],
  rangeBackgrounds=list(r[0x8168:0x816a]),fields=fields(r).hex(),
  inventoryAP=hashlib.sha1(r[0x1940:0x1e70]).hexdigest(),
  stats=[r[u+0x18:u+0x20].hex() for u in [0x80+264*i for i in range(24)]+[0x2fc4+264*i for i in range(12)]])

for action in (380,382):
 for empty in (False,True):
  source=PLAY/str(action)/'0'/('empty' if empty else 'occupied')/'0'/'next-turn.state'
  for flow in ('move','action','status'):
   if '--remaining-ui' in sys.argv and not(flow=='status' or (empty and flow=='move')):continue
   comparison=[];latencies=[]
   for variant,rom in (('native-control',CONTROL),('field-display',TEST_ROM)):
    case=(action,empty,flow,variant);folder=OUT/str(action)/str(int(empty))/flow/variant;folder.mkdir(parents=True,exist_ok=True)
    e=E(rom)
    try:
     e.load(source);e.run(240);menu(e)
     if variant=='field-display':display(e)
     before=e.memory();rows=[snapshot(e,'start',folder)];move_frames=None
     if flow=='move':
      tap(e,256);rows.append(snapshot(e,'move-range',folder))
      check('native-Move-range-active',e.memory()[0x8168:0x816a]==bytes((1,3)))
      tap(e,64 if empty else 16);rows.append(snapshot(e,'move-cursor',folder))
      move_frames=confirm_move(e);rows.append(snapshot(e,'move-completed',folder))
      check('native-Move-actually-changes-displayed-position',rows[-1]['displayedPosition']!=rows[0]['displayedPosition'])
     elif flow=='action':
      for key in (32,256):tap(e,key)
      rows.append(snapshot(e,'action-menu',folder))
      tap(e,256);rows.append(snapshot(e,'Fight-targeting',folder))
      for _ in range(6):
       tap(e,1)
       if menus['menu_visible'](e) and half(e.memory(),0xf5c4)==37:break
      menu(e);rows.append(snapshot(e,'action-cancelled',folder))
     else:
      for key in (32,32,32,256):tap(e,key)
      rows.append(snapshot(e,'status-open',folder))
      tap(e,1)
      check('Status-returns-to-command-phase',half(e.memory(),0xf5c4)==37)
      # The shared menu anchor expects white Status text. Move the orange
      # highlight to Action before using that unchanged visual observer.
      for key in (16,16):tap(e,key)
      menu(e);rows.append(snapshot(e,'status-closed',folder))
     after=e.memory()
     check('UI-keeps-current-turn',active(after)==active(before))
     check('UI-does-not-tick-or-replace-fields',fields(after)==fields(before))
     check('UI-preserves-inventory-and-AP',after[0x1940:0x1e70]==before[0x1940:0x1e70])
     check('UI-does-not-execute-an-attack',word(after,0x3ff54)==word(before,0x3ff54))
     if variant=='field-display':display(e)
     comparison.append(rows);latencies.append(dict(variant=variant,moveReadyFrames=move_frames))
    except BaseException as error:
     e.save(folder/'failure.state');e.screenshot(folder/'failure.png')
     failures.append(dict(case=case,error=repr(error)))
    finally:e.close()
   if len(comparison)==2:
    try:check('actual-native-UI-behavior-matches-display-disabled-control',comparison[0]==comparison[1])
    except AssertionError as error:failures.append(dict(case=case,error=repr(error),rows=comparison,latencies=latencies))
    outcomes.append(dict(action=action,empty=empty,flow=flow,sourceSha1=hashlib.sha1(source.read_bytes()).hexdigest(),rows=comparison,latencies=latencies))
report=dict(passed=not failures,romSha1=meta['romSha1'],sourcePlaybackSha1=play['instrumentedSha1'],controlSha1=hashlib.sha1(control).hexdigest(),
 controlPatch=dict(offset=hex(offset),original=original[offset:offset+len(patch)].hex(),replacement=patch.hex()),
 checks=dict(checks),outcomes=outcomes,failures=failures,
 limits=['No claim of identical screenshots outside UI: field edges and animated sprites legitimately differ.','HBlank distortion, overlapping casters and real-device frame rate remain separate.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
assert not failures,('Field/UI failures',len(failures))
