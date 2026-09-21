"""Native empty-center ownership guards and transparent original-call ABI."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer-arts.py';ns={'__file__':str(source),'__name__':'selection_fixture'}
exec(compile(source.read_text().split('\nfor action,seed in itertools.product')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,reset,wrappers=(ns[k] for k in ('m','S','meta','OUT','A','T','STACK','reset','wrappers'))
checks=collections.Counter();case=None;SEL=0x02028800
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,case)
def setup(action,mode=6,owner=True,wrapper_owner=True,listed=True,count=1,stage=0):
 reset(action);manager=m.word(0x0200f438)
 m.put(manager+4,bytes((mode,)));m.put(manager+24,struct.pack('<I',A if owner else T))
 m.put(0x0200f4ec,struct.pack('<I',wrappers[A] if wrapper_owner else wrappers[T]))
 m.put(SEL,bytes(0x180));m.put(SEL,struct.pack('<I',wrappers[A]))
 m.put(SEL+0xec,struct.pack('<H',action));m.put(SEL+0xf6,bytes((stage,)))
 m.put(SEL+0x109,bytes((7,14)));m.put(SEL+0x110,struct.pack('<H',count))
 m.put(SEL+0x112,bytes((7 if listed else 6,14,16,0)))

# Every original action, both legal stack alignments, and a normal external
# caller must preserve the native helper's return, RAM effects and RNG.
for action,sp in itertools.product(range(347),(STACK,STACK+4)):
 case=('native-center-transparency',action,sp);results=[]
 for entry in (S['ffta_geo_original_center'],0x080b5920):
  setup(action);m.put(sp,struct.pack('<I',action))
  value=m.call(entry,wrappers[A],5,14,0,stack=sp)
  results.append((value,m.read(0x02000000,0x40000),m.read(0x030034b0,4)))
 check('original-action-return-RAM-RNG',results[1],results[0])

for action,caller,mode,stage,sp in itertools.product((380,382),(0x080b780f,0x080b76b3),(6,11),(0,1),(STACK,STACK+4)):
 case=('legal-empty-center',action,caller,mode,stage,sp);setup(action,mode=mode,stage=stage)
 m.put(sp,struct.pack('<I',action));native=m.call(S['ffta_geo_original_center'],wrappers[A],7,14,0,stack=sp)
 check('independent-native-empty-rejection',native,0)
 setup(action,mode=mode,stage=stage)
 m.put(sp,struct.pack('<III',action,SEL,caller));before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 check('legal-field-center-accepted',m.call(S['ffta_geo_center'],wrappers[A],7,14,0,stack=sp),1)
 check('center-query-no-RAM-writes',m.read(0x02000000,0x40000),before)
 check('center-query-no-RNG',m.read(0x030034b0,4),rng)

variants=('wrong-caller','before-selection','after-selection','wrong-owner','wrong-wrapper',
          'unlisted-tile','oversized-list','late-stage','null-selection','wrong-action','wrong-cursor','void-tile')
for action,variant,sp in itertools.product((380,382),variants,(STACK,STACK+4)):
 case=('rejected-placement-override',action,variant,sp);setup(action)
 caller=0x080b780f;selection=SEL;manager=m.word(0x0200f438)
 if variant=='wrong-caller':caller=0x080b780d
 if variant=='before-selection':m.put(manager+4,b'\x05')
 if variant=='after-selection':m.put(manager+4,b'\x0c')
 if variant=='wrong-owner':m.put(manager+24,struct.pack('<I',T))
 if variant=='wrong-wrapper':m.put(0x0200f4ec,struct.pack('<I',wrappers[T]))
 if variant=='unlisted-tile':m.put(SEL+0x112,b'\x06')
 if variant=='oversized-list':m.put(SEL+0x110,struct.pack('<H',26))
 if variant=='late-stage':m.put(SEL+0xf6,b'\x02')
 if variant=='null-selection':selection=0
 if variant=='wrong-action':m.put(SEL+0xec,struct.pack('<H',374))
 if variant=='wrong-cursor':m.put(SEL+0x109,b'\x06')
 if variant=='void-tile':m.put(ns['GRID']+2*(14*16+7),b'\x00')
 m.put(sp,struct.pack('<III',action,selection,caller))
 before=m.read(0x02000000,0x40000);iw=m.read(0x03000000,0x8000)
 native=m.call(S['ffta_geo_original_center'],wrappers[A],7,14,0,stack=sp)
 wanted=(native,m.read(0x02000000,0x40000),m.read(0x030034b0,4))
 m.put(0x02000000,before);m.put(0x03000000,iw)
 result=m.call(S['ffta_geo_center'],wrappers[A],7,14,0,stack=sp)
 check('invalid-override-retains-native', (result,m.read(0x02000000,0x40000),m.read(0x030034b0,4)),wanted)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),
 scope='Native helper transparency and owned legal-list override; actual empty casts are in geomancer-playback.')
(OUT/'geomancer-selection.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
