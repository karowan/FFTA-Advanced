"""Actual battle Status menu allocation and return using a compatible capture."""
import ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator
from live_palette_evidence import observe
manifest=ROOT/'build/art/connected/current.json'
if '--manifest' in sys.argv:manifest=ROOT/sys.argv[sys.argv.index('--manifest')+1]
m=json.loads(manifest.read_text());rom=Path(m['path']).read_bytes()
old=json.loads((ROOT/'build/art/connected/5ee3099323fe1af8b2348b772786435d1e011cb6/manifest.json').read_text());previous=Path(old['path']).read_bytes()
source=ROOT/'build/art/live-palette/battle/20260918T164311.010995Z/observed.json'
exact='--retained-ready' in sys.argv
if exact:source=ROOT/sys.argv[sys.argv.index('--retained-ready')+1]
prior=json.loads(source.read_text());seed=source.parent/'candidate-ready.state';seedbytes=seed.read_bytes()
assert prior['status']=='passed'
assert m['romSha1']==hashlib.sha1(rom).hexdigest()
# Only three immediate/literal bytes change, all allocating the not-yet-open
# party parent. Code/data pointers and every serialized layout remain identical.
if exact:
 assert prior['romSha1']==m['romSha1']
else:
 assert prior['romSha1']==old['romSha1']==hashlib.sha1(previous).hexdigest()
 assert [i for i,(a,b) in enumerate(zip(previous,rom)) if a!=b]==[0x24644,0x30c78,0x30c9d]
 assert previous[0x24644:0x24648]==bytes.fromhex('c6242402') and rom[0x24644:0x24648]==bytes.fromhex('ed242402')
shared=m['components']['livePalette'].get('sharedBattleMenuHeap',False)
compact=m['components']['livePalette'].get('compactBattleStatus',False)
owner_bytes=0x7280 if compact else 0x9980
list_offset=0x4340 if compact else 0x7280
owner_magic=0x50485232 if compact else 0x50485231
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
out=ROOT/'build/art/owned-menu/battle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];inputs=[];captures={};help_exits=[];e=None
def check(ok,label):
 assert ok,label
 checks.append(label)
def word(data,at):return struct.unpack_from('<I',data,at)[0]
def capture(name):
 r=e.memory();iw=C.string_at(*e.maps[0x03000000])
 if e.frame is not None:e.screenshot(out/(name+'.png'))
 e.save(out/(name+'.state'))
 for ext,data in [('ram',r),('iwram',iw),('vram',C.string_at(*e.maps[0x06000000])),('palette',C.string_at(*e.maps[0x05000000])),('oam',C.string_at(*e.maps[0x07000000]))]:(out/(name+'.'+ext)).write_bytes(data)
 captures[name]=dict(ramSha256=sha(r),iwramSha256=sha(iw),party=word(iw,0x2818),parent=word(iw,0x2778),parentBytes=word(iw,0xe54))
 return r,iw
