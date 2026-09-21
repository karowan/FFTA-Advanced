"""Read-only native preview reproduction from frozen real battle snapshots."""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys,collections,argparse
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
from capstone import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
LAB=ROOT/'build/expansion/probes/chop-game-lab';OUT=ROOT/'build/expansion/probes/chop-preview-council';OUT.mkdir(exist_ok=True)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ui',action='store_true',help='Replay one real target-confirmation input and save separate evidence')
parser.add_argument('--rom',default=str(LAB/'frozen.gba'))
parser.add_argument('--state',default=str(LAB/'prepreview.state'))
parser.add_argument('--break-name',action='store_true',help='Test-only spin breakpoint at2C09A before font call')
parser.add_argument('--break-hit',action='store_true',help='Test-only spin breakpoint atA300A after native hit roll; supply confirmation state')
parser.add_argument('--break-result',action='store_true',help='Test-only spin breakpoint atA3762 before result executor returns')
parser.add_argument('--break-exec',action='store_true',help='Test-only spin breakpoint atA2E70 before ordinary A-action execution')
parser.add_argument('--seed',type=int,help='Set native RNG seed at commit, without modifying chance or hit flags')
args=parser.parse_args()
if args.ui:
    data=bytearray(pathlib.Path(args.rom).read_bytes());sha=hashlib.sha1(data).hexdigest()
    assert sum((args.break_name,args.break_hit,args.break_result,args.break_exec))<=1
    destination=OUT/(sha+('-break-name' if args.break_name else '-break-hit' if args.break_hit else '-break-result' if args.break_result else '-break-exec' if args.break_exec else '-ui')+(f'-seed{args.seed}' if args.seed is not None else ''));destination.mkdir(exist_ok=True)
    if args.break_name:struct.pack_into('<H',data,0x2c09a,0xe7fe)
    if args.break_hit:struct.pack_into('<H',data,0xa300a,0xe7fe)
    if args.break_result:struct.pack_into('<H',data,0xa3762,0xe7fe)
    if args.break_exec:struct.pack_into('<H',data,0xa2e70,0xe7fe)
    image=destination/'frozen.gba';image.write_bytes(data)
    spec=importlib.util.spec_from_file_location('preview_emulator',ROOT/'scripts/emulator-test.py')
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);e=h.Emulator(image)
    try:
        e.load(pathlib.Path(args.state));before=e.memory()
        if args.seed is not None:C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',args.seed),4)
        e.run(8,256);e.run(180)
        e.save(destination/'after.state');e.screenshot(destination/'after.png')
        (destination/'after.ram').write_bytes(e.memory());(destination/'after.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
        state=(destination/'after.state').read_bytes()
        report=dict(sourceRomSha1=sha,stateSha1=hashlib.sha1(pathlib.Path(args.state).read_bytes()).hexdigest(),
                    breakpoint='name' if args.break_name else 'hit' if args.break_hit else 'result' if args.break_result else 'executor' if args.break_exec else None,seed=args.seed,registers=[hex(v) for v in struct.unpack_from('<17I',state,0x20)],
                    sourceState=str(args.state),image=str(destination/'after.png'),context=e.memory()[0xf3f0:0xf424].hex(),
                    reservedGuardPreserved=e.memory()[0x3ff44:0x40000]==before[0x3ff44:0x40000])
        if args.break_exec:
            tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
            exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<harness>','exec'))
            m=ARM(pathlib.Path(args.rom).read_bytes(),(destination/'after.iwram').read_bytes())
            m.put(0x02000000,e.memory());rs=struct.unpack_from('<17I',state,0x20)
            regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR]
            m.u.reg_write(UC_ARM_REG_CPSR,rs[16])
            for reg,value in zip(regs,rs):m.u.reg_write(reg,value)
            events=[];hp_writes=[];trace=collections.deque(maxlen=20)
            def event(u,pc,size,_):
                trace.append(hex(pc))
                if pc in (0x0812fe38,0x080a3072,0x080a3162,0x0813388c,0x080a29e8):
                    events.append(dict(pc=hex(pc),args=[hex(u.reg_read(r)) for r in regs[:4]],stage=m.read(0x0200f418,1)[0],sp=hex(u.reg_read(UC_ARM_REG_SP))))
            def written(u,access,address,size,value,_):
                if u.reg_read(UC_ARM_REG_PC)==0x080a2298:hp_writes.append((hex(address),value))
            m.u.hook_add(UC_HOOK_CODE,event);m.u.hook_add(UC_HOOK_MEM_WRITE,written)
            try:m.u.emu_start(0x080a2e71,0x080a3762,count=2000000);error=None
            except Exception as ex:error=str(ex)
            report['nativeExecutor']=dict(error=error,endPC=hex(m.u.reg_read(UC_ARM_REG_PC)),events=events,hpWrites=hp_writes,trace=list(trace),object=m.read(rs[9],0x2c4).hex())
            if args.seed in (0,1):
                hit=args.seed==0;obj=m.read(rs[9],0x2c4)
                assert error is None and m.u.reg_read(UC_ARM_REG_PC)==0x080a3762
                assert obj[0x2c0]==1 and not(struct.unpack_from('<H',obj,0x2c)[0]&0x20)
                assert len([x for x in events if x['pc']=='0x812fe38'])==int(hit)
                assert len([x for x in events if x['pc']=='0x80a3162'])==int(hit)
                assert hp_writes==([('0x20033fc',9)] if hit else [])
                report['nativeExecutor']['fixtureAssertions']='PASS: one target, no critical flag, hit has one formula/HP application, miss has none, no other native HP writes'
        (destination/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
    finally:e.close()
    raise SystemExit(0)
rom=(LAB/'frozen.gba').read_bytes();ram=(LAB/'prepreview.ram').read_bytes();iwram=(LAB/'prepreview.iwram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name=='ARM'],type_ignores=[]),'<harness>','exec'))
results=[]
for action in (423,112):
 for address,args in [(0x080b4c90,(UNIT,0x020033e4,action,453)),(0x08130200,(UNIT,0x020033e4,action,453))]:
  m=ARM(rom,iwram);m.put(0x02000000,ram);m.put(STACK,struct.pack('<II',0,2))
  trace=collections.deque(maxlen=40);writes=[];calls=[]
  def code(u,pc,size,data):
   trace.append(pc)
   if pc in (0x08130fbc,0x08131378,0x08131b20,0x0812fe38,0x081300e2) or 0x09100000<=pc<0x09104000:
    calls.append((pc,[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR)]))
  def write(u,access,p,size,v,data):
   if 0x02000000<=p<0x02040000:writes.append((u.reg_read(UC_ARM_REG_PC),p,size,v))
  m.u.hook_add(UC_HOOK_CODE,code);m.u.hook_add(UC_HOOK_MEM_WRITE,write)
  try:value=m.call(address,*args);error=None
  except Exception as e:value=None;error=str(e)
  result=dict(action=action,address=hex(address),value=value,error=error,trace=[hex(x) for x in trace],writes=[(hex(pc),hex(p),s,hex(v)) for pc,p,s,v in writes],calls=[(hex(pc),[hex(x) for x in rs]) for pc,rs in calls],context=m.read(0x0200f3f0,52).hex())
  results.append(result)
  print(json.dumps({k:result[k] for k in ('action','address','value','error','context')},indent=2))
(OUT/'native-preview.json').write_text(json.dumps(dict(romSha1=hashlib.sha1(rom).hexdigest(),results=results),indent=2))
