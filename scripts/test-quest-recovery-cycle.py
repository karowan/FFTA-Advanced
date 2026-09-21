"""Two paid quest recoveries with full-bag rejection/replacement and cold save.

Initial inputs declare earned Elda's Cup entitlement, a full64-slot quest bag,
5000 gil and level50 Ford. After preparation, controller inputs alone advance
days, pay fees, return dispatches, reject/replace rewards and save/load.
"""
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
helper=ROOT/'scripts/test-paid-recovery-cycle.py'
helper_source=helper.read_text(encoding='utf-8')
# Import only the shared recorder/navigation definitions, before its scenario.
prefix=helper_source.split('def prepare():')[0].replace('paid-recovery-cycle','quest-recovery-cycle')
scope=__doc__
exec(compile(prefix,str(helper),'exec'))
__doc__=scope
values['helperSha1']=sha(helper.read_bytes())
rule=next(r for r in meta['missionRecovery']['rules'] if r['mission']==407)
assert rule['item']==4 and rule['sources']==[dict(mission=138,copies=1)]
stock=b''.join(bytes((item,0,0,0)) for item in range(1,66) if item!=4)
assert len(stock)==256


def item_count():return list(e.memory()[0x2b08:0x2c08:4]).count(4)

def record():
    ram=e.memory()
    return next((ram[p:p+16] for p in range(0x21c8,0x25c8,16)
                 if (ram[p]|((ram[p+1]&3)<<8))==407),None)


def capture(label):
    ram=e.memory();sram=e.memory(0)
    e.save(OUT/(label+'.state'));e.screenshot(OUT/(label+'.png'))
    (OUT/(label+'.ram')).write_bytes(ram);(OUT/(label+'.srm')).write_bytes(sram)
    row=dict(label=label,directory=str(OUT),gil=gil(),questCopies=item_count(),
             questItems=ram[0x2b08:0x2c08].hex(),assigned=half(ram,0x2a6),
             cached=record().hex() if record() else None,
             stateSha1=sha((OUT/(label+'.state')).read_bytes()),ramSha1=sha(ram),sramSha1=sha(sram))
    observations.append(row);return row


def prepare():
    e.set_memory(0,seed,0);e.run(3600)
    for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
    bit=138+0x2ff;at=0x1f70+(bit>>3);ram=e.memory()
    e.set_memory(at,bytes((ram[at]|(1<<(bit&7)),)))
    e.set_memory(0x1f64,struct.pack('<I',5000))
    e.set_memory(0x2b08,stock);e.set_memory(0x299,bytes((50,)))
    values['initialGil']=gil()
    check(native().call(meta['symbols']['ffta_recovery_needed'],407)==1,
          'Original earned entitlement qualifies despite full unrelated inventory')


# Same native pub selection/payment path, with the declared service and fee.
accept_node=next(n for n in ast.parse(helper_source).body if isinstance(n,ast.FunctionDef) and n.name=='accept')
accept_source=ast.get_source_segment(helper_source,accept_node).replace('471','407').replace('15000','300')
accept_source=accept_source.replace('displayed Cyril fee','displayed town-adjusted fee')
exec(compile(accept_source,'<quest recovery pub acceptance>','exec'))


