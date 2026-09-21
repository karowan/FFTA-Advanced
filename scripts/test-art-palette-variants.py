"""Native deployment palette identity and compiled simultaneous variant bindings.

Uses retained deployment observations and isolated ARM execution. No game route,
new player fixture or production artwork is created.
"""
import argparse,ast,datetime,hashlib,json,struct,subprocess,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
source=ROOT/'build/art/live-palette/battle/20260918T064034.204059Z/observed.json'
assert sha(source.read_bytes())=='ce58165d3aea82d809f9c17f4c0409c03c63d84fdbb3324a161bd09b4ae00e4c'
proof=json.loads(source.read_text());row=proof['entryPaletteTraces']['candidate']['entry-10']
meta=json.loads((ROOT/'build/art/live-palette/3979dfe594840cedbd8a6f378271f7d610003558/manifest.json').read_text())
rom=bytearray(Path(meta['source']).read_bytes());assert hashlib.sha1(rom).hexdigest()==meta['baseRomSha1']
out=ROOT/'build/art/palette-variants'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'variants.elf';binary=out/'variants.bin'
sources=['src/engine/art-palette-variants.c','src/engine/art-palette-binding.c','src/engine/art-palette-fade.c']
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--native-prefix',action='store_true');args=parser.parse_args()
extra=['-DFFTA_ART_NATIVE_OAM_PREFIX=1'] if args.native_prefix else []
p=subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-Wl,-Ttext=0x09f90000','-Wl,-e,ffta_art_variants_prepare',*extra,*sources,'-o',str(elf)],capture_output=True,text=True,cwd=ROOT)
(out/'compile.log').write_text(p.stdout+p.stderr);p.check_returncode()
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
symbols={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
code=binary.read_bytes();assert len(code)<0x40000 and rom[0x1f90000:0x1f90000+len(code)]==b'\xff'*len(code);rom[0x1f90000:0x1f90000+len(code)]=code
a=ARM(rom,bytes(0x8000));S,B,T,O,M,N,R,C,V,TARGET=0x02010000,0x02011000,0x02012000,0x02012400,0x02012800,0x02013000,0x02013400,0x02013800,0x02014000,0x02015000
checks=[];records=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
def call(name,*args):
 a.put(STACK,struct.pack('<'+'I'*len(args[4:]),*args[4:]));return a.call(symbols[name],*args[:4])
def scale(values,factor):return [sum((((v>>s)&31)*factor//32)<<s for s in (0,5,10)) for v in values]
native=bytes.fromhex(row['nativeShadow'])[512:];normal=list(struct.unpack_from('<16H',rom,0x419d60));dim=struct.unpack_from('<16H',native,9*32)
custom=list(struct.unpack('<16H',(ROOT/'build/art/imagegen/human-dark-knight/march-v2-own-palette/palette.bin').read_bytes()))
refs=[0]*160;refs[16:32]=normal;refs[32:48]=normal
colors=[0]*160;colors[16:32]=custom;colors[32:48]=custom[::-1]
def setup():
 a.put(N,native);a.put(R,struct.pack('<160H',*refs));a.put(C,struct.pack('<160H',*colors));a.put(V,bytes(320))
 a.put(S-4,b'\xd7'*4);a.put(S+20,b'\xe9'*4)
 call('ffta_art_variants_reset',S);call('ffta_art_bindings_reset',B,C)
def prepare(oam,tags,banks):
 a.put(O,oam);a.put(T,tags);a.put(M,struct.pack('<10H',*banks))
 return call('ffta_art_variants_prepare',S,B,T,O,M,N,R,C,V)
def snapshot():return a.read(S,20),a.read(B,2852),a.read(T,128),a.read(V,320)
try:
 a.put(0x020037c2,b'\0')
 check(a.read(a.call(0x080cba3c,0),32)==bytes(native[:32]),'Native normal getter matches actual deployment bank0')
 a.put(TARGET,native[:32]);a.call(0x08148104,TARGET,TARGET+256,16,0x99)
 check(a.read(TARGET+256,32)==native[9*32:10*32],'Original deployment multiplier148104 matches actual bank9')
 probes=[value<<shift for shift in (0,5,10) for value in range(32)]
 a.put(TARGET,struct.pack('<96H',*probes));a.call(0x08148104,TARGET,TARGET+256,96,0x99)
 check(a.read(TARGET+256,192)==struct.pack('<96H',*scale(probes,19)),'Original153/256 transform equals19/32 for every native channel value')
 check(scale(normal,19)==list(dim),'All original deployment-dim colors exactly match19/32 channel scaling')
 check(row['refusals']['variants']>0 and row['refusals']['setup']==row['refusals']['target']==row['refusals']['tick']==0,'Retained refusal was simultaneous native-bank demand')
 setup();objects=bytes.fromhex(row['oam']);tags=bytes.fromhex(row['tags']);banks=[0]*10;banks[1]=1
 single=bytearray(tags);single[9]=255
 check(prepare(objects,single,banks)==2,'Normal class retains preferred identity slot1')
 if args.native_prefix:
  stable=snapshot();check(prepare(objects,single,banks)==2 and snapshot()==stable,'Existing identity preserves complete binding/history/tag/visible state')
  a.put(S+9,b'\xc8');corrupt=snapshot()
  check(prepare(objects,single,banks)==0 and snapshot()==corrupt,'Corrupt dormant owner refuses before identity shortcut')
  a.put(S+9,b'\xff')
 before=a.read(B+252,252);banks[1]|=1<<9
 check(prepare(objects,tags,banks)==3,'Simultaneous normal/dim class receives two slots')
 check(a.read(S,20)==bytes([25,16]+[255]*8+[19,32]+[0]*8),'Exact stable key/scale assignments')
 check(a.read(B+252,252)==before,'Adding preview preserves existing normal binding')
 check(a.word(B+248)==9 and a.word(B+252+248)==0,'Distinct original bank ownership preserved')
 check(a.read(T,128)==bytes(0 if i==9 else 1 if i==43 else 255 for i in range(128)),'Only authenticated preview tag split from normal class')
 check(a.read(V,32)==struct.pack('<16H',*scale(custom,19)) and a.read(V+32,32)==struct.pack('<16H',*custom),'Both generated palettes use their correct source class and brightness')
 check(a.read(O,1024)==objects and a.read(N,512)==native,'No native OAM or native colors changed by binding preparation')
 stable=snapshot();prepare(objects,tags,banks);check(snapshot()==stable,'Repeated variant frame preserves exact bindings and visible colors')
 for name,kind,target in [('black',1,0),('restore dim baseline',3,N+9*32)]:
  call('ffta_art_binding_start_mapped',B,400,415,3,0x1234,kind,target,C,S)
  expected=bytes(32) if kind==1 else struct.pack('<16H',*scale(custom,19))
  check(a.read(B+32,32)==expected,name+' constructs correct per-variant target')
  for remaining in (3,2,1):call('ffta_art_binding_tick',B,0x1234,remaining,remaining-1,int(remaining>1),0)
  check(a.read(B,32)==expected and a.read(B+252,32)==struct.pack('<16H',*custom),name+' changes preview while preserving normal copy')
 check(a.read(S-4,4)==b'\xd7'*4 and a.read(S+20,4)==b'\xe9'*4,'Mapping remains within20 bytes')
 # Unknown new native variants and capacity overflow must fail atomically.
 for label,mask,native_override in [('unknown palette',1<<4,None),('eleven simultaneous pairs',(1<<11)-1,bytes(native[:32])*16)]:
  setup()
  if native_override:a.put(N,native_override)
  a.put(T,tags);saved=snapshot();banks=[0]*10;banks[1]=mask
  check(prepare(objects,tags,banks)==0 and snapshot()==saved,label+' refuses before all state/color/tag writes')
 # Two distinct classes may share a native bank but require distinct artwork.
 setup();two=bytearray(objects);twotags=bytearray([255]*128);twotags[9]=1;twotags[43]=2
 struct.pack_into('<H',two,9*8+4,struct.unpack_from('<H',two,9*8+4)[0]&0xfff)
 banks=[0]*10;banks[1]=banks[2]=1
 check(prepare(two,twotags,banks)==6,'Two classes sharing native bank receive independent generated slots')
 check(a.read(V+32,64)==struct.pack('<32H',*custom,*custom[::-1]),'Source class identity survives shared native bank')
 report=dict(status='passed',checks=checks,source=str(source),sourceSha256=sha(source.read_bytes()),romSha1=meta['baseRomSha1'],compiledSha256=sha(code),sources={f:sha((ROOT/f).read_bytes()) for f in sources},scope='Native normal getter and actual148104 deployment multiplier identity, all channel values, compiled variant grouping/brightness, stable bindings, independent fades/restoration, atomic refusal and shared-native-bank class separation. Does not prove installed hooks, live deployment, color reload/late entry, all color modes or final artwork.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print(out);raise
