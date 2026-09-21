"""Compose the Dark Knight layer over the verified local Samurai candidate."""
import hashlib,json,pathlib,struct,subprocess,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'build/expansion/probes';sha=lambda b:hashlib.sha1(b).hexdigest()
samurai=json.loads((P/'samurai/current.json').read_text())
prior=json.loads((P/'job-state/current.json').read_text())
assert prior['baseSha1']==samurai['romSha1']
base=pathlib.Path(prior['path']).read_bytes();assert sha(base)==prior['romSha1']
OUT=P/'dark-knight'/sha(base);OUT.mkdir(parents=True,exist_ok=True)
rom=bytearray(base);clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
imports={'ZERO_MAGNITUDE':struct.unpack_from('<I',base,0x3a86f8)[0],
         'ELIGIBILITY':struct.unpack_from('<I',base,0x3a8604+8*4)[0],
         'HEALING':struct.unpack_from('<I',base,0x3a86f8+25*4)[0],
         'WEAPON':prior['symbols']['ffta_samurai_weapon_valid']|1,
         'PAID':prior['symbols']['ffta_custom_physical_paid']|1,
         'STAGE':prior['symbols']['ffta_exposed_native_stage']|1,
         'LAW_WEAPONS':prior['symbols']['ffta_samurai_law_weapons']|1}
(OUT/'dark-knight-imports.h').write_text('\n'.join(f'#define DRK_PRIOR_{n} 0x{v:08x}u' for n,v in imports.items())+'\n#define DRK_DESCRIPTOR_BANK 0x0922c000u\n')
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)
generated=pathlib.Path(samurai['path']).parent.parent
combat=(generated/'combat.c').read_text().replace('ffta_samurai_weapon_valid','ffta_drk_weapon_valid')
combat=once(combat,'static const PhysicalDefinition physical_definitions[]={','static const PhysicalDefinition physical_definitions[]={\n    {FFTA_DRK_A1,150,100},{FFTA_DRK_A5,100,100},{FFTA_DRK_A6,115,100},{FFTA_DRK_A7,140,100},{FFTA_DRK_A8,175,100},')
combat=once(combat,'if (action!=FFTA_SLD_AX_A3','if (action!=FFTA_DRK_A7 && action!=FFTA_DRK_A8 && action!=FFTA_SLD_AX_A3')
combat='#include \"action-snapshot.h\"\nextern unsigned ffta_drk_outgoing_numerator(const uint8_t *,const uint8_t *,unsigned,unsigned);\nextern unsigned ffta_drk_incoming_numerator(const uint8_t *,const uint8_t *,unsigned,unsigned);\n'+combat
combat=once(combat,'/(definition->denominator*1600u)','*((reference>0 && !restorative)?ffta_drk_outgoing_numerator(actor,target,action,1):8)*((reference>0 && !restorative)?ffta_drk_incoming_numerator(actor,target,action,1):40)/(definition->denominator*512000u)')
combat=once(combat,'    unsigned weapon=ffta_primary_weapon(actor);\n    if (!actor || !target', '    unsigned weapon=ffta_primary_weapon(actor);\n    if(action==FFTA_DRK_A5 && actor==target)return 0;\n    if (!actor || !target')
combat='extern unsigned ffta_drk_line_numerator(const unsigned char *,const unsigned char *);\n'+combat
combat=once(combat,' : definition->numerator;',' : action==FFTA_DRK_A7 ? ffta_drk_line_numerator(actor,target) : definition->numerator;')
(OUT/'combat.c').write_text(combat)
combat_asm=(generated/'combat-hooks.s').read_text()
for reg,value,label in [('r0','r1','8f'),('r2','r0','9f')]:
 combat_asm=once(combat_asm,f'    ldr {reg},=FFTA_DRK_A2',''.join(f'    ldr {reg},=FFTA_DRK_A{a}\n    cmp {value},{reg}\n    beq {label}\n' for a in (1,5,6,7,8))+f'    ldr {reg},=FFTA_DRK_A2')
