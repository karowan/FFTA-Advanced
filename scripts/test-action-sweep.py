"""Every new job action executed through native battle menus, real core.

Two disposable Giza fixtures (scripts/fixtures/action-sweep-{a,b}-profile.json)
cover the ten new jobs: every lesson learned, HP/MP 400, the job's first
weapon. Party units Wait until each test unit's first turn, which is saved.
Each action then starts from that saved turn with a declared formation built
only from the original Giza layout's tiles and heights: the actor at (1,14),
enemies on the adjacent (2,14) and (1,15); every item owned x99, no active law,
the actor at 150/400 HP and MP, and a Mystic Knight's weapon Fire-enchanted. Inputs: Action, the job command, the action row, then the first valid
target among the adjacent enemy, the actor, the second enemy and an ally
(the cursor mode reads 4 at the forecast), then confirm. The run lasts
until the actor's menu returns. Recorded per action: the native action id at
targeting, the target used, MP/HP/status changes and the game_pass monitor
(resident IWRAM code, stack low-water mark, heap chain, rendering) and the
EXP each action earns; every expansion job must earn EXP. An action
that hangs, corrupts the monitor or cannot be selected is a problem.
"""
import datetime, hashlib, json, runpy, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from game_pass import Pass
from native_battle_wrappers import from_emulator
current=ROOT/'build/expansion/memory-fixes/current.json'
if '--current' in sys.argv:current=ROOT/sys.argv[sys.argv.index('--current')+1]
meta=json.loads(Path(json.loads(current.read_text())['manifest']).read_text())
rom_path=Path(meta['path']);rom=rom_path.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
out=rom_path.parent/('action-sweep-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
groups=[g for g in ('a','b') if g in sys.argv[1:]] or ['a','b']
word=lambda r,a:struct.unpack_from('<I',r,a)[0];half=lambda r,a:struct.unpack_from('<H',r,a)[0]
PARTY=[0x80+264*i for i in range(6)];ENEMIES=[0x2fc4+264*i for i in range(6)]
# Original Giza layout tiles (x, y, height, facing).
TARGETING=(5,6,7)
# Revivals need a KO ally; Field Remedy needs a curable ailment and Requiem an
# undead enemy, which this battle does not have (reported as expected).
KO_ALLY=('CHM-A3','CHM-A8')
EXPECTED_NO_TARGET=('CHM-A2','BRD-A4')
ACTOR,TARGET,SECOND=(1,14,16,3),(2,14,16,1),(1,15,16,0)
SPARE=[(2,13,32,3),(1,13,32,3),(0,14,16,3),(10,5,48,0),(5,14,32,1),(8,11,32,1),(8,2,80,0),(7,11,32,1),(5,8,48,0)]
actions={}
for l in registry['lessons']:
    if l['type']=='Action':
        for o in l['owners']:actions.setdefault(o['jobId'],[]).append(l)
report=dict(romSha1=meta['romSha1'],groups={});problems=[]

def fixture(group):
    if f'--fixture-{group}' in sys.argv:return Path(sys.argv[sys.argv.index(f'--fixture-{group}')+1])
    path=out/f'fixture-{group}'
    subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom_path),'--out',str(path),
        '--party-profile',str(ROOT/f'scripts/fixtures/action-sweep-{group}-profile.json'),'--confirm-pub-exit','--heap-end','0x0203f000'],
        check=True,capture_output=True)
    return path
def active(e):
    r=e.memory();m=word(r,0xf438)-0x02000000
    return word(r,m+24)-0x02000000 if 0<=m<len(r)-28 else 0
def state(e):
    r=e.memory();m=word(r,0xf438)-0x02000000
    return r[m+4] if 0<=m<len(r)-8 else None
