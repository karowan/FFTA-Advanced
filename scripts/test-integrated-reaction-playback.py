"""Fixed native menu -> queued results -> rendered frames -> next-turn playback.

Test-only entry instrumentation fixes the declared RNG input and copies result
summaries. It does not replace actions, damage, reactions, rendering or AI.
"""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess,collections,sys
from native_battle_wrappers import fixed_giza_formation,from_emulator
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);image=ROM.read_bytes();LAB=ROM.parent;FIX=LAB/'fixture'
assert hashlib.sha1(image).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==image
# Native sprite renderer plus its fixed lookup tables.6000..616F is mutable
# runtime data, not code. The ROM mapping verifies both exact guard boundaries.
CODE_FIRST,CODE_LAST=0x6170,0x6d68
NATIVE_CODE=image[0xa38d24:0xa3991c]
assert len(NATIVE_CODE)==CODE_LAST-CODE_FIRST
OUT=LAB/'reaction-playback';OUT.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
ACTOR,LOG=0x80,0x3ff50
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
checks=collections.Counter();outcomes=[];cold=[];case=None

def check(key,value):
    checks[key]+=1
    assert value,(key,case)

def active(e):
    r=e.memory();p=word(r,0xf438)-0x02000000
    return word(r,p+24) if 0<=p<len(r)-28 else 0

def tap(e,key,wait=180):e.run(8,key);e.run(wait)

def menu(e,previous=None):
    for elapsed in range(0,9001,10):
        if observe['menu_visible'](e) and (previous is None or active(e)!=previous):return
        if elapsed<9000:e.run(10)
    e.save(OUT/'menu-failure.state');(OUT/'menu-failure.ram').write_bytes(e.memory())
    (OUT/'menu-failure.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
    raise AssertionError(('menu timeout',case,hex(active(e))))

# Native A433C inline entry has already pushed r3. Undo that before entering
# ordinary C; an inner shim reproduces that push for the real shared entry.
original=word(image,0xa4344)
assert image[0xa433c:0xa4344]==bytes.fromhex('08b4c046004b1847')
assert original==meta['priorSymbols']['ffta_samurai_execute_entry']|1
source=r'''
#include <stdint.h>
typedef unsigned (*Executor)(uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned);
extern unsigned playback_original(uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned);
static unsigned h(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
unsigned playback_call(uint8_t *out,unsigned actor,unsigned x,unsigned y,unsigned action,unsigned mode,unsigned a,unsigned b){
 volatile uint32_t *log=(volatile uint32_t *)0x0203ff50u;
 log[0]=0;
 if(log[37])*(volatile uint32_t *)0x030034b0u=log[38];
 unsigned result=playback_original(out,actor,x,y,action,mode,a,b);
 log[2]=action;log[3]=actor;log[4]=out[0x26bd];
 for(unsigned i=0;i<4;i++){
  for(unsigned j=0;j<7;j++)log[5+i*7+j]=0;
  if(i>=out[0x26bd])continue;
  const uint8_t *o=out+i*0x2c4,*row=o+0x20;
  log[5+i*7]=h(o+0x10);log[6+i*7]=**(const uint32_t *const *)o;
  if(!o[0x2c0])continue;
  log[7+i*7]=**(const uint32_t *const *)row;log[8+i*7]=h(row+12);
  log[9+i*7]=(int16_t)h(row+0x1e);log[10+i*7]=(int16_t)h(row+0x20);log[11+i*7]=h(row+0x28);
 }
 /* A video frame can end inside this recorder. Publish only after all rows
  * are complete; neither an early count nor partially copied rows are ready. */
 log[1]++;log[0]=0x504c4159;
 return result;
}
'''
(OUT/'logger.c').write_text(source)
(OUT/'logger.s').write_text(f'''.syntax unified
.cpu arm7tdmi
.thumb
.section .text.entry,"ax"
.global playback_entry
.thumb_func
playback_entry:
 pop {{r3}}
 b playback_call
.section .text
.global playback_original
.thumb_func
playback_original:
 push {{r3}}
 ldr r3,={original}
 bx r3
.ltorg
''')
(OUT/'logger.ld').write_text('SECTIONS { . = 0x093f0000; .text : { *(.text.entry) *(.text*) *(.rodata*) } /DISCARD/ : { *(.comment) *(.ARM.attributes) } }')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror',
    '-Wl,-T,'+str(OUT/'logger.ld'),str(OUT/'logger.s'),str(OUT/'logger.c'),'-o',str(OUT/'logger.elf')],check=True,capture_output=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'logger.elf'),str(OUT/'logger.bin')],check=True)
