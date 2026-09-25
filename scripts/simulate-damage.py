"""Deterministic native damage simulation for every playable job by game stage.

Runs the installed native action executor (0A433C) of the current release
candidate (build/expansion/help-pages) in the ARM harness used by the
integrated Bard/synergy tests: the executor-entry RAM of the integrated build's
fixed Giza battle (scripts/jobs/viking/prepare-executor.py), with the candidate
ROM mapped over it. BIOS ArcTan2 (SWI 0Ah, projectile direction) is supplied by
the harness. Nothing is played.

For each stage (level, original shop tier, expansion shipment) and each job of
every race (original and new):
- The attacker has that job's native base stats plus growth x (level - 1),
  i.e. it levelled only in that job, full HP. It holds the stage-available
  weapon its native permission mask allows with the highest Weapon Attack, and
  separately the one with the highest magic bonus; each action keeps the better
  of the two. No armor, accessory, support or reaction ability.
- Weapons: original items sold in ordinary shops at or below the stage's shop
  tier (build/reports/vanilla-teaching-sources.json from
  scripts/audit-vanilla-teaching-sources.mjs) and expansion items of released
  shipments.
- Actions: Fight and every Action-type ability of the job (native racial rows
  between the job's first/last ability index, plus expansion lessons the job
  owns, such as Soldier and Gladiator axe skills) that a stage-available weapon
  teaches. Abilities taught only by items outside ordinary shops count from the
  late stage; abilities no item teaches (e.g. Blue Magic) count at every stage.
  MP is raised to the action's cost when the stage's MP pool is smaller; the
  report records cost and pool.
- The target is a Human Soldier of the same level, no equipment, neutral
  affinity to all nine elements (unit +0C..+14), the fixture's enemy allegiance, adjacent and attacked from the side (native hit rates for this
  pairing: front 62%, side 90%, back 100% for Fight and Fire).
- Each action runs over fixed RNG states; the mean HP loss (misses count as 0)
  is the expected damage. When a hit reaches the target's HP the action is
  measured again against 999 HP: if every hit then removes exactly 999 HP it
  is an instant KO effect (reported separately), otherwise the uncapped
  damage is used (marked overkill).
Outliers compare each job's best expected damage per action with the stage
median of the jobs ranked at that stage: a job is ranked once its prerequisite
chain depth (native requirement records; e.g. Paladin 1, Dark Knight 2) is no
greater than the stage index (opening 0, Twisted Flow 1, Pale Company 2) and it
has a stage-available weapon. Other jobs are still simulated and listed. Not modelled: turn economy (charge time, Speed, setup
turns, MP regeneration), range and area size, statuses, reactions, supports,
and effects that need other units (e.g. Illusionist's all-enemy spells or
combos report no damage here).
"""
import argparse, datetime, hashlib, json, math, pathlib, random, statistics, struct, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_LR, UC_ARM_REG_PC
STAGES=[dict(id='early',level=5,shopTier=0,shipment=0,rare=False,label='Opening (L5, first shop, S0)'),
        dict(id='first',level=10,shopTier=1,shipment=1,rare=False,label='After Twisted Flow (L10, shop tier 1, S1)'),
        dict(id='second',level=16,shopTier=2,shipment=2,rare=False,label='After Pale Company (L16, shop tier 2, S2)'),
        dict(id='advanced',level=22,shopTier=2,shipment=3,rare=False,label='After Desert Patrol (L22, S3)'),
        dict(id='late',level=40,shopTier=2,shipment=3,rare=True,label='Late game (L40, rare-weapon abilities)')]
_rng=random.Random(20260924);SEEDS=[_rng.getrandbits(32) for _ in range(48)]   # fixed native RNG states
SIDE=0   # target facing: 1 faces the attacker (front), 0/2 side, 3 back
RACES={1:'Human',2:'Bangaa',3:'Nu Mou',4:'Viera',5:'Moogle'}
parser=argparse.ArgumentParser();parser.add_argument('--seeds',type=int,default=len(SEEDS))
parser.add_argument('--jobs',type=int,nargs='*');args=parser.parse_args()
SEEDS=SEEDS[:args.seeds]

