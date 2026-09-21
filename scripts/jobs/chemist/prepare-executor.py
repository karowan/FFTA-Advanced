"""Capture the real native executor from this candidate's fresh heap/layout."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[3];P=ROOT/'build/expansion/probes'
meta=_load_job_candidate(P/'chemist/current.json');ROM=pathlib.Path(meta['path']);OUT=ROM.parent/'executor';OUT.mkdir(exist_ok=True)
image=bytearray(ROM.read_bytes());assert hashlib.sha1(image).hexdigest()==meta['romSha1']
fixture=ROM.parent/'fixture';assert json.loads((fixture/'report.json').read_text())['romSha1']==meta['romSha1']
# A diagnostic instruction breakpoint observes arguments; it injects no result.
image[0xa433c:0xa433e]=bytes.fromhex('fee7');trap=OUT/'trap.gba';trap.write_bytes(image)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(trap)
try:
 e.load(fixture/'battle-ready.state');e.run(1);e.set_memory(0x33fc,struct.pack('<HH',250,250))
 for key in (256,128,128,128,256,256,256,128,256,256,256):e.run(8,key);e.run(180)
 e.save(OUT/'execute-trap.state');(OUT/'execute-trap.ram').write_bytes(e.memory());(OUT/'execute-trap.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
 regs=struct.unpack_from('<17I',(OUT/'execute-trap.state').read_bytes(),0x20);assert regs[15]==0x080a433e,[hex(x) for x in regs]
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],heapEnd=meta['heapEnd'],files={p.name:hashlib.sha1(p.read_bytes()).hexdigest() for p in OUT.glob('execute-trap.*')})
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
