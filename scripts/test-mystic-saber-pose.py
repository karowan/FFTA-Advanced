"""Scoped Viera saber pose versus native rapier; no gameplay item substitution."""
import pathlib,itertools
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-axe-visuals.py';ns={'__file__':str(source),'__name__':'saber_pose_fixture'}
support=source.read_text(encoding='utf-8').split('types=list(range(256))')[0]
first=support.index("meta=json.loads((OUT/'axe-visual.json')")
last=support.index('tree=ast.parse',first)
support=support[:first]+'''meta=json.loads((OUT/'integrated-jobs/current.json').read_text())
probe=pathlib.Path(meta['path']).read_bytes();assert hashlib.sha1(probe).hexdigest()==meta['romSha1']
OUT=pathlib.Path(meta['path']).parent
base=bytearray(probe);clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
base[0x986da:0x986e6]=clean[0x986da:0x986e6];base=bytes(base)
meta['poseControlSha1']=hashlib.sha1(base).hexdigest()
''' +support[last:]
exec(compile(support,str(source),'exec'),ns)
native,expanded,segment,check,STATE,meta,OUT=(ns[k] for k in ('native','expanded','segment','check','STATE','meta','OUT'))

# Every racial/job identity proves the exception is limited to Viera125.
for race,job,residue in itertools.product(range(24),range(126),(0,4)):
 data=bytearray(264);data[6]=race;data[5]=job
 values={0:0,4:0,5:3,6:STATE,7:35,8:2,9:0,10:7}
 original=dict(values);original[5]=8 if (race,job)==(4,125) else 3
 a=segment(native,0x080986da,{0x080988a4},original,residue,unitdata=data)
 b=segment(expanded,0x080986da,{0x080988a4},values,residue,unitdata=data)
 for key in ('regs','flags','frame','state'):
  check('saber-pose-scope-'+key,(race,job,residue),a[key]==b[key],(a[key],b[key]) if a[key]!=b[key] else None)

# Native actor-animation modes and facing retain the real item's graphical
# properties while selecting the supported case. Test all original/new sabers.
items=[i for i in range(1,461) if expanded.call(0x080ca7a4,i,3)==3]
for item,mode,facing,residue in itertools.product(items,range(6,18),range(4),(0,4)):
 data=bytearray(264);data[6]=4;data[5]=125
 values={0:0,4:0,5:3,6:STATE,7:item,8:facing,9:expanded.call(0x080ca7a4,item,8),10:mode}
 original=dict(values);original[5]=8
 a=segment(native,0x080986da,{0x080988a4},original,residue,unitdata=data)
 b=segment(expanded,0x080986da,{0x080988a4},values,residue,unitdata=data)
 for key in ('regs','flags','frame','state'):
  check('saber-native-pose-'+key,(item,mode,facing,residue),a[key]==b[key],(a[key],b[key]) if a[key]!=b[key] else None)
report=dict(passed=not ns['failures'],romSha1=meta['romSha1'],poseControlSha1=meta['poseControlSha1'],
 checks=ns['checks'],total=sum(ns['checks'].values()),failures=ns['failures'],sabers=items,
 limits=['Native pose-selection ABI; actual rendered casts and cold resume are separate.'])
(OUT/'mystic-saber-pose.json').write_text(ns['json'].dumps(report,indent=2),encoding='utf-8')
print(ns['json'].dumps({**report,'failures':report['failures'][:10]},indent=2));assert report['passed']
