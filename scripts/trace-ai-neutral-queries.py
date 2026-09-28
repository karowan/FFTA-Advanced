"""Read-only query admission trace on a retained fully learned Black Mage turn.

No new fixture: reproduce the declared constructor seed, then observe selected
compiled function entry/return instructions. All instructions execute normally
and final EWRAM must match the ordinary timing run exactly. Raw unit samples
remain ignored evidence, not source or shareable artifacts.
"""
import struct
import collections, ctypes as C, hashlib, json, re, runpy
from pathlib import Path
from contextlib import ExitStack
from chemist_candidate import ROOT,candidate
from ai_planner_seed import PlannerSeed,BOUNDARY
from mgba_instruction_trace import InstructionTrace
BASE=ROOT/'build/expansion/ai-timing'
source=Path(json.loads((BASE/'latest-measurement.json').read_text())['report'])
report=json.loads(source.read_text());assert report['status']=='completed' and report['seedBoundary']==BOUNDARY
row=next(r for r in report['records'] if r['build']=='mod' and r['seed']==5 and r['actor']=='0x188')
assert row['romSha1']==candidate()['romSha1']
code=json.loads((ROOT/'build/expansion/chemist-progressions/code/manifest.json').read_text())
dis=(ROOT/'build/expansion/chemist-progressions/code/disassembly.txt').read_text()
sites={}
for name in ('plain_unit','ffta_action_neutral_query','ffta_evaluated_exposed','heap_container','ffta_job_state','ffta_snapshot_begin','ffta_snapshot_end','ffta_snapshot_copy','ffta_cp_trap_at','ffta_integrated_exposed_native_stage','ffta_on_unit_copy','ffta_geo_field_at','ffta_geo_renderer_update','ffta_integrated_status_next_key'):
    if name not in code['symbols']:continue # LTO may inline an internal helper completely.
    start=code['symbols'][name]['address']&~1
    sites[start]=name+' entry'
    part=dis.split('<'+name+'>:',1)[1].split('\n\n',1)[0]
    for line in part.splitlines():
        if re.search(r'\bbx\s+r[0-7]\s*$',line):sites[int(line.split(':')[0],16)]=name+' return'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
class Observe(InstructionTrace):
    def __init__(self,e):
        super().__init__(e,sites);self.counts=collections.Counter();self.units=[];self.unit=None;self.query={};self.refusals=collections.Counter();self.calls=[];self.timing=collections.Counter()
    def read(self,p,n):
        for start,(host,size) in self.emulator.maps.items():
            if start<=p and p+n<=start+size:return C.string_at(host+p-start,n)
        return bytes(n)
    def word(self,p):return int.from_bytes(self.read(p,4),'little')
    def query_state(self):
        a,t=self.registers[0],self.registers[1];p=self.word(0x0203ff78)
        if not p:return ['no snapshot',hex(a),hex(t)]
        count=self.word(p+12);phase=self.word(p+800)
        result=[phase,count]
        pool=self.word(self.word(0x0200f4b0)+0x448)
        slot=next((i for i in range(8) if self.word(pool+0x19e0+i*260)==p),None)
        for unit in (a,t):
            index=next((i for i in range(min(count,64)) if self.word(p+20+i*12)==unit),None)
            result.append(None if index is None else [self.word(p+24+index*12),0 if slot is None else self.word(pool+0x2660+slot*256+index*4)])
        return result
    def _instruction(self,cpu,opcode):
        try:
            pc=self.registers[15]-4
            if pc in self.sites:
                name=self.sites[pc]
                function=name.rsplit(' ',1)[0]
                if name.endswith('entry'):
                    self.calls.append(dict(name=function,lr=self.registers[14]&~1,sp=self.registers[13],start=self.cycles(),child=0))
                else:
                    target=self.registers[(opcode>>3)&15]&~1
                    if not self.calls or target!=self.calls[-1]['lr'] or self.registers[13]!=self.calls[-1]['sp']:
                        self.handlers[opcode>>6](cpu,opcode);return
                    while self.calls and target==self.calls[-1]['lr'] and self.registers[13]==self.calls[-1]['sp']:
                        item=self.calls.pop();elapsed=(self.cycles()-item['start'])&0xffffffff
                        self.timing[(item['name'],'calls')]+=1
                        self.timing[(item['name'],'inclusive')]+=elapsed
                        self.timing[(item['name'],'selectedExclusive')]+=elapsed-item['child']
                        if self.calls:self.calls[-1]['child']+=elapsed
                if name=='plain_unit entry':self.unit=self.registers[0]
                if name=='ffta_action_neutral_query entry':self.query=self.query_state()
                if name=='ffta_action_neutral_query return' and self.registers[0]==0:self.refusals[json.dumps(self.query)]+=1
                self.counts[(name,str(self.registers[0]) if name.endswith('return') else 'calls')]+=1
                if name=='plain_unit return' and self.registers[0]==0 and len(self.units)<24:
                    p=self.unit
                    for start,(host,n) in self.emulator.maps.items():
                        if start<=p and p+308<=start+n:
                            data=C.string_at(host+p-start,308)
                            self.units.append(dict(unit=hex(p),nativeStatus=data[232:240].hex(),rs=data[58:60].hex(),tail=data[264:].hex()))
                            break
        except BaseException as exc:self.error=repr(exc)
        self.handlers[opcode>>6](cpu,opcode)
folder=Path(row['folder']);rom=Path(report['fixtureDirectory'])/'mod/frozen.gba'
assert hashlib.sha1(rom.read_bytes()).hexdigest()==row['romSha1']
with E(rom) as e,ExitStack() as control:
    e.load(folder/'planning-start.state');pin=control.enter_context(PlannerSeed(e,row['seed']))
    frames=0
    while int.from_bytes(e.memory()[0x156ec:0x156ee],'little')!=1:
        e.run(1);frames+=1;assert frames<row['decisionFrames']
    control.close();assert len(pin.pins)==1
    with Observe(e) as trace:e.run(row['decisionFrames']-frames)
    assert e.memory()==(folder/'choice-published.ram').read_bytes(),'Observed replay differs'
value=dict(romSha1=row['romSha1'],exactReplay=True,source=str(source),counts=[list(k)+[v] for k,v in trace.counts.items()],samples=trace.units,refusals=trace.refusals,timing=[list(k)+[v] for k,v in trace.timing.items()],unreturned=[c['name'] for c in trace.calls])
(source.parent/'neutral-trace.json').write_text(json.dumps(value,indent=2))
print(json.dumps(value))