def tap(e,key,wait=150):e.run(8,key);e.run(wait)
D,U,L,R,A,B=32,16,64,128,256,1
def place(e,actor):
    wrappers=from_emulator(rom,e);others=[u for u in PARTY+ENEMIES if u!=actor and u in wrappers]
    alive=[u for u in ENEMIES if u in wrappers and half(e.memory(),u+0x18)]
    first,second=alive[0],alive[1]
    layout={actor:ACTOR,first:TARGET,second:SECOND}
    spare=iter(SPARE)
    for u in others:
        if u not in layout:layout[u]=next(spare)
    for u,(x,y,h,f) in layout.items():
        w=wrappers[u];e.set_memory(u+0xf6,bytes((x,y)));e.set_memory(w+8,struct.pack('<3H',x*32+16,h,y*32+16));e.set_memory(w+0x1f,bytes((f,)))
    return first,second
def forecast(e):
    return e.memory()[0xf3b0]!=1   # cursor mode: 1 while targeting; a valid target leaves it
def cursor(e):
    r=e.memory();return (half(r,0xf3ac+12),half(r,0xf3ac+16))
def move(e,tile):
    for _ in range(12):
        x,y=cursor(e)
        if (x,y)==tuple(tile):return
        tap(e,R if x<tile[0] else L if x>tile[0] else D if y<tile[1] else U,60)
def list_position(e):
    """Absolute row of the open ability list: its heap object carries the
    native list callbacks 08017E81/08017F05; scroll at +2, visible row at +0x19."""
    r=e.memory()
    for a in range(0x02000,0x3f000-0x20,4):
        if word(r,a+8)==0x08017e81 and word(r,a+0x1c)==0x08017f05:return r[a+2]+r[a+0x19]
    return None
def list_window(e):
    raw,w,h,pitch,px=e.frame;bpp=4 if px==1 else 2
    return b''.join(bytes(raw[y*pitch+80*bpp:y*pitch+240*bpp]) for y in range(30,112))
def finish(e):
    """Run until the actor's menu returns; answer confirmation prompts with A."""
    for elapsed in range(0,6000,60):
        if observe['menu_visible'](e):return elapsed
        e.run(60)
        if elapsed%300==240:e.run(8,A)
    return None
def snapshot(e,units):
    r=e.memory();return {hex(u):dict(hp=half(r,u+0x18),mp=half(r,u+0x1c),status=r[u+0xe8:u+0xf0].hex()) for u in units}
def experience(e,unit):
    r=e.memory();return r[unit+9]*100+r[unit+10]   # level at +0x09, EXP 0..99 at +0x0A