# Native harness and its setup/execute wrappers.
source=ROOT/'scripts/test-integrated-bard.py';ns={'__file__':str(source),'__name__':'damage_simulation'}
exec(compile(source.read_text().split('# Native command flags')[0],str(source),'exec'),ns)
m,ACTOR,ENEMY,setup,execute,half=(ns[k] for k in ('m','ACTOR','ENEMY','setup','execute','half'))
integrated=ns['meta']
meta=json.loads(pathlib.Path(json.loads((ROOT/'build/expansion/help-pages/current.json').read_text())['manifest']).read_text())
rom=pathlib.Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
harness=ns['ns']['rom']
assert rom[0xa433c:0xa4400]==harness[0xa433c:0xa4400],'Executor entry differs from the integrated build'
m.put(0x08000000,rom)
ARCTAN2=0x08141860   # svc 0Ah; bx lr
assert rom[ARCTAN2-0x08000000:ARCTAN2-0x08000000+4]==bytes.fromhex('0adf7047')
def arctan2(u,address,size,data):
    signed=lambda v:v-0x10000 if v&0x8000 else v
    x,y=signed(u.reg_read(UC_ARM_REG_R0)&0xffff),signed(u.reg_read(UC_ARM_REG_R1)&0xffff)
    u.reg_write(UC_ARM_REG_R0,round(math.atan2(y,x)/(2*math.pi)*0x10000)&0xffff)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
m.u.hook_add(UC_HOOK_CODE,arctan2,begin=ARCTAN2,end=ARCTAN2)
u16=lambda p:struct.unpack_from('<H',rom,p)[0];u32=lambda p:struct.unpack_from('<I',rom,p)[0]
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
sources_path=ROOT/'build/reports/vanilla-teaching-sources.json';sources=json.loads(sources_path.read_text())
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert sources['cleanSha1']==hashlib.sha1(clean).hexdigest()
JOBS=u32(0xc8de4)-0x08000000;ITEMS=u32(0x2b2a0)-0x08000000;BANKS=u32(0x257e8)-0x08000000;ACTIONS=u32(0xccd84)-0x08000000
OTHERS=meta['equipmentRevision']['othersTable']-0x08000000
NAMES=u32(0x18da4)-0x08000000;PERMS=u32(0xcac40)-0x08000000   # item/job names; weapon permission masks
CHARS=json.loads((ROOT/'tools/ffta-randomizer-source/src/main/ffta/utils/charLookup.json').read_text())
def text(name_id,table=None):
    p=u32((OTHERS if table is None else table)+name_id*4)-0x08000000;out='';compact=rom[p]==1
    if compact:p+=1
    while rom[p]:
        if compact:out+=CHARS.get(f'{rom[p]:X}','?');p+=1;continue
        a,b=rom[p],rom[p+1];p+=2
        if a==0x80 and 0xb0<=b<=0xc9:out+=chr(65+b-0xb0)
        elif a==0x80 and 0xca<=b<=0xe3:out+=chr(97+b-0xca)
        elif a==0x80 and 0xa6<=b<=0xaf:out+=chr(48+b-0xa6)
        else:out+={(0x40,0x73):' ',(0x81,0x0b):'-',(0x80,0xf4):"'",(0x80,0xe4):'.'}.get((a,b),'?')
    return out
def job_record(j):return rom[JOBS+j*52:JOBS+j*52+52]
item=lambda i:rom[ITEMS+i*32:ITEMS+i*32+32]
def stats(j,level):
    r=job_record(j);grow=list(r[0x20:0x27]);n=level-1
    atk=int.from_bytes(r[0x1a:0x1d],'little');mag=int.from_bytes(r[0x1d:0x20],'little')
    base=dict(hp=r[0x17],mp=r[0x18],speed=r[0x19],watk=atk&0xfff,wdef=atk>>12,mpow=mag&0xfff,mres=mag>>12)
    for key,g in zip(('hp','mp','speed','watk','wdef','mpow','mres'),grow):base[key]+=g*n//10
    return base
def abilities(j):
    r=job_record(j);race=r[4];bank=u32(BANKS+race*4)-0x08000000;out=[]
    added=[o['abilityIndex'] for l in registry['lessons'] for o in l['owners'] if o['jobId']==j]   # e.g. Soldier/Gladiator axes
    for index in sorted(set(range(r[0x2e],r[0x2f]+1))|set(added)):
        name_id,_,action,kind=struct.unpack_from('<HHHB',rom,bank+index*8)
        if kind==1 and action:out.append((index,action,text(u16(ACTIONS+action*28))))
    return out

# Stage availability: weapons by shop tier/shipment; abilities by teaching item.
catalog={}   # item -> ('shop', tier) | ('shipment', stage) | ('rare', None)
teaches={}   # (job, racial ability index) -> set of item IDs
for row in sources['rows']:
    catalog[row['id']]=('shop',min(row['ordinaryTiers'])) if row['ordinaryTiers'] else ('rare',None)
    for lesson in row['lessons']:teaches.setdefault((lesson['job'],lesson['index']),set()).add(row['id'])
