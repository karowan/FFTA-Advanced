import ast,ctypes as C,hashlib,importlib.util,pathlib,struct,sys,json
ROOT=pathlib.Path.cwd();sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
s=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native>','exec'))
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();m=ARM(rom,iwram_from_boot());GRID=0x02026000;reads=[]
def watched(u,access,address,size,value,data):reads.append((address-GRID)//2)
m.u.hook_add(UC_HOOK_MEM_READ,watched,begin=GRID,end=GRID+511)
results=[]
for action in (134,147,148):
 for delta in (-10,-4,-3,0,3,4,10):
  for obstacle in (0,1,8,9,255):
   for distance in (3,4,5):
    m.fixture(2,[52]);grid=bytearray(bytes((16,0))*256);grid[2*(6*16+6+distance)]=16+delta
    for x in range(7,6+distance):grid[2*(6*16+x):2*(6*16+x)+2]=bytes((255 if obstacle else 16,obstacle))
    m.put(GRID,grid);header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=header[13]=header[15]=16;m.put(0x02007f10,header)
    m.put(STACK,struct.pack('<4I',6,action,52,0));reads=[];r=m.call(0x080a0014,UNIT,6,6,6+distance)
    assert not any(6*16+6<x<6*16+6+distance for x in reads),(action,reads)
    assert r==int(distance<=(3 if action==134 else 4)),(action,delta,obstacle,distance,r)
    results.append({'action':action,'heightDifference':delta,'intermediateTerrainFlags':obstacle,'distance':distance,'result':r,'tileReads':sorted(set(reads))})
out={'passed':True,'cases':len(results),'scope':'Clean native A0014 real grid: no intervening tile reads and no height cap for original134/147/148; not a complete native projectile executor','results':results}
(ROOT/'build/expansion/probes/tomahawk-native-geometry.json').write_text(json.dumps(out,indent=2));print(out['scope'],len(results))
