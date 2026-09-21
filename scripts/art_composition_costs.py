"""Authenticate compiled Thumb call boundaries for inclusive cycle accounting.

Host-only observer sites; no ROM patches or interactive execution. Both halves
of each ARMv4T BL must match actual ROM; its next instruction is the return site.
"""
import re,subprocess
from pathlib import Path
from native_art import ROOT

def cost_sites(meta,rom,extra_callers=()):
    elf=Path(meta['compileDirectory'])/'live.elf'
    raw=subprocess.check_output([str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-objdump.exe'),'-d',str(elf)],text=True)
    callers={'ffta_art_live_compose',
             'ffta_art_palette_live_apply_prefix' if meta.get('nativeOamPrefix') else 'ffta_art_palette_live_apply',
             'plan' if meta.get('nativeOamPrefix') else 'plan.constprop.0',
             'ffta_art_owners_compose_native' if meta.get('nativeOwnerProducer') else 'ffta_art_owners_compose_filtered'}
    if meta.get('fusedCompose'):
        callers.remove('plan')
        callers.update({'plan_inputs','ffta_art_palette_live_apply_fused','ffta_art_owners_compose_fused'})
    callers.update(extra_callers)
    sites={};function=None;rows=[]
    for line in raw.splitlines():
        label=re.match(r'^([0-9a-f]+) <([^>]+)>:',line)
        if label:function=label[2]
        if function not in callers:continue
        inst=re.match(r'^\s*([0-9a-f]+):\s+([0-9a-f]{4}) ([0-9a-f]{4})\s+bl\s+[0-9a-f]+ <([^>]+)>',line)
        if not inst:continue
        pc=int(inst[1],16);word0=int(inst[2],16);word1=int(inst[3],16)
        assert word0&0xf800==0xf000 and word1&0xf800==0xf800,line
        assert rom[pc-0x08000000:pc-0x08000000+4]==word0.to_bytes(2,'little')+word1.to_bytes(2,'little'),line
        key=function+'/'+inst[4]+'@'+hex(pc)
        assert pc not in sites and pc+4 not in sites
        sites[pc]='cost:'+key+':call';sites[pc+4]='cost:'+key+':return'
        rows.append(dict(caller=function,callee=inst[4],call=pc,returnPC=pc+4,
                         instructions=rom[pc-0x08000000:pc-0x08000000+6].hex()))
    assert {r['caller'] for r in rows}==callers,'Every declared compiled caller located'
    return sites,rows

def summarize_costs(events):
    active={};rows={};shared_returns={}
    for event in events:
        site=event['site']
        if not site.startswith('cost:'):continue
        key,phase=site[5:].rsplit(':',1)
        if phase=='call':
            assert key not in active,'Unexpected recursive/reentrant sampled call'
            active[key]=event
        else:
            if key not in active:
                # A compiler loop can branch directly to the instruction
                # following a conditional call. No invocation occurred, so
                # explicitly count and exclude this shared-target arrival.
                shared_returns[key]=shared_returns.get(key,0)+1
                continue
            start=active.pop(key);cycles=(event['cycle']-start['cycle'])&0xffffffff
            assert 0<cycles<280896,'Call exceeded one display frame'
            rows.setdefault(key,[]).append(dict(cycles=cycles,videoFrame=start['videoFrame'],
                startLine=start['scanline'],endLine=event['scanline'],stack=start['registers'][13]))
    assert not active,'Incomplete sampled calls'
    return dict(calls=rows,sharedReturnArrivalsExcluded=shared_returns)
