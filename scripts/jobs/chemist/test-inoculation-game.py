"""Both racial native Inoculation menus, cancellation, payment, expiry and save."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
exec(compile((ROOT/'scripts/jobs/chemist/test-game.py').read_text().split('for race,unit,job,turns in')[0],str(ROOT/'scripts/jobs/chemist/test-game.py'),'exec'))
OUT=LAB/'inoculation-game';OUT.mkdir(exist_ok=True)
for race,unit,job,turns in ((3,0x4a0,120,2),(5,0x188,122,5)):
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
  e.set_memory(unit+0x18,struct.pack('<4H',100,300,50,50));e.set_memory(0x1940+362,bytes([5])*14)
  state=0x3f410+((unit-0x80)//264)*22+8
  ready=capture(e,f'{race}-ready')
  for k in (32,256,32,256):tap(e,k)
  for i in range(12):tap(e,32)
  capture(e,f'{race}-row');tap(e,256);tap(e,256);preview=capture(e,f'{race}-preview')
  check('native-Inoculation-selected',struct.unpack_from('<H',preview,0xf58e)[0],391)
  check('preview-no-stock-cost',preview[0x1940:0x1e70],ready[0x1940:0x1e70]);check('preview-no-live-state',preview[state],0)
  tap(e,1);cancel=capture(e,f'{race}-cancel');check('cancel-no-live-state',cancel[state],0);check('cancel-no-stock-cost',cancel[0x1940:0x1e70],ready[0x1940:0x1e70])
  for k in (256,256,256):tap(e,k,180)
  e.run(1200);result=capture(e,f'{race}-result')
  check('actual-Inoculated-owned-T2',result[state]&7,6)
  check('exact-two-ingredient-payment',result[0x1940+362:0x1940+376],bytes(4 if i in (362,374) else 5 for i in range(362,376)))
  check('Inoculation-no-healing-or-MP-cost',result[unit+24:unit+32],struct.pack('<4H',100,300,50,50))
  menu(e);previous=active(e)
  for k in (32,32,256,256):tap(e,k)
  menu(e,previous);after=capture(e,f'{race}-turn-ended');check('application-own-turn-skipped',after[state]&7,2)
  # Native suspend; cold boot receives only this private SRAM.
  for k in (1,8,16,256,256):tap(e,k)
  tap(e,256,300);saved=e.memory(0);(OUT/f'{race}-suspended.sav').write_bytes(saved)
 finally:e.close()
 e=Emulator(ROM)
 try:
  e.set_memory(0,saved,0);e.run(3600)
  for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
  menu(e);cold=capture(e,f'{race}-cold');check('native-suspend-cold-state',cold[state]&7,2);check('native-suspend-cold-inventory',cold[0x1940:0x1e70],after[0x1940:0x1e70])
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,total=sum(checks.values()));(LAB/'inoculation-game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
