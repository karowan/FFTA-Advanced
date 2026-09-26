"""Whole-game pass on the release candidate: fixed inputs, real core.

Sections (all by default, or name them as arguments):
- world: Sprohm pub (missions, rumors), shop (every Buy/Sell tab scrolled),
  prison; world menu Party (every unit: Equip Items slots, Pick Abilities
  slots, Change Jobs wheel), Item List, Area List, System; map Law and Info.
- deploy: pre-battle unit Info on all six units with every submenu.
- battle: every unit's turn menu and Status in the Giza battle.
Menus are browsed and cancelled, never confirmed. Each checkpoint records the
game_pass monitor (resident IWRAM code, stack low-water mark, unused EWRAM
guard, heap chain, rendered tiles) and asserts that browsing changed no unit
record, clan inventory/AP/format data or job-state bank. Problems are
collected and reported together; any problem fails the run.
"""
import datetime, hashlib, json, runpy, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from game_pass import Pass
current=ROOT/'build/expansion/memory-fixes/current.json'
if '--current' in sys.argv:current=ROOT/sys.argv[sys.argv.index('--current')+1]
meta=json.loads(Path(json.loads(current.read_text())['manifest']).read_text())
rom_path=Path(meta['path']);rom=rom_path.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
sections=[a for a in sys.argv[1:] if a in ('world','deploy','battle','reactions','save')] or ['world','deploy','battle']
out=rom_path.parent/('game-pass-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
fixture=out/'fixture'
if '--fixture' in sys.argv:fixture=Path(sys.argv[sys.argv.index('--fixture')+1])
else:
    profile=['--party-profile',str(ROOT/sys.argv[sys.argv.index('--profile')+1])] if '--profile' in sys.argv else []
    subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom_path),'--out',str(fixture),
        '--confirm-pub-exit','--heap-end','0x0203f000',*profile],check=True,capture_output=True)
assert (fixture/'frozen.gba').read_bytes()==rom
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
# Data that browsing must never change: unit records, clan inventory/AP/format
# data (0x1940..0x1F1C) and the job-state bank.
# 0x1E7A..0x1E7B are the job-discovery bits, which viewing the wheel sets.
STABLE=((0x80,0x80+24*264,'unit records'),(0x1940,0x1e7a,'clan inventory/AP/format data'),(0x1e7c,0x1f1c,'clan preference/status data'),
        (0x3f400,0x3f728,'job-state bank'))
# The leader's +0xF6/+0xF9 record the town facility being visited; the clean
# game changes them identically (2 at the map, 5 in the shop, 4 in the prison).
NATIVE_TOWN=(0x80+0xf6,0x80+0xf9)
# Viewing a unit refreshes its derived Jump (+0xFE) and complement (+0xFF)
# through the native mobility recalculation; profiled fixtures change jobs
# without that refresh, so the first view updates it.
NATIVE_TOWN+=tuple(0x80+264*i+o for i in range(24) for o in (0xfe,0xff))
report=dict(romSha1=meta['romSha1'],fixture=str(fixture),sections={})

def run_section(name,state,route):
    e=E(fixture/'frozen.gba')
    try:
        e.load(fixture/(state+'.state'));e.run(30)
        p=Pass(e,out,name+'-');p.arm();base=e.memory();p.check('start')
        for step in route:
            p.run([step])
            if step[2]:
                now=e.memory()
                for i in NATIVE_TOWN:now=now[:i]+base[i:i+1]+now[i+1:]
                for a,b,label in STABLE:
                    if now[a:b]!=base[a:b]:
                        diff=[f'{0x02000000+i:#x}:{base[i]}->{now[i]}' for i in range(a,b) if now[i]!=base[i]]
                        p.problems.append((name+'-'+step[2],f'{label} changed at {diff[:12]}'));base=now
        report['sections'][name]=dict(points=p.points,problems=p.problems,inputs=p.inputs,
            minStackMargin=min(x['stackMargin'] for x in p.points))
        return p.problems
    finally:e.close()

