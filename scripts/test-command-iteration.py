"""Execute native battle/AI command builders with guarded caller buffers.
Added action definitions below are disposable donor fixtures, not production data.
"""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<harness>','exec'))
out=ROOT/'build/expansion/probes';rom=(out/'command-core.gba').read_bytes();meta=json.loads((out/'command-core.json').read_text());base=(out/'command-data.gba').read_bytes();engine=(ROOT/'build/expansion/engine.bin').read_bytes();symbol_bytes=(ROOT/'build/expansion/engine.symbols').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'];assert hashlib.sha1(base).hexdigest()==meta['baseSha1'];assert hashlib.sha1(engine).hexdigest()==meta['engineSha1'];assert rom[0x1100000:0x1100000+len(engine)]==engine
symbols={p[2]:int(p[0],16) for line in symbol_bytes.decode().splitlines() if len(p:=line.split())==3}
frozen=out/'command-iteration-council'/meta['romSha1'];frozen.mkdir(parents=True,exist_ok=True)
for name,data in [('command-core.gba',rom),('command-data.gba',base),('engine.symbols',symbol_bytes),('command-core.json',json.dumps(meta,indent=2).encode())]:(frozen/name).write_bytes(data)
iwram=iwram_from_boot();checks={};baseline_only='--baseline' in sys.argv
MENU,DESC,IDS,FLAGS,AI,CONTEXT=0x02008000,0x02008400,0x02008500,0x02008800,0x02008a00,0x02009000

def check(group,ok,label):
 assert ok,f'{group}: {label}'
 checks[group]=checks.get(group,0)+1

def setup(image,job,slot,ap_mode='original',mp=20,silence=0,duplicate=False,synthetic17=False):
 m=ARM(image,iwram);m.put(0x02000000,bytes(0x40000));m.put(0x02001e70,b'FFTAEXP1\x01')
 m.put(0x0200f438,struct.pack('<I',CONTEXT));m.put(CONTEXT+0x18,struct.pack('<I',UNIT));m.put(CONTEXT+4,[slot+5])
 m.fixture(2 if job==80 else job,alias=job==80);race=m.read(UNIT+6,1)[0]
 m.put(UNIT+8,[2 if job==80 else job]);m.put(UNIT+0x35,[2 if slot==1 or duplicate else 0,2 if slot==2 or duplicate else 0,0]);m.put(UNIT+0x1c,struct.pack('<H',mp))
 m.silence=silence;m.special=1;m.restricted=1;m.blocked=0;m.nested=0;m.aligned=[];m.silence_bypass=0
 # Keep real definition bank and original name/font data. Added action IDs get
 # a temporary copy of original76 with fixed MP/type for deterministic tests.
 native_actions=m.word(0x08026e18);actiontable=0x09300000
 m.put(actiontable,m.read(native_actions,347*28))
 needle=struct.pack('<I',native_actions)
 offset=image.find(needle)
 while offset>=0:
  if offset%4==0:m.put(0x08000000+offset,struct.pack('<I',actiontable))
  offset=image.find(needle,offset+4)
 donor=bytearray(m.read(actiontable+76*28,28));donor[4]=10;donor[0x19]=1
 for action in range(347,476):m.put(actiontable+action*28,donor)
 bank=m.word(m.word(0x080ccf40)+race*4)
 lessons=list(range(1,12))+list(range(172,178)) if job==2 else list(range(33,44))+list(range(105,111)) if job==16 else []
 original=lessons[:11];added=lessons[11:]
 for i in range(1,142):m.put(UNIT+0x40+i,[0])
 for i in (lessons if ap_mode=='all' else added if ap_mode=='added' else original):
  m.put(0x02001b40+i-144 if race==1 and i>=144 else UNIT+0x40+i,[0xe4])
 if job not in (2,16):m.put(UNIT+0x40,b'\xe4'*100)
 for n,i in enumerate(lessons):
  row=bytearray(m.read(bank+i*8,8))
  if i in added or synthetic17:
   struct.pack_into('<H',row,4,347+n);row[6]=1 if synthetic17 else row[6];m.put(bank+i*8,row)
 m.put(IDS-16,b'\xA5'*(16+85*4+16));m.put(FLAGS-16,b'\xA6'*(16+85+16));m.put(AI-16,b'\xA7'*(16+256+16))
 m.put(MENU+0x94,struct.pack('<II',IDS,FLAGS));m.put(FLAGS,b'\x01'*85)
 m.call(0x080cce60,UNIT,slot,DESC+4,DESC+5);m.put(DESC,struct.pack('<I',bank));m.put(DESC+6,[2,0,0,0]);m.bank=bank;m.lessons=lessons
 def hook(u,address,size,data):
  if address==0x08026ab8:m.nested+=1;return
  if address in (0x080c95a8,0x080cd95c,0x080c8280,0x080cdb9c,0x080cdbb4,0x080cd944,0x080cdb54):value=0
  elif address==0x080cdb3c:value=m.silence
  elif address==0x080c8298:value=m.blocked
  elif address==0x080258c4:value=u.reg_read(UC_ARM_REG_R1)
  elif address==0x0812f0d8:m.put(u.reg_read(UC_ARM_REG_R1),b'\0\0');value=0
  elif address==0x0812ed98:value=m.read(actiontable+28*(u.reg_read(UC_ARM_REG_R1)&65535)+4,1)[0]
  elif address==0x080ccd50:
   selector=u.reg_read(UC_ARM_REG_R1)&255
   value=m.special if selector==0x13 else m.restricted if selector==0x15 else m.silence_bypass if selector==0x14 else 0 if selector in (3,0x18) else 1
  else:raise AssertionError(hex(address))
  u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 for address in (0x08026ab8,0x080c95a8,0x080cd95c,0x080c8280,0x080cdb9c,0x080cdbb4,0x080cd944,0x080cdb54,0x080cdb3c,0x080c8298,0x080258c4,0x0812f0d8,0x0812ed98,0x080ccd50):m.u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
 for name,address in symbols.items():
  if name in ('ffta_command_successor','ffta_descriptor_successor','ffta_special_action'):
   m.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:m.aligned.append(u.reg_read(UC_ARM_REG_SP)),begin=address,end=address)
 return m