(OUT/'combat-hooks.s').write_text(combat_asm)
paid=(ROOT/'src/engine/samurai-actions.s').read_text()
paid=paid[:paid.index('.align 2\n.global ffta_samurai_law_entry')]
paid=paid.replace('ffta_samurai_paid_entry','ffta_drk_paid_entry').replace('bl ffta_custom_physical_paid','bl ffta_drk_paid')
(OUT/'paid.s').write_text(paid)
element=(generated/'dark-hooks.s').read_text()
element=element[:element.index('@ Law kind10')]
element=element.replace('ffta_dark_sword_element_entry','ffta_drk_element_entry')
element=once(element,'    ldr r3,=FFTA_DRK_A2','    ldr r3,=FFTA_DRK_A1\n    cmp r0,r3\n    beq 4f\n    ldr r3,=FFTA_DRK_A8\n    cmp r0,r3\n    bne 3f\n4:  pop {r0,r3}\n    movs r0,#8\n    bx lr\n3:\n    ldr r3,=FFTA_DRK_A2')
(OUT/'element.s').write_text(element)
stage=(ROOT/'src/engine/exposed-effects.s').read_text()
stage=stage[:stage.index('.align 2\n.global ffta_exposed_combo_entry')]
stage=stage.replace('ffta_exposed_preview','ffta_drk_exposed_preview').replace('ffta_original_exposed_preview','ffta_drk_original_exposed_preview')
stage=stage.replace('ffta_exposed_stage_entry','ffta_drk_stage_entry').replace('bl ffta_exposed_native_stage','bl ffta_drk_stage')
(OUT/'stage.s').write_text(stage)
law=(ROOT/'src/engine/dark-sword-hooks.s').read_text()
law='.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n'+law[law.index('@ Law kind10'):law.index('@ A315A')]
law=law.replace('ffta_dark_sword_law_weapon_entry','ffta_drk_law_weapon_entry').replace('bl ffta_dark_law_weapons','bl ffta_drk_law_weapons')
(OUT/'law.s').write_text(law)
geometry=(generated/'combat-geometry.c').read_text()
geometry=once(geometry,'if((uint16_t)action==FFTA_SAM_A2)', 'if((uint16_t)action==FFTA_SAM_A2 || (uint16_t)action==FFTA_DRK_A7)')
geometry=once(geometry,'        (uint16_t)action!=FFTA_DRK_A2','        (uint16_t)action!=435 &&\n        (uint16_t)action!=FFTA_DRK_A1 &&\n        (uint16_t)action!=FFTA_DRK_A5 &&\n        (uint16_t)action!=FFTA_DRK_A6 &&\n        (uint16_t)action!=FFTA_DRK_A8 &&\n        (uint16_t)action!=FFTA_DRK_A2')
(OUT/'geometry.c').write_text(geometry)
bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n'
aliases={'ffta_drk_previous_centered_event':'ffta_centered_event','ffta_drk_previous_centered_turn_end':'ffta_centered_turn_end',**{f'ffta_drk_previous_status_{n}':f'ffta_wound_status_{n}' for n in ('icon','next_key','visual')}}
for name in (*aliases,'ffta_job_state','ffta_job_origin','ffta_job_peers','ffta_action_actor','ffta_action_claim','ffta_action_claimed','ffta_action_unit_at','ffta_action_reaction_kind','ffta_action_reaction_value','ffta_reaction_queue_append','ffta_action_unit_flags','ffta_action_set_actor_flags','ffta_action_reactions_enabled','ffta_action_origin','ffta_snapshot_begin','ffta_snapshot_end','ffta_exposed_native_physical','ffta_action_paid','ffta_action_paid_count','ffta_action_phase','ffta_action_id','ffta_action_hp_lost','ffta_samurai_restoration_action','ffta_samurai_restoration_eligibility','ffta_exposed_can_apply','ffta_exposed_incoming_numerator','ffta_centered_factor','ffta_poise_hp_factor','ffta_blade_ward_factor','ffta_execution_capture','ffta_finisher_numerator','ffta_physical_rider_reference','ffta_samurai_line_geometry','ffta_arc_geometry','ffta_projectile_los'):
 address=prior['symbols'].get(aliases.get(name,name))
 if address is None:
  main={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
  address=main[name]
 bindings+=f'.align 2\n.global {name}\n.thumb_func\n{name}:\n push {{r3}}\n ldr r3,=0x{address|1:08x}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(OUT/'bindings.s').write_text(bindings)
status_asm=(ROOT/'src/engine/status-display.s').read_text().replace('ffta_status_','ffta_drk_status_').replace('ffta_original_status_icon','ffta_drk_unused_original_status_icon')
(OUT/'status.s').write_text(status_asm)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
elf=OUT/'dark-knight.elf';binary=OUT/'dark-knight.bin'
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11',
 '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib',
 '-I',str(ROOT/'build/expansion'),'-I',str(ROOT/'src/engine'),'-I',str(OUT),'-Wl,-Ttext=0x09200000,-e,ffta_drk_eligibility_entry',
 str(ROOT/'src/engine/dark-knight.c'),str(ROOT/'src/engine/dark-knight.s'),str(ROOT/'src/engine/dark-knight-support.c'),str(ROOT/'src/engine/dark-knight-damage.c'),str(ROOT/'src/engine/dark-knight-state.c'),str(ROOT/'src/engine/dark-knight-status.c'),str(ROOT/'src/engine/dark-knight-reactions.c'),
 *map(str,[OUT/n for n in ('combat.c','combat-hooks.s','paid.s','element.s','stage.s','law.s','geometry.c','bindings.s','status.s')]),
 str(ROOT/'src/engine/combat-geometry.s'),'-lgcc','-o',str(elf)],check=True,cwd=ROOT)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
