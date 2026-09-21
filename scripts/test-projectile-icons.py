"""Native Throw projectile icon domain, ABI, and quest-preservation regression."""
import ast,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/probes';sha=lambda b:hashlib.sha1(b).hexdigest()
meta=json.loads((OUT/'combat.json').read_text());rom=(OUT/'combat.gba').read_bytes()
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
engine=(ROOT/'build/expansion/engine.bin').read_bytes()
symbols=(ROOT/'build/expansion/engine.symbols').read_bytes()
assert sha(rom)==meta['romSha1'] and sha(engine)==meta['engineSha1']
assert rom[0x1100000:0x1100000+len(engine)]==engine
folder=OUT/'projectile-icons'/sha(rom);folder.mkdir(parents=True,exist_ok=True)
for name,data in [('frozen.gba',rom),('engine.bin',engine),('engine.symbols',symbols)]:
 (folder/name).write_bytes(data)
(folder/'manifest.json').write_text(json.dumps(meta,indent=2))
profiles=json.loads((OUT/'content-data.json').read_text())['itemProfiles']
donors={p['id']:p['donor'] for p in profiles};assert len(donors)==85 and donors[454]==52
# Reuse only the decoder harness definition, not the older test's main.
tree=ast.parse((ROOT/'scripts/test-equipment-icons.py').read_text())
definition=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM')
# Exercise both native stack residues without changing the shared harness.
source=ast.unparse(definition).replace('sp = 50360320','sp = TEST_STACK')
assert 'sp = TEST_STACK' in source
exec(compile(source,'<icon-harness>','exec'))
native,expanded=ARM(clean),ARM(rom);cases=0
for TEST_STACK in (0x03007000,0x03006ffc):
 for ident in range(503):
  for draw in (False,True):
   fn=0x080cb980 if draw else 0x080cb99c
   expected=native.icon(fn,ident,draw)
   assert expanded.icon(fn,ident,draw)==expected,('Generic quest/equipment API changed',ident,draw)
   cases+=1
   # Every original icon remains exact even through the projectile boundary.
   if ident<=460:
    site=0x080d6614 if draw else 0x080d601a
    expected=native.icon(fn,donors.get(ident,ident),draw)
    assert expanded.icon(site,ident,draw,block=True)==expected,('Projectile mapping',ident,draw)
    cases+=1
assert (ROOT/'build/expansion/engine.symbols').read_bytes()==symbols,'Engine changed while freezing'
report={'passed':True,'romSha1':sha(rom),'engineSha1':sha(engine),'symbolsSha1':sha(symbols),
 'cases':cases,'projectileSites':['0x080d601a','0x080d6614'],
 'scope':'Actual native icon decoder/palette instructions at both stack residues; all376 original equipment/consumable IDs unchanged,85new IDs use approved donors; generic namespace0..502 unchanged. Full reward path has separate test-reward-popup.py.'}
(folder/'report.json').write_text(json.dumps(report,indent=2));(OUT/'projectile-icons/report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
