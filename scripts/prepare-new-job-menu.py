"""Package reviewed-size UI proposals without changing character drawings.

Wheel figures retain every approved base index and use only vertical padding.
Badges combine a generated head with the existing frame and the same six-pixel
lettering renderer as equipment-preview.c. Captured dim palette previews are
labelled as such; actual new-job runtime routing still requires verification.
"""
import argparse
import json
import re
from pathlib import Path
import numpy as np
from PIL import Image
from new_job_art_helpers import ROOT, checked, record
from native_art import tile_image, pack_tiles, sha
from native_miniatures import decode, CONTAINER


def build(base_path, ui_folder, out):
    if not out.is_relative_to(ROOT/'build/art') or out.exists():raise ValueError('Use a fresh build/art folder')
    base=json.loads(base_path.read_text());rom=checked(base['paletteROM']).read_bytes()
    approval=json.loads(checked(base['approval']).read_text());approved={r['path']:r['sha256'] for r in approval['images']}
    if not approval['approved']:raise ValueError('Base approval required')
    font_path=ROOT/'src/engine/equipment-preview.c';source=font_path.read_text()
    table=source.split('letters[26]={',1)[1].split('};',1)[0]
    letters=[(int(w),[int(n) for n in rows.split(',')]) for w,rows in re.findall(r'\{(\d+),\{([\d,]+)\}\}',table)]
    if len(letters)!=26 or any(len(rows)!=6 for w,rows in letters):raise ValueError('Lettering layout changed')
    old_manifest=ROOT/'build/art/native-final-integration-2026-09-20/candidate.json'
    old=json.loads(old_manifest.read_text());out.mkdir(parents=True);units=[]
    for spec in base['jobs']:
        slug=spec['slug'];old_job={'physician':120,'sapper':122}[slug]
        neutral=record(ROOT/base['outputDirectory']/(spec['front']+'-native.png'))
        if approved.get(neutral['path'])!=neutral['sha256']:raise ValueError('Changed base')
        body=Image.open(checked(neutral))
        if body.mode!='P' or body.size!=(32,32):raise ValueError('Expected indexed approved base')
        donor=next(j['miniature']['donor'] for j in old['components']['classes']['jobs'] if j['job']==old_job)
        donor_raw=decode(rom,CONTAINER,donor);ref=tile_image(donor_raw,body.getpalette()[:48],32)
        shift=ref.getbbox()[3]-body.getbbox()[3]
        if not 0<=shift<=8:raise ValueError('Wheel baseline would clip the approved figure')
        mini=Image.new('P',(32,40));mini.putpalette(body.getpalette());mini.paste(body,(0,shift));mini.info['transparency']=0
        if mini.crop((0,shift,32,shift+32)).tobytes()!=body.tobytes():raise ValueError('Wheel pixels changed')
        path=out/(slug+'-wheel.png');mini.save(path)
        icon_receipt=ui_folder/slug/'icon-v2-receipt.json';icon=json.loads(icon_receipt.read_text())
        head=Image.open(checked(icon['native']));head_indices=np.array(head);badges={};sources={}
        text={'physician':'PHY','sapper':'SAP'}[slug]
        for state in ('eligible','ineligible'):
            template=ROOT/'build/art/job-art-approval-2026-09-20/assets'/('moogle-chemist-badge-'+state+'.png')
            panel=Image.open(template).copy()
            if state=='eligible' and panel.getpalette()[:48]!=head.getpalette()[:48]:raise ValueError('Badge bank mismatch')
            # Opaque native panel background is index 3. Artwork fills ONLY
            # the existing head rectangle; text is the existing UI font.
            block=Image.fromarray(np.where(head_indices==0,3,head_indices).astype('uint8'))
            block.putpalette(panel.getpalette());panel.paste(block,(1,1))
            panel.paste(12,(17,4,31,12));width=2+sum(letters[ord(c)-65][0] for c in text)
            for mode in (0,1):
                left=31-width
                for c in text:
                    w,rows=letters[ord(c)-65]
                    for y,row in enumerate(rows):
                        for x in range(w):
                            if not row&(1<<(w-1-x)):continue
                            if mode:panel.putpixel((left+x,5+y),3)
                            else:
                                for dy in (-1,0,1):
                                    for dx in (-1,0,1):
                                        if left+x+dx<31:panel.putpixel((left+x+dx,5+y+dy),4)
                    left+=w+1
            target=out/(slug+'-badge-'+state+'.png');panel.save(target)
            badges[state]=record(target);sources[state]=record(template)
        portrait_receipt=ui_folder/slug/'portrait-v1-receipt.json'
        portrait=json.loads(portrait_receipt.read_text());checked(portrait['native'])
        units.append(dict(slug=slug,label=spec['label'],portrait=portrait['native'],portraitReceipt=record(portrait_receipt),
            head=icon['native'],headReceipt=record(icon_receipt),badges=badges,badgeFrameSources=sources,labelText=text,
            wheel=dict(native=record(path),base=neutral,donor=donor,donorTilesSha256=sha(donor_raw),shiftY=shift,
                tileSha256=sha(pack_tiles(mini,20)),method='Exact approved indices, vertical transport padding only')))
    result=dict(units=units,baseApproval=base['approval'],paletteROM=base['paletteROM'],font=record(font_path),
        baselineReference=record(old_manifest),status='UI-proposals-not-runtime-captures',ROMWritten=False,
        dimScope='Ineligible preview uses the preserved native UI capture palette; verify actual new-job eligibility consumer after implementation.')
    path=out/'menu.json';path.write_text(json.dumps(result,indent=2)+'\n');print(path)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('base-plan','ui-folder','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();build(a.base_plan.resolve(),a.ui_folder.resolve(),a.out.resolve())
