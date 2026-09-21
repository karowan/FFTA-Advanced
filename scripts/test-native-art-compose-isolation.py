"""Installed compositor versus original entry on identical captured inputs.

Native DMA0 is modeled synchronously at its four authenticated completion
points. This isolates writes and native color phases, not real VBlank timing.
"""
import argparse, ast, bisect, collections, datetime, hashlib, itertools, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--current',action='store_true');parser.add_argument('--profile',action='store_true')
parser.add_argument('--mixed-status',action='store_true',help='Profile the pinned current mixed-class raw inputs; never resume serialized actor pointers.')
parser.add_argument('--installed-mixed',action='store_true',help='Use the corrected7507 mixed capture including native-highlight state.')
parser.add_argument('--candidate-manifest',type=Path,help='Compose the same pinned mixed raw inputs with an ABI-compatible candidate; no actor playback.')
parser.add_argument('--repeat-frame',action='store_true',help='Validate a primed exact-repeat candidate on all native phases/stack alignments; optional profile counts the hit.')
args=parser.parse_args();assert not args.mixed_status or args.profile or args.repeat_frame
assert not args.installed_mixed or args.mixed_status
assert not args.candidate_manifest or args.mixed_status
arm_source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
source=ROOT/'build/art/live-palette/battle/20260918T075021.733381Z'
assert sha((source/'failed.json').read_bytes())=='35b26fea1f86929b3d0a98ac34d28badf4be82631aa165ac30b97664a201bc76'
fixture_meta=json.loads((ROOT/'build/art/live-palette/29453def10826d971c689b6169a316b182c2fda1/manifest.json').read_text())
meta=json.loads((ROOT/'build/art/live-palette/poc.json').read_text()) if args.current else fixture_meta
for field in ('ramReservation','transientStateBytes','bindingOffset','bindingEntryBytes','visibleColorsOffset','profileOffset','refusalOffset','variantOffset','paletteSha256','generatedSourceSha256','baseRomSha1'):
 assert meta[field]==fixture_meta[field],field
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
expected={'ram':'a7fa401e99806ad8b6c9be5004b98aaaa716194fc71e121f661fd2bfceaa4dad','iwram':'d7250d07c74b2ece6ea6ba4151a82b28d8b2657f720920e21683aa5812570280','vram':'6d6181e62fbf6cb7fce54ae6ec3c220a5873abe94a008d762244e89be3d3b1e9','palette':'243b791d6a7098b8b3e2e40fa4662b7830f7c5ab2ef93bfcef180df701b89d73','oam':'6bb0466a5a8af2f52f14d8bcf57e3e75f326d63d670aaa40a842d1d966bd0859'}
if args.mixed_status:
 source=ROOT/'build/art/live-palette/battle/20260918T183919.610099Z'
 meta=json.loads((ROOT/'build/art/connected/4a7d55ce09cd4a40965a0bb97de2701d276789c5/live-palette-view.json').read_text(encoding='utf-8'))
 rom=Path(meta['path']).read_bytes()
 assert hashlib.sha1(rom).hexdigest()==meta['romSha1']=='4a7d55ce09cd4a40965a0bb97de2701d276789c5'
 prior=json.loads((source/'observed.json').read_text(encoding='utf-8'))
 assert prior['status']=='passed' and prior['romSha1']==meta['romSha1']
 expected={'ram':'0a0de57cd3ee8b617475b572b856b2181628eed8ed0e120af93451394f642018','iwram':'6ab0ad9dd121fc844eb9aaa15f184ee83ba4f1ebdb8cd9b5109ad433f686ada4','vram':'01ed6c3da8e222e9900997cf7433efe62d077bcd932a79813fb478e083300bb7','palette':'150b5f0c9c220e6d36aeb6b76c2eaf32e82ecb5f9f10265727508392f16dcb02','oam':'2ec2e6a3bc8ba35fe482f6617a157e330e16caca8b8755481e48805795e61b45'}
 if args.installed_mixed:
  source=ROOT/'build/art/live-palette/battle/20260918T210407.312558Z'
  meta=json.loads((ROOT/'build/art/connected/7507ca5cb03c1db7a717fd6d21d97a9f5a4ae08b/live-palette-view.json').read_text(encoding='utf-8'))
  rom=Path(meta['path']).read_bytes()
  assert hashlib.sha1(rom).hexdigest()==meta['romSha1']=='7507ca5cb03c1db7a717fd6d21d97a9f5a4ae08b'
  raw=(source/'observed.json').read_bytes()
  assert sha(raw)=='b645c15226a343f95b35d3ae260174abd9e76efe255c779966ac0b9bc1da1fcf'
  assert json.loads(raw)['status']=='passed' and json.loads(raw)['romSha1']==meta['romSha1']
  expected.update(ram='a9ac988e1766226e94d35a0ab1a435ff8f5eb2a2b76cb851ee56bb78e952cc48',iwram='de7d1f9480c4b7ce59269a5147d3ffdfa8efc1628b436958ca11917d1a337ea8')
 if args.candidate_manifest:
  candidate=json.loads(args.candidate_manifest.read_text(encoding='utf-8'))
  for field in ('ramReservation','transientStateBytes','bindingOffset','bindingEntryBytes','visibleColorsOffset','profileOffset','refusalOffset','variantOffset','paletteSha256','generatedSourceSha256','baseRomSha1','tagOffset','historySlots'):
   if field=='transientStateBytes' and args.repeat_frame:
    assert candidate[field]==meta[field]+928 and candidate['repeatOffset']==meta[field] and candidate['repeatBytes']==928
   else:assert candidate[field]==meta[field],field
  meta=candidate;rom=Path(meta['path']).read_bytes()
  assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
