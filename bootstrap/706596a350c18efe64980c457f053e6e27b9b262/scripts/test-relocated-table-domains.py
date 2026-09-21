"""Audit full native namespaces preserved by relocated expansion tables.

Uses structural boundaries, native referenced indexes, exact original prefixes,
and native job/help consumers. The separate racial-table test owns all24 racial
getter executions; this test checks that pointer table's allocation only.
"""
import ast,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/probes';clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
foundation=(ROOT/'build/foundation/FFTA_vanillaplus_dev.gba').read_bytes()
assert hashlib.sha1(foundation).hexdigest()==json.loads((ROOT/'build/foundation/manifest.json').read_text())['outputSha1']
assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
def u16(b,p):return struct.unpack_from('<H',b,p)[0]
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
stages={}
for name in ('job-data','content-data','command-data','action-data'):
    meta=json.loads((OUT/(name+'.json')).read_text());rom=(OUT/(name+'.gba')).read_bytes()
    assert hashlib.sha1(rom).hexdigest()==meta['romSha1'],('stale stage',name)
    stages[name]=(meta,rom)
counts={};domains=[];failures=[];allocations={}
def check(group,value,label):
    if not value:failures.append({'group':group,'detail':label})
    counts[group]=counts.get(group,0)+1
def allocation(stage,key):
    if (stage,key) in allocations:return allocations[stage,key]
    meta,rom=stages[stage];address=meta['addresses'][key]
    matches=[a for a in meta['allocations'] if a['address']==address]
    check('allocation_identity',len(matches)==1,(stage,key))
    allocations[stage,key]=matches[0]
    return matches[0]
