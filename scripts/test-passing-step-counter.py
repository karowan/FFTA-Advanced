"""Native Counter delivery before Passing Step's finishing movement.

Reuses the hash-matched player final-confirmation capture. Native monster
Counter mastery, reaction slot, attack stat and actor HP are declared inputs;
the test never writes a queued reaction, damage, status or outcome.
"""
import collections,ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text());ROM=pathlib.Path(meta['path']);image=ROM.read_bytes()
LAB=ROM.parent;FIX=LAB/'passing-step-playback';OUT=LAB/'passing-step-counter';OUT.mkdir(exist_ok=True)
proof=json.loads((FIX/'report.json').read_text());test=FIX/'playback.gba'
assert proof['passed'] and proof['romSha1']==meta['romSha1']==hashlib.sha1(image).hexdigest()
assert proof['instrumentedSha1']==hashlib.sha1(test.read_bytes()).hexdigest()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
ACTOR,TARGET,LOG=0x5a8,0x33e4,0x3ff50
initial=(FIX/'route-0/final-confirmation.ram').read_bytes()
race=initial[TARGET+6];bank=word(image,word(image,0xcd538)-0x08000000+4*race)-0x08000000
counter=next(i for i in range(1,144) if half(image,bank+8*i+4)==8 and image[bank+8*i+6]==2)
checks=collections.Counter();outcomes=[];case=None
(OUT/'report.json').write_text(json.dumps(dict(passed=False,romSha1=meta['romSha1'])))
def check(k,v):checks[k]+=1;assert v,(k,case)
def snap(e,label,folder):
 r=e.memory();e.save(folder/(label+'.state'));e.screenshot(folder/(label+'.png'));(folder/(label+'.ram')).write_bytes(r)
 (folder/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 check('native-code-intact',C.string_at(*e.maps[0x03000000])[0x6170:0x6d68]==image[0xa38d24:0xa3991c])
 check('action-root-and-log-guards',r[0x3ff44:0x3ff50]==bytes(8)+b'\xd7'*4 and r[0x3fff0:]==b'\xd7'*16)
 return r
for enabled in (False,True):
 for hp in (500,1):
  for seed in (0,3,18):
   case=(enabled,hp,seed);folder=OUT/('-'.join(map(str,case)));folder.mkdir(exist_ok=True);e=E(test)
   try:
    e.load(FIX/'route-0/final-confirmation.state');e.run(1)
    e.set_memory(TARGET+0x3a,bytes((counter if enabled else 0,)));e.set_memory(TARGET+0x40+counter,b'\xff')
    e.set_memory(TARGET+0x20,struct.pack('<H',400));e.set_memory(ACTOR+0x18,struct.pack('<H',hp))
    e.set_memory(LOG+148,struct.pack('<II',1,seed));before=snap(e,'confirmation',folder)
    wrapper=word(before,0xf4ec);executed=None;e.run(8,256)
    for frame in range(3600):
     r=e.memory()
     if word(r,LOG)==0x504c4159 and word(r,LOG+4) and executed is None:
      executed=snap(e,'native-queued-transaction',folder)
     if executed is not None and (word(r,0x3f004)==7 or word(r,0xf4ec) not in (0,wrapper)):
      after=snap(e,'finished',folder);break
     e.run(1)
    else:raise AssertionError('bounded reaction playback timeout')
    check('exactly-one-Passing-Step',word(executed,LOG+4)==1 and word(executed,LOG+8)==409)
    count=word(executed,LOG+16)
    rows=[list(struct.unpack_from('<7I',executed,LOG+20+28*i)) for i in range(min(count,4))]
    reacted=any(row[0]==0 and row[1]==0x02000000+TARGET and row[2]==0x02000000+ACTOR for row in rows[1:])
    check('actual-Counter-queue-matches-equipped-reaction',reacted==enabled)
    check('once-only-six-MP',half(before,ACTOR+0x1c)-half(executed,ACTOR+0x1c)==6)
    # Counter's completed transaction is observed while the actor is still
    # at the origin. Only a living actor can proceed to the selected endpoint.
    check('reaction-resolves-before-movement',executed[ACTOR+0xf6:ACTOR+0xf8]==bytes((0,13)))
    dead=half(after,ACTOR+0x18)==0
    check('KO-cancels-step-survival-permits-step',after[ACTOR+0xf6:ACTOR+0xf8]==bytes((0,13 if dead else 11)))
    if enabled and not dead:check('Counter-delivered-HP-damage',half(after,ACTOR+0x18)<=hp)
    outcomes.append(dict(enabled=enabled,hp=hp,seed=seed,rows=rows,dead=dead,finalHP=half(after,ACTOR+0x18),endpoint=list(after[ACTOR+0xf6:ACTOR+0xf8])))
   except Exception:snap(e,'failure',folder);raise
   finally:e.close()
check('nonvacuous-Counter-KO',any(o['enabled'] and o['dead'] for o in outcomes))
check('nonvacuous-Counter-damage-survival',any(o['enabled'] and 0<o['finalHP']<o['hp'] for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=proof['instrumentedSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
            limits=['Counter covers immediate damage and KO. Reaction-delivered movement statuses and native trap/law cases remain separate.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
