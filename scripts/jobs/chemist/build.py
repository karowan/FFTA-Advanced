"""Compose Chemist over the locally tested, hash-verified job-state image."""
import hashlib,json,pathlib,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];P=ROOT/'build/expansion/probes';sha=lambda b:hashlib.sha1(b).hexdigest()
up=json.loads((P/'job-state/current.json').read_text());base=pathlib.Path(up['path']).read_bytes();assert sha(base)==up['romSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert sha(clean)=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
OUT=P/'chemist'/sha(base);OUT.mkdir(parents=True,exist_ok=True);(OUT/'input.gba').write_bytes(base)
old={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3};old.update(up['symbols'])
names={'ffta_previous_eligibility':'ffta_physical_eligibility','ffta_previous_paid':'ffta_custom_physical_paid','ffta_previous_geometry':'ffta_combat_geometry','ffta_native_free_count':'ffta_native_free_count','ffta_native_lose_item':'ffta_native_lose_item','ffta_projectile_los':'ffta_projectile_los'}
names['ffta_previous_centered_event']='ffta_centered_event'
names['ffta_previous_centered_turn_end']='ffta_centered_turn_end'
for name in ('icon','next_key','visual'):names['ffta_previous_status_'+name]='ffta_wound_status_'+name
for name in ('ffta_job_state','ffta_job_origin','ffta_job_potion','ffta_job_peers','ffta_action_paid','ffta_action_phase','ffta_action_origin','ffta_action_unit_flags','ffta_action_claimed','ffta_action_claim','ffta_action_reactions_enabled','ffta_action_actor','ffta_action_unit_at','ffta_action_reaction_kind','ffta_action_reaction_value','ffta_reaction_queue_append','ffta_reaction_queue_entry'):names[name]=name
bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n'
for name,previous in names.items():
 bindings+=f'.align 2\n.global {name}\n.thumb_func\n{name}:\n push {{r3}}\n ldr r3,={old[previous]|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(OUT/'bindings.s').write_text(bindings)
paid=(ROOT/'src/engine/samurai-actions.s').read_text();paid=paid[:paid.index('.global ffta_samurai_law_entry')];paid=paid.replace('ffta_samurai_paid_entry','ffta_chemist_paid_entry').replace('    bl ffta_custom_physical_paid','    movs r2,r4\n    ldr r3,=0x104\n    adds r2,r2,r3\n    ldr r2,[r2]\n    movs r3,r4\n    adds r3,#40\n    bl ffta_chemist_payment_gate');(OUT/'paid.s').write_text(paid)
geometry=(ROOT/'src/engine/combat-geometry.s').read_text();geometry=geometry[:geometry.index('.global ffta_original_combat_geometry')].replace('ffta_combat_geometry','ffta_chemist_geometry');(OUT/'geometry.s').write_text(geometry)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'chemist.elf';binary=OUT/'chemist.bin'
labels=['Remedy: Antidote','Remedy: Eye Drops','Remedy: Echo Screen','Remedy: Soft','Tonic: Hi-Potion','Tonic: X-Potion']
def encoded(text):
 result=[]
 for c in text:
  if 'A'<=c<='Z':result += [0x80,0xb0+ord(c)-65]
  elif 'a'<=c<='z':result += [0x80,0xca+ord(c)-97]
  else:result += {' ':[0x40,0x73],'-':[0x81,0x0b],':':[0x80,0xee]}[c]
 return result+[0]
header=''.join('static const uint8_t label%d[]={%s};\n'%(i,','.join(map(str,encoded(t)))) for i,t in enumerate(labels))
header+='static const uint8_t *const ffta_chemist_choice_labels[]={'+','.join('label%d'%i for i in range(6))+'};\n'
(OUT/'chemist-menu-labels.h').write_text(header,encoding='utf-8')
header=''
for i,t in enumerate(('Auto: Potion','Auto: Hi-Potion','Potion - set','Hi-Potion - set')):
 header+='static const uint8_t potion%d[]={%s};\n'%(i,','.join(map(str,encoded(t))))
header+='static const uint8_t *const ffta_potion_preference_labels[]={potion0,potion1,potion2,potion3};\n'
(OUT/'chemist-preference-labels.h').write_text(header,encoding='utf-8')
status_asm=(ROOT/'src/engine/status-display.s').read_text().replace('ffta_status_','ffta_chemist_status_');(OUT/'status.s').write_text(status_asm)
sources=[ROOT/'src/engine/chemist-preference.c',ROOT/'src/engine/chemist-preference.s',ROOT/'src/engine/chemist-reactions.c',OUT/'status.s',ROOT/'src/engine/chemist-status-display.c',ROOT/'src/engine/chemist-state.s',ROOT/'src/engine/chemist-state.c',ROOT/'src/engine/chemist-menu.c',ROOT/'src/engine/chemist-menu.s',ROOT/'src/engine/chemist-items.c',ROOT/'src/engine/chemist-items.s',OUT/'bindings.s',OUT/'paid.s',OUT/'geometry.s']
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(OUT),'-I',str(ROOT/'src/engine'),'-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x09280000,-e,ffta_chemist_eligibility_entry',*map(str,sources),'-lgcc','-o',str(elf)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
# Inline entry must not pass through a C binding veneer that clobbers r12.
symbols['ffta_reaction_queue_entry']=old['ffta_reaction_queue_entry']
rom=bytearray(base);code=binary.read_bytes();assert len(code)<0x10000;assert rom[0x1280000:0x12c0000]==b'\xff'*0x40000;rom[0x1280000:0x1280000+len(code)]=code;changes=[]
def hook(start,end,name,previous=None):
 jump=(start+5)&~3
 if previous:assert struct.unpack_from('<I',rom,jump+4)[0]==old[previous]|1,(hex(start),previous)
 else:assert rom[start:end]==clean[start:end],hex(start)
 original=rom[start:end].hex();rom[start:end]=b'\xc0\x46'*((end-start)//2);struct.pack_into('<H',rom,start,0xb408);struct.pack_into('<HHI',rom,jump,0x4b00,0x4718,symbols[name]|1);changes.append(dict(start=start,end=end,name=name,original=original))
def pointer(offset,name):
 original=struct.unpack_from('<I',rom,offset)[0];struct.pack_into('<I',rom,offset,symbols[name]|1);changes.append(dict(start=offset,end=offset+4,name=name,original=original))
assert rom[0x97098:0x9709c]==bytes.fromhex('f3235b00');rom[0x97098]=0xf8
assert struct.unpack_from('<I',rom,0x9da10)[0]==old['ffta_status_icon_entry']|1
pointer(0x9da10,'ffta_chemist_status_icon_entry')
hook(0x9dd52,0x9dd62,'ffta_chemist_status_next_entry','ffta_status_next_entry')
hook(0x97ad0,0x97ae4,'ffta_chemist_status_visual_entry','ffta_status_visual_entry')
provider=old['ffta_additional_beneficial']-0x08000000
assert rom[provider:provider+4]==bytes.fromhex('00207047')
struct.pack_into('<HHI',rom,provider,0x4b00,0x4718,symbols['ffta_chemist_beneficial_entry']|1)
changes.append(dict(name='Chemist beneficial provider',start=provider,end=provider+8))
provider=old['ffta_additional_snapshot_flags']-0x08000000
assert rom[provider:provider+16]==bytes.fromhex('00207047')+bytes(12)
struct.pack_into('<HHI',rom,provider,0x4b00,0x4718,symbols['ffta_chemist_snapshot_flags_entry']|1)
changes.append(dict(name='Chemist snapshot provider',start=provider,end=provider+8))
for previous,name in [('ffta_additional_hp_loss','ffta_chemist_hp_loss_entry'),('ffta_additional_reaction_queue','ffta_chemist_reaction_queue_entry')]:
 provider=old[previous]-0x08000000
 assert rom[provider:provider+16]==bytes.fromhex('00207047')+bytes(12),previous
 struct.pack_into('<HHI',rom,provider,0x4b00,0x4718,symbols[name]|1)
 changes.append(dict(name=name,start=provider,end=provider+8))
hook(0xa4adc,0xa4ae8,'ffta_reaction_queue_entry')
hook(0xa2eb8,0xa2ec4,'ffta_chemist_native_item_debit_entry')
hook(0x131dd4,0x131de0,'ffta_chemist_status_entry')
hook(0x7d96c,0x7d978,'ffta_potion_roster_entry')
hook(0x7e004,0x7e014,'ffta_potion_confirm_entry')
hook(0x26d44,0x26d50,'ffta_chemist_menu_entry')
hook(0x26f9c,0x26fa8,'ffta_chemist_restricted_menu_entry')
hook(0x25758,0x25764,'ffta_chemist_menu_name_entry')
hook(0x28a8c,0x28a98,'ffta_chemist_menu_selected_entry')
hook(0xa45c6,0xa45d4,'ffta_chemist_paid_entry','ffta_samurai_paid_entry')
hook(0xa0014,0xa0020,'ffta_chemist_geometry_entry','ffta_combat_geometry_entry')
hook(0x12f230,0x12f23c,'ffta_chemist_context_entry')
hook(0xa013a,0xa014a,'ffta_chemist_range_entry')
hook(0xa2edc,0xa2eea,'ffta_chemist_consumption_entry')
pointer(0x3a8604+8*4,'ffta_chemist_eligibility_entry');pointer(0x3a86f8+35*4,'ffta_chemist_hp_entry');pointer(0x3a86f8+34*4,'ffta_chemist_mp_entry')
# Descriptor bank relocation preserves all native indices and six direct users.
descriptor=0x1290000;bank=bytearray(rom[0x553e70:0x553e70+209*4]);bank+=bytes([8,38,1,35,8,68,1,41])+bytes(4*4)+bytes([8,95,1,1])+bytes(4*4)+bytes([8,96,23,0])
rom[descriptor:descriptor+len(bank)]=bank
for offset in (0xb4cec,0xc1ca4,0xc230c,0x12f2a0,0x12f348,0x12f3c8):
 assert struct.unpack_from('<I',rom,offset)[0]==0x08553e70;struct.pack_into('<I',rom,offset,0x08000000+descriptor)
# Native application callback metadata and the separate status-admission/removal
# bitpairs are independent domains; both must cover custom application95.
application=0x1291000;masks=0x1292000
app=bytearray(rom[0x3a87b0:0x3a87b0+93*12]);app+=app[:12]*4
struct.pack_into('<I',app,95*12,symbols['ffta_chemist_inoculation_entry']|1)
app[95*12+8]=255
struct.pack_into('<I',app,96*12,symbols['ffta_chemist_inert_entry']|1)
app[96*12+8]=255
status_masks=bytearray(rom[0x52790c:0x52790c+93*12]);status_masks+=bytes(4*12)
# Positive custom effect admits existing native statuses and removes none;
# its eligibility/callback separately rejects KO, Petrify and undead.
status_masks[95*12:96*12]=bytes([0x55]*11+[0])
status_masks[96*12:97*12]=bytes([0x55]*11+[0])
for original,replacement,required in [(0x083a87b0,0x08000000+application,{0x1323b8,0x132430,0x133920,0x133984,0x1339a4}),
                                     (0x0852790c,0x08000000+masks,{0x1339c8})]:
 sites=[i for i in range(0,len(base)-3,4) if struct.unpack_from('<I',base,i)[0]==original]
 assert required.issubset(sites),(hex(original),sites)
 for i in sites:struct.pack_into('<I',rom,i,replacement)
 changes.append(dict(name='application table domain',old=original,new=replacement,pointerSites=sites))
rom[application:application+len(app)]=app;rom[masks:masks+len(status_masks)]=status_masks
# Compose the existing explicit-unit lifecycle calls. Newly linked previous
# imports live outside these scanned regions, so cannot recurse into wrappers.
samurai=json.loads((P/'samurai/current.json').read_text());assert samurai['romSha1']==up['baseSha1']
regions=[(0x1100000,len((ROOT/'build/expansion/engine.bin').read_bytes())),
         (0x11c0000,len((P/'samurai'/samurai['baseSha1']/'samurai.bin').read_bytes())),
         (0x11d0000,len((P/'job-state'/up['baseSha1']/'state.bin').read_bytes()))]
for previous,name in [('ffta_centered_event','ffta_chemist_combined_event'),('ffta_centered_turn_end','ffta_chemist_combined_turn_end')]:
 address=old[previous];sites=[]
 for start,size in regions:
  for i in range(start,start+size-2,2):
   a,b=struct.unpack_from('<HH',rom,i)
   if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
   d=((a&0x7ff)<<12)|((b&0x7ff)<<1)
   if d&0x400000:d-=0x800000
   if 0x08000000+i+4+d!=address:continue
   d=symbols[name]-(0x08000000+i+4);assert -0x400000<=d<0x400000 and not d&1
   struct.pack_into('<HH',rom,i,0xf000|((d>>12)&0x7ff),0xf800|((d>>1)&0x7ff));sites.append(i)
  for i in range(start,start+size-3,4):
   if struct.unpack_from('<I',rom,i)[0]==address|1:struct.pack_into('<I',rom,i,symbols[name]|1);sites.append(i)
 assert sites,previous
 changes.append(dict(name=name,previous=address,callAndPointerSites=sites))
registry=json.loads((ROOT/'build/expansion/registry.json').read_text());table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
enabled=[(383,251,(209,1,1,1)),(384,264,(139,1,1,1)),(385,256,(210,1,1,1)),(386,252,(209,1,1,1)),(387,251,(209,1,1,1)),(388,254,(36,1,1,1)),(389,264,(139,1,1,1)),(390,256,(210,1,1,1)),(391,251,(215,1,1,1)),(392,12,(45,78,1,1))]
for action,donor,vector in enabled:
 lesson=next(l for l in registry['lessons'] if l['globalAbilityId']==action and l['type']=='Action');r=bytearray(clean[0x55187c+donor*28:0x55187c+(donor+1)*28]);struct.pack_into('<H',r,0,lesson['nameId']);r[2]=0;r[4]=0;r[5]=0;r[6]=3 if action==387 else 4;r[7]=2;r[8]=1;r[9]=5;r[10]=2;r[12:16]=bytes(vector)
 flags=struct.unpack_from('<I',r,16)[0];flags|=(1<<16)|(1<<9);flags&=~((1<<7)|(1<<8));struct.pack_into('<I',r,16,flags)
 assert not any(rom[table+action*28:table+(action+1)*28]);rom[table+action*28:table+(action+1)*28]=r
# Explicit hidden reaction-action domain, disjoint from learned/AI lists.
# Preserve all432 assembled rows, including every existing custom action.
hidden_table=0x1294000
bank=bytearray(rom[table:table+432*28])+bytearray(4*28)
row=bytearray(clean[0x55187c+264*28:0x55187c+265*28])
row[2]=row[4]=row[5]=0;row[6]=0;row[7]=2;row[8]=1
row[12:16]=bytes([220,1,1,1])
flags=struct.unpack_from('<I',row,16)[0]
flags=(flags|(1<<9))&~((1<<7)|(1<<8)|(1<<16))
struct.pack_into('<I',row,16,flags);bank[432*28:433*28]=row
rom[hidden_table:hidden_table+len(bank)]=bank
users={0x23320,0x236ac,0x25998,0x26c9c,0x26d3c,0x26e18,0x27048,0x27170,0x279a0,0x27a94,0xa784c,0xb5d18,0xc3080,0xc3474,0xccd84,0x133e70,0x13416c}
sites=[i for i in range(0,len(base)-3,4) if struct.unpack_from('<I',base,i)[0]==0x08000000+table]
assert users.issubset(sites),(users-set(sites))
for i in sites:struct.pack_into('<I',rom,i,0x08000000+hidden_table)
changes.append(dict(name='hidden reaction action bank',pointerSites=sites,originalCount=432,totalCount=436,offset=hidden_table,hidden=[432]))
ART=OUT/sha(rom);ART.mkdir(exist_ok=True);(ART/'chemist.gba').write_bytes(rom);(ART/'input.gba').write_bytes(base)
report=dict(status='Development: medicines, explicit choices and supports wired; Inoculated installed; reactions in progress; full acceptance pending',heapEnd=up['heapEnd'],romSha1=sha(rom),baseSha1=sha(base),path=str(ART/'chemist.gba'),symbols=symbols,changes=changes,enabled=[x[0] for x in enabled],upstream=up)
(ART/'manifest.json').write_text(json.dumps(report,indent=2));(P/'chemist/current.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('symbols','upstream')},indent=2))