code=binary.read_bytes();assert len(code)<0x28000
assert rom[0x1200000:0x1200000+len(code)]==b'\xff'*len(code),'DRK reserved ROM occupied'
rom[0x1200000:0x1200000+len(code)]=code
for offset,name in [(0x3a8604+8*4,'ffta_drk_eligibility_entry'),(0x3a86f8+25*4,'ffta_drk_healing_entry')]:
 struct.pack_into('<I',rom,offset,symbols[name]|1)
struct.pack_into('<I',rom,0x3a86f8+30*4,symbols['ffta_physical_magnitude_entry']|1)
struct.pack_into('<I',rom,0x3a86f8,symbols['ffta_drk_zero_magnitude_entry']|1)
changes=[]
for old,new in [('ffta_additional_snapshot_flags','ffta_drk_snapshot_flags'),('ffta_additional_action_event','ffta_drk_action_event'),('ffta_additional_beneficial','ffta_drk_beneficial'),('ffta_additional_hp_loss','ffta_drk_hp_loss'),('ffta_additional_reaction_queue','ffta_drk_reaction_queue')]:
 offset=prior['symbols'][old]-0x08000000
 assert offset%4==0 and rom[offset:offset+16]==bytes.fromhex('00207047')+bytes(12)
 struct.pack_into('<HHI',rom,offset,0x4b00,0x4718,symbols[new]|1)
 changes.append(dict(name=old,offset=offset,provider=new,size=8))
