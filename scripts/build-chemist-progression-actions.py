"""Install command records in the isolated integration probe.

This is deliberately not a release builder. Tile movement, delayed execution,
UI presentation and combined acceptance are separate required gates. The
original 446 actions and 237 descriptors retain their bytes and addresses;
only the reserved tails and the explicit application observers are changed.
"""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
 parent=Path(json.loads((ROOT/'build/expansion/chemist-progressions/probes/current.json').read_text())['manifest'])
 meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
 assert hashlib.sha1(original).hexdigest()==meta['romSha1']
 rom=bytearray(original);sy=meta['symbols'];patches=[]
 integrated=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
 t=integrated['tables'];actions,desc,apps,masks=[t[n] for n in ('actions','descriptors','applications','masks')]
 def put(at,b,label):
  before=bytes(rom[at:at+len(b)]);rom[at:at+len(b)]=b
  patches.append(dict(offset=at,before=before.hex(),after=b.hex(),label=label))
 def new(at,b,label):
  assert original[at:at+len(b)]==b'\xff'*len(b),(label,hex(at))
  put(at,b,label)
 # All sure custom applications reuse native eligibility slot8 and accuracy
 # slot23. Flash gets ordinary status accuracy through a separate descriptor.
 assert original[desc+63*4:desc+64*4]==bytes((8,21,10,30))
 new(desc+237*4,bytes((8,112,23,0)),'custom state descriptor')
 new(apps+112*12,struct.pack('<III',sy['ffta_cp_application_observer_entry']|1,0,255),'custom state application and actual-cure observer')
 new(masks+112*12,bytes([0x55]*11+[0]),'custom state native mask')
 # The old Chemist used the native half-max revival directly. Its C wrapper
 # was linked but was not selected by slot41, so changing only that wrapper
 # silently leaves Rescue Team at50%. Preserve that formula for all old IDs.
 revive=0x3a86f8+41*4
 assert struct.unpack_from('<I',original,revive)[0]==0x08131a61
 put(revive,struct.pack('<I',sy['ffta_chemist_revive_entry']|1),'revival magnitude dispatcher')
 # Descriptor87 is the same native Blind component used by Forbidden Dance.
 # Its application is a dedicated native function, not a status-ID argument.
 blind_template=bytes(original[desc+87*4:desc+88*4])
 assert blind_template==bytes((8,35,21,0)),blind_template.hex()
 blind=[35]
 new(desc+238*4,bytes((8,blind[0],blind_template[2],blind_template[3])),'Flash ordinary Blind roll')
 # IDs, donors, MP, range, cross, element, power, descriptor vector.
 rows=[
 (446,1,8,2,False,0,0,[223,1,1,1]),
 (447,12,10,3,False,0,0,[237,1,1,1]),
 (448,12,12,3,False,0,0,[237,1,1,1]),
 (449,1,12,3,False,0,0,[223,227,1,1]),
 (450,256,24,2,True,0,0,[210,1,1,1]),
 (451,1,18,2,True,0,0,[223,1,1,1]),
 (452,12,20,3,False,0,0,[237,1,1,1]),
 (453,23,9,3,False,1,40,[63,1,1,1]),
 (454,23,12,3,True,6,24,[63,238,1,1]),
 (455,23,9,3,False,0,40,[63,237,1,1]),
 (456,12,8,3,False,0,0,[237,1,1,1]),
 (457,12,12,3,True,0,0,[237,1,1,1]),
 (458,12,8,2,False,0,0,[237,1,1,1]),
 (459,23,13,3,False,1,24,[63,237,1,1]),
 (460,1,0,0,False,0,0,[223,237,1,1]),
 (461,1,0,0,False,0,0,[223,237,1,1]),
 (462,1,0,0,False,0,0,[223,237,1,1]),
 (463,23,0,0,True,1,40,[63,1,1,1]),
 (464,23,0,0,False,6,40,[63,104,1,1])]
 for ident,donor,cost,radius,area,element,power,vector in rows:
  row=bytearray(original[actions+28*donor:actions+28*(donor+1)])
  name=896+(ident-446) if ident<=452 else 906+(ident-453) if ident<=459 else {460:897,461:903,462:904,463:912,464:909}[ident]
  struct.pack_into('<H',row,0,name);struct.pack_into('<H',row,22,0)
  row[2]=element;row[4]=cost;row[5]=0;row[6]=radius;row[7]=2
  row[8]=3 if ident>=460 else 1;row[9]=5 if area else 1;row[10]=2 if area else 0
  row[11]=power;row[12:16]=bytes(vector);row[25]=int(ident<460)
  flags=struct.unpack_from('<I',row,16)[0]&~sum(1<<b for b in (7,8,9,15,17))
  flags|=1<<9
  if power:flags|=1<<17
  struct.pack_into('<I',row,16,flags)
  new(actions+28*ident,row,'action '+str(ident))
 # Observe actual cures, including old commands, behind their unchanged
 # callbacks. The compiler captured the original pointers before this stage.
 for i in range(112):
  if struct.unpack_from('<I',original,apps+i*12)[0]:
   put(apps+i*12,struct.pack('<I',sy['ffta_cp_application_observer_entry']|1),'cure observer '+str(i))
 assert rom[actions:actions+446*28]==original[actions:actions+446*28]
 assert rom[desc:desc+237*4]==original[desc:desc+237*4]
 allowed={n for p in patches for n in range(p['offset'],p['offset']+len(bytes.fromhex(p['after'])))}
 assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
 digest=hashlib.sha1(rom).hexdigest();out=ROOT/'build/expansion/chemist-progressions/actions'/digest;out.mkdir(parents=True,exist_ok=True)
 path=out/'INCOMPLETE_TEST_ONLY.gba';path.write_bytes(rom)
 result=dict(status='INCOMPLETE action integration probe; not release eligible',path=str(path),romSha1=digest,parent=str(parent),
  symbols=sy,tables=t,patches=patches,blindApplication=blind[0],blindTemplate=blind_template.hex(),
  unresolved=['Tripwire native movement trigger and marker','Springboard native route selection','Timed Fuse delayed action playback','Combined UI AI laws and save acceptance'])
 manifest=out/'manifest.json';manifest.write_text(json.dumps(result,indent=2)+'\n')
 (out.parent/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
 print(json.dumps(dict(romSha1=digest,manifest=str(manifest),actions=len(rows))))

if __name__=='__main__':main()
