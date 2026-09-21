"""Native party lesson-list iteration, ABI, filtering and real UI regression."""
import ctypes as C, hashlib, json, pathlib, runpy, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
a=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
OUT=ROOT/'build/expansion/probes/party-command-lists';OUT.mkdir(exist_ok=True)
manifest=json.loads((OUT.parent/'command-core.json').read_text())
ROM=(OUT.parent/'command-core.gba').read_bytes();CLEAN=(OUT.parent/'command-data.gba').read_bytes()
engine=(ROOT/'build/expansion/engine.bin').read_bytes();symbol_text=(ROOT/'build/expansion/engine.symbols').read_text()
assert hashlib.sha1(ROM).hexdigest()==manifest['romSha1'],'Stale command-core manifest'
assert hashlib.sha1(CLEAN).hexdigest()==manifest['baseSha1'],'Stale native-loop baseline'
assert hashlib.sha1(engine).hexdigest()==manifest['engineSha1'],'Stale compiled engine'
assert ROM[0x1100000:0x1100000+len(engine)]==engine,'Embedded engine differs'
assert (ROOT/'build/expansion/engine.symbols').read_text()==symbol_text,'Symbols changed while freezing'
assert (ROOT/'build/expansion/engine.bin').read_bytes()==engine,'Engine changed while freezing'
(OUT/'frozen.gba').write_bytes(ROM);(OUT/'native-loops.gba').write_bytes(CLEAN)
(OUT/'engine.bin').write_bytes(engine);(OUT/'engine.symbols').write_text(symbol_text)
IW=a['native_iwram']();UNIT=0x02000080;MENU=0x02008000;DEST=0x02024000;CURSOR=0x02023000
MEMBERS={2:list(range(1,12))+list(range(172,178)),16:list(range(33,44))+list(range(105,111))}
COUNTS={1:178,2:111,3:124,4:118,5:116};NATIVE={1:142,2:77,3:95,4:85,5:88}
checks=[]; helper_visits=[]
symbols={line.split()[2]:int(line.split()[0],16) for line in symbol_text.splitlines() if len(line.split())==3}
for patch in manifest['changes']:
 if patch['name'].startswith(('ffta_party_','ffta_primary_','ffta_secondary_')):
  entry=struct.pack('<I',symbols[patch['name']]|1)
  assert entry in ROM[patch['offset']:patch['offset']+patch['size']],('Stale iterator symbol',patch['name'])
def setup(image,job,slot=1,mode=0,live_value=1,preview_value=3,alias=False,original_only=False):
 m=a['ARM'](IW);m.put(0x08000000,image);m.put(0x02000000,bytes(0x40000));m.put(0x02001e70,b'FFTAEXP1\x01')
 bank=m.r32(0x080c8598);record=m.get(bank+job*52,52);race=record[4]
 assert race in COUNTS,(job,race)
 fallback={1:2,2:13,3:20,4:28,5:36}[race]
 data=bytearray(264);data[4]=1;data[5]=0x50 if alias else job;data[6]=race;data[7]=job if record[5]!=255 else fallback
 data[8]=job;data[0x34]=COUNTS[race]
 command=m.call(0x080c8570,job,data[7],0x0c);data[0x35]=command;data[0x36]=command;data[0x37]=1
 m.put(UNIT,data);m.put(MENU+0x1be4,data);m.w32(0x03002818,MENU);m.w32(MENU+0x1d0c,UNIT)
 m.put(0x0203ff30,struct.pack('<5I',0x31525041,0,0,0,MENU));m.put(MENU+0x7240,bytes(36))
 def value(spec,index):return spec(index) if callable(spec) else spec
 for index in range(1,COUNTS[race]):
  if race==1 and index in (142,143):continue
  for pointer,spec,extra in [(UNIT,live_value,0x02001b40),(MENU+0x1be4,preview_value,MENU+0x7240)]:
   val=0 if original_only and index>=NATIVE[race] else value(spec,index)
   address=extra+index-144 if race==1 and index>=144 else pointer+0x40+index
   m.put(address,bytes([val]))
 m.put(MENU+0xbf9,bytes([slot]));m.put(MENU+0x1131,bytes([slot-1]));m.put(MENU+0x1133,b'\0');m.put(MENU+0x1134,bytes([1 if mode==1 else command]))
 m.put(DEST-16,b'\xDA'*16);m.put(DEST,bytes(0x2000));m.put(DEST+0x2000,b'\xDB'*16)
 m.put(0x0203ff44,b'\xDC'*0xbc)
 return m,race

