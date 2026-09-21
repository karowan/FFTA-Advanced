"""Colors1..15 damage flash and native restoration, independent native oracle."""
import argparse, ast, datetime, hashlib, itertools, json, struct, sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
code=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000')
code=code.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(code);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/connected/current.json').read_text());live=meta['components']['livePalette']
rom=Path(meta['path']).read_bytes();original=Path(live['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(original).hexdigest()==live['baseRomSha1']
source=ROOT/'build/art/connected/casting/20260918T205730.189020Z'
iw=(source/'371-active-ready.iwram').read_bytes();ram=(source/'371-active-ready.ram').read_bytes()
BASE,LIMIT=live['ramReservation'];B=BASE+live['bindingOffset'];V=BASE+live['variantOffset'];PAL=0x03003be0;TEMP=0x02028000
out=ROOT/'build/art/connected/damage-native'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--additional-operations',action='store_true');parser.add_argument('--boundaries-only',action='store_true');args=parser.parse_args()
checks=[];case='setup'
def check(ok,label):
    assert ok,(case,label)
    checks.append(case+'/'+label)
def machine(data):
    a=ARM(data,iw);a.put(0x02000000,ram)
    if data==rom:
        a.put(BASE,bytes(4));a.call(live['symbols']['ffta_art_heap_reset'])
    return a
def call(a,pc,*args,residue=0):
    a.put(STACK+residue,struct.pack('<'+'I'*len(args[4:]),*args[4:]));return a.call(pc,*args[:4],stack=STACK+residue)
def native(a):return a.read(0x03003860,0x1e09)
def outside(a):return a.read(0x02000000,BASE-0x02000000)+a.read(LIMIT,0x02040000-LIMIT)
operations=[('blend',0x08147d94,(0x318,8,8))]
if args.additional_operations:
    operations=[('black',0x08147a7c,()),('white',0x08147ad0,()),('gray',0x08147b28,()),
        ('tint',0x08147ba4,()),('rgb',0x08147c2c,(128,320,192)),('solid',0x08147cc0,(5,17,29)),
        ('brighten',0x08147ec8,(8,)),('darken',0x08147f50,(8,)),('exposure',0x0814731c,(384,)),
        ('exposure_rgb',0x081473e4,(128,256,384)),('table_exposure',0x081474bc,(TEMP+2,128,256,384)),
        ('table_blend',0x08147e28,(TEMP+2,0x421f,8,8))]
if args.boundaries_only:operations=[]
try:
    for (name,pc,values),owner,duration,interrupt,residue in itertools.product(operations,range(10),(6,) if args.additional_operations else (0,6,17),(False,) if args.additional_operations else (False,True),(0,4)):
        case=str((name,owner,duration,interrupt,residue));a,n,o=machine(rom),machine(original),machine(original)
        ref=a.read(live['symbols']['ffta_art_native_reference']+owner*32,32)
        custom=a.read(live['symbols']['ffta_art_custom_colors']+owner*32,32)
        for m in (a,n):m.put(PAL,ref);m.put(TEMP,ref)
        o.put(PAL,custom);o.put(TEMP,custom)
        # The native damage operation is blend first449,count15. Exercise
        # supported endpoints/interruption too; do not invent a palette target.
        tasks=[call(m,pc,449,15,duration,*values,residue=residue) for m in (a,n,o)]
        keys=a.read(V,20);slot=keys.index(owner*16+12);entry=B+slot*252
        check(native(a)==native(n),'Original native setup unchanged')
        check(a.word(entry+244)==tasks[0] and tasks[0]==tasks[1],'Late class history owns actual damage task')
        check(a.read(entry,32)==o.read(PAL,32),'Generated initial colors exact native oracle')
        advance=3 if interrupt and duration==17 else max(1,duration)
        for step in range(advance):
            for m,t in zip((a,n,o),tasks):call(m,0x08148740,t,residue=residue)
            check(native(a)==native(n),'Native damage tick exact '+str(step))
            check(a.read(entry,32)==o.read(PAL,32),'Every generated damage color exact native interpolation '+str(step))
            check(a.read(entry,2)==custom[:2],'Transparent color stays unchanged '+str(step))
        # Restore only colors1..15 from a differently located native baseline.
        tasks=[call(m,0x08147d2c,449,15,6,TEMP+2,residue=residue) for m in (a,n,o)]
        check(native(a)==native(n),'Partial baseline table setup unchanged')
        for step in range(6):
            for m,t in zip((a,n,o),tasks):call(m,0x08148740,t,residue=residue)
            check(native(a)==native(n),'Native restore tick exact '+str(step))
            check(a.read(entry,32)==o.read(PAL,32),'Generated partial restoration exact '+str(step))
        check(a.read(entry,32)==custom and a.word(entry+244)==0,'Generated full original palette restored and task retired')
        check(a.word(B+live['bindingCounterOffset']+8)==0 and a.read(BASE+live['refusalOffset'],16)==bytes(16),'No partial-range refusal')
        check(outside(a)==outside(n),'No unrelated game/save/heap memory changes')
    if args.additional_operations or args.boundaries_only:
        for first,count,duration in ((450,14,6),(448,15,6),(449,15,256)):
            case='unsupported-range-'+str((first,count,duration));a,n=machine(rom),machine(original)
            ref=a.read(live['symbols']['ffta_art_native_reference']+64,32)
            for m in (a,n):m.put(PAL,ref)
            # Establish the authenticated whole-bank identity before probing
            # rejected ranges, so absence of an owner cannot hide a refusal.
            call(a,live['symbols']['ffta_art_variants_track'],V,B,0x03003a60,
                live['symbols']['ffta_art_native_reference'],live['symbols']['ffta_art_custom_colors'],448,463,1023,BASE+live['visibleColorsOffset'])
            slot=a.read(V,20).index(0x2c);entry=B+slot*252;before=a.read(entry,32)
            task=call(a,0x08147d94,first,count,duration,0x318,8,8);ntask=call(n,0x08147d94,first,count,duration,0x318,8,8)
            check(task==ntask and native(a)==native(n),'Unsupported range preserves original operation')
            check(a.read(entry,32)==before and a.word(entry+244)==0 and a.word(B+live['bindingCounterOffset']+8)>0,'Unsupported range remains explicit and invents no colors')
    if args.boundaries_only:
        for confirmed,uniform in itertools.product((False,True),(False,True)):
            case='partial-table-'+str((confirmed,uniform));a,n,o=machine(rom),machine(original),machine(original)
            ref=a.read(live['symbols']['ffta_art_native_reference']+64,32)
            for m in (a,n):m.put(PAL,ref)
            custom=a.read(live['symbols']['ffta_art_custom_colors']+64,32);o.put(PAL,custom)
            call(a,live['symbols']['ffta_art_variants_track'],V,B,0x03003a60,
                live['symbols']['ffta_art_native_reference'],live['symbols']['ffta_art_custom_colors'],448,463,1023,BASE+live['visibleColorsOffset'])
            slot=a.read(V,20).index(0x2c);entry=B+slot*252
            if confirmed:a.put(BASE+live['confirmedOffset']+slot,b'\x2c')
            payload=b'\x34\x12'*15 if uniform else struct.pack('<15H',*range(1,16))
            for m in (a,n,o):m.put(TEMP,payload)
            before=a.read(entry,32)
            tasks=[call(m,0x08147d2c,449,15,6,TEMP) for m in (a,n,o)]
            check(native(a)==native(n),'Partial table preserves native setup')
            if uniform:
                for step in range(6):
                    for m,t in zip((a,n,o),tasks):call(m,0x08148740,t)
                    check(a.read(entry,32)==o.read(PAL,32) and native(a)==native(n),'Uniform partial target exact '+str(step))
                check(a.word(B+live['bindingCounterOffset']+8)==0,'Uniform partial target supported')
            elif confirmed:
                check(a.read(V+slot,1)==b'\x2c' and a.word(B+live['bindingCounterOffset']+8)==1 and a.read(entry,32)==before and a.word(entry+244)==0,'Confirmed unmappable partial target explicitly refused')
            else:
                check(a.read(V+slot,1)==b'\xff' and a.word(B+live['bindingCounterOffset']+8)==0 and a.read(entry,32)==before and a.word(entry+244)==0,'Unconfirmed unrelated partial target retires without invented colors')
    result=dict(status='passed',romSha1=meta['romSha1'],checks=checks,operations=operations,boundariesOnly=args.boundaries_only,
        sources={p.name:sha(p.read_bytes()) for p in (source/'371-active-ready.ram',source/'371-active-ready.iwram')},
        scope='All ten generated palettes: listed actual installed colors1..15 operations and partial native-table restoration; original native oracle every RGB555 color/tick; durations0/6/17, interruption, both stack alignments, unchanged transparent color and unrelated game RAM. Does not establish live timing, simultaneous disjoint partial tasks or arbitrary partial ranges.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),case=case,checks=checks),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
