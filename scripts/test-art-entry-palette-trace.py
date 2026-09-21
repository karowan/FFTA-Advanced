"""Read-only attribution of the first retained deployment palette divergence.

Replay only entry6 to entry7. Preserve raw paired phases, and compare every
observed complete machine state/frame to a fresh ordinary replay of that ROM.
This diagnoses the original entry failure; it does not waive or replace it.
"""
import argparse,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from mgba_instruction_trace import InstructionTrace,INSTRUCTION
from art_fused_trace import FusedTrace
from art_composition_costs import cost_sites,summarize_costs
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--composition-costs',action='store_true')
parser.add_argument('--input-index',type=Path,help='Committed manifest/source/hash index for another exact-ROM retained entry checkpoint.')
args=parser.parse_args()

class PaletteWrites(FusedTrace):
 def __init__(self,*args):
  super().__init__(*args);self.writes=[]
  groups=set(range(0x6000>>6,0x6800>>6))|set(range(0x8000>>6,0x8800>>6))|set(range(0x5000>>6,0x5400>>6))
  for index in groups:
   self.handlers[index]=INSTRUCTION(self.original_entries[index]);self.table[index]=C.cast(self.callback,C.c_void_p).value
 def _instruction(self,cpu,opcode):
  try:
   size=0
   if opcode&0xf800==0x6000:size=4;offset=((opcode>>6)&31)*4
   elif opcode&0xf800==0x8000:size=2;offset=((opcode>>6)&31)*2
   elif opcode&0xfe00 in (0x5000,0x5200):
    size=4 if opcode&0xfe00==0x5000 else 2;offset=self.registers[(opcode>>6)&7]
   if size:
    address=(self.registers[(opcode>>3)&7]+offset)&0xffffffff
    if address<0x03003bb2 and address+size>0x03003ba4:
     self.writes.append(dict(pc=self.registers[15]-4,lr=self.registers[14],address=address,bytes=size,
      value=self.registers[opcode&7]&((1<<(size*8))-1),videoFrame=self.frame_counter(self.core),
      nativeFrame=self.iw[0xeb4]|self.iw[0xeb5]<<8,registers=list(self.registers[:17])))
   pc=self.registers[15]-4
   if pc in (0x080ba66c,0x080ba69a):
    address=self.registers[0 if pc==0x080ba66c else 7]+0xa0;pointer,length=self.emulator.maps[0x02000000]
    assert 0x02000000<=address<0x02000000+length
    self.writes.append(dict(kind='deployment-cycle-counter',pc=pc,address=address,
     value=C.c_uint8.from_address(pointer+address-0x02000000).value,videoFrame=self.frame_counter(self.core)))
  except BaseException as error:self.error=repr(error)
  super()._instruction(cpu,opcode)

SOURCE=ROOT/'build/art/live-palette/battle/20260919T053401.085987Z'
META=ROOT/'build/art/connected/390e4b0420c546f7afb2c78d5771924e0b3c308e/live-palette-view.json'
PINS={
 'failed.json':'109ad4d236e7823c4085f34609e73aee68a0d931a70094c1cd7eab1d72cba50a',
 'parent-entry-6.state':'f333798424ed21f8f428ff71e94abd6450e048adac0de21e737a1c2bf85572c3',
 'parent-entry-6.ram':'ca853c10314ded0866cde3a2e19b88aad29f6e3d978147cd1a2a1c608bd9b000',
 'parent-entry-6.iwram':'d543851a60f295dce7d9c69765af6d46b984e4440083350c86094edb5a6c4639',
 'candidate-entry-6.state':'a9105542c87c54bbd16fe2a128afcc1667d708422a7cc34938527e58881df753',
 'candidate-entry-6.ram':'51270aaf8cf3ef6fdd51dc21480513d9698f8aa261ad5f226dc83ab3abb2cbf1',
 'candidate-entry-6.iwram':'4d5abced005c166ea8e74f0892a21dd985e1e090ea594f65b8c15ac0fbf67707',
}
if args.input_index:
 index=json.loads(args.input_index.read_text(encoding='utf-8'))
 assert set(index['inputHashes'])==set(PINS),'Complete retained source set required'
 SOURCE=ROOT/index['source'];META=ROOT/index['manifest'];PINS=index['inputHashes']