def build(m,which,slot=1):
 ids=[]
 def row(u,pc,size,data):ids.append(u.reg_read(UC_ARM_REG_R6))
 hooks=[m.u.hook_add(UC_HOOK_CODE,row,begin=pc,end=pc) for pc in [0x0807b9be,0x0807c37c,0x0807c4c2]]
 def helper(u,pc,size,data):
  sp=u.reg_read(UC_ARM_REG_SP);assert sp%8==0,('C alignment',hex(pc),hex(sp));helper_visits.append(sp)
 address=symbols['ffta_command_successor']&~1
 hooks.append(m.u.hook_add(UC_HOOK_CODE,helper,begin=address,end=address))
 before_ap=m.get(0x02001b40,816);before_live=m.get(UNIT,264);before_copy=m.get(MENU+0x1be4,264)
 before_tail=m.get(MENU+0x7240,36)
 try:result=m.call(0x0807b928,0,slot,DEST) if which=='learned' else m.call(0x0807c28c,DEST,CURSOR)
 finally:
  for hook in hooks:m.u.hook_del(hook)
 count=m.r32(DEST);assert count==len(ids),(which,count,ids)
 assert m.get(DEST-16,16)==b'\xDA'*16 and m.get(DEST+0x2000,16)==b'\xDB'*16,'List allocation guard'
 assert m.get(0x0203ff44,0xbc)==b'\xDC'*0xbc,'Owner/view guard'
 assert m.get(0x02001b40,816)==before_ap,'List changed live Human AP'
 assert m.get(UNIT,264)==before_live,'List changed source unit'
 assert m.get(MENU+0x7240,36)==before_tail,'List changed preview AP'
 after_copy=m.get(MENU+0x1be4,264)
 assert all(a==b or i in (8,0x36) for i,(a,b) in enumerate(zip(before_copy,after_copy))),'Preview mutation outside native secondary selection'
 rows=[m.get(DEST+0x230+20*i,20) for i in range(count)]
 return {'count':count,'ids':ids,'rows':[x.hex() for x in rows],'ap':[x[14] for x in rows],
         'result':result,'cursor':m.r32(CURSOR),'header':m.get(DEST,28).hex()}

def original_differential():
 table=struct.unpack_from('<I',CLEAN,0xc8598)[0]-0x08000000;jobs=[]
 for job in range(2,116):
  record=CLEAN[table+job*52:table+(job+1)*52]
  if record[4] not in COUNTS or job in MEMBERS:continue
  # Original secondary-command reverse lookup accepts playable job records.
  slots=(1,2) if job<=43 else (1,)
  for slot in slots:
   for which in ['learned','edit']:
    for val in [0,1,0x80,0xe4]:
     outputs=[]
     for image in [CLEAN,ROM]:
      m,race=setup(image,job,slot,live_value=val,preview_value=val,original_only=True)
      outputs.append(build(m,which,slot))
     for output in outputs: output.pop('header') # Header name-table pointer relocates intentionally.
     assert outputs[0]==outputs[1],('Original differential',job,slot,which,val,outputs)
     checks.append(['original',job,slot,which,val])
  jobs.append(job)
 return jobs

