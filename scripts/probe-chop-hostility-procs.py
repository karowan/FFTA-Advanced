"""Native Charm/control contracts and original equipment-help evidence.

Clean-ROM native functions run in disposable Unicorn RAM. This establishes
status ownership and item effect meaning, not committed Chop effect coverage.
"""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
s=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native harness>','exec'))
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
m=ARM(rom,iwram_from_boot());counts={}
def check(group,actual,expected):
    assert actual==expected,(group,actual,expected)
    counts[group]=counts.get(group,0)+1
for status,value,side in itertools.product(range(256),(0,1),(0,1)):
    unit=bytearray(264);unit[0xeb]=status;struct.pack_into('<H',unit,0x28,side<<15)
    m.put(UNIT,unit);m.call(0x080ce124,UNIT,value)
    expected=bytearray(unit);expected[0xeb]=(status&~32)|(value<<5)
    check('Charm_exact_mutation',m.read(UNIT,264),expected)
    check('Charm_getter',m.call(0x080cdb6c,UNIT),value)
    check('base_side_unchanged',m.call(0x080c8240,UNIT),side)
    check('Confusion_getter',m.call(0x080cdb54,UNIT),(status>>4)&1)
ctx,target=0x02024000,0x02025000
for preview,targetid,side,stack in itertools.product((0,1),(0,1,12,255),(0,1),(STACK,STACK+4)):
    actor=bytearray(264);actor[0xed]=0xa5;actor[0xe6]=87;struct.pack_into('<H',actor,0x28,side<<15)
    receiver=bytearray(264);receiver[0x104]=targetid;receiver[0xeb]=32
    struct.pack_into('<H',receiver,0x28,(1-side)<<15)
    m.put(UNIT,actor);m.put(target,receiver)
    context=bytearray(64);struct.pack_into('<III',context,0,UNIT,target,target);struct.pack_into('<H',context,0x26,preview*16)
    m.put(ctx,context);m.call(0x0813363c,ctx,stack=stack)
    expected=bytearray(actor)
    if not preview:expected[0xed]|=8;expected[0xe6]=targetid
    check('Control_actor_ownership',m.read(UNIT,264),expected)
    check('Control_target_unchanged',m.read(target,264),receiver)
    check('Control_context_unchanged',m.read(ctx,64),context)
    check('Control_getter',m.call(0x080cdca4,UNIT),0 if preview else 1)
    check('Control_targetID_getter',m.call(0x080ce410,UNIT),87 if preview else targetid)
# Decode actual native compressed help, retaining raw bytes as the primary
# evidence. ASCII-readable extraction only makes the status labels searchable.
namespace=dict(globals());s=ast.parse((ROOT/'scripts/test-content-data.py').read_text())
exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','u16','u32')],type_ignores=[]),'<native text>', 'exec'),namespace)
text_machine=namespace['ARM'](rom)
def readable(raw):
    result='';i=0
    while i<len(raw):
        if raw[i]==128 and i+1<len(raw):
            z=raw[i+1];i+=2
            if 176<=z<=201:result+=chr(65+z-176)
            elif 202<=z<=227:result+=chr(97+z-202)
            elif 166<=z<=175:result+=chr(48+z-166)
            elif z==244:result+="'"
            else:result+=' '
        elif raw[i]==64 and i+1<len(raw):result+=' ';i+=2
        else:i+=1
    return ' '.join(result.split())
help_rows=[]
for item,label in ((53,'Petrify'),(54,'Slow'),(55,'Doom'),(56,'Confusion'),(57,'Poison'),(58,'KO'),(59,'Charm'),(60,'Silence'),(61,'Sleep'),(121,None),(124,None)):
    record=rom[0x51d180+item*32:0x51d180+(item+1)*32]
    help_id=struct.unpack_from('<H',record,2)[0]
    bank,index=text_machine.map_help(help_id);_,raw,_=text_machine.decode_help(bank,index)
    raw=raw[:raw.index(0)];text=readable(raw)
    if label:check('native_help_immunity',('null' in text and label in text),True)
    help_rows.append({'item':item,'effects':list(record[0x1a:0x1d]),'nativeHelp':text,'decodedBytes':list(raw)})
report={'passed':True,'cleanSha1':hashlib.sha1(rom).hexdigest(),'checks':sum(counts.values()),'groups':counts,'nativeItemHelp':help_rows,
        'scope':'Native Charm setters/getters, native Control application including preview, native compressed original item help. No claim of exhaustive committed weapon-effect suppression.'}
(ROOT/'build/expansion/probes/chop-hostility-procs-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='nativeItemHelp'},indent=2))
for row in help_rows:print(row['item'],row['effects'],row['nativeHelp'])
