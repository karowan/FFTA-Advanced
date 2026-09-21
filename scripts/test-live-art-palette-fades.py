"""Controlled native fade commands with actual mGBA callback/display playback.

Execute the original native setter on a paused-state clone and copy back only
its declared palette/effect and private-binding state. Inputs, not results, are
installed. The running game then advances its real callbacks and hardware DMA.
"""
import argparse, ast, ctypes as C, datetime, hashlib, json, runpy, struct, sys
from pathlib import Path
from native_art import ROOT, sha
from actor_render_evidence import actors
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--color-operations',action='store_true')
parser.add_argument('--reload',action='store_true')
parser.add_argument('--late-entry',action='store_true')
parser.add_argument('--late-rotation',action='store_true')
parser.add_argument('--dark-knight-mask-control',action='store_true')
parser.add_argument('--extended-color-operations',action='store_true')
parser.add_argument('--table-color-operations',action='store_true')
parser.add_argument('--task-controls',action='store_true')
parser.add_argument('--rotation',action='store_true')
parser.add_argument('--candidate-manifest',type=Path,default=ROOT/'build/art/live-palette/poc.json')
args=parser.parse_args()
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
arm_source=(ROOT / 'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=500000')
arm_source=arm_source.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree = ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
meta = json.loads(args.candidate_manifest.read_text())
SLOTS=meta.get('historySlots',10)
COUNTERS=meta.get('bindingCounterOffset',2840)
BASE, LIMIT = meta['ramReservation']
BO = BASE - 0x02000000 + meta['bindingOffset']
ENTRY = BO + meta['bindingEntryBytes']  # Dark Knight owner 1.
seedpath = ROOT / 'build/showcase/20260917T160011.215713Z/showcase.sav'
seed = seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest() == '7831543efb239ef145764889214f8d83cd56eb14'
colors = (ROOT / 'build/art/imagegen/human-dark-knight/march-v2-own-palette/palette.bin').read_bytes()
assert sha(colors) == meta['paletteSha256']
oldmeta = json.loads((ROOT / 'build/art/live-palette/19c8d9e05546607ad12d76be27fab1be6a4f9dbf/manifest.json').read_text())
oracle_rom = Path(oldmeta['path']).read_bytes()
assert hashlib.sha1(oracle_rom).hexdigest() == oldmeta['romSha1']
E = runpy.run_path(str(ROOT / 'scripts/emulator-test.py'))['Emulator']
out = ROOT / 'build/art/live-palette/fades' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
mask_control=None
if args.dark_knight_mask_control:
    assert args.late_rotation and meta['allClasses']
    raw=Path(meta['path']).read_bytes();assert hashlib.sha1(raw).hexdigest()==meta['romSha1']
    offset=meta['symbols']['ffta_art_custom_mask']-0x08000000
    assert struct.unpack_from('<I',raw,offset)[0]==1023
    changed=bytearray(raw);struct.pack_into('<I',changed,offset,2)
    assert changed[:offset]==raw[:offset] and changed[offset+4:]==raw[offset+4:]
    control_path=out/'dark-knight-mask-control.gba';control_path.write_bytes(changed)
    mask_control=dict(sourceRomSha1=meta['romSha1'],offset=offset,before=1023,after=2,
        scope='Diagnostic only: identical code, assets and layout; only Dark Knight custom-palette enable bit. No all-class acceptance.')
    meta=dict(meta,path=str(control_path),romSha1=hashlib.sha1(changed).hexdigest())
    (out/'mask-control.json').write_text(json.dumps(dict(meta=meta,control=mask_control),indent=2)+'\n')
checks, inputs, observations, commands, restored_states = [], [], {}, {}, {}
initial_counters = {}
e = None
case = 'setup'


def check(ok, label):
    assert ok, case + '/' + label
    checks.append(case + '/' + label)


def region(address): return C.string_at(*e.maps[address])


def tap(key, wait=120):
    inputs.append([case, 8, key, wait])
    e.run(8, key)
    e.run(wait)


