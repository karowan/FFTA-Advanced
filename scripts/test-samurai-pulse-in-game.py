"""Actual Wait inputs: two fixed wound pulses and native lethal handling."""
import collections,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text())
ROM=pathlib.Path(meta['path']);FIX=ROM.parent/'fixture';OUT=ROM.parent/'wound-pulses';OUT.mkdir(exist_ok=True)
assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==ROM.read_bytes()
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
checks=collections.Counter();results=[];actor=0x398;record=0x1ec2
def check(k,a,b):
 checks[k]+=1
 if isinstance(a,bytes) and isinstance(b,bytes) and a!=b:
  different=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
  raise AssertionError((k,'byte lengths',len(a),len(b),'different bytes',len(different),'first offsets',different[:32]))
 assert a==b,(k,a,b)
def tap(e,key,frames=180):e.run(8,key);e.run(frames)
def active(e):
 b=e.memory();return word(b,word(b,0xf438)-0x02000000+0x18)
def wait(e):
 previous=active(e)
 for key in (32,32,256,256):e.run(8,key);e.run(180)
 for _ in range(900):
  if menu['menu_visible'](e) and active(e)!=previous:return
  e.run(10)
 raise AssertionError(('next menu missing',hex(active(e))))
# Native Wait must preserve all non-audio EWRAM at the same animation phase.
# SoundInit14553C clears0x980 bytes at84E0 (literal1455F4=05000260).
# CgbInit1453F8 initializes four64-byte channels at8EF0. Native1416D4
# returns MusicPlayerInfo F2A0; +0C is its clock and +22 its tempo accumulator.
# Mixer state is cycle-sensitive even with identical emulated button frames.
audio_ranges=((0x84e0,0x8e60),(0x8ef0,0x8ff0),(0xf2ac,0xf2b0),(0xf2c2,0xf2c4))
image=ROM.read_bytes()
check('native_SoundInfo_base',word(image,0x14519c),0x020084e0)
check('native_SoundInfo_clear_size',word(image,0x1455f4),0x05000260)
check('native_CGB_channel_base',word(image,0x1451a0),0x02008ef0)
check('native_music_player_base',word(image,0x1416d8),0x0200f2a0)
def gameplay_memory(memory):
 result=bytearray(memory)
 for start,end in audio_ranges:result[start:end]=bytes(end-start)
 return bytes(result)
ordinary=[]
for path in (ROM.with_name('input.gba'),ROM):
 e=Emulator(path)
 try:
  e.load(FIX/'battle-ready.state');menu['wait_for_menu'](e,limit=9000)
  e.set_memory(0x1e98,bytes(108));wait(e)
  samples=[]
  for delay in range(3):
   if delay:e.run(1)
   samples.append(e.memory());(OUT/f'ordinary-{len(ordinary)}-{delay}.ram').write_bytes(samples[-1]);e.save(OUT/f'ordinary-{len(ordinary)}-{delay}.state')
  ordinary.append(samples)
 finally:e.close()
for samples in ordinary:
 for memory in samples:
  check('ordinary_Wait_sound_signature',word(memory,0x84e0),0x68736d53)
  check('ordinary_Wait_units_persistent_inventory',memory[:0x3c24],ordinary[0][0][:0x3c24])
