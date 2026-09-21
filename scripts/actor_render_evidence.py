"""Read-only validation of retained native actor records and live tile uploads."""
import struct
from native_art import TILES,OAM,layout

def actors(rom,ram,vram,addresses=None):
    result=[]
    for p in (range(0x10000,len(ram)-72,4) if addresses is None else sorted(addresses)):
        assert 0x10000<=p<len(ram)-72 and p%4==0,'Invalid declared actor address'
        first,current=struct.unpack_from('<II',ram,p+0x34)
        count=struct.unpack_from('<H',ram,p+0xe)[0]
        if not (0x08000004<=first<0x08000000+len(rom)-4 and 1<=count<100):continue
        if not (first<=current<first+20*count and (current-first)%20==0):continue
        if struct.unpack_from('<I',rom,first-0x08000004)[0]!=count:continue
        flags,resource,mode,timer,index=struct.unpack_from('<I2x4H',ram,p)
        if not flags&1:continue
        tile,alternate,allocation=struct.unpack_from('<3H',ram,p+0x12)
        offset=struct.unpack_from('<I',ram,p+0x20)[0]
        tilecount=struct.unpack_from('<H',ram,p+0x24)[0]
        oam=struct.unpack_from('<I',ram,p+0x2c)[0]
        if not (0x08000000<=oam<0x08000000+len(rom) and 0<tilecount<=64):continue
        objects,raw=layout(rom,oam-0x08000000)
        expected=sum(o['width']*o['height']//64 for o in objects)
        source=rom[TILES+offset:TILES+offset+tilecount*32]
        destination=0x10000+tile*32
        displayed=[]
        # At a video callback the native record can already hold the next
        # frame while its dirty upload is queued for the following VBlank.
        indices={(index-1)%count}
        # Native210E4 dispatches the byte at entry+9. Only opcode1 installs
        # tiles/layout;0 is a native no-op,2..8 update controls or do nothing.
        # Follow that exact executed command chain back to its last opcode1,
        # requiring the actor's recorded source/layout as well. Do not treat
        # arbitrary tile fields inside a control entry as a new displayed pose.
        control_hold=None
        if 0<index<=count and current==first+20*min(index,count-1):
            last=index-1;cursor=last
            while cursor>=0 and rom[first-0x08000000+20*cursor+9] in (0,2,3,4,5,6,7,8):
                cursor-=1
            if cursor>=0 and cursor!=last and rom[first-0x08000000+20*cursor+9]==1:
                source_tile,source_oam=struct.unpack_from('<II',rom,first-0x08000000+20*cursor)
                if offset==source_tile and oam==0x08000000+OAM+source_oam:
                    indices={cursor}
                    control_hold=dict(graphicsEntry=cursor,throughEntry=last,
                        commands=[rom[first-0x08000000+20*k+9] for k in range(cursor+1,last+1)])
        # Native21E28 directly selects an animation phase: it writes index,
        # clears the timer and sets current=first+20*index. The manual-control
        # flag100 bypasses countdown at212C4. During this boundary the current
        # index, rather than index-1, can already be uploaded. Require both
        # recorded tile/layout sources to match that exact native entry.
        if flags&0x100 and timer==0 and index<count and current==first+20*index:
            mt,mo=struct.unpack_from('<II',rom,current-0x08000000)
            if offset==mt and oam==0x08000000+OAM+mo:indices.add(index)
        # 0x100000: native transfer budget deferred; 0x20000: upload queued.
        # Set at080211ae/080214fe and080211da/0802152e respectively.
        if flags&0x120000:indices.add((index-2)%count)
        for f in sorted(indices):
            if rom[first-0x08000000+20*f+9]!=1:continue
            t,o=struct.unpack_from('<II',rom,first-0x08000000+20*f)
            # Held-weapon streams also contain native command-only records.
            # They supply no tile/layout and cannot be a displayed-frame proof.
            # Do not skip malformed near-matches or search additional frames.
            if t==0xffff and o==0xffffffff:continue
            objs,_=layout(rom,OAM+o)
            size=sum(v['width']*v['height']//64 for v in objs)*32
            if vram[destination:destination+size]==rom[TILES+t:TILES+t+size]:displayed.append(f)
        table=struct.unpack_from('<I',rom,0x2102c)[0]-0x08000000
        descriptor=struct.unpack_from('<I',rom,table+resource*4)[0]-0x08000000
        descriptor+=(mode&~3)*6+(12 if mode&3 in (1,2) else 0)
        declared=struct.unpack_from('<I',rom,descriptor)[0]+4
        result.append(dict(address=p,resource=resource,mode=mode,timer=timer,index=index,
                           first=first,current=current,flags=flags,tile=tile,alternate=alternate,
                           allocation=allocation,tileCount=tilecount,oam=oam,objects=objects,
                           expectedTiles=expected,sourceBytes=len(source),
                           tileOffset=offset,controlHold=control_hold,
                           exactUpload=vram[destination:destination+len(source)]==source,
                           displayedFrames=displayed,declaredSequence=declared==first))
    return result

def compare(old_rom,new_rom,old_ram,new_ram,old_vram,new_vram,bg_frames):
    before=actors(old_rom,old_ram,old_vram);after=actors(new_rom,new_ram,new_vram)
    assert len(before)==len(after)==12,('Expected12 native battle actors',len(before),len(after))
    checks=[];allowed=set();pairs=[]
    def check(ok,name):
        assert ok,name
        checks.append(name)
    for old,new in zip(before,after):
        p=hex(old['address'])
        for key in ('address','mode','tile','alternate','allocation'):
            check(old[key]==new[key],p+' unchanged '+key)
        custom=old['resource']==4
        check(new['resource']==(256 if custom else old['resource']),p+' intended resource')
        if not custom:check(new['first']==old['first'],p+' original sequence unchanged')
        for label,a in [('baseline',old),('generated',new)]:
            check(a['declaredSequence'],p+'/'+label+' sequence matches ROM resource/facing descriptor')
            check(a['expectedTiles']==a['tileCount']<=a['allocation'],p+'/'+label+' OAM fits native allocation')
            check(bool(a['displayedFrames']),p+'/'+label+' VRAM equals current or queued predecessor native frame')
        # The allocator's original bounded ranges, not inferred diff extents,
        # own the graphics writes, including inactive/stale tile tails.
        allowed.update(range(0x10000+old['tile']*32,0x10000+(old['tile']+old['allocation'])*32))
        pairs.append(dict(address=p,baseline=old,generated=new))
    check(sum(a['resource']==256 for a in after)==1,'Only one custom actor')
    check(all(a==b or i<0x10000 or i in allowed for i,(a,b) in enumerate(zip(old_vram,new_vram))),'All OBJ VRAM outside original actor allocations unchanged')
    # The map's water tiles animate too. Require an exact whole-BG match to
    # an authenticated, previously captured baseline phase of this same scene.
    phase=next((name for name,data in bg_frames.items() if new_vram[:0x10000]==data),None)
    check(phase is not None,'Complete BG VRAM matches an observed original scene phase')
    return dict(checks=checks,actors=pairs,baselineBackgroundPhase=phase)

if __name__=='__main__':
    import argparse,json
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom',type=Path);parser.add_argument('capture',type=Path)
    args=parser.parse_args()
    print(json.dumps(actors(args.rom.read_bytes(),args.capture.with_suffix('.ram').read_bytes(),args.capture.with_suffix('.vram').read_bytes()),indent=2))