code=(OUT/'logger.bin').read_bytes();assert len(code)<4096 and image[0x13f0000:0x13f0000+len(code)]==b'\xff'*len(code)
instrumented=bytearray(image);instrumented[0x13f0000:0x13f0000+len(code)]=code
struct.pack_into('<I',instrumented,0xa4344,0x093f0001)
TEST_ROM=OUT/'playback.gba';TEST_ROM.write_bytes(instrumented)

def equip(e,unit,lesson_id,race,enabled):
    lesson=next(l for l in registry['lessons'] if l['id']==lesson_id)
    index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==race)
    e.set_memory(unit+0x3a,bytes((index if enabled else 0,)))
    e.set_memory(0x1b40+index-144 if race==1 and index>=144 else unit+0x40+index,b'\xff')

def capture(e,label,folder):
    e.save(folder/(label+'.state'));e.screenshot(folder/(label+'.png'))
    r=e.memory();(folder/(label+'.ram')).write_bytes(r)
    check('root-and-log-guards',r[0x3ff44:0x3ff50]==bytes(8)+b'\xd7'*4 and r[0x3fff0:]==b'\xd7'*16)
    return r

cases=[('SAM-R2',116,1,377,435),('VIK-R1',118,2,399,436),('DRK-R2',117,1,384,434),
       ('BRD-R1',42,5,0,439),('BRD-R2',42,5,0,440),('DNC-R1',124,4,416,441),('DNC-R2',124,4,416,442),
       ('GEO-R1',121,3,0,443),('GEO-R2',121,3,0,444)]