for entry in registry['items']:
    catalog[entry['romItemId']]=('shipment',int(entry['stageId'][1]))
    for owner in entry['teaching']:teaches.setdefault((owner['jobId'],owner['abilityIndex']),set()).add(entry['romItemId'])
def obtainable(i,stage):
    kind,tier=catalog.get(i,('rare',None))
    return tier<=stage['shopTier'] if kind=='shop' else tier<=stage['shipment'] if kind=='shipment' else stage['rare']
def learnable(j,index,stage):
    items=teaches.get((j,index))
    return 'untaught' if not items else 'yes' if any(obtainable(i,stage) for i in items) else None
REQUIREMENTS=u32(0xc8b18)-0x08000000   # job prerequisite records: (job, count) x2
def depth(j,seen=()):
    index=job_record(j)[0x30];pairs=rom[REQUIREMENTS+index*4:REQUIREMENTS+index*4+4] if index else b''
    needed=[pairs[k] for k in (0,2) if pairs and pairs[k] and pairs[k] not in seen]
    return 1+max(depth(p,seen+(j,)) for p in needed) if needed else 0
def legal(j,i):
    kind=item(i)[8];mask=u32(PERMS+job_record(j)[0x2d]*4)
    return (1<=kind<=19 or kind==31) and bool(mask>>(kind-1)&1)
def weapons(j,stage):
    ok=[i for i,(kind,_) in catalog.items() if kind!='rare' and obtainable(i,stage) and legal(j,i)]
    if not ok:return [0]
    best_wa=max(ok,key=lambda i:(item(i)[16],item(i)[18]));best_mp=max(ok,key=lambda i:(item(i)[18],item(i)[16]))
    return sorted({best_wa,best_mp})
def run(j,level,weapon,action,target,hp=None):
    r=job_record(j);s=stats(j,level);hp=hp or target['hp'];mp=max(s['mp'],rom[ACTIONS+action*28+4]);losses=[]
    for seed in SEEDS:
        setup(action,seed)
        m.put(ACTOR+5,bytes((j,r[4],j)));m.put(ACTOR+0x35,bytes((j,)));m.put(ACTOR+9,bytes((level,)))
        m.put(ACTOR+0x18,struct.pack('<4H',s['hp'],s['hp'],mp,mp))
        m.put(ACTOR+0x20,struct.pack('<4H',s['watk'],s['wdef'],s['mpow'],s['mres']))
        m.put(ACTOR+0x2a,struct.pack('<5H',weapon,0,0,0,0))
        m.put(ENEMY+9,bytes((level,)));m.put(ENEMY+0x2a,bytes(10))
        m.put(ENEMY+0x18,struct.pack('<4H',hp,hp,target['mp'],target['mp']))
        m.put(ENEMY+0x20,struct.pack('<4H',target['watk'],target['wdef'],target['mpow'],target['mres']))
        # Fixture allegiance (+28/+29; +29 bit 80 = enemy). The Bard setup
        # clears the target's enemy flag, which custom hostile actions check.
        m.put(ACTOR+0x28,ns['ram'][0x80+0x28:0x80+0x2a]);m.put(ENEMY+0x28,ns['ram'][0x33e4+0x28:0x33e4+0x2a])
        # Neutral affinity (1) for all nine elements, unit +0C..+14, like a
        # Human Soldier. The fixture monster absorbs Holy and is weak to Dark;
        # the Bard setup neutralizes only Holy (+13).
        m.put(ENEMY+0x0c,bytes([1]*9))
        m.put(ENEMY+0xf8,bytes((SIDE,)));m.put(ns['wrappers'][ENEMY]+0x1f,bytes((SIDE,)))   # unit and battle-wrapper facing
        before=half(ENEMY+0x18);execute(action);losses.append(before-half(ENEMY+0x18))
    return losses

