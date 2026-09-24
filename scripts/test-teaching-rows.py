"""Native ARM checks for equipment lesson rows on every item record.

Runs the native row builder (C8D14) on the job-visibility parent and the
teaching-row candidate with guard bytes around its 28-byte buffer, then checks
the lesson AP/type selections used by the three equipment-help consumers.
"""
import ast, ctypes as C, datetime, hashlib, importlib.util, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# --current selects a later bounded stage that retains the teaching-row patch.
CURRENT=sys.argv[sys.argv.index('--current')+1] if '--current' in sys.argv else 'build/expansion/teaching-rows/current.json'
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
BUF,ROW,ENTRY=0x02010000,0x02010100,0x02010200
BUILDER,SET_INDEX,SET_TABLE=0x080c8d14,0x080ca7a4,0x080c8d54
meta=json.loads(Path(json.loads((ROOT/CURRENT).read_text())['manifest']).read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
parent=json.loads(Path(meta['teachingRows']['parent']).read_text());base=Path(parent['path']).read_bytes()
assert hashlib.sha1(base).hexdigest()==meta['teachingRows']['baseSha1']
symbols=meta['teachingRows']['symbols']
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
lessons={l['id']:l for l in registry['lessons']}
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<native-harness>','exec'))
iw=iwram_from_boot();native,changed=ARM(base,iw),ARM(rom,iw)
checks=[];cases=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def build(m,item):
    m.put(BUF-16,b'\xa5'*16+bytes(28)+b'\xa5'*36)
    n=m.call(BUILDER,item,BUF)
    raw=m.read(BUF,28);guarded=m.read(BUF-16,16)==b'\xa5'*16 and m.read(BUF+28,36)==b'\xa5'*36
    count=struct.unpack_from('<H',raw,0)[0]
    rows=[]
    for r in range(min(count,3)):
        name,badges=struct.unpack_from('<HH',raw,4+r*8);rows.append((name,list(raw[8+r*8:8+r*8+min(badges,4)])))
    return n,count,rows,raw,guarded
def teaching_set(m,item):
    at=m.call(SET_INDEX,item,0x12)*20+m.word(SET_TABLE)
    n=m.read(at,1)[0];return at,[tuple(m.read(at+2+i*2,2)) for i in range(n)]
def lesson(m,job,index):
    jobs=m.word(0x080c8de4);race=m.read(jobs+job*52+4,1)[0]
    at=m.call(0x080cd480,race,index);return at,struct.unpack('<H',m.read(at,2))[0],m.read(at+6,1)[0],m.read(at+7,1)[0]*10
def matches(m,row,entry):
    m.put(ROW,struct.pack('<HH',row[0],len(row[1]))+bytes(row[1]+[0]*(4-len(row[1]))));m.put(ENTRY,bytes(entry))
    return m.call(symbols['ffta_teaching_row_match'],ROW,ENTRY)
by_item={i['romItemId']:i for i in registry['items']}
overflow=[];vanilla_ap_changes=[]
for item in range(0,461):
    old=build(native,item);new=build(changed,item)
    if old[1]>3 or not old[4]:overflow.append(item)
    check(new[0]==new[1]<=3 and new[4],f'item {item} builds at most three guarded rows')
    address,entries=teaching_set(changed,item)
    expected=None
    if item in by_item:
        expected=[]
        for owner in by_item[item]['teaching']:
            lid=owner['lesson'];name=lessons[lid]['nameId']
            if expected and expected[-1][0]==name and expected[-1][2]==lid:expected[-1][1].append(owner['jobId'])
            else:expected.append([name,[owner['jobId']],lid])
        check([(n,j) for n,j,_ in expected]==new[2],f'item {item} merges racial rows per lesson')
    else:
        check(new[:4]==old[:4],f'original item {item} rows unchanged')
    for r,row in enumerate(new[2]):
        first=next(e for e in entries if matches(changed,row,e))
        _,name,kind,ap=lesson(changed,*first)
        check(name==row[0] and first[0]==row[1][0],f'item {item} row {r} AP lookup selects its own lesson')
        if expected:
            check(ap==lessons[expected[r][2]]['ap'],f'item {item} row {r} shows lesson AP')
        else:
            legacy=next(e for e in entries if e[0]==row[1][0])
            if lesson(changed,*legacy)[3]!=ap:vanilla_ap_changes.append(dict(item=item,row=r,before=lesson(changed,*legacy)[3],after=ap))
    if new[2]:
        changed.put(BUF,new[3])
        chosen=changed.call(symbols['ffta_teaching_first_lesson'],BUF,address,0x08000000)
        row0=next(e for e in entries if matches(changed,new[2][0],e))
        check(chosen==lesson(changed,*row0)[0],f'item {item} type icon uses first row lesson')
    cases.append(dict(item=item,parentRows=old[1],parentGuarded=old[4],rows=[dict(nameId=n,jobs=j) for n,j in new[2]]))
four=sorted(i for i,it in by_item.items() if len(it['teaching'])==4)
check(overflow==four,'parent overflow is exactly the ten four-entry expansion items')
check(not vanilla_ap_changes,'original items keep their displayed AP')
family=[i for i,it in by_item.items() if len({o['jobId'] for o in it['teaching']})>1]
check(all(len(c['rows'])==len(by_item[c['item']]['lessons']) for c in cases if c['item'] in family),
      'each multi-race expansion item shows one row per lesson')
out=Path(meta['path']).parent/('native-rows-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
out.mkdir()
report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=meta['teachingRows']['baseSha1'],checks=len(checks),
    uniqueChecks=len(set(checks)),parentOverflowItems=overflow,items=cases,nativeCalls=native.calls+changed.calls)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),parentOverflowItems=overflow,report=str(out/'report.json'))))
