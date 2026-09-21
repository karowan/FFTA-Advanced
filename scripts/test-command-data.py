"""Native command identity, additive discovery, and descriptor compatibility."""
import ast,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/probes'
image=(OUT/'command-data.gba').read_bytes();base=(OUT/'content-inventory.gba').read_bytes()
meta=json.loads((OUT/'command-data.json').read_text())
R=json.loads((ROOT/'build/expansion/registry.json').read_text())
SYMBOLS={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
assert hashlib.sha1(image).hexdigest()==meta['romSha1']
source=ast.parse((ROOT/'scripts/test-ability-core.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
a,b=ARM(image),ARM(base);cases={}
def check(value,label,group):
    assert value,label
    cases[group]=cases.get(group,0)+1
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
table=meta['addresses']['commands']-0x08000000
check(image[table:table+74*4]==clean[0x527244:0x527244+74*4],'Original command descriptors','data')
check(image[table+74*4:table+116*4]==bytes(42*4),'Reserved command holes','data')
for site in (0x25850,0x2632c,0x263cc,0x2647c,0x26660,0x26704,0x267d0,0x2892c,0x74c0c,0x7be7c,0x7da78):
    check(struct.unpack_from('<I',image,site)[0]==0x08000000+table,hex(site),'data')
for profile in meta['profiles']:
    name_id,help_id=struct.unpack_from('<HH',image,table+profile['jobId']*4)
    check((name_id,help_id)==(profile['nameId'],0),'New command descriptor','data')
    p=struct.unpack_from('<I',image,meta['addresses']['others']-0x08000000+name_id*4)[0]-0x08000000
    encoded=b''.join(b'\x40\x73' if c==' ' else bytes((0x80,ord(c)-ord('A')+0xb0 if c.isupper() else ord(c)-ord('a')+0xca)) for c in profile['name'])+b'\x00'
    check(image[p:p+len(encoded)]==encoded,'Native Other namespace name','data')

for race in R['races']:
    unit=a.setup(race['id']);b.setup(race['id'])
    for command in range(116):
        for cpu in (a,b):cpu.u.mem_write(unit+0x36,bytes((command,)))
        check(a.call(0x080c9078,unit)==b.call(0x080c9078,unit),f'old command {race["id"]}/{command}','native reverse command')
    for job in R['jobs']:
        if job.get('existing'):continue
        a.u.mem_write(unit+0x36,bytes((job['id'],)))
        check(a.call(0x080c9078,unit)==(job['id'] if job['race']==race['id'] else 0),'Race-safe command resolution','new reverse command')
    for index in range(race['nativeCount']):
        check(a.call(0x080c94d0,race['id'],index)==b.call(0x080c94d0,race['id'],index),'Original lesson owner','native reverse lesson')
for lesson in R['lessons']:
    for owner in lesson['owners']:
        check(a.call(0x080c94d0,owner['race'],owner['abilityIndex'])==owner['jobId'],lesson['id'],'new reverse lesson')

for race in R['races']:
    for all_flags in (False,True):
        for ap in (0,1,0x80,0xe4):
            unit=a.setup(race['id']);b.setup(race['id'])
            for cpu in (a,b):
                cpu.u.mem_write(unit+0x34,bytes((race['nativeCount'],)))
                cpu.u.mem_write(unit+0x40,bytes((ap,))*race['nativeCount'])
                if all_flags:
                    cpu.u.mem_write(0x02001f70,b'\xff'*16)
                    cpu.u.mem_write(0x02002ad0,b'\xff'*16)
                cpu.u.mem_write(0x02023ff0,b'\xa5'*288)
            old=b.call(0x080c8ebc,unit,0x02024000)
            new=a.call(0x080c8ebc,unit,0x02024000)
            old_ids=bytes(b.u.mem_read(0x02024000,old));new_ids=bytes(a.u.mem_read(0x02024000,new))
            check(new_ids[:old]==old_ids,'Native discovery prefix/order','discovery')
            expected=[j['id'] for j in R['jobs'] if not j.get('existing') and j['race']==race['id'] and a.call('ffta_new_job_eligible',unit,j['id'])]
            check(list(new_ids[old:])==expected,'Exactly eligible new commands','discovery')
            check(len(set(new_ids))==new and new<=15,'Command count/dedup bound','discovery')
            check(bytes(a.u.mem_read(0x02023ff0,16))==b'\xa5'*16 and bytes(a.u.mem_read(0x02024000+new,256-new))==b'\xa5'*(256-new),'Output guard','discovery')
# Run the installed command grey-row predicate through its real menu contract.
menu=0x02024000
def menu_fixture(cpu,unit):
    cpu.u.mem_write(menu,bytes(0x7264))
    cpu.u.mem_write(0x03002818,struct.pack('<I',menu))
    cpu.u.mem_write(menu+0x1d0c,struct.pack('<I',unit))
    cpu.u.mem_write(menu+0x1be4,bytes(cpu.u.mem_read(unit,264)))
for race in R['races']:
    for ap in (0,1,0x80,0xe4):
        unit=a.setup(race['id']);b.setup(race['id'])
        for cpu in (a,b):
            cpu.u.mem_write(unit+0x34,bytes((race['nativeCount'],)))
            cpu.u.mem_write(unit+0x40,bytes((ap,))*race['nativeCount'])
        for command in range(1,74):
            for cpu in (a,b):menu_fixture(cpu,unit)
            new=a.call(0x0807d8ec,command);old=b.call(0x0807d8ec,command)
            check(new==old,f'Native command browse {race["id"]}/{ap}/{command}','native browse')
            check(bytes(a.u.mem_read(menu+0x1be4,264))==bytes(b.u.mem_read(menu+0x1be4,264)),'Native preview side effects','native browse')
for job in R['jobs']:
    unit=a.setup(job['race']);menu_fixture(a,unit)
    command=job['id'] if not job.get('existing') else {2:2,16:8}[job['id']]
    for owner in [o for lesson in R['lessons'] for o in lesson['owners'] if o['jobId']==job['id']]:
        for value in (0,1,0x80,0xe4):
            a.ap(unit,owner['abilityIndex'],value)
            check(a.call(0x0807d8ec,command)==int(value!=0),'New lesson makes command browsable','expanded browse')
            a.ap(unit,owner['abilityIndex'],0)
    preview=bytes(a.u.mem_read(menu+0x1be4,264))
    check(preview[0x36]==command and preview[8]==job['id'],'New preview command/secondary identity','expanded browse')
report={'passed':True,'romSha1':meta['romSha1'],'cases':cases,'total':sum(cases.values()),'remaining':['Battle command usable predicates','Job wheel and explicit primary/secondary action rows','Action dispatch and command help']}
(OUT/'command-data-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
