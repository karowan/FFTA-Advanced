"""Native renderer/compositor ownership bridge, including clipping and reuse.

Runs compiled ARM helpers and actual native 216F8/12BC in an isolated machine.
DMA0 is modeled synchronously at the four native completion points. This is
not live mGBA VBlank, a timing measurement, or a installed palette hook.
"""
import argparse, ast, datetime, hashlib, json, struct, subprocess, sys
from pathlib import Path
from native_art import ROOT, sha
from art_palette_build import write_pixel_banks
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
arm_source=(ROOT / 'scripts/test-equipment-legality.py').read_text().replace(
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree = ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
out = ROOT / 'build/art/palette-owners' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
prefix = str(ROOT / 'tools/arm-gnu/bin/arm-none-eabi-')
elf, binary, entry = out / 'owners.elf', out / 'owners.bin', 0x09f90000
sources = ['src/engine/art-palette-owners.c', 'src/engine/art-palette-plan.c', 'src/engine/art-palette-scan.s']
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--scoped-frame',action='store_true');parser.add_argument('--native-prefix',action='store_true');parser.add_argument('--native-owner-producer',action='store_true');parser.add_argument('--fused-compose',action='store_true');parser.add_argument('--fused-word-reads',action='store_true');parser.add_argument('--compact-leaves',action='store_true');parser.add_argument('--unrolled-copy',action='store_true');args=parser.parse_args()
if args.fused_word_reads or args.compact_leaves or args.unrolled_copy:args.fused_compose=True
if args.fused_compose:args.native_owner_producer=True
if args.native_owner_producer:args.native_prefix=True
if args.native_prefix:args.scoped_frame=True
extra=[]
scoped_proof=None
if args.scoped_frame:
    from art_scoped_build import build_scoped
    assembly,scoped_proof=build_scoped(out,10,args.native_owner_producer,args.fused_compose,args.fused_word_reads,args.compact_leaves,args.unrolled_copy)
    sources.append(str(assembly));extra=['-DFFTA_ART_SCOPED_FRAME=1']
if args.native_prefix:extra+=['-DFFTA_ART_NATIVE_OAM_PREFIX=1']
if args.native_owner_producer:extra+=['-DFFTA_ART_NATIVE_OWNER_PRODUCER=1']
if args.fused_compose:
    extra+=['-DFFTA_ART_FUSED_COMPOSE=1','-DFFTA_ART_ARM_OAM_SCAN=1','-DFFTA_ART_FAST_BANK_SCAN=1','-DFFTA_ART_FAST_OAM_PLAN=1']
    sources+=['src/engine/art-oam-demands.s','src/engine/art-palette-bank-scan.s']
if args.fused_word_reads:extra+=['-DFFTA_ART_FUSED_WORD_READS=1']
lookup, lookup_bytes = write_pixel_banks(out)
compiled = subprocess.run([prefix + 'gcc.exe', '-mcpu=arm7tdmi', '-mthumb', '-O2', '-ffreestanding', '-fno-builtin', '-nostdlib', '-Wall', '-Wextra', '-Werror', '-Wl,-Ttext=' + hex(entry), '-Wl,-e,ffta_art_owners_compose', *extra, *sources, str(lookup), '-o', str(elf)], cwd=ROOT, capture_output=True, text=True)
(out / 'compile.log').write_text(compiled.stdout + compiled.stderr)
compiled.check_returncode()
subprocess.run([prefix + 'objcopy.exe', '-O', 'binary', str(elf), str(binary)], check=True, capture_output=True)
symbols = {v[2]: int(v[0], 16) for line in subprocess.check_output([prefix + 'nm.exe', str(elf)], text=True).splitlines() if len(v := line.split()) == 3}
meta = json.loads((ROOT / 'build/art/generated-actions/refined-samurai-current.json').read_text())
original = Path(meta['path']).read_bytes()
assert hashlib.sha1(original).hexdigest() == '0fa7d1707e2d85fb2a8602f061b5eb4479ff3211'
rom = bytearray(original); code = binary.read_bytes()
assert len(code) < 0x40000 and rom[entry - 0x08000000:entry - 0x08000000 + len(code)] == b'\xff' * len(code)
rom[entry - 0x08000000:entry - 0x08000000 + len(code)] = code
a = ARM(rom, bytes(0x8000))
for address, size in ((0x04000000, 0x1000), (0x07000000, 0x1000)):
    a.u.mem_map(address, size)
S, TAGS, F, P, C, R, V = 0x02010000, 0x02011000, 0x02011200, 0x02011400, 0x02011800, 0x02011900, 0x02020000
STATE_SIZE = 2056
DEMANDS,EXTENT=0x02018000,0x02018100
checks, records, transfers = [], [], []

def check(ok, label):
    assert ok, label
    checks.append(label)

def call(name, *args):
    return a.call(symbols[name], *args)

def dma(u, address, size, user):
    source, dest, control = struct.unpack('<3I', a.read(0x040000b0, 12))
    assert control & 0xffff0000 == 0x84000000
    count = (control & 0xffff) * 4
    assert 0x03000000 <= source <= 0x03008000 - count
    assert 0x07000000 <= dest <= 0x07000400 - count
    a.put(dest, a.read(source, count))
    a.put(0x040000b8, struct.pack('<I', control & 0x7fffffff))
    transfers.append(dict(source=source, destination=dest, bytes=count))

for pc in (0x08001322, 0x08001396, 0x080013e2, 0x08001430):
    a.u.hook_add(UC_HOOK_CODE, dma, begin=pc, end=pc)

def record(bank, before, after, resource):
    # Six-argument C ABI: resource/count tail are on the caller's stack.
    a.put(STACK, struct.pack('<2I', after, resource))
    return call('ffta_art_owners_record', S, bank, 0x03000030 + bank * 1024, before)

def demand_setup(stack,enabled,banks):
    a.put(stack,struct.pack('<4I',enabled,banks,DEMANDS,EXTENT))
    a.put(DEMANDS-4,b'pre!'+b'\xcc'*140+b'end!');a.put(EXTENT-4,b'pre!'+b'\xa5'*4+b'end!')

def demand_audit(hw,tags,bound):
    occupied=requested=0;eight=[];valid=True
    for i in range(bound):
        x,y,z,_=struct.unpack_from('<4H',hw,i*8);owner=tags[i]
        if owner<10:requested|=1<<owner
        if x&0x300==0x200:continue
        if x>>14==3:valid=False;continue
        if owner!=255:
            if x&0xe100 or y>>14!=2:valid=False
        elif x&0x2000:eight.append(i)
        else:occupied|=1<<(z>>12)
    check(a.read(DEMANDS,12)==struct.pack('<3I',occupied,requested,len(eight) if valid else 129),'Fused current class/native bank/eight-bit count oracle')
    check(a.read(DEMANDS+12,len(eight))==bytes(eight),'Fused complete ordered eight-bit index list')
    check(a.word(EXTENT)==bound,'Fused actual native extent')
    check(a.read(DEMANDS-4,4)==a.read(EXTENT-4,4)==b'pre!' and a.read(DEMANDS+140,4)==a.read(EXTENT+4,4)==b'end!','Fused demand/extent bounds')

def compose():
    a.call(0x080012bc)
    if args.native_prefix:
        bound=call('ffta_art_owners_native_count',0x03000000)
        check(0<=bound<=128,'Native prefix count bounded')
        check(all(a.read(0x07000000+i*8,6)==bytes.fromhex('a800f8000000') for i in range(bound,128)),'Actual native compositor leaves exact unowned bank0 sentinel tail')
    a.put(TAGS, b'\xa5' * 128)
    result = call('ffta_art_owners_compose', S, 0x03000000, 0x07000000, TAGS)
    tags,hw=a.read(TAGS,128),a.read(0x07000000,1024)
    for residue in range(4):
        output=TAGS+residue
        a.put(output-4,b'\xd7'*4);a.put(output,b'\xa5'*128);a.put(output+128,b'\xe9'*4)
        observed=call('ffta_art_owners_compose',S,0x03000000,0x07000000,output)
        check(observed==result and a.read(output,128)==tags,'Exact aligned/unaligned complete owner output '+str(residue))
        check(a.read(output-4,4)==b'\xd7'*4 and a.read(output+128,4)==b'\xe9'*4,'Owner output stays within128 bytes '+str(residue))
        check(a.read(0x07000000,1024)==hw,'Owner output preserves all hardware OAM '+str(residue))
    banks=0x02011a00
    for stack in ((0x03007800,0x03007804,STACK,0x0201c000) if args.scoped_frame else (STACK,)):
      for enabled in (0,1,0x155,1023):
       for residue in (range(4) if args.scoped_frame else (0,)):
        output=TAGS+residue
        a.put(output-4,b'pre!');a.put(output,b'\xa5'*128);a.put(output+128,b'end!')
        a.put(banks-4,b'pre!');a.put(banks,b'\xc7'*20);a.put(banks+20,b'end!')
        a.put(stack,struct.pack('<2I',enabled,banks))
        if args.fused_compose:demand_setup(stack,enabled,banks)
        resident=a.read(0x03000000,0x6d68);executed=[]
        hook=a.u.hook_add(UC_HOOK_CODE,lambda u,pc,size,user:executed.append(pc),begin=0x03006d68,end=0x03007fff)
        requested=a.call(symbols['ffta_art_owners_compose_fused' if args.fused_compose else 'ffta_art_owners_compose_native' if args.native_owner_producer else 'ffta_art_owners_compose_filtered'],S,0x03000000,0x07000000,output,stack=stack)
        a.u.hook_del(hook)
        expected=bytes(owner if owner<10 and enabled&(1<<owner) else 255 for owner in tags)
        wanted=sum(1<<owner for owner in set(expected) if owner<10)
        masks=[0]*10
        for i,owner in enumerate(expected):
            if owner<10:masks[owner]|=1<<(struct.unpack_from('<H',hw,i*8+4)[0]>>12)
        check(requested==wanted and a.read(output,128)==expected,'Filtered tags match native owner bridge '+str((enabled,stack,residue)))
        check(a.read(banks,20)==struct.pack('<10H',*masks),'Filtered native bank masks exact')
        if args.fused_compose:demand_audit(hw,expected,call('ffta_art_owners_native_count',0x03000000))
        check(a.read(output-4,4)==b'pre!' and a.read(output+128,4)==b'end!' and a.read(banks-4,4)==b'pre!' and a.read(banks+20,4)==b'end!','Filtered output bounds')
        check(a.read(0x03000000,0x6d68)==resident,'Resident native IWRAM unchanged')
        if args.scoped_frame:check(bool(executed)==(stack in (0x03007800,0x03007804)),'Scoped execution or ROM fallback as bounded')
    a.put(TAGS,tags)
    return result,tags,hw

def counters(bank, other, front, ui, main, tail):
    a.put(0x03000028, bytes([bank ^ 1]))
    a.put(0x03002f58, bytes([other ^ 1]))
    for base, selected, count in ((0x2c50, bank, front), (0x2f60, other, ui), (0x20, bank, main), (0x3168, other, tail)):
        a.put(0x03000000 + base + selected * 4, struct.pack('<I', count))

try:
    # Exact existing native actor, not a new game/save fixture.
    capture = ROOT / 'build/art/explicit-walk/20260918T013433.309654Z'
    proofbytes = (capture / 'report.json').read_bytes()
    assert sha(proofbytes) == '0a3d7cab394bf947c9a0d51df940b65aa81e1febd19e15e61b542537cbaa6f76'
    proof = json.loads(proofbytes)
    ram = (capture / 'mapped-ready.ram').read_bytes()
    assert sha(ram) == '0ca0ae3656f8c1ad4af9d5fceb36d3786d04c609c095c7dc0259629819183159'
    actor = proof['observations']['mapped']['ready']['actor']
    iwpath = Path(meta['releaseSource']).parent / 'fixture/battle-ready.iwram'
    iw = iwpath.read_bytes()
    for bank in (0, 1):
        a.put(0x02000000, ram); a.put(0x03000000, iw)
        a.put(S, bytes(STATE_SIZE)); call('ffta_art_owners_reset', S, bank)
        a.put(0x03000020, bytes(12)); a.put(0x03000028, bytes([bank]))
        context = 0x02008000
        a.put(context, struct.pack('<hh7B', 64, 64, 0, 0, 0, 0, 0, 0, 0))
        a.call(0x080216f8, 0x02000000 + actor['address'], context)
        count = a.word(0x03000020 + bank * 4)
        check(count == 1 and record(bank, 0, count, actor['resource']) == 1, f'Bank {bank}: real Samurai renderer recorded')
        counters(bank, bank ^ 1, 2, 3, count, 1)
        result, tags, hw = compose()
        check(result == 1 and tags == bytes([255] * 5 + [0] + [255] * 122), f'Bank {bank}: real body tracks native prefix translation')
        check(hw[5 * 8:5 * 8 + 6] == a.read(0x03000030 + bank * 1024, 6), f'Bank {bank}: real body exact hardware attributes')

    # Native 12BC supplies the ordering/clipping oracle for isolated inputs.
    cases = [(0, 0, 0, 0, 1, 0), (1, 0, 3, 7, 20, 6),
             (0, 1, 48, 32, 100, 16), (1, 1, 48, 32, 70, 16),
             (0, 0, 0, 32, 128, 16), (1, 0, 2, 32, 0, 16)]
    for case in cases:
        bank, other, front, ui, main, tail = case
        a.put(0x03000000, bytes(0x8000)); a.put(S, bytes(STATE_SIZE))
        call('ffta_art_owners_reset', S, bank)
        counters(*case)
        # Give every group a disjoint native OAM identity.
        for base, selected, stride, count, tilebase in ((0x2c58, bank, 384, front, 400), (0x2f68, other, 256, ui, 500), (0x30, bank, 1024, main, 600), (0x3170, other, 128, tail, 900)):
            for i in range(count):
                a.put(0x03000000 + base + selected * stride + i * 8, struct.pack('<4H', 64, 0x8040, tilebase + i, 0))
        for i in range(main):
            check(record(bank, i, i + 1, 256 + (i % 20)) == 1, f'{case}: record land/water resource {i}')
        native_iw = a.read(0x03000000, 0x7000)
        result, tags, hw = compose()
        expected = bytearray([255] * 128)
        for i in range(128):
            tile = struct.unpack_from('<H', hw, i * 8 + 4)[0] & 1023
            if 600 <= tile < 600 + main: expected[i] = ((tile - 600) % 20) // 2
        check(result == 1 and tags == expected, f'{case}: owners follow actual native clipped output')
        after_iw = a.read(0x03000000, 0x7000)
        changed = [i for i, (old, new) in enumerate(zip(native_iw, after_iw)) if old != new]
        # These are real function calls using STACK=03007000. Their stack
        # scratch is not native OAM state and cannot be expected byte-exact.
        check(all(0x6e00 <= i < 0x7000 for i in changed), f'{case}: native buffers unchanged outside bounded test call stack')
        records.append(dict(case=case, tags=list(tags), hardwareSha256=sha(hw), changedIWRAMOffsets=changed))
        # Reusing this native bank after reset cannot inherit old actor tags.
        call('ffta_art_owners_reset', S, bank)
        result, tags, _ = compose()
        check(result == 1 and tags == b'\xff' * 128, f'{case}: reset removes previous frame ownership')

    # Use the produced tags as real inputs to the existing allocator.
    bank = other = 0
    a.put(0x03000000, bytes(0x8000)); a.put(S, bytes(STATE_SIZE))
    call('ffta_art_owners_reset', S, bank); counters(0, 0, 0, 0, 2, 0)
    a.put(0x03000030, struct.pack('<8H', 64, 0x8040, 600, 0, 64, 0x8041, 616, 0))
    record(0, 0, 1, 256); record(0, 1, 2, 258)
    result, tags, hw = compose()
    colors = bytes(range(64))
    a.put(P, bytes(512)); a.put(C, colors); a.put(V, bytes(32768))
    a.put(F, struct.pack('<8I', 0x07000000, V, TAGS, P, C, R, 1, 2))
    check(result == 1 and call('ffta_art_palette_apply', F) == 1, 'Native composition ownership feeds compiled palette allocation')
    slots = list(a.read(R + 4, 2)); expected = bytearray(hw); pal = bytearray(512)
    for i, slot in enumerate(slots):
        old = struct.unpack_from('<H', expected, i * 8 + 4)[0]
        struct.pack_into('<H', expected, i * 8 + 4, (old & 0xfff) | (slot << 12))
        pal[slot * 32:slot * 32 + 32] = colors[i * 32:i * 32 + 32]
    check(slots == [1, 2] and a.read(0x07000000, 1024) == expected and a.read(P, 512) == pal, 'Two custom actors receive distinct exact colors; all other OAM/colors preserved')

    # Mutation/lifetime refusal tests are evaluated before any palette write.
    _, _, hw = compose()
    a.put(0x07000004, struct.pack('<H', 999)); a.put(TAGS, b'\xa5' * 128)
    check(call('ffta_art_owners_compose', S, 0x03000000, 0x07000000, TAGS) == 0 and a.read(TAGS, 128) == b'\xa5' * 128, 'Hardware/source drift fails without publishing tags')
    a.put(0x03000034, struct.pack('<H', 999))
    result, tags, _ = compose()
    check(result == 1 and tags[0] == 255 and tags[1] == 1, 'Overwritten source entry loses stale ownership')
    record(0, 1, 2, 276)
    result, tags, _ = compose()
    check(result == 1 and tags == b'\xff' * 128, 'Ordinary or held-weapon redraw clears prior body tag')
    for label, address, value in [('bad bank', 0x03000028, b'\x02'), ('bad main count', 0x03000020, struct.pack('<I', 129))]:
        old = a.read(address, len(value)); a.put(address, value); a.put(TAGS, b'\xa5' * 128)
        check(call('ffta_art_owners_compose', S, 0x03000000, 0x07000000, TAGS) == 0 and a.read(TAGS, 128) == b'\xa5' * 128, label + ' fails without writes')
        a.put(address, old)
    before = a.read(S, STATE_SIZE)
    check(record(0, 2, 1, 256) == 0 and record(0, 127, 129, 256) == 0 and a.read(S, STATE_SIZE) == before, 'Invalid emission spans leave state unchanged')
    a.put(S, bytes(STATE_SIZE)); a.put(TAGS, b'\xa5' * 128)
    check(call('ffta_art_owners_compose', S, 0x03000000, 0x07000000, TAGS) == 0 and a.read(TAGS, 128) == b'\xa5' * 128, 'Uninitialized frame bank fails without writes')
    if args.scoped_frame:
        a.put(S,bytes(STATE_SIZE));call('ffta_art_owners_reset',S,0)
        counters(0,0,0,0,128,0)
        objects=struct.pack('<4H',64,0x8040,0xf2c0,0)*128
        a.put(0x03000030,objects);a.put(0x07000000,objects);record(0,0,128,274)
        for stack in (0x03007800,0x03007804,STACK,0x0201c000):
          for address in (0x03000028,0x03000020,0x03002c50,0x03002f60,0x03003168,0x07000000,0x070003fc):
            old=a.read(address,4);a.put(address,b'\xff'*4)
            a.put(TAGS,b'\xa5'*128);a.put(R,b'\xc7'*20);a.put(stack,struct.pack('<2I',1023,R))
            result=a.call(symbols['ffta_art_owners_compose_filtered'],S,0x03000000,0x07000000,TAGS,stack=stack)
            check(result==0 and a.read(TAGS,128)==b'\xa5'*128 and a.read(R,20)==b'\xc7'*20,'Atomic invalid-frame refusal '+str((stack,address)))
            if args.native_owner_producer and address<0x07000000:
                result=a.call(symbols['ffta_art_owners_compose_native'],S,0x03000000,0x07000000,TAGS,stack=stack)
                check(result==0 and a.read(TAGS,128)==b'\xa5'*128 and a.read(R,20)==b'\xc7'*20,'Native-only malformed counter atomic refusal')
            a.put(address,old)
    if args.native_prefix:
        import itertools
        for bank,other,front,ui,main,tail in itertools.product((0,1),(0,1),(0,1,48),(0,1,32),(0,1,79,80,81,127,128),(0,1,16)):
            a.put(0x03000000,bytes(0x8000));counters(bank,other,front,ui,main,tail)
            # Affine flags update attr3 throughout hardware OAM, including the
            # omitted tail. They must not change its palette/enable fields.
            a.put(0x03003270+bank*32,b'\x01'*32)
            a.put(0x030032b0+bank*256,struct.pack('<128H',*(0x5a00+i for i in range(128))))
            if args.native_owner_producer:
                a.put(S,bytes(STATE_SIZE));call('ffta_art_owners_reset',S,bank)
                for index in sorted({0,31,63,95,127,main-1}):
                    if not 0<=index<main:continue
                    a.put(0x03000030+bank*1024+index*8,struct.pack('<4H',64,0x8040,((index%16)<<12)|600,0))
                    record(bank,index,index+1,256+index%20)
            start=len(transfers);a.call(0x080012bc)
            bound=call('ffta_art_owners_native_count',0x03000000)
            copies=transfers[start:]
            end=max((v['destination']+v['bytes'] for v in copies),default=0x07000000)
            check(a.read(0x070003fe,2)==struct.pack('<H',0x5a7f),'Native affine update actually changes last hardware slot attr3')
            check(bound==(end-0x07000000)//8,'Count exactly matches native DMA destination extent '+str((bank,other,front,ui,main,tail)))
            if args.native_owner_producer:
                a.put(STACK,struct.pack('<2I',1023,R));a.put(TAGS,b'\xa5'*128);a.put(R,b'\xc7'*20)
                ref=call('ffta_art_owners_compose_filtered',S,0x03000000,0x07000000,TAGS)
                expected=ref,a.read(TAGS,128),a.read(R,20)
                stack=0x03007800+bank*4;a.put(stack,struct.pack('<2I',1023,R))
                a.put(TAGS,b'\xa5'*128);a.put(R,b'\xc7'*20)
                if args.fused_compose:demand_setup(stack,1023,R)
                actual=a.call(symbols['ffta_art_owners_compose_fused' if args.fused_compose else 'ffta_art_owners_compose_native'],S,0x03000000,0x07000000,TAGS,stack=stack)
                if args.fused_compose:demand_audit(a.read(0x07000000,1024),a.read(TAGS,128),bound)
                check((actual,a.read(TAGS,128),a.read(R,20))==expected,'Native-only owner output equals generic hardware-authenticated bridge across count matrix')
            check(all(a.read(0x07000000+i*8,6)==bytes.fromhex('a800f8000000') for i in range(bound,128)),'Counter matrix exact native sentinel tail')
    if args.fused_word_reads:
        for stack in (0x03007800,0x03007804,STACK,0x0201c000):
            for field in range(3):
                for residue in (1,2,3):
                    pointers=[S,0x03000000,0x07000000];pointers[field]+=residue
                    demand_setup(stack,1023,R);a.put(TAGS,b'\xa5'*128);a.put(R,b'\xc7'*20)
                    result=a.call(symbols['ffta_art_owners_compose_fused'],*pointers,TAGS,stack=stack)
                    check(result==0 and a.read(TAGS,128)==b'\xa5'*128 and a.read(R,20)==b'\xc7'*20,'Unaligned native-only inputs refuse before owner writes')
                    check(a.read(DEMANDS,140)==b'\xcc'*140 and a.read(EXTENT,4)==b'\xa5'*4,'Unaligned input cannot publish prepared demands')
    report = dict(status='passed', checks=checks, records=records, transfers=transfers,
                  fusedCompose=args.fused_compose,nativeOwnerProducer=args.native_owner_producer, scopedFrame=scoped_proof, sourceRomSha1=hashlib.sha1(original).hexdigest(), compiledBytes=len(code), compiledSha256=sha(code),
                  sources={name: sha((ROOT / name).read_bytes()) for name in sources + ['src/engine/art-palette-owners.h', 'src/engine/art-palette-plan.h']},
                  retainedActorReport=str(capture / 'report.json'), retainedActorReportSha256=sha(proofbytes), iwramSha256=sha(iw),
                  scope='Compiled ownership recording and actual native renderer/compositor with synchronous DMA model, both buffers, priority/UI/main/tail order and clipping, palette allocator connection, overwrite/reset/refusal. No installed hook, RAM reservation, live VBlank/fades/timing or final artwork acceptance.')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='passed', checks=len(checks), report=str(out / 'report.json'))))
except Exception as error:
    (out / 'failed.json').write_text(json.dumps(dict(status='failed', error=str(error), checks=checks, records=records, transfers=transfers), indent=2) + '\n')
    print(str(out)); raise