def run(m,address,stack=STACK,ai_filter=255):
 before=m.read(UNIT,264);sidecar=m.read(0x02001b40,816)
 if address==0x08133f70:
  count=m.call(address,AI,UNIT,ai_filter,stack=stack);values=list(struct.unpack('<'+'H'*count,m.read(AI,2*count)));flags=[]
  check('guards',m.read(AI-16,16)==b'\xA7'*16 and m.read(AI+count*2,256-count*2+16)==b'\xA7'*(256-count*2+16),'AI bounds')
 else:
  try:m.call(address,MENU,DESC,stack=stack)
  except Exception:
   print('DEBUG',hex(address),hex(m.u.reg_read(UC_ARM_REG_PC)),m.read(DESC,12).hex(),m.read(UNIT,64).hex());raise
  count=struct.unpack('<H',m.read(MENU+0x84,2))[0] if address==0x08027918 else m.read(DESC+9,1)[0]
  values=list(struct.unpack('<'+'I'*count,m.read(IDS,count*4)));flags=list(m.read(FLAGS,count))
  capacity=85 if address==0x08027918 else 22
  check('guards',count<=capacity and m.read(IDS-16,16)==b'\xA5'*16 and m.read(IDS+count*4,85*4-count*4+16)==b'\xA5'*(85*4-count*4+16),'lesson output bounds')
  check('guards',m.read(FLAGS-16,16)==b'\xA6'*16 and m.read(FLAGS+85,16)==b'\xA6'*16,'flag bounds')
 check('guards',m.read(UNIT,264)==before and m.read(0x02001b40,816)==sidecar,'read-only learning')
 check('abi',all(sp%8==0 for sp in m.aligned),'C helper alignment')
 return values,flags

entries=(0x08026d44,0x08026f9c,0x08027918,0x08133f70)
if '--skip-special' in sys.argv:entries=tuple(a for a in entries if a!=0x08027918)
for job in (2,16,3,17,80):
 for slot in (1,2):
  for mp,silence in ((20,0),(0,0),(20,1)):
   for address in entries:
    a=setup(base,job,slot,mp=mp,silence=silence);b=setup(rom,job,slot,mp=mp,silence=silence)
    av,bv=run(a,address),run(b,address)
    check('native',av==bv,str((job,slot,mp,silence,hex(address),av,bv)))
