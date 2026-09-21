"""Complete native law selector and Guarding Draw self-Protect prediction."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=json.loads((P/'samurai/current.json').read_text());OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();symbols=meta['symbols'];assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=P/'samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000;TARGET=0x020033e4;LAW=0x0203e000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
native,expanded=ARM(base,iw),ARM(rom,iw);counts=collections.Counter()
def check(kind,a,b):
 counts[kind]+=1;assert a==b,(kind,(a,b) if not isinstance(a,bytes) else [(hex(i),x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y][:15])
def reset(m,status=-1):
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x02001e98,bytes(36));m.put(UNIT+5,bytes([116,1,116]));m.put(UNIT+0x3a,bytes(2))
 m.put(UNIT+0x2a,struct.pack('<5H',376,460,0,0,0));m.put(UNIT+0x18,struct.pack('<HHHH',100,100,50,50));m.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
 m.put(TARGET+0xe8,bytes(8));m.put(TARGET+0x18,struct.pack('<HH',250,250))
def live(m):return m.read(0x02000000,0x1940)+m.read(0x02001e98,36)+m.read(0x02002fc4,12*264)
def law(m,action,kind,value,status=-1,residue=0):
 reset(m,status);m.put(LAW,bytes([0,0,0,0,kind,value,0,0,0,0,0,0]));sp=STACK+residue;m.put(sp,struct.pack('<4I',0,376,0,LAW));before=live(m)
 out=m.call(0x081343c8,UNIT,TARGET,action,0,stack=sp)
 check('law_live_isolation',live(m),before)
 return out,m.read(0x02000000,0x40000)
for action,kind in itertools.product(range(347),range(1,21)):
 a,ar=law(native,action,kind,25);b,br=law(expanded,action,kind,25)
 check('original_law_result',b,a);check('original_law_complete_memory',br,ar)
for action,kind,value,residue in itertools.product((347,348,349,352,353),(2,10,15),(1,2,9,25),(0,4)):
 result,_=law(expanded,action,kind,value,residue=residue)
 expected=int(kind==10 and value==9 or kind==15 and value==25 and action==352 or kind==2 and value==2 and action==348)
 check('samurai_element_weapon_self_status',result,expected)
# Every native actor status: prediction and the actual granted Protect use the
# same native admission. Petrify/KO are rejected by the native outer law gate.
for status,value,residue in itertools.product(range(-1,44),range(44),(0,4)):
 reset(expanded,status);before=expanded.read(UNIT,264)
 expanded.call(symbols['ffta_samurai_after_attempt'],UNIT,352,1,stack=STACK+residue)
 after=expanded.read(UNIT,264);granted=bool(after[0xeb]&2) and after[0xde]==3
 # Confusion rejects a direct custom strike; Charm reverses allegiance and
 # makes this enemy fixture friendly. Neither reaches an admitted attempt.
 expected=int(value==25 and granted and status not in (6,28,29))
 result,_=law(expanded,352,15,value,status,residue)
 check('guarding_law_matches_native_protect_admission',(status,value,residue,result),(status,value,residue,expected))
# Native Protect's removal mask is an independent oracle for self-status
# removals. The enemy has none of those statuses: its native removal precheck
# must not hide the actor's Invisible removal. Caller-owned copies stay local.
for status,queried,residue in itertools.product(range(-1,44),range(44),(0,4)):
 reset(native,status);before=native.read(UNIT,264)
 context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,TARGET,UNIT,UNIT,9,0);struct.pack_into('<I',context,0x30,0x08553e70+78*4);native.put(0x0200f3f0,context)
 native.call(0x0813388c,stack=STACK+residue);after=native.read(UNIT,264)
 mask=1<<(queried&7);offset=0xe8+(queried>>3)
 expected=int(bool(before[offset]&mask) and not after[offset]&mask and status not in (28,29))
 reset(expanded,status);ca,ct=0x02022000,0x02022200;expanded.put(ca,expanded.read(UNIT,264));expanded.put(ct,expanded.read(TARGET,264));live_before=live(expanded)
 sp=STACK+residue;expanded.put(sp,struct.pack('<II',queried,1))
 value=expanded.call(0x081342cc,ca,ct,352,376,stack=sp)
 check('guarding_self_removal_native_mask',(status,queried,value),(status,queried,expected));check('self_removal_live_isolation',live(expanded),live_before)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),scope='All347 native actions across20 law kinds; Samurai primary-only/non-elemental laws; Guarding Draw44 native actor statuses and status queries; native Protect self-removal mask; live sources unchanged')
(OUT/'law-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
