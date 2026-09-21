"""Fixed Higanbana replay stopped at the first native law query after confirmation."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;OUT=LAB/'law-trace';OUT.mkdir(exist_ok=True)
rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
proof=json.loads((LAB/'higanbana-game/report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
trial=bytearray(rom);assert trial[0x1343c8:0x1343ca]==b'\xf0\xb5';trial[0x1343c8:0x1343ca]=b'\xfe\xe7';path=OUT/'law-entry.gba';path.write_bytes(trial)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];outcomes=[]
for seed in (0,1):
 e=Emulator(path)
 try:
  e.load(LAB/'higanbana-game/confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4);e.run(8,256);e.run(3000)
  state=OUT/f'entry-{seed}.state';e.save(state);b=state.read_bytes();r=e.memory();iw=C.string_at(*e.maps[0x03000000]);regs=struct.unpack_from('<17I',b,0x20)
  def read(p,n):
   if 0x02000000<=p<=0x02040000-n:return r[p-0x02000000:p-0x02000000+n]
   if 0x03000000<=p<=0x03008000-n:return iw[p-0x03000000:p-0x03000000+n]
   if 0x08000000<=p<=0x08000000+len(rom)-n:return rom[p-0x08000000:p-0x08000000+n]
   raise AssertionError(('pointer',hex(p),n))
  assert regs[15]==0x081343ca,hex(regs[15]);args=list(regs[:4])+list(struct.unpack('<4I',read(regs[13],16)))
  outcomes.append(dict(seed=seed,PC=hex(regs[15]),LR=hex(regs[14]),args=[hex(x) for x in args],law=read(args[7],16).hex(),nativeStatusMask=read(args[6],8).hex() if args[6] else None,executionRoot=hex(struct.unpack_from('<I',r,0x3ff44)[0]),wound=hex(struct.unpack_from('<H',r,0x1ef4)[0]),targetHP=struct.unpack_from('<H',r,0x33fc)[0]))
  (OUT/f'entry-{seed}.ram').write_bytes(r);(OUT/f'entry-{seed}.iwram').write_bytes(iw)
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],scope='Diagnostic breakpoint evidence, not acceptance of custom harmful-status law handling',outcomes=outcomes)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