def call_setter(kind, first, count, duration, target):
    global ENTRY
    ram, iw = e.memory(), region(0x03000000)
    check(iw[0x5668] == 0, kind + ' native effect dispatcher idle at command boundary')
    a = ARM(rom, iw)
    a.put(0x02000000, ram)
    a.put(0x02008000, target)
    address = {'black': 0x08147a7d, 'white': 0x08147ad1, 'restore': 0x08147d2d,
               'gray':0x08147b29,'tint':0x08147ba5,'rgb':0x08147c2d,'solid':0x08147cc1,
               'blend':0x08147d95,'brighten':0x08147ec9,'darken':0x08147f51,
               'exposure':0x0814731d,'exposure_rgb':0x081473e5,
               'table_exposure':0x081474bd,'table_blend':0x08147e29}[kind]
    parameters={'rgb':(128,320,192),'solid':(5,17,29),'blend':(0x421f,8,8),
                'brighten':(8,),'darken':(8,),'exposure':(384,),'exposure_rgb':(128,256,384),
                'table_exposure':(0x02008000,128,256,384),'table_blend':(0x02008000,0x421f,8,8)}.get(kind)
    if parameters:
        a.put(STACK,struct.pack('<'+'I'*(len(parameters)-1),*parameters[1:]))
        task=a.call(address,first,count,duration,parameters[0])
    else:task = a.call(address, first, count, duration, 0x02008000)
    check(0x03003c68 <= task < 0x03003e68, kind + ' real native fade task allocated')
    after_ram, after_iw = a.read(0x02000000, 0x40000), a.read(0x03000000, 0x8000)
    # Only test input scratch, private reserved RAM and actual native palette
    # state may differ. Never copy input scratch or the clone's call stack back.
    expected_ram = bytearray(ram)
    expected_ram[0x8000:0x8000 + len(target)] = target
    if case == 'candidate': expected_ram[BASE - 0x02000000:LIMIT - 0x02000000] = after_ram[BASE - 0x02000000:LIMIT - 0x02000000]
    check(after_ram == expected_ram, kind + ' setter changes no gameplay heap/unit/save bytes')
    expected_iw = bytearray(iw)
    if parameters:
        # The fifth/sixth arguments are declared clone input, above the
        # downward-growing call scratch. They must remain exactly supplied.
        expected_iw[STACK-0x03000000:STACK-0x03000000+(len(parameters)-1)*4]=struct.pack('<'+'I'*(len(parameters)-1),*parameters[1:])
    expected_iw[0x3860:0x5669] = after_iw[0x3860:0x5669]
    expected_iw[0x6e00:0x7000] = after_iw[0x6e00:0x7000]
    check(after_iw == expected_iw, kind + ' setter changes only native palette/effect state and clone stack')
    C.memmove(e.maps[0x03000000][0] + 0x3860, after_iw[0x3860:0x5669], 0x1e09)
    if case == 'candidate':
        e.set_memory(BASE - 0x02000000, after_ram[BASE - 0x02000000:LIMIT - 0x02000000])
        keys=after_ram[BASE-0x02000000+meta['variantOffset']:BASE-0x02000000+meta['variantOffset']+SLOTS]
        key=16+(first-256)//16
        check(key in keys,kind+' exact class/native-bank binding exists')
        ENTRY=BO+keys.index(key)*meta['bindingEntryBytes']
        check(struct.unpack_from('<I', after_ram, ENTRY + 244)[0] == task, kind + ' generated palette bound to exact native task')
    inputs.append([case, 'native setter clone', hex(address), first, count, duration, sha(target), task])
    return task, iw, ram


def oracle(iw, source, target, duration, first):
    a = ARM(oracle_rom, iw)
    a.put(0x03003860 + first * 2, source)
    for i in range(16): a.put(0x03003e68 + (first + i) * 12, target[i * 2:i * 2 + 2])
    task = a.call(0x08146e55, first, first + 15, duration, 0)
    sequence = [source.hex()]
    for _ in range(max(1, duration)):
        a.call(0x08148741, task)
        sequence.append(a.read(0x03003860 + first * 2, 32).hex())
    return sequence

def target_colors(kind,source,restore,iw):
    if kind=='black':return bytes(32)
    if kind=='white':return b'\xff\x7f'*16
    if kind=='restore':return restore
    a=ARM(oracle_rom,iw)
    if kind=='table_exposure':
        values=[sum(max(3,(v>>s)&31)<<s for s in (0,5,10)) for v in struct.unpack('<16H',restore)]
        return struct.pack('<16H',*[a.call(0x08148384,c,128,256,384) for c in values])
    if kind=='table_blend':return struct.pack('<16H',*[a.call(0x08147830,c,0x421f,8,8) for c in struct.unpack('<16H',restore)])
    if kind in ('blend','brighten','darken','exposure','exposure_rgb'):
        fn,parameters={'blend':(0x08147830,(0x421f,8,8)),
            'brighten':(0x081478dc,(8,)),'darken':(0x08147958,(8,)),
            'exposure':(0x08148384,(384,384,384)),
            'exposure_rgb':(0x08148384,(128,256,384))}[kind]
        return struct.pack('<16H',*[a.call(fn,c,*parameters) for c in struct.unpack('<16H',source)])
    if kind=='gray':values=[a.call(0x081477dc,c) for c in struct.unpack('<16H',source)]
    elif kind=='solid':values=[5|(17<<5)|(29<<10)]*16
    else:
        coefficients=(294,273,204) if kind=='tint' else (128,320,192)
        values=[a.call(0x081483ec,c,*coefficients) for c in struct.unpack('<16H',source)]
    return struct.pack('<16H',*values)

def reload_colors(iw,source,dim):
    if not dim:return source
    a=ARM(oracle_rom,iw);a.put(0x02008000,source)
    a.call(0x08148104,0x02008000,0x02008040,16,153)
    return a.read(0x02008040,32)


def control_command(name,task,first):
    ranges={'whole':(first,first+15),'lower':(first,first+5),
            'upper':(first+10,first+15),'middle':(first+5,first+10)}
    if name in ranges:return 0x08146dc8,(*ranges[name],0xffff)
    if name=='delete':return 0x08148498,(task,)
    if name=='delete-all':return 0x08148540,()
    if name.startswith('collect'):return 0x081484cc,(task,)
    if name=='pause':return 0x08148518,(task,)
    if name=='resume':return 0x0814852c,(task,)
    if name=='pause-all':return 0x08148588,()
    if name=='resume-all':return 0x081485ac,()
    raise AssertionError(name)


def rotation_input(a,kind,first,right,partial):
    low,high=(first+3,first+12) if partial else (first,first+15)
    pc=0x08146fb8 if kind=='rotate' else 0x08147068
    parameters=(2,) if kind=='rotate' else (2,0x08419d60)
    a.put(STACK,struct.pack('<'+'I'*len(parameters),*parameters))
    task=a.call(pc,low,high,6,2 if right else 1)
    if kind=='rotate':a.call(0x0814862c,task,3)
    return task