if not baseline_only:
 # Audit compiled native continuation literals against every overwritten span.
 ordered=sorted((address,name) for name,address in symbols.items())
 for index,(address,name) in enumerate(ordered):
  if name not in {row['name'] for row in meta['changes'] if 'savesR3' in row}:continue
  end=ordered[index+1][0] if index+1<len(ordered) else 0x09100000+len(engine)
  for offset in range((address+3)&~3,end-3,4):
   target=struct.unpack_from('<I',rom,offset-0x08000000)[0]
   if not target&1 or not 0x08000000<=target<0x08200000:continue
   check('continuations',not any(row['offset']<=((target&~1)-0x08000000)<row['offset']+row['size'] for row in meta['changes']),f'{name} continuation {target:08x} enters overwritten code')
 for job in (2,16):
  for slot in (1,2):
   for mode in ('added','all'):
    for mp,silence in ((20,0),(0,0),(20,1)):
     for address in entries:
      m=setup(rom,job,slot,mode,mp,silence)
      expected=[i for i in m.lessons if (mode=='all' or i in m.lessons[11:]) and m.read(m.bank+i*8+6,1)[0] in (1,4)]
      if address==0x08133f70:
       expected=[struct.unpack('<H',m.read(m.bank+i*8+4,2))[0] for i in expected]
       expected=[i for i in expected if m.call(0x08133e18,UNIT,i,255)]
      values,flags=run(m,address)
      check('extended',values==expected,str((job,slot,mode,mp,silence,hex(address),values,expected)))
      if flags and mode=='added':check('extended',flags==[int(mp>=10 and not silence)]*len(flags),'added usability flags')
 # All17 members as action fixtures fit real22-row single-command allocation.
 for job in (2,16):
  for address in entries:
   m=setup(rom,job,1,'all',synthetic17=True)
   expected=m.lessons if address!=0x08133f70 else list(range(347,364))
   check('capacity',run(m,address)[0]==expected,'17 synthetic actions')
 # Duplicate command slots deduplicate action IDs in AI, while preserving order.
 for job in (2,16):
  m=setup(rom,job,1,'all',duplicate=True)
  expected=[struct.unpack('<H',m.read(m.bank+i*8+4,2))[0] for i in m.lessons if m.read(m.bank+i*8+6,1)[0] in (1,4)]
  expected=[i for i in expected if m.call(0x08133e18,UNIT,i,255)]
  check('dedup',run(m,0x08133f70)[0]==list(dict.fromkeys(expected)),'AI duplicate secondary')
 # Real nested ordinary builder calls26AB8 for a synthetic action21 record.
 for present in (0,1):
  m=setup(rom,2,1,'added');first=m.lessons[11];m.put(m.bank+first*8+4,struct.pack('<H',0x21));m.special=present
  values,flags=run(m,0x08026d44)
  check('nested',m.nested>0 and first in values and flags[values.index(first)]==present,'actual26D44->26AB8')
 # Each appended lesson independently: types and learned-bit semantics are
 # applied by native bodies, not reproduced by a test-side list provider.
 for job in (2,16):
  for slot in (1,2):
   for lesson_index in range(11,17):
    for kind in range(5):
     for ap in (0,37,0x80,0xe4):
      for address in entries:
       m=setup(rom,job,slot,'none');lesson=m.lessons[lesson_index]
       # 'none' starts with original AP; clear every lesson for isolation.
       for i in m.lessons:m.put(0x02001b40+i-144 if job==2 and i>=144 else UNIT+0x40+i,[0])
       m.put(0x02001b40+lesson-144 if job==2 else UNIT+0x40+lesson,[ap]);m.put(m.bank+lesson*8+6,[kind])
       wanted=kind in (1,4) and bool(ap&0x80)
       expected=[347+lesson_index if address==0x08133f70 else lesson] if wanted else []
       check('isolated',run(m,address,stack=STACK-(4 if ap==37 or ap==0xe4 else 0))[0]==expected,str((job,slot,lesson,kind,ap,hex(address))))
 # Denied selectors, silence exception, AI signed filter and duplicate slots.
 for job in (2,16):
  for slot in (1,2):
   for address in entries:
    m=setup(rom,job,slot,'added');m.restricted=0;m.special=0;m.blocked=1
    values,_=run(m,address,stack=STACK-4)
    check('denied',bool(values)==(address==0x08026d44),'selector/status rejection')
    m=setup(rom,job,slot,'added',silence=1);m.silence_bypass=1
    values,flags=run(m,address,stack=STACK-4)
    check('denied',len(values)==4 and (not flags or all(flags)),'silence bypass selector')
   for filter_value in (0,1,2,255):
    m=setup(rom,job,slot,'added')
    check('filter',len(run(m,0x08133f70,ai_filter=filter_value)[0])==(4 if filter_value in (1,255) else 0),'native AI action category')
  m=setup(rom,job,1,'all',duplicate=True,synthetic17=True)
  check('capacity',run(m,0x08027918)[0]==m.lessons*2,'34 special-list rows fit native85')
 # A descriptor that only partly matches a custom slot must stay native.
 for job in (2,16):
  for slot in (1,2):
   for field in ('bank','first','last','command'):
    for address in (0x08026d44,0x08026f9c):
     a,b=setup(base,job,slot,'all'),setup(rom,job,slot,'all')
     for m in (a,b):
      if field=='bank':
       m.put(0x02024000,m.read(m.bank,2048));m.put(DESC,struct.pack('<I',0x02024000))
      else:
       p=DESC+{'first':4,'last':5,'command':6}[field];m.put(p,[m.read(p,1)[0]+1])
     check('descriptor',run(a,address)==run(b,address),'partial descriptor match remains native')
 # Item / empty slots retain their native namespace and skip behavior.
 for job in (2,16):
  for commands in ((0,0,0),(1,2,1),(2,1,1),(0,2,1),(2,0,1)):
   for slot in (1,2):
    for address in entries:
     a,b=setup(base,job,slot),setup(rom,job,slot)
     for m in (a,b):
      m.put(UNIT+0x35,commands)
      bank=m.call(0x080cce60,UNIT,slot,DESC+4,DESC+5)
      m.put(DESC,struct.pack('<I',bank));m.put(DESC+6,[commands[slot-1]])
      # The inventory policy provider selects the native no-quantity-check
      # branch. Item's original bank, action filters and AP path remain real.
      m.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:(u.reg_write(UC_ARM_REG_R0,0),u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))),begin=0x08133bc4,end=0x08133bc4)
     check('item',run(a,address)==run(b,address),str((job,commands,slot,hex(address))))
 # Both real AI callers reserve only40 halfwords. Even an artificial Soldier
 # with all17 lessons converted to actions, plus all20 Blue Magic actions and
 # all native AI-eligible Items, must fit those original allocations.
 for synthetic in (False,True):
  for builder in (0x08133f70,0x08134094):
   m=setup(rom,2,1,'all',mp=999,synthetic17=synthetic)
   m.put(UNIT+8,[10]);m.put(UNIT+0x35,[2,2,1]);m.put(UNIT+0x40,b'\xe4'*142)
   m.put(UNIT+0x18,struct.pack('<HH',20,100))
   m.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:(u.reg_write(UC_ARM_REG_R0,0),u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))),begin=0x08133bc4,end=0x08133bc4)
   count=m.call(builder,AI,UNIT,255,stack=STACK-4)
   expected=39 if synthetic else 33
   check('ai_capacity',count==expected and count<=40,str(('maximum custom plus Blue Magic plus Item',synthetic,hex(builder),count,expected)))
   check('ai_capacity',m.read(AI+80,16)==b'\xa7'*16,'native40-action guard')
report={'passed':True,'romSha1':meta['romSha1'],'baselineOnly':baseline_only,'checks':checks,'total':sum(checks.values()),'scope':'Native ordinary/restricted/special battle and AI builders with donor action fixtures and controlled external MP/status/selectors; actual AP and IDs, nested special predicate, buffers and ABI. No rendering or production action effects.'}
(out/'command-iteration-tests.json').write_text(json.dumps(report,indent=2)+'\n');(frozen/'tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
