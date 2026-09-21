"""Actual native Wait and command/cancel against the isolated lifecycle stage."""
import argparse,ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha1(b).hexdigest()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-sha');p.add_argument('--fell',action='store_true');p.add_argument('--current',action='store_true');args=p.parse_args()
base_sha=args.base_sha or json.loads((ROOT/'build/expansion/probes/combat.json').read_text())['romSha1']
OUT=ROOT/'build/expansion/probes/exposed-effects'/base_sha
if args.fell:
 from fell_test_context import load_context
 report=load_context(args.current);ROM=pathlib.Path(report['path']);OUT=ROM.parent;fix=OUT/'fixture'
 assert sha((fix/'frozen.gba').read_bytes())==report['romSha1']
else:
 report=json.loads((OUT/'report.json').read_text());ROM=OUT/'isolated.gba';fix=ROOT/'build/expansion/probes/exposed-storage/current'/base_sha/'battle'
 assert sha((fix/'frozen.gba').read_bytes())==base_sha
assert sha(ROM.read_bytes())==report['romSha1']
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](ROM)
def tap(key,wait=120):e.run(8,key);e.run(wait)
try:
 e.load(fix/'battle-ready.state');e.run(1);e.set_memory(0x1e98,bytes([1])*36);before=e.memory()
 # Inspect ordinary Act/Fight, then cancel completely. No turn start occurs.
 for key in [32,256,256,128,256]:tap(key)
 assert e.memory()[0x1e98:0x1ebc]==bytes([1])*36,'Preview expired live state'
 for _ in range(3):tap(1)
 assert e.memory()[0x1e98:0x1ebc]==bytes([1])*36,'Cancel expired live state'
 # Cursor is on Act after cancel; Down selects Wait, then facing confirmation.
 for key in [32,256,256]:tap(key,600)
 after=e.memory();expected=bytearray([1]*36);expected[5]=0
 assert after[0x1e98:0x1ebc]==expected,('Actual own-turn expiry',after[0x1e98:0x1ebc].hex())
 ctx=struct.unpack_from('<I',after,0xf438)[0]-0x02000000
 assert struct.unpack_from('<I',after,ctx+0x18)[0]==0x020005a8,'Wrong actual next actor'
 assert before[0x1940:0x1e98]==after[0x1940:0x1e98],'Inventory/AP/preferences changed'
 assert before[0x3ff44:]==after[0x3ff44:],'Reserved guard changed'
 e.save(OUT/'actual-next-turn.state');e.screenshot(OUT/'actual-next-turn.png')
 (OUT/'actual-next-turn.ram').write_bytes(after)
 result={'passed':True,'romSha1':report['romSha1'],'baseSha1':report['baseSha1'],'checks':['Native Fight preview/cancel retain all36 Exposed bytes','Native Wait/facing starts Colette turn and clears only her owned byte','All inventory/AP/preferences and3FF44 guard preserved'],'scope':'Native own-turn lifecycle on disposable fixture; actual Fell and incoming modifier acceptance are separate.'}
 (OUT/'in-game-report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:e.close()
