"""Native event selection and initial-roster inventory on current and clean code.

Execute the original selector prefix for every native event/location pair and
the scene-search prefix for every byte-valued scene plus two out-of-range cases.
Stop after selection, before scene allocation. This is not battle playback or
proof of every later scripted spawn. All 512 mission slots are included.
"""
import datetime, hashlib, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha

sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_MEM_WRITE
from unicorn.arm_const import (UC_CPU_ARM_TI925T, UC_ARM_REG_R0,
    UC_ARM_REG_R1, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC)

manifest=ROOT/'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json'
meta=json.loads(manifest.read_text());rom=Path(meta['path']).read_bytes()
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
out=ROOT/'build/art/native-event-roots'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True);checks=[];cases=[];scene_cases=[];consumers=[]
half=lambda data,p:struct.unpack_from('<H',data,p)[0]
word=lambda data,p:struct.unpack_from('<I',data,p)[0]

def check(ok,label):
    assert ok,label
    checks.append(label)

def formation(data,identity):
    p=0x54cd54+40*identity;count=data[p];start=word(data,p+4)-0x08000000
    flags=[half(data,start+48*i+42) for i in range(count)]
    return dict(formation=identity,templates=count,opposing=sum(bool(f&0x8000) for f in flags),
        allied=sum(not f&0x8000 for f in flags),deploymentByte=data[p+32],judgeSelector=data[p+33],
        recordSha256=sha(data[p:p+40]),templatesSha256=sha(data[start:start+48*count]))

