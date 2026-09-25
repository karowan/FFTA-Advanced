"""Real-core Spellblade with a greatbow: native menus, targeting and results.

Creates a disposable Giza battle fixture on the enchant-weapons candidate with
scripts/fixtures/enchant-sniper-profile.json (Viera Sniper, Windslash Bow,
secondary Spellblade, all fourteen actions learned). Fixed inputs: other units
Wait; the fixed Giza layout puts an enemy five tiles away. Cases: Fire Ench. on
the Sniper's own tile and on that enemy; the full list scrolled to its end
(BG2 menu map rows above the window stay unchanged); Spellbreak on that enemy
with Haste and Protect removes one at random on each hit (both occur across
fixed seeds replayed from the confirmed action). RNG, HP and MP are declared; menus,
targeting, hit, damage, enchantment and rendering are native.
"""
import ctypes as C, datetime, hashlib, json, runpy, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from native_battle_wrappers import fixed_giza_formation
meta=json.loads(Path(json.loads((ROOT/'build/expansion/enchant-weapons/current.json').read_text())['manifest']).read_text())
rom_path=Path(meta['path']);rom=rom_path.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
out=rom_path.parent/('ui-enchant-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
profile=ROOT/'scripts/fixtures/enchant-sniper-profile.json'
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom_path),'--out',str(out/'fixture'),
    '--party-profile',str(profile),'--confirm-pub-exit','--heap-end','0x0203c000'],check=True,capture_output=True)
FIX=out/'fixture';assert (FIX/'frozen.gba').read_bytes()==rom
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
ACTOR,TARGET,STATE,BOW,FIRE,SPELLBREAK=0x5a8,0x33e4,0x3f410+5*22,174,410,421
HASTE,PROTECT=21,25
SEEDS=(1,2,5,9,0x10,0x100,0x1234,0x7fff,0xffff,0x12345678,0x2468ace,0x7654321)
DOWN,RIGHT,A=32,128,256
word=lambda r,p:struct.unpack_from('<I',r,p)[0];half=lambda r,p:struct.unpack_from('<H',r,p)[0]
checks=[];inputs=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