saved={name:(source/('candidate-ready.'+name)).read_bytes() for name in expected}
assert all(sha(saved[name])==value for name,value in expected.items())
control=bytearray(rom);change=next(c for c in meta['changes'] if c['offset']==0x12bc)
assert rom[0x12bc:0x12c4].hex()==change['after'] and change['before']=='f0b557464e464546'
control[0x12bc:0x12c4]=bytes.fromhex(change['before'])
out=ROOT/'build/art/compose-isolation'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
BASE=meta['ramReservation'][0];LIMIT=meta['ramReservation'][1]
checks=collections.Counter();records=[];case=None;transfers={};phase_rows=[]
instruction_counts=collections.Counter()
named=sorted((address,name) for name,address in meta['symbols'].items() if not name.startswith('$'))
symbol_addresses=[address for address,name in named]

def profile(u,pc,size,data):
 if meta['used'][0]+0x08000000<=pc<meta['used'][1]+0x08000000:
  index=bisect.bisect_right(symbol_addresses,pc)-1
  name=named[index][1]
 elif 0x03007000<=pc<0x03007800:name='scoped IWRAM scan'
 elif 0x03000000<=pc<0x03008000:name='native IWRAM'
 else:name='native ROM'
 instruction_counts[name]+=1
def check(group,actual,expected):
 checks[group]+=1;assert actual==expected,(case,group,repr(actual)[:200],repr(expected)[:200])
