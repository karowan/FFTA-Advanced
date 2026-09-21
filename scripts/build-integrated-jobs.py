"""Compose declared job exports and native tables, never overlapping ROM patches.

The private builders supply independently compiled, disjoint modules. Every
native entry/table and shared provider below has one explicit integration owner.
This development candidate does not imply that unfinished lessons are complete.
"""
import hashlib
import json
import pathlib
import struct
import subprocess
import shutil
from ffta_terrain import material_table
from arm_literal_relocations import ELFData
from native_table_literals import authenticate, native_literal_allowed
import importlib.util

ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/'build/expansion/probes'
sha=lambda data:hashlib.sha1(data).hexdigest()
read=lambda name:json.loads((P/name/'current.json').read_text())
base_meta=read('job-state');samurai=read('samurai')
meta={name:read(name) for name in ('dark-knight','viking','chemist')}
base=pathlib.Path(base_meta['path']).read_bytes()
assert sha(base)==base_meta['romSha1'] and base_meta['baseSha1']==samurai['romSha1']
images={name:pathlib.Path(m['path']).read_bytes() for name,m in meta.items()}
for name,m in meta.items():
    assert sha(images[name])==m['romSha1'] and m['baseSha1']==sha(base),(name,'different common base')
rom=bytearray(base)
OUT=P/'integrated-jobs'/sha(base);OUT.mkdir(parents=True,exist_ok=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
RANGES={'dark-knight':(0x1200000,0x1240000),'viking':(0x1240000,0x1280000),'chemist':(0x1280000,0x12c0000)}
CODE=0x11e0000;ACTIONS=0x11e8000;DESCRIPTORS=0x11ec000;APPLICATIONS=0x11ec400;MASKS=0x11ed000
assert rom[CODE:0x1200000]==b'\xff'*0x20000,'central reservation occupied'
for name,(start,end) in RANGES.items():
    assert rom[start:end]==b'\xff'*(end-start),(name,'reservation occupied')
    rom[start:end]=images[name][start:end]
changes=[]
terrain=json.loads((ROOT/'notes/terrain-materials.json').read_text())
materials=material_table((ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes(),terrain)
assert 0x11f0000+len(materials)<=0x1200000
rom[0x11f0000:0x11f0000+len(materials)]=materials
changes.append(dict(kind='Geomancer material catalog',address=0x091f0000,bytes=len(materials),maps=len(terrain['maps']),status=terrain['status']))

def once(source,old,new):
    assert source.count(old)==1,(old,source.count(old))
    return source.replace(old,new)

# Generate one complete custom-physical finalizer from the current compiled
# DRK definition set, adding Reaving and its factor BEFORE the single division.
drk_work=pathlib.Path(meta['dark-knight']['path']).parent.parent
combat=(drk_work/'combat.c').read_text()
combat=once(combat,'static const PhysicalDefinition physical_definitions[]={',
    'static const PhysicalDefinition physical_definitions[]={\n    {FFTA_DNC_A1,85,100},{FFTA_DNC_A4,80,100},{FFTA_DNC_A5,80,100},{FFTA_DNC_A7,1,1},{FFTA_DNC_A8,160,100},{FFTA_DNC_A9,95,100},{FFTA_VIK_A3,85,100},{FFTA_VIK_A6,100,100},{435,1,1},')
combat=once(combat,'/(definition->denominator*512000u)',
    '*((reference>0 && !restorative)?ffta_viking_outgoing_numerator(actor,target,action):1000)/(definition->denominator*512000000ULL)')
combat='extern unsigned ffta_viking_outgoing_numerator(const unsigned char *,const unsigned char *,unsigned);\n'+combat
combat=once(combat,'/(definition->denominator*512000000ULL)',
    '*((reference>0 && !restorative)?ffta_bard_outgoing(actor,target,action,1):50)/(definition->denominator*25600000000ULL)')
combat='extern unsigned ffta_bard_outgoing(const unsigned char *,const unsigned char *,unsigned,unsigned);\n'+combat
combat=once(combat,'/(definition->denominator*25600000000ULL)',
    '*((reference>0 && !restorative)?ffta_turn_damage_numerator(actor,target,action,1):20)/(definition->denominator*512000000000ULL)')
combat='extern unsigned ffta_turn_damage_numerator(const unsigned char *,const unsigned char *,unsigned,unsigned);\n'+combat
formula=next(line for line in combat.splitlines() if line.strip().startswith('magnitude=magnitude*numerator*incoming'))
denominator='(definition->denominator*512000000000ULL)'
assert formula.endswith('/'+denominator+';')
product=formula[:-len('/'+denominator+';')]+';'
combat=once(combat,formula,product+'\n    ffta_integrated_barrier_candidate(actor,target,action,\n        (reference>0 && !restorative)?(unsigned)(magnitude*2u/'+denominator+'):0);\n    magnitude/='+denominator+';')
combat='extern void ffta_integrated_barrier_candidate(const unsigned char *,const unsigned char *,unsigned,unsigned);\n'+combat
for old,new in [('ffta_drk_weapon_valid','ffta_integrated_weapon_valid'),
                ('ffta_physical_eligibility','ffta_integrated_physical_eligibility'),
                ('ffta_physical_magnitude','ffta_integrated_physical_magnitude'),
                ('ffta_physical_final','ffta_integrated_physical_final')]:combat=combat.replace(old,new)
combat='#include "dancer.h"\n#include "geomancer.h"\n#include "mystic-knight.h"\n'+combat
combat=once(combat,'if (!definition) return reference;',
    'if (!definition) return action?reference:ffta_myk_fight_restorative(reference,actor);')
combat=combat.replace('ffta_drk_incoming_numerator','ffta_integrated_incoming_numerator')
combat=once(combat,'static const PhysicalDefinition physical_definitions[]={',
    'static const PhysicalDefinition physical_definitions[]={\n'+''.join('{%d,%d,100},'%(i,80 if i in (414,418,419) else 85 if i==421 else 100) for i in range(410,422)))
combat=once(combat,'    if (!physical_definition(action))\n        return ((int (*)(const uint8_t *))0x0813189du)(context);',
    '    if(ffta_myk_action(action))return ffta_myk_magnitude(context);\n    if(action==FFTA_GEO_WRATH_ACTION)return ffta_geo_magnitude(context);\n    if(ffta_dancer_physical(action))return ffta_dancer_magnitude(context);\n    if (!physical_definition(action))\n        return ((int (*)(const uint8_t *))0x0813189du)(context);')
combat=once(combat,'    if (!physical_definition(action))\n        return ((unsigned (*)(const uint8_t *))0x08130a95u)(context);',
    '    if(ffta_myk_action(action))return ffta_myk_eligibility(context);\n    if(ffta_dancer_physical(action))return ffta_dancer_eligibility(context);\n    if (!physical_definition(action))\n        return ((unsigned (*)(const uint8_t *))0x08130a95u)(context);')
combat=once(combat,'unsigned restorative=primary &&','unsigned restorative=!ffta_dancer_virtual(action) && primary &&')
combat=once(combat,'(unsigned)(magnitude*2u/'+denominator+')',
    '(unsigned)ffta_dancer_scaled(magnitude*2u,'+denominator+',actor,target,action,1)')
combat=once(combat,'magnitude/='+denominator+';',
    'magnitude=(reference>0 && !restorative)?ffta_dancer_scaled(magnitude,'+denominator+',actor,target,action,1):magnitude/'+denominator+';')
combat='#include \"custom-laws.h\"\n'+once(combat,'    const PhysicalDefinition *definition=physical_definition(action);','    reference=ffta_custom_law_reference(reference,action,actor,target);\n    const PhysicalDefinition *definition=physical_definition(action);')
(OUT/'combat.c').write_text(combat)
asm=(drk_work/'combat-hooks.s').read_text()
for register,value,label in [('r0','r1','8f'),('r2','r0','9f')]:
    anchor=f'    ldr {register},=FFTA_DRK_A2'
    skip=f'.Lmyk_skip_{register}'
    asm=once(asm,anchor,f'    ldr {register},=410\n    cmp {value},{register}\n    blo {skip}\n    ldr {register},=421\n    cmp {value},{register}\n    bhi {skip}\n    b {label}\n{skip}:\n'+anchor)
    asm=once(asm,anchor,''.join(f'    ldr {register},={action}\n    cmp {value},{register}\n    beq {label}\n' for action in ('FFTA_VIK_A3','FFTA_VIK_A6','434','435','FFTA_DNC_A1','FFTA_DNC_A4','FFTA_DNC_A5','FFTA_DNC_A7','FFTA_DNC_A8','FFTA_DNC_A9'))+anchor)
for name in ('physical_final','physical_eligibility','physical_magnitude','weapon_drain','weapon_effect'):
    asm=asm.replace('ffta_'+name,'ffta_integrated_'+name)
(OUT/'combat-hooks.s').write_text(asm)
stage=(ROOT/'src/engine/exposed-effects.s').read_text().split('.align 2\n.global ffta_exposed_combo_entry')[0]
stage=stage.replace('ffta_exposed_','ffta_integrated_exposed_').replace('ffta_original_exposed_preview','ffta_integrated_original_exposed_preview')
(OUT/'stage.s').write_text(stage)
status=(ROOT/'src/engine/status-display.s').read_text().replace('ffta_status_','ffta_integrated_status_').replace('ffta_original_status_icon','ffta_integrated_original_status_icon')
(OUT/'status.s').write_text(status)
hp_asm=(ROOT/'src/engine/action-snapshot.s').read_text().split('.align 2\n.global ffta_action_hp_apply_entry')[1].split('.align 2\n.global ffta_original_action_hp_apply')[0]
hp_asm='.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n.align 2\n.global ffta_action_hp_apply_entry'+hp_asm
hp_asm=hp_asm.replace('ffta_action_hp_apply','ffta_integrated_native_hp_apply')
hp_asm=once(hp_asm,'    pop {r3}\n','    pop {r3}\n    mov r2,lr @ exact native writer caller, before C/veneer calls\n')
(OUT/'hp-entry.s').write_text(hp_asm)
direct=(ROOT/'src/engine/dark-sword.c').read_text().replace('ffta_dark_sword_apply','ffta_integrated_dark_sword_apply')
direct='extern unsigned ffta_integrated_direct_hp_apply(unsigned char *,int);\n'+once(direct,
    '((unsigned (*)(uint8_t *,int))0x080a2211u)(target,delta)',
    'ffta_integrated_direct_hp_apply(target,delta)')
direct='#include \"dancer.h\"\n#include \"mystic-knight.h\"\n'+direct
direct=once(direct,'unsigned after=half(target+0x18),action=half(object+0x10);','unsigned after=half(target+0x18),action=half(object+0x10);\n    ffta_dancer_drain(target,before,object);\n    ffta_myk_resource(target,before,object,row);')
(OUT/'direct-riders.c').write_text(direct)
callbacks=r'''.syntax unified
.cpu arm7tdmi
.thumb
.text
.macro callback name
.align 2
.global \\name\()_entry
.thumb_func
\\name\()_entry:
 push {r4-r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl \\name
 mov sp,r4
 pop {r4-r5}
 pop {r1}
 bx r1
.endm
callback ffta_integrated_eligibility
callback ffta_integrated_challenged_apply
callback ffta_integrated_zero_magnitude
callback ffta_integrated_item_healing
callback ffta_integrated_technique_healing
callback ffta_integrated_mp_restoration
callback ffta_bard_buff_apply
callback ffta_bard_application
callback ffta_bard_reaction_apply
callback ffta_bard_mp_cost
callback ffta_bard_compatibility
callback ffta_dancer_fury_apply
callback ffta_dancer_witch_hunt
callback ffta_dancer_status_accuracy
callback ffta_geo_element
callback ffta_geo_torrent_apply
callback ffta_myk_element
callback ffta_myk_usable
callback ffta_myk_accuracy
'''
# Python preserves backslashes in the assembly macro syntax explicitly.
callbacks=callbacks.replace('\\\\','\\')
(OUT/'callbacks.s').write_text(callbacks)
# Preserve original application callbacks behind one change observer. Native
# sources are fixed ROM entries; custom sources are explicit job exports.
observed_apps=[2,3,10,17,31,32,33,52,60,70,73,78,82,83,84,93,95,98,102,103,109,110]
application_source='#include <stdint.h>\n#include "geomancer.h"\nextern uint8_t *ffta_bard_buff_apply(uint8_t *);\nuint8_t *ffta_bard_original_application(uint8_t *c,unsigned id){ switch(id){\n'
for app in observed_apps:
    if app==110:application_source+='case 110:return ffta_geo_ward_apply(c);\n';continue
    if app==109:application_source+='case 109:return ffta_geo_updraft_apply(c);\n';continue
    if app in (102,103): application_source+=f'case {app}:return ffta_bard_buff_apply(c);\n';continue
    if app<93: address=struct.unpack_from('<I',base,0x3a87b0+12*app)[0]
    else:
        job={93:'viking',95:'chemist',98:'dark-knight'}[app]
        bank=struct.unpack_from('<I',images[job],0x1323b8)[0]-0x08000000
        address=struct.unpack_from('<I',images[job],bank+12*app)[0]
    application_source+=f'case {app}:return ((uint8_t *(*)(uint8_t *)){address}u)(c);\n'
application_source+='default:return c;}}\n';(OUT/'bard-applications.c').write_text(application_source)
status_gate=(ROOT/'src/engine/chemist-state.s').read_text().replace('ffta_chemist_status_entry','ffta_bard_status_entry').replace('ffta_chemist_status_gate','ffta_bard_status_gate')
(OUT/'bard-status.s').write_text(status_gate)
entry='.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'
for name in ('mp_cost','compatibility'):
    entry+=f'.align 2\n.global ffta_bard_{name}_hook\n.thumb_func\nffta_bard_{name}_hook:\n pop {{r3}}\n b ffta_bard_{name}_entry\n'
entry+='.align 2\n.global ffta_dancer_status_accuracy_hook\n.thumb_func\nffta_dancer_status_accuracy_hook:\n pop {r3}\n b ffta_dancer_status_accuracy_entry\n'
entry+='.align 2\n.global ffta_myk_usable_hook\n.thumb_func\nffta_myk_usable_hook:\n pop {r3}\n b ffta_myk_usable_entry\n'
(OUT/'bard-entry.s').write_text(entry)
dancer_element=(drk_work/'element.s').read_text().replace('ffta_drk_element_entry','ffta_dancer_element_entry')
dancer_element=once(dancer_element,'    ldr r3,=FFTA_DRK_A2',''.join(f'    ldr r3,=FFTA_DNC_A{n}\n    cmp r0,r3\n    beq 1f\n' for n in (1,4,5,7,9))+'    ldr r3,=FFTA_DRK_A2')
dancer_element=once(dancer_element,'    ldr r3,=435','    ldr r3,=FFTA_GEO_A8\n    cmp r0,r3\n    bne 8f\n    pop {r0,r3}\n    ldr r3,=ffta_geo_element_entry\n    bx r3\n8:\n    ldr r3,=435')
dancer_element=once(dancer_element,'    ldr r3,=435',
    '    ldr r3,=410\n    cmp r0,r3\n    blo 7f\n    ldr r3,=420\n    cmp r0,r3\n    bls 6f\n    ldr r3,=422\n    cmp r0,r3\n    bne 7f\n6:\n    pop {r0,r3}\n    ldr r3,=ffta_myk_element_entry\n    bx r3\n7:\n    ldr r3,=435')
(OUT/'dancer-element.s').write_text(dancer_element)
dancer_law=(ROOT/'src/engine/dark-sword-hooks.s').read_text().split('@ Law kind10')[1].split('@ A315A')[0]
dancer_law='.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n@ Law kind10'+dancer_law
dancer_law=dancer_law.replace('ffta_dark_sword_law_weapon_entry','ffta_dancer_law_entry').replace('ffta_dark_law_weapons','ffta_dancer_law_weapons')
(OUT/'dancer-law.s').write_text(dancer_law)
menu_asm=(ROOT/'src/engine/chemist-menu.s').read_text()
menu_asm=menu_asm.split('.macro original')[0]+'.align 2\n'+menu_asm[menu_asm.index('.global ffta_chemist_menu_selected_entry'):]
menu_asm=menu_asm.replace('ffta_chemist_','ffta_dancer_')
item_asm=(ROOT/'src/engine/chemist-items.s').read_text()
menu_asm+='\n'+item_asm[item_asm.index('.macro callback'):item_asm.index('callback ffta_chemist_eligibility_entry')]
menu_asm+='\n.align 2\n.global ffta_dancer_context_entry\n.thumb_func\nffta_dancer_context_entry:\n pop {r3}\n b ffta_dancer_context_aligned\ncallback ffta_dancer_context_aligned,ffta_dancer_context\n'
(OUT/'dancer-choice-menu.s').write_text(menu_asm)
labels=['Blind Dance','Silence Dance','Poison Dance','Confuse Dance']
def choice_text(text):
    encoded=[]
    for ch in text:
        if 'A'<=ch<='Z':encoded.extend((0x80,0xb0+ord(ch)-65))
        elif 'a'<=ch<='z':encoded.extend((0x80,0xca+ord(ch)-97))
        else:encoded.extend({' ':(0x40,0x73),':':(0x80,0xee)}[ch])
    return encoded+[0]
(OUT/'dancer-choice-labels.h').write_text(''.join('static const uint8_t dancer_label%d[]={%s};\n'%(i,','.join(map(str,choice_text(label)))) for i,label in enumerate(labels))+'static const uint8_t *const ffta_dancer_choice_labels[]={dancer_label0,dancer_label1,dancer_label2,dancer_label3};\n')
geo_labels=['Torrent North','Torrent East','Torrent South','Torrent West','Gaia Fire','Gaia Wind','Gaia Earth','Gaia Water','Gaia Ice']
with (OUT/'dancer-choice-labels.h').open('a') as f:
    for i,label in enumerate(geo_labels):f.write('static const uint8_t geo_label%d[]={%s};\n'%(i,','.join(map(str,choice_text(label)))))
    f.write('static const uint8_t *const ffta_geomancer_choice_labels[]={'+','.join('geo_label%d'%i for i in range(len(geo_labels)))+'};\n')
myk_labels=['Auto Life','Regen','Astra','Reflect','Invisible','Haste','Shell','Protect','Centered','Last Resort','Blackest Night','War Cry','Inoculated','Battle Chant','Inspired Magic','Magick Boost','Fury','Float','Jump','Steady','Spellblade']
with (OUT/'dancer-choice-labels.h').open('a') as f:
    for i,label in enumerate(myk_labels):f.write('static const uint8_t myk_label%d[]={%s};\n'%(i,','.join(map(str,choice_text('Break '+label)))))
    f.write('static const uint8_t *const ffta_mystic_choice_labels[]={'+','.join('myk_label%d'%i for i in range(len(myk_labels)))+'};\n')
sources=[ROOT/'src/engine'/name for name in ('integrated-jobs.c','integrated-reactions.c','integrated-restoration.c','bard.c','bard-display.c','bard-passives.c','turn-supports.c','turn-supports.s','dancer.c','dancer.s','dancer-display.c','dancer-choice.c','dancer-choice.s','ai-choice.c','ai-choice.s','geomancer-ai.c','passing-step.c','passing-step.s','geomancer.c','geomancer.s','geomancer-fields.c','geomancer-display.c','geomancer-arts.c','geomancer-selection.c','geomancer-selection.s')]+[OUT/name for name in ('combat.c','combat-hooks.s','stage.s','status.s','callbacks.s','hp-entry.s','direct-riders.c','bard-applications.c','bard-status.s','bard-entry.s','dancer-element.s','dancer-law.s','dancer-choice-menu.s')]
sources += [ROOT/'src/engine'/name for name in ('medicine-ai.c','medicine-ai.s','custom-law-prediction.c','geomancer-utility-ai.c','geomancer-utility-search.c','geomancer-map.c','battle-workspace.c','battle-workspace.s','action-snapshot.c','mystic-knight-state.c','mystic-knight-display.c','mystic-knight-visual.s','mystic-knight-laws.c','mystic-knight-laws.s','mystic-knight-prediction.c','mystic-knight-ai.c','mystic-knight-ratio.c','mystic-knight-actions.c','mystic-knight-dispel.c','mystic-knight-reactions.c','mystic-knight-shell.c','mystic-knight-doublecast.c','mystic-knight-doublecast.s','mystic-knight-fight.c','mystic-knight-fight.s')]
riders=(ROOT/'src/engine/physical-riders.s').read_text()
riders=riders.split('@ Installer contract: rawA3072')[0]+riders[riders.index('@ Native law simulation'):].split('@ C callable wrappers')[0]
for old,new in [('ffta_physical_effective_defense','ffta_myk_defense'),('ffta_physical_law_hit','ffta_myk_law_hit'),('ffta_physical_defense_entry','ffta_myk_defense_hook'),('ffta_physical_law_entry','ffta_myk_law_hook')]:riders=riders.replace(old,new)
riders=once(riders,'    mov r1,r10\n','    mov r1,r10\n    mov r2,r8\n    mov r3,r9\n')
riders+=(ROOT/'src/engine/samurai-wound.s').read_text().replace('ffta_samurai_success_entry','ffta_myk_success_hook').replace('ffta_samurai_magnitude','ffta_myk_success')
(OUT/'mystic-knight-hooks.s').write_text(riders);sources.append(OUT/'mystic-knight-hooks.s')
subprocess.run([shutil.which('node'),str(ROOT/'scripts/generate-mission-recovery.mjs'),str(OUT)],check=True,capture_output=True,text=True)
recovery=json.loads((OUT/'catalog.json').read_text(encoding='utf-8'))
sources += [ROOT/'src/engine/mission-recovery.c',ROOT/'src/engine/mission-recovery.s']
sources += [ROOT/'src/engine'/name for name in ('geomancer-renderer.c','geomancer-renderer.s','geomancer-compositor.c','geomancer-animation.c')]
# The reproducible first stage intentionally compiles historical bootstrap
# source. Install this current pose override in the final layer instead of
# silently relying on a modern edit being present in that pinned binary.
(OUT/'mystic-knight-pose.s').write_text((ROOT/'src/engine/axe-visual-hooks.s').read_text())
sources.append(OUT/'mystic-knight-pose.s')
flags=['-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror',
       '-I',str(ROOT/'src/engine'),'-I',str(ROOT/'build/expansion'),'-I',str(OUT)]
objects=[];defined=set();unresolved=set();snapshot_exports=set()
for index,source in enumerate(sources):
    named=source.name in ('dancer-choice.c','medicine-ai.c','medicine-ai.s','custom-law-prediction.c','ai-choice.c','geomancer-ai.c','geomancer-utility-ai.c','geomancer-utility-search.c','geomancer-map.c') or source.name=='action-snapshot.c' or source.name.startswith(('mystic-knight-','battle-workspace'))
    named=named or source.name.startswith(('mission-recovery','geomancer-renderer','geomancer-compositor','geomancer-animation'))
    obj=OUT/(source.stem+('-asm' if source.suffix=='.s' else '')+'.o' if named else f'part{index}.o');objects.append(obj)
    # The pure terrain hot loop has a measured CPU budget; keep other modules
    # on their existing size-oriented flags and optimize this module for speed.
    module_flags=[*flags,'-O2'] if source.name=='geomancer-compositor.c' else flags
    subprocess.run([prefix+'gcc.exe',*module_flags,'-c',str(source),'-o',str(obj)],check=True)
    for line in subprocess.check_output([prefix+'nm.exe','-g',str(obj)],text=True).splitlines():
        pieces=line.split()
        if len(pieces)==3:
            defined.add(pieces[2])
            if source.name=='action-snapshot.c' and pieces[1]=='T':snapshot_exports.add(pieces[2])
        elif len(pieces)==2 and pieces[0] in ('U','w'):unresolved.add(pieces[1])
pool=dict(base_meta['symbols'])
engine_symbols={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
pool['ffta_move_with_support']=engine_symbols['ffta_move_with_support']
pool['ffta_physical_effective_defense']=engine_symbols['ffta_physical_effective_defense']
for m in meta.values():
    for name,address in m['symbols'].items():pool.setdefault(name,address)
bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'
for name in sorted(unresolved-defined):
    if name.startswith('__aeabi_'):continue
    assert name in pool,('unresolved integration export',name)
    bindings+=f'.align 2\n.global {name}\n.thumb_func\n{name}:\n push {{r3}}\n ldr r3,={pool[name]|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(OUT/'bindings.s').write_text(bindings)
elf=OUT/'integrated.elf';binary=OUT/'integrated.bin'
GEO_RENDER=0x1360000
assert rom[GEO_RENDER:0x1380000]==bytes([255])*0x20000,"Geomancer renderer reservation occupied"
assert rom[0x1400000:0x1a00000]==bytes([255])*0x600000,"Geomancer asset reservation occupied"
asset_spec=importlib.util.spec_from_file_location("geo_asset_builder",ROOT/"scripts/generate-geomancer-assets.py")
asset_builder=importlib.util.module_from_spec(asset_spec);asset_spec.loader.exec_module(asset_builder)
geo_assets=asset_builder.generate(OUT/"geomancer-assets")
asset_blob=(OUT/"geomancer-assets/geomancer-assets.bin").read_bytes()
rom[0x1400000:0x1400000+len(asset_blob)]=asset_blob
GEO_AI=0x11ed600
MYK_CODE=0x1300000
RECOVERY_CODE=0x1340000
assert rom[RECOVERY_CODE:0x1360000]==b'\xff'*0x20000,'Mission recovery reservation occupied'
assert rom[MYK_CODE:MYK_CODE+0x30000]==b'\xff'*0x30000,'Mystic Knight code reservation occupied'
linker=OUT/'integration.ld'
linker.write_text("""SECTIONS {
 .geo_render 0x09360000 : { *geomancer-renderer*.o(.text* .rodata*) *geomancer-compositor.o(.text* .rodata*) *geomancer-animation.o(.text* .rodata*) }
 .recovery 0x09340000 : { *mission-recovery*.o(.text* .rodata*) }
 .geo_ai 0x091ed600 : { *geomancer-ai.o(.text* .rodata*) *geomancer-utility-ai.o(.text* .rodata*) *geomancer-utility-search.o(.text* .rodata*) *geomancer-map.o(.text* .rodata*) }
 .myk 0x09300000 : { *custom-law-prediction.o(.text* .rodata*) *ai-choice.o(.text* .rodata*) *medicine-ai*.o(.text* .rodata*) *dancer-choice.o(.text* .rodata*) *action-snapshot.o(.text* .rodata*) *mystic-knight-*.o(.text* .rodata*) *battle-workspace*.o(.text* .rodata*) }
 .text 0x091e0000 : { *(.text* .rodata*) }
 .unexpected : { *(.data*) *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.ARM.attributes) *(.ARM.exidx*) *(.ARM.extab*) }
 ASSERT(SIZEOF(.geo_render) <= 0x20000, "Geomancer renderer overlaps immutable assets")
 ASSERT(SIZEOF(.unexpected) == 0, "Unexpected writable section")
 ASSERT(SIZEOF(.text) < 0x8000, "Central code overlaps action table")
 ASSERT(SIZEOF(.geo_ai) <= 0x2a00, "Geomancer AI overlaps material catalog")
 ASSERT(SIZEOF(.myk) <= 0x30000, "Mystic Knight overlaps help reservation")
 ASSERT(SIZEOF(.recovery) <= 0x4000, "Mission recovery code overlaps text")
}""")
subprocess.run([prefix+'gcc.exe',*flags,'-nostdlib',f'-Wl,-T,{linker},-Map,{OUT / "integration.map"},-e,ffta_integrated_eligibility_entry',
                *map(str,objects),str(OUT/'bindings.s'),'-lgcc','-o',str(elf)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.text',str(elf),str(binary)],check=True)
render_binary=OUT/'geomancer-renderer.bin'
subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.geo_render',str(elf),str(render_binary)],check=True)
render_code=render_binary.read_bytes();rom[GEO_RENDER:GEO_RENDER+len(render_code)]=render_code
geo_binary=OUT/'geomancer-ai.bin'
subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.geo_ai',str(elf),str(geo_binary)],check=True)
geo_code=geo_binary.read_bytes();assert len(geo_code)<=0x11f0000-GEO_AI
rom[GEO_AI:GEO_AI+len(geo_code)]=geo_code
myk_binary=OUT/'mystic-knight.bin'
subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.myk',str(elf),str(myk_binary)],check=True)
myk_code=myk_binary.read_bytes();rom[MYK_CODE:MYK_CODE+len(myk_code)]=myk_code
recovery_binary=OUT/'mission-recovery.bin'
subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.recovery',str(elf),str(recovery_binary)],check=True)
recovery_code=recovery_binary.read_bytes()
rom[RECOVERY_CODE:RECOVERY_CODE+len(recovery_code)]=recovery_code
symbols={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
code=binary.read_bytes();assert len(code)<ACTIONS-CODE
rom[CODE:CODE+len(code)]=code
# Keep the original820-byte snapshot payload. Fresh results use eight824-byte
# constructor-owned slots; extra flags share the owned allocation. Passing Step
# stays in the global4KiB reservation excluded by all three native heap limits.
engine_symbols={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
for name in ('ffta_battle_heap_limit','ffta_results_heap_limit','ffta_global_heap_limit'):
    start=engine_symbols[name]-0x08000000
    hits=[i for i in range(start,start+28,4) if struct.unpack_from('<I',rom,i)[0]==0x0203f400]
    assert len(hits)==1,(name,hits)
    struct.pack_into('<I',rom,hits[0],0x0203f000)
    changes.append(dict(kind='heap limit',name=name,offset=hits[0],old=0x0203f400,new=0x0203f000))

def ptr(image,offset):return struct.unpack_from('<I',image,offset)[0]
def write_pointer(offset,address,label):
    old=ptr(rom,offset);struct.pack_into('<I',rom,offset,address)
    changes.append(dict(kind='pointer',label=label,offset=offset,previous=old,value=address))
def hook(start,end,address,label):
    assert end-start>=12 and not (start|end)&1
    original=rom[start:end].hex();jump=(start+5)&~3
    rom[start:end]=bytes.fromhex('c046')*((end-start)//2)
    struct.pack_into('<H',rom,start,0xb408)
    struct.pack_into('<HHI',rom,jump,0x4b00,0x4718,address|1)
    changes.append(dict(kind='hook',label=label,start=start,end=end,previous=original,value=address|1))
for start,end,original,name in [
 (0x1a060,0x1a06c,'f0b557464e464546e0b4214f','ffta_geo_map_reset_entry'),
 (0x1ac5e,0x1ac6a,'10b038bc9846a146aa46f0bc','ffta_geo_map_end_entry'),
 (0x1b7f8,0x1b804,'30b582b0059d069c2406240e','ffta_geo_stream_entry'),
 (0x1ac78,0x1ac84,'30b582b012480088002843d1','ffta_geo_pump_entry'),
 (0xcfd00,0xcfd0c,'e97870200840741c0194291c','ffta_recovery_posting_entry'),
 (0xd0590,0xd059c,'f0b557464e464546e0b484b0','ffta_recovery_pub_list_entry'),
 (0x5ee20,0x5ee2c,'b4f7a0fa2868044a80180e21','ffta_recovery_accept_entry'),
 (0xd0fb2,0xd0fc4,'fe200240c82a04d1154958180121f8f7d8fa','ffta_recovery_completion_entry'),
 (0xd1e9c,0xd1eac,'5046002804d0144958180121f7f764fb','ffta_recovery_dispatch_complete_entry')]:
 assert rom[start:end]==bytes.fromhex(original),(name,rom[start:end].hex())
 hook(start,end,symbols[name],name)
assert rom[0x7138:0x7140]==bytes.fromhex('00b5021c002901d1')
rom[0x7138:0x7140]=struct.pack('<HHI',0x4b00,0x4718,symbols['ffta_geo_allocate']|1)
changes.append(dict(kind='allocation pressure',offset=0x7138,label='Reclaim optional field display only after native allocation failure'))
# Names use the original512-entry pointer table. The description consumer has
# a separate16-bit-offset bank: copy its original contents before appending.
text_cursor=RECOVERY_CODE+0x4000
for row in recovery['names']:
 data=bytes.fromhex(row['bytes']);write_pointer(0x55a64c+row['mission']*4,0x08000000+text_cursor,row['title'])
 rom[text_cursor:text_cursor+len(data)]=data;text_cursor+=len(data)
text_cursor=(text_cursor+3)&~3
bank=(OUT/'mission-recovery-descriptions.bin').read_bytes()
assert text_cursor+len(bank)<=0x1360000,'Mission description reservation exceeded'
assert ptr(rom,0x13cc0)==0x084aadfc
write_pointer(0x13cc0,0x08000000+text_cursor,'Recovery descriptions; original bank entries preserved')
rom[text_cursor:text_cursor+len(bank)]=bank
recovery['descriptionBank']['installed']=text_cursor
for row in recovery['records']:
 at=0x55ae4c+row['mission']*70
 assert rom[at+2:at+70]==bytes(68),'Recovery mission slot occupied'
 rom[at:at+70]=bytes.fromhex(row['bytes'])
changes.append(dict(kind='mission and equipment recovery',first=recovery['first'],count=recovery['serviceCount'],code=[RECOVERY_CODE,RECOVERY_CODE+len(recovery_code)],text=[RECOVERY_CODE+0x4000,text_cursor+len(bank)]))
assert rom[0x97000:0x97004]==bytes.fromhex('004b1847')
assert ptr(rom,0x97004)==engine_symbols['ffta_manager_entry']|1
assert rom[0x12ff5a:0x12ff64]==bytes.fromhex('504621219cf7f7fe04e0')
# Word-aligned literal atFF60; do not overwrite the independent FF64 entry.
rom[0x12ff5a:0x12ff64]=struct.pack('<HHHI',0x4b01,0x4718,0x46c0,symbols['ffta_dancer_coefficient_entry']|1)
changes.append(dict(kind='physical coefficient',offset=0x12ff5a,end=0x12ff64,label='Last Resort primary power; native coefficient fallback'))
write_pointer(0x97004,symbols['ffta_workspace_manager_entry']|1,'Owned battle workspace constructor')
assert rom[0x96ef4:0x96efc]==bytes.fromhex('9620c0002418201c')
rom[0x96ef4:0x96efc]=struct.pack('<HHI',0x4b00,0x4718,symbols['ffta_workspace_parent_capacity']|1)
changes.append(dict(kind='battle parent capacity',offset=0x96ef4,old=0x4b0,new=0x4c0,managerBytes=0x440))
for start,end,original,name in [
 (0xa8194,0xa81a0,'f0b557464e464546e0b488b0','ffta_myk_doublecast_construct_hook'),
 (0x95d66,0x95d72,'3e2038800d2033f01cfc0006','ffta_myk_doublecast_finish_hook')]:
 assert base[start:end]==bytes.fromhex(original),(name,base[start:end].hex())
 hook(start,end,symbols[name],'Controller-owned Mystic Doublecast lifetime')
for start,end,original,name in [
 (0x12fdc4,0x12fdd0,'fff764fc0004001401b018bc','ffta_dancer_attack_entry'),
 (0x12ff64,0x12ff70,'404649460a22fff739fb6843','ffta_dancer_power_entry')]:
 assert base[start:end]==bytes.fromhex(original),(name,base[start:end].hex())
 if name=='ffta_dancer_power_entry':
  # Native special-weapon paths branch directly to12FF6E. Preserve that
  # shared MUL instead of putting a long-hook literal across its entry.
  rom[start:start+10]=struct.pack('<HHIH',0x4b00,0x4718,symbols[name]|1,0x46c0)
  changes.append(dict(kind='hook',label=name,start=start,end=start+10,previous=base[start:start+10].hex(),value=symbols[name]|1))
 else:hook(start,end,symbols[name],name)

assert base[0xbeac8:0xbead4]==bytes.fromhex('f0b557464e464546e0b48fb0')
hook(0xbeac8,0xbead4,symbols['ffta_myk_ai_self_search_entry'],'Mystic self-only AI preparation')

assert base[0xbef28:0xbef34]==bytes.fromhex('f0b557464e464546e0b490b0')
hook(0xbef28,0xbef34,symbols['ffta_geo_ai_search_entry'],'Geomancer evaluated-position choice search')

assert base[0xb5920:0xb592c]==bytes.fromhex('f0b557464e464546e0b483b0')
hook(0xb5920,0xb592c,symbols['ffta_geo_center_entry'],'Geomancer legal empty field centers')
for start,end,old,name in ((0xc2618,0xc2624,'f0b557464e464546e0b485b0','row'),
                           (0xbdecc,0xbded8,'f0b557464e464546e0b483b0','score')):
    assert base[start:end]==bytes.fromhex(old),(name,'AI entry changed')
    hook(start,end,symbols['ffta_ai_choice_'+name+'_entry'],'Scoped Forbidden Dance AI '+name)

assert base[0xc2940:0xc294c]==bytes.fromhex('f0b557464e464546e0b497b0')
hook(0xc2940,0xc294c,symbols['ffta_myk_ai_rank_entry'],'Mystic tactical rows after native sorting')
assert base[0xc35d6:0xc35e2]==bytes.fromhex('40460af090f9051c2d062d0e')
hook(0xc35d6,0xc35e2,symbols['ffta_martial_ai_filter_entry'],'Custom ward benefit after native AI willingness')
assert base[0xc3608:0xc3614]==bytes.fromhex('308801385b2801d901f0b3f8')
hook(0xc3608,0xc3614,symbols['ffta_provoke_ai_filter_entry'],'Provoke AI after native effect compatibility')

def native_hook(job,start,end,name):hook(start,end,meta[job]['symbols'][name],name)
native_hook('chemist',0x7d96c,0x7d978,'ffta_potion_roster_entry')
native_hook('chemist',0x7e004,0x7e014,'ffta_potion_confirm_entry')

# Exactly one native entry owner. Original instructions come from the common
# base, not an earlier job patch, so an unexpected upstream change is visible.
hook(0xa2210,0xa221c,symbols['ffta_integrated_native_hp_apply_entry'],'direct HP writer provenance')
for start,end,name in [(0x1300e2,0x1300f2,'physical_final'),(0x130654,0x130660,'weapon_drain'),
                       (0x130688,0x130694,'weapon_effect'),(0x131b4a,0x131b56,'exposed_stage'),
                       (0x130200,0x13020c,'exposed_preview'),(0x9dd52,0x9dd62,'status_next'),(0x97ad0,0x97ae4,'status_visual')]:
    target={'weapon_drain':'ffta_myk_fight_drain_hook','weapon_effect':'ffta_myk_fight_effect_hook',
            'exposed_preview':'ffta_myk_fight_preview_hook'}.get(name,'ffta_integrated_'+name+'_entry')
    hook(start,end,symbols[target],name)
write_pointer(0x9da10,symbols['ffta_integrated_status_icon_entry']|1,'status icon')
assert rom[0x9709a:0x9709c]==bytes.fromhex('5b00')
rom[0x97098:0x9709c]=bytes.fromhex('88239b00') # MOV r3,136; LSL r3,2: pool starts at220 after Mystic icons.
for job,entries in {
    'viking':[(0x133a58,0x133a64,'compatibility'),(0x131220,0x13122c,'status_accuracy')],
    'dark-knight':[(0x12f8a4,0x12f8b0,'element'),(0x133e18,0x133e24,'usable'),
                   (0x12ed98,0x12eda8,'mp_cost'),(0x13467a,0x134686,'law_weapon')],
    'chemist':[(0xa2eb8,0xa2ec4,'native_item_debit'),(0x131dd4,0x131de0,'status'),
               (0x26d44,0x26d50,'menu'),(0x26f9c,0x26fa8,'restricted_menu'),
               (0x25758,0x25764,'menu_name'),(0x28a8c,0x28a98,'menu_selected'),
               (0xa45c6,0xa45d4,'paid'),(0xa0014,0xa0020,'geometry'),
               (0x12f230,0x12f23c,'context'),(0xa013a,0xa014a,'range'),(0xa2edc,0xa2eea,'consumption')]
}.items():
    prefix_name={'dark-knight':'drk','viking':'viking','chemist':'chemist'}[job]
    for start,end,name in entries:native_hook(job,start,end,f'ffta_{prefix_name}_{name}_entry')
hook(0x12ed98,0x12eda8,symbols['ffta_bard_mp_cost_hook'],'Clear Voice MP cost')
hook(0x133a58,0x133a64,symbols['ffta_bard_compatibility_hook'],'Clear Voice compatibility')
hook(0x131dd4,0x131de0,symbols['ffta_bard_status_entry'],'Clear Voice and Chemist component gate')
assert base[0xc9574:0xc9580]==bytes.fromhex('00b500040904c30c094a9b18')
hook(0xc9574,0xc9580,symbols['ffta_turn_flag_entry'],'voluntary movement completion and cancellation')
for start,end,expected,name in [
    (0xca2e8,0xca2f4,'f0b5051c2221fef7ffff0006','ffta_geo_mobility_entry'),
    (0x97814,0x97820,'f0b557464e464546e0b48eb0','ffta_geo_tile_entry')]:
    assert base[start:end]==bytes.fromhex(expected),name
    hook(start,end,symbols[name],name)
assert base[0xca394:0xca3a0]==struct.pack('<HHHHI',0xb408,0x46c0,0x4b00,0x4718,engine_symbols['ffta_move_support_entry']|1)
hook(0xca394,0xca3a0,symbols['ffta_geo_move_entry'],'Updraft with original Light Foot movement')
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
for start,end,name in [(0x25720,0x2572c,'begin'),(0xb6544,0xb6550,'poll'),(0x93c5e,0x93c6a,'after'),(0x93994,0x939a0,'ai')]:
    assert rom[start:end]==clean[start:end],('Passing Step hook conflict',hex(start))
    hook(start,end,symbols['ffta_passing_'+name+'_entry'],'Passing Step '+name)
hook(0xa4adc,0xa4ae8,base_meta['symbols']['ffta_reaction_queue_entry'],'native reaction queue')
for offset,name in [(0x3a8604+8*4,'eligibility'),(0x3a86f8+30*4,'physical_magnitude')]:
    write_pointer(offset,symbols['ffta_integrated_'+name+'_entry']|1,name)
for job,offset,name in [
                       ('dark-knight',0x3a86f8+25*4,'ffta_drk_healing_entry'),
                       ('chemist',0x3a86f8+35*4,'ffta_chemist_hp_entry'),('chemist',0x3a86f8+34*4,'ffta_chemist_mp_entry'),
                       ('viking',0x3a8604+15*4,'ffta_viking_theft_eligibility_entry'),
                       ('viking',0x3a8678+14*4,'ffta_viking_theft_accuracy_entry'),
                       ('viking',0x3a86f8+7*4,'ffta_viking_theft_accessory_entry'),
                       ('viking',0x3a86f8+15*4,'ffta_viking_theft_armor_entry')]:
    write_pointer(offset,meta[job]['symbols'][name]|1,name)

hook(0x12f8a4,0x12f8b0,symbols['ffta_myk_fight_element_hook'],'Enchanted primary Fight and existing element policies')
assert base[0xa2dcc:0xa2dd8]==bytes.fromhex('cf9a5019006800688ef040ff')
hook(0xa2dcc,0xa2dd8,symbols['ffta_myk_fight_status_hook'],'Primary Fight status after native wake cleanup')
hook(0x13467a,0x134686,symbols['ffta_dancer_law_entry'],'Dancer native weapon law policy')
assert rom[0x134410:0x13441c]==bytes.fromhex('169908790138132800d9e2e2')
hook(0x134410,0x13441c,symbols['ffta_myk_fight_law_hook'],'Enchanted Fight native elemental/status law selector')
hook(0x131220,0x13122c,symbols['ffta_dancer_status_accuracy_hook'],'Counter Rhythm S accuracy')
hook(0x133e18,0x133e24,symbols['ffta_myk_usable_hook'],'Mystic weapon Silence and resource admission')
write_pointer(0x3a8678+10*4,symbols['ffta_myk_accuracy_entry']|1,'Mystic self enchant Sure and original A accuracy')
for offset,name in [(0x12feac,'ffta_myk_defense_hook'),(0x134350,'ffta_myk_law_hook'),(0xa3078,'ffta_myk_success_hook')]:
    # Replace only an established native veneer literal; preserve its ABI.
    assert (rom[offset-4:offset]==bytes.fromhex('00480047') if offset!=0xa3078 else rom[offset-4:offset]==bytes.fromhex('004b1847')),(name,rom[offset-4:offset].hex())
    write_pointer(offset,symbols[name]|1,name)
# 27DA0 copies descriptor3, allocates count*4 rows and count flags through
# native5B28, and uses those same owned pointers for native cleanup. The
# command constructors later set actual length; increase capacity only.
menu_capacity=0x391454+3*20+4
assert struct.unpack_from('<H',base,menu_capacity)[0]==22
struct.pack_into('<H',rom,menu_capacity,42)
changes.append(dict(kind='command menu capacity',offset=menu_capacity,previous=22,value=42))
for start,end,name in [(0x26d44,0x26d50,'menu'),(0x26f9c,0x26fa8,'restricted_menu'),(0x25758,0x25764,'menu_name'),(0x28a8c,0x28a98,'menu_selected'),(0x12f230,0x12f23c,'context')]:
    hook(start,end,symbols['ffta_dancer_'+name+'_entry'],'Dancer choice with Chemist delegation')
assert base[0xa447a:0xa4486]==bytes.fromhex('201c1b2128f067fc002803d1')
hook(0xa447a,0xa4486,symbols['ffta_dancer_choice_transport_entry'],'Forbidden Dance explicit extra without item semantics')
# Spellbreak's explicit buff operand is never a presentation weapon ID.
assert ptr(rom,0x986e0)==engine_symbols['ffta_axe_actor_visual']|1
write_pointer(0x986e0,symbols['ffta_axe_actor_visual']|1,'Current racial weapon pose aliases')
for start,end,name in [(0xa6238,0xa624c,'category'),(0xa6412,0xa6420,'direction'),
                       (0xa6424,0xa6434,'projectile'),(0xa662c,0xa6638,'actor'),
                       (0xa5730,0xa573c,'impact'),(0xa588c,0xa58a0,'sound'),(0xddfce,0xddfe0,'magic_actor')]:
    assert rom[start:end]==clean[start:end],('Mystic visual hook conflict',hex(start))
    hook(start,end,symbols['ffta_myk_visual_'+name],'Spellbreak presentation '+name)

assert rom[0xc48a4:0xc48b0]==bytes.fromhex('f0b5474680b481b0051c0f1c')
hook(0xc48a4,0xc48b0,symbols['ffta_medicine_recipient_entry'],'Field Remedy exact stocked cure admission')
assert base[0xb4cf0:0xb4cfc]==bytes.fromhex('201c311c00227af0d5fa184c')
hook(0xb4cf0,0xb4cfc,symbols['ffta_dancer_preview_choice_entry'],'Forbidden Dance exact player target choice')
assert base[0x94342:0x94350]==bytes.fromhex('199c20881b2138f002fd002804d1')
hook(0x94342,0x94350,symbols['ffta_dancer_player_choice_entry'],'Forbidden Dance native player operand publication')
assert base[0x12dbca:0x12dbd6]==bytes.fromhex('04a80188381c002201f067fb')
hook(0x12dbca,0x12dbd6,symbols['ffta_dancer_chance_choice_entry'],'Forbidden Dance player chance forecast')
assert base[0x13025c:0x130268]==bytes.fromhex('101c391c0022fff71ff82660')
hook(0x13025c,0x130268,symbols['ffta_dancer_magnitude_choice_entry'],'Forbidden Dance player magnitude forecast')

write_pointer(0x3a86f8,symbols['ffta_integrated_zero_magnitude_entry']|1,'combined fixed reaction magnitude')
write_pointer(0x3a86f8+25*4,symbols['ffta_integrated_technique_healing_entry']|1,'combined technique healing')
write_pointer(0x3a86f8+35*4,symbols['ffta_integrated_item_healing_entry']|1,'combined medicine healing')
write_pointer(0x3a86f8+34*4,symbols['ffta_integrated_mp_restoration_entry']|1,'combined MP restoration')
# Owned action rows are combined explicitly; never interpret a nonzero row in
# another job's reserved range as that job's implementation.
old_actions=ptr(base,0xccd84)-0x08000000
actions=bytearray(base[old_actions:old_actions+432*28])+bytearray(14*28)
owners={'dark-knight':[356,359,360,361,362,363,364,433,434],
        'viking':list(range(365,374))+[436,437],'chemist':list(range(383,393))+[432]}
for job,ids in owners.items():
    table=ptr(images[job],0xccd84)-0x08000000
    for action in ids:
        assert not any(actions[action*28:(action+1)*28]),('duplicate action',action)
        row=images[job][table+action*28:table+(action+1)*28];assert len(row)==28 and any(row)
        actions[action*28:(action+1)*28]=row
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
lesson=next(x for x in registry['lessons'] if x['id']=='SAM-R2')
row=bytearray(actions[347*28:348*28]);struct.pack_into('<H',row,0,lesson['nameId'])
row[2]=0;row[4]=0;row[6]=1;row[7]=2;row[12:16]=bytes((63,1,1,1));struct.pack_into('<H',row,22,0)
assert not any(actions[435*28:436*28]);actions[435*28:436*28]=row
# All eight songs share the native action consumers. Custom descriptors own
# eligibility/magnitude only where the approved rule differs from its donor.
for ident,donor,cost,radius,area,vector in [
    ('BRD-A1',1,8,4,False,[224,1,1,1]),
    ('BRD-A2',12,12,3,True,[78,225,1,1]),
    ('BRD-A3',12,12,3,True,[45,226,1,1]),
    ('BRD-A4',11,8,3,True,[63,1,1,1]),
    ('BRD-A5',1,12,3,True,[223,227,1,1]),
    ('BRD-A6',12,0,0,False,[123,1,1,1]),
    ('BRD-A7',254,0,4,False,[36,1,1,1]),
    ('BRD-A8',12,24,3,True,[78,45,227,1])]:
    lesson=next(x for x in registry['lessons'] if x['id']==ident);action=lesson['globalAbilityId']
    row=bytearray(base[0x55187c+donor*28:0x55187c+(donor+1)*28])
    struct.pack_into('<H',row,0,lesson['nameId']);struct.pack_into('<H',row,22,0)
    row[2]=7 if ident=='BRD-A4' else 0;row[4]=cost;row[5]=0;row[6]=radius;row[7]=2
    # Selector1 centers on the chosen tile; selector3 forces the caster.
    # Cross shape belongs to byte9 independently of the center selector.
    row[8]=3 if ident=='BRD-A6' else 1;row[9]=5 if area else 1;row[10]=2 if area else 0
    row[11]=60 if ident=='BRD-A4' else 0;row[12:16]=bytes(vector)
    # Native133E18 rejects byte25==0 for AI admission (flag128). Ether's
    # donor forbids AI item use; Ballad is a free song, not a consumable.
    if ident=='BRD-A7':row[25]=1
    flags=struct.unpack_from('<I',row,16)[0]&~((1<<7)|(1<<8)|(1<<9)|(1<<15)|(1<<17))
    flags|=(1<<9) if ident=='BRD-A6' else (1<<17)
    struct.pack_into('<I',row,16,flags)
    assert not any(actions[action*28:(action+1)*28]),ident
    actions[action*28:(action+1)*28]=row
    changes.append(dict(kind='Bard action',lesson=ident,action=action,donor=donor,record=row.hex()))
for ident,action,descriptor,donor in [('BRD-S1',438,228,1),('BRD-R1',439,229,12),('BRD-R2',440,230,42)]:
    lesson=next(x for x in registry['lessons'] if x['id']==ident)
    row=bytearray(base[0x55187c+donor*28:0x55187c+(donor+1)*28])
    struct.pack_into('<H',row,0,lesson['nameId']);struct.pack_into('<H',row,22,0)
    row[2]=0;row[4]=0;row[5]=0;row[6]=0;row[7]=2;row[8]=3;row[9]=1;row[10]=0;row[11]=0
    row[12:16]=bytes((descriptor,1,1,1));struct.pack_into('<I',row,16,0x0012f121&~((1<<7)|(1<<8)|(1<<15)))
    assert not any(actions[action*28:(action+1)*28]);actions[action*28:(action+1)*28]=row
# A6 uses a native status template for target/menu classification. Its
# constructor still makes an absent/invalid explicit choice inert.
# A9 owns a preselected route and defers native movement until paid completion.
for ident,donor,cost,radius,area,vector in [
 ('DNC-A1',180,6,3,True,[63,1,1,1]),('DNC-A2',254,8,3,True,[232,1,1,1]),
 ('DNC-A3',35,12,3,True,None),('DNC-A4',180,12,3,False,[63,1,1,1]),
 ('DNC-A5',180,12,3,False,[63,1,1,1]),('DNC-A6',35,14,3,True,[87,1,1,1]),('DNC-A7',180,10,2,False,[63,1,1,1]),
 ('DNC-A8',180,16,1,False,[63,1,1,1]),('DNC-A9',180,6,1,False,[63,1,1,1]),('DNC-R1',12,0,0,False,[231,1,1,1]),
 ('DNC-R2',35,0,3,False,None)]:
 lesson=next(x for x in registry['lessons'] if x['id']==ident)
 action=441 if ident=='DNC-R1' else 442 if ident=='DNC-R2' else lesson['globalAbilityId']
 row=bytearray(base[0x55187c+donor*28:0x55187c+(donor+1)*28])
 struct.pack_into('<H',row,0,lesson['nameId']);struct.pack_into('<H',row,22,0)
 row[2]=0;row[4]=cost;row[5]=1 if ident in ('DNC-A1','DNC-A4','DNC-A5','DNC-A7','DNC-A8','DNC-A9') else 0
 row[6]=radius;row[7]=2;row[8]=3 if ident=='DNC-R1' else 1;row[9]=5 if area else 1;row[10]=2 if area else 0
 if vector:row[12:16]=bytes(vector)
 # Witch Hunt also inherits Ether's MP descriptor without its AI-item ban.
 if ident=='DNC-A2':row[25]=1
 flags=struct.unpack_from('<I',row,16)[0]&~((1<<7)|(1<<8)|(1<<9)|(1<<15)|(1<<17))
 # Field20 (bit9) means usable while Silenced, not silence-dependent.
 # All dances, including the two reaction carriers, are non-incanted.
 flags|=1<<9
 struct.pack_into('<I',row,16,flags)
 assert not any(actions[action*28:(action+1)*28]);actions[action*28:(action+1)*28]=row
 changes.append(dict(kind='Dancer action',lesson=ident,action=action,donor=donor,record=row.hex()))
for ident,action,donor,element,power,vector in [
    ('GEO-R1',443,12,0,0,[78,1,1,1]),('GEO-R2',444,23,2,24,[63,1,1,1])]:
    lesson=next(x for x in registry['lessons'] if x['id']==ident)
    row=bytearray(base[0x55187c+donor*28:0x55187c+(donor+1)*28])
    struct.pack_into('<H',row,0,lesson['nameId']);struct.pack_into('<H',row,22,0)
    row[2]=element;row[4]=0;row[5]=0;row[6]=4 if action==444 else 0;row[7]=2
    row[8]=1 if action==444 else 3;row[9]=1;row[10]=0;row[11]=power;row[12:16]=bytes(vector)
    flags=struct.unpack_from('<I',row,16)[0]&~((1<<7)|(1<<8)|(1<<9)|(1<<15)|(1<<17))
    struct.pack_into('<I',row,16,flags)
    assert not any(actions[action*28:(action+1)*28]);actions[action*28:(action+1)*28]=row
    changes.append(dict(kind='Geomancer reaction',lesson=ident,action=action,donor=donor,record=row.hex()))
assert ACTIONS+len(actions)<=DESCRIPTORS
for ident,donor,cost,power,element,vector in [
    ('GEO-A1',23,4,26,3,[63,1,1,1]),
    ('GEO-A2',23,6,24,0,[63,71,1,1]),
    ('GEO-A3',23,8,28,4,[63,235,1,1]),
    ('GEO-A4',12,8,0,0,[233,1,1,1]),
    ('GEO-A5',12,10,0,0,[234,1,1,1]),
    ('GEO-A6',23,10,28,1,[63,1,1,1]),
    ('GEO-A7',29,12,28,5,[63,102,1,1]),
    ('GEO-A8',23,18,40,2,[63,1,1,1]),
    ('GEO-A9',12,12,0,0,[236,1,1,1])]:
    lesson=next(x for x in registry['lessons'] if x['id']==ident);action=lesson['globalAbilityId']
    row=bytearray(base[0x55187c+donor*28:0x55187c+(donor+1)*28])
    struct.pack_into('<H',row,0,lesson['nameId']);struct.pack_into('<H',row,22,0)
    row[2]=element;row[4]=cost;row[5]=0;row[6]=4 if ident=='GEO-A8' else 3;row[7]=2;row[8]=1;row[9]=1 if ident in ('GEO-A2','GEO-A6') else 5;row[10]=0 if row[9]==1 else 2;row[11]=power;row[12:16]=bytes(vector)
    flags=struct.unpack_from('<I',row,16)[0]&~((1<<7)|(1<<8)|(1<<9)|(1<<15)|(1<<17))
    struct.pack_into('<I',row,16,flags)
    assert not any(actions[action*28:(action+1)*28]);actions[action*28:(action+1)*28]=row
    # Native field28 classifies direct magic for the shared damage consumers.
    # It is independent of Silence/Reflect/Doublecast flags and sequencing.
    flags|=1<<17;struct.pack_into('<I',row,16,flags)
    actions[action*28:(action+1)*28]=row
    changes.append(dict(kind='Geomancer action',lesson=ident,action=action,donor=donor,record=row.hex()))
myk_costs=[6,6,6,6,10,8,12,20,12,8,12,10,14,24]
myk_status={413:125,414:97,415:111,418:104}
for n,cost in enumerate(myk_costs,1):
    ident=f'MYK-A{n}';lesson=next(x for x in registry['lessons'] if x['id']==ident);action=lesson['globalAbilityId']
    donor=23 if n==13 else 180
    row=bytearray(base[0x55187c+donor*28:0x55187c+(donor+1)*28])
    struct.pack_into('<H',row,0,lesson['nameId']);struct.pack_into('<H',row,22,0)
    row[2]={1:1,2:5,3:6,11:7}.get(n,0);row[4]=cost;row[5]=int(n<=12);row[6]=3 if n==13 else 1;row[7]=2;row[8]=1
    row[9]=5 if n==13 else 1;row[10]=2 if n==13 else 0;row[11]=40 if n==13 else 0
    row[12:16]=bytes((98,1,1,1) if n==14 else (63,myk_status.get(action,1),1,1))
    flags=struct.unpack_from('<I',row,16)[0]&~((1<<7)|(1<<8)|(1<<9)|(1<<15)|(1<<17))
    if n==13:flags|=1<<17
    struct.pack_into('<I',row,16,flags)
    assert not any(actions[action*28:(action+1)*28]),ident
    actions[action*28:(action+1)*28]=row
    changes.append(dict(kind='Mystic Knight command',lesson=ident,action=action,record=row.hex()))
row=bytearray(actions[422*28:423*28]);row[11]=44
actions[445*28:446*28]=row
changes.append(dict(kind='internal native M44 formula',action=445,record=row.hex()))
# Learned Medicine is available to AI only through the integrated exact-owner
# and whole-recipe stock gate. Native Item donors disable six otherwise valid
# commands; hidden reaction carriers retain their separate discovery policy.
for action in range(383,393):actions[action*28+25]=1
rom[ACTIONS:ACTIONS+len(actions)]=actions
descriptors=bytearray(base[0x553e70:0x553e70+209*4])+bytearray(28*4)
for job,ids in {'dark-knight':[213,214,216,217,219],'viking':[211,212,218,221,222],'chemist':[209,210,215,220]}.items():
    source=ptr(images[job],0x12f2a0)-0x08000000
    for index in ids:descriptors[index*4:(index+1)*4]=images[job][source+index*4:source+(index+1)*4]
for index,values in {223:[8,38,23,25],224:[8,104,23,25],225:[8,102,23,0],226:[8,103,23,0],227:[8,31,23,0],228:[8,105,23,0],229:[8,106,23,0],230:[8,107,23,0],231:[8,108,23,0],232:[8,8,10,34],233:[8,109,23,0],234:[8,110,23,0],235:[8,111,23,0],236:[8,96,23,0]}.items():
    descriptors[index*4:(index+1)*4]=bytes(values)
assert DESCRIPTORS+len(descriptors)<=APPLICATIONS
rom[DESCRIPTORS:DESCRIPTORS+len(descriptors)]=descriptors
apps=bytearray(base[0x3a87b0:0x3a87b0+93*12])+bytearray(19*12)
masks=bytearray(base[0x52790c:0x52790c+93*12])+bytearray(19*12)
for job,ids in {'dark-knight':[97,98],'viking':[93,94,99,100,101],'chemist':[95,96]}.items():
    app_source=ptr(images[job],0x1323b8)-0x08000000
    mask_source=ptr(images[job],0x1339c8)-0x08000000
    for index in ids:
        apps[index*12:(index+1)*12]=images[job][app_source+index*12:app_source+(index+1)*12]
        masks[index*12:(index+1)*12]=images[job][mask_source+index*12:mask_source+(index+1)*12]
struct.pack_into('<I',apps,59*12,meta['viking']['symbols']['ffta_viking_theft_apply_entry']|1)
struct.pack_into('<I',apps,94*12,symbols['ffta_integrated_challenged_apply_entry']|1)
for kind in (102,103):
    struct.pack_into('<III',apps,kind*12,symbols['ffta_bard_buff_apply_entry']|1,0,255)
    masks[kind*12:(kind+1)*12]=bytes([0x55]*11+[0])
apps[104*12:105*12]=apps[38*12:39*12]
mask=bytearray([0x55]*11+[0])
for status in (9,10,27,28):mask[(2*status+1)//8]|=1<<((2*status+1)%8)
masks[104*12:105*12]=mask
apps[105*12:106*12]=apps[38*12:39*12]
for kind in (106,107):struct.pack_into('<III',apps,12*kind,symbols['ffta_bard_reaction_apply_entry']|1,0,255)
struct.pack_into('<III',apps,108*12,symbols['ffta_dancer_fury_apply_entry']|1,0,255)
struct.pack_into('<III',apps,109*12,symbols['ffta_bard_application_entry']|1,0,255)
struct.pack_into('<III',apps,110*12,symbols['ffta_bard_application_entry']|1,0,255)
struct.pack_into('<III',apps,111*12,symbols['ffta_geo_torrent_apply_entry']|1,0,1)
for kind in (105,106,107,108,109,110,111):masks[kind*12:(kind+1)*12]=bytes([0x55]*11+[0])
for kind in observed_apps:struct.pack_into('<I',apps,12*kind,symbols['ffta_bard_application_entry']|1)
assert APPLICATIONS+len(apps)<=MASKS
assert MASKS+len(masks)<=GEO_AI
rom[APPLICATIONS:APPLICATIONS+len(apps)]=apps;rom[MASKS:MASKS+len(masks)]=masks

# Redirect table literals, including exact interior descriptor references in
# private native-rider prediction helpers. Native sites require reviewed load
# provenance; expansion sites require ELF data provenance. Raw graphics words
# can coincide with these addresses and must never be relocated.
native_clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
authenticate(native_clean)
samurai_work=pathlib.Path(samurai['path']).parent.parent
base_regions=[(0x1100000,len((ROOT/'build/expansion/engine.bin').read_bytes())),
              (0x11c0000,len((samurai_work/'samurai.bin').read_bytes())),
              (0x11d0000,len((P/'job-state'/base_meta['baseSha1']/'state.bin').read_bytes()))]
job_regions={job:(start,(pathlib.Path(m['path']).parent.parent/('dark-knight.bin' if job=='dark-knight' else 'chemist.bin')).stat().st_size)
             for job,m in meta.items() if job!='viking' for start,end in [RANGES[job]]}
job_regions['viking']=(RANGES['viking'][0],(P/'viking-code/viking.bin').stat().st_size)
table_maps=[(old_actions,432*28,ACTIONS),(0x553e70,209*4,DESCRIPTORS),
            (0x3a87b0,93*12,APPLICATIONS),(0x52790c,93*12,MASKS)]
for job in meta:
    for native,extent,new in [(0xccd84,438*28,ACTIONS),(0x12f2a0,223*4,DESCRIPTORS),
                              (0x1323b8,102*12,APPLICATIONS),(0x1339c8,102*12,MASKS)]:
        old=ptr(images[job],native)-0x08000000
        if not any(x[0]==old for x in table_maps):table_maps.append((old,extent,new))
classified={
    0x1100000:ELFData(ROOT/'build/expansion/engine.elf',prefix),
    0x11c0000:ELFData(samurai_work/'samurai.elf',prefix),
    0x11d0000:ELFData(P/'job-state'/base_meta['baseSha1']/'state.elf',prefix),
    CODE:ELFData(elf,prefix),GEO_AI:ELFData(elf,prefix),MYK_CODE:ELFData(elf,prefix),RECOVERY_CODE:ELFData(elf,prefix),
}
for job,(start,length) in job_regions.items():
    job_elf=(P/'viking-code/viking.elf' if job=='viking' else
        pathlib.Path(meta[job]['path']).parent.parent/(job+'.elf'))
    classified[start]=ELFData(job_elf,prefix)
for start,length in [(0,0x1000000),*base_regions,*job_regions.values(),(CODE,len(code)),(GEO_AI,len(geo_code)),(MYK_CODE,len(myk_code)),(RECOVERY_CODE,len(recovery_code))]:
    for offset in range(start,start+length-3,4):
        value=ptr(rom,offset)
        for old,size,new in table_maps:
            if 0x08000000+old<=value<0x08000000+old+size:
                if start==0 and not native_literal_allowed(native_clean,rom,offset):
                    changes.append(dict(kind='preserved native data collision',offset=offset,value=value))
                    break
                if start in classified and not classified[start].contains_word(0x08000000+offset):
                    changes.append(dict(kind='preserved instruction collision',offset=offset,value=value))
                    break
                struct.pack_into('<I',rom,offset,value-old+new)
                changes.append(dict(kind='table literal relocation',offset=offset,old=value,value=value-old+new))
                break

def rebind(regions,address,replacement,label,required=True):
    sites=[];address&=~1;replacement&=~1
    for start,length in regions:
        for offset in range(start,start+length-2,2):
            if classified[start].contains_word(0x08000000+offset):continue
            a,b=struct.unpack_from('<HH',rom,offset)
            if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
            delta=((a&0x7ff)<<12)|((b&0x7ff)<<1)
            if delta&0x400000:delta-=0x800000
            if 0x08000000+offset+4+delta!=address:continue
            delta=replacement-(0x08000000+offset+4);assert -0x400000<=delta<0x400000
            struct.pack_into('<HH',rom,offset,0xf000|((delta>>12)&0x7ff),0xf800|((delta>>1)&0x7ff));sites.append(offset)
        for offset in range(start,start+length-3,4):
            if ptr(rom,offset)==address|1 and classified[start].contains_word(0x08000000+offset):
                struct.pack_into('<I',rom,offset,replacement|1);sites.append(offset)
    assert sites or not required,('missing explicit consumer',label)
    changes.append(dict(kind='rebind',label=label,old=address,new=replacement,sites=sites))

# One lifecycle chain, so Centered/Wound are called once, followed by each job.
for kind,old in [('event','ffta_centered_event'),('turn_end','ffta_centered_turn_end')]:
    rebind(base_regions,base_meta['symbols'][old],meta['dark-knight']['symbols']['ffta_drk_lifecycle_'+kind],old)
    rebind([job_regions['dark-knight']],base_meta['symbols'][old],meta['viking']['symbols']['ffta_viking_lifecycle_'+kind],'DRK lifecycle delegation')
    rebind([job_regions['viking']],base_meta['symbols'][old],meta['chemist']['symbols']['ffta_chemist_combined_'+kind],'Viking lifecycle delegation')
    rebind([job_regions['chemist']],base_meta['symbols'][old],symbols['ffta_bard_lifecycle_'+kind],'Chemist lifecycle delegation')
all_old_regions=base_regions+list(job_regions.values())
rebind(all_old_regions,base_meta['symbols']['ffta_copy_owners_reset'],symbols['ffta_geo_reset_owners'],'retire field renderer before scene heap reset')
for name in sorted(snapshot_exports & base_meta['symbols'].keys()):
    rebind(all_old_regions,base_meta['symbols'][name],symbols[name],'extended snapshot '+name,required=False)
rebind(base_regions,base_meta['symbols']['ffta_dark_sword_apply'],symbols['ffta_integrated_dark_sword_apply'],'explicit direct descriptor HP rider')
for old,new in [('ffta_physical_eligibility','ffta_integrated_physical_eligibility'),
                ('ffta_physical_magnitude','ffta_integrated_physical_magnitude'),
                ('ffta_physical_final','ffta_integrated_physical_final')]:
    rebind(all_old_regions,base_meta['symbols'][old],symbols[new],old)
    rebind([job_regions['dark-knight']],meta['dark-knight']['symbols'][old],symbols[new],'DRK '+old)
rebind([job_regions['chemist']],base_meta['symbols']['ffta_custom_physical_paid'],meta['dark-knight']['symbols']['ffta_drk_paid'],'compound payment delegation')
rebind([job_regions['chemist']],base_meta['symbols']['ffta_combat_geometry'],meta['dark-knight']['symbols']['ffta_combat_geometry'],'geometry delegation')
rebind([job_regions['dark-knight']],meta['dark-knight']['symbols']['ffta_drk_direct_kind'],symbols['ffta_integrated_direct_kind'],'all-job direct classification')
rebind(base_regions,base_meta['symbols']['ffta_higanbana_commit'],symbols['ffta_integrated_higanbana_commit'],'broad-remedy Higanbana prevention')
for old,new in [('ffta_chemist_payment_gate','ffta_myk_payment_gate'),('ffta_chemist_geometry','ffta_myk_geometry')]:
    rebind([job_regions['chemist']],meta['chemist']['symbols'][old],symbols[new],new)
for suffix in ('snapshot_flags','extra_snapshot_flags','snapshot_storage','result_storage','action_limit','beneficial','action_category','action_event','hp_loss','reaction_queue','reaction_wrapper'):
    offset=base_meta['symbols']['ffta_additional_'+suffix]-0x08000000
    assert base[offset:offset+16]==bytes.fromhex('00207047')+bytes(12),suffix
    struct.pack_into('<HHI',rom,offset,0x4b00,0x4718,symbols['ffta_integrated_'+suffix]|1)

# Reassign help IDs serially from the shared bank. Both jobs originally used
# the same next ID in isolation; copying either private help pointer loses the
# other's descriptions. These source builders update their own lesson rows.
for job in ('viking','dark-knight'):
    # These are exclusively each job's declared help allocation, outside its
    # code and native banks. Rebuild descriptions with fresh, noncolliding IDs.
    help_start=0x1230000 if job=='dark-knight' else 0x1270000
    rom[help_start:help_start+0x10000]=b'\xff'*0x10000
    source=OUT/f'{job}-help-input.gba';target=OUT/f'{job}-help-output.gba'
    source.write_bytes(rom)
    subprocess.run([shutil.which('node'),str(ROOT/f'scripts/jobs/{job}/patch-help.mjs'),str(source),str(target),str(OUT/f'{job}-help.json')],check=True)
    rom=bytearray(target.read_bytes())
source=OUT/'bard-help-input.gba';target=OUT/'bard-help-output.gba';source.write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/patch-bard-help.mjs'),str(source),str(target),str(OUT/'bard-help.json')],check=True)
rom=bytearray(target.read_bytes())
source=OUT/'turn-help-input.gba';target=OUT/'turn-help-output.gba';source.write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/patch-turn-help.mjs'),str(source),str(target),str(OUT/'turn-help.json')],check=True)
rom=bytearray(target.read_bytes())
source=OUT/'dancer-help-input.gba';target=OUT/'dancer-help-output.gba';source.write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/patch-dancer-help.mjs'),str(source),str(target),str(OUT/'dancer-help.json')],check=True)
rom=bytearray(target.read_bytes())
source=OUT/'geomancer-help-input.gba';target=OUT/'geomancer-help-output.gba';source.write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/patch-geomancer-help.mjs'),str(source),str(target),str(OUT/'geomancer-help.json')],check=True)
rom=bytearray(target.read_bytes())
source=OUT/'mystic-knight-help-input.gba';target=OUT/'mystic-knight-help-output.gba';source.write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/patch-mystic-knight-help.mjs'),str(source),str(target),str(OUT/'mystic-knight-help.json')],check=True)
rom=bytearray(target.read_bytes())
source=OUT/'completion-help-input.gba';target=OUT/'completion-help-output.gba';source.write_bytes(rom)
subprocess.run([shutil.which('node'),str(ROOT/'scripts/patch-completion-help.mjs'),str(source),str(target),str(OUT/'completion-help.json')],check=True)
rom=bytearray(target.read_bytes())
for native in (0x23320,0x236ac,0x25998,0x26c9c,0x26d3c,0x26e18,0x27048,0x27170,0x279a0,0x27a94,0xa784c,0xb5d18,0xc3080,0xc3474,0xccd84,0x133e70,0x13416c):
    assert ptr(rom,native)==0x08000000+ACTIONS,hex(native)
from equipment_preview import apply as apply_equipment_preview
equipment_preview=apply_equipment_preview(rom,OUT/'equipment-preview')
changes.append(dict(kind='Paged native equipment preview',**equipment_preview))
ART=OUT/sha(rom);ART.mkdir(exist_ok=True)
(ART/'integrated.gba').write_bytes(rom);(ART/'input.gba').write_bytes(base)
report=dict(status='PRIVATE UNACCEPTED COMBINED JOB IMAGE; incomplete lessons and native integration acceptance remain',
    path=str(ART/'integrated.gba'),romSha1=sha(rom),baseSha1=sha(base),heapEnd=0x0203f000,
    jobs={name:m['romSha1'] for name,m in meta.items()},symbols={**pool,**symbols},
    geomancerAssets={k:v for k,v in geo_assets.items() if k!="maps"},
    regions=dict(geomancerRenderer=[GEO_RENDER,GEO_RENDER+len(render_code)],integration=[CODE,CODE+len(code)],geomancerAI=[GEO_AI,GEO_AI+len(geo_code)],mysticKnight=[MYK_CODE,MYK_CODE+len(myk_code)],missionRecovery=[RECOVERY_CODE,RECOVERY_CODE+len(recovery_code)],jobs=RANGES),tables=dict(actions=ACTIONS,descriptors=DESCRIPTORS,applications=APPLICATIONS,masks=MASKS),missionRecovery=recovery,
    changes=changes,persistentRAM=0,hiddenActions=[432,433,434,435,436,437,438,439,440,441,442,443,444],unimplementedHiddenActions=[],
    jobViews=meta,upstream=base_meta,priorSymbols=base_meta['symbols'],fixtureBaseSha1=samurai['baseSha1'],
    help={job:json.loads((OUT/f'{job}-help.json').read_text()) for job in ('dark-knight','viking','bard','turn','dancer','geomancer','mystic-knight','completion')})
for name in ('physical_eligibility','physical_magnitude','physical_final'):
    report['symbols']['ffta_'+name]=symbols['ffta_integrated_'+name]
(ART/'manifest.json').write_text(json.dumps(report,indent=2));(P/'integrated-jobs/current.json').write_text(json.dumps(report,indent=2))
print(json.dumps({key:value for key,value in report.items() if key not in ('symbols','changes')},indent=2))