def run_case(case):
    e=E(FIX/'frozen.gba')
    def active():
        r=e.memory();p=word(r,0xf438)-0x02000000
        return word(r,p+24) if 0<=p<len(r)-28 else 0
    def tap(key,wait=180,name=None):
        e.run(8,key);e.run(wait);inputs.append([case,key,wait,name])
        if name:e.screenshot(out/f'{case}-{name}.png')
    try:
        e.load(FIX/'battle-ready.state');e.run(1);observe['wait_for_menu'](e);fixed_giza_formation(rom,e)
        for _ in range(12):
            if active()==0x02000000+ACTOR:break
            previous=active()
            for key in (DOWN,DOWN,A,A):tap(key)
            for _ in range(0,6300,30):
                if active()!=previous and observe['menu_visible'](e):break
                e.run(30)
        check(active()==0x02000000+ACTOR,f'{case}: Sniper owns the native turn')
        fixed_giza_formation(rom,e)
        r=e.memory()
        check(r[ACTOR+7]==35 and r[ACTOR+0x36]==125 and half(r,ACTOR+0x2a)==BOW,f'{case}: Sniper, secondary Spellblade, greatbow')
        for u in (ACTOR,TARGET):e.set_memory(u+0x18,struct.pack('<4H',300,300,120,120));e.set_memory(u+0xe8,bytes(8))
        e.set_memory(STATE+20,bytes(2));inputs.append([case,'declared HP300 MP120, no ailments, no enchantment'])
        e.run(30);tap(0,30,'ready')
        if case=='spellbreak':
            for status in (HASTE,PROTECT):
                r=e.memory();e.set_memory(TARGET+0xe8+status//8,bytes((r[TARGET+0xe8+status//8]|(1<<(status%8)),)))
            inputs.append([case,'declared target Haste and Protect'])
        tap(DOWN,120);tap(A,180,'commands');tap(DOWN,90);tap(DOWN,90,'spellblade');tap(A,180,'abilities')
        if case=='list':
            menu_map=lambda:bytes(C.string_at(*e.maps[0x06000000])[0xe000:0xe140])
            above=menu_map()
            for i in range(13):tap(DOWN,90)
            e.screenshot(out/f'{case}-bottom.png')
            check(menu_map()==above,f'{case}: scrolling fourteen entries keeps the menu map above the window')
            return dict(case=case)
        if case=='spellbreak':
            for _ in range(11):tap(DOWN,60)
            e.screenshot(out/f'{case}-row.png')
        tap(A,240,'targeting')
        if case in ('strike','spellbreak'):
            for _ in range(5):tap(RIGHT,60)
            e.screenshot(out/f'{case}-cursor.png')
        r=e.memory();manager=word(r,0xf438)-0x02000000
        action=SPELLBREAK if case=='spellbreak' else FIRE
        check(r[manager+4]==7 and half(r,0xf3fc)==action,f'{case}: native targeting selects action {action}')
        tap(A,120,'forecast');tap(A,120,'confirm')
        if case=='spellbreak':
            # Replay the confirmed hit from one saved point with fixed seeds:
            # each hit removes exactly one buff, and both buffs occur.
            confirm=out/'spellbreak-confirm.state';e.save(confirm);removed=[]
            for seed in SEEDS:
                e.load(confirm);C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
                before=e.memory();tap(A,0);e.run(1200);after=e.memory()
                check(half(before,ACTOR+0x1c)==120 and half(after,ACTOR+0x1c)==110,f'{case} seed {seed:#x}: pays 10 MP')
                hit=half(after,TARGET+0x18)<300;kept=[bool(after[TARGET+0xe8+s//8]&(1<<(s%8))) for s in (HASTE,PROTECT)]
                check(sum(kept)==(1 if hit else 2),f'{case} seed {seed:#x}: one buff removed on a hit, none on a miss')
                inputs.append([case,'native RNG',seed,'hit',hit,'kept',kept])
                if hit:removed.append('Haste' if not kept[0] else 'Protect')
            check({'Haste','Protect'}<=set(removed),f'{case}: random removal picks both buffs across seeds')
            e.screenshot(out/f'{case}-after.png')
            return dict(case=case,removed=removed)
        C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',1),4);inputs.append([case,'native RNG',1])
        before=e.memory();tap(A,0)
        for i in range(0,150):
            e.run(4)
            if i%10==0:e.screenshot(out/f'{case}-frame{i:03d}.png')
        e.run(600);after=e.memory();e.screenshot(out/f'{case}-after.png')
        check(half(before,ACTOR+0x1c)==120 and half(after,ACTOR+0x1c)==114,f'{case}: pays 6 MP')
        check(half(after,STATE+20)==(BOW<<4|1),f'{case}: Fire enchantment on the greatbow')
        others=[p for p in range(0x80,0x80+6*264,264) if p!=ACTOR]+[0x32dc,0x33e4,0x2fc4,0x34ec,0x30cc,0x31d4]
        if case=='strike':
            check(half(after,TARGET+0x18)<300,f'{case}: enemy five tiles away takes damage')
            check(all(half(after,p+0x18)==half(before,p+0x18) for p in others if p!=TARGET),f'{case}: no other unit damaged')
        else:
            check(all(half(after,p+0x18)==half(before,p+0x18) for p in others),f'{case}: self preparation damages nobody')
        return dict(case=case,targetHp=half(after,TARGET+0x18),actorMp=half(after,ACTOR+0x1c),enchantment=half(after,STATE+20))
    finally:e.close()

results=[run_case(case) for case in ('self','strike','list','spellbreak')]
report=dict(status='passed',romSha1=meta['romSha1'],fixture=str(FIX),profile=str(profile),
    profileSha1=hashlib.sha1(profile.read_bytes()).hexdigest(),checks=checks,results=results,inputs=inputs)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),results=results,report=str(out/'report.json'))))
