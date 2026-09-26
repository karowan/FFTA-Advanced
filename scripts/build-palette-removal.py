"""Remove the retired art palette engine's RAM reservation and last live hook.

Bounded patch on the help-pages candidate. The live palette engine was switched
off when the artwork moved to native shared palettes (29 palette/render/fade
hooks restored, custom ownership mask zero), but its 12 KiB EWRAM reservation
0x0203C000..0x0203F000 was kept by lowering the native heap end from
0x0203F000, and one hook still initialized palette state there. Without those
12 KiB the pre-battle unit Info screen (R during deployment) cannot allocate its
10 KiB display buffer: it draws garbage and freeing the NULL buffer corrupts the
heap (black screen).

This stage:
- restores the heap end literals to 0x0203F000; the heap-setup hook at
  0x11D0714 keeps its endpoint check but its one call now resets only the
  party-heap record instead of the palette engine (which also did that);
- raises the matching limits in the still-used art heap helpers (shared party
  heap and low-address battle workspace placement) from 0x0203C000 to
  0x0203F000, and moves their 16-byte party-heap record from 0x0203EFF0 (now
  heap) to the unused 0x0203F200;
- retires the compact read-only Status context: pre-battle unit Info reaches
  that entry too and its Equip Items list (up to 461 owned items) overflowed
  the compact 376-entry area into the AP/status/job-copy tail. Every party
  context now uses the full list tail again (native entries 70688/71138/711CC
  restored), and the party scene's display buffer shrinks from 0x2800 to
  0x1E00 bytes (measured peak 5,920 with every item owned) so the full
  context fits the deployment heap;
- restores the native size (0x4504) of an AI table workspace that the
  upstream inventory hack's literal substitution had raised to 0x9C08;
- fills every palette-engine function that no live code can reach with 0xFF,
  within the compiled code segment only (the artwork data after it stays).
Party list ownership, Auto-Potion, status iteration and all artwork data are
unchanged.
"""
import datetime, hashlib, json, re, struct, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/palette-removal'
OLD_END,NEW_END=0x0203c000,0x0203f000
OLD_ROOT,NEW_ROOT=0x0203eff0,0x0203f200   # unused; below the 0x0203F220 diagnostics window
ART=(0x1f90000,0x1fd0000)   # retired live-palette reservation (code segment + artwork data)
CODE_END=None               # end of its compiled code, from the manifest segments
AI_WORKSPACE=(0xbdb14,0xbdbc0)   # native AI table copy: allocation and copy size
HEAP_END=(0x1103dc4,0x1103de0,0x1103dfc)
OWNER_RESET=0x11d0714   # integrated heap-setup site hooked to ffta_art_clear_endpoint
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
def sha(b):return hashlib.sha256(b).hexdigest()

def bl_target(rom,a):
    h,l=struct.unpack_from('<HH',rom,a-0x08000000)
    if h>>11!=0b11110 or l>>11!=0b11111:return None
    off=((h&0x7ff)<<12)|((l&0x7ff)<<1)
    return a+4+(off-0x800000 if off&0x400000 else off)

def bl(a,target):
    off=target-(a+4);assert -0x400000<=off<0x400000 and not off&1
    off&=0x7fffff
    return struct.pack('<HH',0xf000|(off>>12),0xf800|((off>>1)&0x7ff))

def functions(rom,symbols):
    """Functions of the compiled code segment: start -> end (next symbol or
    the end of compiled code; artwork data after it is never included)."""
    end=CODE_END or ART[1]
    starts=sorted({v&~1 for v in symbols.values() if ART[0]<=(v&~1)-0x08000000<end})
    used_end=0x08000000+end
    return {s:(starts[i+1] if i+1<len(starts) else used_end) for i,s in enumerate(starts)}

def references(rom,start,end):
    """Direct BL targets and literal words inside [start,end).

    Thumb BL and PC-relative literals, plus ARM B/BL words (libgcc and the
    linker's Thumb-to-ARM veneers). Misreading data only keeps more code."""
    out=set()
    for w in range(start+(-start&3),end-3,4):
        word=u32(rom,w-0x08000000)
        if word>>25&7==0b101 and word>>28==0xe:
            off=(word&0xffffff)<<2
            if off&0x2000000:off-=0x4000000
            out.add(w+8+off)
    a=start
    while a<end-2:
        h=struct.unpack_from('<H',rom,a-0x08000000)[0]
        if h>>11==0b11110 and a+4<=end:
            l=struct.unpack_from('<H',rom,a+2-0x08000000)[0]
            if l>>11 in (0b11111,0b11101):
                off=((h&0x7ff)<<12)|((l&0x7ff)<<1)
                if off&0x400000:off-=0x800000
                out.add((a+4+off)&~1);a+=4;continue
        if h>>11==0b01001:   # ldr rX,[pc,#imm]
            lit=((a+4)&~3)+(h&0xff)*4
            if lit+4<=0x08000000+len(rom):out.add(u32(rom,lit-0x08000000)&~1)
        a+=2
    return out