for group in groups:
    fix=fixture(group);profile=json.loads((ROOT/f'scripts/fixtures/action-sweep-{group}-profile.json').read_text())
    slots={0x80+264*u['slot']:u for u in profile['units']};turns={}
    e=E(fix/'frozen.gba')
    try:
        e.load(fix/'battle-ready.state');e.run(1);observe['wait_for_menu'](e)
        for _ in range(60):
            a=active(e)
            if a in slots and a not in turns:turns[a]=out/f'{group}-turn-{a:x}.state';e.save(turns[a])
            if len(turns)==len(slots):break
            for key in (D,D,A,A):tap(e,key)
            observe['wait_for_menu'](e,limit=12000)
    finally:e.close()
    missing=[hex(u) for u in slots if u not in turns]
    if missing:problems.append((group,f'units never got a turn: {missing}'))
    results=[]
    for unit,turn in turns.items():
        job=slots[unit]['job'];expected={l['globalAbilityId']:l for l in actions[job]};seen=[];index=0
        while index<len(expected)+16:
            e=E(fix/'frozen.gba');label=f'{group}-{job}-row{index:02d}'
            try:
                e.load(turn);e.run(1);first,second=place(e,unit)
                e.set_memory(0x1941,bytes([99]*460))   # declared: every item owned x99
                e.set_memory(0x3c33,bytes(2))   # declared: no active law (no Judge prompt)
                # Declared: the actor at 150/400 HP and MP, so restoration is visible; a
                # Mystic Knight carries a Fire enchantment on its weapon (Arcane Release).
                e.set_memory(unit+0x18,struct.pack('<H',150));e.set_memory(unit+0x1c,struct.pack('<H',150))
                if job==125:
                    slot=(unit-0x80)//264;weapon=half(e.memory(),unit+0x2a)
                    e.set_memory(0x3f410+22*slot+20,struct.pack('<H',weapon<<4|1))
                e.run(2)
                ally=[u for u in PARTY if u!=unit and e.memory()[u+0xf6:u+0xf8]==bytes(SPARE[0][:2])]
                if ally and set(KO_ALLY)&{l['id'] for l in actions[job]}:
                    # Declared: the ally beside the actor is KO (HP 0, status 12) for revival rows.
                    e.set_memory(ally[0]+0x18,bytes(2));r=e.memory();e.set_memory(ally[0]+0xe9,bytes((r[ally[0]+0xe9]|0x10,)));e.run(2)
                p=Pass(e,out,label+'-');p.arm();before=snapshot(e,[unit,first,second]+ally);items=e.memory()[0x1940+362:0x1940+376]
                exp_before=experience(e,unit)
                tap(e,D);tap(e,A,200);tap(e,D);tap(e,A,250)
                for _ in range(index):tap(e,D,60)
                e.screenshot(out/(label+'-row.png'))
                if list_position(e)!=index:break   # the list has fewer rows
                tap(e,A,250);s=state(e);selected=half(e.memory(),0xf3fc)
                entry=dict(job=job,row=index,actionId=selected,targetingState=s)
                if s not in TARGETING:
                    entry['result']='not selectable'
                else:
                    seen.append(selected);lesson=expected.get(selected)
                    entry.update(lesson=lesson and lesson['id'],name=lesson and lesson['name'],cursorStart=cursor(e))
                    tiles={'enemy':TARGET[:2],'self':ACTOR[:2],'second enemy':SECOND[:2],'ally':SPARE[0][:2]}
                    design=(lesson or {}).get('effect','').lower()
                    if 'enemy' not in design and ('ally' in design or 'self' in design):
                        tiles={k:tiles[k] for k in ('self','ally','enemy','second enemy')}
                    if lesson and lesson['id'] in KO_ALLY:
                        tiles={k:tiles[k] for k in ('ally','self','enemy','second enemy')}
                    for target,tile in tiles.items():
                        move(e,tile);tap(e,A,200)
                        if forecast(e):break
                    else:target=None
                    if not target:
                        entry['result']='no valid target'
                        if not (lesson and lesson['id'] in EXPECTED_NO_TARGET):problems.append((label,f'action {selected}: no valid target'))
                    else:
                        entry['target']=target;e.screenshot(out/(label+'-forecast.png'));tap(e,A,0)
                        entry['frames']=finish(e)
                        if entry['frames'] is None:
                            entry['result']='no menu within 6000 frames';p.problems.append((label,f'action {selected}: actor menu did not return'))
                        else:
                            after=snapshot(e,[unit,first,second]+ally);entry['before']=before;entry['after']=after
                            entry['items']=[f'{i}:{items[i-362]}->{e.memory()[0x1940+i]}' for i in range(362,376) if e.memory()[0x1940+i]!=items[i-362]]
                            entry['result']='executed' if after!=before else 'executed, no visible change'
                            entry['exp']=experience(e,unit)-exp_before
                p.check('after',min_tiles=40);entry['monitor']=p.points[-1];entry['problems']=p.problems;problems.extend(p.problems)
                results.append(entry)
            finally:e.close()
            index+=1
        # Expansion jobs earn EXP like original jobs (native 12E5B4 job gate).
        if not any(x.get('exp',0)>0 for x in results if x['job']==job):problems.append((f'{group}-{job}','no action earned EXP'))
        untested=[l['id'] for a,l in expected.items() if a not in seen]
        if untested:problems.append((f'{group}-{job}',f'actions never selectable: {untested}'))
    report['groups'][group]=dict(fixture=str(fix),turns={hex(k):str(v) for k,v in turns.items()},results=results)
report['status']='passed' if not problems else 'failed';report['problems']=problems
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
summary={g:[(r['lesson'],r['result'],r.get('target')) for r in v['results']] for g,v in report['groups'].items()}
print(json.dumps(dict(status=report['status'],romSha1=meta['romSha1'],problems=problems[:60],report=str(out/'report.json'))))
sys.exit(0 if not problems else 1)
