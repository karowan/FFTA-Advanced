import runpy,json,struct
q=runpy.run_path('scripts/probe-tomahawk-geometry.py');m=q['m'];GRID=q['GRID'];UNIT=q['UNIT'];STACK=q['STACK'];root=q['ROOT']
m.fixture(2,[52]);m.put(GRID,bytes((16,0))*256)
results={}
for action in (92,102,103,113,180):
 cells=[]
 for dy in range(-5,6):
  for dx in range(-5,6):
   m.put(STACK,struct.pack('<4I',6+dy,action,52,0));r=m.call(0x080a0254,UNIT,6,6,6+dx)
   if r:cells.append((dx,dy))
 results[action]=cells
print('Raw membership executions:', 5*121)
(root/'build/expansion/probes/physical-native-area.json').write_text(json.dumps(results,indent=2))
BUFFER=0x02027000;OUTPUT=0x02029000;final={}
for action in (92,102,103,113,180):
 for facing in range(4):
  descriptor=bytearray(16);struct.pack_into('<I',descriptor,0,UNIT);descriptor[4:8]=bytes((6,6,6,6));struct.pack_into('<HH',descriptor,8,action,52);m.put(BUFFER,descriptor);m.put(OUTPUT-8,b'\xa5'*1040)
  count=m.call(0x080b4a1c,BUFFER,facing,1,OUTPUT);assert count<=256
  cells=[tuple(m.read(OUTPUT+i*4,2)) for i in range(count)];assert m.read(OUTPUT-8,8)==b'\xa5'*8 and m.read(OUTPUT+count*4,8)==b'\xa5'*8
  final[f'{action}/{facing}']=cells
print('Enumerated native area:',final)
(root/'build/expansion/probes/physical-native-area.json').write_text(json.dumps({'scope':'Clean native A0254 raw membership vs actual B4A1C mode1 area enumeration; flat16x16 real grid; not a committed attack','rawPredicate':results,'enumerated':final},indent=2))

# Clarification: approved area probe expectations are the actual list, not A0254 bounds.
for action in (92,102,113):
 for facing in range(4):assert set(final[f'{action}/{facing}'])=={(5,6),(6,5),(7,6),(6,7)}
for facing in range(4):assert set(final[f'180/{facing}'])=={(6,6),(5,6),(6,5),(7,6),(6,7)}
