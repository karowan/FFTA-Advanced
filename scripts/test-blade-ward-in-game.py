"""UI-launched Guarding Draw, fixed RNG at native entry and measured at return.

Private test ROMs seed once at A433C and stop at its observed UI caller return.
This preserves combat RNG and avoids ambient input-update RNG before/after the
transaction. No result, accuracy, cost, damage or reaction is injected.
"""
import sys
import ctypes as C,hashlib,itertools,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/('build/expansion/probes/job-state/current.json' if '--job-state' in sys.argv else 'build/expansion/probes/samurai/current.json')).read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
proof=json.loads((LAB/'game-report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
OUT=LAB/'blade-ward-game';OUT.mkdir(exist_ok=True);control=bytearray(rom)
for name,value in (('ffta_poise_factor',4),('ffta_blade_ward_factor',20)):
 p=meta['symbols'][name]-0x08000000;control[p:p+4]=bytes((value,0x20,0x70,0x47))
CONTROL=OUT/'neutral-factors.gba';CONTROL.write_bytes(control)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];outcomes=[];checks=0
instrumented=[];entry_paths={};capture_frames={}

def fixed_entry(image,name,seed):
 if (name,seed) in entry_paths:return entry_paths[name,seed]
 # The installed entry saves r3 before its literal jump. Preserve r0/r1,
 # flags, LR and that exact stack contract before forwarding to its target.
 image=bytearray(image);entry=0xa433c;stub=0x11df000;done=0xa822e
 assert image[entry:entry+8]==bytes.fromhex('08b4c046004b1847'),image[entry:entry+12].hex()
 original=struct.unpack_from('<I',image,entry+8)[0]
 assert original==meta['symbols']['ffta_samurai_execute_entry']|1
 code=bytes.fromhex('03b403480349086003bc034b1847c046')+struct.pack('<3I',seed,0x030034b0,original)
 assert image[stub:stub+len(code)]==b'\xff'*len(code),'test reservation must be unused'
 image[stub:stub+len(code)]=code;struct.pack_into('<I',image,entry+8,0x08000000+stub+1)
 # Observed LR at A433C is 080A822F. Halt only after its complete native
 # transaction returns, including nested Counter and root retirement.
 image[done:done+2]=bytes.fromhex('fee7')
 path=OUT/f'entry-{seed}-{name}.gba';path.write_bytes(image)
 instrumented.append(dict(name=name,seed=seed,sha1=hashlib.sha1(image).hexdigest(),originalEntry=original))
 entry_paths[name,seed]=path
 return path

def capture(e,label):
 e.run(8,256)
 for frames in range(0,2101,30):
  e.save(OUT/(label+'.state'));state=(OUT/(label+'.state')).read_bytes();pc=struct.unpack_from('<I',state,0x5c)[0]
  if pc==0x080a8230:break
  if frames<2100:e.run(30)
 check(pc==0x080a8230,(label,'native transaction return not reached',hex(pc)))
 capture_frames[label]=frames+8
 r=e.memory();(OUT/(label+'.ram')).write_bytes(r)
 return r
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
for katana,poise,exposed,seed in itertools.product((False,True),(False,True),(0,1),range(8)):
 pair=[]
 for name,path in (('control',CONTROL),('ward',ROM)):
  e=E(fixed_entry(control if name=='control' else rom,name,seed))
  try:
   e.load(LAB/'game-352/confirmation.state');e.set_memory(0x1e98,b'\x00');e.set_memory(0x3ff48,bytes(4))
   e.set_memory(0x33e4+5,bytes((116,1,116)));e.set_memory(0x33e4+0x3a,bytes((155,154 if poise else 0)))
   e.set_memory(0x33e4+0x18,struct.pack('<4H',500,500,49,49));e.set_memory(0x33e4+0xe8,bytes((8 if poise else 0,))+bytes(7))
   e.set_memory(0x33e4+0x2a,struct.pack('<5H',383 if katana else 0,0,0,0,0));e.set_memory(0x1eb4,bytes((exposed if name=='ward' else 0,)))
   label=f'{int(katana)}-{int(poise)}-{exposed}-{seed}-{name}';r=capture(e,label)
   check(r[0x3ff44:]==bytes(8)+b'\xd7'*0xb4,(label,'root/guard'))
   pair.append(dict(damage=500-half(r,0x33fc),mp=half(r,0x3400),actorHP=half(r,0x98),actorMP=half(r,0x9c),rng=C.string_at(e.maps[0x03000000][0]+0x34b0,4).hex()))
  finally:e.close()
 expected=pair[0]['damage']*(13 if katana else 20)*(3 if poise else 4)*(6 if exposed else 5)//400
 check(pair[1]['damage']==expected,('combined physical damage',katana,poise,exposed,seed,pair,expected))
 check(pair[0]['rng']==pair[1]['rng'],('no extra RNG',pair))
 check(pair[0]['mp']==pair[1]['mp']==49,('incoming MP unaffected',pair))
 check(pair[0]['actorHP']==pair[1]['actorHP'] and pair[0]['actorMP']==pair[1]['actorMP']==44,('attacker costs/HP unchanged',pair))
 outcomes.append(dict(katana=katana,poise=poise,exposed=exposed,seed=seed,control=pair[0],ward=pair[1]))
 print(katana,poise,exposed,seed,pair,flush=True)
check(any(x['katana'] and x['ward']['damage']>0 for x in outcomes),'positive Ward damage case required')
check(any(x['control']['damage']==0 for x in outcomes),'native miss case required')
for poise,seed in itertools.product((False,True),range(8)):
 pair=[]
 for name,path in (('control',CONTROL),('ward',ROM)):
  e=E(fixed_entry(control if name=='control' else rom,name,seed))
  try:
   e.load(LAB/'game-352/confirmation.state');e.set_memory(0xba,bytes((155,154 if poise else 0)));e.set_memory(0x1b4a,b'\xff\xff')
   e.set_memory(0x1e98,b'\x00');e.set_memory(0x168,bytes(8));e.set_memory(0x98,struct.pack('<4H',500,500,50,50));e.set_memory(0x3ff48,bytes(4))
   e.set_memory(0x33e4+5,bytes((16,2,16)));e.set_memory(0x33e4+0x3a,b'\x35');e.set_memory(0x33e4+0x40+53,b'\xff');e.set_memory(0x33e4+0x2a,struct.pack('<5H',460,0,0,0,0))
   label=f'counter-{int(poise)}-{seed}-{name}';r=capture(e,label)
   check(r[0x3ff44:]==bytes(8)+b'\xd7'*0xb4,(label,'root/guard'))
   pair.append(dict(damage=500-half(r,0x98),strike=250-half(r,0x33fc),reaction=r[0xba],mastery=r[0x1b4b],rng=C.string_at(e.maps[0x03000000][0]+0x34b0,4).hex()))
  finally:e.close()
 check(pair[0]['strike']==pair[1]['strike'],('outgoing hit or miss unchanged',pair))
 check(pair[1]['damage']==(pair[0]['damage']*3//4 if poise else pair[0]['damage']),('Counter bypasses Ward but not Poise',pair))
 check(pair[0]['rng']==pair[1]['rng'],('Counter RNG unchanged',pair))
 outcomes.append(dict(counter=True,poise=poise,seed=seed,control=pair[0],ward=pair[1]))
 print('Counter',poise,seed,pair,flush=True)
for poise in (False,True):
 cases=[x for x in outcomes if x.get('counter') and x['poise']==poise]
 check(any(x['control']['strike']>0 for x in cases),'positive outgoing Counter test required')
 check(any(x['control']['strike']==0 for x in cases),'native outgoing miss Counter test required')
 check(any(x['control']['damage']>0 for x in cases),'positive native Counter required')
report=dict(passed=True,romSha1=meta['romSha1'],controlSha1=hashlib.sha1(control).hexdigest(),checks=checks,outcomes=outcomes,instrumented=instrumented,captureFrames=capture_frames,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
