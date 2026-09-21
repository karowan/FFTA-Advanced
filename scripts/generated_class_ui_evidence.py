"""Validate retained class-art display allocations, including cancellation.

Returning from the job wheel leaves its animated unit header alive. Infer
ownership from each captured native actor record, never from a screen label.
"""
import hashlib
from pathlib import Path
from native_art import sha
from native_miniatures import CONTAINER,decode
from actor_render_evidence import actors

def verify(meta,folder,observations,check,read=lambda p:p.read_bytes()):
    base_rom=Path(meta['source']).read_bytes();new_rom=Path(meta['path']).read_bytes()
    check(hashlib.sha1(base_rom).hexdigest()==meta['baseRomSha1'],'retained comparison ROM authenticated')
    check(hashlib.sha1(new_rom).hexdigest()==meta['romSha1'],'retained generated ROM authenticated')
    pairs=[(decode(base_rom,CONTAINER,j['miniature']['donor']),decode(new_rom,meta['container'],j['miniature']['index'])) for j in meta['jobs']]
    check(set(observations)=={'baseline','generated'},'both complete display cohorts captured')
    for kind,rom in [('baseline',base_rom),('generated',new_rom)]:
        check(set(observations[kind])=={str(j['job']) for j in meta['jobs']},kind+' all ten classes captured')
        for job in meta['jobs']:
            samples=observations[kind][str(job['job'])]
            check(set(samples)=={'wheel0','wheel1','wheel2','wheel3','cancelled'},kind+' all display lifecycle samples captured')
            for name,obs in samples.items():
                stem=folder/f'{kind}-{job["job"]}-{name}';ram=read(stem.with_suffix('.ram'));vram=read(stem.with_suffix('.vram'))
                for field in ('vram','palette','oam'):check(sha(read(stem.with_suffix('.'+field)))==obs[field],str(stem.name)+' retained '+field+' hash')
                check(sha(ram[0x80:0x1e70])==obs['owned'],str(stem.name)+' retained owned-state hash')
                figures=actors(rom,ram,vram)
                check(len(figures)==1,str(stem.name)+' one actual live header including after cancel')
                f=figures[0];obs['actor']=f
                check(f['resource']==job['resource'] and f['declaredSequence'] and bool(f['displayedFrames']),str(stem.name)+' actual resource and native uploaded frame')
                if kind=='generated':check(f['first']==0x08000004+job['sequences'][0]['target'],str(stem.name)+' generated idle ownership')
    for job in meta['jobs']:
        for name,old in observations['baseline'][str(job['job'])].items():
            new=observations['generated'][str(job['job'])][name];stem=f'{job["job"]}-{name}'
            a=read(folder/('baseline-'+stem+'.vram'));b=read(folder/('generated-'+stem+'.vram'));expected=bytearray(a)
            check(old['owned']==new['owned'],stem+' no owned gameplay-data changes')
            check(old['palette']==new['palette'],stem+' native palettes unchanged')
            before,after=old['actor'],new['actor']
            for field in ('address','tile','allocation','resource','mode'):check(before[field]==after[field],stem+' actor '+field+' unchanged')
            start=0x10000+before['tile']*32;allowed=set(range(start,start+before['allocation']*32))
            check(old['frame']!=new['frame'],stem+' actual rendered pixels change')
            for old_mini,new_mini in pairs:
                for i in range(0x10000,len(a)-639,32):
                    if a[i:i+640]==old_mini and b[i:i+640]==new_mini:expected[i:i+640]=new_mini
            check(all(x==y or i in allowed for i,(x,y) in enumerate(zip(expected,b))),stem+' exact VRAM outside identified miniature and actor allocations')
