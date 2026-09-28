"""Read-only-on-the-live-core diagnostic forecasts for declared tactical cases.

All scratch allocation and native queries run on a private ARM memory clone.
These recipient rows diagnose admission/value; they do not establish reachable
placement, actual damage, or the chosen turn's optimality. No synthetic scores.
"""
import ast
import struct
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

RETURN,STACK=0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))


def forecast_rows(rom,ram,iwram,wrappers,actor,case):
    machine=ARM(rom,iwram)
    machine.put(0x02000000,ram)
    row=machine.call(0x08022840,20)
    assert 0x02000000<=row<0x0203f000
    if case['category'] in ('healing','revival','support'):
        targets=[0x30cc,actor]
        actions=[0,1,2,3,4,5,6,7,8,9]
    else:
        targets=[128]
        actions=[0,23,26,29] if 'caster' in case['id'] else [0]
    results=[]
    protected=b''.join(machine.read(0x02000000+u,264) for u in sorted(wrappers))+machine.read(0x030034b0,4)
    for target in targets:
        for action in actions:
            admitted=machine.call(0x08133e18,0x02000000+actor,action,128)
            machine.put(row,bytes(20));machine.put(STACK,bytes(8))
            machine.call(0x080c2618,row,0x02000000+wrappers[actor],0x02000000+wrappers[target],action)
            values=struct.unpack('<10h',machine.read(row,20))
            results.append(dict(target=target,action=action,usable=bool(admitted),row=list(values)))
    after=b''.join(machine.read(0x02000000+u,264) for u in sorted(wrappers))+machine.read(0x030034b0,4)
    assert after==protected, 'Forecast changed canonical units or RNG on its clone'
    return results