SITES={0x08146870:'native-rotate-start',0x08146b9e:'native-rotate-end',
       0x080ba66c:'deployment-cycle-start',0x080ba69a:'deployment-cycle-end',
       0x080012bc:'compose',0x080004dc:'compose-return',
       0x080004c8:'vblank-flag-check',0x0800042e:'foreground-return'}
SNAPS={pc:dict(shadow=(0x03003860,1024),tasks=(0x03003c60,1024)) for pc in SITES}
out=ROOT/'build/art/entry-palette-trace'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records=[];e=None
def check(ok,label):assert ok,label;checks.append(label)
def frame_hash(frame):
 raw,w,h,pitch,pixel=frame
 return sha(struct.pack('<4I',w,h,pitch,pixel)+raw)
try:
 for name,pin in PINS.items():check(sha((SOURCE/name).read_bytes())==pin,'Pinned '+name)
 retained=json.loads((SOURCE/'failed.json').read_text());meta=json.loads(META.read_text())
 check(retained['status']=='failed' and retained['error']=='candidate/ready paired native palette shadow preserved','Original failure retained unchanged')
 E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
 original=Path(retained['statusControl']['path']).read_bytes()
 for case,path,digest in (('parent',Path(retained['statusControl']['path']),retained['statusControl']['romSha1']),('candidate',Path(meta['path']),meta['romSha1'])):
  rom=path.read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,case+' exact ROM')
  check(rom[0x146870:0x146874].hex()=='061c0c30' and rom[0x146b9e:0x146ba0].hex()=='09b0',case+' native rotation observation boundaries authenticated')
  check(rom[0xba66c:0xba69a]==original[0xba66c:0xba69a],case+' unchanged original deployment cycling code')
  check(struct.unpack_from('<I',rom,0xba6c8)[0]==0x03003ba4,case+' original literal targets exact divergent color range')
  sites=dict(SITES);snapshots=dict(SNAPS);cost_proof=None
  if args.composition_costs and case=='candidate':
   measured,cost_proof=cost_sites(meta,rom,extra_callers=('ffta_art_live_palette_copy',))
   check(not (set(measured)&set(sites)),case+' distinct cost boundaries');sites.update(measured)
   site=meta['symbols']['ffta_art_palette_live_apply_fused']&~1
   sites[site]='fused-apply'
   snapshots[site]=dict(oam=(0x07000000,1024),tags=(meta['ramReservation'][0]+meta['tagOffset'],128))
  keys=[256]*8+[0]*600;baseline=[];initial=None
  for observed in (False,True):
   e=E(path);e.load(SOURCE/(case+'-entry-6.state'))
   check(e.memory()==(SOURCE/(case+'-entry-6.ram')).read_bytes(),case+' exact initial EWRAM '+str(observed))
   check(C.string_at(*e.maps[0x03000000])==(SOURCE/(case+'-entry-6.iwram')).read_bytes(),case+' exact initial IWRAM '+str(observed))
   trace=PaletteWrites(e,sites,snapshots,meta)
   if not observed:initial=trace.state()
   else:check(initial==trace.state(),case+' identical complete initial states')
   if observed:trace.__enter__()
   frames=[]
   try:
    for tick,key in enumerate(keys):
     e.run(1,key);signature=(sha(trace.state()),frame_hash(e.frame))
     if not observed:baseline.append(signature)
     else:
      check(signature==baseline[tick],case+'/'+str(tick)+' full observed state and framebuffer equal ordinary execution')
      iw=C.string_at(*e.maps[0x03000000]);frames.append(dict(tick=tick,shadow=iw[0x3860:0x3c60].hex()))
   finally:
    if observed:trace.__exit__(None,None,None)
   if observed:
    final=frames[-1]['shadow'];expected=retained['entryPaletteTraces'][case]['entry-7']['nativeShadow']
    check(final==expected,case+' full final shadow reproduces original divergence endpoint')
    pending=None;rotations=[];compose=None;compositions=0;cycle=None;cycles=[];demand_rows=[]
    counters=iter(x for x in trace.writes if x.get('kind')=='deployment-cycle-counter')
    for event in trace.events:
     if event['site']=='fused-apply':
      mem={k:bytes.fromhex(v) for k,v in event['memory'].items()}
      frame=struct.unpack('<8I',mem['frame']);count=struct.unpack('<I',mem['extent'])[0]
      occupied=requested=0;indices=[];valid=True
      check(frame[0]==0x07000000 and frame[2]==meta['ramReservation'][0]+meta['tagOffset'] and frame[7]==20 and count<=128,case+' actual bounded current fused inputs')
      for i in range(count):
       a,b,c=struct.unpack_from('<3H',mem['oam'],i*8);owner=mem['tags'][i]
       if a&0x300==0x200:continue
       if a>>14==3:valid=False;continue
       if owner!=255:
        if owner>=20 or a&0xe100 or b>>14!=2:valid=False
        else:requested|=1<<owner
       elif a&0x2000:indices.append(i)
       else:occupied|=1<<(c>>12)
      check(struct.unpack_from('<3I',mem['demands'])==(occupied,requested,len(indices) if valid else 129) and list(mem['demands'][12:12+len(indices)])==indices,case+' same-call demands exactly equal independent complete current OAM classification')
      demand_rows.append(dict(frame=event['videoFrame'],extent=count,occupied=occupied,requested=requested,eightBitCount=len(indices)))
     if event['site']=='native-rotate-start':
      check(pending is None,case+' no nested native rotation');pending=event
     elif event['site']=='native-rotate-end':
      check(pending is not None,case+' paired native rotation')
      task=pending['registers'][0];off=task-0x03003c60
      check(0<=off<=1024-40,case+' bounded actual native task')
      data=bytes.fromhex(pending['memory']['tasks'])[off:off+40]
      before=bytes.fromhex(pending['memory']['shadow']);after=bytes.fromhex(event['memory']['shadow'])
      changed=[i for i in range(512) if before[i*2:i*2+2]!=after[i*2:i*2+2]]
      rotations.append(dict(frame=pending['videoFrame'],nativeFrame=pending['nativeFrame'],task=task,
       taskBytes=data.hex(),first=struct.unpack_from('<H',data,6)[0],last=struct.unpack_from('<H',data,8)[0],
       changed=changed,before=before.hex(),after=after.hex()))
      pending=None
     elif event['site']=='compose':compose=event
     elif event['site']=='compose-return':
      check(compose is not None and compose['memory']['shadow']==event['memory']['shadow'],case+' actual compositor preserves full native shadow')
      compose=None;compositions+=1
     elif event['site']=='deployment-cycle-start':
      check(cycle is None,case+' no nested deployment cycle');cycle=(event,next(counters))
     elif event['site']=='deployment-cycle-end':
      before,counter=cycle;after_counter=next(counters);value=counter['value'];shadow=bytes.fromhex(before['memory']['shadow'])
      check(0<=value<=5 and counter['pc']==0x080ba66c and after_counter['pc']==0x080ba69a,case+' exact native six-call counter domain')
      expected=shadow[:836]+shadow[838:850]+shadow[836:838]+shadow[850:] if value==5 else shadow
      check(bytes.fromhex(event['memory']['shadow'])==expected,case+' full native shadow equals original seven-color shift or unchanged counter tick')
      check(after_counter['value']==(value+1)%6 and after_counter['address']==counter['address'],case+' exact native counter progression')
      cycles.append(dict(frame=before['videoFrame'],before=value,after=after_counter['value'],rotated=value==5))
      cycle=None
    check(pending is None and compose is None and cycle is None,case+' all observed calls complete')
    check(next(counters,None) is None and len(cycles)>0,case+' all counter observations consumed')
    check(compositions==608,case+' complete composition coverage')
    if cost_proof:check(len(demand_rows)>0,case+' actual deployment fused demands exercised')
    records.append(dict(case=case,romSha1=digest,frames=frames,rotations=rotations,events=trace.events,writes=trace.writes,deploymentCycles=cycles,
     costBoundaries=cost_proof,compositionCosts=summarize_costs(trace.events) if cost_proof else None,fusedDemands=demand_rows))
   e.close();e=None
 for name,pin in PINS.items():check(sha((SOURCE/name).read_bytes())==pin,'Source unchanged '+name)
 result=dict(status='passed',checks=checks,source=str(SOURCE),inputHashes=PINS,manifest=str(META),manifestSha256=sha(META.read_bytes()),records=records,
  nativeDeploymentCodeSha256=sha(original[0xba66c:0xba69a]),
  scope=__doc__+' Original deployment callback080BA66C increments a counter and shifts seven colors on every sixth call. Every complete shadow and actual counter at its observed start/end must match that code exactly. Thumb word/halfword stores are recorded; ARM stores, BIOS and DMA writes are not inferred. All compositor boundaries preserve native shadow. Raw callback counts/phases retained; no entry response or full engineering acceptance.')
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,records=records),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
 if e:e.close()
