"""Reproduce Moogle Chemist's missing native knife animation on detached RAM.

Authenticate the real failed Fight capture. Replay the native wrapper mode
constructor, and use a same-race native knife descriptor as a diagnostic control.
The control changes private ROM memory only; it is not generated-art integration
or permission to accept original artwork as the replacement character.
"""
import ast, datetime, hashlib, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *

RETURN, STACK = 0x08000100, 0x03007000
source_text = (ROOT/'scripts/test-equipment-legality.py').read_text().replace(
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(source_text).body
    if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<ARM>', 'exec'))
source = ROOT/'build/art/class-fight/20260919T022121.606456Z'
pins = {
    'failed.json': 'e47b9214fc4fa05f479b0b96ea4c53db2829d000b2270cd63e805029bbb3d7f7',
    'failed.ram': 'b9a68e508c50acb9074e75241abd89846be7dea2c6a40c8c3ccb8e8af84182c4',
    'failed.iwram': '7097aa69cca72d9d495e3506ae71a563b7b684431809d0ba5e2bc654b253cf4b',
    'failed.vram': '05ff4da3a1fbd71119a3e7c74fb791a05f86c26639e8a89288c55bec5d7d994d',
}
out = ROOT/'build/art/native-missing-action'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
checks, records = [], []
def check(ok, label):
    assert ok, label
    checks.append(label)
word = lambda data, p: struct.unpack_from('<I', data, p)[0]
half = lambda data, p: struct.unpack_from('<H', data, p)[0]
try:
    samples = {name: (source/name).read_bytes() for name in pins}
    for name, digest in pins.items():
        check(sha(samples[name]) == digest, 'Authenticated retained ' + name)
    prior = json.loads(samples['failed.json'])
    meta = json.loads((ROOT/'build/art/connected/e1a87ecde67f265f666d3ab9d7e50ba401370633/live-palette-view.json').read_text())
    rom = Path(meta['path']).read_bytes()
    clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    check(hashlib.sha1(rom).hexdigest() == prior['romSha1'] == meta['romSha1'], 'Exact failing candidate')
    gameplay = Path(meta['fixtureSource']).read_bytes()
    check(hashlib.sha1(gameplay).hexdigest() == meta['fixtureRomSha1'], 'Authenticated gameplay fixture ROM')
    check(rom[0x975dc:0x97704] == gameplay[0x975dc:0x97704], 'Wrapper constructor preserves existing gameplay hooks')
    check(all(rom[p] == clean[p] or 0x975f2 <= p < 0x975fc or 0x9764c <= p < 0x9764e
              for p in range(0x975dc,0x97704)), 'Wrapper changes confined to existing allocation/status hooks')
    for start, end in ((0x21618, 0x216f8),):
        check(rom[start:end] == clean[start:end], 'Native constructor unchanged ' + hex(start))
    ram = samples['failed.ram']; wrapper, body, unit = 0x229d8, 0x20e28, 0x5a8
    check(word(ram, wrapper) == 0x02000000 + unit and ram[unit+5:unit+8] == bytes((122,5,122)), 'Real generic Moogle Chemist wrapper')
    check(word(ram, wrapper+0x44) == 0xffffffff, 'Failure is missing body result')
    check(half(ram, wrapper+0x34) == 268 and half(ram, wrapper+0x36) == 84 and ram[wrapper+0x1f] == 3, 'Actual request is resource268 mode87')
    job_table = word(rom, 0xc8598)-0x08000000
    permissions = word(rom, 0xcac40)-0x08000000
    mask = word(rom, permissions+rom[job_table+122*52+0x2d]*4)
    item_table = word(rom, 0x79aec)-0x08000000
    check(half(ram, unit+0x2a) == 74 and rom[item_table+74*32+8] == 7 and mask & (1<<6), 'Actual knife74 is permitted')
    table = word(rom, 0x2102c)-0x08000000
    descriptor = word(rom, table+268*4)-0x08000000+42*12
    check(rom[descriptor:descriptor+24] == bytes(24), 'Both knife-facing descriptors absent')
    donor_record = job_table+39*52
    donor_resource = half(rom, donor_record+7)
    check(rom[donor_record+4] == 5 and donor_resource == 37 and word(rom, permissions+rom[donor_record+0x2d]*4)&(1<<6), 'Control is original same-race knife job39/resource37')
    donor = word(rom, table+donor_resource*4)-0x08000000+42*12
    check(word(rom, donor) != 0 and word(rom, donor+12) != 0, 'Control has both actual knife-facing streams')
    image = bytearray(rom)
    image[descriptor:descriptor+24] = rom[donor:donor+24]
    for name, payload in [('missing', rom), ('descriptor-control', bytes(image))]:
        for facing in range(4):
            machine = ARM(payload, samples['failed.iwram']); machine.put(0x02000000, ram)
            # Restore only the constructor's input pointer to the last real body.
            # Do not alter its mode, frame source, allocation, tiles or unit data.
            machine.put(0x02000000+wrapper+0x44, struct.pack('<I', 0x02000000+body))
            writes = []
            def record_write(u, access, address, size, value, data):
                if address == 0x02000000+wrapper+0x44:
                    writes.append(dict(pc=u.reg_read(UC_ARM_REG_PC), value=value & 0xffffffff, size=size))
            hook = machine.u.hook_add(UC_HOOK_MEM_WRITE, record_write)
            machine.call(0x080975dc, 0x02000000+wrapper, 84, facing, 0)
            machine.u.hook_del(hook)
            result = machine.word(0x02000000+wrapper+0x44)
            check(writes == [dict(pc=0x0809768a, value=result, size=4)], name+str(facing)+' actual native wrapper pointer publication')
            if name == 'missing':
                check(result == 0xffffffff, 'Missing stream reproduces invalid body '+str(facing))
                check(machine.read(0x02000000+body,72) == ram[body:body+72], 'Missing constructor preserves retired-looking old body '+str(facing))
            else:
                expected = word(rom, donor+(12 if facing in (1,2) else 0))+4
                check(result == 0x02000000+body, 'Present stream preserves valid body '+str(facing))
                check(machine.read(result+6,4) == struct.pack('<HH',268,84+facing) and machine.word(result+0x34) == expected,
                      'Native body uses exact selected knife stream '+str(facing))
            check(machine.read(0x02000000+unit,264) == ram[unit:unit+264], name+str(facing)+' complete actual unit and equipment unchanged')
            records.append(dict(case=name,facing=facing,result=result,writes=writes))
    report = dict(status='passed',romSha1=meta['romSha1'],checks=checks,records=records,source=str(source),inputHashes=pins,
        missingDescriptors=[descriptor,descriptor+12],diagnosticDonor=dict(job=39,resource=donor_resource,descriptor=donor),scope=__doc__,
        engineeringAccepted=False,conclusion='Real missing native sequence; observer bounds remain correct. Same-race stream removes constructor failure only; generated payload, full playback, weapons/effects and all required actions still need integration.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,records=records),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out)); raise
