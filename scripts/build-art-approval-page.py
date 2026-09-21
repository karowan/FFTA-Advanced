"""Export current ROM artwork and its provenance for user approval; no art edits.

Decodes final native tiles/palettes, preserves all sequence records, and lays out
existing generation stages and captured UI. Does not modify the ROM or saves.
"""
import hashlib,json,shutil,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,palette,tile_image,layout,compose,TILES,OAM
from native_portraits import entry,decode as portrait_decode,pack as portrait_pack
from native_miniatures import decode as archive_decode

OUT=ROOT/'build/art/job-art-approval-2026-09-20'
FINAL=ROOT/'build/art/native-final-integration-2026-09-20'

def main():
    manifest=FINAL/'candidate.json';meta=json.loads(manifest.read_text())
    rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
    actions=meta['components']['reviewedActions'];catalog_path=Path(actions['catalog'])
    assert sha(catalog_path.read_bytes())==actions['catalogSha256']
    catalog=json.loads(catalog_path.read_text())
    plan_path=Path(meta['components']['reviewedPortraits']['plan'])
    assert sha(plan_path.read_bytes())==meta['components']['reviewedPortraits']['planSha256']
    plan=json.loads(plan_path.read_text())
    evidence=json.loads((FINAL/'evidence.json').read_text());assert evidence['romSha1']==meta['romSha1']
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'assets').mkdir(exist_ok=True)
    inventory=[]
    def save(im,name,source):
        path=OUT/'assets'/(name+'.png');im.save(path)
        inventory.append(dict(path=str(path.relative_to(OUT)),sha256=sha(path.read_bytes()),source=source))
        return str(path.relative_to(OUT)).replace('\\','/')
    def copy(ref,name):
        p=ROOT/ref['path'];assert sha(p.read_bytes())==ref['sha256'],p
        dest=OUT/'assets'/(name+p.suffix);shutil.copy2(p,dest)
        inventory.append(dict(path=str(dest.relative_to(OUT)),sha256=sha(dest.read_bytes()),source=str(p)))
        return str(dest.relative_to(OUT)).replace('\\','/')
    def capture(test,name):
        row=next(r for r in evidence['screenshots'] if Path(r['path']).name==test+'-'+name)
        return copy(row,test+'-'+Path(name).stem)
    reports={r['test']:r for r in evidence['reports']}
    inv=reports['test-final-native-inventory-ui'];invpath=Path(inv['path'])
    assert sha(invpath.read_bytes())==inv['sha256']
    vram=(invpath.parent/'party-new-jobs.vram').read_bytes()
    pals=(invpath.parent/'party-new-jobs.palette').read_bytes()
    badges=meta['components']['reviewedMenuBadges']
    issues={116:'Face distorted in the battle portrait.',119:'Unwanted blue bandana behind the helmet.',125:'Portrait looks distorted and does not match the design.'}
    units=[];framecount=controls=sequencecount=emptycount=0
    for u in catalog['units']:
        job=u['job'];slug=u['slug'];p=next(x for x in plan['jobs'] if x['job']==job)
        out=dict(job=job,slug=slug,label=u['label'],issue=issues.get(job,''),poses=[],sequences=[],emptySlots=[])
        out['concept']=copy(p['concept'],slug+'-concept')
        out['worksheet']=copy(p['generatedSource'],slug+'-generated-worksheet')
        out['template']=copy(p['template'],slug+'-input-template')
        out['sourcePortrait']=copy(p['output'],slug+'-portrait-extracted')
        out['prompt']=p['prompt'];out['generationVersion']=p.get('version',1)
        out['references']=[copy(r['image'],slug+'-reference-'+str(r['job'])) for r in p['nativeReferences']]
        portrait=next(x for x in meta['components']['portraits']['jobs'] if x['job']==job)
        native=Image.open(portrait['nativeImage'])
        raw,_=portrait_decode(rom,entry(rom,meta['components']['portraits']['pixelArchive'],portrait['portrait']))
        assert portrait_pack(native)==raw and sha(raw)==portrait['pixelsSha256']
        portrait_pal=archive_decode(rom,meta['components']['portraits']['paletteArchives'][0],portrait['paletteIDs'][0])
        assert sha(portrait_pal)==portrait['paletteSha256']
        words=struct.unpack('<48H',portrait_pal)
        assert native.getpalette()[288:432]==[((w>>s)&31)*255//31 for w in words for s in (0,5,10)]
        out['nativePortrait']=save(native,slug+'-native-portrait',dict(archive=meta['components']['portraits']['pixelArchive'],index=portrait['portrait']))
        out['portraitHash']=sha(raw)
        out['battle']=capture('test-final-native-fight-'+str(job),'moved.png')
        out['menu']=capture('test-final-native-menus',f'generated-{job}-wheel0.png')
        shot=Image.open(OUT/out['battle']);assert shot.size==(720,480)
        out['battleFace']=save(shot.crop((0,306,156,465)).resize((52,53),Image.Resampling.NEAREST),slug+'-battle-face','Unretouched crop from '+out['battle'])
        shot=Image.open(OUT/out['menu']);assert shot.size==(720,480)
        out['menuFace']=save(shot.crop((0,0,156,174)).resize((52,58),Image.Resampling.NEAREST),slug+'-menu-face','Unretouched crop from '+out['menu'])
        index=job-116;row=next(x for x in badges['jobs'] if x['job']==job)
        badge_raw=vram[0x20+index*256:0x20+(index+1)*256]
        # Captured VRAM includes the game's live lettering. Authenticate heads
        # against the final ROM; do not redraw lettering or costume pixels.
        for at in (0,128):assert badge_raw[at:at+64]==rom[badges['offset']+index*256+at:badges['offset']+index*256+at+64]
        bank=row['badge']['paletteBank'];out['badges']={}
        for state,pal in [('eligible',bank),('ineligible',bank-13)]:
            _,rgb=palette(pals,pal*32)
            out['badges'][state]=save(tile_image(badge_raw,rgb,32),slug+'-badge-'+state,dict(vram=str(invpath.parent/'party-new-jobs.vram'),paletteBank=pal))
        # Use the component's native archive for exact menu pixels.
        mini=next(x['miniature'] for x in meta['components']['classes']['jobs'] if x['job']==job)
        selector=next(x for x in actions['assets'] if x['job']==job)['nativeSelector']
        mini_raw=archive_decode(rom,meta['components']['classes']['container'],mini['index'])
        out['miniatures']={}
        for state,at in [('bright',0x94eddc+selector*32),('dim',0x94ee3c+selector*32)]:
            _,rgb=palette(rom,at);out['miniatures'][state]=save(tile_image(mini_raw,rgb,32),slug+'-mini-'+state,dict(archive=meta['components']['classes']['container'],index=mini['index'],palette=at))
        posemap={}
        for pose in u['poses']:
            a=next(x for x in actions['assets'] if x['job']==job and x['pose']==pose['id'])
            raw=rom[a['tile']:a['tile']+512];assert sha(raw)==a['tileSha256']
            objects,_=layout(rom,a['oam']);assert len(objects)==1
            record=dict(id=pose['id'],images={},uses=pose['uses'],meaning=pose.get('generation',{}).get('poseMeaning',{}).get('label',''),sha256=sha(raw))
            for side,sel in [('ally',a['nativeSelector']),('enemy',a['opposingSelector'])]:
                _,rgb=palette(rom,0x419d60+sel*32)
                full=compose(raw,objects,rgb);im=full.crop((16,16,80,80))
                assert sum(v!=0 for v in full.get_flattened_data())==sum(v!=0 for v in im.get_flattened_data()),'Clipped actor export'
                record['images'][side]=save(im,slug+'-'+pose['id']+'-'+side,dict(tile=a['tile'],oam=a['oam'],palette=sel))
            posemap[pose['id']]=record;out['poses'].append(record)
        for resource in actions['resources']:
            if resource['job']!=job:continue
            source=next(r for r in catalog['resources'] if r['resource']==resource['id'])
            for slot in source['slots']:
                if not slot['frames']:
                    assert struct.unpack_from('<I',rom,resource['descriptors']+slot['slot']*12)[0]==0
                    out['emptySlots'].append(dict(lifetime=resource['lifetime'],slot=slot['slot']));emptycount+=1;continue
                sequence=next(s for s in resource['sequences'] if s['slot']==slot['slot'])
                pointer=struct.unpack_from('<I',rom,resource['descriptors']+slot['slot']*12)[0]-0x08000000
                assert pointer==sequence['target']
                count=struct.unpack_from('<I',rom,pointer)[0];assert count==len(slot['frames'])
                frames=[]
                for n,frame in enumerate(slot['frames']):
                    t,o,duration,command,*params=struct.unpack_from('<IIBB5H',rom,pointer+4+20*n)
                    assert (duration,command,params)==(frame['duration'],frame['command'],frame['params'])
                    f=dict(index=n,duration=duration,command=command,params=params)
                    if command==1:
                        f['pose']=frame['pose'];a=next(x for x in actions['assets'] if x['job']==job and x['pose']==f['pose'])
                        assert t+TILES==a['tile'] and o+OAM==a['oam'];framecount+=1
                    else:controls+=1
                    frames.append(f)
                out['sequences'].append(dict(id=f'{slug}-{resource["lifetime"]}-{slot["slot"]:02}',lifetime=resource['lifetime'],slot=slot['slot'],frames=frames));sequencecount+=1
        units.append(out)
    assert sum(len(u['poses']) for u in units)==675 and framecount==3025 and controls==1116 and sequencecount==796 and emptycount==884
    data=dict(romSha1=meta['romSha1'],status='User art approval round 1; no new approvals inferred',units=units,
        counts=dict(jobs=10,poses=675,sequences=sequencecount,draws=framecount,controls=controls,emptySlots=emptycount),
        badgeScreenshot=capture('test-final-native-inventory-ui','party-new-jobs.png'))
    (OUT/'review-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    inventory_path=OUT/'export-proof.json'
    inventory_path.write_text(json.dumps(dict(romSha1=meta['romSha1'],manifestSha256=sha(manifest.read_bytes()),
        catalogSha256=sha(catalog_path.read_bytes()),portraitPlanSha256=sha(plan_path.read_bytes()),
        counts=data['counts'],files=inventory),indent=2)+'\n')
    template=(ROOT/'scripts/art-approval-page.html.txt').read_text(encoding='utf-8')
    (OUT/'index.html').write_text(template.replace('/*REVIEW_DATA*/',json.dumps(data).replace('</','<\\/')),encoding='utf-8')
    print(json.dumps(dict(page=str(OUT/'index.html'),counts=data['counts'],files=len(inventory))))

if __name__=='__main__':main()