def scroll(n,wait=24):return [('D',wait,None)]*n
def world_route():
    # Pub: no missions are posted in this seed (modal notice, dismissed with A).
    r=[('A',240,'town-menu'),('A',300,'pub'),('A',300,'pub-missions'),('A',300,'pub-menu'),('B',300,'pub-left')]
    # Shop: d-pad Right changes tab, R shows an item's teaching rows. Only B
    # leaves lists and the shop (A would buy or sell).
    r+=[('A',240,None),('D',120,None),('A',300,'shop'),('A',300,'shop-buy')]
    for t in range(8):r+=scroll(12)+[('N',30,f'shop-buy-tab{t}'),('RB',150,f'shop-buy-tab{t}-info'),('B',150,None),('R',150,None)]
    r+=[('B',240,None),('N',60,'shop-menu'),('D',120,None),('A',300,'shop-sell')]
    for t in range(8):r+=scroll(12)+[('N',30,f'shop-sell-tab{t}'),('RB',150,f'shop-sell-tab{t}-info'),('B',150,None),('R',150,None)]
    r+=[('B',240,None),('N',60,'shop-menu-again'),('B',300,'shop-left')]
    r+=[('A',240,None),('D',120,None),('D',120,None),('A',300,'prison'),('B',300,None),('B',300,'map-after-town')]
    r+=[('ST',150,'world-menu'),('A',300,'party')]
    for u in range(6):
        # The party cursor returns to No. 1 after each unit; four per row.
        r+=([('D',90,None)] if u>=4 else [])+[('R',90,None)]*(u%4)
        r+=[('A',300,f'unit{u}'),('A',250,f'unit{u}-equip')]
        for s in range(5):r+=[('A',200,None)]+scroll(24)+[('N',30,f'unit{u}-equip-slot{s}'),('B',120,None),('D',90,None)]
        r+=[('B',200,None),('D',90,None),('A',250,f'unit{u}-abilities')]
        for s in range(5):r+=[('A',200,None)]+scroll(12)+[('N',30,f'unit{u}-abilities-slot{s}'),('B',120,None),('D',90,None)]
        r+=[('B',200,None),('D',90,None),('A',300,f'unit{u}-jobs')]
        for j in range(12):r+=[('R',60,f'unit{u}-job{j}' if j%4==3 else None)]
        r+=[('D',60,None)]+[('R',60,None)]*6+[('N',30,f'unit{u}-jobs-row2'),('B',240,None),('U',90,None),('U',90,None),('B',300,f'unit{u}-closed')]
    r+=[('ST',300,'item-list')]+scroll(30)+[('N',30,'item-list-end'),('B',240,None),('B',300,'map-after-party')]
    # Area List moves the map cursor; leave it with B only (A would travel).
    r+=[('ST',150,None),('D',90,None),('A',300,'area-list')]+scroll(3,60)+[('N',30,'area-list-end'),('B',240,None),('B',240,'map-after-area'),
        ('ST',150,None),('D',90,None),('D',90,None),('A',300,'system'),('D',90,'system-2'),('B',240,None),('B',240,None),
        ('LB',300,'law'),('B',240,None),('RB',300,'map-info'),('B',240,'map-end')]
    return r
def deploy_route():
    r=[]
    for u in range(6):
        r+=[('R',120,None),('RB',300,f'unit{u}-info'),('A',250,None)]
        for s in range(5):r+=[('A',200,None)]+scroll(24)+[('N',30,f'unit{u}-equip-slot{s}'),('B',120,None),('D',90,None)]
        r+=[('B',200,None),('D',90,None),('A',250,None)]
        for s in range(5):r+=[('A',200,None)]+scroll(12)+[('N',30,f'unit{u}-abilities-slot{s}'),('B',120,None),('D',90,None)]
        r+=[('B',200,None),('D',90,None),('A',300,f'unit{u}-jobs')]+[('R',60,None)]*8+[('N',30,f'unit{u}-jobs-moved'),('B',240,None),('B',300,f'unit{u}-closed')]
    return r
def battle_section(name,state,turns=40):
    """Party units Wait; enemies act on native AI. Check at every turn menu."""
    import struct
    observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
    e=E(fixture/'frozen.gba');log=[]
    word=lambda r,a:struct.unpack_from('<I',r,a)[0];half=lambda r,a:struct.unpack_from('<H',r,a)[0]
    units=[0x80+264*i for i in range(6)]+[0x2fc4+264*i for i in range(6)]
    try:
        e.load(fixture/(state+'.state'));e.run(1);observe['wait_for_menu'](e)
        p=Pass(e,out,name+'-');p.arm();p.check('start')
        for t in range(turns):
            r=e.memory();m=word(r,0xf438)-0x02000000;actor=word(r,m+24) if 0<=m<len(r)-28 else 0
            log.append(dict(turn=t,actor=hex(actor),hp=[half(r,u+0x18) for u in units],status=[r[u+0xe8:u+0xf0].hex() for u in units]))
            if t%5==0 or t==turns-1:p.check(f'turn{t:02d}')
            for key in ('D','D','A','A'):p.run([(key,150,None)])
            try:observe['wait_for_menu'](e,limit=12000)
            except AssertionError:
                p.check(f'turn{t:02d}-no-menu',min_tiles=1);log.append(dict(turn=t,end='no turn menu within 12000 frames'));break
        report['sections'][name]=dict(points=p.points,problems=p.problems,inputs=p.inputs,turns=log,
            minStackMargin=min(x['stackMargin'] for x in p.points))
        return p.problems
    finally:e.close()
