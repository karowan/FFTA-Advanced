"""Paired palette-composition cost from identical authenticated saved states.

Private diagnostic ROM normally restores only the original12BC entry. Optional
planner bypass instead disables its exact four-byte call and retains the complete
custom compositor. Both keep assets and exact saved CPU/game state. No deployment replay,
player save, package change or timing acceptance follows from this experiment.
"""
import argparse,collections,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cpu-profile',action='store_true');parser.add_argument('--status-fast',action='store_true');parser.add_argument('--current',action='store_true');parser.add_argument('--candidate-manifest',type=Path,default=ROOT/'build/art/live-palette/poc.json')
parser.add_argument('--planner-bypass',action='store_true',help='Keep the complete compositor; bypass only its optional scoped planner call to compare the existing ROM planner on the identical state.')
parser.add_argument('--retained-report',type=Path,help='Reuse an exact-ROM ready state already saved by a completed battle run, including a failed run; diagnostic only.')
args=parser.parse_args();assert not args.retained_report or args.current
assert not args.planner_bypass or args.current
sources=[
 ('21052ed615a6463251cba9b98952b4cc07ba4546','20260918T070700.550270Z','85c7cb3fff9cbf67e9f84c6e452e6023fd3fbdaf3d1d18bb90a363bc2df389ca','43270a7f2985e94387afe45bce707035fff67f4998ca41ad366fd0016e5e6d70'),
 ('cd390d3560ecd9e87279672a6f18b932d306ee01','20260918T072556.059316Z','6f49cfb452348cda38bc7d2004efc393dc62b0f9631a16c12bb756b0e6404972','4e043080e72ecd953aa650450293aabe9d90ab2354db368a6e0a9e688e1caee5')]
if args.cpu_profile:sources=sources[:1]
if args.status_fast:
 sources=[('29453def10826d971c689b6169a316b182c2fda1','20260918T075021.733381Z','35b26fea1f86929b3d0a98ac34d28badf4be82631aa165ac30b97664a201bc76','8a7d3962ca8adfe77caa26de4c2a2a1ec85a3f62946faf772663c8dd32378d97')]