def machine(data):
 a=ARM(data,saved['iwram']);a.put(0x02000000,saved['ram'])
 for address,size in ((0x04000000,0x1000),(0x05000000,0x1000),(0x06000000,0x18000),(0x07000000,0x1000)):a.u.mem_map(address,size)
 for name,address in [('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:a.put(address,saved[name])
 a.put(0x04000006,struct.pack('<H',180))
 return a
def dma(u,pc,size,a):
 src,dst,flags=struct.unpack('<3I',a.read(0x040000b0,12));count=(flags&65535)*4
 assert flags>>16==0x8400 and 0x03000000<=src<=0x03008000-count and 0x07000000<=dst<=0x07000400-count
 a.put(dst,a.read(src,count));a.put(0x040000b8,struct.pack('<I',flags&0x7fffffff))
 transfers[id(a)].append((src,dst,count))
try:
 # Use the actual native rotation callback to derive each phase; never
 # relabel mismatching live frames or edit their recorded palette samples.
 phase=machine(rom);initial=phase.read(0x03003860,1024)
 for tick in range(64):
  row=phase.read(0x03003860,1024)
  if row not in phase_rows:phase_rows.append(row)
  for task in (0x03003c7c,0x03003cb4):phase.call(0x08146864,task)
 check('all seven native BG phases derived',len(phase_rows),7)
 for row in phase_rows:check('native phase callback range',row[:324]+row[352:],initial[:324]+initial[352:])
 original,active=machine(control),machine(rom)
 for a in (original,active):
  for pc in (0x08001322,0x08001396,0x080013e2,0x08001430):a.u.hook_add(UC_HOOK_CODE,dma,user_data=a,begin=pc,end=pc)
 if args.current and not args.profile:
  # A rotation may precede the first custom emission and never start a fade.
  # Its display latch must still follow native fresh/skipped palette DMA.
  for kind,pc,callback in (('rotate',0x08146fb8,0x08146864),('cycle',0x08147068,0x08146bb0)):
   case=('unseen rotation latch',kind)
   a=machine(rom)
   for point in (0x08001322,0x08001396,0x080013e2,0x08001430):a.u.hook_add(UC_HOOK_CODE,dma,user_data=a,begin=point,end=point)
   a.put(BASE+2572,bytes(4));a.call(meta['symbols']['ffta_art_heap_reset'])
   a.put(0x03003a60,rom[0x419d60:0x419d80])
   a.put(STACK,struct.pack('<2I',1,0x08419d60))
   task=a.call(pc,257,271,6,1)
   a.call(callback,task);a.call(callback,task)
   binding=BASE+meta['bindingOffset']+252;visible=BASE+meta['visibleColorsOffset']+32
   check('rotation-only history has no fade starts',a.word(BASE+meta['bindingOffset']+2840),0)
   check('unseen rotation has no emitted owners',a.read(BASE+5596,8),bytes(8))
   check('rotation changed colors after initial pretracking',a.read(binding,32)!=a.read(visible,32),True)
   before=a.read(visible,32);a.put(0x03000e10,struct.pack('<H',1));transfers[id(a)]=[];a.call(0x080012bc)
   check('skipped DMA retains prior unseen latch',a.read(visible,32),before)
   a.put(0x03000e10,bytes(2));transfers[id(a)]=[];a.call(0x080012bc)
   check('fresh DMA latches unseen rotation history',a.read(visible,32),a.read(binding,32))
   check('unseen rotation does not fabricate an overlay',a.word(BASE+2572),0)
 for phase_id,skipped,residue in itertools.product(range(7),(0,1),(0,4)):
  if args.profile and (phase_id or residue):continue
  case=(phase_id,skipped,residue)
  for a in (original,active):
   a.put(0x02000000,saved['ram']);a.put(0x03000000,saved['iwram']);a.put(0x06000000,saved['vram']);a.put(0x07000000,saved['oam'])
   if args.repeat_frame:a.put(BASE+meta['repeatOffset'],bytes(meta['repeatBytes']))
   palette=bytearray(saved['palette']);mask=a.word(BASE+2572)
   # Same input as restoration before composition: remove the preceding
   # custom overlay using its retained native backups and retire active.
   for bank in range(16):
    if mask&(1<<bank):palette[512+bank*32:544+bank*32]=a.read(BASE+2060+bank*32,32)
   a.put(BASE+2572,bytes(4));a.put(0x03003860,phase_rows[phase_id]);a.put(0x03000e10,struct.pack('<H',skipped))
   # On skipped-DMA frames hardware keeps its prior native phase; on fresh
   # DMA it receives current shadow, exactly as the two native cases require.
   a.put(0x05000000,palette if skipped else phase_rows[phase_id])
   transfers[id(a)]=[]
   if args.profile and a is active:
    instruction_counts.clear();hook=a.u.hook_add(UC_HOOK_CODE,profile)
   a.call(0x080012bc,stack=STACK+residue)
   if args.profile and a is active:a.u.hook_del(hook)
   if args.repeat_frame and a is active:
    repeat=BASE+meta['repeatOffset'];check('Actual mixed footprint primed',a.word(repeat),1)
    cold_counts=dict(instruction_counts.most_common()) if args.profile else None
    before_hits=a.word(repeat+4)
    a.put(0x03000000,saved['iwram']);a.put(0x03003860,phase_rows[phase_id]);a.put(0x03000e10,struct.pack('<H',skipped))
    a.put(BASE+2572,bytes(4));a.put(0x05000000,original.read(0x05000000,1024));transfers[id(a)]=[]
    if args.profile:instruction_counts.clear();hook=a.u.hook_add(UC_HOOK_CODE,profile)
    a.call(0x080012bc,stack=STACK+residue)
    if args.profile:a.u.hook_del(hook)
    check('Actual repeated native publication hits',a.word(repeat+4),before_hits+1)
  check('identical native DMA transfers',transfers[id(active)],transfers[id(original)])
  check('complete native shadow exact',active.read(0x03003860,1024),phase_rows[phase_id])
  check('native IWRAM below call scratch exact',active.read(0x03000000,0x7000),original.read(0x03000000,0x7000))
  check('complete VRAM exact',active.read(0x06000000,0x18000),original.read(0x06000000,0x18000))
  check('all EWRAM outside owned reservation exact',active.read(0x02000000,BASE-0x02000000)+active.read(LIMIT,0x02040000-LIMIT),original.read(0x02000000,BASE-0x02000000)+original.read(LIMIT,0x02040000-LIMIT))
  mask=active.word(BASE+2572);check('generated overlay present',mask!=0,True)
  check('no new allocation failure',active.word(BASE+2584),original.word(BASE+2584))
  check('no new unsupported operations',active.read(BASE+meta['refusalOffset'],16),original.read(BASE+meta['refusalOffset'],16))
  tags=active.read(BASE+meta.get('tagOffset',2608),128);oam=active.read(0x07000000,1024);old=original.read(0x07000000,1024);banks=set()
  for i,tag in enumerate(tags):
   a,b,c,d=struct.unpack_from('<4H',oam,i*8);old_a,old_b,old_c,old_d=struct.unpack_from('<4H',old,i*8)
   if tag<meta.get('historySlots',10):
    check('owned OAM changes only palette bank',(a,b,c&4095,d),(old_a,old_b,old_c&4095,old_d));bank=c>>12;banks.add(bank)
    check('owned bank exact generated phase',active.read(0x05000200+bank*32,32),active.read(BASE+meta['visibleColorsOffset']+tag*32,32))
   else:check('all unowned OAM bytes exact',oam[i*8:i*8+8],old[i*8:i*8+8])
  check('active mask equals actual remapped banks',mask,sum(1<<bank for bank in banks))
  expected_palette=bytearray(original.read(0x05000000,1024))
  for bank in banks:expected_palette[512+bank*32:544+bank*32]=active.read(0x05000200+bank*32,32)
  check('every unowned hardware color exact',active.read(0x05000000,1024),bytes(expected_palette))
  records.append(dict(phase=phase_id,skippedDMA=skipped,stackResidue=residue,banks=sorted(banks),paletteSha256=sha(active.read(0x05000000,1024)),nativeShadowSha256=sha(phase_rows[phase_id])))
  if args.profile:records[-1]['instructionLocations']=dict(instruction_counts.most_common())
  if args.profile and args.repeat_frame:records[-1]['coldInstructionLocations']=cold_counts
 report=dict(status='passed',romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),source=str(source),sourceHashes=expected,records=records,scope='Installed compositor versus exact original entry on identical retained battle data, all seven actual native BG phases, fresh/skipped palette DMA inputs and both stack alignments. Exact unowned colors/OAM, native shadow/VRAM and memory outside owned storage. Synchronous native DMA0 model, not real VBlank timing, scheduler equivalence, all scenes or final art.')
 if args.profile:report['scope']='Instruction-location diagnostic of current compiled compositor on authenticated retained raw battle inputs, one native phase, fresh/skipped DMA and stack residue0. Same native/output isolation checks, synchronous DMA model. Counts are not hardware cycles or a timing acceptance claim; no saved actor animation executes.'
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),case=case,checks=dict(checks),records=records),indent=2)+'\n');print(out);raise