def call_rotation(kind,first,right,partial):
    ram,iw=e.memory(),region(0x03000000)
    check(iw[0x5668]==0,kind+' dispatcher idle at rotation boundary')
    a=ARM(rom,iw);a.put(0x02000000,ram)
    task=rotation_input(a,kind,first,right,partial)
    after_ram,after_iw=a.read(0x02000000,0x40000),a.read(0x03000000,0x8000)
    expected_ram=bytearray(ram)
    if case=='candidate':expected_ram[BASE-0x02000000:LIMIT-0x02000000]=after_ram[BASE-0x02000000:LIMIT-0x02000000]
    check(after_ram==expected_ram,kind+' constructor changes no gameplay unit heap save bytes')
    expected_iw=bytearray(iw)
    parameters=(2,) if kind=='rotate' else (2,0x08419d60)
    expected_iw[STACK-0x03000000:STACK-0x03000000+len(parameters)*4]=struct.pack('<'+'I'*len(parameters),*parameters)
    expected_iw[0x3860:0x5669]=after_iw[0x3860:0x5669]
    expected_iw[0x6e00:0x7000]=after_iw[0x6e00:0x7000]
    check(after_iw==expected_iw,kind+' constructor changes only native effect state and declared clone stack')
    C.memmove(e.maps[0x03000000][0]+0x3860,after_iw[0x3860:0x5669],0x1e09)
    if case=='candidate':e.set_memory(BASE-0x02000000,after_ram[BASE-0x02000000:LIMIT-0x02000000])
    inputs.append([case,'native rotation constructor',kind,first,right,partial,task])
    return task


def rotation_oracle(iw,source,first,kind,right,partial,elapsed):
    a=ARM(oracle_rom,iw);address=0x03003860+first*2;a.put(address,source)
    if elapsed:
        a.call(0x08147ad0,first,16,17)
        for _ in range(elapsed):a.call(0x08147288)
    rotation_input(a,kind,first,right,partial)
    sequence=[a.read(address,32).hex()]
    for _ in range(26):a.call(0x08147288);sequence.append(a.read(address,32).hex())
    return sequence


def rotation_cases(first,original):
    for kind,right,partial,fade in (('rotate',False,False,False),('rotate',True,True,False),
        ('rotate',False,True,True),('rotate',True,False,True),('cycle',False,False,False),('cycle',True,True,False)):
        label='rotation-'+kind+str(int(right))+str(int(fade))
        call_reload(first,False)
        iw=region(0x03000000);native_source=iw[0x3860+first*2:0x3880+first*2]
        own_source=e.memory()[ENTRY:ENTRY+32] if case=='candidate' else colors
        elapsed=0
        if fade:
            task,_,_=call_setter('white',first,16,17,native_source);e.run(4)
            elapsed=17-struct.unpack_from('<H',region(0x03000000),task-0x03000000+12)[0]
            check(0<elapsed<17,label+' real concurrent fade active')
        task=call_rotation(kind,first,right,partial)
        command=dict(label=label,task=task,native=rotation_oracle(iw,native_source,first,kind,right,partial,elapsed))
        if case=='candidate':command['custom']=rotation_oracle(iw,own_source,first,kind,right,partial,elapsed)
        commands[case].append(command)
        for tick in range(26):
            e.run(1);record=sample(label+'-'+str(tick))
            if tick in (0,8,25):e.screenshot(out/(case+'-'+record['label']+'.png'))
        check(region(0x03000000)[0x3860+first*2:0x3880+first*2].hex()==command['native'][-1],label+' final native rotated colors exact')
        if case=='candidate':check(e.memory()[ENTRY:ENTRY+32].hex()==command['custom'][-1],label+' final generated rotated colors exact')
    target=original[first*2:first*2+32]
    native_source=region(0x03000000)[0x3860+first*2:0x3880+first*2]
    own_source=e.memory()[ENTRY:ENTRY+32] if case=='candidate' else colors
    task,iw,_=call_setter('restore',first,16,8,target)
    command=dict(label='rotation-restored',native=oracle(iw,native_source,target,8,first))
    if case=='candidate':command['custom']=oracle(iw,own_source,colors,8,first)
    commands[case].append(command)
    for tick in range(12):e.run(1);sample(command['label']+'-'+str(tick))


def call_control(name,task,first):
    ram,iw=e.memory(),region(0x03000000)
    check(iw[0x5668]==0,name+' dispatcher idle at control boundary')
    a=ARM(rom,iw);a.put(0x02000000,ram)
    pc,parameters=control_command(name,task,first);result=a.call(pc,*parameters)
    after_ram,after_iw=a.read(0x02000000,0x40000),a.read(0x03000000,0x8000)
    expected_ram=bytearray(ram)
    if case=='candidate':expected_ram[BASE-0x02000000:LIMIT-0x02000000]=after_ram[BASE-0x02000000:LIMIT-0x02000000]
    check(after_ram==expected_ram,name+' control preserves all gameplay heap unit save bytes')
    expected_iw=bytearray(iw)
    expected_iw[0x3860:0x5669]=after_iw[0x3860:0x5669]
    expected_iw[0x6e00:0x7000]=after_iw[0x6e00:0x7000]
    check(after_iw==expected_iw,name+' control changes only native palette task state and clone stack')
    C.memmove(e.maps[0x03000000][0]+0x3860,after_iw[0x3860:0x5669],0x1e09)
    if case=='candidate':e.set_memory(BASE-0x02000000,after_ram[BASE-0x02000000:LIMIT-0x02000000])
    inputs.append([case,'native control clone',name,hex(pc),parameters,result])
    return result


def control_oracle(iw,source,elapsed,first,name):
    a=ARM(oracle_rom,iw);address=0x03003860+first*2;a.put(address,source)
    task=a.call(0x08147a7c,first,16,17);sequence=[source.hex()]
    for _ in range(elapsed):
        a.call(0x08148740,task);sequence.append(a.read(address,32).hex())
    pc,parameters=control_command(name,task,first);a.call(pc,*parameters)
    if name.startswith('pause'):
        pc,parameters=control_command(name.replace('pause','resume'),task,first);a.call(pc,*parameters)
    if name not in ('whole','middle','delete','delete-all','collect-completed'):
        for _ in range(elapsed,17):
            a.call(0x08148740,task);sequence.append(a.read(address,32).hex())
    return sequence


