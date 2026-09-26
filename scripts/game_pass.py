"""Health monitor and fixed-input route runner for whole-game passes.

A route is a list of (keys, wait frames, checkpoint label or None). Keys use
libretro bits; a checkpoint screenshots the frame and records the monitor's
view: resident IWRAM code unchanged, the lowest stack address reached (stack
canary below the live frames), the unused high-EWRAM guard, the native heap
walk and the number of distinct 8x8 screen tiles. Problems are collected, not
raised, so one pass reports every broken screen.
"""
import ast, ctypes as C, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
_tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[x for x in _tree.body if isinstance(x,ast.FunctionDef) and x.name=='heap'],type_ignores=[]),'<native heap walk>','exec'))
KEYS=dict(B=1,SEL=4,ST=8,U=16,D=32,L=64,R=128,A=256,RB=2048,LB=1024,N=0)
CODE=(0x6170,0x6d68)                 # resident IWRAM code (IWRAM offsets)
CANARY=(0x6d70,0x7800,0xa5)          # stack region below live frames at a frame boundary
GUARD=(0x3ff4c,0x40000,0xd7)         # unused high EWRAM after the scope pointers

class Pass:
    def __init__(self,emulator,out,prefix=''):
        self.e=emulator;self.out=out;self.prefix=prefix;self.problems=[];self.points=[];self.inputs=[]
    def arm(self):
        """Call after loading a state: snapshot code, lay the canary and guard."""
        iw=C.string_at(*self.e.maps[0x03000000]);self.code=iw[CODE[0]:CODE[1]]
        a,b,v=CANARY;C.memmove(self.e.maps[0x03000000][0]+a,bytes([v])*(b-a),b-a)
        a,b,v=GUARD;self.e.set_memory(a,bytes([v])*(b-a))
    def distinct(self):
        raw,w,h,pitch,px=self.e.frame;bpp=4 if px==1 else 2
        return len({b''.join(bytes(raw[(y+j)*pitch+x*bpp:(y+j)*pitch+(x+8)*bpp]) for j in range(8))
                    for y in range(0,h,8) for x in range(0,w,8)})
    def lowest_stack(self):
        iw=C.string_at(*self.e.maps[0x03000000]);a,b,v=CANARY
        for i in range(a,b):
            if iw[i]!=v:return 0x03000000+i
        return 0x03000000+b
    def check(self,label,min_tiles=40):
        iw=C.string_at(*self.e.maps[0x03000000]);ram=self.e.memory();point=dict(label=self.prefix+label)
        if iw[CODE[0]:CODE[1]]!=self.code:self.problems.append((point['label'],'resident IWRAM code changed'))
        low=self.lowest_stack();point['stackLow']=hex(low);point['stackMargin']=low-0x03006d68
        if low<0x03006d68+0x100:self.problems.append((point['label'],f'stack reached {low:#x} (margin {low-0x03006d68})'))
        a,b,v=GUARD
        if ram[a:b]!=bytes([v])*(b-a):self.problems.append((point['label'],'unused high EWRAM written'))
        try:
            h=heap(ram);point['heap']=dict(end=hex(h.get('end',0)),free=h.get('freePayload'),largest=h.get('largestFree'))
        except AssertionError as error:
            self.problems.append((point['label'],f'native heap chain invalid {error}'));point['heap']='invalid'
        point['tiles']=self.distinct()
        if point['tiles']<min_tiles:self.problems.append((point['label'],f"only {point['tiles']} distinct tiles"))
        self.e.screenshot(self.out/(point['label']+'.png'));self.points.append(point)
        return point
    def run(self,route):
        for keys,wait,label in route:
            bits=0
            for k in keys.split('+'):bits|=KEYS[k]
            self.e.run(8,bits);self.e.run(wait);self.inputs.append([keys,wait,label])
            if label:self.check(label)