def tap(key):inputs.append([8,key,180]);e.run(8,key);e.run(180)
try:
 e=E(Path(m['path']));e.load(seed)
 initial=e.memory();iw=C.string_at(*e.maps[0x03000000])
 check(initial==(source.parent/'candidate-ready.ram').read_bytes() and iw==(source.parent/'candidate-ready.iwram').read_bytes(),'Exact retained ready RAM/IWRAM before inputs')
 e.run(1);inputs.append([1,0]);initial=e.memory()
 capture('ready');check(menu['menu_visible'](e),'Initial native turn menu visible')
 original_wrappers=from_emulator(rom,e)
 for key in (32,32,32,256):tap(key)
 r,iw=capture('status');ctx=word(iw,0x2818);parent=word(iw,0x2778);size=word(iw,0xe54)
 if shared:
  check(parent==word(r,0xf434) and size==0xed00,'Actual Status borrows current battle heap')
  heap_end=parent+8+4*struct.unpack_from('<H',r,parent-0x02000000+6)[0]
  check(parent<=ctx<ctx+owner_bytes<=heap_end<=0x0203c000,'Context fits actual battle heap extent')
  check(r[ctx-0x02000000-8:ctx-0x02000000-6]==b'la' and owner_bytes<=4*struct.unpack_from('<H',r,ctx-0x02000000-6)[0]-12<=owner_bytes+12,'Context has its own native allocation header')
  state=m['components']['livePalette']['partyHeapRoot']-0x02000000
  check(struct.unpack_from('<4I',r,state)==(owner_magic,parent,1,0),'Exact borrowed constructor lifetime recorded')
 else:
  check(size==0xed00 and 0x02000000<=parent<parent+size<=0x0203c000,'Actual enlarged battle party parent allocated below palette state')
  check(parent<=ctx<ctx+0x9980<=parent+size,'Actual enlarged context fits live parent')
 check(word(r,ctx-0x02000000+0x2d50)==ctx+list_offset,'Battle Status publishes context-owned list')
 check(r[0x80:0x1e70]==initial[0x80:0x1e70],'Opening Status preserves roster inventory AP')
 if compact:
  # Exercise both native panels and their Select inspection/help path on the
  # smaller allocation, then use the actual menu cancellation/teardown.
  for page in range(2):
   if page:tap(128)
   ordinary_phase=0x0f if page else 3
   check(C.string_at(*e.maps[0x03000000])[0xec2]==ordinary_phase,'Exact native panel before inspection '+str(page))
   tap(4)
   for _ in range(5):tap(32)
   tap(256);capture('status-help-'+str(page))
   # Long text consumes a B to finish printing; already-complete text does
   # not. Bounded native-state inputs avoid closing Status one level too far.
   exits=[]
   for _ in range(3):
    phase=C.string_at(*e.maps[0x03000000])[0xec2];exits.append(phase)
    if phase==ordinary_phase:break
    check(phase in (0x1c,0x1b if page else 0x19),'Known help or panel-specific inspection-cursor state '+str((page,phase)))
    tap(1)
   help_exits.append(exits)
   r,iw=capture('status-page-'+str(page))
   check(iw[0xec2]==ordinary_phase,'Native inspection returns to its ordinary Status panel '+str(page))
   check(word(r,0x3ff40)==ctx and struct.unpack_from('<4I',r,state)==(owner_magic,parent,1,0),'Status remains owned after help '+str(page))
   check(r[0x80:0x1e70]==initial[0x80:0x1e70],'Help preserves roster inventory AP '+str(page))
 tap(1);e.run(180);capture('returned-status-selected')
 # Native return keeps Status selected (orange). The existing white-letter
 # menu anchor is authenticated for Move selected. Restore that cursor with
 # three Up presses before using the anchor; do not relax its pixel checks.
 for _ in range(3):tap(16)
 r,iw=capture('returned')
 check(menu['menu_visible'](e),'Return to actual native turn menu')
 check(word(r,0x3ff40)==0,'Party owner retired after return')
 if shared:check(struct.unpack_from('<4I',r,state)==(0,parent,1,1),'Borrowed heap retired after exact native destructor and parent release')
 check(set(from_emulator(rom,e))==set(original_wrappers),'All native battle actors restored')
 check(r[0x80:0x1e70]==initial[0x80:0x1e70],'Status round trip preserves roster inventory AP')
 observe(m['components']['livePalette'],rom,r,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),check,{1,2,4,8})
 check(seed.read_bytes()==seedbytes,'Retained source state unchanged')
 report=dict(status='passed',romSha1=m['romSha1'],checks=checks,inputs=inputs,captures=captures,helpExitStates=help_exits,source=dict(report=str(source),reportSha256=sha(source.read_bytes()),stateSha256=sha(seedbytes),romSha1=prior['romSha1'],compatibleDelta=[] if exact else [0x24644,0x30c78,0x30c9d]),scope='Actual mixed-class battle Status allocation and return with authenticated ready state; exact ROM when retained-ready supplied, otherwise strictly bounded three-byte delta. Shared heap entry/teardown and class colors checked when enabled. Compact mode additionally opens both equipment/ability help panels and returns through bounded native states. No other encounter, worst-case heap, opening keyboard, timing or final-art acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 if e:capture('failed')
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=m['romSha1'],checks=checks,inputs=inputs,captures=captures,error=str(error)),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
 if e:e.close()
