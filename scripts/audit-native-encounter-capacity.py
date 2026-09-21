"""Read-only native formation inventory for capacity test selection.

Authenticates the candidate and original table, then inventories all442 native
records and their template flags. Template counts are not simultaneous actor
counts: scripted spawns, deployment, judges and optional secondary formations
need their own consumer/lifetime evidence. No emulation or fixtures are created.
"""
import argparse, collections, datetime, hashlib, json, struct
from pathlib import Path
from native_art import ROOT, sha

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--manifest',type=Path,required=True)
args=parser.parse_args()
out=ROOT/'build/art/encounter-capacity-audit'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
checks=[];rows=[]

def check(ok,label):
    assert ok,label
    checks.append(label)

try:
    meta=json.loads(args.manifest.read_text(encoding='utf-8'))
    rom=Path(meta['path']).read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Candidate ROM authentication')
    check(hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9','Known original US ROM')
    table=0x54cd54
    check(rom[table+40:table+443*40]==clean[table+40:table+443*40],'Every native formation record1..442 unchanged')
    consumers={}
    for name,start,end in [('enemyAllocator',0xc83a4,0xc83cc),('actorEnumerator',0x99cdc,0x99d08),
                           ('bulkFormationConstructor',0xca744,0xca7a4),
                           ('initialFormationLoader',0x96e18,0x96e78),
                           ('initialFormationEvent',0x123670,0x123694),
                           ('scriptedIdentityAndAllocation',0x1243c0,0x12443a),
                           ('judgeAllocation',0x12baa2,0x12bb20),
                           ('savedRosterActorRestore',0x992e0,0x993f4),
                           ('secondaryDeploymentChoice',0x123694,0x123714),
                           ('secondaryEventBranch',0x123cc0,0x123cfc),
                           ('formationSelectors',0xa018,0xa050),('battleSetup',0x8f8e8,0x8fa98),
                           ('eventFormationSelection',0x9c04,0x9c94),
                           ('scriptSceneSelection',0x123898,0x123900),
                           ('battleRosterEvent',0x1237d0,0x123814),
                           ('battlePrimaryRoster',0x1256d4,0x125760),
                           ('battleSecondaryRoster',0x124bb4,0x124ce8),
                           ('battleRosterActors',0x124ce8,0x124d58),
                           ('sceneRosterReset',0x123e00,0x123e98),
                           ('templateSideTransfer',0xc9668,0xc9672),
                           ('nativeSidePredicate',0xc8240,0xc8260)]:
        check(rom[start:end]==clean[start:end],'Original '+name+' bytes retained')
        consumers[name]=dict(start=start,end=end,sha256=sha(rom[start:end]))
    # Exact static allocator instructions, not the observer's permissive36 bound.
    check(rom[0xc83a8:0xc83ae].hex()=='002284235b00' and
          rom[0xc83bc:0xc83c6].hex()=='0132c9180b2af4dd0020' and
          struct.unpack_from('<I',rom,0xc83b8)[0]==0x02002fc4,
          'Native enemy allocator starts at02002FC4, stride264, twelve records')
    def bl_target(p):
        first,second=struct.unpack_from('<2H',rom,p)
        assert first&0xf800==0xf000 and second&0xf800==0xf800
        delta=((first&2047)<<12)|((second&2047)<<1)
        if delta&(1<<22):delta-=1<<23
        return p+4+delta
    check(rom[0x96e30:0x96e32]==bytes.fromhex('0c22') and bl_target(0x96e32)==0xca744 and
          struct.unpack_from('<I',rom,0x96e74)[0]==0x02002fc4,
          'Initial formation loader passes twelve and native nonparty base to bulk constructor')
    check(bl_target(0x123672)==0xa018 and bl_target(0x123684)==0x96e18,
          'Initial scene event obtains primary formation and invokes bounded loader')
    check(rom[0xca75e:0xca762]==bytes.fromhex('4a4519da') and
          rom[0xca792:0xca796]==bytes.fromhex('4a45e5db'),
          'Original bulk loop checks caller limit before and after each template')
    check(bl_target(0x1243c6)==0x121cb4 and bl_target(0x1243d2)==0xc83cc and
          bl_target(0x1243e2)==0xc83a4 and bl_target(0x1243ec)==0xc9644 and
          bl_target(0x124404)==0x99560 and bl_target(0x124434)==0x92440,
          'Scripted spawn resolves existing identity/actor before its twelve-slot allocation fallback')
    check(bl_target(0x12baa2)==0xa018 and bl_target(0x12bacc)==0xc83a4 and
          bl_target(0x12bad6)==0xc9644 and bl_target(0x12bb08)==0x92440 and
          rom[0x12baba:0x12babe].hex()=='21310978',
          'Judge selector at formation+33 constructs through the same twelve-record allocator')
    check(rom[0x992fe:0x99300].hex()=='1720' and rom[0x99370:0x99372].hex()=='0b22' and
          bl_target(0x9934a)==0x92440 and bl_target(0x993bc)==0x92440,
          'Saved actor restoration walks24 party and12 nonparty records with native eligibility flags')
    check(bl_target(0x1236a6)==0xa024 and rom[0x1236e8:0x1236ec].hex()=='26342078' and
          bl_target(0x123cc6)==0xa024 and rom[0x123cd8:0x123cdc].hex()=='22310878',
          'These secondary-selector consumers read formation metadata+38/+34, not an additional bulk roster')
    for identity in range(1,443):
        start=table+40*identity;record=rom[start:start+40];count=record[0]
        pointer=struct.unpack_from('<I',record,4)[0]-0x08000000
        check(1<=count<=13 and struct.unpack_from('<H',record)[0]==count and
              0x52a4d0<=pointer<pointer+48*count<=0x54bb30,
              'Bounded original template extent '+str(identity))
        templates=rom[pointer:pointer+48*count]
        flags=[struct.unpack_from('<H',templates,48*i+42)[0] for i in range(count)]
        rows.append(dict(formation=identity,templateCount=count,templateOffset=pointer,
                         deploymentByte=record[32],judgeSelector=record[33],
                         initialPlusPotentialJudge=min(count,12)+bool(record[33]),
                         initialBulkTemplateCount=min(count,12),
                         outsideInitialBulkIndices=list(range(12,count)),
                         opposingFlagCount=sum(bool(f&0x8000) for f in flags),flags=flags,
                         recordSha256=sha(record),templatesSha256=sha(templates),
                         templatesChangedFromOriginal=templates!=clean[pointer:pointer+48*count]))
    # Inventory actual event selectors, rather than promoting every formation
    # table row into a reachable battle. The script scene-selection handler
    # searches this same event table backwards and forwards its primary value.
    event_start=0x563a70
    check(rom[event_start:event_start+256*12]==clean[event_start:event_start+256*12],
          'All256 original event records retained')
    check(struct.unpack_from('<III',rom,0x1238c0)==(0x08563a70,0x02003c2a,255*12) and
          rom[0x1238ac:0x1238b8].hex()=='4878a0420cd11a7048880021' and
          bl_target(0x1238b8)==0x9c04 and
          rom[0x1238cc:0x1238d4].hex()=='0c39013a002aebdc',
          'Script scene selector searches event255..1 and forwards matching primary formation')
    event_rows=[];links=collections.defaultdict(list)
    for event in range(256):
        record=rom[event_start+12*event:event_start+12*(event+1)]
        primary,secondary=struct.unpack_from('<HH',record,2)
        event_rows.append(dict(event=event,scene=record[1],primary=primary,secondary=secondary,
                               recordSha256=sha(record)))
        for role,formation in [('primary',primary),('secondary',secondary)]:
            if formation:links[formation].append(dict(event=event,role=role,scene=record[1]))
    for row in rows:row['nativeEventSelectors']=links[row['formation']]
    check(not links[19] and not links[29],
          'Neither formation19 nor judge-template formation29 is selected by any native event record')
    check(rom[0x12bab4:0x12bab8].hex()=='9123db00' and
          rom[0x12bac4:0x12baca].hex()=='303854682418' and
          rows[28]['templateCount']==4 and
          max(row['judgeSelector'] for row in rows)==4,
          'Judge uses formation29 template pointer with selector-minus-one stride48 and four available templates')
    check(bl_target(0x1237e2)==0x124bb4 and bl_target(0x1237f4)==0x1256d4 and
          rom[0x1237d6:0x1237e2].hex()=='a2321088002806d0a0310988',
          'Battle opcode4E chooses secondary roster124BB4 when present, otherwise primary1256D4')
    check(bl_target(0x125716)==0xc9644 and bl_target(0x124c20)==0xc9644 and
          bl_target(0x125754)==0x124ce8 and bl_target(0x124cd4)==0x124ce8 and
          bl_target(0x124cfc)==0x92440,
          'Actual battle roster constructors iterate templates and publish actors through shared124CE8')
    check(rom[0x123e1c:0x123e20].hex()=='c6210901' and
          struct.unpack_from('<I',rom,0x123e7c)[0]==0x02002fc4 and
          bl_target(0x123e22)==0x14224c,
          'Scene setup requests native fill of exactly twelve264-byte nonparty records before mode dispatch')
    check(rom[0xc9668:0xc9672].hex()=='398d4246508d01433985' and
          rom[0xc8248:0xc8250].hex()=='018d802000020840',
          'Template+42 flags transfer to unit+40 and native side predicate reads bit8000')
    # Two actual generic battle scenes begin with the reset then roster command.
    script_base=struct.unpack_from('<I',rom,0x1223c0)[0]-0x08000000
    scene_prefixes=[]
    for scene in (168,173):
        group,index=rom[0xa19970+scene*4:0xa19970+scene*4+2]
        group_start=script_base+struct.unpack_from('<I',rom,script_base+4*(group-1))[0]
        start=group_start+struct.unpack_from('<I',rom,group_start+4*index)[0]
        check(rom[start:start+5]==clean[start:start+5]==bytes.fromhex('0c0048014e'),
              'Original generic battle scene reset48/roster4E prefix '+str(scene))
        scene_prefixes.append(dict(scene=scene,start=start,prefix=rom[start:start+5].hex()))
    maximum=max(r['templateCount'] for r in rows)
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,scope=__doc__,
        manifest=str(args.manifest),manifestSha256=sha(args.manifest.read_bytes()),
        consumers=consumers,nativeEnemyRecordCapacity=12,
        nativeEvents=event_rows,
        genericBattlePrefixes=scene_prefixes,
        actualBattleRosterContract='Opcode4E uses1256D4 for primary or124BB4 for secondary. Both iterate the complete selected template count and search the twelve nonparty records before C9644; neither safely refuses a full domain. The separate opcode4A bound is not their bound. Generic scenes168/173 execute reset48 first. Template bit8000 is the opposing side, not an allied flag.',
        eventSelectedLargeFormations=[row['formation'] for row in rows
                                     if row['nativeEventSelectors'] and row['templateCount']>=9],
        initialBulkTemplateLimit=12,
        savedActorRecordDomain=dict(party=24,nonparty=12,scope='Native restore iterator domain, not a proved reachable simultaneous actor maximum'),
        potentialJudgeSlotConflicts=[r['formation'] for r in rows if r['initialPlusPotentialJudge']>12],
        initialBulkContract='Event123670 selects primary formation with A018. Loader96E18 invokes CA744 with limit12 and base02002FC4. With an initially empty domain it constructs the first min(count,12) templates; this does not prove scene reachability or subsequent script behavior.',
        maximumTemplateCount=maximum,maximumTemplateFormations=[r['formation'] for r in rows if r['templateCount']==maximum],
        templateHistogram=dict(sorted(collections.Counter(r['templateCount'] for r in rows).items())),
        deploymentHistogram=dict(sorted(collections.Counter(r['deploymentByte'] for r in rows).items())),
        formations=rows,limitations=[
            '13 templates do not prove13 simultaneous enemies; allocator has12 records including non-enemy actors.',
            'Initial bulk constructor can skip occupied records; empty-domain precondition and scripted secondary spawns require runtime lifecycle proof.',
            'Formation deployment byte is not an unconditional party actor count.',
            'Judge construction shares the twelve nonparty slots. Formation19 has twelve templates and a nonzero judge selector, but no native event selects it. This bounded negative does not exclude direct selector writes, saved-state inputs or other indirect paths.',
            'Native event selection and two generic scene prefixes are audited, not every conditional script or subsequent spawn/retirement.',
            'No maximum live actor, heap, palette, effect or all-ten coexistence acceptance.'])
    destination=out/'report.json';destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),maximumTemplates=maximum,
                         maximumTemplateFormations=report['maximumTemplateFormations'],report=str(destination))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,formations=rows),indent=2)+'\n',encoding='utf-8')
    raise
