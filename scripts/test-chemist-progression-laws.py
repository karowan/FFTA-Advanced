"""Native elemental and harmful-status law queries from real action results.

The native executor creates the result masks. No success flags, custom law
receipts, or post-cast status results are injected by this test.
"""
import json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-chemist-progression-effects.py'
exec(compile(source.read_text().split('\ntry:\n')[0],str(source),'exec'))
out=Path(meta['path']).parent/'laws';out.mkdir(exist_ok=True)
LAW=0x0203e000

def query(action,kind,value,mask=0):
 m.put(LAW,bytes(4)+bytes((kind,value))+bytes(10))
 m.put(STACK,struct.pack('<4I',0,0,mask,LAW))
 before=m.read(UNIT,264)+m.read(TARGET,264)+m.read(record(TARGET),27)+m.read(0x030034b0,4)
 result=m.call(0x081343c8,UNIT,TARGET,action,0,stack=STACK)
 check('law-query-pure',m.read(UNIT,264)+m.read(TARGET,264)+m.read(record(TARGET),27)+m.read(0x030034b0,4),before)
 return result

try:
 for action,element in ((453,1),(454,6),(455,0),(459,1)):
  for seed in range(6):
   case=(action,seed);execute_damage(action,seed)
   rows=[]
   for i in range(14):
    o=regs[0]+i*0x2c4
    if m.word(o)!=wrappers[UNIT] or int.from_bytes(m.read(o+16,2),'little')!=action:continue
    for j in range(m.read(o+0x2c0,1)[0]):
     row=o+0x20+j*0x2c
     if m.word(row)==wrappers[TARGET]:rows.append(row)
   check('native-recipient-row',bool(rows),True)
   for value in range(1,9):
    check('native-element-forecast',query(action,2,value),int(value==element))
    for row in rows:check('native-element-committed',query(action,2,value,row+0x14),int(value==element))
   if action==459:
    applied=bool(m.read(record(TARGET)+23,1)[0]>>6)
    for row in rows:check('Fuse-real-application-law',query(action,16,0,row+0x14),int(applied))
 result=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks))
except BaseException as error:
 result=dict(passed=False,romSha1=meta['romSha1'],checks=dict(checks),case=case,error=repr(error));raise
finally:(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
