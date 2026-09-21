"""Execute the compiled frame palette planner on retained OAM and rejection cases."""
import argparse,ast,datetime,json,random,struct,subprocess,sys
from pathlib import Path
from native_art import ROOT,sha
from art_palette_build import write_pixel_banks
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
arm_source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace(
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
out=ROOT/'build/art/palette-plan'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--fast-bank-scan',action='store_true')
parser.add_argument('--block-scan',action='store_true')
parser.add_argument('--burst-scan',action='store_true')
parser.add_argument('--joined-rows',action='store_true')
parser.add_argument('--rect-conflict',action='store_true')
parser.add_argument('--fast-oam-plan',action='store_true')
parser.add_argument('--arm-oam-scan',action='store_true')
parser.add_argument('--scoped-frame',action='store_true')
parser.add_argument('--native-prefix',action='store_true')
parser.add_argument('--shared-scanner',action='store_true')
args=parser.parse_args()
if args.shared_scanner:args.burst_scan=args.scoped_frame=args.native_prefix=True
if args.burst_scan:args.block_scan=True
if args.block_scan:args.fast_bank_scan=True
if args.native_prefix:args.scoped_frame=args.arm_oam_scan=args.fast_bank_scan=True
if args.arm_oam_scan:args.fast_oam_plan=True
elf=out/'plan.elf';binary=out/'plan.bin';entry=0x09f90000
lookup,lookup_bytes=write_pixel_banks(out)
extra=['-DFFTA_ART_FAST_BANK_SCAN=1','src/engine/art-palette-bank-scan.s'] if args.fast_bank_scan else []
if args.shared_scanner:
    shim=out/'scanner-entry.s'
    shim.write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n.align 2\n.global reviewed_scanner_entry\n.thumb_func\nreviewed_scanner_entry:\n ldr r3,=ffta_art_bank_span_fast\n bx r3\n.ltorg\n')
    extra+=['-DFFTA_ART_GROUPED_PALETTES=1',str(shim)]
if args.rect_conflict:extra+=['-DFFTA_ART_RECT_CONFLICT=1','-Wa,--defsym,FFTA_ART_RECT_CONFLICT=1']
if args.joined_rows:extra+=['-DFFTA_ART_JOINED_ROWS=1']
if args.burst_scan:extra+=['-Wa,--defsym,FFTA_ART_BURST_SCAN=1']
if args.block_scan:extra+=['-Wa,--defsym,FFTA_ART_BLOCK_SCAN=1']
if args.fast_oam_plan:extra+=['-DFFTA_ART_FAST_OAM_PLAN=1']
if args.arm_oam_scan:extra+=['-DFFTA_ART_ARM_OAM_SCAN=1','src/engine/art-oam-demands.s']
scoped_proof=None
if args.scoped_frame:
    from art_scoped_build import build_scoped
    assembly,scoped_proof=build_scoped(out,10)
    extra+=['-DFFTA_ART_SCOPED_FRAME=1',str(assembly)]
if args.native_prefix:extra+=['-DFFTA_ART_NATIVE_OAM_PREFIX=1']
compiled=subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext='+hex(entry),'-Wl,-e,ffta_art_palette_apply','src/engine/art-palette-plan.c', 'src/engine/art-palette-scan.s',*extra,str(lookup),'-o',str(elf)],cwd=ROOT,capture_output=True,text=True)
(out/'compile.log').write_text(compiled.stdout+compiled.stderr)
if compiled.returncode:print(compiled.stderr)
compiled.check_returncode()
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
symbols={line.split()[2]:int(line.split()[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(line.split())==3}
if args.shared_scanner and '__ffta_art_bank_span_fast_from_thumb' not in symbols:
    symbols['__ffta_art_bank_span_fast_from_thumb']=symbols['reviewed_scanner_entry']
code=binary.read_bytes();assert len(code)<0x40000
source=ROOT/'build/art/palette-ownership/20260918T020302.811405Z/report.json'
proof=json.loads(source.read_text());assert proof['status']=='passed' and len(proof['captures'])==50
oldproof=Path(proof['sourceReport']);assert sha(oldproof.read_bytes())==proof['sourceReportSha256']
observed=json.loads(oldproof.read_text());captures=oldproof.parent
palpath=ROOT/'build/art/imagegen/human-dark-knight/march-v2-own-palette/palette.bin'
custom=palpath.read_bytes();assert sha(custom)=='4803df6e40ba73159e547a5a387eccf7db897170a4934d87e43ef25f21401a53'
rom=bytearray(b'\xff'*0x2000000);rom[entry-0x08000000:entry-0x08000000+len(code)]=code
a=ARM(rom,bytes(0x8000));checks=[];records=[]
F,O,V,P,C,T,R=0x02010000,0x02011000,0x02020000,0x02012000,0x02012400,0x02013000,0x02013100
CACHE=0x02014000
a.put(CACHE-4,b'\xd7'*4);a.put(CACHE+2124,b'\xe9'*4)
def check(ok,label):
    assert ok,label
    checks.append(label)
def apply(oam,obj,palette,owners,colors=custom,one_d=1):
    assert len(oam)==1024 and len(obj)==32768 and len(palette)==512 and len(owners)==128
    a.put(O,oam);a.put(V,obj);a.put(P,palette);a.put(T,owners);a.put(C,colors);a.put(R,b'\xa5'*16)
    a.put(F,struct.pack('<8I',O,V,T,P,C,R,one_d,len(colors)//32))
    result=a.call(symbols['ffta_art_palette_apply'],F)
    expected=result,a.read(O,1024),a.read(P,512),a.read(R,16)
    for repeat in range(2):
        a.put(O,oam);a.put(P,palette);a.put(R,b'\xa5'*16)
        result=a.call(symbols['ffta_art_palette_apply_cached'],F,CACHE)
        check((result,a.read(O,1024),a.read(P,512),a.read(R,16))==expected,'Exact cached/uncached result including changed input, repeat '+str(repeat))
        check(a.read(CACHE-4,4)==b'\xd7'*4 and a.read(CACHE+2124,4)==b'\xe9'*4,'Cache writes stay within2124 bytes')
    a.put(O,oam);a.put(P,palette)
    preferred=a.call(symbols['ffta_art_palette_reapply'],F)
    if preferred:
        check((preferred,a.read(O,1024),a.read(P,512),a.read(R,16))==expected,'Validated preferred bank preserves exact current full-plan result')
    else:
        check(a.read(O,1024)==oam and a.read(P,512)==palette,'Preferred-bank refusal writes no OAM or palette bytes')
    backup=0x02016000
    for stack in ((0x03007800,0x03007804,STACK,0x0201c000) if args.scoped_frame else (STACK,)):
      for prior in (b'\xa5'*16,expected[3]):
        a.put(O,oam);a.put(P,palette);a.put(R,prior);a.put(backup,b'\xc7'*512)
        result=a.call(symbols['ffta_art_palette_live_apply'],F,CACHE,backup,stack=stack)
        check((result,a.read(O,1024),a.read(P,512),a.read(R,16))==expected,'Live validated snapshot/apply exact with fresh or reused plan')
        saved=bytearray(b'\xc7'*512)
        if result:
            wanted=struct.unpack_from('<H',expected[3],2)[0]
            for owner in range(len(colors)//32):
                if wanted&(1<<owner):
                    bank=expected[3][4+owner];saved[bank*32:bank*32+32]=palette[bank*32:bank*32+32]
        check(a.read(backup,512)==saved,'Only allocated native banks backed up; refusal preserves backup')
    if args.native_prefix:
        count=128
        while count and owners[count-1]==255 and oam[(count-1)*8:(count-1)*8+6]==bytes.fromhex('a800f8000000'):count-=1
        for prior in (b'\xa5'*16,expected[3]):
            a.put(O,oam);a.put(P,palette);a.put(R,prior);a.put(backup,b'\xc7'*512)
            result=a.call(symbols['ffta_art_palette_live_apply_prefix'],F,CACHE,backup,count,stack=0x03007800)
            check((result,a.read(O,1024),a.read(P,512),a.read(R,16))==expected,'Native-prefix plan/apply exactly matches full128-slot oracle')
            check(a.read(backup,512)==saved,'Native-prefix exact backup including rejection')
        unchanged=a.read(O,1024),a.read(P,512),a.read(R,16),a.read(backup,512)
        result=a.call(symbols['ffta_art_palette_live_apply_prefix'],F,CACHE,backup,129,stack=0x03007800)
        check(result==0 and (a.read(O,1024),a.read(P,512),a.read(R,16),a.read(backup,512))==unchanged,'Invalid prefix refuses without writes')
    return expected
try:
    if args.native_prefix:
        for count in (0,1,5,31,127,128):
            objects=bytearray(bytes.fromhex('a800f8000000cdab')*128);tags=bytearray([255]*128)
            for i in range(count):struct.pack_into('<4H',objects,i*8,64,0x8040,0x2200+i,0xabcd)
            if count:tags[0]=0;tags[count-1]=9
            values=bytes((i*37)&255 for i in range(320))
            result=apply(bytes(objects),bytes(32768),bytes(range(256))*2,bytes(tags),values)
            check(result[0]==1,'Native sentinel tail works at prefix bound '+str(count))
    if args.arm_oam_scan:
        demand=0x02018000;rng=random.Random(0x20260919)
        cases=[]
        for index in (0,31,63,95,127):
            for owner in (0,9,19,20,254,255):
                for attr0,attr1 in ((0,0x8000),(0x200,0xc000),(0x100,0x8000),(0x2000,0x8000),(0xc000,0x8000),(0,0),(0x2100,0xc000)):
                    objects=bytearray(struct.pack('<4H',0x200,0,0,0)*128);tags=bytearray([255]*128)
                    struct.pack_into('<4H',objects,index*8,attr0,attr1,0xf3ff,0xbabe);tags[index]=owner
                    cases.append((bytes(objects),bytes(tags),20,128))
        for n in range(40):
            objects=bytearray();tags=bytearray()
            for index in range(128):
                owner=rng.choice((255,255,255,0,4,9,19))
                a0,b0=(0,0x8000) if owner!=255 else (rng.choice((0,0x200,0x2000,0x4000,0x6000,0x8000,0xa000)),rng.randrange(4)<<14)
                objects+=struct.pack('<4H',a0,b0,rng.randrange(65536),rng.randrange(65536));tags.append(owner)
            cases.append((bytes(objects),bytes(tags),20,rng.choice((0,1,31,64,128,129))))
        for case_id,(objects,tags,owners,limit) in enumerate(cases):
            used=wanted=0;eight=[];valid=limit<=128
            for index in range(min(limit,128)):
                av,bv,cv,_=struct.unpack_from('<4H',objects,index*8);owner=tags[index]
                if av&0x300==0x200:continue
                if av>>14==3:valid=False;break
                if owner!=255:
                    if owner>=owners or av&0xe100 or bv>>14!=2:valid=False;break
                    wanted|=1<<owner
                elif av&0x2000:eight.append(index)
                else:used|=1<<(cv>>12)
            a.put(O,objects);a.put(T,tags);a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,owners))
            a.put(0x03006d00,b'\x7b'*0x68)
            for stack in (0x03007800,0x03007804,0x03007000,0x0201c000):
                a.put(demand-4,b'pre!');a.put(demand,b'\xa5'*140);a.put(demand+140,b'end!')
                before=a.read(0x03006d68,0x1298);executed=set()
                hook=a.u.hook_add(UC_HOOK_CODE,lambda u,pc,size,user:executed.add(pc),begin=0x03006d68,end=0x03007fff)
                actual=a.call(symbols['__ffta_art_oam_demands_from_thumb'],F,demand,limit,stack=stack);a.u.hook_del(hook)
                check(actual==int(valid),'ARM current-OAM validation '+str((case_id,stack)))
                if valid:
                    check(a.read(demand,12+len(eight))==struct.pack('<3I',used,wanted,len(eight))+bytes(eight),'Exact independent demand masks/list '+str((case_id,stack)))
                check(a.read(O,1024)==objects and a.read(T,128)==tags,'Object/tag inputs read-only '+str((case_id,stack)))
                check(a.read(demand-4,4)==b'pre!' and a.read(demand+140,4)==b'end!','140-byte demand scratch bounds '+str((case_id,stack)))
                check(a.read(0x03006d00,0x68)==b'\x7b'*0x68,'Native IWRAM fence '+str((case_id,stack)))
                check(bool(executed)==(stack in (0x03007800,0x03007804)),'Scoped IWRAM or exact ROM fallback '+str((case_id,stack)))
                if stack==0x0201c000:check(a.read(0x03006d68,0x1298)==before,'External stack leaves all IWRAM untouched '+str(case_id))
    if args.fast_oam_plan:
        for position in (0,1,2,3,4,31,63,124,125,126,127):
            for attr0,attr1,attr2,mask in ((0xa8,0xf8,0,1),(0xa8,0xf8,3<<12,9),(0,0,4<<12,17),(0x200,0,15<<12,1)):
                objects=bytearray(struct.pack('<4H',0xa8,0xf8,0,0xffff)*128)
                tags=bytearray([255]*128)
                target=(position+1)%128;struct.pack_into('<4H',objects,target*8,0,0x8000,0,0xffff);tags[target]=0
                struct.pack_into('<4H',objects,position*8,attr0,attr1,attr2,0x5a5a)
                result,oam,palette,plan=apply(objects,bytes(32768),bytes(512),tags)
                check(result==1 and struct.unpack_from('<H',plan)[0]==mask,'Exact grouped native tail with exceptional lane '+str((position,attr0,attr1,attr2)))
    if args.fast_bank_scan:
        rng=random.Random(0x20260918)
        native_fence=bytes([0x7b])*0x68
        a.put(0x03006d00,native_fence)
        cases=[]
        for value in range(256):
            for lane in range(4):
                raw=bytearray(64);raw[lane]=value
                cases.append((bytes(raw),16,1,64))
        for rows in (1,2,4,8):
            for words in (16,32,64,128):
                for gap in (0,64):
                    stride=words*4+gap
                    raw=bytes(rng.choice((0,0,1,15,16,31,64,128,240,255)) for _ in range(stride*rows))
                    cases.append((raw,words,rows,stride))
        if args.block_scan:
            # Prime an all-zero tile before a change at every byte, including
            # the last comparison lane. Later stack variants exercise the hit.
            for byte in range(64):
                for value in (1,240):
                    raw=bytearray(64);raw[byte]=value
                    cases.extend([(bytes(64),16,1,64),(bytes(raw),16,1,64)])
        cases.extend([(bytes(64),0,1,64),(bytes(64),16,0,64)])
        for index,(raw,words,rows,stride) in enumerate(cases):
            expected=0
            for row in range(rows):
                for pixel in raw[row*stride:row*stride+words*4]:
                    if pixel:expected|=1<<(pixel>>4)
            a.put(V,raw);a.put(V-4,b'pre!');a.put(V+len(raw),b'end!')
            for stack in ((0x03007800,0x03007804,0x03007000,0x02018000) if args.burst_scan else (0x03007800,0x03007000,0x02018000)):
                before=a.read(0x03006d68,0x1298)
                descriptor=0x02013200
                a.put(descriptor,struct.pack('<5I',V,words,rows,stride,CACHE))
                actual=a.call(symbols['__ffta_art_bank_span_fast_from_thumb'],descriptor,stack=stack)
                check(actual==expected,'Exact direct bank-mask oracle '+str((index,stack)))
                check(a.read(V-4,len(raw)+8)==b'pre!'+raw+b'end!','Read-only source span '+str((index,stack)))
                check(a.read(0x03006d00,0x68)==native_fence,'Native IWRAM fence '+str((index,stack)))
                check(a.read(CACHE-4,4)==b'\xd7'*4 and a.read(CACHE+2124,4)==b'\xe9'*4,'Exact tile-cache bounds '+str((index,stack)))
                if stack==0x02018000:check(a.read(0x03006d68,0x1298)==before,'External-stack fallback leaves IWRAM untouched '+str(index))
    if args.burst_scan:
        # Wrapper saves24 bytes; leaf uses48, code512, interrupt reserve512.
        minimum=0x03006d68+512+512+48+24
        check(symbols['ffta_art_bank_span_end']-symbols['ffta_art_bank_span']==512,'Exact burst leaf fits512-byte scoped copy')
        for stack in (minimum-4,minimum,minimum+4,0x02018000):
            raw=bytes([0x21])*64;a.put(V,raw)
            a.put(descriptor,struct.pack('<5I',V,16,1,64,0))
            before=a.read(0x03000000,0x6f68);executed=[]
            hook=a.u.hook_add(UC_HOOK_CODE,lambda u,pc,size,user:executed.append(pc),begin=0x03006d68,end=0x03007fff)
            result=a.call(symbols['__ffta_art_bank_span_fast_from_thumb'],descriptor,stack=stack)
            a.u.hook_del(hook)
            check(result==4,'Exact burst boundary result '+hex(stack))
            check(bool(executed)==(minimum<=stack<0x03008000),'Actual burst scoped/fallback cutoff '+hex(stack))
            check(a.read(0x03000000,0x6f68)==before,'Native resident and512-byte interrupt reserve unchanged '+hex(stack))
    for record in proof['captures']:
        case='generated-'+str(record['job']);phase=record['phase'];label=case+'/'+phase
        stem=captures/(case+'-'+phase);data={k:stem.with_suffix('.'+k).read_bytes() for k in ('oam','vram','palette')}
        for key,value in data.items():check(sha(value)==observed['observations'][case][phase][key],label+' authentic '+key)
        owners=bytearray([255]*128);index=record['actor']['index'];owners[index]=0
        result,oam,palette,plan=apply(data['oam'],data['vram'][0x10000:0x18000],data['palette'][512:1024],owners)
        occupied=sum(1<<int(bank) for bank,entries in record['bankOwners'].items() if any(v['kind']!='customActor' for v in entries))
        used,wanted,*rest=struct.unpack('<HH10BH',plan);slot=rest[0]
        check(result==1 and used==occupied and wanted==1,label+' exact retained noncustom palette demand')
        check(slot==next(i for i in range(16) if not occupied&(1<<i)),label+' deterministic unused-slot selection')
        expected=bytearray(data['oam']);old=struct.unpack_from('<H',expected,index*8+4)[0];struct.pack_into('<H',expected,index*8+4,(old&0xfff)|(slot<<12))
        check(oam==expected,label+' only owned palette nibble changes')
        expected=bytearray(data['palette'][512:1024]);expected[slot*32:slot*32+32]=custom
        check(palette==expected,label+' only allocated color bank changes')
        check(a.read(V,32768)==data['vram'][0x10000:0x18000] and a.read(T,128)==owners and a.read(C,32)==custom,label+' input pixels/tags/colors unchanged')
        records.append(dict(job=record['job'],phase=phase,occupied=occupied,slot=slot))
    # Explicit isolated renderer inputs, not a new game fixture.
    disabled=bytearray(struct.pack('<4H',0x200,0,0,0)*128);tags=bytearray([255]*128)
    for i in range(2):struct.pack_into('<4H',disabled,i*8,0,0x8000,0,0);tags[i]=i
    two=custom+bytes(reversed(custom));r,o,p,plan=apply(disabled,bytes(32768),bytes(512),tags,two)
    check(r==1 and plan[4:6]==bytes((0,1)) and p[:64]==two,'Two distinct owners allocate distinct slots and exact palettes')
    # Transparent index 0 and opaque indices 1..15 share a bank signature.
    # Exercise changes within that signature and repeated shade runs; the
    # lookup scan must still account for bank 0 exactly.
    for label,stream,mask in [
        ('transparent only',bytes(64),0),
        ('opaque bank0 after transparent',bytes(60)+bytes((0,1,2,15)),1),
        ('one bank with changing shades',bytes(range(16,32))*4,2),
        ('mixed banks and zeros',bytes((0,16,96,127,128,255,0,0))*8,0x81c2),
        ('mixed plus low opaque',bytes((0,16,96,127,128,255,0,1))*8,0x81c3)]:
        objects=bytearray(disabled);struct.pack_into('<4H',objects,0,0x2000,0,0,0)
        owners=bytearray([255]*128);owners[1]=0
        result,oam,palette,plan=apply(objects,stream+bytes(32768-len(stream)),bytes(512),owners)
        occupied,requested=struct.unpack_from('<2H',plan)
        check(result==1 and occupied==mask and requested==1,'Exact8bpp bank demand: '+label)
    # Pixel-coordinate oracle for tile clipping, independently checking every
    # pixel in a 64x64 source. Each tile has one bank, so partial tiles are exact.
    for x,y,hflip,vflip,affine in [(-32,-8,0,0,0),(-32,-8,1,0,0),(-32,-8,0,1,0),(-32,-8,1,1,0),
                                 (240,0,0,0,0),(239,159,0,0,0),(-1,159,1,1,0),(0,128,0,0,0),
                                 (0,-65,0,0,0),(240,0,0,0,1),(-32,-8,0,0,1),
                                 (240,0,0,0,2),(-32,-8,1,1,2),
                                 *[(0,y,0,flip,0) for y in (-64,-32,-8,0,128,152,159,160) for flip in (0,1)]]:
        objects=bytearray(disabled)
        # Mode 1 is affine, mode 2 mosaic: both require conservative full scan.
        attr0=0x2000|(y&255)|(0x100 if affine==1 else 0x1000 if affine==2 else 0)
        attr1=0xc000|(x&511)|(hflip<<12)|(vflip<<13)
        struct.pack_into('<4H',objects,0,attr0,attr1,0,0)
        owners=bytearray([255]*128);owners[1]=0
        pixels=b''.join(bytes([16*((tile//8+tile%8)%8+1)])*64 for tile in range(64))
        occupied=0
        for sy in range(64):
            for sx in range(64):
                dx=x+(63-sx if hflip else sx);dy=y+(63-sy if vflip else sy)
                if affine or (0<=dx<240 and 0<=dy<160):occupied|=1<<((sy//8+sx//8)%8+1)
        result,oam,palette,plan=apply(objects,pixels+bytes(32768-len(pixels)),bytes(512),owners)
        check(result==1 and struct.unpack_from('<H',plan)[0]==occupied,'Visible8bpp tile demand '+str((x,y,hflip,vflip,affine)))
        for bank in range(1,10):
            a.put(O,objects);a.put(P,bytes(512));a.put(R,struct.pack('<HH10BH',0,1,bank,*([255]*9),0))
            result=a.call(symbols['ffta_art_palette_reapply'],F)
            check(result==int(not occupied&(1<<bank)),'Preferred row spans match independent visible-pixel oracle '+str((x,y,hflip,vflip,affine,bank)))
    # A single occupied tile row makes vertical clipping observable even when
    # every full-width row would otherwise contain the same set of banks.
    for y in (-64,-32,-8,0,128,152,159,160):
        for flip in (0,1):
            objects=bytearray(disabled);struct.pack_into('<4H',objects,0,0x2000|(y&255),0xc000|(flip<<13),0,0)
            owners=bytearray([255]*128);owners[1]=0
            a.put(T,owners);a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,1))
            for row in range(8):
                pixels=bytearray(32768);pixels[row*512:row*512+64]=bytes([48])*64
                visible=any(0<=y+(63-sy if flip else sy)<160 for sy in range(row*8,row*8+8))
                a.put(O,objects);a.put(V,pixels);a.put(P,bytes(512));a.put(R,struct.pack('<HH10BH',0,1,3,*([255]*9),0))
                result=a.call(symbols['ffta_art_palette_reapply'],F,stack=0x03007800)
                check(result==int(not visible),'Contiguous visible rows retain exact single-row conflict '+str((y,flip,row)))
                if visible:check(a.read(O,1024)==objects and a.read(P,512)==bytes(512),'Row collision refuses without writes '+str((y,flip,row)))
    # Same OAM key, isolated changed bytes including cache boundaries and tiles
    # beyond the cache. Every changed color must be observed on the next call.
    objects=bytearray(disabled);struct.pack_into('<4H',objects,0,0x2000,0xc000,0,0)
    owners=bytearray([255]*128);owners[1]=0
    for position in (0,3,63,64,511,1023,2047,2048,4095):
        pixels=bytearray(bytes([16])*4096+bytes(32768-4096));pixels[position]=96
        result,oam,palette,plan=apply(objects,pixels,bytes(512),owners)
        check(result==1 and struct.unpack_from('<H',plan)[0]==66,'Exact single-byte cache invalidation at '+str(position))
    # Validate the preferred-bank pixel test through compiled ARM/Thumb code:
    # every nonzero proposed bank, every pixel bank and all four byte lanes.
    objects=bytearray(disabled);struct.pack_into('<4H',objects,0,0x2000,0,0,0)
    owners=bytearray([255]*128);owners[1]=0
    a.put(T,owners);a.put(C,custom);a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,1))
    for bank in range(1,16):
        preferred=struct.pack('<HH10BH',0,1,bank,*([255]*9),0)
        for pixelbank in range(16):
            for lane in range(64):
                pixels=bytearray(32768);pixels[lane]=pixelbank*16+(15 if lane&1 else 0)
                a.put(O,objects);a.put(V,pixels);a.put(P,bytes(512));a.put(R,preferred)
                result=a.call(symbols['ffta_art_palette_reapply'],F)
                label=str((bank,pixelbank,lane))
                if pixelbank==bank:
                    check(result==0 and a.read(O,1024)==objects and a.read(P,512)==bytes(512),'Reject exact8bpp preferred-bank collision without writes '+label)
                else:
                    expected=bytearray(objects);struct.pack_into('<H',expected,12,bank<<12)
                    palette=bytearray(512);palette[bank*32:bank*32+32]=custom
                    check(result==1 and a.read(O,1024)==expected and a.read(P,512)==palette,'Accept exact conflict-free preferred bank '+label)
                check(a.read(R,16)==preferred,'Preferred path leaves last-full-plan diagnostics unchanged '+label)
    # The grouped less-than16 byte predicate must ignore every possible low
    # nibble, including inter-byte borrows and 0x80/0xff boundaries.
    for bank in range(1,16):
        for value in range(256):
            for lane in range(4):
                pixels=bytearray(32768);pixels[lane]=value
                a.put(O,objects);a.put(V,pixels);a.put(P,bytes(512));a.put(R,struct.pack('<HH10BH',0,1,bank,*([255]*9),0))
                result=a.call(symbols['ffta_art_palette_reapply'],F,stack=0x03007800)
                check(result==int(value//16!=bank),'Relocated grouped byte predicate all values/lanes '+str((bank,value,lane)))
    # Disabled tail trimming must still find the final enabled entry after a
    # large hole; stale tags on disabled entries must never affect allocation.
    for last in (2,63,126,127):
        sparse=bytearray(disabled);struct.pack_into('<4H',sparse,last*8,0,0,3<<12,0)
        owners=bytearray([255]*128);owners[1]=0;owners[126 if last!=126 else 125]=9
        a.put(T,owners);a.put(O,sparse);a.put(V,bytes(32768));a.put(P,bytes(512));a.put(R,struct.pack('<HH10BH',0,1,3,*([255]*9),0))
        check(a.call(symbols['ffta_art_palette_reapply'],F)==0 and a.read(O,1024)==sparse and a.read(P,512)==bytes(512),'Late enabled conflict survives disabled holes '+str(last))
        struct.pack_into('<H',sparse,last*8+4,4<<12);a.put(O,sparse)
        check(a.call(symbols['ffta_art_palette_reapply'],F)==1,'Disabled stale owner is ignored with last object '+str(last))
    for last in (2,63,120,121,122,123,124,125,126,127):
        sparse=bytearray(struct.pack('<4H',0xa8,0xf8,0,0)*128)
        struct.pack_into('<4H',sparse,8,0,0x8000,0,0)
        owners=bytearray([255]*128);owners[1]=0;a.put(T,owners)
        for attr0,attr1,attr2,expected in [(0xa8,0xf8,0,1),(0xa8,0xf8,3<<12,0),(0x100,0xf8,3<<12,0),(0,0,3<<12,0)]:
            struct.pack_into('<4H',sparse,last*8,attr0,attr1,attr2,0)
            a.put(O,sparse);a.put(V,bytes(32768));a.put(P,bytes(512));a.put(R,struct.pack('<HH10BH',0,1,3,*([255]*9),0))
            check(a.call(symbols['ffta_art_palette_reapply'],F)==expected,'Native sentinel tail requires exact geometry/bank at '+str((last,attr0,attr1,attr2)))
    # Grouped marker checks must ignore affine matrix storage, but must not
    # skip an owned entry or a palette conflict in any of the four lanes.
    for owner_offset in (0,1):
        for last in range(124,128):
            sparse=bytearray(struct.pack('<4H',0xa8,0xf8,0,0xffff)*128)
            struct.pack_into('<4H',sparse,8,0,0x8000,0,0xffff)
            owners=bytearray([255]*128);owners[1]=0
            a.put(T+owner_offset,owners);a.put(F,struct.pack('<8I',O,V,T+owner_offset,P,C,R,1,1))
            a.put(O,sparse);a.put(V,bytes(32768));a.put(P,bytes(512));a.put(R,struct.pack('<HH10BH',0,1,3,*([255]*9),0))
            check(a.call(symbols['ffta_art_palette_reapply'],F)==1,'Affine storage ignored with aligned or unaligned owner tags '+str((owner_offset,last)))
            owners[last]=9;a.put(T+owner_offset,owners);a.put(O,sparse);a.put(P,bytes(512))
            check(a.call(symbols['ffta_art_palette_reapply'],F)==0 and a.read(O,1024)==sparse and a.read(P,512)==bytes(512),'Owned marker cannot disappear in grouped tail '+str((owner_offset,last)))
            owners[last]=255;a.put(T+owner_offset,owners);struct.pack_into('<H',sparse,last*8+4,3<<12);a.put(O,sparse)
            check(a.call(symbols['ffta_art_palette_reapply'],F)==0 and a.read(O,1024)==sparse,'Each grouped lane retains its palette conflict '+str((owner_offset,last)))
    a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,1))
    owners=bytearray([255]*128);owners[1]=0;a.put(T,owners)
    # A noncustom4bpp sprite colliding with the prior assignment also refuses.
    struct.pack_into('<4H',objects,16,0,0,3<<12,0);a.put(O,objects);a.put(V,bytes(32768));a.put(P,bytes(512));a.put(R,struct.pack('<HH10BH',0,1,3,*([255]*9),0))
    check(a.call(symbols['ffta_art_palette_reapply'],F)==0 and a.read(O,1024)==objects and a.read(P,512)==bytes(512),'Reject native4bpp collision without writes')
    # Hold the prior plan/cache across mutations. The optimized live path must
    # detect a newly occupied bank in every compared word/byte boundary and
    # produce the same new allocation as the independent uncached planner.
    objects=bytearray(disabled);struct.pack_into('<4H',objects,0,0x2000,0xc000,0,0)
    struct.pack_into('<4H',objects,16,0,0,0,0)
    owners=bytearray([255]*128);owners[1]=0
    a.put(T,owners);a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,1))
    original_pixels=bytes([16])*4096+bytes(32768-4096)
    for position in (0,1,2,3,15,16,31,32,63,64,255,256,511,1023,2047,2048,4095):
        a.put(O,objects);a.put(V,original_pixels);a.put(P,bytes(512));a.put(R,b'\xa5'*16)
        check(a.call(symbols['ffta_art_palette_apply_cached'],F,CACHE)==1,'Prepare authenticated pre-mutation cached demand')
        prior=a.read(R,16);check(prior[4]==2,'Mutation control initially allocates bank2')
        changed=bytearray(original_pixels);changed[position]=32
        a.put(O,objects);a.put(P,bytes(512));a.put(V,changed)
        result=a.call(symbols['ffta_art_palette_apply'],F)
        expected=result,a.read(O,1024),a.read(P,512),a.read(R,16)
        a.put(O,objects);a.put(P,bytes(512));a.put(R,prior)
        result=a.call(symbols['ffta_art_palette_live_apply'],F,CACHE,0x02016000)
        check((result,a.read(O,1024),a.read(P,512),a.read(R,16))==expected,'Current-frame reuse detects changed pixel and reallocates exactly at '+str(position))
    # The exact same scan can execute from scoped IWRAM stack storage. Guard
    # the resident-code edge, verify the actual execution addresses, and prove
    # an EWRAM caller stack takes the unchanged ROM fallback without RAM writes.
    objects=bytearray(disabled);struct.pack_into('<4H',objects,0,0x2000,0,0,0)
    owners=bytearray([255]*128);owners[1]=0
    a.put(T,owners);a.put(O,objects);a.put(V,bytes(32768));a.put(P,bytes(512));a.put(R,struct.pack('<HH10BH',0,1,3,*([255]*9),0))
    a.put(0x03006d00,b'\x7b'*0x68)
    executed=set()
    hook=a.u.hook_add(UC_HOOK_CODE,lambda u,pc,size,user:executed.add(pc),begin=0x03006d68,end=0x03007fff)
    check(a.call(symbols['ffta_art_palette_reapply'],F,stack=0x03007800)==1 and bool(executed),'Exact scan executes from bounded IWRAM stack')
    check(a.read(0x03006d00,0x68)==b'\x7b'*0x68,'Resident IWRAM code fence unchanged')
    saved=a.read(0x03006d68,0x1298);executed.clear();a.put(O,objects)
    check(a.call(symbols['ffta_art_palette_reapply'],F,stack=0x02018000)==1 and not executed,'Non-IWRAM stack uses ROM scan fallback')
    check(a.read(0x03006d68,0x1298)==saved,'ROM fallback leaves IWRAM untouched')
    executed.clear();a.put(O,objects)
    check(a.call(symbols['ffta_art_palette_reapply'],F,stack=0x03007000)==1 and not executed,'Deep IWRAM stack keeps interrupt margin and uses ROM fallback')
    check(a.read(0x03006d00,0x68)==b'\x7b'*0x68,'Deep-stack fallback preserves resident native code fence')
    a.u.hook_del(hook)
    if args.rect_conflict:
        descriptor=0x02017000
        a.put(descriptor,struct.pack('<5I',V,64,8,512,0x30303030))
        leaf=a.read(symbols['ffta_art_span_has_bank'],160)
        for stack in (0x03007040,0x03007044,0x03007048,0x02018000):
            for position,wanted in ((None,0),(255,1),(256,0),(3839,1),(4095,0)):
                pixels=bytearray(32768)
                if position is not None:pixels[position]=0x3f
                a.put(V,pixels);resident=a.read(0x03000000,0x6f68);executed=[]
                hook=a.u.hook_add(UC_HOOK_CODE,lambda u,pc,size,user:executed.append(pc),begin=0x03006d68,end=0x03007fff)
                actual=a.call(symbols['__ffta_art_rect_has_bank_fast_from_thumb'],descriptor,stack=stack)
                a.u.hook_del(hook)
                check(actual==wanted,'Rectangle scans exact current rows and excludes stride gaps '+str((stack,position)))
                fast=stack in (0x03007044,0x03007048)
                check(bool(executed)==fast,'Rectangle actual below/at/above stack cutoff and external fallback '+str((stack,position)))
                check(a.read(0x03000000,0x6f68)==resident,'Rectangle preserves native resident region and complete512-byte interrupt reserve')
                if fast:check(a.read(stack-32-160,160)==leaf,'Rectangle executes exact original160-byte scan leaf')
    failures=[]
    full=bytearray(disabled)
    for i in range(16):struct.pack_into('<4H',full,i*8,0,0, i<<12,0)
    struct.pack_into('<4H',full,127*8,0,0x8000,0,0);owners=bytearray([255]*128);owners[127]=0
    failures.append(('all16banks occupied',full,bytes(32768),owners,1))
    eight=bytearray(disabled);struct.pack_into('<4H',eight,0,0x2000,0xc000,0,0);owners=bytearray([255]*128);owners[1]=0
    pixels=bytes(range(256))*128
    failures.append(('8bpp consumes all16banks',eight,pixels,owners,1))
    over=bytearray(eight);struct.pack_into('<H',over,4,1022);failures.append(('8bpp footprint outside OBJ memory',over,pixels,owners,1))
    invalid=bytearray(disabled);struct.pack_into('<H',invalid,0,0x2000);failures.append(('custom8bpp unsupported',invalid,bytes(32768),tags,1))
    failures.append(('2D mapping unsupported',disabled,bytes(32768),tags,0))
    invalid=bytearray(disabled);struct.pack_into('<H',invalid,0,0xc000);failures.append(('invalid shape',invalid,bytes(32768),tags,1))
    badtags=bytearray(tags);badtags[0]=10;failures.append(('unknown custom owner',disabled,bytes(32768),badtags,1))
    for label,oam,obj,owners,mapping in failures:
        palette=bytes(range(256))*2;r,after,colors,plan=apply(oam,obj,palette,owners,two,mapping)
        check(r==0 and after==oam and colors==palette and plan==b'\xa5'*16,'Fail closed without writes: '+label)
    result=dict(status='passed',rectConflict=args.rect_conflict,joinedRows=args.joined_rows,burstScan=args.burst_scan,blockScan=args.block_scan,checks=checks,compiledBytes=len(code),compiledSha256=sha(code),fastOamPlan=args.fast_oam_plan,armOamScan=args.arm_oam_scan,sources={str(p):sha((ROOT/p).read_bytes()) for p in ('src/engine/art-palette-plan.c', 'src/engine/art-palette-scan.s','src/engine/art-palette-plan.h')+ (('src/engine/art-palette-bank-scan.s',) if args.fast_bank_scan else ())+(('src/engine/art-oam-demands.s',) if args.arm_oam_scan else ())},
        retainedReport=str(source),retainedReportSha256=sha(source.read_bytes()),records=records,
        scope='Compiled ARM planner/application on50 authenticated menu frames, complete OAM and palette preservation outside owned changes,8bpp palette footprint accounting,2owners and7 fail-closed cases. Caller owner authentication, native timing/hook, restoration, battle and color-mode lifetimes are not implemented by this primitive.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as e:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(e),checks=checks,records=records),indent=2)+'\n');print(str(out));raise