def original_prefix(stage,key,base,count,stride,reference=None):
    reference=clean if reference is None else reference
    meta,rom=stages[stage];a=allocation(stage,key);offset=a['offset']
    check('native_capacity',a['bytes']>=count*stride,(stage,key,count))
    for i in range(count):
        check('original_record',rom[offset+i*stride:offset+(i+1)*stride]==reference[base+i*stride:base+(i+1)*stride],(stage,key,i))
    domains.append({'stage':stage,'table':key,'originalBase':hex(base),'nativeCount':count,'stride':stride,'allocatedCount':a['bytes']//stride})
    return a
job,jobrom=stages['job-data'];content,contentrom=stages['content-data'];command,commandrom=stages['command-data'];action,actionrom=stages['action-data']
original_prefix('job-data','jobs',0x521a14,116,52)
original_prefix('job-data','names',0x526680,753,4)
original_prefix('content-data','items',0x51d180,376,32)
original_prefix('content-data','teaching',0x520080,225,20)
original_prefix('content-data','others',0x5567f0,767,4,foundation)
original_prefix('command-data','others',0x5567f0,767,4,foundation)
original_prefix('command-data','commands',0x527244,74,4)
original_prefix('action-data','actions',0x55187c,347,28)
check('physical_boundary',0x526680+753*4==0x527244,'item/job names end at commands')
check('physical_boundary',0x527244+74*4==0x52736c,'commands end at support metadata')
check('physical_boundary',0x55187c+347*28==0x553e70,'actions including Blank Card346 end at descriptors')
check('physical_boundary',0x51d0f4+35*4==0x51d180,'permissions end at biased item0')
check('physical_boundary',0x51d180+376*32==0x520080,'equipment including item0 ends at teaching table')
check('physical_boundary',u32(clean,0x51ba84)==0x0851ba84+24*4,'native racial pointer table ends at bank0')
check('native_capacity',allocation('content-data','races')['bytes']>=24*4,'all native racial banks allocated; getters audited separately')

jobs=[clean[0x521a14+i*52:0x521a14+(i+1)*52] for i in range(116)]
max_permission=max(row[0x2d] for row in jobs);max_requirement=max(row[0x30] for row in jobs)
check('referenced_domain',max_permission==34,('highest original permission',max_permission))
reqbase=u32(clean,0xc8b18)-0x08000000
original_prefix('job-data','permissions',0x51d0f4,max_permission+1,4)
original_prefix('content-data','permissions',0x51d0f4,max_permission+1,4)
original_prefix('job-data','requirements',reqbase,max_requirement+1,4)
for index,row in enumerate(jobs):
    check('referenced_domain',u16(row,0)<753,('job name',index,u16(row,0)))
    check('referenced_domain',row[0x10]<74,('job command',index,row[0x10]))
    check('referenced_domain',row[0x2d]*4<allocation('job-data','permissions')['bytes'],('job mask',index))
    check('referenced_domain',row[0x30]*4<allocation('job-data','requirements')['bytes'],('job prereq',index))
sets=[]
for index in range(376):
    p=0x51d180+index*32;teaching=clean[p+29];sets.append(teaching)
    check('referenced_domain',teaching<225,('item teaching',index,teaching))
    check('referenced_domain',u16(clean,p)<753,('item name',index,u16(clean,p)))
check('referenced_domain',max(sets)==224,('highest native teaching set',max(sets)))
for index in range(225):
    p=0x520080+index*20;n=clean[p]
    check('referenced_domain',n<=9,('teaching row capacity',index,n))
    for j in range(n):check('referenced_domain',clean[p+2+j*2]<116 or clean[p+2+j*2]==255,('teaching job or native wildcard255',index,j))
for index in range(74):check('referenced_domain',u16(clean,0x527244+index*4)<767,('command Other-name',index))
for index in range(347):check('referenced_domain',u16(clean,0x55187c+index*28)<767,('action Other-name',index))
# Expanded references also remain inside allocated tables; inherited job-data
# allocations persist in the content/command ROMs.
for index in range(126):
    row=contentrom[job['addresses']['jobs']-0x08000000+index*52:job['addresses']['jobs']-0x08000000+(index+1)*52]
    check('expanded_domain',u16(row,0)<allocation('job-data','names')['bytes']//4,('expanded job name',index))
    check('expanded_domain',row[0x10]<126,('expanded command',index))
    check('expanded_domain',row[0x2d]<allocation('content-data','permissions')['bytes']//4,('expanded permissions',index))
    check('expanded_domain',row[0x30]<allocation('job-data','requirements')['bytes']//4,('expanded prerequisite',index))
for index in range(461):
    p=content['addresses']['items']-0x08000000+index*32
    check('expanded_domain',u16(contentrom,p)<848,('expanded item name',index))
    check('expanded_domain',u16(contentrom,p+29)<310,('expanded teaching',index))

# Native help mapper iterates exactly11 ranges (19A80 compares index<=10).
# Preserve the first10 ranges. The original eleventh entry is zero padding;
# append the extension there without hiding any previously valid help range.
help_alloc=allocation('content-data','helpBanks');help_offset=help_alloc['offset']
check('native_capacity',help_alloc['bytes']==11*8,'native help scanner11 rows')
check('original_record',contentrom[help_offset:help_offset+80]==clean[0x36da1c:0x36da1c+80],'original ten help ranges')
old_ranges=[struct.unpack_from('<4H',clean,0x36da1c+8*i) for i in range(11)]
native_action_help=next(row for row in old_ranges if row[0]==23)
check('physical_boundary',native_action_help[2]-native_action_help[1]+1==347,'native action-help bank independently covers347 actions')
check('help_domain',old_ranges[10]==(0,0,0,0),'original final scan slot is zero padding')
check('help_domain',struct.unpack_from('<3H',contentrom,help_offset+80)==(0x13,0x1de,0x6a4),'extension occupies final scan slot')
namespace=dict(globals());s=ast.parse((ROOT/'scripts/test-content-data.py').read_text())
exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native text>', 'exec'),namespace)
native,modified,job_machine=namespace['ARM'](clean),namespace['ARM'](contentrom),namespace['ARM'](jobrom)
for index in range(116):
    for selector in range(48):
        try:check('native_job_getter',job_machine.call(0x080c8570,index,2,selector)==native.call(0x080c8570,index,2,selector),(index,selector))
        except Exception as error:raise AssertionError(('native job execution',index,selector)) from error
for bank,first,last,reserved in old_ranges[:10]:
    for help_id in range(first,last+1):check('native_help_mapping',modified.map_help(help_id)==native.map_help(help_id),(help_id,bank))
native_bank13=next(row for row in old_ranges if row[0]==0x13)
for index in range(native_bank13[2]-native_bank13[1]+1):
    before=native.decode_help(0x13,index);after=modified.decode_help(0x13,index)
    check('native_help_text',before==after,index)
report={'passed':not failures,'checks':sum(counts.values()),'groups':counts,'failures':failures,'stageHashes':{n:m['romSha1'] for n,(m,b) in stages.items()},'domains':domains,
        'maxNativePermission':max_permission,'maxNativeRequirement':max_requirement,'originalHelpRanges':old_ranges,
        'scope':'Full relocated original prefixes, structural/native referenced domains, native job selectors and valid original help mapping/text. Not an exhaustive arbitrary-invalid-index hardening claim.'}
(OUT/'relocated-table-domain-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('domains','originalHelpRanges')},indent=2))
if failures:raise SystemExit(1)
