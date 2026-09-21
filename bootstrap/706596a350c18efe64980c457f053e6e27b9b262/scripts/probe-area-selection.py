"""Read-only native area candidate/direction geometry audit."""
import runpy,struct,json
q=runpy.run_path('scripts/probe-tomahawk-geometry.py')
m=q['m'];ROOT=q['ROOT'];GRID=q['GRID'];UNIT=q['UNIT']
BUFFER=0x02027000;OUTPUT=0x02029000
m.fixture(2,[52]);m.put(GRID,bytes((16,0))*256)
result={}
for action in (92,102,103,113,180):
 for mode in (0,1):
  for facing in range(4):
   descriptor=bytearray(16);struct.pack_into('<I',descriptor,0,UNIT)
   descriptor[4:8]=bytes((6,6,6,6));struct.pack_into('<HH',descriptor,8,action,52)
   m.put(BUFFER,descriptor);m.put(OUTPUT,b'\xa5'*1024)
   count=m.call(0x080b4a1c,BUFFER,facing,mode,OUTPUT)
   result[f'{action}/{mode}/{facing}']=[list(m.read(OUTPUT+i*4,4)) for i in range(count)]
print(json.dumps(result,indent=2))
(ROOT/'build/expansion/probes/native-area-selection.json').write_text(json.dumps(result,indent=2))