matches=[(i,j) for i,a in enumerate(ordinary[0]) for j,b in enumerate(ordinary[1]) if gameplay_memory(a)==gameplay_memory(b)]
print('ordinary Wait non-audio RAM frame alignment',matches,flush=True)
check('ordinary_Wait_non_audio_RAM_at_same_animation_phase',bool(matches),True)
for hp,pulse,condition in [(100,11,'plain'),(1,11,'plain'),(100,0,'plain'),(100,11,'protected-exposed'),(100,11,'poison'),(100,11,'ward-poise')]:
 e=Emulator(ROM);d=OUT/f'hp{hp}-pulse{pulse}-{condition}';d.mkdir(exist_ok=True)
 try:
  e.load(FIX/'battle-ready.state');menu['wait_for_menu'](e,limit=9000)
  check('fixture_actor',active(e),0x02000398)
  e.set_memory(actor+0x18,struct.pack('<HH',hp,100));e.set_memory(actor+0xe8,bytes(8))
  e.set_memory(0x1ebc,bytes(72));e.set_memory(record,struct.pack('<H',0x8000|pulse));e.set_memory(0x3ff44,bytes(8));e.set_memory(0x3ff4c,b'\xd7'*0xb4)
  if condition=='protected-exposed':e.set_memory(actor+0xeb,b'\x03');e.set_memory(0x1e9b,b'\x05')
  if condition=='poison':e.set_memory(actor+0xe9,b'\x02')
  if condition=='ward-poise':
   e.set_memory(actor+5,bytes((116,1,116)));e.set_memory(actor+0x35,b'\x74');e.set_memory(actor+0x3a,bytes((155,154)))
   e.set_memory(actor+0x2a,struct.pack('<5H',383,0,0,0,0));e.set_memory(0x1bb0,b'\xff\xff');e.set_memory(actor+0xeb,b'\x03');e.set_memory(0x1e9b,b'\x05')
  e.save(d/'ready.state');wait(e);b=e.memory();first=half(b,actor+0x18)
  check('first_end_turn_HP',first,max(0,hp-pulse));check('first_end_turn_record',half(b,record),(0x4000|pulse) if first else 0)
  check('Poison_status_preserved',b[actor+0xe9]&2,2 if condition=='poison' else 0);check('reserved_RAM_guard',b[0x3ff48:],bytes(4)+b'\xd7'*0xb4)
  if condition=='ward-poise':
   check('Ward_Poise_remain_equipped',b[actor+0x3a:actor+0x3c],bytes((155,154)))
   check('Centered_still_qualifies_Poise_after_first_pulse',b[0x1e9b]&6,2)
  e.save(d/'first.state');e.screenshot(d/'first.png');timeline=[]
  if hp==100 and pulse==11 and condition=='plain':
   expected=b;old=e.memory(0)
   for key in (1,8,16,256,256):tap(e,key)
   tap(e,256,300);saved=e.memory(0);check('suspend_wrote_SRAM',saved!=old,True);(d/'suspended.sav').write_bytes(saved)
   e.close();e=Emulator(ROM);e.set_memory(0,saved,0);e.run(3600)
   for key,frames in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,frames)
   menu['wait_for_menu'](e,limit=9000);b=e.memory()
   check('cold_resume_one_remaining_pulse',half(b,record),0x400b);check('cold_resume_HP',half(b,actor+0x18),89)
   check('cold_resume_AP_inventory',b[0x1940:0x1e70],expected[0x1940:0x1e70]);e.save(d/'cold-resumed.state')
  if first:
   for turn in range(12):
    if active(e)==0x02000398:break
    wait(e);b=e.memory();timeline.append(half(b,actor+0x18))
    check('other_turns_preserve_pulse_count',half(b,record),0x4000|pulse)
    if condition!='poison':check('other_turns_do_not_pulse',half(b,actor+0x18),first)
   check('returns_to_affected_actor',active(e),0x02000398)
   second_before=half(b,actor+0x18)
   if condition=='poison':check('native_Poison_still_ticks',0<second_before<first,True)
   wait(e);b=e.memory();check('second_end_turn_HP',half(b,actor+0x18),max(0,second_before-pulse));check('second_record_retired',half(b,record),0)
   e.save(d/'second.state');e.screenshot(d/'second.png')
  else:
   check('lethal_native_status_cleanup',b[actor+0xe8:actor+0xf0],bytes(8));check('lethal_next_menu',menu['menu_visible'](e),True)
  results.append(dict(initialHP=hp,pulse=pulse,condition=condition,firstHP=first,finalHP=half(b,actor+0x18),betweenTurns=timeline))
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),cases=results,ordinaryWait=dict(frameMatches=matches,excludedAudioRanges=audio_ranges,fullCaptures='ordinary-*.ram/.state'),scope='Actual native Wait and non-audio RAM equivalence at matched animation phase, exactly two end-turn pulses, no pulses on intervening turns, lethal cleanup and return to menu; original-action regression and save/remedy coverage separate')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