if '--dancer-only' in sys.argv:cases=[c for c in cases if c[0].startswith('DNC-')]
for lesson,job,race,weapon,hidden in cases:
    TARGET=0x188 if race==5 else 0x5a8 if race==4 else 0x4a0 if race==3 else 0x398 if race==2 else 0x290
    for enabled in (False,True):
        folder=OUT/(lesson+('-on' if enabled else '-off'));folder.mkdir(exist_ok=True)
        e=E(TEST_ROM)
        try:
            e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
            wait_code=C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]
            check('native-code-matches-ROM',wait_code==NATIVE_CODE)
            for turn in range(4):
                previous=active(e)
                for key in (32,32,256,256):tap(e,key)
                menu(e,previous)
                check('Wait-preserves-native-IWRAM-code',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==wait_code)
            check('native-Marche-turn',active(e)==0x02000000+ACTOR)
            e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
            for unit in (ACTOR,TARGET):
                e.set_memory(unit+0x18,struct.pack('<4H',500,500,99,99));e.set_memory(unit+0x20,struct.pack('<4H',70,40,40,40))
                e.set_memory(unit+0xe8,bytes(8));e.set_memory(unit+0x3a,bytes(2))
            e.set_memory(ACTOR+0x2a,struct.pack('<5H',1,0,0,0,0))
            # Preserve an actual racial sprite. Reclassifying Giza's Panther
            # unit after its monster sprite loads cannot test katana playback.
            check('fixture-native-race',e.memory()[TARGET+6]==race)
            wrappers=from_emulator(image,e)
            # Bard's charge lasts until the reactor finishes its next turn.
            # Keep that reactor player-controlled so its next-turn menu can
            # suspend before expiry. Allegiance is an explicit fixture input,
            # set before all attack inputs; neither result nor save is altered.
            if lesson.startswith(('BRD-','DNC-','GEO-')):
                e.set_memory(ACTOR+0x29,b'\x80');e.set_memory(TARGET+0x29,b'\x00')
            else:e.set_memory(TARGET+0x29,b'\x80')
            e.set_memory(TARGET+0xf6,bytes((3,12)))
            e.set_memory(wrappers[TARGET]+8,struct.pack('<3H',3*32+16,32,12*32+16))
            for offset in (5,7,0x35):e.set_memory(TARGET+offset,bytes((job,)))
            e.set_memory(TARGET+6,bytes((race,)));e.set_memory(TARGET+0x2a,struct.pack('<5H',weapon,0,0,0,0))
            equip(e,TARGET,lesson,race,enabled)
            # Actual Move to (2,12), Act -> Fight -> adjacent opponent.
            for key in (256,16,256,256,256,128,256,256):tap(e,key)
            before=capture(e,'confirmation',folder)
            check('native-final-confirmation-mode',before[word(before,0xf438)-0x02000000+4]==11)
            check('no-execution-before-confirmation',word(before,LOG+4)==0)
        finally:e.close()
        for seed in ((0,1,3,7,15,18) if lesson=='SAM-R2' else (0,3,18)):
            case=(lesson,enabled,seed);sample=folder/str(seed);sample.mkdir(exist_ok=True);e=E(TEST_ROM)
            try:
                e.load(folder/'confirmation.state');e.set_memory(LOG+148,struct.pack('<II',1,seed))
                native_iwram_code=C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]
                e.run(8,256);render_hashes=[];result=None
                for frames in range(0,1801,12):
                    r=e.memory()
                    if word(r,LOG)==0x504c4159 and result is None:
                        count=word(r,LOG+16);check('bounded-result-count',0<count<=4)
                        result=[list(struct.unpack_from('<7I',r,LOG+20+28*i)) for i in range(count)]
                        executed=capture(e,'native-result',sample)
                    raw=e.frame[0];render_hashes.append(hashlib.sha1(raw).hexdigest())
                    if frames%48==0:e.screenshot(sample/f'frame-{frames:04}.png')
                    if frames<1800:e.run(12)
                check('native-transaction-completed',result is not None)
                check('real-native-Fight',result[0][0]==0 and result[0][1]==0x02000000+ACTOR)
                reaction=[row for row in result if row[0]==hidden]
                check('disabled-reaction-control',enabled or not reaction)
                if reaction:check('correct-reactor-and-single-result',len(reaction)==1 and reaction[0][1]==0x02000000+TARGET)
                check('rendered-frame-changes',len(set(render_hashes))>=3)
                r=capture(e,'after-playback',sample)
                check('native-IWRAM-code-preserved',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==native_iwram_code)
                check('rendering-does-not-reapply-HP',r[ACTOR+0x18:ACTOR+0x20]==executed[ACTOR+0x18:ACTOR+0x20] and r[TARGET+0x18:TARGET+0x20]==executed[TARGET+0x18:TARGET+0x20])
                check('AP-inventory-unchanged',r[0x1940:0x1e70]==before[0x1940:0x1e70])
                # Move+Fight spends both commands. Native FFTA then asks for
                # facing; it does not reopen the Wait/Status command menu.
                previous=active(e);tap(e,256,900);menu(e,previous);capture(e,'next-turn',sample)
                outcomes.append(dict(lesson=lesson,enabled=enabled,seed=seed,frames=frames,results=result,uniqueFrames=len(set(render_hashes)),target=TARGET,sample=str(sample)))
                (OUT/'partial.json').write_text(json.dumps(outcomes,indent=2))
            finally:e.close()
    check('nonvacuous-playback-'+lesson,any(x['lesson']==lesson and x['enabled'] and any(row[0]==hidden for row in x['results']) for x in outcomes))
