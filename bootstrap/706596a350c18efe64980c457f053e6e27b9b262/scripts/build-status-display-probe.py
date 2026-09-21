"""Private status-icon overlay; no production ROM or player save writes."""
import pathlib,struct,subprocess,json,hashlib,runpy
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes';OUT=P/'status-display/private';OUT.mkdir(parents=True,exist_ok=True)
rom=bytearray((P/'combat.gba').read_bytes());meta=json.loads((P/'combat.json').read_text());assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
runpy.run_path(str(ROOT/'scripts/generate-status-glyphs.py'))
stub='.syntax unified\n.cpu arm7tdmi\n.thumb\n.global ffta_owned_exposed\n.thumb_func\nffta_owned_exposed:\n ldr r3,='+hex(symbols['ffta_owned_exposed']|1)+'\n bx r3\n'
(OUT/'link.s').write_text(stub)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x09170000,-e,ffta_status_icon_entry',str(ROOT/'src/engine/status-display.c'),str(ROOT/'src/engine/status-display.s'),str(ROOT/'src/engine/samurai-state.c'),str(OUT/'link.s'),'-o',str(OUT/'private.elf')],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'private.elf'),str(OUT/'private.bin')],check=True)
symbols.update({p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'private.elf')],text=True).splitlines() if len(p:=l.split())==3})
code=(OUT/'private.bin').read_bytes();assert rom[0x1170000:0x1170000+len(code)]==b'\xff'*len(code);rom[0x1170000:0x1170000+len(code)]=code
(OUT/'input.gba').write_bytes(rom);(OUT/'symbols.json').write_text(json.dumps(symbols))
js="import fs from'node:fs';import{patchStatusDisplay}from'./scripts/patch-status-display.mjs';const p=process.argv[1],b=fs.readFileSync(p+'/input.gba'),s=JSON.parse(fs.readFileSync(p+'/symbols.json'));const h=patchStatusDisplay(b,s);fs.writeFileSync(p+'/patched.gba',b);fs.writeFileSync(p+'/hooks.json',JSON.stringify(h));"
subprocess.run(['node','--input-type=module','-e',js,str(OUT)],cwd=ROOT,check=True)
rom=(OUT/'patched.gba').read_bytes();hooks=json.loads((OUT/'hooks.json').read_text())
sha=hashlib.sha1(rom).hexdigest();LAB=OUT/sha;LAB.mkdir(exist_ok=True)
(LAB/'status.gba').write_bytes(rom);(LAB/'base.gba').write_bytes((P/'combat.gba').read_bytes())
report=dict(romSha1=sha,baseSha1=meta['romSha1'],path=str(LAB/'status.gba'),symbols=symbols,hooks=hooks,status='Private display layer; acceptance is in matching native-report.json and game-report.json. Full ability composition is separate.')
(OUT/'current.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='symbols'},indent=2))