def expanded_cases():
 cases=[]
 for job,order in MEMBERS.items():
  for slot in [1,2]:
   for which in ['learned','edit']:
    for mode in [0]:
     for profile in ['none','partial','available','all','added-only']:
      values={i:(0 if profile=='none' else (1 if n%2 else 0) if profile=='partial' else 128 if profile=='available' else 1 if profile=='all' else int(n>=11)) for n,i in enumerate(order)}
      m,race=setup(ROM,job,slot,mode,lambda i:values.get(i,0),lambda i:7 if i in order else 0)
      m.put(MENU+0x1c19,bytes([order[-1]]))
      result=build(m,which,slot)
      expected=[]
      for index in order:
       record=m.get(m.call(0x080cd480,race,index),8)
       if (which=='edit' and slot==2 and mode==1) or values[index] and record[6]:expected.append(index)
      assert result['ids']==expected,('Explicit membership',job,slot,which,mode,profile,result,expected)
      expected_ap=[(values[i] if which=='learned' else 7) if m.get(m.call(0x080cd480,race,i),8)[7] or which=='learned' else 255 for i in expected]
      assert result['ap']==expected_ap,('Preview AP owner',job,slot,which,profile,result['ap'],expected_ap)
      if which=='edit' and slot==2 and order[-1] in expected:assert result['cursor']==expected.index(order[-1]),('Cursor real-ID mapping',result)
      cases.append({'job':job,'slot':slot,'builder':which,'mode':mode,'profile':profile,**result})
 return cases

def item_bypass():
 for job in MEMBERS:
  for val in [0,1,128,228]:
   results=[]
   for image in [CLEAN,ROM]:
    m,_=setup(image,job,2,1,val,val);results.append(build(m,'edit',2))
   assert results[0]==results[1],('Native Item bypass',job,val)
   assert results[1]['count']>0,('Item bypass empty with zero AP',job,val)
   checks.append(['item-bypass',job,val])