# Read owned state on a clone only. The emulator itself performs all native
# saving, booting and resuming; no serialized output/state is repaired.
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
STACK,RETURN=0x03007000,0x08000100
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<readonly native accessors>','exec'))
def owned(e,unit):
    m=ARM(image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
    state=m.call(meta['symbols']['ffta_job_state'],0x02000000+unit)
    exposed=m.call(meta['symbols']['ffta_owned_exposed'],0x02000000+unit)
    return dict(state=m.read(state,22).hex() if state else None,exposed=m.read(exposed,1).hex() if exposed else None,
        centered=m.call(meta['symbols']['ffta_centered_active'],0x02000000+unit))
for lesson,_,_,_,hidden in cases:
    positives=[x for x in outcomes if x['lesson']==lesson and x['enabled'] and any(r[0]==hidden and (r[4] or lesson.startswith(('BRD-','DNC-')) or lesson=='GEO-R1') for r in x['results'])]
    if lesson=='DNC-R2':
        positives=[x for x in positives if (pathlib.Path(x['sample'])/'next-turn.ram').read_bytes()[ACTOR+0xea]&0x40]
    check('nonvacuous-actual-reaction-effect-'+lesson,bool(positives));selected=positives[0]
    case=('cold',lesson);target=selected['target'];folder=OUT/(lesson+'-cold');folder.mkdir(exist_ok=True)
    e=E(TEST_ROM)
    try:
        e.load(pathlib.Path(selected['sample'])/'next-turn.state');expected=e.memory();expected_owned=owned(e,target)
        if lesson=='SAM-R2':check('positive-counter-established-Centered',expected_owned['centered']==1)
        if lesson=='BRD-R1':check('positive-reaction-established-charge',bool(bytes.fromhex(expected_owned['state'])[11]&1))
        if lesson=='BRD-R2':check('positive-reaction-established-Haste',bool(expected[target+0xea]&0x20) and bool(bytes.fromhex(expected_owned['state'])[11]&28))
        if lesson=='DNC-R1':check('positive-reaction-established-Fury',bool(bytes.fromhex(expected_owned['state'])[3]&64))
        if lesson=='DNC-R2':check('positive-reaction-established-Slow',bool(expected[ACTOR+0xea]&0x40))
        if lesson=='GEO-R1':check('positive-reaction-established-Protect',bool(expected[target+0xeb]&2))
        for key in (1,8,16,256,256):tap(e,key)
        old=e.memory(0);tap(e,256,300);saved=e.memory(0)
        check('native-suspend-save-changed',saved!=old);(folder/'suspended.sav').write_bytes(saved)
    finally:e.close()
    e=E(ROM)
    try:
        e.set_memory(0,saved,0);e.run(3600)
        for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
        menu(e);actual=e.memory();actual_owned=owned(e,target)
        check('cold-party-and-recipient-HP-MP',all(actual[u+0x18:u+0x20]==expected[u+0x18:u+0x20] for u in (ACTOR,target)))
        check('cold-AP-and-inventory',actual[0x1940:0x1e70]==expected[0x1940:0x1e70])
        check('cold-owned-record-and-Centered',actual_owned==expected_owned)
        if lesson=='BRD-R2':check('cold-native-Haste-preserved',bool(actual[target+0xea]&0x20))
        if lesson=='DNC-R2':check('cold-attacker-Slow-preserved',actual[ACTOR+0xea]&0x40==expected[ACTOR+0xea]&0x40)
        if lesson=='GEO-R1':check('cold-native-Protect-preserved',bool(actual[target+0xeb]&2))
        check('cold-transient-roots-clear',actual[0x3ff44:0x3ff4c]==bytes(8))
        e.save(folder/'cold-resumed.state');e.screenshot(folder/'cold-resumed.png');(folder/'cold-resumed.ram').write_bytes(actual)
        cold.append(dict(lesson=lesson,seed=selected['seed'],saveSha1=hashlib.sha1(saved).hexdigest(),expectedOwned=expected_owned,actualOwned=actual_owned))
    finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),checks=dict(checks),outcomes=outcomes,cold=cold,
    limits=['Frame changes and menu return do not recognize banner text or certify every animation frame.','Gil Snapper, Dark Ward and Chemist reactions remain separate playback scenarios.','Allegiance is a controlled fixture input; full job changes, legal AI builds and campaign acceptance remain separate.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
