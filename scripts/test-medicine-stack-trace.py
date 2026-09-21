"""Pinned diagnostic: first renderer overwrite with/without result recorder.

Replay one captured initial state, fixed RNG and native Wait inputs. No action,
result, scheduler choice or fixture state is repaired after replay starts.
"""
import ctypes as C,json,pathlib,runpy,struct,hashlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/'build/expansion/probes/integrated-jobs/b26778520203359c3b129bcc025b92dd0e4c01f1/da1702c5df2c0d398a94605a3e57da76ef883405'
matches=list(BASE.glob('medicine-turns-*/383-useful-5/declared-input.state'));assert len(matches)==1
STATE=matches[0];FIX=STATE.parent.parent
OUT=BASE/'medicine-stack-trace-fixed-inputs';OUT.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
original=(BASE/'integrated.gba').read_bytes();assert hashlib.sha1(original).hexdigest()==BASE.name
guard=original[0xa38d24:0xa3991c];outcomes=[]
# Match every original Wait frame and executor seed; only the recorder's
# stack frame differs. The minimal seed stub retires before native execution.
recorded=json.loads((FIX/'report.json').read_text())['fixedInputs'];events=[]
for i in range(0,len(recorded),4):
 group=recorded[i:i+4];start=group[0][1]+572*(i//4)
 for j,offset in enumerate((0,188,376,564)):events.append((start+offset,group[j][2]))
entry=struct.unpack_from('<I',original,0xa4344)[0]
(OUT/'rng.s').write_text(f""".syntax unified
.cpu arm7tdmi
.thumb
.text
.global entry
.thumb_func
entry:
 push {{r0}}
 ldr r0,=0x030034b0
 movs r3,#5
 str r3,[r0]
 pop {{r0}}
 ldr r3,={entry}
 bx r3
.ltorg
""")
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-nostdlib','-Wl,-Ttext=0x093f0000,-e,entry',str(OUT/'rng.s'),'-o',str(OUT/'rng.elf')],check=True,capture_output=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'rng.elf'),str(OUT/'rng.bin')],check=True,capture_output=True)
code=(OUT/'rng.bin').read_bytes();assert original[0x13f0000:0x13f0000+len(code)]==b'\xff'*len(code)
minimal=bytearray(original);minimal[0x13f0000:0x13f0000+len(code)]=code;struct.pack_into('<I',minimal,0xa4344,0x093f0001)
(OUT/'minimal.gba').write_bytes(minimal)
for mode,path in (('recorder',FIX/'playback.gba'),('minimal-RNG-only',OUT/'minimal.gba')):
 e=E(path);inputs=[];frame=0;previous=None;bad=False;folder=OUT/mode;folder.mkdir(exist_ok=True)
 try:
  e.load(STATE)
  n=e.core.retro_serialize_size();saved=C.create_string_buffer(n)
  def step(key=0):
   global frame,previous,bad
   assert e.core.retro_serialize(saved,n);previous=saved.raw
   e.run(1,key);frame+=1
   iw=C.string_at(*e.maps[0x03000000])
   if iw[0x6170:0x6d68]!=guard:
    (folder/'before.state').write_bytes(previous);e.save(folder/'first-overwrite.state')
    (folder/'first-overwrite.iwram').write_bytes(iw);(folder/'first-overwrite.ram').write_bytes(e.memory())
    e.screenshot(folder/'first-overwrite.png');bad=True;return False
   return True
  while frame<12000 and not bad:
   key=next((key for start,key in events if start<=frame<start+8),0)
   if key:inputs.append((frame,key))
   if not step(key):break
  cpu=struct.unpack_from('<17I',previous,32)
  outcomes.append(dict(mode=mode,romSha1=hashlib.sha1(path.read_bytes()).hexdigest(),firstOverwrite=frame if bad else None,
   beforeCPU=[hex(x) for x in cpu],inputs=inputs))
  (OUT/'report.json').write_text(json.dumps(dict(outcomes=outcomes),indent=2))
 finally:e.close()
print(json.dumps(dict(passed=True,diagnostic=True,outcomes=outcomes),indent=2))
