"""Actual learned-action choice rows carry explicit stock into native execution."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
code=(ROOT/'scripts/jobs/chemist/test-game.py').read_text().split('for race,unit,job,turns in')[0]
exec(compile(code,str(ROOT/'scripts/jobs/chemist/test-game.py'),'exec'))
for race,unit,job,turns in ((3,0x4a0,120,2),(5,0x188,122,5)):
 for selected,row,amount,action,status in ((363,6,50,386,None),(364,7,150,386,None),(367,1,0,384,9),(368,2,0,384,10),(369,3,0,384,27)):
  e=Emulator(ROM)
  try:
   e.load(FIX/'battle-ready.state');e.run(1)
   for offset in (5,7,0x35):e.set_memory(unit+offset,bytes([job]))
   e.set_memory(unit+0x2a,bytes(10));e.set_memory(unit+0x3a,bytes(3))
   for l in registry['lessons']:
    if l['id'].startswith('CHM-'):
     owner=next(o for o in l['owners'] if o['race']==race);e.set_memory(unit+0x40+owner['abilityIndex'],b'\xff')
   for i in range(turns):
    menu(e);previous=active(e)
    for k in (32,32,256,256):tap(e,k)
    menu(e,previous)
   check('native-active-owner',active(e),0x02000000+unit)
   e.set_memory(unit+0x18,struct.pack('<4H',1,300,50,50));e.set_memory(0x1940+362,bytes([5])*14)
   if status is not None:e.set_memory(unit+0xe8,struct.pack('<Q',1<<status))
   ready=capture(e,f'choice-{race}-{selected}-ready')
   for k in (32,256,32,256):tap(e,k)
   for i in range(row):tap(e,32)
   capture(e,f'choice-{race}-{selected}-row');tap(e,256);tap(e,256)
   preview=capture(e,f'choice-{race}-{selected}-preview')
   check('explicit-selected-learned-action',struct.unpack_from('<H',preview,0xf58e)[0],action)
   check('explicit-selected-consumable',struct.unpack_from('<H',preview,0xf590)[0],selected)
   check('preview-exact-stock-unchanged',preview[0x1940:0x1e70],ready[0x1940:0x1e70])
   tap(e,1);cancel=capture(e,f'choice-{race}-{selected}-cancel');check('cancel-stock-unchanged',cancel[0x1940:0x1e70],ready[0x1940:0x1e70])
   for k in (256,256,256):tap(e,k,180)
   e.run(1800);result=capture(e,f'choice-{race}-{selected}-result')
   if status is None:check('native-selected-item-amount',struct.unpack_from('<H',result,unit+24)[0],1+amount)
   else:check('native-selected-cure',bool(result[unit+0xe8+status//8]&(1<<(status%8))),False)
   check('exact-selected-item-only',result[0x1940+362:0x1940+376],bytes(4 if i==selected else 5 for i in range(362,376)))
   check('no-MP-cost',struct.unpack_from('<H',result,unit+28)[0],50);menu(e)
  finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,total=sum(checks.values()));(LAB/'choice-game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