jobs=[j for j in range(1,130) if job_record(j)[4] in RACES and job_record(j)[0x2f] and abilities(j)]
if args.jobs:jobs=[j for j in jobs if j in args.jobs]
new_jobs={j['id'] for j in registry['jobs'] if j['id']>=116}   # Soldier/Gladiator are listed for their added axe lessons
expanded={o['jobId'] for l in registry['lessons'] for o in l['owners']}-new_jobs   # original jobs with added lessons
started=time.time();results=[];errors=[]
for stage in STAGES:
    target=stats(2,stage['level'])
    for j in jobs:
        r=job_record(j);pool=stats(j,stage['level'])['mp']
        row=dict(stage=stage['id'],job=j,name=text(u16(JOBS+j*52),NAMES),race=RACES[r[4]],new=j in new_jobs,expanded=j in expanded,
                 prerequisiteDepth=depth(j),unlocked=depth(j)<=STAGES.index(stage),
                 level=stage['level'],mpPool=pool,weapons=[],actions=[])
        for weapon in weapons(j,stage):row['weapons'].append(dict(item=weapon,name=text(u16(ITEMS+weapon*32),NAMES) if weapon else 'none',
            wa=item(weapon)[16] if weapon else 0,mp=item(weapon)[18] if weapon else 0))
        for index,action,name in [(None,0,'Fight')]+abilities(j):
            source='yes' if index is None else learnable(j,index,stage)
            if not source:continue
            best=None
            for weapon in row['weapons']:
                try:losses=run(j,stage['level'],weapon['item'],action,target)
                except Exception as e:errors.append(dict(stage=stage['id'],job=j,action=action,error=repr(e)[:200]));continue
                capped=any(x>=target['hp'] for x in losses);ko=False
                if capped:   # overkill or KO: measure against 999 HP
                    losses=run(j,stage['level'],weapon['item'],action,target,999)
                    ko=all(x in (0,999) for x in losses)
                mean=sum(losses)/len(losses);hits=[x for x in losses if x>0]
                if best is None or mean>best['expected']:
                    best=dict(action=action,name=name,weapon=weapon['name'],expected=round(mean,1),
                              hitRate=round(len(hits)/len(losses),2),onHit=round(sum(hits)/len(hits),1) if hits else 0,
                              max=max(losses),mpCost=rom[ACTIONS+action*28+4],untaught=source=='untaught',
                              overkill=capped and not ko,instantKO=ko and bool(hits))
            if best:row['actions'].append(best)
        damaging=[a for a in row['actions'] if a['expected']>0 and not a['instantKO']]
        row['fight']=next((a['expected'] for a in row['actions'] if a['action']==0),0)
        row['best']=max(damaging,key=lambda a:a['expected']) if damaging else None
        row['instantKO']=[a['name'] for a in row['actions'] if a['instantKO']]
        row['stageWeapon']=any(w['item'] for w in row['weapons'])
        row['ranked']=row['stageWeapon'] and row['unlocked']
        results.append(row)
    print(json.dumps(dict(stage=stage['id'],jobs=len(jobs),seconds=round(time.time()-started))),flush=True)

# Outliers: each job's best expected damage per action against the stage median.
def brief(r,median):
    b=r['best'] or dict(expected=0,name=None,mpCost=0,hitRate=0,onHit=0)
    return dict(job=r['name'],race=r['race'],new=r['new'],expanded=r['expanded'],expected=b['expected'],action=b['name'],ratio=round(b['expected']/median,2),
                mpCost=b['mpCost'],mpPool=r['mpPool'],hitRate=b['hitRate'],onHit=b['onHit'],fight=r['fight'])
summary=[]
for stage in STAGES:
    rows=[r for r in results if r['stage']==stage['id']]
    median=statistics.median(r['best']['expected'] if r['best'] else 0 for r in rows if r['ranked'])
    fights=[r['fight'] for r in rows];fight_median=statistics.median(fights)
    ranked=sorted(rows,key=lambda r:-(r['best'] or {}).get('expected',0))
    summary.append(dict(stage=stage,median=median,fightMedian=fight_median,
        ranking=[brief(r,median) for r in ranked],
        high=[brief(r,median) for r in ranked if r['ranked'] and r['best'] and r['best']['expected']>=1.5*median],
        low=[brief(r,median) for r in ranked if r['ranked'] and (not r['best'] or r['best']['expected']<=0.6*median)],
        noStageWeapon=[r['name']+' ('+r['race']+')' for r in rows if not r['stageWeapon']],
        locked=[r['name']+' ('+r['race']+')' for r in rows if not r['unlocked']],
        instantKO=[dict(job=r['name'],race=r['race'],actions=r['instantKO']) for r in rows if r['instantKO']]))
out=ROOT/'build/reports/damage-simulation'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(romSha1=meta['romSha1'],harnessSha1=integrated['romSha1'],sourcesSha1=hashlib.sha1(sources_path.read_bytes()).hexdigest(),
    seeds=SEEDS,stages=STAGES,method=__doc__,summary=summary,results=results,errors=errors,seconds=round(time.time()-started))
(out/'report.json').write_text(json.dumps(report,indent=1)+'\n')
print(json.dumps(dict(status='complete',report=str(out/'report.json'),jobs=len(jobs),errors=len(errors),seconds=report['seconds'])))
