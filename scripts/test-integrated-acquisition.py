"""Installed candidate's complete teaching stock, pricing and purchase matrix.

Reuse the independent approved-ledger/native-stock oracle without executing
the legacy suite or overlaying its bootstrap binary onto the current ROM.
Original progression flags are declared inputs; campaign earning is separate.
"""
import ast,datetime,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
path=pathlib.Path(meta['path']);image=path.read_bytes();sha=lambda b:hashlib.sha1(b).hexdigest()
assert sha(image)==meta['romSha1']
OUT=path.parent/('integrated-acquisition-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));OUT.mkdir()
fix=path.parent/'fixture';proof=json.loads((fix/'prepare-cache.json').read_text())
assert (fix/'frozen.gba').read_bytes()==image
iwram=(fix/'battle-ready.iwram').read_bytes();assert sha(iwram)==proof['outputs']['battle-ready.iwram']
ROM=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert sha(ROM)=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
tree=ast.parse((ROOT/'scripts/test-battle-inventory.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
def machine():return ARM(iwram)
RECORDS=[7,13,19]
TOWNS={2:'Cyril',3:'Sprohm',4:'Muscadet',5:'Cadoan',6:'Baguba Port'}
source=(ROOT/'scripts/test-acquisition-gates.py').read_text()
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('stock_checks','block')],type_ignores=[]),'<native acquisition oracle>','exec'))
failure=None;result=None
try:result=stock_checks(image)
except BaseException as error:failure=repr(error)
report=dict(passed=failure is None,romSha1=meta['romSha1'],oracleSha1=sha(source.encode()),
            ledgerSha1=sha((ROOT/'notes/equipment-acquisition.json').read_bytes()),
            inputs=dict(gates=RECORDS,towns=TOWNS,territories=[0,7,30],tiers=[0,10,20],ranks=[0,1,5],quantities=[1,3]),
            result=result,failure=failure,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],result=result,failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
