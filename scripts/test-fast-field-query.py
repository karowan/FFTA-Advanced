"""Differential native field queries and complete movement grids.

Use authenticated detached battle memory, not resumed actor state. Compare the
original full query with the candidate, independent native map geometry, copied
owners and full grids. This does not establish live timing or campaign coverage.
"""
import ast,collections,datetime,hashlib,itertools,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007800
text=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')
exec(compile(ast.Module(body=[n for n in ast.parse(text).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
out=ROOT/'build/art/field-query-contracts'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=collections.Counter();case=None;records=[]
def check(ok,label):
    assert ok,(case,label)
    checks[label]+=1

try:
    view=json.loads((ROOT/'build/art/performance/field-query/current.json').read_bytes())
    part=json.loads(Path(view['fieldQueryFast']).read_bytes())
    parent_raw=Path(part['sourceManifest']).read_bytes();check(sha(parent_raw)==part['sourceManifestSha256'],'Parent manifest authenticated')
    parent=json.loads(parent_raw);roms=[Path(parent['path']).read_bytes(),Path(view['path']).read_bytes()]
    check([hashlib.sha1(r).hexdigest() for r in roms]==[part['baseRomSha1'],view['romSha1']],'Both ROM hashes authenticated')
    lo,hi=part['used'];h=part['patch']['offset']
    check(roms[0][:h]==roms[1][:h] and roms[0][h+12:lo]==roms[1][h+12:lo] and roms[0][hi:]==roms[1][hi:],'Every unrelated art/gameplay/save byte preserved')
    upstream=json.loads(Path(part['upstreamManifest']).read_bytes());S=upstream['symbols'];query=S['ffta_geo_field_at']
    capture=ROOT/'build/art/live-palette/battle/20260919T013433.783581Z'
    ram=(capture/'candidate-ready.ram').read_bytes();iw=(capture/'candidate-ready.iwram').read_bytes()
    pins=dict(ram=sha(ram),iwram=sha(iw))
    check(pins==dict(ram='133af7f1fd42414e7161e69c0aed1fae9cca65fa29ab67c2b898f336b1ff36f2',iwram='98dfbdef073919f3531ce01463d3431818be6f7f0bb7f62495f0216446c35067'),'Detached native context authenticated')
    machines=[ARM(r,iw) for r in roms]
    units=[0x02000080+i*264 if i<24 else 0x02002fc4+(i-24)*264 for i in range(36)]
    for m in machines:m.put(0x02000000,ram)
    banks=[m.call(S['ffta_job_state'],units[0]) for m in machines]
    check(banks==[0x0203f410]*2,'Existing canonical bank validated')
    heights={}
    for y,x in itertools.product(range(16),repeat=2):
        if machines[0].call(0x0801cc7c,x,y):heights[x,y]=machines[0].call(0x0801cc18,x,y)
    check(len(heights)>20,'Native map has positive query coverage')
    center=next((x,y) for x,y in heights if (x+1,y) in heights and (x,y+1) in heights)
    bank=banks[0];counts=[collections.Counter(),collections.Counter()]
    fallback_entries=[[],[]]
    sites={S['ffta_job_peers']:'peers',S['ffta_job_state']:'state',part['symbols']['ffta_geo_field_original']:'fallback'}
    for index,m in enumerate(machines):
        def observe(uc,pc,size,data):
            index,name=data;counts[index][name]+=1
        for pc,name in sites.items():m.u.hook_add(UC_HOOK_CODE,observe,user_data=(index,name),begin=pc,end=pc)
        def fallback(uc,pc,size,index):
            sp=uc.reg_read(UC_ARM_REG_SP)
            fallback_entries[index].append((sp,bytes(uc.mem_read(sp,200))))
        m.u.hook_add(UC_HOOK_CODE,fallback,user_data=index,begin=query+12,end=query+12)
        # Accessor/map preflight already translated these blocks. Unicorn must
        # retranslate them after installing bounded instruction observers.
        m.u.ctl_flush_tb()
    def reset(fields=()):
        for index,m in enumerate(machines):
            m.put(0x02000000,ram);m.put(0x03000000,iw)
            m.put(0x080cd538,roms[index][0xcd538:0xcd53c])
            m.put(bank,bytes(36*22))
            for i,u in enumerate(units):
                m.put(u+0x18,struct.pack('<H',100));m.put(u+0xe8,bytes(8));m.put(u+0x29,bytes((128 if i>=24 else 0,)))
            for slot,kind,timer,cx,cy,hp,petrify,charm in fields:
                m.put(bank+slot*22+15,bytes((cx,cy,(timer<<2)|kind)))
                m.put(units[slot]+0x18,struct.pack('<H',hp));m.put(units[slot]+0xe8,bytes((64 if petrify else 0,)))
                m.put(units[slot]+0xeb,bytes((32 if charm else 0,)))
        for c in counts:c.clear()
    def pair(u,x,y,kind,expected=None,stack=STACK):
        for rows in fallback_entries:rows.clear()
        before=[m.read(0x02000000,0x40000) for m in machines]
        values=[m.call(query,u,x,y,kind,stack=stack) for m in machines]
        check(values[0]==values[1],'Exact original query result')
        if expected is not None:check(values==[expected]*2,'Independent geometry/eligibility result')
        if u not in units:
            check(len(fallback_entries[0])==len(fallback_entries[1])==1,'Both noncanonical calls enter original body once')
            # Original prologue writes args at8..20 and preserved registers at
            #180..199. Uninitialized local stack bytes are not API outputs.
            a,b=fallback_entries[0][0],fallback_entries[1][0]
            check(a[0]==b[0]==stack-200 and a[1][8:24]==b[1][8:24] and a[1][180:]==b[1][180:],
                  'Original fallback stack arguments preserved registers and return address exact')
        for m,b in zip(machines,before):check(m.read(0x02000000,0x40000)==b,'Query leaves complete EWRAM unchanged')
        return values[0]
    # Every byte within both native arrays and the intervening gap, plus
    # address-space boundaries. Compare the actual original canonical helper.
    for pointer in [0,0xffffffff,0x03007900,*range(units[0]-1,units[-1]+265)]:
        expected=int(pointer in units)
        old=machines[0].call(0x091d0026,pointer)
        new=machines[1].call(part['symbols']['ffta_geo_field_canonical'],pointer)
        check(bool(old)==bool(new)==bool(expected),'Exact native canonical predicate across every array and gap byte')
    # All canonical slots, including empty roster slots and enemy records.
    for slot,kind,timer in itertools.product(range(36),(1,2),range(8)):
        case=('canonical',slot,kind,timer);cx,cy=center
        reset([(slot,kind,timer,cx,cy,100,False,False)])
        for recipient in (0,24):
            expected=int((timer&3) in (1,2) and (kind==1 or (slot>=24)==(recipient>=24)))
            pair(units[recipient],cx,cy,kind,expected)
        # The queried owner itself must be accepted in every canonical slot.
        pair(units[slot],cx,cy,kind,int((timer&3) in (1,2)),stack=STACK+4)
        check(counts[1]['peers']==0 and counts[1]['fallback']==0 and counts[1]['state']==3,'Canonical queries avoid peer construction with current accessor checks')
    # Complete native map for both kinds and difficult eligibility combinations.
    for kind,hp,petrify,charm,overlap in itertools.product((1,2),(0,100),(False,True),(False,True),(False,True)):
        case=('map',kind,hp,petrify,charm,overlap);cx,cy=center
        fields=[(24,kind,6,cx,cy,hp,petrify,charm)]
        if overlap:fields.append((0,kind,2,cx,cy,100,False,False))
        reset(fields)
        for y,x in itertools.product(range(16),repeat=2):
            inside=(x,y) in heights and abs(x-cx)+abs(y-cy)<=1 and abs(heights[x,y]-heights[cx,cy])<=2
            eligible=overlap or (hp>0 and not petrify and (kind==1 or charm))
            pair(units[0],x,y,kind,int(inside and eligible))
    # Bad coordinates/kinds, bank guards and noncanonical pointers use exact
    # original semantics. These are isolated test inputs, never player files.
    for defect in ('none','bank-magic','format-magic','format-version'):
        case=('guards',defect);reset([(0,1,6,*center,100,False,False)])
        for m in machines:
            if defect=='bank-magic':m.put(bank-16,bytes(4))
            if defect=='format-magic':m.put(0x02001e70,bytes(8))
            if defect=='format-version':m.put(0x02001e78,b'\x02')
        for u in (0,*units,units[0]+1,0x03007400):
            for x,y,kind in [(*center,1),(-1,0,1),(16,0,1),(0,-1,1),(0,16,1),(*center,0),(*center,3)]:
                pair(u,x,y,kind,int(defect=='none' and u in units and (x,y)==center and kind==1))
    # Actual owned evaluation snapshots must not borrow a live caster's field.
    # Containers live above the active stack, as required by the ownership API.
    copy=0x03007900
    for own,live_field in itertools.product((False,True),repeat=2):
        case=('owned-copy',own,live_field);reset([(0,1,6,*center,100,False,False)] if live_field else [])
        for m in machines:
            check(m.call(S['ffta_snapshotted_evaluated_init'],copy,units[24])==1,'Actual evaluated owner created')
            s=m.call(S['ffta_job_state'],copy);check(s!=0 and not bank<=s<bank+36*22,'Copied state is independent')
            m.put(s+15,bytes((*center,25 if own else 0)))
        pair(copy,*center,1,int(own))
        check(counts[1]['fallback']>0,'Noncanonical copy uses complete original query')
        for m in machines:m.call(S['ffta_snapshotted_evaluated_close'],copy)
        pair(copy,*center,1,0)
    # Explicit height boundary and invalid field centers, beyond the native
    # map's incidental height distribution. Native getters provide the oracle.
    cx,cy=center
    for delta in (0,2,3,6):
        case=('height-boundary',delta);reset([(0,1,6,cx,cy,100,False,False)])
        for m in machines:
            hm=m.word(0x02007f14);width=m.read(0x02007f18,1)[0]
            check(0x02000000<=hm<0x02040000 and 1<=width<=32,'Bounded native height grid')
            m.put(hm+2*(cy*width+cx),b'\x04');m.put(hm+2*(cy*width+cx+1),bytes((4+delta,)))
        a=machines[0].call(0x0801cc18,cx,cy);b=machines[0].call(0x0801cc18,cx+1,cy)
        check(abs(a-b)==delta,'Native height getter confirms controlled difference')
        pair(units[0],cx+1,cy,1,int(delta<=2))
    for fx,fy in [(255,0),(0,255),(16,16)]:
        case=('invalid-center',fx,fy);reset([(0,1,6,fx,fy,100,False,False)])
        pair(units[0],*center,1,0)
    # Native tile callback consumes the optimized query; compare every grid
    # cell with original behavior under Rime, Refuge, Float and Surefoot.
    from native_battle_wrappers import from_memory
    wrappers=from_memory(roms[0],ram,iw)
    unit_offset,wrapper_offset=next(iter(wrappers.items()));unit=0x02000000+unit_offset;wrapper=0x02000000+wrapper_offset
    grid=0x0202d000
    check(unit in units,'Native grid consumer uses a canonical live actor')
    for kind,air,sure in itertools.product((0,1,2),(0,1,2),(False,True)):
        case=('native-grid',kind,air,sure);reset([(0,kind,6,*center,100,False,False)] if kind else [])
        for m in machines:
            m.put(unit+0x3b,bytes((0x87 if sure else 0,)))
            # Surefoot is lesson135, represented directly only in this detached
            # native support table fixture; other fields remain native-derived.
            race=m.read(unit+6,1)[0];ptrs=m.word(0x080cd538);table=m.word(ptrs+race*4)
            table_copy=bytearray(m.read(table,0x800));table_copy[0x87*8:0x88*8]=struct.pack('<HHHBB',0,0,135,3,1)
            ptr_copy=bytearray(m.read(ptrs,28));struct.pack_into('<I',ptr_copy,race*4,0x0202c000)
            m.put(0x0202c000,table_copy);m.put(0x0202b000,ptr_copy);m.put(0x080cd538,struct.pack('<I',0x0202b000))
            check(m.call(0x080cd50c,unit)==(135 if sure else 0),'Native Surefoot support fixture confirmed')
            if air==1:m.put(unit+0xfc,b'\x02')
            if air==2:m.put(bank+units.index(unit)*22+18,b'\x04')
            m.put(grid,bytes(0x98a))
            for y,x in itertools.product(range(16),repeat=2):m.call(0x08097814,grid,x,y,wrapper)
        check(machines[0].read(grid,0x98a)==machines[1].read(grid,0x98a),'Complete native movement grid identical')
        check(machines[0].read(0x02000000,0x40000)==machines[1].read(0x02000000,0x40000),'Native grid complete EWRAM identical')
        records.append(dict(kind=kind,air=air,surefoot=sure,gridSha256=sha(machines[1].read(grid,0x98a))))
    report=dict(status='passed',romSha1=view['romSha1'],controlRomSha1=parent['romSha1'],checks=dict(checks),records=records,inputHashes=pins,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=sum(checks.values()),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),case=case,checks=dict(checks),records=records,observedCalls=[dict(v) for v in counts] if 'counts' in globals() else []),indent=2)+'\n');print(out);raise
