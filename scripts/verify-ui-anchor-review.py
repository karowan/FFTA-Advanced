"""Deterministic native-color, shared-anchor, and review inventory checks."""
import json,struct
import numpy as np
from PIL import Image
from native_art import ROOT,sha
from native_portraits import PALETTES
from native_miniatures import decode

GEN=ROOT/'build/art/anchor-ui-v4-2026-09-20'
OUT=ROOT/'build/art/job-art-approval-v4-2026-09-20'
RESULTS_NAME='results.json'

def main():
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    result=json.loads((GEN/RESULTS_NAME).read_text());data=json.loads((OUT/'review-data.json').read_text())
    original=json.loads((ROOT/'build/art/job-art-approval-2026-09-20/review-data.json').read_text())
    checks=[]
    for a in result['assets']:
        for ref in a['references']+[a['native'],a['sampled'],a['raw']]:assert sha((ROOT/ref['path']).read_bytes())==ref['sha256']
        im=Image.open(ROOT/a['native']['path']);idx=np.array(im)
        assert im.size==tuple(a['nativeSize'])
        words=a['palette']['words'];expected=[((w>>s)&31)*255//31 for w in words for s in (0,5,10)]
        assert im.getpalette()[:len(expected)]==expected and idx.max()<len(words)
        if a['kind']=='portrait':assert list(struct.unpack('<48H',decode(rom,PALETTES[0],a['palette']['index'])))==words
        else:
            assert words in [list(struct.unpack_from('<16H',rom,0x419d60+n*32)) for n in range(3)]
            if a['anchorMode']=='exact-shared-native-pixels':
                anchors=a.get('conversionAnchors',a['anchors']);coords=anchors['coordinates']
                ids=anchors.get('agreementJobs')
                sources=[ROOT/f'build/art/native-reference/ui/job-{j:03}.png' for j in ids] if ids else [ROOT/r['path'] for r in a['anchors']['references']]
                heads=[np.array(Image.open(p).crop((1,1,17,15))) for p in sources]
                assert all(all(int(h[y,x])==v for h in heads) and idx[y,x]==v for x,y,v in coords)
            else:
                expected_eyes={(7,7),(10,7)}
                if a['slug']=='human-dark-knight':expected_eyes|={(7,8),(10,8)}
                assert {(x,y) for y in (7,8) for x in range(5,12) if idx[y,x]==7}==expected_eyes
        checks.append(dict(slug=a['slug'],kind=a['kind'],passed=True,anchorProof=a['anchorProof']))
    assert len(checks)==12 and data['counts']==original['counts']
    for new,old in zip(data['units'],original['units']):
        assert new['poses']==old['poses'] and new['sequences']==old['sequences'] and new['emptySlots']==old['emptySlots']
        for state in ('eligible','ineligible'):
            newimg=Image.open(OUT/new['badges'][state]);oldimg=Image.open(ROOT/'build/art/job-art-approval-2026-09-20'/old['badges'][state])
            mask=np.ones((16,32),bool);mask[1:15,1:17]=False
            assert np.array_equal(np.array(newimg)[mask],np.array(oldimg)[mask])
    paths=set()
    def visit(x):
        if isinstance(x,dict):
            for v in x.values():visit(v)
        elif isinstance(x,list):
            for v in x:visit(v)
        elif isinstance(x,str) and x.startswith('assets/'):
            assert (OUT/x).is_file(),x;paths.add(x)
    visit(data)
    report=dict(passed=True,assets=checks,linkedReviewAssets=len(paths),counts=data['counts'],
        nativeSourceRomSha256=sha(rom),runtimeTestRun=False,
        scope='Offline review only: original native palettes, extracted anchors, helmet eye coordinates, badge frame/letter indices, hashes and complete animation inventory. Visual approval and new in-game import remain pending.')
    (OUT/'anchor-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(checks),linkedReviewAssets=len(paths),counts=data['counts'])))

if __name__=='__main__':main()
