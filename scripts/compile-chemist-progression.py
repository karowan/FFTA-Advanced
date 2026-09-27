"""Compile the coordinated Physician/Sapper ABI without changing a release.

All headers and imported entry addresses are captured in the output receipt.
This compiler deliberately does not install hooks or call a ROM playable.
Installation requires the complete consumer patch plan and runtime acceptance.
"""
import hashlib, json, re, shutil, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/chemist-progressions/code'
SOURCES=('job-state chemist-progression-codec job-save unit-copies evaluated-units action-snapshot battle-state viking-snapshot viking-modifiers '
 'execution-scope snapshot-lend battle-workspace inventory persistent equipment inventory-menus chemist-party chemist-preference '
 'abilities ability-counts command-lists job-wheel combos equipment-preview integrated-jobs '
 'integrated-restoration reaction-queue chemist-progression chemist-delayed chemist-ai samurai-pulse bard bard-passives dark-knight-support dancer chemist-items chemist-state '
 'ai-choice mystic-knight-actions mystic-knight-fight mystic-knight-doublecast mystic-knight-state '
 'mystic-knight-prediction mystic-knight-shell mystic-knight-ai mystic-knight-dispel '
 'custom-law-prediction mystic-knight-laws geomancer geomancer-fields geomancer-field-fast geomancer-renderer geomancer-selection geomancer-ai physical-riders dancer-choice recruit-prerequisites passing-step turn-supports').split()

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 integrated=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
 work=Path(integrated['path']).parents[1]
 memorypath=Path(json.loads((ROOT/'build/expansion/memory-fixes/current.json').read_text())['manifest'])
 memory=json.loads(memorypath.read_text())
 menupath=Path(json.loads((ROOT/'build/expansion/chemist-progressions/menu/current.json').read_text())['manifest'])
 menu=json.loads(menupath.read_text());rom=Path(menu['path']).read_bytes()
 assert hashlib.sha1(rom).hexdigest()==menu['romSha1']
 # The constant-time reaction predicate is derived from this native row.
 # Refuse builds with different permission data instead of silently changing R.
 assert rom[0x527d5c+5*12:0x527d5c+6*12].hex()=='544555775515451554551500'
 symbols={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
 installed_entries={n:{a} for n,a in symbols.items() if 0x08000000<=a<0x0a000000}
 # Later component symbol maps override older versions of the same function.
 # Their entry bytes are retained in the receipt for the installation audit.
 def collect(value):
  if not isinstance(value,dict):return
  for k,v in value.items():
   if k in ('symbols','priorSymbols') and isinstance(v,dict):
    for n,a in v.items():
     if isinstance(a,int) and 0x08000000<=a<0x0a000000:installed_entries.setdefault(n,set()).add(a)
    symbols.update({n:a for n,a in v.items() if isinstance(a,int) and 0x08000000<=a<0x0a000000})
   elif isinstance(v,dict):collect(v)
 collect(integrated)
 symbols.update(integrated['symbols'])
 collect(memory)
 for key in ('jobVisibility','teachingRows','equipmentRevision','enchantWeapons','paletteRemoval','memoryFixes'):collect(memory.get(key,{}))
 registry=(ROOT/'build/expansion/registry.h').read_text().replace('#define FFTA_MAX_ITEM 460u','#define FFTA_MAX_ITEM 470u')
 (OUT/'registry.h').write_text(registry)
 icons=(ROOT/'build/expansion/icons.h').read_text().replace('[85]','[95]').replace('};',',121,149,121,149,121,74,149,74,149,74};')
 (OUT/'icons.h').write_text(icons)
 stock=(ROOT/'build/expansion/stock.h').read_text().replace('[85]','[95]')
 equipment=json.loads((ROOT/'notes/chemist-progression-equipment.json').read_text())['items']
 stock=stock.replace('};',',\n'+','.join('{%d,%d,4}'%(i['id'],{'S1':0,'S2':774,'S3':780}[i['stage']]) for i in equipment)+'\n};')
 (OUT/'stock.h').write_text(stock)
 def encode(s):
  return ','.join(str(v) for c in s for v in ((64,115) if c==' ' else (128,ord(c)+(111 if c.isupper() else 105))))+',0'
 (OUT/'chemist-choice-labels.h').write_text(''.join('static const uint8_t cp_label%d[]={%s};\n'%(i,encode(s)) for i,s in enumerate(('Breach Protect','Breach Shell')))+'static const uint8_t *const ffta_chemist_choice_labels[]={cp_label0,cp_label1};\n')
 shutil.copyfile(Path(menu['header']['path']),OUT/'job-icons.h')
 combat=(work/'combat.c').read_text().replace('item>460','item>470')
 combat='#include "chemist-progression.h"\n'+combat
 combat=combat.replace('if(ffta_myk_action(action))return ffta_myk_magnitude(context);','if(action>=453 && action<=459)return ffta_cp_magnitude(context);\n    if(ffta_myk_action(action))return ffta_myk_magnitude(context);')
 (OUT/'combat.c').write_text(combat)
 # Preserve the native badge decoder behind the already-installed hook.
 preview=memory['components']['preview']
 symbols['ffta_cp_original_icon']=preview['originalIconDecoder']
 assert symbols['ffta_cp_original_icon']&1
 # The observer must call each installed callback, not its new table entry.
 table=0x08000000+integrated['tables']['applications']
 assert 0x08000000<=table<0x0a000000
 original_apps=[struct.unpack_from('<I',rom,table-0x08000000+12*i)[0] for i in range(112)]
 original_c='#include "chemist-progression.h"\nuint8_t *ffta_cp_original_application(uint8_t *c,unsigned id){\n static const uintptr_t callbacks[112]={'+','.join(hex(x) for x in original_apps)+'};\n if(id==112)return ffta_cp_apply(c);\n return id<112 && callbacks[id]?((uint8_t *(*)(uint8_t *))callbacks[id])(c):c;\n}\n'
 (OUT/'applications.c').write_text(original_c)
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 flags=['-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-DFFTA_CHEMIST_PROGRESSION=1','-DFFTA_PARTY_LIST_OFFSET=0x7290',
  '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-ffunction-sections','-fdata-sections','-fstack-usage',
  '-I',str(OUT),'-I',str(ROOT/'src/engine'),'-I',str(ROOT/'build/expansion'),'-I',str(work)]
 callbacks='.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'
 for name in ('ffta_cp_apply','ffta_cp_application_observer','ffta_chemist_revive'):
  callbacks+=f'.align 2\n.global {name}_entry\n.thumb_func\n{name}_entry:\n push {{r4-r5,lr}}\n mov r4,sp\n mov r5,sp\n lsrs r5,r5,#3\n lsls r5,r5,#3\n mov sp,r5\n bl {name}\n mov sp,r4\n pop {{r4-r5}}\n pop {{r1}}\n bx r1\n'
 (OUT/'cp-callbacks.s').write_text(callbacks)
 # The native executor transports Breach's explicit defense selection through
 # the same operand channel as the established choice-based commands.
 (OUT/'cp-choice-transport.s').write_text('.equ FFTA_CHEMIST_PROGRESSION,1\n'+(ROOT/'src/engine/dancer-choice.s').read_text().split('.global ffta_dancer_preview_choice_entry')[0])
 sources=[ROOT/'src/engine'/f'{s}.c' for s in SOURCES]+[ROOT/'src/engine/chemist-controller.s']+[OUT/n for n in ('combat.c','applications.c','cp-callbacks.s','cp-choice-transport.s')]
 objects=[];exports=[];failures=[]
 for source in sources:
  obj=OUT/(source.stem+'.o');cmd=[prefix+'gcc.exe',*flags,'-c',str(source),'-o',str(obj)]
  run=subprocess.run(cmd,capture_output=True,text=True);(OUT/(source.stem+'.log')).write_text(run.stdout+run.stderr)
  if run.returncode:failures.append(dict(source=str(source),errors=run.stderr));continue
  objects.append(obj)
  exports.extend(p[2] for line in subprocess.check_output([prefix+'nm.exe',str(obj)],text=True).splitlines() if len(p:=line.split())==3 and p[1]=='T')
 assert not failures,json.dumps(failures,indent=2)
 # Weak extension callbacks are still real integration dependencies when the
 # installed engine supplies them. The linker silently resolves an omitted
 # weak reference to zero, disabling snapshots/reactions without an error.
 # Authenticate and import these explicitly before resolving strong imports.
 weak=set()
 for obj in objects:
  for line in subprocess.check_output([prefix+'nm.exe','-u',str(obj)],text=True).splitlines():
   p=line.split()
   if len(p)==2 and p[0]=='w' and p[1] in symbols and p[1] not in exports:weak.add(p[1])
 helpers=OUT/'imports.s';needed=sorted(weak);elf=OUT/'jobs.elf';binary=OUT/'jobs.bin'
 for attempt in range(4):
  helpers.write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'+''.join(
   f'.align 2\n.global {n}\n.thumb_func\n{n}:\n push {{r3}}\n ldr r3,={hex(symbols[n]|1)}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n' for n in needed))
  cmd=[prefix+'gcc.exe',*flags,'-nostdlib','-Wl,--gc-sections,-Ttext=0x09a50000,-e,ffta_cp_apply',
    *[f'-Wl,-u,{n}' for n in exports],*map(str,objects),str(helpers),'-lgcc','-o',str(elf)]
  run=subprocess.run(cmd,capture_output=True,text=True);(OUT/'link.log').write_text(run.stdout+run.stderr)
  if not run.returncode:break
  missing=sorted(set(re.findall(r"undefined reference to `([A-Za-z0-9_]+)'",run.stderr))-set(needed))
  assert missing and all(n in symbols for n in missing),dict(unresolved=[n for n in missing if n not in symbols],log=str(OUT/'link.log'))
  needed+=missing
 run.check_returncode()
 subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.text','-j','.rodata',str(elf),str(binary)],check=True)
 sections=subprocess.check_output([prefix+'objdump.exe','-h',str(elf)],text=True);(OUT/'sections.txt').write_text(sections)
 assert not any(len(p:=line.split())>2 and p[1] in ('.data','.bss') and int(p[2],16) for line in sections.splitlines())
 disassembly=subprocess.check_output([prefix+'objdump.exe','-d',str(elf)],text=True);(OUT/'disassembly.txt').write_text(disassembly)
 assert 'veneer' not in disassembly and 'ldr\tpc' not in disassembly
 built={p[3]:dict(address=int(p[0],16),bytes=int(p[1],16)) for line in subprocess.check_output([prefix+'nm.exe','-S',str(elf)],text=True).splitlines() if len(p:=line.split())==4 and p[2] in ('T','t')}
 for line in subprocess.check_output([prefix+'nm.exe','-S',str(elf)],text=True).splitlines():
  p=line.split()
  if len(p)==3 and p[1] in ('T','t'):built[p[2]]=dict(address=int(p[0],16),bytes=0)
 assert len(binary.read_bytes())<=0x40000
 receipt=dict(status='Compiled only; no hooks installed',romSha1=menu['romSha1'],parent=str(menupath),elf=str(elf),binary=str(binary),
  binarySha256=hashlib.sha256(binary.read_bytes()).hexdigest(),symbols=built,exports=exports,
  imports={n:dict(address=symbols[n],installedBytes=rom[(symbols[n]&~1)-0x08000000:(symbols[n]&~1)-0x08000000+16].hex()) for n in needed},
  installedSymbols=symbols,installedEntries={n:sorted(v) for n,v in installed_entries.items()},
  sourceSha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
  headerSha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src/engine').glob('*.h'))+sorted(OUT.glob('*.h'))},command=cmd)
 (OUT/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(dict(status='compiled',sources=len(sources),exports=len(exports),imports=len(needed),bytes=len(binary.read_bytes()))))

if __name__=='__main__':main()
