"""Bounded acceptance of an exactly retained native body upload.

No arbitrary pose matches: one preceding directly verified allocation only.
Land/water changes must be one of the explicitly owned class resource pairs.
"""
def retained(a, block, old, pairs=()):
    if not old or not old['direct'] or block != old['block']:
        return None
    previous_resource, tile, allocation = old['identity']
    if (a['tile'], a['allocation']) != (tile, allocation):
        return None
    same = a['resource'] == previous_resource
    paired = frozenset((a['resource'], previous_resource)) in pairs
    if a['flags'] & 0x120000 and (same or paired):
        return 'unchanged previous verified upload' if same else 'queued land/water swap retains verified upload'
    if (same and a['index'] == 0 and a['timer'] == 0 and old['index'] > 0
            and a['first'] == old['first'] and a['exactUpload']):
        return 'single sequence rewind retains verified upload'
    return None


def pending_from_anchor(a, block, anchor, elapsed_frames, pairs=()):
    """At most16 video frames since a direct proof, never an inferred anchor.

    Native transfer budgeting can hold one original image across two8-frame
    observations. Require the complete allocation to stay exact, a pending
    transfer flag at every accepted hold, and the original allocation identity.
    Callers must discard the anchor on a failed observation or identity change.
    """
    if not 0 < elapsed_frames <= 16 or not a['flags'] & 0x120000:
        return None
    result=retained(a,block,anchor,pairs)
    return 'bounded pending upload from direct anchor' if result else None