def task_control_cases(first,original):
    names=('whole','lower','upper','middle','delete','delete-all',
           'collect-active','collect-completed','pause','pause-all')
    for name in names:
        call_reload(first,False)
        native_source=region(0x03000000)[0x3860+first*2:0x3880+first*2]
        own_source=e.memory()[ENTRY:ENTRY+32] if case=='candidate' else colors
        task,iw,_=call_setter('black',first,16,17,native_source)
        e.run(22 if name=='collect-completed' else 4)
        remaining=struct.unpack_from('<H',region(0x03000000),task-0x03000000+12)[0]
        alive=struct.unpack_from('<H',region(0x03000000),task-0x03000000)[0]
        elapsed=17-remaining if alive else 17
        check(elapsed==17 if name=='collect-completed' else 0<elapsed<17,name+' native lifetime reached')
        command=dict(label='control-'+name,kind=name,task=task,elapsed=elapsed,
                     native=control_oracle(iw,native_source,elapsed,first,name))
        if case=='candidate':command['custom']=control_oracle(iw,own_source,elapsed,first,name)
        commands[case].append(command)
        result=call_control(name,task,first)
        if name.startswith('collect'):check(result==(0 if name=='collect-completed' else task),name+' exact native collect result')
        if name.startswith('pause'):
            frozen=region(0x03000000)[0x3860+first*2:0x3880+first*2]
            own=e.memory()[ENTRY:ENTRY+212] if case=='candidate' else None
            for tick in range(6):
                e.run(1);sample(command['label']+'-pause'+str(tick))
            check(region(0x03000000)[0x3860+first*2:0x3880+first*2]==frozen,name+' native dispatcher holds colors while paused')
            check(struct.unpack_from('<H',region(0x03000000),task-0x03000000+12)[0]==remaining,name+' native dispatcher holds remaining duration')
            if case=='candidate':check(e.memory()[ENTRY:ENTRY+212]==own,name+' generated colors targets errors and duration remain paused')
            call_control(name.replace('pause','resume'),task,first)
        for tick in range(22):
            e.run(1);record=sample(command['label']+'-'+str(tick))
            if tick in (0,8,21):e.screenshot(out/(case+'-'+record['label']+'.png'))
        check(region(0x03000000)[0x3860+first*2:0x3880+first*2].hex()==command['native'][-1],name+' final native colors exact')
        if case=='candidate':
            check(e.memory()[ENTRY:ENTRY+32].hex()==command['custom'][-1],name+' final generated colors exact')
            check(struct.unpack_from('<I',e.memory(),ENTRY+244)[0]==0,name+' no stale task handle after cancellation or completion')
    target=original[first*2:first*2+32]
    native_source=region(0x03000000)[0x3860+first*2:0x3880+first*2]
    own_source=e.memory()[ENTRY:ENTRY+32] if case=='candidate' else colors
    task,iw,_=call_setter('restore',first,16,8,target)
    command=dict(label='controls-restored',native=oracle(iw,native_source,target,8,first))
    if case=='candidate':command['custom']=oracle(iw,own_source,colors,8,first)
    commands[case].append(command)
    for tick in range(12):e.run(1);sample(command['label']+'-'+str(tick))

def reload_oracle(iw,source,reloaded,duration,elapsed,first):
    a=ARM(oracle_rom,iw);address=0x03003860+first*2
    a.put(address,source)
    task=a.call(0x08147a7c,first,16,duration);sequence=[source.hex()]
    for _ in range(elapsed):
        a.call(0x08148740,task);sequence.append(a.read(address,32).hex())
    a.put(0x02008000,reloaded);a.call(a.word(0x0836d4bc),address,0x02008000,32)
    sequence.append(a.read(address,32).hex())
    for _ in range(elapsed,duration):
        a.call(0x08148740,task);sequence.append(a.read(address,32).hex())
    return sequence

def call_reload(first,dim):
    ram,iw=e.memory(),region(0x03000000);a=ARM(rom,iw);a.put(0x02000000,ram)
    source=0x08419d60
    if dim:
        a.call(0x08148104,source,0x02008000,16,153);source=0x02008000
    supplied=a.read(source,32);a.call(a.word(0x0836d4bc),0x03003860+first*2,source,32)
    after_ram,after_iw=a.read(0x02000000,0x40000),a.read(0x03000000,0x8000)
    expected_ram=bytearray(ram)
    if dim:expected_ram[0x8000:0x8020]=supplied
    if case=='candidate':expected_ram[BASE-0x02000000:LIMIT-0x02000000]=after_ram[BASE-0x02000000:LIMIT-0x02000000]
    check(after_ram==expected_ram,'reload changes only declared clone input and owned bindings')
    expected_iw=bytearray(iw);offset=0x3860+first*2
    expected_iw[offset:offset+32]=supplied;expected_iw[0x6e00:0x7000]=after_iw[0x6e00:0x7000]
    check(after_iw==expected_iw,'reload changes exact native bank only and preserves active effect records')
    C.memmove(e.maps[0x03000000][0]+offset,after_iw[offset:offset+32],32)
    if case=='candidate':e.set_memory(BASE-0x02000000,after_ram[BASE-0x02000000:LIMIT-0x02000000])
    inputs.append([case,'actual native copy callback',first,dim,hex(a.word(0x0836d4bc)),sha(supplied)])
    return supplied