def hook(offset,end,name,previous=None):
 jump=(offset+5)&~3
 if previous:assert struct.unpack_from('<I',rom,jump+4)[0]==prior['symbols'][previous]|1,(hex(offset),previous)
 else:assert rom[offset:end]==clean[offset:end],hex(offset)
 original=rom[offset:end].hex();rom[offset:end]=b'\xc0\x46'*((end-offset)//2)
 struct.pack_into('<H',rom,offset,0xb408);struct.pack_into('<HHI',rom,jump,0x4b00,0x4718,symbols[name]|1)
 changes.append(dict(offset=offset,end=end,name=name,original=original))
for start,end,name in ((0x1300e2,0x1300f2,'ffta_physical_final_entry'),(0x130654,0x130660,'ffta_weapon_drain_entry'),(0x130688,0x130694,'ffta_weapon_effect_entry')):hook(start,end,name,name)
hook(0xa45c6,0xa45d4,'ffta_drk_paid_entry','ffta_samurai_paid_entry')
hook(0x12f8a4,0x12f8b0,'ffta_drk_element_entry','ffta_dark_sword_element_entry')
hook(0x133e18,0x133e24,'ffta_drk_usable_entry')
hook(0x12ed98,0x12eda8,'ffta_drk_mp_cost_entry')
hook(0x131b4a,0x131b56,'ffta_drk_stage_entry','ffta_exposed_stage_entry')
hook(0x130200,0x13020c,'ffta_drk_exposed_preview_entry','ffta_exposed_preview_entry')
hook(0x13467a,0x134686,'ffta_drk_law_weapon_entry','ffta_dark_sword_law_weapon_entry')
hook(0xa0014,0xa0020,'ffta_combat_geometry_entry','ffta_combat_geometry_entry')
assert struct.unpack_from('<I',rom,0x9da10)[0]==prior['symbols']['ffta_status_icon_entry']|1
struct.pack_into('<I',rom,0x9da10,symbols['ffta_drk_status_icon_entry']|1)
hook(0x9dd52,0x9dd62,'ffta_drk_status_next_entry','ffta_status_next_entry')
hook(0x97ad0,0x97ae4,'ffta_drk_status_visual_entry','ffta_status_visual_entry')
assert rom[0x97098:0x9709c]==bytes.fromhex('f3235b00');rom[0x97098]=0xf8
changes.append(dict(name='shared status OBJ pool',offset=0x97098,value=0xf8,tiles=[0x1e6,0x1e9]))
regions=[(0x1100000,len((ROOT/'build/expansion/engine.bin').read_bytes())),(0x11c0000,len((generated/'samurai.bin').read_bytes())),(0x11d0000,len((P/'job-state'/prior['baseSha1']/'state.bin').read_bytes()))]
for old,new in [('ffta_centered_event','ffta_drk_lifecycle_event'),('ffta_centered_turn_end','ffta_drk_lifecycle_turn_end')]:
 target=prior['symbols'][old];sites=[]
 for start,size in regions:
  for offset in range(start,start+size-2,2):
   a,b=struct.unpack_from('<HH',rom,offset)
   if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
   delta=((a&0x7ff)<<12)|((b&0x7ff)<<1)
   if delta&0x400000:delta-=0x800000
   if 0x08000000+offset+4+delta!=target:continue
   delta=symbols[new]-(0x08000000+offset+4);assert -0x400000<=delta<0x400000
   struct.pack_into('<HH',rom,offset,0xf000|((delta>>12)&0x7ff),0xf800|((delta>>1)&0x7ff));sites.append(offset)
  for offset in range(start,start+size-3,4):
   if struct.unpack_from('<I',rom,offset)[0]==target|1:
    struct.pack_into('<I',rom,offset,symbols[new]|1);sites.append(offset)
 assert sites,old
 changes.append(dict(name=new,sites=sites))
table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
lesson=next(x for x in registry['lessons'] if x['id']=='DRK-A4')
action=lesson['globalAbilityId'];assert action==359
row=bytearray(clean[0x55187c+12*28:0x55187c+13*28])
struct.pack_into('<H',row,0,lesson['nameId'])
row[2]=0;row[4]=8;row[5]=0;row[6]=0;row[7]=2
row[8]=3;row[9]=1;row[10]=0;row[12:16]=bytes((45,90,1,1))
flags=struct.unpack_from('<I',row,16)[0]
flags=(flags|(1<<(20-11)))&~((1<<(19-11))|(1<<(18-11)))
struct.pack_into('<I',row,16,flags);struct.pack_into('<H',row,20,8);struct.pack_into('<H',row,22,0)
assert not any(rom[table+action*28:table+(action+1)*28])
rom[table+action*28:table+(action+1)*28]=row
lesson=next(x for x in registry['lessons'] if x['id']=='DRK-A1');action=lesson['globalAbilityId'];assert action==356
row=bytearray(clean[0x55187c+147*28:0x55187c+148*28]);struct.pack_into('<H',row,0,lesson['nameId'])
row[2]=8;row[4]=0;row[5]=1;row[6]=1;row[7]=2;row[12:16]=bytes((63,1,1,1));struct.pack_into('<H',row,22,0)
assert not any(rom[table+action*28:table+(action+1)*28]);rom[table+action*28:table+(action+1)*28]=row
lesson=next(x for x in registry['lessons'] if x['id']=='DRK-A7');action=lesson['globalAbilityId'];assert action==362
row=bytearray(clean[0x55187c+147*28:0x55187c+148*28]);struct.pack_into('<H',row,0,lesson['nameId'])
row[2]=0;row[4]=10;row[5]=1;row[6]=0x40;row[7]=2
row[8]=4;row[9]=0x80;row[10]=2;row[12:16]=bytes((63,1,1,1));struct.pack_into('<H',row,22,0)
assert not any(rom[table+action*28:table+(action+1)*28]);rom[table+action*28:table+(action+1)*28]=row
# Extend the shared native descriptor domain without changing its first209 rows.
# Root owns assignments213/214/216/217 for this job; other reserved rows stay0.
descriptors=bytearray(rom[0x553e70:0x553e70+209*4])+bytearray(11*4)
descriptors[213*4:214*4]=bytes((8,19,26,0)) # native Stop application19/status23
descriptors[214*4:215*4]=bytes((8,51,26,0)) # native Slow application51/status22
assert rom[0x122c000:0x122c000+len(descriptors)]==b'\xff'*len(descriptors)
rom[0x122c000:0x122c000+len(descriptors)]=descriptors
users=[]
for offset in range(0,len(clean)-3,4):
 if struct.unpack_from('<I',rom,offset)[0]==0x08553e70:
  struct.pack_into('<I',rom,offset,0x0922c000);users.append(offset)
assert users==[0xb4cec,0xc1ca4,0xc230c,0x12f2a0,0x12f348,0x12f3c8],list(map(hex,users))
changes.append(dict(name='DRK native descriptor extension',offset=0x122c000,rows=220,users=users))
for action,mp,radius,descriptor in ((361,10,2,213),(363,14,0,214)):
 lesson=next(x for x in registry['lessons'] if x['globalAbilityId']==action and x['type']=='Action')
 row=bytearray(clean[0x55187c+147*28:0x55187c+148*28]);struct.pack_into('<H',row,0,lesson['nameId'])
 row[2]=8 if action==363 else 0;row[4]=mp;row[5]=1;row[6]=radius;row[7]=2
 row[12:16]=bytes((63,descriptor,1,1));struct.pack_into('<H',row,22,0)
 if action==363:row[8]=3;row[9]=5;row[10]=2
 assert not any(rom[table+action*28:table+(action+1)*28]);rom[table+action*28:table+(action+1)*28]=row
# Two owned beneficial effects extend the native application and mask banks.
for old,count,stride,destination,users in [(0x3a87b0,93,12,0x122c400,[0x1323b8,0x132430,0x133920,0x133984,0x1339a4]),(0x52790c,93,12,0x122cc00,[0x1339c8])]:
 bank=bytearray(rom[old:old+count*stride])+bytearray(6*stride)
 for app in (97,98):
  if old==0x3a87b0:
   struct.pack_into('<III',bank,app*12,symbols['ffta_drk_'+('last_resort' if app==97 else 'tbn')+'_apply_entry']|1,0,255)
  else:
   mask=bytearray(bank[82*12:83*12])
   for status in range(44):mask[(2*status+1)//8]&=~(1<<((2*status+1)%8))
   bank[app*12:(app+1)*12]=mask
 found=[]
 for offset in range(0,len(clean)-3,4):
  if struct.unpack_from('<I',rom,offset)[0]==0x08000000+old:
   struct.pack_into('<I',rom,offset,0x08000000+destination);found.append(offset)
 assert found==users,(hex(old),found)
 assert rom[destination:destination+len(bank)]==b'\xff'*len(bank)
 rom[destination:destination+len(bank)]=bank;changes.append(dict(name='DRK application/mask bank',offset=destination,users=found))
rom[0x122c000+216*4:0x122c000+217*4]=bytes((8,97,23,0))
rom[0x122c000+217*4:0x122c000+218*4]=bytes((8,98,23,0))
for action in (360,364):
 lesson=next(x for x in registry['lessons'] if x['globalAbilityId']==action and x['type']=='Action')
 row=bytearray(rom[table+(359 if action==364 else 361)*28:table+(360 if action==364 else 362)*28])
 struct.pack_into('<H',row,0,lesson['nameId']);row[4]=10 if action==364 else 8
 row[5]=0;row[6]=3 if action==364 else 1;row[8]=1;row[9]=1;row[10]=0
 row[12:16]=bytes((217,1,1,1)) if action==364 else bytes((63,216,1,1))
 # Native selector11 allows self targeting; keep the hostile physical mode.
 if action==360:row[16]|=1
 assert not any(rom[table+action*28:table+(action+1)*28]);rom[table+action*28:table+(action+1)*28]=row
# Hidden reaction-only action rows never enter teaching/AP/command lists.
actions=bytearray(rom[table:table+432*28])+bytearray(4*28)
for action,lesson_id,descriptor in [(433,'DRK-R1',45),(434,'DRK-R2',219)]:
 lesson=next(x for x in registry['lessons'] if x['id']==lesson_id)
 row=bytearray(rom[table+(359 if action==433 else 361)*28:table+(360 if action==433 else 362)*28])
 struct.pack_into('<H',row,0,lesson['nameId']);row[2]=0 if action==433 else 8
 row[4]=0;row[5]=0;row[6]=0 if action==433 else 3;row[7]=3;row[8]=3 if action==433 else 1
 row[9]=1;row[10]=0;row[12:16]=bytes((descriptor,1,1,1))
 actions[action*28:(action+1)*28]=row
users=[0x23320,0x236ac,0x25998,0x26c9c,0x26d3c,0x26e18,0x27048,0x27170,0x279a0,0x27a94,0xa784c,0xb5d18,0xc3080,0xc3474,0xccd84,0x133e70,0x13416c]
for pointer in users:
 assert struct.unpack_from('<I',rom,pointer)[0]==0x08000000+table
 struct.pack_into('<I',rom,pointer,0x09228000)
assert rom[0x1228000:0x1228000+len(actions)]==b'\xff'*len(actions)
rom[0x1228000:0x1228000+len(actions)]=actions
rom[0x122c000+219*4:0x122c000+220*4]=bytes((8,21,23,0))
changes.append(dict(name='hidden reaction global actions',offset=0x1228000,rows=436,users=users,owned=[433,434]))
(OUT/'help-input.gba').write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/jobs/dark-knight/patch-help.mjs'),str(OUT/'help-input.gba'),str(OUT/'help-output.gba'),str(OUT/'help.json')],check=True)
rom=bytearray((OUT/'help-output.gba').read_bytes());help_meta=json.loads((OUT/'help.json').read_text())
ART=OUT/sha(rom);ART.mkdir(exist_ok=True)
(ART/'dark-knight.gba').write_bytes(rom);(ART/'input.gba').write_bytes(base)
report=dict(status='PRIVATE UNACCEPTED BATCH: Last Resort/TBN/support/reaction implementation; full Dark Knight acceptance pending',
 romSha1=sha(rom),baseSha1=sha(base),fixtureBaseSha1=samurai['baseSha1'],heapEnd=prior['heapEnd'],path=str(ART/'dark-knight.gba'),
 symbols=symbols,priorSymbols=prior['symbols'],imports=imports,newActions=[356,359,360,361,362,363,364],hiddenActions=[433,434],pendingActions=[],help=help_meta,changes=changes,
 reservation=dict(start=0x1200000,end=0x1240000,used=len(code)),persistentRAM=0)
(ART/'manifest.json').write_text(json.dumps(report,indent=2))
(P/'dark-knight/current.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('symbols','priorSymbols')},indent=2))