def collect(number):
    prefix=f'return{number}';before=e.memory();initial=record()
    check(initial is not None and ((initial[1]>>2)|((initial[2]&3)<<6))==5,
          prefix+': native five-day accepted duration')
    elapsed=0
    for leg in range(1,7):
        travel(8 if leg%2 else 2,prefix+f'-travel-{leg}')
        rec=record();check(rec is not None,prefix+': dispatch survives travel')
        days=(rec[1]>>2)|((rec[2]&3)<<6)
        check(days<5-elapsed,prefix+': ordinary travel advances native days')
        elapsed=5-days
        if not days:break
        tap(1);tap(1)
    check(elapsed==5,prefix+': full native duration elapsed')
    # The existing native return fixture locates the reward boundary after two
    # result-page confirmations. The inventory is already full from setup.
    for page in range(2):tap(256,240);capture(prefix+f'-result-{page}')
    choices=(256,256,32,256,64,256) if number==1 else (256,256,256,256,32,256,64,256)
    for page,key in enumerate(choices):
        tap(key,240);capture(prefix+f'-choice-{page}')
        if half(e.memory(),0x2a6)==0:break
    after=e.memory();expected=stock if number==1 else bytes((4,0,0,0))+stock[4:]
    check(half(after,0x2a6)==0 and not half(after,0x2b8)&4,prefix+': Ford returns normally')
    check(after[0x2b08:0x2c08]==expected,prefix+': exact native full-bag reject/replacement')
    check(after[0x1940:0x1f40]==before[0x1940:0x1f40],prefix+': equipment and extra AP preserved')
    check(gil()==word(before,0x1f64),prefix+': return has no extra charge or refund')
    check(all(((after[0x1f70+((mid+0x2ff)>>3)]^before[0x1f70+((mid+0x2ff)>>3)])&
               (1<<((mid+0x2ff)&7)))==0 for mid in range(512)),prefix+': no source/use/service completion flags invented')
    check(native().call(meta['symbols']['ffta_recovery_needed'],407)==(1 if number==1 else 0),
          prefix+': rejection retains entitlement; held replacement suppresses it')
    world()


def cooldown():
    for leg in range(1,5):
        rec=record()
        if rec is None or rec[2]&0x1c in (4,8):break
        check(rec[2]&0x1c==12,'Rejected reward retains native cooldown')
        travel(8 if leg%2 else 2,f'cooldown-travel-{leg}');world()
    else:raise AssertionError('One-day recovery cooldown exceeded native travel bound')
    travel(2,'second-pub-area2');world()
    check(e.memory()[0x2b08:0x2c08]==stock,'Cooldown grants no free item and loses no held item')
    check(gil()==4700,'Only first fee has been paid before second acceptance')


cold_node=next(n for n in ast.parse(helper_source).body if isinstance(n,ast.FunctionDef) and n.name=='cold')
cold_source=ast.get_source_segment(helper_source,cold_node).replace('471','407').replace("50000-30000+values['saleGil']",'5000-600')
exec(compile(cold_source,'<quest recovery normal save/cold continue>','exec'))

stages=[('prepared',prepare),('paid1',lambda:accept(1)),('rejected1',lambda:collect(1)),
        ('cooled',cooldown),('paid2',lambda:accept(2)),('collected2',lambda:collect(2)),('cold',cold)]
try:
    e=Emulator(private)
    if '--resume' in sys.argv:
        prior_path=pathlib.Path(json.loads(latest.read_text())['report']);prior_bytes=prior_path.read_bytes();prior=json.loads(prior_bytes)
        assert prior['romSha1']==meta['romSha1'] and prior['seedSha1']==sha(seed)
        checks.extend(prior['checks']);completed.extend(prior['completed']);values.update(prior['values'])
        retained.update(report=str(prior_path),reportSha1=sha(prior_bytes),completed=list(completed))
        observations.extend(r for r in prior['observations'] if r['label'] in completed)
        anchor=next(r for r in reversed(observations) if r['label']==completed[-1]);folder=pathlib.Path(anchor['directory'])
        for ext,key in (('state','stateSha1'),('ram','ramSha1'),('srm','sramSha1')):
            assert sha((folder/(anchor['label']+'.'+ext)).read_bytes())==anchor[key]
        e.load(folder/(anchor['label']+'.state'));e.set_memory(0,(folder/(anchor['label']+'.srm')).read_bytes(),0);e.run(1)
    for label,fn in stages:
        if label in completed:continue
        fn();capture(label);completed.append(label);report(False,capture_failure=False)
finally:
    if e is not None:
        if len(completed)!=len(stages):report(False)
        e.close();e=None
report(True);atexit.unregister(report)
print(json.dumps(dict(passed=True,assertions=len(checks),completed=completed,values=values,report=str(OUT/'report.json'))))