out=ROOT/'build/art/compose-cost'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records={};e=None
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 if args.current:
  selected=json.loads(args.candidate_manifest.read_text())
  if args.retained_report:
   folder=args.retained_report.parent;retained=json.loads(args.retained_report.read_text())
   pin=dict(romSha1=retained['romSha1'],directory=str(folder),reportSha256=sha(args.retained_report.read_bytes()),
    stateSha256=sha((folder/'candidate-ready.state').read_bytes()),ramSha256=sha((folder/'candidate-ready.ram').read_bytes()),
    iwramSha256=sha((folder/'candidate-ready.iwram').read_bytes()))
  else:pin=json.loads((Path(selected['path']).parent/'cost-fixture.json').read_text())
  check(pin['romSha1']==selected['romSha1'],'saved animation pointers require exact candidate identity')
  sources=[(pin['romSha1'],Path(pin['directory']).name,pin['reportSha256'],pin['stateSha256'])]
 for digest,stamp,report_hash,state_hash in sources:
  source=ROOT/'build/art/live-palette/battle'/stamp
  report_path=args.retained_report if args.retained_report else source/('observed.json' if args.current else 'failed.json')
  raw=report_path.read_bytes();state=source/'candidate-ready.state'
  check(sha(raw)==report_hash and sha(state.read_bytes())==state_hash,digest+' original report/state authenticated')
  retained=json.loads(raw);fixture_meta=json.loads((ROOT/'build/art/live-palette'/digest/'manifest.json').read_text())
  meta=json.loads(args.candidate_manifest.read_text()) if args.current else fixture_meta
  rom=Path(meta['path']).read_bytes()
  check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],digest+' selected ROM authenticated')
  if args.current:
   check(retained['romSha1']==meta['romSha1']==digest,'captured actors reference this exact ROM')
   check(sha((source/'candidate-ready.ram').read_bytes())==pin['ramSha256'] and sha((source/'candidate-ready.iwram').read_bytes())==pin['iwramSha256'],'captured ready memory authenticated')
   for field in ('ramReservation','transientStateBytes','bindingOffset','bindingEntryBytes','visibleColorsOffset','profileOffset','refusalOffset','variantOffset','paletteSha256','generatedSourceSha256','baseRomSha1'):
    check(meta[field]==fixture_meta[field],'current candidate retains fixture contract '+field)
  if args.planner_bypass:
   check(bool(meta.get('scopedPlanner')),'Scoped planner declared')
   site=meta['symbols']['ffta_art_palette_live_apply']-0x08000000+16
   first,second=struct.unpack_from('<2H',rom,site)
   high=first&2047;high=high-2048 if high&1024 else high
   destination=0x08000000+site+4+(high<<12)+((second&2047)<<1)
   check(first&0xf800==0xf000 and second&0xf800==0xf800 and destination==meta['symbols']['__ffta_art_palette_scoped_call_from_thumb'],'Exact native Thumb call to scoped wrapper')
   check(rom[site+4:site+10].hex()=='041e06d00120','Zero return enters existing complete ROM planner')
   change=dict(offset=site,before=rom[site:site+4].hex(),after='0020c046')
   bypass=bytearray(rom);bypass[site:site+4]=bytes.fromhex(change['after'])
   check(bypass[:site]==rom[:site] and bypass[site+4:]==rom[site+4:],'Only four-byte optional planner call disabled')
  else:
   change=next(x for x in meta['changes'] if x['offset']==0x12bc)
   check(rom[0x12bc:0x12c4].hex()==change['after'] and change['before']=='f0b557464e464546',digest+' exact eight-byte composition hook identified')
   bypass=bytearray(rom);bypass[0x12bc:0x12c4]=bytes.fromhex(change['before'])
   check(bypass[:0x12bc]==rom[:0x12bc] and bypass[0x12c4:]==rom[0x12c4:],digest+' only original compositor entry restored')
  folder=out/digest;folder.mkdir();control=folder/'compose-bypass.gba';control.write_bytes(bypass)
  records[digest]=dict(source=str(source),reportSha256=report_hash,sourceStatus=retained['status'],stateSha256=state_hash,activeSha1=meta['romSha1'],plannerBypass=args.planner_bypass,controlPatch=dict(offset=change['offset'],before=rom[change['offset']:change['offset']+(4 if args.planner_bypass else 8)].hex(),after=bypass[change['offset']:change['offset']+(4 if args.planner_bypass else 8)].hex()),bypassSha1=hashlib.sha1(bypass).hexdigest(),cases={})
  for name,path in [('active',Path(meta['path'])),('bypass',control)]:
   e=E(path);e.load(state);ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);wrapper=from_emulator(rom,e)[0x290]
   check(ram==(source/'candidate-ready.ram').read_bytes() and iw==(source/'candidate-ready.iwram').read_bytes(),digest+'/'+name+' starts from exact identical RAM/IWRAM')
   if args.current:
    start_cpu=C.create_string_buffer(e.core.retro_serialize_size());assert e.core.retro_serialize(start_cpu,len(start_cpu))
    registers=struct.unpack_from('<16I',start_cpu,0x20)
    check(registers[15]==0x0800042a,'retained CPU is waiting in unchanged native foreground code')
    check(registers[14]<0x091f0000,'retained live return address is outside relocated art stage')
   rows={};cpu_buffer=C.create_string_buffer(e.core.retro_serialize_size()) if args.cpu_profile else None
   for key in (256,128,128,128):e.run(8,key);e.run(180)
   for action,key,initial,target in [('move',256,48,144),('cancel',1,144,48)]:
    e.run(8,key)
    for tick in range(600):
     e.run(1);ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);position=list(struct.unpack_from('<3H',ram,wrapper+8));label=action+'-'+str(tick)
     rows[label]=dict(position=position,skippedDMA=struct.unpack_from('<H',iw,0xe10)[0],cycleHead=struct.unpack_from('<I',iw,0x3c64)[0],shadowCycles=iw[0x39a4:0x39c0].hex(),profile=list(struct.unpack_from('<4H',ram,meta['ramReservation'][0]-0x02000000+meta['profileOffset'])))
     if cpu_buffer is not None:
      # mGBA format11: CPU GPRs at20, CPSR at60. Sample only; never reload
      # or change CPU state. Frame-boundary PCs are not cycle percentages.
      assert e.core.retro_serialize(cpu_buffer,len(cpu_buffer))
      assert struct.unpack_from('<I',cpu_buffer)[0]==0x0100000b
      registers=struct.unpack_from('<16I',cpu_buffer,0x20)
      rows[label]['cpu']=dict(pc=registers[15],lr=registers[14],sp=registers[13],cpsr=struct.unpack_from('<I',cpu_buffer,0x60)[0])
     if name=='active' and not args.current:check(position==retained['observations']['candidate'][label]['position'],digest+'/'+label+' active replay reproduces retained position')
    check(position==[target,32,432],digest+'/'+name+'/'+action+' exact final native position')
   unit_label='ready' if args.current else 'returned'
   check(sha(ram[0x80:0x1e70])==retained['paletteTraces']['candidate'][unit_label]['units'],digest+'/'+name+' canonical final unit state matches retained gameplay result')
   e.close();e=None
   motion={}
   for action,initial,target in [('move',48,144),('cancel',144,48)]:
    selected=[(int(label.rsplit('-',1)[1]),row) for label,row in rows.items() if label.startswith(action+'-')]
    start=next(t for t,row in selected if row['position'][0]!=initial);end=next(t for t,row in selected if row['position'][0]==target)
    motion[action]=dict(start=start,end=end,elapsed=end-start)
   records[digest]['cases'][name]=dict(motion=motion,observations=rows)
   if args.cpu_profile:
    records[digest]['cases'][name]['pcSamples']=[dict(pc=pc,samples=count) for pc,count in collections.Counter(row['cpu']['pc'] for row in rows.values()).most_common()]
  for action in ('move','cancel'):
   a=records[digest]['cases']['active']['motion'][action];b=records[digest]['cases']['bypass']['motion'][action]
   records[digest].setdefault('activeMinusBypass',{})[action]={k:a[k]-b[k] for k in a}
 report=dict(status='passed',checks=checks,records=records,cpuProfile=args.cpu_profile,currentCandidate=args.current,
  scope='Identical retained state per candidate, only compositor hook bypassed in private diagnostic ROM; active position trace reproduced and final gameplay records preserved. Measures composition cost relative to its own starting phase, not complete parent/candidate or final-art acceptance.')
 if args.current:report['scope']='Exact current ROM/state identity, including saved animation pointers, at authenticated native wait point; identical active/bypass state and final gameplay records. This is diagnostic, not native scheduler equivalence or battle acceptance. Earlier layout-only cross-ROM timing experiments are invalid.'
 if args.planner_bypass:report['scope']='Identical exact-ROM ready state; only optional fast planner call is disabled in the control, retaining complete custom compositor and ROM fallback planner. Matched-state movement/cancel and planner scanline metrics. Not broad timing, phase or final-art acceptance.'
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),comparisons={k:dict(delta=v['activeMinusBypass'],motion={n:c['motion'] for n,c in v['cases'].items()}) for k,v in records.items()},report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,records=records),indent=2)+'\n');print(out);raise
finally:
 if e:e.close()
