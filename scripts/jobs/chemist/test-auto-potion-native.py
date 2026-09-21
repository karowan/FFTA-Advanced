"""Complete native hostile Fight to explicit party Auto-Potion, no result stubs."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
exec(compile((ROOT/'scripts/jobs/chemist/test-reactions.py').read_text().split('for status,race,reaction,residue in')[0],'<reaction fixture helpers>','exec'))
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
n=ARM(rom,iw);events=[]
def trace(u,pc,size,data):
 root=m.word(0x0203ff48)
 events.append(dict(pc=hex(pc),args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],phase=m.word(root+800) if root else 0,permission=m.word(root+16) if root else 0,lr=hex(u.reg_read(UC_ARM_REG_LR))))
for name in ('ffta_chemist_reaction_queue','ffta_chemist_hp_loss','ffta_chemist_reaction_consumption','ffta_chemist_consumption','ffta_native_lose_item'):
 m.u.hook_add(UC_HOOK_CODE,trace,begin=S[name],end=S[name])
old_symbols={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
m.u.hook_add(UC_HOOK_CODE,trace,begin=old_symbols['ffta_native_lose_item'],end=old_symbols['ffta_native_lose_item'])

def stock_trace(u,access,address,size,value,data):
 events.append(dict(write=hex(address),value=value,pc=hex(u.reg_read(UC_ARM_REG_PC)),lr=hex(u.reg_read(UC_ARM_REG_LR)),sp=hex(u.reg_read(UC_ARM_REG_SP))))
m.u.hook_add(UC_HOOK_MEM_WRITE,stock_trace,begin=0x02001940+362,end=0x02001940+363)

def execute(machine,seed,preference=0,boost=False,reaction=True,quantity=5,hp=150,lock=0,race=3,residue=0,stock_pair=None):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.call(S['ffta_job_reset'])
 for unit,x,side in ((UNIT,4,128),(TARGET,5,0)):
  machine.put(unit+5,bytes([2,1,2]));machine.put(unit+0x35,b'\x02');machine.put(unit+0x3a,bytes(2));machine.put(unit+0xe8,bytes(8));machine.put(unit+0x28,bytes([0,side]));machine.put(unit+0x18,struct.pack('<4H',500,500,999,999));machine.put(unit+0x2a,struct.pack('<5H',1,0,0,0,0));machine.put(unit+0xf6,bytes([x,14]));machine.put(wrappers[unit]+8,struct.pack('<H',x*32));machine.put(wrappers[unit]+12,struct.pack('<H',14*32))
 machine.put(TARGET+5,bytes([120 if race==3 else 122,race,120 if race==3 else 122]));machine.put(TARGET+0x35,bytes([120 if race==3 else 122]));machine.put(TARGET+0x18,struct.pack('<4H',hp,300,50,50));machine.put(TARGET+0x2a,bytes(10))
 for name,field in [('CHM-R1',0x3a)] + ([('CHM-S1',0x3b)] if boost else []):
  l=next(l for l in registry['lessons'] if l['id']==name);index=next(o['abilityIndex'] for o in l['owners'] if o['race']==race)
  if field!=0x3a or reaction:machine.put(TARGET+field,bytes([index]));machine.put(TARGET+0x40+index,b'\xff')
 machine.put(machine.call(S['ffta_job_potion'],TARGET),bytes([preference]));machine.put(machine.call(S['ffta_job_state'],TARGET)+8,bytes([lock]))
 machine.put(0x02001940+362,bytes(stock_pair if stock_pair is not None else [quantity,quantity]));machine.put(0x030034b0,struct.pack('<I',seed));sp=regs[13]+((residue-regs[13])&7);machine.put(sp,struct.pack('<4I',0,0,0,255));machine.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=sp)
 return int.from_bytes(machine.read(TARGET+0x18,2),'little')
positive=0
for race,residue,preference,boost,qty,lock,hp,seed in itertools.product((3,5),(0,4),(0,1),(False,True),(0,5),(0,8),(1,150,300),range(8)):
 events=[];ordinary=execute(n,seed,preference,boost,False,qty,hp,lock,race,residue);actual=execute(m,seed,preference,boost,True,qty,hp,lock,race,residue)
 eligible=ordinary>0 and ordinary<hp and ordinary*2<=300 and qty>0 and not lock
 amount=(25 if preference==0 else 50)*(3 if boost else 2)//2
 expected=min(300,ordinary+amount) if eligible else ordinary
 if actual!=expected:
  (OUT/'auto-potion-failure.json').write_text(json.dumps(dict(case=[race,residue,preference,boost,qty,lock,hp,seed],ordinary=ordinary,actual=actual,expected=expected,events=events),indent=2))
 check('native-auto-potion-completed-recovery',actual,expected)
 check('native-auto-potion-exact-selected-stock',m.read(0x02001940+362,2),bytes([qty-int(eligible and preference==0),qty-int(eligible and preference==1)]))
 state=m.call(S['ffta_job_state'],TARGET)
 if m.read(state+8,1)[0]&8 != (8 if (eligible or (lock and ordinary>0)) else 0):
  (OUT/'auto-potion-failure.json').write_text(json.dumps(dict(case=[race,residue,preference,boost,qty,lock,hp,seed],ordinary=ordinary,actual=actual,expected=expected,events=events),indent=2))
 check('consumption-only-turn-lock',m.read(state+8,1)[0]&8,8 if (eligible or (lock and ordinary>0)) else 0)
 check('auto-potion-no-MP-change',m.read(TARGET+0x1c,4),n.read(TARGET+0x1c,4))
 if eligible:
  positive+=1;count=m.read(regs[0]+0x26bd,1)[0]
  objects=m.read(regs[0],count*0x2c4)
  check('native-item-result-object-present',any(struct.unpack_from('<H',objects,i*0x2c4+0x10)[0]==251+preference for i in range(count)),True)
check('positive-native-reaction-controls',positive>0,True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),positive=positive,scope='Native full executor and queued item results; visible animation/preference UI pending')
(OUT/'auto-potion-native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