def actual_ui():
 h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));seed=ROOT/'build/test-lab/early-town.sav';original=seed.read_bytes();cases=[]
 def tap(e,key,wait=60):e.run(8,key);e.run(wait)
 def context(e):return struct.unpack_from('<I',C.string_at(*e.maps[0x03000000]),0x2818)[0]-0x02000000
 for job,roster in [(2,0),(16,3)]:
  e=h['Emulator'](OUT/'frozen.gba')
  try:
   e.set_memory(0,original,0);e.run(3600);tap(e,8,180);tap(e,256);tap(e,256);tap(e,256,180)
   offset=0x80+264*roster;unit=bytearray(e.memory()[offset:offset+264]);order=MEMBERS[job]
   machine,race=setup(ROM,job);command=machine.get(UNIT+0x35,1)[0]
   # Preserve the valid seed unit's identity, gear and stats. Only its test job,
   # selected commands and AP change, before the native menu creates its copy.
   if job!=2:unit[5]=job
   unit[7]=unit[8]=job;unit[0x34]=COUNTS[race];unit[0x35]=unit[0x36]=command
   for index in range(1,min(COUNTS[race],142 if race==1 else COUNTS[race])):unit[0x40+index]=0
   for index in order:
    if index<144:unit[0x40+index]=129
   e.set_memory(offset,bytes(unit))
   flag=job+3;flag_base=struct.unpack_from('<I',ROM,0xc9568)[0]-0x02000000
   address=flag_base+(flag>>3);e.set_memory(address,bytes([e.memory()[address]|(1<<(flag&7))]))
   if race==1:
    extra=bytearray(34)
    for index in order:
     if index>=144:extra[index-144]=129
    e.set_memory(0x1b40+roster*34,bytes(extra))
   before=e.memory();e.set_memory(0x3ff44,b'\xDC'*0xbc)
   tap(e,8);tap(e,256,120)
   for _ in range(roster):tap(e,128)
   tap(e,256,120);tap(e,32);tap(e,256,120)
   # Native party entry refreshes the two-byte unit checksum after fixture
   # job/AP edits. Preview/cancel must preserve the resulting valid unit.
   before=e.memory()
   e.save(OUT/f'job-{job}-pick.state')
   for view in ['current-command','secondary-command']:
    if view=='secondary-command':
     e.load(OUT/f'job-{job}-pick.state');e.run(1);tap(e,256,120)
     r=e.memory();ctx=context(e)
     commands=list(r[ctx+0x1134:ctx+0x1134+r[ctx+0x1132]])
     assert command in commands,('Native command selection unavailable',job,command,commands)
     for _ in range(commands.index(command)):tap(e,32)
    tap(e,2048,120) # libretro R is bit11, not X/bit9.
    r=e.memory();ctx=context(e);dest=struct.unpack_from('<I',r,ctx+0x2e1c)[0]-0x02000000
    count=struct.unpack_from('<I',r,dest)[0];assert count==17,(job,view,count)
    rows=[r[dest+0x230+i*20:dest+0x244+i*20] for i in range(count)]
    records=[machine.get(machine.call(0x080cd480,race,i),8) for i in order]
    assert [struct.unpack_from('<H',row,8)[0] for row in rows]==[struct.unpack_from('<H',record)[0] for record in records],('Rendered row identities',job,view)
    assert [row[14] for row in rows]==[129]*17,('Rendered AP owner',job,view)
    e.screenshot(OUT/f'job-{job}-{view}-first.png')
    for _ in range(16):tap(e,32,24)
    e.screenshot(OUT/f'job-{job}-{view}-last.png')
    r=e.memory();assert r[0x3ff44:]==b'\xDC'*0xbc,'Actual party guard'
    assert (r[ctx+0x2d8a],r[ctx+0x2de6],r[ctx+0x2dfd])==(16,12,4),('Last-row navigation',job,view)
    assert r[0x1b40:0x1e70]==before[0x1b40:0x1e70],'Actual menu changed sidecar AP'
    assert r[offset:offset+264]==before[offset:offset+264],('Actual preview changed source unit',job,view,[(hex(i),a,b) for i,(a,b) in enumerate(zip(before[offset:offset+264],r[offset:offset+264])) if a!=b])
    cases.append({'job':job,'view':view,'count':count,'lessonIds':order,'rowAP':[row[14] for row in rows],
                  'context':hex(ctx+0x02000000),'destination':hex(dest+0x02000000),'slot':r[ctx+0xbf9], 'mode':r[ctx+0x1131]})
  finally:e.close()
 assert seed.read_bytes()==original
 return cases

jobs=original_differential() if '--ui-only' not in sys.argv else []
item_bypass() if '--ui-only' not in sys.argv else None
if '--baseline-only' not in sys.argv:
 expanded=expanded_cases() if '--ui-only' not in sys.argv else []
else:expanded=[]
ui=actual_ui() if '--baseline-only' not in sys.argv else []
report={'passed':True,'romSha1':hashlib.sha1(ROM).hexdigest(),'originalJobs':jobs,'originalComparisons':len(checks),'expandedCases':expanded,
        'baseSha1':hashlib.sha1(CLEAN).hexdigest(),'engineSha1':hashlib.sha1(engine).hexdigest(),
        'symbolsSha1':hashlib.sha1(symbol_text.encode()).hexdigest(),
        'actualUI':ui,'alignedHelperVisits':len(helper_visits),
        'scope':'Native primary/secondary learned/edit builders; actual current-command and secondary-command browse UI',
        'limitations':['Both rendered browse routes retain native mode1131=1; mode0 primary edit branch is directly executed in ARM, not separately reached through normal menu navigation',
                       'Disposable fixture gives the existing Bangaa Gladiator job and unlock flag; it does not prove natural prerequisite progression or new combat effects']}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':True,'originalComparisons':len(checks),'expandedCases':len(expanded)}))
