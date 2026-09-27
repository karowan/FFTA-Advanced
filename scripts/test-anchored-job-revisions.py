"""Validate selected offline motion proposals against their real preserved inputs.

These checks prove provenance, palette and playback coverage, not anatomical
quality or a working ROM consumer. No game/emulator is launched.
"""
import argparse
import json
import re
import runpy
import copy
import uuid
import hashlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
from PIL import Image
from new_job_art_helpers import ROOT, checked


class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.players=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for key in ['src','href']:
            if key in a:self.links.append(a[key])
        if 'data-frames' in a:self.players.append(json.loads(a['data-frames']))


def verify(folder,require_complete=False):
    summary=json.loads((folder/'review-receipt.json').read_text())
    atlas=json.loads(checked(summary['atlas']).read_text());checked(summary['page'])
    expected_records=sum(len(s['records']) for u in atlas['units'] for s in u['sequences'])
    assert expected_records==summary['orderedRecords']
    poses=0;bases=0;outliers=[];translations=[]
    for unit in atlas['units']:
        selected=summary['selections'][unit['slug']]
        assert set(selected)<=set(unit['poseUses'])
        if require_complete:assert set(selected)==set(unit['poseUses']),'Missing motion proposals'
        for pid,item in selected.items():
            poses+=1
            if 'approvedSource' in item:
                source=Image.open(checked(item['approvedSource']));preview=Image.open(checked(item['preview']))
                assert preview.crop((16,20,48,52)).tobytes()==source.tobytes()
                assert sum(v!=0 for v in preview.tobytes())==sum(v!=0 for v in source.tobytes())
                bases+=1;continue
            rec=json.loads(checked(item).read_text());req=json.loads(checked(rec['request']).read_text())
            raw=checked(rec['source']);checked(req['atlas'])
            for ref in req['references']:checked(ref)
            if req.get('parentRequest'):checked(req['parentRequest'])
            if req.get('poseNotes'):checked(req['poseNotes']['source'])
            if req.get('motionAnchor'):checked(req['motionAnchor'])
            assert (req['job'],req['pose'])==(unit['slug'],pid)
            assert req['origin']==[32,56] and req['logicalGrid']==[128,128] and req['crop']==[64,64,128,128]
            rom=checked(req['paletteROM']).read_bytes();off=req['palette']['offset']
            assert [int.from_bytes(rom[i:i+2],'little') for i in range(off,off+32,2)]==req['palette']['words']
            im=Image.open(checked(rec['native']));base=Image.open(checked(rec['approvedBase']))
            assert im.mode=='P' and im.size==(64,64) and im.info.get('transparency')==0
            assert im.getpalette()[:48]==base.getpalette()[:48]
            assert set(im.tobytes())<=set(base.tobytes())|{0}
            # Test actual extraction/registration alpha against the frozen raw
            # output. This catches phantom shadow masks and clipped tall poses.
            rgba=Image.open(raw).convert('RGBA').resize((128,128),Image.Resampling.NEAREST)
            clear=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
            rgba=clear(rgba).crop((64,64,128,128))
            if req.get('registration'):
                reg=req['registration'];assert reg['sourceSha256']==rec['source']['sha256']
                assert reg['reason'].strip()
                shifted=Image.new('RGBA',(64,64));shifted.alpha_composite(rgba,tuple(reg['translation']));rgba=shifted
                translations.append([unit['slug'],pid,reg['translation']])
            assert bytes(int(v>0) for v in rgba.getchannel('A').tobytes())==bytes(int(v>0) for v in im.tobytes())
            box=im.convert('RGBA').getbbox();bounds=[box[0]-32,box[1]-56,box[2]-32,box[3]-56]
            assert bounds==rec['bounds']
            if max(abs(v) for v in rec['edgeDifferences'])>2:outliers.append([unit['slug'],pid,rec['edgeDifferences']])
    assert bases==4
    page=Page();text=(folder/'index.html').read_text(encoding='utf-8');page.feed(text)
    assert len(page.ids)==len(set(page.ids)),'Duplicate annotation targets'
    for url in page.links:
        if url.startswith('#'):assert url[1:] in page.ids
        elif not re.match(r'^[a-z]+:',url):assert (folder/unquote(url.split('#')[0])).exists(),url
    assert len(page.players)==summary['completePlayers']
    expected_players=[]
    for unit in atlas['units']:
        chosen=summary['selections'][unit['slug']]
        for seq in unit['sequences']:
            draws=[r for r in seq['records'] if r['pose']]
            if draws and all(r['pose'] in chosen for r in draws):
                expected_players.append([(r['pose'],r['duration']) for r in draws])
            for rec in seq['records']:assert f'{seq["id"]}-record-{rec["index"]}' in page.ids
    assert len(expected_players)==len(page.players)
    for expected,actual in zip(expected_players,page.players):
        assert len(expected)==len(actual)
        for (pid,ticks),frame in zip(expected,actual):
            assert pid in frame['caption'] and ticks==frame['ticks']
            assert (folder/frame['src']).exists()
    # Actual preserved inputs exercise failure boundaries. Rejected requests and
    # logs stay in a unique ignored folder; no emulator fixtures are invented.
    convert=runpy.run_path(str(ROOT/'scripts/convert-anchored-job-revision.py'))['convert']
    failure_dir=folder/'checks'/uuid.uuid4().hex;failure_dir.mkdir(parents=True)
    rejected=[]
    variants=[]
    bad=copy.deepcopy(req);bad['references'][0]['sha256']='0'*64;variants.append(('changed-reference',bad,ValueError))
    bad=copy.deepcopy(req);bad['palette']['words'][1]^=1;variants.append(('changed-palette',bad,AssertionError))
    bad=copy.deepcopy(req);bad['registration']=dict(sourceSha256='0'*64,translation=[0,1],reason='invalid source test');variants.append(('unbound-translation',bad,AssertionError))
    bad=copy.deepcopy(req);bad['registration']=dict(sourceSha256=hashlib.sha256(raw.read_bytes()).hexdigest(),translation=[0,40],reason='invalid distance test');variants.append(('large-translation',bad,AssertionError))
    for name,bad,error in variants:
        path=failure_dir/(name+'.json');path.write_text(json.dumps(bad)+'\n')
        try:convert(path,raw,name.replace('-',''))
        except error:rejected.append(name)
        else:raise AssertionError('Failed to reject '+name)
    report=dict(passed=True,selectedPoses=poses,approvedBases=bases,completePlayers=len(page.players),orderedRecords=expected_records,rejectedInvalidInputs=rejected,
                rigidTranslations=translations,extentOutliersForVisualReview=outliers,anatomicalApproval=False,runtimeImported=False)
    (folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--require-complete',action='store_true')
    a=p.parse_args();verify(a.out.resolve(),a.require_complete)
