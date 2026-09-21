"""Reviewed class enters intact native water and cancels back to land.

Uses the candidate's own pre-battle world checkpoint. A declared 88-byte map
record substitution selects complete original map92; no terrain flags, live
appearance, animation mode, or outcome are injected. Formation is the existing
deterministic natural-water fixture. Not campaign encounter acceptance.
"""
import ctypes as C
import argparse
import datetime
import hashlib
import json
import runpy
import struct
from pathlib import Path
from native_art import ROOT,sha
from natural_water_fixture import build,formation,MAP,LAND,WATER
from native_battle_wrappers import from_emulator
from actor_render_evidence import actors
from live_palette_evidence import observe
from native_body_display import retained,pending_from_anchor,completed_pending_facing
from native_oam_evidence import snapshot_ranges,hidden_at_composition
from mgba_instruction_trace import InstructionTrace


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job',type=int,choices=range(116,126),default=116)
    parser.add_argument('--native',action='store_true')
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--entry-index',type=Path)
    args=parser.parse_args()
    assert bool(args.manifest)==bool(args.entry_index), 'Isolated candidates need their own entry evidence'
    meta=json.loads((args.manifest or ROOT/'build/art/reviewed-integration'/('native-complete-candidate.json' if args.native else 'action-candidate.json')).read_text())
    index=json.loads((args.entry_index or ROOT/'build/art/reviewed-integration'/('native-entry-latest.json' if args.native else 'action-entry-latest.json')).read_text())
    entry_path=ROOT/index['report'];assert sha(entry_path.read_bytes())==index['sha256']
    entry=json.loads(entry_path.read_text());assert entry['status']=='passed' and entry['romSha1']==meta['romSha1']
    source=entry_path.parent/'cold-entry';seed=source/'accepted-world.state';seed_hash=sha(seed.read_bytes())
    rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
    assert (source/'frozen.gba').read_bytes()==rom
    route=json.loads((source/'route.json').read_text());assert route['romSha1']==meta['romSha1']
    out=ROOT/'build/art/reviewed-integration/water'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    path,fixture,native,map_proof=build(rom,out);live=meta['components']['livePalette']
    E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
    e=None;checks=[];inputs=[];samples=[];failure=None;clock=0;previous=None;anchor=None;wrappers={};visible_phases=set();composition=[]
    word=lambda r,p:struct.unpack_from('<I',r,p)[0]
    table=word(rom,0xc8598)-0x08000000
    race=rom[table+args.job*52+4]
    assert race in range(1,6)
    focus={1:0x290,2:0x398,3:0x4a0,4:0x5a8,5:0x5a8}[race]
    land=256+2*(args.job-116);water=land+1
    transitions={frozenset((land,water))}
    owner=args.job-116 if args.native else live['paletteGroups']['ownerMap'][args.job-116]
    def check(ok,label):
        assert ok,label
        checks.append(label)
    def run(n,key=0):
        nonlocal clock
        e.run(n,key);clock+=n
    def tap(key,wait=180):inputs.append([8,key,wait]);run(8,key);run(wait)
    def active():
        r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)
    def capture(label,expected):
        nonlocal previous,anchor
        trace=InstructionTrace(e,{0x080004dc:'native-composed'},{0x080004dc:snapshot_ranges(live)})
        for tick in range(64):
            with trace:run(1)
            r=e.memory();vram=C.string_at(*e.maps[0x06000000]);body=word(r,wrappers[focus]+0x44)-0x02000000
            rows=actors(fixture,r,vram,{body});check(len(rows)==1,label+' native body exists');a=rows[0]
            check(a['resource']==expected and a['declaredSequence'],label+' exact land/water resource')
            check(a['expectedTiles']==a['tileCount']<=a['allocation']==16,label+' bounded native tile allocation')
            start=0x10000+a['tile']*32;block=vram[start:start+a['allocation']*32];direct=bool(a['displayedFrames'])
            hold=None
            if not direct:
                if anchor:hold=pending_from_anchor(a,block,anchor,clock-anchor['frame'],transitions)
                if not hold:hold=retained(a,block,previous,transitions)
                if not hold and anchor:hold=completed_pending_facing(fixture,a,block,anchor,clock-anchor['frame'])
            check(direct or hold,label+' exact current or bounded pending native upload')
            row=dict(direct=direct,identity=(a['resource'],a['tile'],a['allocation']),block=block,first=a['first'],index=a['index'])
            if direct:anchor=dict(row,frame=clock,actor=a)
            previous=row
            if tick in (0,16,32,48):
                e.screenshot(out/f'{label}-{tick}.png')
                hardware=C.string_at(*e.maps[0x07000000])
                visible=any((attr&0x300)!=0x200 and tile&1023==a['tile'] and (attr,x,tile)!=(0xa8,0xf8,0)
                            for attr,x,tile in (struct.unpack_from('<3H',hardware,i*8) for i in range(128)))
                if args.native and visible:
                    from native_shared_palette_evidence import observe as native_observe
                    native_observe(fixture,r,C.string_at(*e.maps[0x05000000]),hardware,wrappers,check,set(range(10)))
                    visible_phases.add(label)
                elif word(r,live['ramReservation'][0]-0x02000000+2572)==0:
                    check(bool(trace.events),'Hidden body has an actual composition observation')
                    hidden_at_composition(live,fixture,trace.events[-1],hardware,a['tile'],a['allocation'],check,native=args.native)
                else:
                    observe(live,fixture,r,C.string_at(*e.maps[0x05000000]),hardware,check,{owner})
                    visible_phases.add(label)
            samples.append(dict(label=label,tick=tick,frame=clock,actor=a,proof='current' if direct else hold))
        composition.extend(trace.events)
        e.save(out/(label+'.state'));return e.memory()
    try:
        e=E(path);e.load(seed);e.set_memory(0x3ff44,bytes(8))
        check(e.memory()[focus+6]==(4 if race==5 else race),'Existing declared generic racial slot')
        e.set_memory(focus+4,bytes((1,args.job,race,args.job)));e.set_memory(focus+0x35,bytes((args.job,)));e.set_memory(focus+0x2a,bytes(10))
        inputs.append(['preallocation class, no equipment; clear transient action roots',args.job,race,focus])
        for x,y,key in route['path']:run(1,key)
        run(30);tap(256,1200)
        for _ in range(7):tap(256,600)
        for _ in range(3):tap(256)
        for _ in range(3):
            for key in (128,256,256,256):tap(key)
        tap(8,600);tap(256,600);tap(256,600);menus['wait_for_menu'](e)
        for turn in range(12):
            if active()==0x02000000+focus:break
            before=active()
            for key in (32,32,256,256):tap(key)
            for waited in range(0,6300,30):
                if active()!=before and menus['menu_visible'](e):break
                run(30)
            else:raise AssertionError('Native preceding turn did not return')
        check(active()==0x02000000+focus,'Actual declared class turn')
        positions=formation(fixture,e,native,focus);inputs.append(['existing original-water dry formation',positions]);run(30)
        wrappers=from_emulator(fixture,e);r=e.memory();grid=word(r,0x7f14)-0x02000000;heights=native.heights(MAP)
        check(r[grid:grid+512]==heights,'Complete native-loaded original water heights')
        check(r[0x91a0:0xd1a0]==native.planar(MAP),'Complete original map arrangement')
        check(r[0xd1a0:0xf1a0]==native.clipping(MAP),'Complete original map clipping')
        initial=capture('land',land);position=struct.unpack_from('<3H',initial,wrappers[focus]+8)
        tile=grid+2*(WATER[1]*16+WATER[0]);height,flags=initial[tile:tile+2]
        check(height>0 and flags&2 and not flags&9,'Unmodified legal natural water destination')
        for key in (256,128):tap(key)
        tap(256,600);wet=capture('water',water)
        check(struct.unpack_from('<3H',wet,wrappers[focus]+8)==(WATER[0]*32+16,(height-1)*16,WATER[1]*32+16),'Native submerged height and position')
        check(struct.unpack_from('<H',wet,wrappers[focus]+0x34)[0]==water,'Native wrapper selected new water body')
        tap(1,600);final=capture('land-return',land)
        check(struct.unpack_from('<3H',final,wrappers[focus]+8)==position,'Cancel returned to exact land position')
        check(final[grid:grid+512]==heights,'Terrain unchanged throughout Move/cancel')
        check(final[0x1940:0x1ebc]==initial[0x1940:0x1ebc],'Inventory/AP/preferences unchanged')
        check(final[0x3ff44:0x3ff4c]==bytes(8),'Transient action roots retired')
        check(sha(seed.read_bytes())==seed_hash,'Own-ROM source checkpoint unchanged')
        check('water' in visible_phases,'New water body actually reaches visible hardware with its declared palette')
    except BaseException as error:
        failure=repr(error)
        if e:e.save(out/'failed.state');e.screenshot(out/'failed.png')
    finally:
        if e:e.close()
        report=dict(status='failed' if failure else 'passed',romSha1=meta['romSha1'],job=args.job,race=race,focus=focus,fixture=map_proof,entrySha256=index['sha256'],
            sourceStateSha256=seed_hash,checks=checks,inputs=inputs,samples=samples,visiblePhases=sorted(visible_phases),failure=failure,scope=__doc__)
        (out/'composition.json').write_text(json.dumps(composition)+'\n')
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(status=report['status'],checks=len(checks),failure=failure,report=str(out/'report.json'))))
    assert failure is None,failure


if __name__=='__main__':main()
