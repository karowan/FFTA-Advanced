"""Execute native actor rendering with all palette offsets on one retained body."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
capture=ROOT/'build/art/explicit-walk/20260918T013433.309654Z'
assert sha((capture/'report.json').read_bytes())=='0a3d7cab394bf947c9a0d51df940b65aa81e1febd19e15e61b542537cbaa6f76'
proof=json.loads((capture/'report.json').read_text());assert proof['status']=='passed'
meta=json.loads((ROOT/'build/art/generated-actions/refined-samurai-current.json').read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==proof['romSha1']=='0fa7d1707e2d85fb2a8602f061b5eb4479ff3211'
ram=(capture/'mapped-ready.ram').read_bytes();assert sha(ram)=='0ca0ae3656f8c1ad4af9d5fceb36d3786d04c609c095c7dc0259629819183159'
actor=proof['observations']['mapped']['ready']['actor'];address=0x02000000+actor['address']
iw=(Path(meta['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes()
out=ROOT/'build/art/native-palette'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    check(actor['resource']==256 and actor['displayedFrames'] and actor['declaredSequence'],'Retained Samurai body is a directly verified native frame')
    baseline=None
    for bank in range(16):
        a=ARM(rom,iw);a.put(0x02000000,ram)
        # Declared isolated renderer inputs: fresh native OAM counter/buffer0,
        # retained actor object, screen position64/64 and palette offset0..15.
        a.put(0x03000020,bytes(12));a.put(0x03000030,bytes(1024))
        context=struct.pack('<hh7B',64,64,0,0,0,0,0,bank,0);a.put(0x02008000,context)
        before=a.read(address,72)
        a.call(0x080216f8,address,0x02008000)
        count=a.word(0x03000020);raw=a.read(0x03000030,8)
        x,y,z=struct.unpack_from('<3H',raw)
        base=ram[actor['address']+0x1c]+ram[actor['address']+0x1d]
        records.append(dict(offset=bank,actorBase=base,oam=raw.hex(),count=count))
        check(count==1,f'Bank{bank}: native renderer emits exactly one object')
        check(z>>12==(base+bank)&15 and z&1023==actor['tile'],f'Bank{bank}: exact palette offset and retained tile owner')
        check((x&0xe300)==0 and y>>14==2,f'Bank{bank}: unchanged ordinary32x32 4bpp object')
        normalized=raw[:4]+struct.pack('<H',z&0xfff)+raw[6:]
        if baseline is None:baseline=normalized
        check(normalized==baseline,f'Bank{bank}: only palette nibble changes')
        check(a.read(address,72)==before and a.read(0x02008000,len(context))==context,f'Bank{bank}: actor and renderer context unchanged')
    result=dict(status='passed',romSha1=proof['romSha1'],checks=checks,records=records,
        sourceReport=str(capture/'report.json'),sourceReportSha256=sha((capture/'report.json').read_bytes()),ramSha256=sha(ram),iwramSha256=sha(iw),
        scope='Native216F8 renderer adds context byte9 to actor bytes1C/1D for all16 OAM palette offsets; byte10 controls priority. Exact geometry/tile/actor/context preservation. This does not allocate a free bank, load custom colors, execute VBlank or establish full game coexistence.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as e:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(e),checks=checks,records=records),indent=2)+'\n');print(str(out));raise