def reload_cases(first,original):
    check(original[first*2:first*2+32]==rom[0x419d60:0x419d80],'reload source is the exact native ROM palette')
    for dim,completed in ((False,True),(False,False),(True,True),(True,False)):
        label=('dim' if dim else 'normal')+('-completed-reload' if completed else '-active-reload')
        native_source=region(0x03000000)[0x3860+first*2:0x3880+first*2]
        own_source=e.memory()[ENTRY:ENTRY+32] if case=='candidate' else colors
        task,start_iw,_=call_setter('black',first,16,17,original[first*2:first*2+32])
        e.run(22 if completed else 4)
        task_offset=task-0x03000000;live_iw=region(0x03000000)
        alive=struct.unpack_from('<H',live_iw,task_offset)[0]
        elapsed=17-struct.unpack_from('<H',live_iw,task_offset+12)[0] if alive else 17
        check((elapsed==17) if completed else (0<elapsed<17),label+' requested active/completed native state actually reached')
        reloaded=call_reload(first,dim)
        command=dict(label=label,kind='native-copy',duration=17,elapsed=elapsed,dim=dim,
            native=reload_oracle(start_iw,native_source,reloaded,17,elapsed,first))
        if case=='candidate':command['custom']=reload_oracle(start_iw,own_source,reload_colors(start_iw,colors,dim),17,elapsed,first)
        commands[case].append(command)
        for tick in range(22):
            e.run(1);record=sample(label+'-'+str(tick))
            if tick in (0,8,21):e.screenshot(out/(case+'-'+record['label']+'.png'))
        check(region(0x03000000)[0x3860+first*2:0x3880+first*2].hex()==command['native'][-1],label+' exact native final colors')


def sample(label):
    ram, iw, pal = e.memory(), region(0x03000000), region(0x05000000)
    record = dict(label=label, shadow=iw[0x3860:0x3c60].hex(), palette=pal.hex(), owned=sha(ram[0x80:0x1e70]))
    if case == 'candidate':
        active, applied, restored, failed = struct.unpack_from('<4I', ram, BASE - 0x02000000 + 0xa0c)
        record['live'] = dict(active=active, applied=applied, restored=restored, failed=failed,
                              counters=list(struct.unpack_from('<3I', ram, BO + COUNTERS)),
                              task=struct.unpack_from('<I', ram, ENTRY + 244)[0],
                              bank=struct.unpack_from('<I', ram, ENTRY + 248)[0],
                              colors=ram[ENTRY:ENTRY + 32].hex(), remaining=struct.unpack_from('<H', ram, ENTRY + 208)[0],
                              backup=ram[BASE - 0x02000000 + 0x80c:BASE - 0x02000000 + 0xa0c].hex())
    observations[case].append(record)
    return record


