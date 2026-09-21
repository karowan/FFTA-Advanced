"""Reproduce the retained private copy-hook startup/menu failure and sample PCs."""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
source=ROOT/'build/art/live-palette/fades/20260918T082644.751496Z'
raw=(source/'failed.json').read_bytes();retained=json.loads(raw)
assert sha(raw)=='edbd43a7aa3cd991fb65db732fe2a6313f6392fb115d19aa6c147148f39a1de5'
assert retained['romSha1']=='1ee4c46b4c91acd9c6b34dba8d73d2e8096ea175'
meta=json.loads((ROOT/'build/art/live-palette'/retained['romSha1']/'manifest.json').read_text())
path=Path(meta['path']);assert hashlib.sha1(path.read_bytes()).hexdigest()==retained['romSha1']
seed=(ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav').read_bytes();assert hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14'
out=ROOT/'build/art/copy-stall'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(path);rows=[]
def sample(label):
 buffer=C.create_string_buffer(e.core.retro_serialize_size());assert e.core.retro_serialize(buffer,len(buffer))
 assert struct.unpack_from('<I',buffer)[0]==0x0100000b
 rows.append(dict(label=label,registers=list(struct.unpack_from('<16I',buffer,0x20)),cpsr=struct.unpack_from('<I',buffer,0x60)[0]))
try:
 e.set_memory(0,seed,0);e.run(3600);sample('boot')
 for i,row in enumerate(r for r in retained['inputs'] if r[0]=='candidate'):
  if isinstance(row[1],int):e.run(row[1],row[2]);e.run(row[3])
  else:
   assert row[1]=='isolated appearance profile';e.set_memory(0x80+row[2]*264+4,bytes(row[3]))
  sample(str(i))
 assert e.memory()==(source/'candidate-failed.ram').read_bytes()
 assert C.string_at(*e.maps[0x03000000])==(source/'candidate-failed.iwram').read_bytes()
 e.save(out/'reproduced.state')
 report=dict(status='passed',sourceSha256=sha(raw),romSha1=retained['romSha1'],rows=rows,scope='Exact reproduction of retained failure RAM/IWRAM with sampled CPU state. Diagnosis only, not candidate acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',report=str(out/'report.json'),pcs=[hex(r['registers'][15]) for r in rows])))
finally:e.close()
