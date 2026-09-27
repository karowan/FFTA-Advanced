"""Verify real-ROM anchor exports, phase exclusions and fixed-canvas placement.

Read-only; uses preserved originals, never synthesizes game fixtures or artwork.
The test result cannot approve anatomical labels or generated animation quality.
"""
import argparse
import json
import struct
from pathlib import Path
from PIL import Image
from native_art import ROOT, ANIM, OAM, TILES, compose, layout, palette, sha, u32
from new_job_art_helpers import checked


def main(folder):
    data=json.loads((folder/'anchors.json').read_text())
    rom=checked(data['sourceROM']).read_bytes()
    manifest=json.loads(checked(data['manifest']).read_text());checked(data['selections'])
    images={};total=0;matched_pixels=0;absent=0;mismatch=0
    for key,draw in data['nativeDrawings'].items():
        objects,raw=layout(rom,draw['oamOffset'])
        assert objects==draw['objects'] and sha(raw)==draw['oamSha256']
        n=max(o['tile']+o['width']*o['height']//64 for o in objects)
        tiles=rom[draw['tileOffset']:draw['tileOffset']+32*n]
        assert sha(tiles)==draw['tileSha256']
        im=compose(tiles,objects,palette(rom,0x41a860)[1])
        saved=Image.open(folder/draw['image']);assert saved.mode=='P' and saved.size==(64,64)
        assert saved.tobytes()==im.crop((16,8,80,72)).tobytes()
        assert saved.getpalette()[:48]==im.getpalette()[:48]
        assert sha((folder/draw['image']).read_bytes())==draw['imageSha256']
        b=im.getbbox();g=draw['geometry']
        assert g['bounds']==[b[0]-48,b[1]-64,b[2]-48,b[3]-64]
        for row in g['rows']:
            xs=[x for x in range(96) if im.getpixel((x,row['y']+64))]
            assert row['left']==min(xs)-48 and row['rightExclusive']==max(xs)+1-48
        images[key]=im
    for unit,source in zip(data['units'],manifest['units']):
        expected={(r['lifetime'],s['slot']):s for r in source['authoringReferenceResources'] for s in r['slots']}
        assert set(expected)=={(s['lifetime'],s['slot']) for s in unit['sequences']}
        for seq in unit['sequences']:
            old=expected[seq['lifetime'],seq['slot']]
            assert len(seq['records'])==len(old['frames'])
            for r,f in zip(seq['records'],old['frames']):
                total+=1
                for k in ['index','duration','command','params']:
                    assert r[k]==f[k]
                assert r['pose']==f.get('pose')
                raw=rom[r['address']:r['address']+20]
                assert raw.hex()==r['raw']
                if not r.get('canonical'):
                    assert r['command']!=1;continue
                drawing=data['nativeDrawings'][r['canonical']]
                assert (drawing['tileOffset'],drawing['oamOffset'])==(TILES+u32(raw,0),OAM+u32(raw,4))
                aligned=[]
                for ref in r['references']:
                    absent+=ref['status']=='absent';mismatch+=ref['status']=='different-record-schedule'
                    table=u32(rom,ANIM+ref['actor']*4)-0x08000000
                    pointer=u32(rom,table+seq['slot']*12)
                    if ref['status']=='absent':
                        assert not pointer and 'drawing' not in ref
                    if ref['status']=='timing-and-command-match':
                        q=pointer-0x08000000;count=u32(rom,q)
                        sig=[]
                        for i in range(count):
                            _,_,d,c,*params=struct.unpack_from('<IIBB5H',rom,q+4+20*i)
                            sig.append([d,c,params])
                        assert sig==seq['schedule']
                        aligned.append(images[ref['drawing']])
                assert len(aligned)==r['alignedOriginalJobs']
                if len(aligned)<3:assert not r['sharedPatches']
                for patch in r['sharedPatches']:
                    assert patch['support']==len(aligned)
                    for x,y,index in patch['pixels']:
                        assert index!=0 and all(im.getpixel((x+48,y+64))==index for im in aligned)
                        matched_pixels+=1
        for pid,draft in unit['drafts'].items():
            im=Image.open(checked(draft['source']))
            dx,dy=draft['worksheetTranslation']
            canvas=Image.new('P',(96,96));canvas.paste(im,(32+dx,28+dy))
            assert Image.open(folder/draft['image']).tobytes()==canvas.crop((16,8,80,72)).tobytes()
            assert unit['poseUses'][pid]
    assert total==data['counts']['records']
    # The real inherited Sapper catalog contains missing original sequences;
    # this check would catch a return to the old silent-fallback worksheet.
    assert absent>0
    result=dict(passed=True,records=total,originalDrawings=len(images),verifiedSharedPixels=matched_pixels,
                absentReferenceRecords=absent,differentScheduleRecords=mismatch,
                checks=['lossless fixed-position original extraction','ROM object positions and row spans',
                        'complete ordered draw/control/null coverage','shared patch unanimity and schedule exclusion',
                        'missing references stay missing','draft placement preserves exact approved/proposed pixels'],
                anatomicalApproval=False)
    (folder/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--atlas',type=Path,required=True)
    main(p.parse_args().atlas)
