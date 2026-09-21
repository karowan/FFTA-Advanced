"""Read-only Thumb halfword-store evidence for the retained target preview.

The observer forwards every original instruction and requires exact full-state
and framebuffer equivalence to a fresh ordinary core on every declared frame (32 idle or580 damage-sequence frames).
"""
import argparse, ctypes as C, datetime, hashlib, json, runpy
from pathlib import Path
from native_art import ROOT, sha
from mgba_instruction_trace import InstructionTrace, INSTRUCTION

class Writes(InstructionTrace):
    def __init__(self, emulator):
        super().__init__(emulator, sites, {pc:{"bank":(watch,32)} for pc in sites})
        for index in list(range(0x8000 >> 6, 0x8800 >> 6)) + list(range(0x5200 >> 6, 0x5400 >> 6)):
            self.handlers[index] = INSTRUCTION(self.original_entries[index])
            self.table[index] = C.cast(self.callback, C.c_void_p).value

    def _instruction(self, cpu, opcode):
        try:
            assert cpu == self.cpu and self.registers[16] & 32
            regs = self.registers
            offset = ((opcode >> 6) & 31) * 2 if opcode & 0xf800 == 0x8000 else regs[(opcode >> 6) & 7]
            address = (regs[(opcode >> 3) & 7] + offset) & 0xffffffff
            if (opcode & 0xf800 == 0x8000 or opcode & 0xfe00 == 0x5200) and watch <= address < watch+32:
                self.events.append(dict(pc=regs[15]-4, lr=regs[14], address=address,
                    value=regs[opcode & 7] & 65535, old=self.iw[address-0x03000000] | self.iw[address-0x03000000+1] << 8,
                    videoFrame=self.frame_counter(self.core), registers=list(regs[:17])))
        except BaseException as error:
            self.error = repr(error)
        super()._instruction(cpu, opcode)

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--damage',action='store_true');args=parser.parse_args()
digest='3f049cace93d90524c2db155d61d092c6dda5d22' if args.damage else '4a7d55ce09cd4a40965a0bb97de2701d276789c5'
meta=json.loads((ROOT/'build/art/connected'/digest/'manifest.json').read_text())
assert hashlib.sha1(Path(meta['path']).read_bytes()).hexdigest()==meta['romSha1']==digest
seed=ROOT/'build/art/connected/casting'/('20260918T205730.189020Z' if args.damage else '20260918T203709.455123Z')/'371-active-confirmation.state'
sites={meta['components']['livePalette']['symbols']['ffta_art_live_palette_copy']&~1:'palette-copy'} if args.damage else {}
if args.damage:
    sites.update({address&~1:name for name,address in meta['components']['livePalette']['symbols'].items()
        if name.startswith('ffta_art_live_fade_') and not any(x in name for x in ('tick','rotate','cycle'))})
watch=0x03003be0 if args.damage else 0x03003b80
schedule=[0]*32+[256]*8+[0]*540 if args.damage else [0]*32
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=ROOT/'build/art/connected/highlight-writes'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];baseline=[];e=None;trace=None
try:
    e=E(Path(meta['path']));e.load(seed);trace=Writes(e);initial=trace.state()
    for frame,key in enumerate(schedule):
        if args.damage and frame==32:C.memmove(e.maps[0x03000000][0]+0x34b0,b'\x01\x00\x00\x00',4)
        e.run(1,key);baseline.append((sha(trace.state()),sha(e.frame[0])))
    e.close();e=None
    e=E(Path(meta['path']));e.load(seed);trace=Writes(e)
    assert trace.state()==initial;checks.append('Fresh core exact initial state')
    with trace:
        for frame,key in enumerate(schedule):
            if args.damage and frame==32:C.memmove(e.maps[0x03000000][0]+0x34b0,b'\x01\x00\x00\x00',4)
            e.run(1,key)
            assert (sha(trace.state()),sha(e.frame[0]))==baseline[frame],frame
            checks.append('Entire native state and framebuffer exact '+str(frame))
    assert trace.slot.value==trace.original;checks.append('Original host table restored')
    result=dict(status='passed',romSha1=meta['romSha1'],checks=checks,events=trace.events,
        source=dict(path=str(seed),sha256=sha(seed.read_bytes())), inputs=dict(schedule=schedule,nativeRngAtFrame32=1 if args.damage else None), watchAddress=watch,
        scope='Read-only immediate/register Thumb STRH observation of declared bank and schedule, plus damage-copy callers when selected. Does not cover word stores, DMA, ARM stores or fix/accept graphics.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),events=len(trace.events),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,events=trace.events if trace else []),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