try:
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1']=='a28b624bb13c8f2f2597a4d4bd3999b17c234b99','Current candidate authenticated')
    check(hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9','Original US authenticated')
    for name,a,b in [('formationSelector',0x9c04,0x9c94),('locationAdapter',0xa040,0xa06c),
        ('missionEntry',0x616ac,0x61720),('sceneSearch',0x123898,0x123900),
        ('randomQueueProducer',0xcf7f4,0xcfa48),('missionQueueProducer',0xd0bf8,0xd0d5c),
        ('worldEventLookup',0xd17c4,0xd1a18),('worldEntry',0x343dc,0x345d0),
        ('missionWorldEntry',0x3b5c0,0x3b858),('deploymentDisplay',0x75574,0x75620)]:
        check(rom[a:b]==clean[a:b],'Original consumer retained '+name)
        consumers.append(dict(name=name,start=a,end=b,sha256=sha(rom[a:b])))
    check(rom[0x563a70:0x564670]==clean[0x563a70:0x564670],'All 256 native event records retained')
    check(word(rom,0x9c38)==0x08563a70+225*12,'Secondary map lookup uses roaming event base225, not event0')
    missions=[]
    for i in range(512):
        p=0x55ae4c+70*i
        check(rom[p+69]==clean[p+69],'Mission selector retained '+str(i))
        missions.append(dict(mission=i,event=rom[p+69],recordSha256=sha(rom[p:p+70])))
    check(not any(row['event']==203 for row in missions),'No event203 selector in any of 512 mission records')
    check(word(rom,0x6170c)==word(rom,0xd18f0)==0x0855ae4c and
        rom[0x616b4:0x616c2].hex()=='4620111c41431448091845310878',
        'Mission entry reads the actual 70-byte table event field69')
    check(rom[0xd0bfa:0xd0c00].hex()=='231c45331978' and rom[0xd0c20:0xd0c22].hex()=='9a46' and
        rom[0xd0d36:0xd0d3a].hex()=='51460b78',
        'Mission queue producer packs the mission event field, not an independent selector')
    check(rom[0xcf8ba:0xcf8c0].hex()=='1f2d00d1bee0' and
        rom[0xcf8ec:0xcf8f2].hex()=='e122d2199046',
        'Random queue producer bounds location1..30 and adds225')
    events=[rom[0x563a70+12*i:0x563a70+12*(i+1)] for i in range(256)]
    reverse={record[1]:i for i,record in enumerate(events) if i>0}
    check(events[203][1]==168 and reverse[168]==255,'Descending scene search chooses255, not203, for scene168')
    # Decode candidate Thumb BL pairs only to inventory direct entry references.
    # This bounded code scan is not a whole-ROM indirect-call reachability proof.
    refs={0x9c04:[],0x9c18:[],0xa040:[]}
    for p in range(0,0x150000-4,2):
        a,b=struct.unpack_from('<HH',rom,p)
        if a&0xf800==0xf000 and b&0xf800==0xf800:
            delta=((a&2047)<<12)|((b&2047)<<1)
            if delta&(1<<22):delta-=1<<23
            if p+4+delta in refs:refs[p+4+delta].append(p)
    check(refs=={0x9c04:[0x9c40,0x1238b8],0x9c18:[0xa058,0x616e6],
        0xa040:[0x34456,0x34500,0x34590,0x3b63c,0x3b804]},'Declared native direct entry reference inventory')
    scenarios=[]
    for i,record in enumerate(events):
        primary,secondary=struct.unpack_from('<HH',record,2)
        if not (primary or secondary):continue
        for location in (range(1,31) if secondary else [0]):
            map_id=half(events[225+location],2) if secondary else primary
            enemy=formation(rom,secondary or primary);map_row=formation(rom,map_id)
            # Includes mandatory allied templates when their count exceeds the
            # deployment display. This is initial-roster arithmetic, not a
            # claim that every combination is eligible or later spawns cannot occur.
            estimate=enemy['opposing']+max(enemy['allied'],map_row['deploymentByte'])+bool(map_row['judgeSelector'])
            scenarios.append(dict(event=i,location=location,primary=map_id,secondary=secondary,
                roster=enemy,map=map_row,initialRosterEstimate=estimate))
    oversized=[row for row in scenarios if row['initialRosterEstimate']>13]
    check(len(scenarios)==1612 and len(oversized)==1 and oversized[0]['event']==203 and
        oversized[0]['initialRosterEstimate']==14,'Event203 is the sole greater-than13 initial-roster estimate across1612 event/location pairs')
    for source,image in [('current',rom),('clean',clean)]:
        m=Uc(UC_ARCH_ARM,UC_MODE_THUMB);m.ctl_set_cpu_model(UC_CPU_ARM_TI925T)
        for address,size in [(0x02000000,0x40000),(0x03000000,0x8000),(0x08000000,0x2000000)]:m.mem_map(address,size)
        m.mem_write(0x08000000,image);writes=[]
        def on_write(machine,access,address,size,value,unused):
            if 0x02000000<=address<0x02040000:writes.append((address,size,value))
        m.hook_add(UC_HOOK_MEM_WRITE,on_write)
        for row in scenarios:
            m.mem_write(0x02002170,b'\xaa'*4);writes.clear()
            for reg,value in [(UC_ARM_REG_R0,0x08563a70+row['event']*12),(UC_ARM_REG_R1,row['location']),
                (UC_ARM_REG_SP,0x03007000),(UC_ARM_REG_LR,0x08000101)]:m.reg_write(reg,value)
            m.emu_start(0x08009c19,0x08009c44,count=200)
            actual=list(struct.unpack('<HH',m.mem_read(0x02002170,4)))
            check(m.reg_read(UC_ARM_REG_PC)==0x08009c44 and actual==[row['primary'],row['secondary']] and
                writes==[(0x02002170,2,row['primary']),(0x02002172,2,row['secondary'])],
                'Actual native event/location selection '+str((source,row['event'],row['location'])))
        for scene in [*range(256),256,65535]:
            m.mem_write(0x02010000,b'\0'+struct.pack('<H',scene))
            m.mem_write(0x02002170,b'\xaa'*4);m.mem_write(0x02003c2a,b'\xaa');writes.clear()
            for reg,value in [(UC_ARM_REG_R1,0x02010000),(UC_ARM_REG_SP,0x03007000),(UC_ARM_REG_LR,0x08000101)]:m.reg_write(reg,value)
            m.emu_start(0x08123899,0x081238d4,count=6000)
            event=reverse.get(scene);expected=[] if event is None else [(0x02003c2a,1,event),
                (0x02002170,2,half(events[event],2)),(0x02002172,2,0)]
            check(m.reg_read(UC_ARM_REG_PC)==0x081238d4 and writes==expected,
                'Actual descending native scene selection '+str((source,scene)))
            scene_cases.append(dict(source=source,scene=scene,event=event,writes=writes.copy()))
        cases.append(dict(source=source,romSha1=hashlib.sha1(image).hexdigest(),eventLocationCases=len(scenarios),sceneCases=258))
    report=dict(status='passed',romSha1=meta['romSha1'],manifestSha256=sha(manifest.read_bytes()),checks=checks,
        consumers=consumers,missions=missions,directReferences={hex(k):v for k,v in refs.items()},
        cases=cases,scenes=scene_cases,scenarios=scenarios,oversized=oversized,scope=__doc__,
        conclusion='Event203 is excluded by all512 mission selectors, the audited mission/random queue producers and the actual descending scene selector. The only retained14-actor failure substitutes it into a different scene. This does not certify all later scripted spawns, effect peaks, saved restoration or full engineering.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',checks=checks,cases=cases,scenes=scene_cases,error=str(error)),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
