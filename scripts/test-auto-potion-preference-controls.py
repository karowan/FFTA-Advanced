"""Bounded native ABI/list controls and retained-capture character isolation."""
import pathlib,json,struct,collections,itertools,sys,runpy
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
source=ROOT/'scripts/test-battle-inventory.py'
ns={'__file__':str(source),'__name__':'potion_menu_native'}
exec(compile(source.read_text(encoding='utf-8').split('def fixture(')[0],str(source),'exec'),ns)
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
ROM=pathlib.Path(meta['path']);data=ROM.read_bytes();S=meta['symbols']
prior=max(p for p in ROM.parent.glob('potion-menu-*') if (p/'preference-report.json').exists())
OUT=prior/'controls';OUT.mkdir(exist_ok=True)
checks=collections.Counter();case=None
def check(k,v):checks[k]+=1;assert v,(k,case)
def word(b,p):return struct.unpack_from('<I',b,p)[0]
m=ns['ARM']((prior/'3-list.iwram').read_bytes());m.put(0x08000000,data)
def invoke(address,*args,residue=0):
 for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):m.u.reg_write(reg,val)
 saved=(UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)
 for i,reg in enumerate(saved):m.u.reg_write(reg,0x55000000+i)
 stack=0x03007700+residue
 m.u.reg_write(UC_ARM_REG_SP,stack);m.u.reg_write(UC_ARM_REG_LR,0x08000101)
 m.u.emu_start(address|1,0x08000100,count=3000000)
 check('native-return',m.u.reg_read(UC_ARM_REG_PC)==0x08000100)
 check('native-stack-and-callee-ABI',m.u.reg_read(UC_ARM_REG_SP)==stack and all(m.u.reg_read(reg)==0x55000000+i for i,reg in enumerate(saved)))
 return m.u.reg_read(UC_ARM_REG_R0)
for race,kind,preference,known,residue in itertools.product((3,5),(1,2,3,5),(0,1),(False,True),(0,4)):
 case=(race,kind,preference,known,residue)
 ram=bytearray((prior/f'{race}-list.ram').read_bytes());iw=(prior/f'{race}-list.iwram').read_bytes()
 ctx=word(iw,0x2818)-0x02000000;u=word(ram,ctx+0x1d0c)-0x02000000;slot=(u-0x80)//264;lesson=121 if race==3 else 100
 ram[0x1e80+slot]=preference;ram[u+0x40+lesson]=228 if known else 0
 outcomes=[]
 for address in (S['ffta_original_potion_roster'],0x0807d96c):
  m.put(0x02000000,ram);m.put(0x03000000,iw)
  n=invoke(address,kind,race,0x0203c000,residue=residue);after=m.get(0x02000000,0x40000)
  check('constructor-read-only-player-data',after[:0x1940]==ram[:0x1940] and after[0x1940:0x1e98]==ram[0x1940:0x1e98])
  outcomes.append((n,after))
 (n,old),(new,actual)=outcomes
 if kind!=2 or not known:
  check('unrelated-constructor-exact-native',new==n and actual==old)
  continue
 check('one-additional-choice',new==n+1)
 indexes=[i for i in range(new) if actual[0x3c23e+20*i]==lesson]
 check('exactly-two-adjacent-choices',len(indexes)==2 and indexes[1]==indexes[0]+1)
 start=indexes[0];allowed=set(range(0x3c000,0x3c004))|set(range(0x3c230+20*start,0x3c230+20*new))|set(range(ctx+0x1134,ctx+0x1134+new))|{ctx+0x1132}
 check('only-owned-list-fields-change',all(a==b or i in allowed for i,(a,b) in enumerate(zip(old,actual))))
 for j in range(new):
  original=j-(j>start);a=actual[0x3c230+20*j:0x3c230+20*(j+1)];b=old[0x3c230+20*original:0x3c230+20*(original+1)]
  check('row-help-lesson-flags-preserved',a[2:8]+a[12:]==b[2:8]+b[12:])
  check('row-native-index',int.from_bytes(a[:2],'little')==j)
  if j not in indexes:check('ordinary-row-name-preserved',a[8:12]==b[8:12])

E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
def tap(e,key):e.run(8,key);e.run(180)
for race in (3,5):
 case=(race,'ordinary-reaction');e=E(ROM)
 try:
  e.load(prior/f'{race}-hi-reopened.state');before=e.memory();ctx=word((prior/f'{race}-hi-reopened.iwram').read_bytes(),0x2818)-0x02000000
  u=word(before,ctx+0x1d0c)-0x02000000;ordinary=before[0x3c23e]
  tap(e,256)
  check('ordinary-reaction-confirms',e.memory()[u+0x3a]==ordinary)
  check('ordinary-choice-retains-medicine',e.memory()[0x1e80:0x1e98]==before[0x1e80:0x1e98])
  e.screenshot(OUT/f'{race}-ordinary.png')
  case=(race,'character-switch');tap(e,128)
  other=word(e.memory(),ctx+0x1d0c)-0x02000000
  check('actual-character-switch',other!=u and 0x80<=other<0x1940)
  tap(e,256);e.screenshot(OUT/f'{race}-other-character.png')
  check('character-switch-preserves-all-choices',e.memory()[0x1e80:0x1e98]==before[0x1e80:0x1e98])
  check('switch-does-not-edit-prior-reaction',e.memory()[u+0x3a]==ordinary)
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],source=str(prior),total=sum(checks.values()),checks=dict(checks))
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