def late_cases(first,original):
    global ENTRY
    # Native21754 checks the OAM pointer and then flag0x40 before drawing.
    check(rom[0x21754:0x21762].hex()=='af6a002f74d040203040002870d0','native actor draw-enable gate authenticated')
    scenarios=[(kind,completed,False,False) for kind in ('black','rgb') for completed in (False,True)]
    if args.late_rotation:
        scenarios=[(kind,completed,right,right) for kind in ('rotate','cycle')
                   for right in (False,True) for completed in (False,True)]
    for kind,completed,right,partial in scenarios:
        label='late-'+kind+str(int(right))+('-completed' if completed else '-active')
        call_reload(first,False)
        bodies=[body for body in actors(rom,e.memory(),region(0x06000000)) if body['resource']==258]
        check(len(bodies)==1 and bool(bodies[0]['flags']&64),label+' unique enabled native actor')
        address=bodies[0]['address']
        e.set_memory(address,struct.pack('<I',bodies[0]['flags']&~64))
        inputs.append([case,'native draw-enable flag',address,False])
        e.run(4)
        check(not struct.unpack_from('<I',e.memory(),address)[0]&64,label+' actor remains disabled')
        if case=='candidate':
            check(struct.unpack_from('<I',e.memory(),BASE-0x02000000+2572)[0]==0,label+' both queued body buffers have left hardware')
            # Start this experiment with no prior ownership, invoking the same
            # owned-state initializer as a real scene reset. Copy only its
            # verified private reservation, never native/gameplay outputs.
            before=e.memory();iw=region(0x03000000);a=ARM(rom,iw);a.put(0x02000000,before)
            a.call(meta['symbols']['ffta_art_heap_reset'])
            after=a.read(0x02000000,0x40000);expected=bytearray(before)
            expected[BASE-0x02000000:LIMIT-0x02000000]=after[BASE-0x02000000:LIMIT-0x02000000]
            check(after==expected,label+' initializer changes only owned art state')
            e.set_memory(BASE-0x02000000,after[BASE-0x02000000:LIMIT-0x02000000])
            check(e.memory()[BASE-0x02000000+meta['variantOffset']:BASE-0x02000000+meta['variantOffset']+SLOTS]==bytes([255]*SLOTS),label+' no prior class bindings')
        native_source=region(0x03000000)[0x3860+first*2:0x3880+first*2]
        if args.late_rotation:
            iw=region(0x03000000)
            task=call_rotation(kind,first,right,partial)
            command=dict(label=label,kind=kind,right=right,partial=partial,
                native=rotation_oracle(iw,native_source,first,kind,right,partial,0))
            if case=='candidate':command['custom']=rotation_oracle(iw,colors,first,kind,right,partial,0)
        else:
            task,iw,_=call_setter(kind,first,16,17,original[first*2:first*2+32])
            command=dict(label=label,kind=kind,duration=17,
                native=oracle(iw,native_source,target_colors(kind,native_source,native_source,iw),17,first))
            if case=='candidate':
                command['custom']=oracle(iw,colors,target_colors(kind,colors,colors,iw),17,first)
                # This experiment starts with no bindings. Each enabled class
                # whose authenticated baseline matches this native bank owns
                # a provisional history, even while only Dark Knight is hidden.
                # Use the original native multiplier for the dim alternative.
                mask=struct.unpack_from('<I',rom,meta['symbols']['ffta_art_custom_mask']-0x08000000)[0]
                ref=meta['symbols']['ffta_art_native_reference']-0x08000000
                expected=[];oracle_a=ARM(oracle_rom,iw)
                for owner in range(10):
                    if not mask&(1<<owner):continue
                    normal=rom[ref+owner*32:ref+owner*32+32]
                    oracle_a.put(0x02008000,normal)
                    oracle_a.call(0x08148104,0x02008000,0x02008040,16,0x99)
                    if native_source in (normal,oracle_a.read(0x02008040,32)):
                        expected.append(owner*16+(first-256)//16)
                command['expectedHistoryKeys']=expected
                actual=e.memory()[BASE-0x02000000+meta['variantOffset']:BASE-0x02000000+meta['variantOffset']+SLOTS]
                check(sorted(k for k in actual if k!=255)==expected,label+' exact native-authenticated provisional histories')
        commands[case].append(command)
        e.run(22 if completed else 4)
        if args.late_rotation:
            state=struct.unpack_from('<H',region(0x03000000),task-0x03000000)[0]
            check((state==0) if completed else (state==1),label+' native rotation lifetime reached while hidden')
        if case=='candidate':
            check(struct.unpack_from('<I',e.memory(),BASE-0x02000000+2572)[0]==0,label+' effect advances with no generated overlay')
            if args.late_rotation:
                ram=e.memory();offset=BASE-0x02000000+meta['variantOffset']
                keys=ram[offset:offset+SLOTS];key=16+(first-256)//16
                check(key in keys,label+' exact class/bank history acquired before emission')
                ENTRY=BO+keys.index(key)*meta['bindingEntryBytes']
                check(list(struct.unpack_from('<3I',ram,BO+COUNTERS))==[0,0,0],label+' unseen history exists without any fade starts or refusals')
                check(ram[ENTRY:ENTRY+32]!=colors,label+' unseen callback changed generated colors')
            else:
                alive=struct.unpack_from('<I',e.memory(),ENTRY+244)[0]
                check(bool(alive)==(not completed),label+' requested effect lifetime reached before first appearance')
        flags=struct.unpack_from('<I',e.memory(),address)[0]
        check(not flags&64,label+' no hidden actor was prematurely reenabled')
        e.set_memory(address,struct.pack('<I',flags|64));inputs.append([case,'native draw-enable flag',address,True])
        # Native double buffering may take two frames to emit and select OAM.
        # For rotation, capture those frames too: first displayed colors must
        # already be correct, not merely settle after a three-frame blind spot.
        if not args.late_rotation:e.run(3)
        for tick in range(25 if args.late_rotation else 22):
            e.run(1);record=sample(label+'-'+str(tick))
            if args.late_rotation:record['appearancePendingAllowed']=tick<3
            if tick in (0,8,21):e.screenshot(out/(case+'-'+record['label']+'.png'))


try:
    for case, path, digest in [('baseline', meta['source'], meta['baseRomSha1']), ('candidate', meta['path'], meta['romSha1'])]:
        rom = Path(path).read_bytes()
        check(hashlib.sha1(rom).hexdigest() == digest, 'ROM authenticated')
        observations[case], commands[case] = [], []
        e = E(Path(path))
        e.set_memory(0, seed, 0)
        e.run(3600)
        for key in (8, 256, 256, 256): tap(key, 300)
        check(e.memory()[0x80 + 2 * 264 + 6] == 1, 'same-race member selected')
        e.set_memory(0x80 + 2 * 264 + 4, bytes([1, 117, 1, 117]))
        inputs.append([case, 'isolated appearance profile', 2, [1, 117, 1, 117]])
        for key in (8, 256, 128, 128, 256, 32, 32, 256): tap(key, 600 if key == 256 else 120)
        original = region(0x03000000)[0x3860:0x3c60]
        native_bank = 0
        if case == 'candidate':
            keys=e.memory()[BASE-0x02000000+meta['variantOffset']:BASE-0x02000000+meta['variantOffset']+SLOTS]
            check(16 in keys,'actual Dark Knight normal-bank identity captured')
            ENTRY=BO+keys.index(16)*meta['bindingEntryBytes']
            native_bank = struct.unpack_from('<I', e.memory(), ENTRY + 248)[0]
            check(native_bank == 0, 'actual native palette origin captured before remapping')
            check(e.memory()[ENTRY + 212:ENTRY + 244] == original[512:544], 'unfaded native palette baseline authenticated')
        first = 256 + native_bank * 16
        if case=='candidate':initial_counters[case]=list(struct.unpack_from('<3I',e.memory(),BO+COUNTERS))
        if args.rotation:
            rotation_cases(first,original);restored_states[case]=observations[case][-1]
            e.close();e=None
            continue
        if args.task_controls:
            task_control_cases(first,original);restored_states[case]=observations[case][-1]
            e.close();e=None
            continue
        if args.late_entry or args.late_rotation:
            late_cases(first,original);restored_states[case]=observations[case][-1]
            e.close();e=None
            continue
        if args.reload:
            reload_cases(first,original);restored_states[case]=observations[case][-1]
            e.close();e=None
            continue
        # The fourth command interrupts the preceding black fade before it ends.
        schedule=[('black', 'black', 8, 12), ('white', 'white', 8, 12),
                                             ('restore', 'restore', 17, 21), ('partial-black', 'black', 17, 5),
                                             ('interrupt-white', 'white', 8, 12), ('restore-again', 'restore', 8, 12)]
        if args.color_operations:
            schedule=[('gray','gray',8,12),('restore','restore',8,12),('tint','tint',8,12),
                ('rgb','rgb',17,21),('solid','solid',8,12),('partial-rgb','rgb',17,5),
                ('interrupt-gray','gray',8,12),('restore-again','restore',8,12)]
        if args.extended_color_operations:
            schedule=[('blend','blend',8,12),('brighten','brighten',8,12),('darken','darken',17,21),
                ('exposure','exposure',8,12),('exposure_rgb','exposure_rgb',17,21),
                ('partial-darken','darken',17,5),('interrupt-exposure','exposure',8,12),
                ('restore-again','restore',8,12)]
        if args.table_color_operations:
            schedule=[('table_exposure','table_exposure',8,12),('table_blend','table_blend',17,21),
                ('partial-black','black',17,5),('interrupt-table-exposure','table_exposure',8,12),
                ('table-blend-again','table_blend',8,12),('restore-again','restore',8,12)]
        for label,kind,duration,frames in schedule:
            target = original[first * 2:first * 2 + 32]
            native_source = region(0x03000000)[0x3860 + first * 2:0x3880 + first * 2]
            own_source = e.memory()[ENTRY:ENTRY + 32] if case == 'candidate' else colors
            task, iw, _ = call_setter(kind, first, 16, duration, target)
            if kind in ('exposure','exposure_rgb'):
                def floor_source(raw):return struct.pack('<16H',*[sum(max(3,(v>>s)&31)<<s for s in (0,5,10)) for v in struct.unpack('<16H',raw)])
                native_source=floor_source(native_source);own_source=floor_source(own_source)
            native_target = target_colors(kind,native_source,target,iw)
            own_target = target_colors(kind,own_source,colors,iw)
            command = dict(label=label, kind=kind, task=task, duration=duration, frames=frames,
                           native=oracle(iw, native_source, native_target, duration, first))
            if case == 'candidate': command['custom'] = oracle(iw, own_source, own_target, duration, first)
            commands[case].append(command)
            for tick in range(frames):
                e.run(1)
                record = sample(label + '-' + str(tick))
                if tick in (0, duration // 2, frames - 1):
                    e.screenshot(out / (case + '-' + record['label'] + '.png'))
            check(region(0x03000000)[0x3860 + first * 2:0x3880 + first * 2].hex() in command['native'], label + ' native colors follow original callback oracle')
        restored_states[case] = observations[case][-1]
        if args.color_operations or args.extended_color_operations or args.table_color_operations:
            e.close();e=None
            continue
        # A completed fade may outlive one menu consumer. Native menu loaders
        # can restore the bank while reusing the same class and bank identity.
        call_setter('black', first, 16, 8, original[first * 2:first * 2 + 32])
        e.run(12)
        sample('lifecycle-black')
        tap(1, 180)
        sample('lifecycle-header')
        tap(256, 600)
        sample('lifecycle-reopened')
        e.screenshot(out / (case + '-lifecycle-reopened.png'))
        e.close()
        e = None
    baseline = {r['label']: r for r in observations['baseline']}
    for command in commands['candidate']:
        for record in [r for r in observations['candidate'] if r['label'].rsplit('-', 1)[0] == command['label']]:
            label, live = record['label'], record['live']
            before = baseline[label]
            check(record['shadow'] == before['shadow'], label + ' exact paired native palette state')
            check(record['owned'] == before['owned'], label + ' canonical units unchanged')
            check(live['failed'] == 0 and live['counters'][2] == 0, label + ' no unsupported binding or allocation failure')
            if args.late_rotation and not live['active']:
                check(record.get('appearancePendingAllowed',False),label+' absent overlay limited to initial native double-buffer transfer')
                check(record['palette']==before['palette'],label+' before first emission every hardware color is native')
                continue
            check(live['active'] != 0, label + ' generated actor retains palette ownership')
            palette = bytes.fromhex(record['palette'])
            expected = bytearray.fromhex(before['palette'])
            # Only overwritten banks have a current backup. A native bank
            # that remains unowned is still directly readable in hardware.
            source = bytes.fromhex(live['backup']) if live['active'] & (1 << live['bank']) else palette[512:1024]
            native_visible = source[live['bank'] * 32:live['bank'] * 32 + 32].hex()
            phases = [i for i, value in enumerate(command['native']) if value == native_visible]
            check(bool(phases), label + ' exact native hardware fade phase identified')
            for bank in range(16):
                if live['active'] & (1 << bank):
                    actual = palette[512 + bank * 32:544 + bank * 32]
                    check(actual.hex() in [command['custom'][i] for i in phases], label + ' custom hardware colors match native interpolation at the same phase')
                    expected[512 + bank * 32:544 + bank * 32] = actual
            check(bytes(expected) == palette, label + ' every unowned hardware color unchanged')
    final = restored_states['candidate']['live']
    starts=8 if args.color_operations or args.extended_color_operations else 6
    initial=initial_counters['candidate']
    if args.rotation:
        check(final['colors']==colors.hex() and final['task']==0 and final['counters']==[initial[0]+3,initial[1]+3,0],'two concurrent fades and restore complete exactly without refusal')
    elif args.task_controls:
        check(final['colors']==colors.hex() and final['task']==0 and final['counters']==[initial[0]+11,initial[1]+7,0],'ten controls and restore: four cancellations, seven completions, no refusal')
    elif args.late_rotation:
        check(final['colors']==commands['candidate'][-1]['custom'][-1] and final['task']==0 and final['counters']==[0,0,0],'last unseen rotation completes with exact colors and no fade starts or refusal')
    elif args.late_entry:
        histories=len(commands['candidate'][-1]['expectedHistoryKeys'])
        check(final['colors']==commands['candidate'][-1]['custom'][-1] and final['task']==0 and final['counters']==[histories,histories,0],'last isolated first-appearance effect completed every authenticated history exactly with no refusal')
    elif args.reload:
        check(final['colors']==commands['candidate'][-1]['custom'][-1] and final['task']==0 and final['counters']==[initial[0]+4,initial[1]+4,0],'four reload scenarios complete with exact generated final colors and no refusal')
    else:check(final['colors'] == colors.hex() and final['task'] == 0 and final['counters'] == [initial[0]+starts, initial[1]+starts-1, 0], 'exact starts/completions, one interruption and original generated colors restored')
    for record in [r for r in observations['candidate'] if r['label'].startswith('lifecycle-')]:
        label, live = record['label'], record['live']
        before = baseline[label]
        check(record['shadow'] == before['shadow'] and record['owned'] == before['owned'], label + ' native palette and units match through consumer replacement')
        native = bytes.fromhex(before['palette'])[512:544]
        check(native in (bytes(32), original[512:544]), label + ' observed native bank is black or exactly restored')
        expected = bytearray.fromhex(before['palette'])
        for bank in range(16):
            if live['active'] & (1 << bank):
                expected[512 + bank * 32:544 + bank * 32] = bytes(32) if native == bytes(32) else colors
        check(bytes(expected) == bytes.fromhex(record['palette']), label + ' custom colors follow actual native bank restoration across cancel/reopen')
    check(seedpath.read_bytes() == seed, 'source save unchanged')
    report = dict(status='passed', checks=checks, inputs=inputs, observations=observations, commands=commands,
                  initialCounters=initial_counters,
                  maskControl=mask_control,
                  romSha1=meta['romSha1'], baseRomSha1=meta['baseRomSha1'], oracleRomSha1=oldmeta['romSha1'],
                  scope='Controlled original native fade setter input on paused-state clones, actual live native callback/DMA playback for Dark Knight black/white/explicit baseline restore and interruption. Exact paired native/unowned hardware/unit isolation. Not naturally triggered campaign fades, all native effect kinds, all classes/variants, battle or heap capacity acceptance.')
    if args.color_operations:
        report['scope']='Controlled native gray/preset tint/RGB multipliers/solid setters with actual live callback and hardware playback, interruption and baseline restoration. Exact original conversion/interpolation oracle and paired native/unowned hardware/unit isolation. No late entry, palette reload, naturally triggered campaign effects, all classes/variants or timing acceptance.'
    if args.extended_color_operations:
        report['scope']='Controlled weighted blend, partial brighten/darken and uniform/per-channel exposure including immediate source floor, actual native callbacks/hardware, interruption and baseline restore. Exact native conversion/interpolation oracle, paired native/unowned colors/units. No table-source variants, natural scenes or all-class/capacity/timing acceptance.'
    if args.table_color_operations:
        report['scope']='Two seven-argument native source-table setters with authenticated baseline source, actual callbacks/hardware, interruption and baseline restore. Source-table bytes preserved by input guard; exact independent native/generated conversion and interpolation oracle, paired native/unowned colors/units. No arbitrary transformed table identity, natural scene/all-class/capacity/timing acceptance.'
    if args.reload:
        report['scope']='Actual native copy callback reload commands followed by live hardware/callback playback, normal/dim colors after completed black fades and during active fades, exact independent native and generated oracle, preserved native effect records and every unowned hardware color/unit. No late entry, unknown/partial reload support, every copy mechanism, all scenes or battle timing acceptance.'
    if args.late_entry:
        report['scope']='Controlled native actor draw-enable hide/reveal in an existing menu, owned-state initializer removes prior bindings, installed black/RGB setters before first emission, actual callbacks and hardware colors during/after effects, exact paired native/unowned/unit isolation. Not a naturally triggered scene transition, every effect/class/capacity case or timing acceptance.'
    if args.late_rotation:
        report['scope']='Eight controlled native hide/reset/rotate-or-cycle/reveal cases: both directions, full or partial single-bank ranges, active/completed tasks before first emission, no fade starts, actual mGBA callbacks and hardware colors. Original native dispatcher oracle, exact paired native/unowned colors and units. Not natural scene triggers, all classes, cross-bank identity, capacity or battle timing acceptance.'
    if args.task_controls:
        report['scope']='Actual native cancellation, lower/upper range trimming, middle/full deletion, direct/all deletion, active/completed collection and single/all pause-resume commands. Live callbacks, held duration/error state while paused, paired native/unowned hardware/unit isolation, independent generated oracle and final restore. Controlled menu fixture; not natural scenes, heap destruction, all classes/capacity or battle timing acceptance.'
    if mask_control:report['scope']='Single-enabled-class diagnostic; not all-class acceptance. '+report['scope']
    if args.rotation:
        report['scope']='Actual type2 rotation/type4 literal cycling callbacks and hardware with both directions, partial/full bank ranges, delay2/step3, concurrent white fades, exact native/generated original dispatcher oracle, unowned hardware/unit isolation and final restoration. Controlled menu inputs; not cross-bank identity support, all classes/capacity, natural triggers or battle timing acceptance.'
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='passed', checks=len(checks), report=str(out / 'report.json'))))
except Exception as error:
    if e:
        e.screenshot(out / (case + '-failed.png'))
        (out / (case + '-failed.ram')).write_bytes(e.memory())
        (out / (case + '-failed.iwram')).write_bytes(region(0x03000000))
    (out / 'failed.json').write_text(json.dumps(dict(status='failed', error=str(error), checks=checks, inputs=inputs,
                                                   observations=observations, commands=commands, romSha1=meta['romSha1'],maskControl=mask_control), indent=2) + '\n')
    print(str(out))
    raise
finally:
    if e: e.close()
