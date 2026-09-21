"""Fixed native roster navigation; retain menu ownership before UI changes."""
import ctypes as C, datetime, hashlib, json, pathlib, runpy, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
manifest=ROOT/'build/expansion/probes/integrated-jobs/current.json'
if '--manifest' in sys.argv:manifest=ROOT/sys.argv[sys.argv.index('--manifest')+1]
meta=json.loads(manifest.read_text(encoding='utf-8'))
ROM=pathlib.Path(meta['path']);assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
OUT=ROM.parent/('potion-menu-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
OUT.mkdir()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
def word(b,p):return struct.unpack_from('<I',b,p)[0]
steps=[]
def capture(e,name):
 r=e.memory();iw=C.string_at(*e.maps[0x03000000]);p=word(iw,0x2818)-0x02000000
 e.save(OUT/(name+'.state'));e.screenshot(OUT/(name+'.png'))
 (OUT/(name+'.ram')).write_bytes(r);(OUT/(name+'.iwram')).write_bytes(iw)
 steps.append(dict(name=name,context=hex(p),selected=hex(word(r,p+0x1d0c)) if 0<=p<0x3c000 else None,preferences=r[0x1e80:0x1e98].hex()))
def tap(e,key):e.run(8,key);e.run(180)
e=E(ROM)
try:
 e.set_memory(0,(ROOT/'build/test-lab/early-town.sav').read_bytes(),0);e.run(3600)
 for key in (8,256,256,256):tap(e,key)
 r=e.memory();slot=next(i for i in range(6) if r[0x80+264*i+6]==3)
 e.set_memory(0x80+264*slot+0x40,bytes([228])*124)
 capture(e,'town')
 keys=[8,256]+([32] if slot>=4 else [])+[128]*(slot%4)+[256,32,256,32,256]
 for n,key in enumerate(keys):tap(e,key);capture(e,f'{n:02d}-{key}')
finally:e.close()
report=dict(romSha1=meta['romSha1'],slot=slot,inputs=keys,steps=steps,output=str(OUT),scope='Navigation diagnostic, not acceptance')
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