def completed_pending_facing(rom,a,block,anchor,elapsed_frames):
    """An already decoded native upload completes during a facing change.

    Only the exact command recorded at a directly verified preceding sample is
    allowed, within one eight-frame observation interval. Never search poses.
    """
    import struct
    from native_art import TILES,OAM,layout
    if not anchor or not anchor['direct'] or not 0<elapsed_frames<=8:return None
    old=anchor.get('actor')
    if not old or not old['flags']&0x120000 or not a['flags']&0x120000:return None
    if not old['declaredSequence'] or not a['declaredSequence']:return None
    if (a['resource'],a['tile'],a['allocation'])!=anchor['identity']:return None
    if a['index']!=1 or a['current']!=a['first']+20:return None
    new_sequence=(old['mode']&~3)!=(a['mode']&~3)
    rewind=old['first']==a['first']
    if rewind and (old['mode']!=a['mode'] or old['index']<=1):return None
    if new_sequence or rewind:
        # A native action can return to idle before its final queued upload
        # reaches VRAM. Authenticate both exact commands; this is not a search
        # for a plausible frame in another animation.
        entry=a['first']-0x08000000
        source,shape=struct.unpack_from('<II',rom,entry)
        if rom[entry+9]!=1 or a['timer']!=rom[entry+8]:return None
        if a.get('tileOffset')!=source or a['oam']!=shape+OAM+0x08000000:return None
    count=struct.unpack_from('<I',rom,old['first']-0x08000004)[0]
    if not 0<old['index']<=count:return None
    if old['current']!=old['first']+20*min(old['index'],count-1):return None
    command=old['first']+20*(old['index']-1)
    source,oam=struct.unpack_from('<II',rom,command-0x08000000)
    if old.get('tileOffset')!=source or old['oam']!=oam+OAM+0x08000000:return None
    objects,_=layout(rom,OAM+oam)
    size=sum(v['width']*v['height']//64 for v in objects)*32
    if size!=old['tileCount']*32 or size>a['allocation']*32:return None
    expected=rom[TILES+source:TILES+source+size]+anchor['block'][size:]
    if len(expected)!=a['allocation']*32 or block!=expected:return None
    return ('exact previously queued native upload completes during sequence rewind' if rewind else
            'exact previously queued native upload completes during sequence change' if new_sequence
            else 'exact previously queued native upload completes during facing change')


def layout_reset_display(rom,ram,vram,hardware,address,anchor,elapsed_frames):
    """Observe a short native layout reset without pretending it is configured.

    The live layout pointer is zero and tile source is -1 for two video frames
    in the retained original trace. Require the queued native layout, sequence,
    full allocation and actual hardware OAM to equal a recent direct proof.
    """
    import struct
    from native_art import OAM
    if not anchor or not anchor['direct'] or not 0<elapsed_frames<=4:return None
    old=anchor['actor'];flags,resource,mode,timer,index,count=struct.unpack_from('<I2x5H',ram,address)
    tile,alternate,allocation=struct.unpack_from('<3H',ram,address+0x12)
    offset=struct.unpack_from('<I',ram,address+0x20)[0]
    tiles=struct.unpack_from('<H',ram,address+0x24)[0]
    queued,live=struct.unpack_from('<II',ram,address+0x28)
    first,current=struct.unpack_from('<II',ram,address+0x34)
    # Native21618 initializes index/current and clears source/layout; callers
    # can additionally set100 (212c4 bypasses timer decrement with that flag).
    # Accept that constructor variant only at its first entry, not arbitrary
    # additional flags or a later stalled animation phase.
    if flags not in (0x67,0x167) or timer or offset!=0xffffffff or live:return None
    if flags==0x167 and (index!=0 or current!=first):return None
    if (resource,tile,allocation)!=anchor['identity'] or mode!=old['mode'] or queued!=old['oam']:return None
    if first!=old['first'] or not 0<=index<count or current!=first+20*index:return None
    if struct.unpack_from('<I',rom,first-0x08000004)[0]!=count or tiles!=old['tileCount']:return None
    native_oam=struct.unpack_from('<I',rom,current-0x08000000+4)[0]+OAM+0x08000000
    if native_oam!=queued:return None
    table=struct.unpack_from('<I',rom,0x2102c)[0]-0x08000000
    desc=struct.unpack_from('<I',rom,table+resource*4)[0]-0x08000000
    desc+=(mode&~3)*6+(12 if mode&3 in (1,2) else 0)
    if struct.unpack_from('<I',rom,desc)[0]+4!=first:return None
    p=0x10000+tile*32
    block=vram[p:p+allocation*32]
    proof='bounded native layout reset retains verified allocation'
    if block!=anchor['block']:
        # A previously queued frame can finish uploading in the same video
        # interval in which native code clears the live layout. Accept only
        # that exact previously recorded command, never any matching pose.
        if not old['flags']&0x120000:return None
        command=current
        if old['current']!=current:
            # A constructor rewind can reset index/current while the preceding
            # decoded upload still completes. Require its actually captured
            # tile source, not merely a matching pose or the next command.
            if flags!=0x167 or index or current!=first:return None
            old_index=old['index']
            if not 0<old_index<count or old['current']!=first+20*old_index:return None
            command=first+20*(old_index-1)
            prior_source,prior_layout=struct.unpack_from('<II',rom,command-0x08000000)
            if old.get('tileOffset')!=prior_source or prior_layout+OAM+0x08000000!=old['oam']:return None
        source=struct.unpack_from('<I',rom,command-0x08000000)[0]
        from native_art import TILES,layout
        objects,_=layout(rom,native_oam-0x08000000)
        size=sum(v['width']*v['height']//64 for v in objects)*32
        if size>allocation*32:return None
        expected=rom[TILES+source:TILES+source+size]+anchor['block'][size:]
        if len(expected)!=allocation*32 or block!=expected:return None
        proof='exact previously queued native frame commits during bounded layout reset'
    objects=[struct.unpack_from('<3H',hardware,i*8) for i in range(128)]
    visible=[v for v in objects if v[0]&0x300!=0x200 and v[2]&1023==tile]
    if not visible or visible!=anchor['hardware']:return None
    return dict(old,flags=flags,mode=mode,timer=timer,index=index,first=first,current=current,
        displayedFrames=[],exactUpload=False,configured=False,queuedLayout=queued,liveLayout=live,
        displayProof=proof)
