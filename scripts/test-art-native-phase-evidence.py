"""Authenticate live phase differences against original native color rotations.

Consumes complete retained traces; does not replay navigation or realign frames.
Only the original compiled native rotation callbacks run on a detached clone.
"""
import ast, datetime, hashlib, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text(encoding='utf-8').replace('count=50000','count=500000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
TRACE=ROOT/'build/art/native-frame-events/20260918T200701.275078Z/report.json'
SEED=ROOT/'build/art/live-palette/battle/20260918T183919.610099Z'
META=ROOT/'build/art/connected/4a7d55ce09cd4a40965a0bb97de2701d276789c5/live-palette-view.json'
# An explicit current trace remains pinned independently of mutable indexes.
trace_pin='5580a5e1652576ff9324e8b14b7e364016b0dad7b1fe52dd5cadb8d2135a5bd0'
if '--trace' in sys.argv:
 TRACE=ROOT/sys.argv[sys.argv.index('--trace')+1]
 trace_pin=sys.argv[sys.argv.index('--trace-sha256')+1]
 META=ROOT/sys.argv[sys.argv.index('--manifest')+1]
 retained=json.loads(TRACE.read_text(encoding='utf-8'))
 SEED=Path(retained['source'])
out=ROOT/'build/art/native-phase-evidence'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 check(sha(TRACE.read_bytes())==trace_pin,'Authenticated entire event report')
 report=json.loads(TRACE.read_text(encoding='utf-8'));meta=json.loads(META.read_text(encoding='utf-8'))
 rom=Path(meta['path']).read_bytes()
 check(report['status']=='passed' and report['romSha1']==meta['romSha1']==hashlib.sha1(rom).hexdigest(),'Exact traced and cloned ROM')
 ram=(SEED/'candidate-ready.ram').read_bytes();iw=(SEED/'candidate-ready.iwram').read_bytes()
 check(sha(META.read_bytes())==report['manifestSha256'],'Authenticated traced manifest')
 check(sha(ram)==report['inputHashes']['candidate-ready.ram'] and
       sha(iw)==report['inputHashes']['candidate-ready.iwram'],'Authenticated original detached state')
 native=bytearray(rom)
 patch=next(p for p in meta['changes'] if p['offset']==0x146864)
 check(native[patch['offset']:patch['offset']+patch['bytes']].hex()==patch['after'],'Installed rotation entry authenticated')
 native[patch['offset']:patch['offset']+patch['bytes']]=bytes.fromhex(patch['before'])
 a=ARM(native,iw);a.put(0x02000000,ram)
 initial=iw[0x3860:0x3c60];phases=[]
 for tick in range(64):
  row=a.read(0x03003860,1024)
  if row not in phases:phases.append(row)
  check(row[:324]+row[352:]==initial[:324]+initial[352:],'Native callback confines changes to the two seven-color ranges '+str(tick))
  for task in (0x03003c7c,0x03003cb4):
   a.call(0x08146864,task)
 check(len(phases)==7,'Original native callbacks independently produce seven complete shadow phases')
 backgrounds=[p[:512] for p in phases]
 for record in report['records']:
  for action,data in record['actions'].items():
   label=record['case']+'/'+str(record['idleFramesBeforeMove'])+'/'+action
   events=data['events'];decisions=[e for e in events if e['site']=='vblank-flag-check']
   starts=[e for e in events if e['site']=='compose'];ends=[e for e in events if e['site']=='compose-return']
   displays=[e for e in events if e['site']=='vblank-display-return']
   control=next(x for x in report['records'] if x['case']=='bypass' and
                x['idleFramesBeforeMove']==record['idleFramesBeforeMove'])
   control_starts=[e for e in control['actions'][action]['events'] if e['site']=='compose']
   check(len(decisions)==len(starts)==len(ends)==len(displays)==128,label+' complete observed boundaries')
   indices=[]
   for index,(decision,before,after,display) in enumerate(zip(decisions,starts,ends,displays)):
    shadow=bytes.fromhex(before['memory']['shadow']);pre=bytes.fromhex(before['memory']['palette']);post=bytes.fromhex(after['memory']['palette'])
    prefix=label+'/'+str(index)
    check(shadow[:512] in backgrounds,prefix+' exact entire background shadow is an independently generated native phase')
    indices.append(backgrounds.index(shadow[:512]))
    check(shadow[512:]==bytes.fromhex(control_starts[index]['memory']['shadow'])[512:],
          prefix+' entire native object shadow matches paired same-input control after navigation')
    check(shadow==bytes.fromhex(after['memory']['shadow']),prefix+' native shadow unchanged across actual compositor')
    check(pre[:512]==post[:512],prefix+' all background hardware colors unchanged across actual compositor')
    expected=bytes.fromhex(decision['memory']['palette'])[:512] if decision['frameFlag'] else shadow[:512]
    check(pre[:512]==expected,prefix+' native DMA decision determines actual displayed phase')
    check(160<=before['scanline']<=after['scanline']<=display['scanline']<228,prefix+' composition and actual display return stay inside VBlank')
   records.append(dict(case=record['case'],idle=record['idleFramesBeforeMove'],action=action,phases=indices,
                       maxDisplayLine=max(e['scanline'] for e in displays),motion=data['motion']))
 differences=[]
 for idle in (0,4):
  for action in ('move','cancel'):
   active=next(x for x in records if x['case']=='active' and x['idle']==idle and x['action']==action)
   control=next(x for x in records if x['case']=='bypass' and x['idle']==idle and x['action']==action)
   mismatch=[i for i,(x,y) in enumerate(zip(active['phases'],control['phases'])) if x!=y]
   # A successful timing change may make these phases identical. Presence of
   # a mismatch was a property of the original diagnostic, not an invariant.
   # Preserve the exact comparison, including an empty difference list.
   check(len(active['phases'])==len(control['phases'])==128,'Complete raw paired phase comparison retained '+str((idle,action)))
   differences.append(dict(idle=idle,action=action,mismatchingFrames=mismatch))
 result=dict(status='passed',checks=checks,romSha1=meta['romSha1'],trace=str(TRACE),traceSha256=sha(TRACE.read_bytes()),
   source=str(SEED),sourceHashes=dict(ram=sha(ram),iwram=sha(iw)),nativeRotationPatch=patch,
   originalNativePhases=[p.hex() for p in phases],records=records,rawPairedDifferences=differences,
   scope='Bounded live Move/cancel color-phase reconciliation on the exact current mixed battle. Entire actual BG shadows match independently executed original native rotations; entire native OBJ shadows match the paired same-input control after navigation. Compositor preserves complete shadow and all BG hardware colors at every observed boundary; fresh/skipped DMA and VBlank timing checked. Raw mismatching timelines retained, not shifted. No claim of zero response overhead, all effect consumers, maximum capacity, other candidates or final art.')
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,records=records),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