def main():
    parent=Path(json.loads((ROOT/'build/expansion/help-pages/current.json').read_text())['manifest'])
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['romSha1']
    comp=meta['components'];live=comp['livePalette'];symbols=live['symbols']
    global CODE_END
    code=[g for g in live['segments'] if g['kind']=='compiled-palette-hooks'];assert len(code)==1 and code[0]['offset']==ART[0]
    CODE_END=code[0]['offset']+code[0]['bytes']
    assert live['ramReservation']==[OLD_END,NEW_END] and live['heapEnd']==OLD_END
    assert live['reservation']==[0x1f90000,0x1fd0000]
    # Pre-art input of the art chain supplies the integrated bytes to restore.
    base=Path(comp['classResources']['source']).read_bytes()
    assert hashlib.sha1(base).hexdigest()==comp['classResources']['baseRomSha1']
    rom=bytearray(original);patches=[]
    def put(at,old,new,label):
        assert rom[at:at+len(old)]==old,(label,hex(at),rom[at:at+len(old)].hex())
        rom[at:at+len(new)]=new;patches.append(dict(offset=at,before=old.hex(),after=new.hex(),label=label))
    for at in HEAP_END:
        assert base[at:at+4]==struct.pack('<I',NEW_END)
        put(at,struct.pack('<I',OLD_END),struct.pack('<I',NEW_END),'native heap end restored')
    # Heap-setup hook: retarget its single BL from the palette-engine reset to
    # the party-heap record reset (the palette reset used to call it).
    assert u32(original,OWNER_RESET+4)&~1==symbols['ffta_art_clear_endpoint']&~1
    endpoint=symbols['ffta_art_clear_endpoint']&~1
    call=next(a for a in range(endpoint,endpoint+0x30,2) if bl_target(original,a)==symbols['ffta_art_heap_reset']&~1)
    put(call-0x08000000,original[call-0x08000000:call-0x08000000+4],bl(call,symbols['ffta_art_party_heap_reset']&~1),
        'heap setup resets only the party-heap record')
    # The upstream inventory hack rewrote every word equal to its shop offset
    # 0x4504, including the size of a native AI table copy at 080BDAFC
    # (allocate, then copy 0x4504 bytes). Restore the native size.
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    for at in AI_WORKSPACE:
        assert u32(clean,at)==0x4504
        put(at,struct.pack('<I',0x9c08),struct.pack('<I',0x4504),'native AI table workspace size restored')
    # Retire the compact read-only Status mode (native entries restored).
    for at,size in ((0x70688,12),(0x71138,8),(0x711cc,8)):
        put(at,original[at:at+size],base[at:at+size],'native party constructor entry restored (compact Status retired)')
    assert u32(rom,0x711f8)==0x9980 and u32(rom,0x71228)==0x7280   # full context, list tail in context
    put(0x71182,bytes.fromhex('a021'),bytes.fromhex('7821'),'party display buffer 0x2800 -> 0x1E00')
    # Still-used art heap helpers: literal pools located through their symbols.
    fn=functions(original,symbols)
    def literals(name,value):
        s=symbols[name]&~1;e=fn[s]
        return [a-0x08000000 for a in range(s,e,4) if u32(original,a-0x08000000)==value]
    root=[a for n in ('ffta_art_party_heap_reset','ffta_art_party_parent_allocate','ffta_art_party_heap_bypass',
                      'ffta_art_party_parent_free','ffta_art_party_list_offset') for a in literals(n,OLD_ROOT)]
    assert len(root)==5,root
    for at in root:put(at,struct.pack('<I',OLD_ROOT),struct.pack('<I',NEW_ROOT),'party-heap record moved out of the heap')
    for name,pairs in (('ffta_art_party_parent_allocate',((0x3bff0,0x3eff0),(OLD_END,NEW_END))),
                       ('ffta_art_workspace_find',((0x3bfe4,0x3efe4),(OLD_END,NEW_END)))):
        for old,new in pairs:
            found=literals(name,old);assert len(found)==1,(name,hex(old),found)
            put(found[0],struct.pack('<I',old),struct.pack('<I',new),name+' heap limit')
    # Reachability: every art function reached from live code outside the
    # reservation (hook literals, BL) or transitively from such functions.
    starts=set(fn)
    live_roots=set()
    for at in range(0,len(rom)-3,4):
        if ART[0]<=at<ART[1]:continue
        v=u32(rom,at)
        if (v&~1) in starts and v&1:live_roots.add(v&~1)
    # Direct BL into the reservation from any nearby code (conservative: data
    # misread as BL can only keep more code).
    for region in ((0x1e00000,ART[0]),(ART[1],0x2000000)):
        for t in references(rom,0x08000000+region[0],0x08000000+region[1]):
            owner=max((s for s in starts if s<=t),default=None)
            if owner is not None and t<fn[owner]:live_roots.add(owner)
    reach=set();todo=list(live_roots)
    while todo:
        f=todo.pop()
        if f in reach:continue
        reach.add(f)
        for t in references(rom,f,fn[f]):
            owner=max((s for s in starts if s<=t),default=None)
            if owner is not None and t<fn[owner] and owner not in reach:todo.append(owner)
    names={}
    for k,v in symbols.items():names.setdefault(v&~1,[]).append(k)
    # Linker veneers and libgcc helpers (ARM-state stubs, literal-loaded
    # targets) are tiny and palette-neutral: always keep them.
    helper=re.compile(r'aeabi|divsi3|modsi3|div0')
    reach|={f for f in starts if any(helper.search(n) for n in names[f])}
    dead=sorted(starts-reach)
    removed=[]
    for f in dead:
        a,e=f-0x08000000,fn[f]-0x08000000
        rom[a:e]=b'\xff'*(e-a);removed.append(dict(address=f,bytes=e-a,names=sorted(names[f])))
    # Nothing live may branch into, or hold a pointer to, a removed function.
    gone=set();[gone.update(range(r['address'],r['address']+r['bytes'])) for r in removed]
    for f in reach:
        bad=[t for t in references(rom,f,fn[f]) if t in gone]
        assert not bad,(hex(f),[hex(t) for t in bad])
    # Words equal to the clean game are original data and cannot address mod
    # code; mod-written words must not hold a removed function's entry.
    entries={r['address'] for r in removed}
    assert all(r['address']+r['bytes']<=0x08000000+CODE_END for r in removed),'removal stays in compiled code'
    assert rom[CODE_END:ART[1]]==original[CODE_END:ART[1]],'artwork data after the code is untouched'
    for at in range(0,len(rom)-3,4):
        if at<len(clean) and rom[at:at+4]==clean[at:at+4]:continue
        v=u32(rom,at)
        if v&1 and (v&~1) in entries:raise AssertionError(('pointer to removed code',hex(at),hex(v)))
    palette=[r for r in removed if any('palette' in n or n.startswith('ffta_art_live') for n in r['names'])]
    compact={'ffta_art_party_mark_readonly','ffta_art_party_context_allocate','ffta_art_party_list_offset',
             'ffta_art_party_readonly_entry','ffta_art_party_context_entry','ffta_art_party_list_entry',
             'ffta_art_party_call_constructor'}
    assert palette and all(n in compact or ('ffta_art_party' not in n and 'workspace' not in n) for r in removed for n in r['names'])
    out=OUT/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    target=out/'FFTA_Reviewed_All_Classes.gba';target.write_bytes(rom)
    meta.update(path=str(target),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=sha(rom))
    meta['paletteRemoval']=dict(parent=str(parent),baseSha1=hashlib.sha1(original).hexdigest(),heapEnd=NEW_END,
        partyRoot=NEW_ROOT,patches=patches,liveFunctions=sorted(reach),removedFunctions=removed,
        removedBytes=sum(r['bytes'] for r in removed))
    manifest=out/'candidate.json';manifest.write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',manifest=str(manifest),romSha1=meta['romSha1'],patches=len(patches),
        liveArtFunctions=len(reach),removedFunctions=len(removed),removedBytes=meta['paletteRemoval']['removedBytes'])))

if __name__=='__main__':main()
