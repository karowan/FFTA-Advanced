"""Fixed hook-isolation sweep for a native movement regression.

Uses the same prepared battle, Viera inputs and checkpoint logic as the full
playback test. Variant ROMs and all observations remain private test outputs.
"""
import pathlib,json,hashlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-dancer-choice-playback.py').read_text().split('# Actual selected player casts')[0]
head,preparation=source.split('e=E(TEST_ROM)',1)
ns={'__file__':str(ROOT/'scripts/test-dancer-choice-playback.py')}
exec(compile(head.replace('dancer-choice-playback','geomancer-movement-diagnostic'),'<native preparation helpers>','exec'),ns)
out=ns['OUT'];test_image=bytes(ns['instrumented']);clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
old=ns['LAB'].parent/'f8d905bde8386802d61c4b9b6258c6182b95fcec';original_fixture=ns['FIX']
rows=[]
variants=[('candidate',()),('native-tile',((0x97814,0x97820),)),('native-Move',((0xca394,0xca3a0),)),
 ('native-Jump',((0xca2e8,0xca2f4),)),('old-OBJ',()),('native-all',((0x97814,0x97820),(0xca394,0xca3a0),(0xca2e8,0xca2f4))),
 ('old-ROM-new-fixture',()),('old-ROM-old-fixture',()),('candidate-old-fixture',()),('fresh-old-OBJ',()),('candidate-settled',())]
if '--initialization' in sys.argv:variants=variants[-2:]
for label,restore in variants:
 image=bytearray(test_image)
 if label.startswith('old-ROM'):
  image=bytearray((old/'integrated.gba').read_bytes());image[0x13f0000:]=test_image[0x13f0000:];image[0xa433c:0xa434c]=test_image[0xa433c:0xa434c]
 ns['FIX']=old/'fixture' if label.endswith('old-fixture') else original_fixture
 for start,end in restore:image[start:end]=clean[start:end]
 if label in ('old-OBJ','fresh-old-OBJ'):image[0x97098:0x9709c]=bytes.fromhex('fe235b00')
 folder=out/label;folder.mkdir(exist_ok=True);rom=folder/'test.gba';rom.write_bytes(image)
 if label=='fresh-old-OBJ':
  ns['FIX']=folder/'fixture'
  subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom),'--out',str(ns['FIX']),'--heap-end',hex(ns['meta']['heapEnd'])],check=True)
 ns['TEST_ROM']=rom;ns['OUT']=folder;ns['case']=label
 body=preparation.replace('e.run(1);menu(e);','e.run(180);menu(e);') if label=='candidate-settled' else preparation
 exec(compile('e=E(TEST_ROM)'+body,'<fixed Viera preparation>','exec'),ns)
 e=ns['E'](rom)
 try:
  e.load(folder/'start.state');e.run(1)
  states=[]
  for key in (256,16,256):
   ns['tap'](e,key);r=e.memory();w=ns['wrappers'][ns['ACTOR']]
   states.append(dict(key=key,mode=ns['mode'](e),xy=[ns['half'](r,w+8)//32,ns['half'](r,w+12)//32]))
  ns['checkpoint'](e,'movement',folder)
  rows.append(dict(variant=label,romSha1=hashlib.sha1(image).hexdigest(),states=states))
 finally:e.close()
 (out/'report.json').write_text(json.dumps(dict(sourceRomSha1=ns['meta']['romSha1'],variants=rows),indent=2))
print(json.dumps(rows,indent=2))