def reaction_section(name,state,profile,rounds_each=3):
    """Each round one reaction holder stands at (1,14) with three enemies on the
    adjacent declared Giza tiles and every other unit on far declared tiles;
    the party Waits and enemies act on native AI. Monitor at every round."""
    import struct
    from native_battle_wrappers import from_emulator
    observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
    NEAR=[(1,14,16,3),(2,14,16,1),(1,15,16,0),(1,13,32,3),(2,13,32,3),(0,14,16,3)]
    FAR=[(10,5,48,0),(8,2,80,0),(5,8,48,0),(8,11,32,1),(7,11,32,1),(5,14,32,1)]
    PARTY=[0x80+264*i for i in range(6)];ENEMIES=[0x2fc4+264*i for i in range(6)]
    half=lambda r,a:struct.unpack_from('<H',r,a)[0];log=[]
    holders=[(0x80+264*u['slot'],u.get('reaction')) for u in profile['units'] if u.get('reaction')]
    e=E(fixture/'frozen.gba')
    try:
        e.load(fixture/(state+'.state'));e.run(1);observe['wait_for_menu'](e)
        e.set_memory(0x3c33,bytes(2))   # declared: no active law
        p=Pass(e,out,name+'-');p.arm();p.check('start')
        for rnd in range(rounds_each*len(holders)):
            holder,reaction=holders[rnd%len(holders)];w=from_emulator(rom,e);r=e.memory()
            alive=[u for u in ENEMIES if u in w and half(r,u+0x18)][:3]
            if not alive:break
            layout={holder:NEAR[0],**dict(zip(alive,NEAR[1:4]))};far=iter(FAR+NEAR[4:])
            for u in PARTY+ENEMIES:
                if u in w and u not in layout:layout[u]=next(far)
            for u,(x,y,hh,f) in layout.items():
                e.set_memory(u+0xf6,bytes((x,y)));e.set_memory(w[u]+8,struct.pack('<3H',x*32+16,hh,y*32+16));e.set_memory(w[u]+0x1f,bytes((f,)))
            r=e.memory();before={u:(half(r,u+0x18),r[u+0xe8:u+0xf0].hex()) for u in [holder]+ENEMIES}
            for key in ('D','D','A','A'):p.run([(key,150,None)])
            try:observe['wait_for_menu'](e,limit=12000)
            except AssertionError:
                p.check(f'round{rnd:02d}-no-menu',min_tiles=1);log.append(dict(round=rnd,end='no turn menu'));break
            r=e.memory();after={u:(half(r,u+0x18),r[u+0xe8:u+0xf0].hex()) for u in [holder]+ENEMIES}
            log.append(dict(round=rnd,holder=hex(holder),reaction=reaction,changes={hex(u):(before[u],after[u]) for u in after if after[u]!=before[u]}))
            p.check(f'round{rnd:02d}')
        report['sections'][name]=dict(points=p.points,problems=p.problems,rounds=log,minStackMargin=min(x['stackMargin'] for x in p.points))
        return p.problems
    finally:e.close()
def save_section(name,state):
    """System > Save to the empty File 2, cold boot, Saved Game > Load > File 2.
    Unit records, clan inventory/AP/format data and the job-state bank must
    round-trip exactly (play time, cursor and clock bytes are native volatile)."""
    e=E(fixture/'frozen.gba');problems=[]
    try:
        e.load(fixture/(state+'.state'));e.run(30);p=Pass(e,out,name+'-');p.arm()
        before=e.memory()
        p.run([('ST',300,None),('D',300,None),('D',300,None),('A',300,'system'),('A',300,'save-slots'),('R',300,None),('A',300,'saved')]+
              [('A',300,None)]*6)   # extra A answers any overwrite prompt with its default No
        flash=e.memory(0);problems+=p.problems;points=p.points
    finally:e.close()
    e=E(fixture/'frozen.gba')
    try:
        e.set_memory(0,flash,0);e.run(3600)
        # The title swaps resident IWRAM code, so arm the monitor in the world.
        for key in (8,256,128,256,256,256,256):e.run(8,key);e.run(300)
        p=Pass(e,out,name+'-load-');p.arm();p.run([('N',120,'loaded')])
        loaded=e.memory();problems+=p.problems
        for a,b,label in ((0x80,0x80+24*264,'unit records'),(0x1940,0x1f1c,'clan inventory/AP/format data'),(0x3f400,0x3f728,'job-state bank')):
            if loaded[a:b]!=before[a:b]:problems.append((name,f'{label} differ after save/load'))
        report['sections'][name]=dict(points=points+p.points,problems=problems,minStackMargin=min(x['stackMargin'] for x in points+p.points))
        return problems
    finally:e.close()
world_state='party-profile' if '--profiled' in sys.argv else 'accepted-world'   # a fixture made with --party-profile
routes=dict(world=(world_state,world_route),deploy=('deployment-4-units',deploy_route))
problems=[]
for name in sections:
    if name=='battle':problems+=battle_section('battle','battle-ready');continue
    if name=='save':problems+=save_section('save',world_state);continue
    if name=='reactions':
        problems+=reaction_section('reactions','battle-ready',json.loads((ROOT/sys.argv[sys.argv.index('--profile')+1]).read_text()));continue
    state,route=routes[name];problems+=run_section(name,state,route())
report['status']='passed' if not problems else 'failed';report['problems']=problems
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],romSha1=meta['romSha1'],problems=problems[:40],
    minStackMargin={k:v['minStackMargin'] for k,v in report['sections'].items()},report=str(out/'report.json'))))
sys.exit(0 if not problems else 1)
