"""Private approved miniature import with explicit native bright/dim palettes.

The menu-only upload/draw veneers do not change battle rendering. They bind
the exact native54..63 image uploads to six menu palette banks. Original54
images, native0..8/12 palette banks, original descriptors and saves stay intact.
This builder is not native/UI/timing acceptance.
"""
import copy,hashlib,json,struct,subprocess,datetime
from pathlib import Path
from PIL import Image,ImageDraw
from native_art import ROOT,sha,pack_tiles,tile_image
from native_miniatures import decode,encode,LITERALS

def build():
    parent_path=ROOT/'build/art/reviewed-integration/portrait-candidate.json'
    parent=json.loads(parent_path.read_text());original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    live=parent['components']['livePalette'];actions=parent['components']['reviewedActions']
    assert live['ramReservation']==[0x0203c000,0x0203f000]
    assert 0x0203c000+live['transientStateBytes']<=0x0203ed00
    assert 0x0203ee08<=live['partyHeapRoot']<0x0203f000
    assert not actions['missing'] and not actions['provisional'] and not actions['draft']
    classes=copy.deepcopy(parent['components']['classes']);old_container=classes['container']
    assert int.from_bytes(original[old_container+2:old_container+4],'big')==64
    images=[decode(original,old_container,i) for i in range(64)]
    groups=live['paletteGroups']['ownerMap'];assert set(groups)=={0,1,2}
    palette_at=live['symbols']['ffta_art_custom_colors']-0x08000000
    normal=[list(struct.unpack_from('<16H',original,palette_at+32*g)) for g in range(3)]
    dim=[[sum(((word>>s)&31)+1>>1<<s for s in (0,5,10)) for word in colors] for colors in normal]
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
    work=ROOT/'build/art/reviewed-integration/menu-miniatures'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    work.mkdir(parents=True);jobs=[]
    sheet=Image.new('RGBA',(960,720),(228,226,220,255));draw=ImageDraw.Draw(sheet)
    for n,unit in enumerate(catalog['units']):
        prior=next(j for j in classes['jobs'] if j['job']==unit['job']);mini=prior['miniature']
        assert mini['index']==54+n
        source=ROOT/'build/art/approved-class-animation-2026-09-19'/unit['slug']/'front-neutral.png'
        im=Image.open(source).convert('RGBA');assert im.size==(32,32)
        source_colors=normal[groups[n]]
        donor=tile_image(images[mini['donor']],[0]*48,32)
        offset=donor.getbbox()[3]-im.getbbox()[3];assert 0<=offset<=8
        indexed=Image.new('P',(32,40));rgb=[((w>>s)&31)*255//31 for w in source_colors for s in (0,5,10)]
        indexed.putpalette(rgb+[0]*(768-48));indexed.info['transparency']=0
        for y in range(32):
            for x in range(32):
                pixel=im.getpixel((x,y))
                if pixel[3]<128:continue
                w=sum(round(pixel[k]*31/255)<<(k*5) for k in range(3))
                i=min(range(1,16),key=lambda c:sum((((w>>s)&31)-((source_colors[c]>>s)&31))**2 for s in (0,5,10)))
                indexed.putpixel((x,y+offset),i)
        raw=pack_tiles(indexed,20);images[54+n]=raw;target=work/(unit['slug']+'.png');indexed.save(target,bits=4)
        jobs.append(dict(job=unit['job'],slug=unit['slug'],index=54+n,group=groups[n],offsetY=offset,
            source=str(source),sourceSha256=sha(source.read_bytes()),nativeImage=str(target),tileSha256=sha(raw),
            normalBank=9+groups[n],dimBank=13+groups[n]))
        cx=n%5*192;cy=n//5*360;draw.text((cx+2,cy+3),unit['label'],fill='black')
        sheet.alpha_composite(im.resize((128,128),Image.Resampling.NEAREST),(cx+32,cy+20))
        for col,colors in enumerate((normal[groups[n]],dim[groups[n]])):
            part=tile_image(raw,[((w>>s)&31)*255//31 for w in colors for s in (0,5,10)],32)
            sheet.alpha_composite(part.convert('RGBA').resize((96,120),Image.Resampling.NEAREST),(cx+96*col,cy+168))
        draw.text((cx+4,cy+300),'Bright / dim conversion',fill='black')
    sheet.save(work/'review.png')
    start=(actions['used'][1]+255)&~255;container=encode(images);code_at=(start+len(container)+255)&~255
    assert original[start:actions['reservation'][1]]==b'\xff'*(actions['reservation'][1]-start)
    table=struct.unpack_from('<8I',original,0x393e78);objects=[]
    for mode in range(4):
        words=list(struct.unpack_from('<256H',original,table[2*mode+1]-0x08000000))
        for g in range(3):
            words[(9+g)*16:(10+g)*16]=normal[g]
            words[(13+g)*16:(14+g)*16]=dim[g]
        objects.append(words)
    config=work/'config.c'
    config.write_text('#include <stdint.h>\nconst uint32_t ffta_reviewed_menu_container='+hex(start+0x08000000)+'u;\n'+
        'const uint8_t ffta_reviewed_menu_groups[10]={'+','.join(map(str,groups))+'};\n'+
        'const uint16_t ffta_reviewed_menu_obj[4][256]={'+','.join('{'+','.join(map(str,ws))+'}' for ws in objects)+'};\n'+
        'const void *const ffta_reviewed_menu_palette_table[8]={'+','.join(f'(const void *){hex(table[2*m])}u,ffta_reviewed_menu_obj[{m}]' for m in range(4))+'};\n')
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=work/'menu.elf';binary=work/'menu.bin'
    sources=['src/engine/reviewed-menu-miniatures.c','src/engine/reviewed-menu-miniatures.s']
    command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror',
        '-Wl,-Ttext='+hex(code_at+0x08000000),'-Wl,-e,ffta_reviewed_menu_init_entry',*sources,str(config),'-o',str(elf)]
    run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(work/'compile.log').write_text(run.stdout+run.stderr);run.check_returncode()
    nm=subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True)
    symbols={name:int(address,16) for address,kind,name in (line.split() for line in nm.splitlines() if len(line.split())==3)}
    assert not any(line.split()[1] in ('b','B','d','D') and line.split()[2]!='_stack'
                   for line in nm.splitlines() if len(line.split())==3),'No unreserved mutable globals'
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
    code=binary.read_bytes();end=code_at+len(code);assert end<=actions['reservation'][1]
    rom=bytearray(original);patches=[]
    def patch(at,data,kind):
        old=original[at:at+len(data)];rom[at:at+len(data)]=data
        patches.append(dict(offset=at,bytes=len(data),beforeSha256=sha(old),sha256=sha(data),kind=kind))
    patch(start,container,'64 miniature archive; original54 byte-exact')
    patch(code_at,code,'Menu upload ownership and native bright/dim palette module')
    for literal in LITERALS:
        assert struct.unpack_from('<I',original,literal)[0]==old_container+0x08000000
        patch(literal,struct.pack('<I',start+0x08000000),'Miniature archive pointer')
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    for at,size,name in [(0x89660,8,'init'),(0x87b90,12,'upload_a'),(0x87c28,12,'upload_b'),(0x87d58,12,'upload_c'),(0x88060,8,'draw')]:
        assert original[at:at+size]==clean[at:at+size],('Native menu site already changed',hex(at))
        jump=bytes.fromhex('004b1847')+struct.pack('<I',symbols['ffta_reviewed_menu_'+name+'_entry']|1)+bytes.fromhex('c046')*((size-8)//2)
        patch(at,jump,'Exact native menu '+name+' continuation')
    allowed={i for p in patches for i in range(p['offset'],p['offset']+p['bytes'])}
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();folder=ROOT/'build/art/reviewed-menu-miniatures'/digest;folder.mkdir(parents=True,exist_ok=True)
    def immutable(path,data):
        if path.exists():assert path.read_bytes()==data
        else:path.write_bytes(data)
    path=folder/'FFTA_Reviewed_Menu_Miniatures.gba';immutable(path,rom)
    for j in jobs:
        original_job=next(v for v in classes['jobs'] if v['job']==j['job'])
        original_job['miniature'].update(offsetY=j['offsetY'],sha256=j['tileSha256'],paletteReference=symbols['ffta_reviewed_menu_obj']-0x08000000+j['normalBank']*32)
    classes['container']=start
    proof=dict(parentManifest=str(folder/'parent-manifest.json'),parentManifestSha256=sha(parent_path.read_bytes()),
        patches=patches,symbols=symbols,jobs=jobs,container=start,priorContainer=old_container,
        ramReservation=[0x0203ed00,0x0203ee08],used=[start,end],work=str(work),
        sources={p:sha((ROOT/p).read_bytes()) for p in sources+[str(config.relative_to(ROOT)),'scripts/build-reviewed-menu-miniatures.py']},
        compilerCommand=command,productionAccepted=False,scope=__doc__)
    result=copy.deepcopy(parent);result.update(path=str(path),romSha1=digest,romSha256=sha(rom),source=parent['path'],baseRomSha1=parent['romSha1'])
    result['components']['classes']=classes;result['components']['reviewedMenuMiniatures']=proof
    archive=folder/'manifest.json';result['archivedManifest']=str(archive)
    data=(json.dumps(result,indent=2)+'\n').encode();immutable(archive,data)
    immutable(folder/'parent-manifest.json',parent_path.read_bytes())
    (ROOT/'build/art/reviewed-integration/menu-candidate.json').write_bytes(data)
    print(json.dumps(dict(romSha1=digest,used=[start,end],work=str(work))))

if __name__=='__main__':build()
