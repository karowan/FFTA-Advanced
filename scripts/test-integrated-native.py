"""Complete native executor/Iaido differential on the assembled job image."""
import pathlib
from job_test_candidate import normalize_native_context,initialize_inactive_turn_domain
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-samurai-native.py').read_text()
source=source.replace("P/'samurai/current.json'","P/'integrated-jobs/current.json'")
source=source.replace("P/'samurai-state'/meta['baseSha1']","pathlib.Path(meta['path']).parent/'executor'")
#423 was an empty reserved record when the Samurai differential was written.
# Its approved Break Blade semantics now belong to the Mystic command suite;
# retain every vanilla0..346 and the existing sword/axe comparison unchanged.
old='list(range(347))+[357,358,423,424,425,426,427,428,429,430,431]'
assert source.count(old)==1
source=source.replace(old,'list(range(347))+[357,358,424,425,426,427,428,429,430,431]')
# Both sides start with an inactive newly allocated turn domain. Keep the
# output comparison intact so unintended lifecycle writes still fail.
source=source.replace(' m.put(0x0203ff48,bytes(4))',' m.put(0x0203ff48,bytes(4))\n initialize_inactive_turn_domain(m)')
checker='''def check(kind,a,b):
 counts[kind]+=1
 if isinstance(a,bytes) and isinstance(b,bytes) and len(a)==0x40000:
  a=normalize_native_context(a,rom,base);b=normalize_native_context(b,rom,base)
  counts['verified-context-table-relocations']+=1
  if kind=='complete-native-executor-preserved' and 424<=globals().get('action',0)<=430:
   # Axe execution now additionally publishes an owned elemental-law receipt.
   # This frozen fixture rejects Fell Cleave431 before result application;
   # keep its entire RAM comparison unchanged, including the zero receipt.
   # Prove its exact content, then compare every other byte as before.
   word=lambda data,p:struct.unpack_from('<I',data,p)[0]
   manager=word(a,0xf4b0)-0x02000000
   assert a[manager+0x430:manager+0x440]==b[manager+0x430:manager+0x440]
   pool=word(a,manager+0x438)-0x02000000;receipt=pool+0x2620
   assert word(a,pool)==0x31535742 and word(a,pool+4)==manager+0x02000000 and word(a,pool+8)==pool+0x02000000
   assert b[receipt:receipt+64]==bytes(64)
   expected=bytearray(64);container=regs[0]-0x02000000
   for index in range(14):
    o=container+index*0x2c4;wrapper=word(a,o)
    if wrapper!=regs[1] or struct.unpack_from('<H',a,o+16)[0]!=action:continue
    actor=word(a,wrapper-0x02000000);gear=struct.unpack_from('<5H',a,actor-0x02000000+0x2a)
    primary=next((item for item in gear if item and item<=375 and rom[0x51d1a0+(item-1)*32+11] in (1,2) and rom[0x51d1a0+(item-1)*32+8]!=20),0)
    assert primary and rom[0x51d1a0+(primary-1)*32+9]==0,('frozen fixture primary changed',primary)
    struct.pack_into('<4I',expected,0,0x314c464d,regs[0],actor,wrapper);expected[16+index]=0x80
   assert expected[:4]!=bytes(4) and a[receipt:receipt+64]==expected,('exact axe law receipt',action)
   b=bytearray(b);b[receipt:receipt+64]=expected;b=bytes(b)
   counts['verified-exact-added-axe-law-receipt']+=1
 if a!=b and isinstance(a,bytes) and isinstance(b,bytes):
  (OUT/'integrated-native-actual.ram').write_bytes(a);(OUT/'integrated-native-expected.ram').write_bytes(b)
  differences=[dict(address=hex(0x02000000+i),actual=x,expected=y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
  (OUT/'integrated-native-difference.json').write_text(json.dumps(dict(action=globals().get('action'),kind=kind,differences=differences),indent=2))
  raise AssertionError((kind,globals().get('action'),len(differences),differences[:20]))
 assert a==b,(kind,a,b)
'''
source=source[:source.index('def check(')]+checker+source[source.index('from native_battle_wrappers'):]
exec(compile(source,__file__,'exec'))
