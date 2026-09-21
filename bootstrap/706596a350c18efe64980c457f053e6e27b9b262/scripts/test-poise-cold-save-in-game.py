"""Native suspend/cold resume of verified Poise or Blade Ward/Poise outcomes."""
import argparse,hashlib,json,pathlib,runpy,struct
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ward',action='store_true');args=parser.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent
assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
proof=json.loads((LAB/('blade-ward-game/report.json' if args.ward else 'poise-counter/report.json')).read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
if args.ward:
 case=next(x for x in proof['outcomes'] if x.get('counter') and x['poise'] and x['ward']['damage']>0)
 source=LAB/'blade-ward-game/counter-1-ward.state';damage=case['ward']['damage']
else:
 case=next(x for x in proof['outcomes'] if x['action']==352 and not x['regen'] and x['poise']['counter']>0)
 source=LAB/'poise-counter'/f"352-0-{case['seed']}-poise.state";damage=case['poise']['counter']
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
OUT=LAB/('blade-ward-cold-save' if args.ward else 'poise-cold-save');OUT.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'));checks=0
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def tap(e,key,wait=180):e.run(8,key);e.run(wait)
def fields(e):
 r=e.memory();return dict(hp=struct.unpack_from('<H',r,0x98)[0],maximum=struct.unpack_from('<H',r,0x9a)[0],support=r[0xbb],mastery=r[0x1b4a],reaction=r[0xba],reactionMastery=r[0x1b4b],protect=bool(r[0x16b]&2),gear=r[0xaa:0xb4].hex())
e=E(ROM)
try:
 e.load(source);e.run(1);before=fields(e)
 check(before['hp']==500-damage and before['support']==154 and before['mastery']==255 and before['protect'],('Verified input state',before,case))
 if args.ward:check(before['reaction']==155 and before['reactionMastery']==255,('Verified Blade Ward/AP',before))
 tap(e,256,900);menu['wait_for_menu'](e,limit=9000);expected=fields(e);old=e.memory(0)
 for key in (1,8,16,256,256):tap(e,key)
 tap(e,256,300);saved=e.memory(0);check(saved!=old,'Native suspend did not write SRAM');(OUT/'suspended.sav').write_bytes(saved)
finally:e.close()
e=E(ROM)
try:
 e.set_memory(0,saved,0);e.run(3600)
 for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
 menu['wait_for_menu'](e,limit=9000);actual=fields(e);check(actual==expected,('Cold retained Poise/AP/equipment/outcome',expected,actual))
 check(e.memory()[0x3ff48:0x3ff4c]==bytes(4),'A transient action snapshot survived cold boot')
 e.save(OUT/'resumed.state');(OUT/'resumed.ram').write_bytes(e.memory())
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,sourceStateSha256=source_hash,before=before,after=actual,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
