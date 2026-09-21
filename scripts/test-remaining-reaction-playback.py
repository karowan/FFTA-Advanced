"""Actual menus, queued results, playback and cold saves for remaining reactions.

One authenticated racial fixture; paired mastery controls and fixed executor
seeds. Gil uses the observed miss/critical seeds0/18. No hit,
reaction, result, inventory debit or serialized state is supplied by the test.
"""
import datetime, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
support=support.replace("FIX=LAB/'fixture'", "FIX=LAB/'fixture-two-geomancers'")
support=support.replace("OUT=LAB/'reaction-playback'", "OUT=LAB/"+repr('remaining-reactions-'+stamp))
exec(compile(support,'<remaining reaction recorder>','exec'))
proof=json.loads((FIX/'prepare-cache.json').read_text())
for name,value in proof['outputs'].items():
    assert hashlib.sha1((FIX/name).read_bytes()).hexdigest()==value,name
assert proof['inputs']['romSha1']==meta['romSha1']

# Accessors run on disposable read-only clones, never within the live game.
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
STACK,RETURN=0x03007000,0x08000100
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<read-only accessors>','exec'))

def owned(e,unit):
    m=ARM(image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
    result={}
    for name,size in [('ffta_job_state',22),('ffta_owned_wound',2),('ffta_job_potion',1)]:
        p=m.call(meta['symbols'][name],0x02000000+unit)
        result[name]=m.read(p,size).hex() if p else None
    return result

def checkpoint(e,label,folder):
    r=capture(e,label,folder)
    check('native-renderer-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
    return r

def mode(r):return r[word(r,0xf438)-0x02000000+4]

def report(passed=False):
    data=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
              fixture=proof,checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,cold=cold,
              limits=['Controlled mastery, stats, stock and allegiance before inputs.',
                      'Rendered frame changes and next-turn return do not certify every animation pixel or banner text.',
                      'Campaign acquisition and final assembled acceptance remain separate.'])
    (OUT/'report.json').write_text(json.dumps(data,indent=2))
    (LAB/'remaining-reactions-latest.json').write_text(json.dumps(dict(path=str(OUT/'report.json'),passed=passed)))
    return data

configs=[dict(name='gil',lesson='VIK-R2',target=0x398,race=2,job=118,weapon=399,action=0,hidden=437),
         dict(name='ward',lesson='DRK-R1',target=0x398,race=2,job=119,weapon=384,action=23,hidden=433),
         *[dict(name='potion-'+str(race),lesson='CHM-R1',target=target,race=race,job=job,weapon=0,action=0,hidden=251+pref,preference=pref)
           for race,target,job,pref in ((3,0x290,120,0),(5,0x188,122,1))],
         *[dict(name='cureall-'+str(race),lesson='CHM-R2',target=target,race=race,job=job,weapon=0,action=355,hidden=432)
           for race,target,job in ((3,0x290,120),(5,0x188,122))]]
if '--family' in sys.argv:
    family=sys.argv[sys.argv.index('--family')+1];configs=[c for c in configs if c['name'].startswith(family)]
assert configs

# Reuse all successful cases from a prior report for a cold-only continuation.
cold_only='--cold-from' in sys.argv
if cold_only:
    previous=json.loads(pathlib.Path(sys.argv[sys.argv.index('--cold-from')+1]).read_text())
    assert previous['romSha1']==meta['romSha1']
    outcomes=previous['outcomes']
else:
    e=E(TEST_ROM)
    try:
        e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
        for turn in range(16):
            if active(e)==0x02000000+ACTOR:break
            previous=active(e)
            for key in (32,32,256,256):tap(e,key)
            menu(e,previous)
        check('native-Human-turn',active(e)==0x02000000+ACTOR)
        e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
        checkpoint(e,'start',OUT)
    finally:e.close()

    for config in configs:
        target=config['target'];action=config['action'];name=config['name']
        folders={}
        for enabled in (False,True):
            case=(name,enabled,'setup');folder=OUT/(name+('-on' if enabled else '-off'));folder.mkdir();folders[enabled]=folder
            e=E(TEST_ROM)
            try:
                e.load(OUT/'start.state');e.run(1)
                wrappers=from_emulator(image,e)
                for unit in (ACTOR,target):
                    e.set_memory(unit+0x18,struct.pack('<4H',500,500,99,99))
                    e.set_memory(unit+0x20,struct.pack('<4H',70,40,70,40))
                    e.set_memory(unit+0xe8,bytes(8));e.set_memory(unit+0x3a,bytes(2))
                check('native-racial-sprite',e.memory()[target+6]==config['race'])
                e.set_memory(ACTOR+0x29,b'\x80');e.set_memory(target+0x29,b'\0')
                e.set_memory(target+0xf6,bytes((3,12)))
                e.set_memory(wrappers[target]+8,struct.pack('<3H',112,32,400))
                e.set_memory(target+5,bytes((config['job'],config['race'],config['job'])))
                e.set_memory(target+0x35,bytes((config['job'],)))
                e.set_memory(target+0x2a,struct.pack('<5H',config['weapon'],0,0,0,0))
                equip(e,target,config['lesson'],config['race'],enabled)
                e.set_memory(0x1f64,struct.pack('<I',1000))
                for item in (362,363,374):e.set_memory(0x1940+item,b'\x05')
                if name.startswith('potion'):
                    e.set_memory(target+0x18,struct.pack('<H',220))
                    e.set_memory(0x1e80+(target-0x80)//264,bytes((config['preference'],)))
                job=116 if action==355 else 8 if action==23 else 2
                e.set_memory(ACTOR+5,bytes((job,1,job)));e.set_memory(ACTOR+0x35,bytes((job,)))
                e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(144));e.set_memory(0x1b40,bytes(32))
                weapon=next(i['romItemId'] for i in registry['items'] if i['name']=='Red Spider Katana') if action==355 else 1
                e.set_memory(ACTOR+0x2a,struct.pack('<5H',weapon,0,0,0,0))
                if action:
                    base=word(image,word(image,0x257e8)-0x08000000+4)-0x08000000
                    indices=[i for i in range(176) if half(image,base+8*i+4)==action and image[base+8*i+6]==1]
                    check('unique-native-action-lesson',len(indices)==1)
                    index=indices[0];e.set_memory(ACTOR+0x40+index if index<144 else 0x1b40+index-144,b'\xff')
                for key in (256,16,256):tap(e,key)
                menu(e)
                for key in ((256,32,256,256) if action else (256,256)):tap(e,key)
                selected=checkpoint(e,'targeting',folder)
                check('selected-requested-action',word(selected,word(selected,0xf438)-0x02000000+20)==action)
                for key in (128,256,256):tap(e,key)
                before=checkpoint(e,'confirmation',folder)
                check('native-final-confirmation',mode(before)==11)
                check('no-premature-execution',word(before,LOG+4)==0)
            finally:e.close()

        positive=False
        for seed in ((0,18) if name=='gil' else (3,0,18)):
            paired={}
            for enabled in (False,True):
                case=(name,enabled,seed);folder=folders[enabled]/str(seed);folder.mkdir();e=E(TEST_ROM)
                try:
                    e.load(folders[enabled]/'confirmation.state');before=e.memory()
                    e.set_memory(LOG+148,struct.pack('<II',1,seed));tap(e,256,1)
                    rendered=set();executed=None;result=None
                    for frames in range(2401):
                        r=e.memory();rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
                        if word(r,LOG)==0x504c4159 and executed is None:
                            count=word(r,LOG+16);check('bounded-result-count',1<=count<=4)
                            result=[list(struct.unpack_from('<7I',r,LOG+20+28*i)) for i in range(count)]
                            executed=checkpoint(e,'native-result',folder);executed_owned=owned(e,target)
                        if frames%480==0:e.screenshot(folder/f'frame-{frames:04}.png')
                        if executed is not None and frames>300 and half(r,0xf4e8+0xdc)==47:break
                        if frames<2400:e.run(1)
                    check('native-execution-finished',executed is not None)
                    after=checkpoint(e,'after-playback',folder)
                    check('one-primary-executor',word(after,LOG+4)==1 and result[0][0]==action and result[0][1]==0x02000000+ACTOR)
                    check('intended-primary-recipient',result[0][2]==0x02000000+target)
                    reaction=[r for r in result if r[0]==config['hidden']]
                    check('disabled-control',enabled or not reaction)
                    if reaction:check('one-owned-self-reaction',len(reaction)==1 and reaction[0][1:3]==[0x02000000+target]*2)
                    check('rendering-changes',len(rendered)>3)
                    check('rendering-no-duplicate-HP-MP',all(after[u+0x18:u+0x20]==executed[u+0x18:u+0x20] for u in (ACTOR,target)))
                    check('rendering-no-duplicate-payment',after[0x1940:0x1e70]==executed[0x1940:0x1e70] and after[0x1f64:0x1f68]==executed[0x1f64:0x1f68])
                    loss=result[0][4];check('bounded-positive-or-missed-injury',loss<=500)
                    expected_inventory=bytearray(before[0x1940:0x1e70]);gain=0;heal=0
                    if name=='gil':
                        gain=min(50,loss//2) if enabled and result[0][3]&32 else 0
                        check('critical-only-gil',word(after,0x1f64)==1000+gain)
                        if gain:check('native-gil-presentation',reaction and reaction[0][3]&0x1000 and reaction[0][6]==gain+1)
                        check('owned-battle-gil-cap',bytes.fromhex(executed_owned['ffta_job_state'])[6:8]==bytes((gain,0)))
                    elif name=='ward':
                        check('Shell-after-positive-magic',bool(after[target+0xeb]&1)==bool(enabled and loss))
                    elif name.startswith('potion'):
                        heal=25*(1+config['preference']) if enabled and loss and 0<220-loss<=250 else 0
                        if heal:expected_inventory[362+config['preference']]-=1
                        check('selected-potion-correct-heal',half(after,target+0x18)==220-loss+heal)
                        check('consumption-only-turn-lock',bool(bytes.fromhex(executed_owned['ffta_job_state'])[8]&8)==bool(heal))
                    else:
                        if enabled and loss:expected_inventory[374]-=1
                        check('wound-prevented-only-by-enabled-reaction',bool(int(executed_owned['ffta_owned_wound'],16))==bool(loss and not enabled))
                    check('exact-one-item-payment-and-AP-preserved',after[0x1940:0x1e70]==expected_inventory)
                    check('reaction-present-exactly-when-triggered',bool(reaction)==bool(gain if name=='gil' else heal if name.startswith('potion') else enabled and loss))
                    previous=active(e);tap(e,256,900);menu(e,previous);checkpoint(e,'next-turn',folder)
                    row=dict(name=name,lesson=config['lesson'],target=target,enabled=enabled,seed=seed,results=result,frames=frames,uniqueFrames=len(rendered),sample=str(folder),loss=loss,executedOwned=executed_owned,gain=gain,heal=heal)
                    outcomes.append(row);paired[enabled]=row;report()
                finally:e.close()
            if name=='ward' and paired[False]['loss']:
                # Direct native magical damage is floored at its support stage;
                # assert exact result against the independently recorded control.
                check('Dark-Ward-three-quarter-incoming-damage',paired[True]['loss']==paired[False]['loss']*3//4)
            positive=any(r[0]==config['hidden'] for r in paired[True]['results'])
            if positive:break
        check('nonvacuous-'+name,positive)

for config in configs:
    name=config['name'];target=config['target'];case=('cold',name)
    selected=next((x for x in outcomes if x['name']==name and x['enabled'] and any(r[0]==config['hidden'] for r in x['results'])),None)
    check('positive-cold-input-'+name,selected is not None)
    source=pathlib.Path(selected['sample']);folder=OUT/(name+'-cold');folder.mkdir()
    e=E(TEST_ROM)
    try:
        e.load(source/'next-turn.state');expected=e.memory();expected_owned=owned(e,target)
        for key in (1,8,16,256,256):tap(e,key)
        old=e.memory(0);tap(e,256,300);saved=e.memory(0)
        check('native-suspend-wrote-save',saved!=old);(folder/'suspended.sav').write_bytes(saved)
    finally:e.close()
    e=E(ROM)
    try:
        e.set_memory(0,saved,0);e.run(3600)
        for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
        menu(e);actual=e.memory();actual_owned=owned(e,target)
        check('cold-HP-MP',all(actual[u+0x18:u+0x20]==expected[u+0x18:u+0x20] for u in (ACTOR,target)))
        check('cold-inventory-and-AP',actual[0x1940:0x1e70]==expected[0x1940:0x1e70])
        check('cold-gil',actual[0x1f64:0x1f68]==expected[0x1f64:0x1f68])
        check('cold-owned-record-wound-and-preference',actual_owned==expected_owned)
        check('cold-native-statuses',actual[target+0xe8:target+0xf0]==expected[target+0xe8:target+0xf0])
        check('cold-transient-roots-clear',actual[0x3ff44:0x3ff4c]==bytes(8))
        e.save(folder/'cold-resumed.state');e.screenshot(folder/'cold-resumed.png');(folder/'cold-resumed.ram').write_bytes(actual)
        cold.append(dict(name=name,source=str(source),saveSha1=hashlib.sha1(saved).hexdigest(),expectedOwned=expected_owned,actualOwned=actual_owned));report()
    finally:e.close()
print(json.dumps(report(True),indent=2))
