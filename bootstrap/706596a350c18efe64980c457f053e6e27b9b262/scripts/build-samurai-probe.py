"""Private Iaido integration over the verified assembled build."""
import hashlib,json,pathlib,struct,subprocess,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes';sha=lambda b:hashlib.sha1(b).hexdigest()
base=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text());engine=(ROOT/'build/expansion/engine.bin').read_bytes()
assert sha(base)==meta['romSha1'] and sha(engine)==meta['engineSha1'];assert base[0x1100000:0x1100000+len(engine)]==engine
old={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
OUT=P/'samurai'/sha(base);OUT.mkdir(parents=True,exist_ok=True);(OUT/'input.gba').write_bytes(base);(OUT/'engine.symbols').write_bytes((ROOT/'build/expansion/engine.symbols').read_bytes())
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
c=(ROOT/'src/engine/combat.c').read_text().replace('ffta_dark_weapon_valid','ffta_samurai_weapon_valid')
c=once(c,'static const PhysicalDefinition physical_definitions[]={','extern unsigned ffta_samurai_restoration_action(unsigned);\nextern unsigned ffta_samurai_restoration_eligibility(const uint8_t *);\nstatic const PhysicalDefinition physical_definitions[]={')
c=once(c,'if (!physical_definition(action))\n        return ((unsigned (*)(const uint8_t *))0x08130a95u)(context);','if(ffta_samurai_restoration_action(action))return ffta_samurai_restoration_eligibility(context);\n    if (!physical_definition(action))\n        return ((unsigned (*)(const uint8_t *))0x08130a95u)(context);')
c=once(c,'static const PhysicalDefinition physical_definitions[]={','extern unsigned ffta_centered_factor(const uint8_t *,unsigned);\nstatic const PhysicalDefinition physical_definitions[]={\n    {FFTA_SAM_A1,110,100},{FFTA_SAM_A2,1,1},{FFTA_SAM_A3,85,100},{FFTA_SAM_A6,100,100},{FFTA_SAM_A7,145,100},{FFTA_SAM_A8,135,100},{FFTA_SAM_A9,80,100},')
c=once(c,'magnitude=magnitude*numerator*incoming/(definition->denominator*5u);','magnitude=magnitude*numerator*incoming*ffta_centered_factor(actor,action)*((reference>0 && !restorative)?ffta_poise_hp_factor(actor,target,action):4)*((reference>0 && !restorative)?ffta_blade_ward_factor(actor,target):20)/(definition->denominator*1600u);');c='#include "action-snapshot.h"\n'+c;(OUT/'combat.c').write_text(c)
asm=(ROOT/'src/engine/combat-hooks.s').read_text()
for reg,value,label in [('r0','r1','8f'),('r2','r0','9f')]:
 oldline=f'    ldr {reg},=FFTA_DRK_A2';new=''.join(f'    ldr {reg},=FFTA_SAM_A{a}\n    cmp {value},{reg}\n    beq {label}\n' for a in (1,2,3,6,7,8,9))+oldline;asm=once(asm,oldline,new)
(OUT/'combat-hooks.s').write_text(asm)
geometry=(ROOT/'src/engine/combat-geometry.c').read_text()
geometry=once(geometry,'unsigned ffta_combat_geometry(', 'extern unsigned ffta_samurai_line_geometry(unsigned,unsigned,unsigned,unsigned);\nunsigned ffta_combat_geometry(')
geometry=once(geometry,'    unsigned result=ffta_original_combat_geometry', '    if((uint16_t)action==FFTA_SAM_A2)return ffta_samurai_line_geometry((uint8_t)actor_x,(uint8_t)actor_y,(uint8_t)target_x,(uint8_t)target_y);\n    unsigned result=ffta_original_combat_geometry')
geometry=once(geometry,'(uint16_t)action!=FFTA_DRK_A2 && (uint16_t)action!=FFTA_DRK_A3) return result;','(uint16_t)action!=FFTA_DRK_A2 && (uint16_t)action!=FFTA_DRK_A3 &&\n        (uint16_t)action!=FFTA_SAM_A1 && (uint16_t)action!=FFTA_SAM_A3 &&\n        (uint16_t)action!=FFTA_SAM_A6 && (uint16_t)action!=FFTA_SAM_A7 && (uint16_t)action!=FFTA_SAM_A9) return result;')
geometry=once(geometry,'(uint16_t)action==FFTA_DRK_A3)?3:2);','(uint16_t)action==FFTA_DRK_A3 ||\n        (uint16_t)action==FFTA_SAM_A3 || (uint16_t)action==FFTA_SAM_A7)?3:2);');(OUT/'combat-geometry.c').write_text(geometry)
asm=(ROOT/'src/engine/dark-sword-hooks.s').read_text().replace('bl ffta_dark_sword_apply','bl ffta_samurai_apply').replace('bl ffta_dark_law_weapons','bl ffta_samurai_law_weapons')
asm=once(asm,'    ldr r3,=FFTA_DRK_A2',''.join(f'    ldr r3,=FFTA_SAM_A{a}\n    cmp r0,r3\n    beq 1f\n' for a in (1,3,6,7,8,9))+'    ldr r3,=FFTA_DRK_A2');asm=once(asm,'    ldr r3,=FFTA_DRK_A2','    ldr r3,=FFTA_SAM_A2\n    cmp r0,r3\n    bne 2f\n    pop {r0,r3}\n    movs r0,#2\n    bx lr\n2:\n    ldr r3,=FFTA_DRK_A2');(OUT/'dark-hooks.s').write_text(asm)
names=['ffta_on_unit_copy','ffta_evaluated_init','ffta_physical_rider_reference','ffta_physical_law_hit','ffta_finisher_numerator','ffta_projectile_los','ffta_arc_geometry','ffta_dark_weapon_valid','ffta_dark_sword_apply','ffta_dark_law_weapons','ffta_owned_exposed','ffta_area_list_dispatch','ffta_owned_wound','ffta_wound_record_replace','ffta_wound_record_clear','ffta_physical_before_hit','ffta_wound_record_tick','ffta_wound_record_remaining','ffta_status_icon','ffta_status_next_key','ffta_status_visual']
names+=['ffta_evaluated_close','ffta_copy_owner_free']
bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n'
for n in names:bindings+=f'.align 2\n.global {n}\n.thumb_func\n{n}:\n push {{r3}}\n ldr r3,={old[n]|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(OUT/'bindings.s').write_text(bindings)
exposed=(ROOT/'src/engine/exposed-effects.c').read_text()
exposed=once(exposed,'static unsigned custom_physical(unsigned action) {','extern unsigned ffta_samurai_direct_action(unsigned);\nstatic unsigned custom_physical(unsigned action) {')
exposed=once(exposed,'return action==357 || action==358 || (action>=424 && action<=431);','return ffta_samurai_direct_action(action) || action==357 || action==358 || (action>=424 && action<=431);')
exposed=once(exposed,'void ffta_exposed_expire(uint8_t *unit,unsigned event) {','extern void ffta_wound_event(uint8_t *,unsigned);\nvoid ffta_exposed_expire(uint8_t *unit,unsigned event) {\n    ffta_wound_event(unit,event);')
(OUT/'exposed-effects.c').write_text(exposed)
exposed='#include "action-snapshot.h"\n'+exposed
exposed=once(exposed,'static int incoming(int damage,const uint8_t *recipient) {','static int incoming(int damage,const uint8_t *recipient,unsigned poise,unsigned ward) {')
exposed=once(exposed,'if(ffta_exposed_incoming_numerator(damage,recipient)==5)return damage;\n    uint64_t product=(uint64_t)(unsigned)damage*6u/5u;','if(damage<=0)return damage;\n    unsigned factor=ffta_exposed_incoming_numerator(damage,recipient);\n    uint64_t product=(uint64_t)(unsigned)damage*factor*poise*ward/400u;')
exposed=once(exposed,'    if(damage<=0 || !ffta_exposed_native_physical(context))return damage;\n    return incoming(damage,*(const uint8_t *const *)(context+8));','''    if(damage<=0 || !context)return damage;
    const uint8_t *target=*(const uint8_t *const *)(context+8);
    const uint8_t *actor=*(const uint8_t *const *)context;
    unsigned action=half(context+12);
    if(ffta_exposed_native_physical(context))return incoming(damage,target,ffta_poise_hp_factor(actor,target,action),ffta_blade_ward_factor(actor,target));
    const uint8_t *d=*(const uint8_t *const *)(context+0x30);
    if(custom_physical(action) || !d || ((const uint8_t *)0x083a87b0u)[d[1]*12u+4]!=1)return damage;
    /* Native magical damage classes; fixed/percentage/cost/recovery stages
     * do not gain a magic tag merely because they return positive HP. */
    if(!((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,28) ||
       (d[3]!=30 && d[3]!=39 && d[3]!=43))return damage;
    return (int)((uint64_t)(unsigned)damage*ffta_poise_hp_factor(actor,target,action)/4u);''')
exposed=once(exposed,'    int damage=ffta_original_exposed_preview(actor,target,action,item,index,mode);\n    return (uint16_t)action==0 ? incoming(damage,target) : damage;','''    FFTA_ActionSnapshot snapshot;
    unsigned opened=ffta_snapshot_begin(&snapshot,actor,target,0);
    int damage=ffta_original_exposed_preview(actor,target,action,item,index,mode);
    if((uint16_t)action==0)damage=incoming(damage,target,ffta_poise_hp_factor(actor,target,(uint16_t)action),ffta_blade_ward_factor(actor,target));
    if(opened)ffta_snapshot_end(&snapshot);
    return damage;''')
exposed=once(exposed,'    return incoming(ffta_original_exposed_combo(actor,target,strength),target);','''    FFTA_ActionSnapshot snapshot;
    unsigned opened=ffta_snapshot_begin(&snapshot,actor,target,0);
    int damage=incoming(ffta_original_exposed_combo(actor,target,strength),target,ffta_poise_factor(target),20);
    if(opened)ffta_snapshot_end(&snapshot);
    return damage;''')
(OUT/'exposed-effects.c').write_text(exposed)
sources=[OUT/'exposed-effects.c',ROOT/'src/engine/exposed-effects.s',OUT/'combat.c',OUT/'combat-hooks.s',OUT/'combat-geometry.c',ROOT/'src/engine/combat-geometry.s',OUT/'dark-hooks.s',OUT/'bindings.s']+[ROOT/f'src/engine/{n}' for n in ('action-snapshot.c','samurai-state.c','samurai-state.s','samurai-actions.c','samurai-actions.s','samurai-lifecycle.c','samurai-lifecycle.s','samurai-restoration.c','samurai-restoration.s','samurai-area.c','samurai-area.s','execution-scope.c','samurai-wound.c','samurai-wound.s','samurai-pulse.c','samurai-pulse.s','samurai-status-display.c','samurai-wound-law.c','samurai-wound-law.s')]
sources.append(ROOT/'src/engine/action-snapshot.s')
status_asm=(ROOT/'src/engine/status-display.s').read_text()
for name in ('icon','next_key','visual'):status_asm=status_asm.replace('bl ffta_status_'+name,'bl ffta_wound_status_'+name)
(OUT/'status-display.s').write_text(status_asm);sources.append(OUT/'status-display.s')
capture=(OUT/'combat.c').read_text();capture=once(capture,'int ffta_physical_final(', '#include "execution-scope.h"\nint ffta_physical_final(');capture=once(capture,'    const PhysicalDefinition *definition=physical_definition(action);','    ffta_execution_capture(reference,action,actor,target);\n    const PhysicalDefinition *definition=physical_definition(action);');(OUT/'combat.c').write_text(capture)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'samurai.elf';binary=OUT/'samurai.bin'
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'src/engine'),'-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091c0000,-e,ffta_samurai_execute_entry',*map(str,sources),'-lgcc','-o',str(elf)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True);symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
rom=bytearray(base);code=binary.read_bytes();assert rom[0x11c0000:0x11c0000+len(code)]==b'\xff'*len(code);rom[0x11c0000:0x11c0000+len(code)]=code;changes=[];clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
def hook(offset,end,name,previous=None):
 jump=(offset+5)&~3
 if previous:assert struct.unpack_from('<I',rom,jump+4)[0]==old[previous]|1,(hex(offset),previous)
 else:assert rom[offset:end]==clean[offset:end],hex(offset)
 original=rom[offset:end].hex();rom[offset:end]=b'\xc0\x46'*((end-offset)//2);struct.pack_into('<H',rom,offset,0xb408);struct.pack_into('<HHI',rom,jump,0x4b00,0x4718,symbols[name]|1);changes.append(dict(offset=offset,end=end,name=name,original=original))
for start,end,name in [(0x1300e2,0x1300f2,'ffta_physical_final_entry'),(0xa0014,0xa0020,'ffta_combat_geometry_entry'),(0x130654,0x130660,'ffta_weapon_drain_entry'),(0x130688,0x130694,'ffta_weapon_effect_entry'),(0x12f8a4,0x12f8b0,'ffta_dark_sword_element_entry'),(0xa315a,0xa3166,'ffta_dark_sword_apply_entry'),(0x13467a,0x134686,'ffta_dark_sword_law_weapon_entry')]:hook(start,end,name,name)
for start,end,name in [(0xa433c,0xa4348,'ffta_samurai_execute_entry'),(0xa4672,0xa467c,'ffta_samurai_attempt_entry'),(0x92f94,0x92fa0,'ffta_samurai_turn_end_entry')]:hook(start,end,name)
for start,end,name in [(0xcaf78,0xcaf84,'ffta_centered_equipment_entry'),(0xcb0d8,0xcb0e4,'ffta_centered_equipment_quiet_entry')]:hook(start,end,name)
hook(0xb4a1c,0xb4a28,'ffta_samurai_area_entry','ffta_area_list_entry')
hook(0xa3072,0xa307c,'ffta_samurai_success_entry','ffta_physical_success_entry')
hook(0x1342cc,0x1342d8,'ffta_samurai_law_status_entry')
hook(0x134834,0x134844,'ffta_higan_harmful_law_entry')
dispel=0x3a87b0+53*12
assert struct.unpack_from('<I',rom,dispel)[0]==0x08132c0d
struct.pack_into('<I',rom,dispel,symbols['ffta_centered_dispel_entry']|1)
assert struct.unpack_from('<I',rom,0x134350)[0]==old['ffta_physical_law_entry']|1
struct.pack_into('<I',rom,0x134350,symbols['ffta_samurai_law_entry']|1)
hook(0xa45c6,0xa45d4,'ffta_samurai_paid_entry','ffta_exposed_paid_entry')
hook(0x131b4a,0x131b56,'ffta_exposed_stage_entry','ffta_exposed_stage_entry')
hook(0xa23b8,0xa23c8,'ffta_snapshot_result_entry')
hook(0xa28e2,0xa28ee,'ffta_snapshot_native_reaction_entry')
hook(0x130200,0x13020c,'ffta_exposed_preview_entry','ffta_exposed_preview_entry')
hook(0x130454,0x130462,'ffta_exposed_combo_entry','ffta_exposed_combo_entry')
# Observe exact native copies after their existing ownership bookkeeping.
# Replace only BL instructions to these two known main-engine functions.
for source,target in [('ffta_evaluated_close','ffta_snapshotted_evaluated_close'),('ffta_copy_owner_free','ffta_snapshotted_owner_free'),('ffta_on_unit_copy','ffta_snapshotted_unit_copy'),('ffta_evaluated_init','ffta_snapshotted_evaluated_init')]:
 sites=[]
 for offset in range(0x1100000,0x1100000+len(engine)-2,2):
  a,b=struct.unpack_from('<HH',rom,offset)
  if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
  delta=((a&0x7ff)<<12)|((b&0x7ff)<<1)
  if delta&0x400000:delta-=0x800000
  if 0x08000000+offset+4+delta!=old[source]:continue
  delta=symbols[target]-(0x08000000+offset+4);assert -0x400000<=delta<0x400000 and not delta&1
  struct.pack_into('<HH',rom,offset,0xf000|((delta>>12)&0x7ff),0xf800|((delta>>1)&0x7ff));sites.append(offset)
 assert sites,(source,'No native observers installed')
 changes.append(dict(name=target,callSites=sites))
# Route the existing exact-owner lifecycle hooks through the composed layer.
for change in meta['changes']:
 name=change['name']
 if name in ('ffta_exposed_event_ko_entry','ffta_exposed_turn_entry','ffta_exposed_battle_end_entry','ffta_exposed_reset_entry','ffta_exposed_petrify_entry','ffta_exposed_status_entry','ffta_exposed_job_entry'):
  hook(change['offset'],change['offset']+change['size'],name,name)
 elif name=='ffta_exposed_cureall_entry':
  assert struct.unpack_from('<I',rom,change['offset'])[0]==old[name]|1
  struct.pack_into('<I',rom,change['offset'],symbols[name]|1)

for offset,name in [(0x3a8604+8*4,'ffta_physical_eligibility_entry'),(0x3a86f8+30*4,'ffta_physical_magnitude_entry')]:struct.pack_into('<I',rom,offset,symbols[name]|1)
assert struct.unpack_from('<I',rom,0x3a86f8+25*4)[0]==0x08131839
struct.pack_into('<I',rom,0x3a86f8+25*4,symbols['ffta_murasame_magnitude_entry']|1)
# Append one private state to each native interpreter, preserving every
# original table entry and bound. Fixed offsets remain outside linked code.
assert len(code)<0x8000
for check_at,old_limit,pointer_at,native_table,count,new_entry,dest in [
 (0x929be,126,0x929d0,0x929d4,127,'ffta_wound_turn_wait_entry',0x11c8000),
 (0x9ed4a,41,0x9ed5c,0x9ed60,42,'ffta_wound_periodic_entry',0x11c8200)]:
 assert rom[check_at]==old_limit and struct.unpack_from('<I',rom,pointer_at)[0]==0x08000000+native_table
 table_bytes=rom[native_table:native_table+4*count]+struct.pack('<I',symbols[new_entry]&~1)
 assert rom[dest:dest+len(table_bytes)]==b'\xff'*len(table_bytes)
 rom[dest:dest+len(table_bytes)]=table_bytes
 rom[check_at]=old_limit+1;struct.pack_into('<I',rom,pointer_at,0x08000000+dest)
# Reserve exactly two more OBJ tiles for Wound. Keep old icon functions and
# glyphs bound to the accepted main engine; the private layer adds key27 only.
assert rom[0x97098:0x9709c]==bytes.fromhex('f2235b00')
rom[0x97098]=0xf3
assert struct.unpack_from('<I',rom,0x9da10)[0]==old['ffta_status_icon_entry']|1
struct.pack_into('<I',rom,0x9da10,symbols['ffta_status_icon_entry']|1)
hook(0x9dd52,0x9dd62,'ffta_status_next_entry','ffta_status_next_entry')
hook(0x97ad0,0x97ae4,'ffta_status_visual_entry','ffta_status_visual_entry')
registry=json.loads((ROOT/'build/expansion/registry.json').read_text());table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
for action,mp,radius,height in [(347,4,1,2),(348,4,3,2),(349,6,2,3),(352,6,1,2),(353,10,4,3),(354,16,0,2),(355,8,1,2)]:
 lesson=next(x for x in registry['lessons'] if x['globalAbilityId']==action and x['type']=='Action');row=bytearray(clean[0x55187c+147*28:0x55187c+148*28]);struct.pack_into('<H',row,0,lesson['nameId']);row[2]=0;row[4]=mp;row[5]=1;row[6]=radius;row[7]=height;row[12:16]=bytes([63,1,1,1]);struct.pack_into('<H',row,22,0);assert not any(rom[table+action*28:table+(action+1)*28]);rom[table+action*28:table+(action+1)*28]=row
# Native directional targeting needs range mode0x40. Our installed geometry
# and area enumerator enforce three tiles; numeric range3 breaks west selection.
# Wind Draw retains its own Wind element independently of the primary katana.
row=table+348*28;rom[row+2]=2;rom[row+6]=0x40;rom[row+8]=4;rom[row+9]=0x80;rom[row+10]=2
# Moon Blossom uses the native fixed self-centered cross selector.
row=table+354*28;rom[row+8]=3;rom[row+9]=5;rom[row+10]=2
for action,mp,radius,stages in [(350,8,2,(90,1,1,1)),(351,10,0,(45,78,1,1))]:
 lesson=next(x for x in registry['lessons'] if x['globalAbilityId']==action and x['type']=='Action')
 row=bytearray(clean[0x55187c+12*28:0x55187c+13*28]);struct.pack_into('<H',row,0,lesson['nameId'])
 row[2]=0;row[4]=mp;row[5]=0;row[6]=radius;row[7]=2;row[9]=5;row[10]=2;row[12:16]=bytes(stages);struct.pack_into('<H',row,22,0)
 # Native133ECC tests selector20 under Silence. Iaido is usable there;
 # Remove Barrier's Doublecast flag; retain no Reflect/Return Magic.
 struct.pack_into('<I',row,16,(struct.unpack_from('<I',row,16)[0]|(1<<(20-11)))&~(1<<(19-11)))
 if action==350:struct.pack_into('<H',row,20,2) # Native Cure healing visual only.
 if action==351:row[8]=3 # Chakra's self-centered selection with preview help.
 assert not any(rom[table+action*28:table+(action+1)*28]);rom[table+action*28:table+(action+1)*28]=row
# Append private help after code/data assembly; no accepted main text is edited.
help_input=OUT/'help-input.gba';help_output=OUT/'help-output.gba';help_input.write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/patch-samurai-help.mjs'),str(help_input),str(help_output),str(OUT/'help.json')],check=True)
help_meta=json.loads((OUT/'help.json').read_text());rom=bytearray(help_output.read_bytes())
ART=OUT/sha(rom);ART.mkdir(exist_ok=True);(ART/'samurai.gba').write_bytes(rom);(ART/'input.gba').write_bytes(base)
report=dict(status='PRIVATE TEST: nine Samurai actions, Centered and Wound with native status display and help; complete expansion and remaining Samurai acceptance pending',baseSha1=sha(base),romSha1=sha(rom),path=str(ART/'samurai.gba'),symbols=symbols,help=help_meta,changes=changes)
(ART/'manifest.json').write_text(json.dumps(report,indent=2));(P/'samurai/current.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='symbols'},indent=2))

