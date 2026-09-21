"""Current build: native normal/suspend save-load Quin history deltas.

Every case uses ordinary game save menus and a new emulator with SRAM only.
Controlled history/mission flags model old expanded saves and tracked sessions;
two genuinely native-format saves are made with the foundation ROM as well.
"""
import hashlib,json,pathlib,runpy
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes';meta=json.loads((P/'combat.json').read_text());D=P/'quin-history'/meta['romSha1'];D.mkdir(exist_ok=True)
ROM=D/'current.gba';ROM.write_bytes((P/'combat.gba').read_bytes());assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
FIX=P/'quin-current-fixture';assert json.loads((FIX/'report.json').read_text())['romSha1']==meta['romSha1']
O=D/'lifecycle';O.mkdir(exist_ok=True);h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));checks=[]
def check(value,label):assert value,label;checks.append(label)
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def normal_load(rom,sram):
 e=h['Emulator'](rom);e.set_memory(0,sram,0);e.run(3600)
 for k,w in ((8,180),(256,60),(256,60),(256,180)):tap(e,k,w)
 return e
def normal_save(e):
 for k,w in ((8,40),(16,40),(256,40),(256,60),(256,60),(64,20),(256,300)):tap(e,k,w)
 return e.memory(0)
for mode in ('normal','suspend'):
 for history,completed,expected in ((0,False,2),(0,True,3),(2,True,2),(3,False,3)):
  name=f'{mode}-history{history}-completed{int(completed)}';e=h['Emulator'](ROM)
  try:
   e.load(FIX/('accepted-world.state' if mode=='normal' else 'battle-ready.state'))
   e.set_memory(0x1e79,bytes((history,)));e.set_memory(0x1fd8,bytes(((e.memory()[0x1fd8]&~2)|(2 if completed else 0),)))
   roster=e.memory()[0x80:0x1940];prefs=e.memory()[0x1e80:0x1e98]
   if mode=='normal':saved=normal_save(e)
   else:
    for k in (1,8,32,32,32,32,32,256,256):tap(e,k)
    e.screenshot(O/(name+'-saved.png'));tap(e,256);saved=e.memory(0)
   (O/(name+'.sav')).write_bytes(saved);(O/(name+'-expected.roster')).write_bytes(roster)
  finally:e.close()
  if mode=='normal':e=normal_load(ROM,saved)
  else:
   e=h['Emulator'](ROM);e.set_memory(0,saved,0);e.run(1200)
   for k in (8,8,256,256,256,256,64,256):tap(e,k,300)
   e.run(600)
  try:
   r=e.memory();(O/(name+'-actual.roster')).write_bytes(r[0x80:0x1940]);check(r[0x1e79]==expected,name+' history')
   expected_roster=bytearray(roster)
   if mode=='suspend':
    # Native resume rebuilds battle wrapper indices. Initial deployment assigns
    # these six slots5..10; resume reindexes them0..5. This is not saved identity.
    for slot in range(6):
     check(r[0x80+264*slot+0xfb]==slot,name+' native resumed wrapper index')
     expected_roster[264*slot+0xfb]=slot
   check(r[0x80:0x1940]==bytes(expected_roster),name+' all24 units except verified native wrapper remap');check(r[0x1e80:0x1e98]==prefs,name+' adjacent preferences');check(bool(r[0x1fd8]&2)==completed,name+' mission completion unchanged');e.screenshot(O/(name+'-cold-loaded.png'))
  finally:e.close()
foundation=ROOT/'build/foundation/FFTA_vanillaplus_dev.gba';native_rom=O/'native-foundation.gba';native_rom.write_bytes(foundation.read_bytes())
for completed in (False,True):
 name=f'native-import-completed{int(completed)}';e=normal_load(native_rom,(ROOT/'build/test-lab/early-town.sav').read_bytes())
 try:
  check(e.memory()[0x1e70:0x1e78]!=b'FFTAEXP1',name+' genuine native storage')
  e.set_memory(0x1fd8,bytes(((e.memory()[0x1fd8]&~2)|(2 if completed else 0),)));saved=normal_save(e);(O/(name+'.sav')).write_bytes(saved);(O/(name+'-expected.roster')).write_bytes(roster)
 finally:e.close()
 e=normal_load(ROM,saved)
 try:
  check(e.memory()[0x1e79]==(3 if completed else 2),name+' conservative migration');check(bool(e.memory()[0x1fd8]&2)==completed,name+' completion retained');e.screenshot(O/(name+'-cold-loaded.png'))
 finally:e.close()
report={'romSha1':meta['romSha1'],'checks':checks,'scope':__doc__};(O/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'romSha1':meta['romSha1'],'checks':len(checks)}))

