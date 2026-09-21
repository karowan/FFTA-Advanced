"""Apply the approved Samurai conversion and retain the tested Dark Knight.

Pure offline native-color conversion. No new colors, pixel drawing, animation
substitution, live palette changes, or player-save access.
"""
import importlib.util,json,shutil
import numpy as np
from PIL import Image
from native_art import ROOT,sha

spec=importlib.util.spec_from_file_location('transfer',ROOT/'scripts/study-approved-native-transfer.py')
transfer=importlib.util.module_from_spec(spec);spec.loader.exec_module(transfer)


def main():
    receipts=json.loads((ROOT/'src/art/race-study/native-color-study-v1.json').read_text())
    unit=json.loads((ROOT/'src/art/race-study/full-animation-v1/116-human-samurai.json').read_text())
    approval=next(r for r in receipts['nativeConversions'] if r['job']==116)
    assert approval['status'].startswith('native-base-user-approved') and approval['method']=='neutral'
    base=ROOT/approval['converted'];assert sha(base.read_bytes())==approval['convertedSha256']
    source=ROOT/unit['front']['path'];assert sha(source.read_bytes())==unit['front']['sha256']
    target=Image.open(base);colors=np.array(target.getpalette()[:48]).reshape(16,3).tolist()
    words=receipts['nativePalettes'][approval['nativePalette']]['words']
    assert colors==[[((w>>s)&31)*255//31 for s in (0,5,10)] for w in words]
    out=ROOT/'build/art/native-human-integration-2026-09-20';folder=out/unit['slug'];folder.mkdir(parents=True,exist_ok=True)
    records=[];images=[]
    for pose in unit['poses']:
        source=ROOT/pose['output'];assert sha(source.read_bytes())==pose['outputSha256']
        im=Image.open(source).convert('RGBA');converted,_=transfer.study.convert(im,colors,'neutral')
        dest=folder/(pose['id']+'.png');converted.save(dest,bits=4)
        exact=pose['outputSha256']==unit['front']['sha256']
        if exact:
            assert dest.read_bytes()==base.read_bytes(),'Approved backup must reproduce exactly'
        records.append(dict(pose=pose['id'],source=pose['output'],sourceSha256=pose['outputSha256'],
                            selected=dict(path=str(dest.relative_to(ROOT)),sha256=sha(dest.read_bytes()),exactApprovedBase=exact)))
        images.append((pose['id'],converted))
    transfer.board(images,folder/'native-poses.png')
    samurai=dict(job=116,poseCount=len(records),sourceBase=unit['front'],approvedNativeBase=approval['converted'],
        approvedNativeBaseSha256=approval['convertedSha256'],nativePalette=approval['nativePalette'],nativePaletteWords=words,
        method='Exact approved neutral Oklab conversion; unchanged native palette',selectedNeighbors=None,records=records)
    priorpath=ROOT/'build/art/native-color-transfer-2026-09-20/dark-knight-candidate.json'
    prior=json.loads(priorpath.read_text());assert prior['romSha1']=='bee412823471003eb42b4f7cbf0f65bc81a095a2'
    ref=prior['components']['reviewedActions']['nativeColorConversion'];path=ROOT/ref['path']
    assert sha(path.read_bytes())==ref['sha256'];dark=json.loads(path.read_text())
    approved_dark=next(g for g in receipts['generations'] if g.get('convertedSha256')==dark['approvedNativeBaseSha256'])
    assert approved_dark['status'].startswith('native-base-user-approved')
    # Use archived, actually imported sources, not mutable study intermediates.
    assets={a['pose']:a for a in prior['components']['reviewedActions']['assets'] if a['job']==117}
    for row in dark['records']:
        asset=assets[row['pose']];path=ROOT/asset['source']
        assert sha(path.read_bytes())==row['selected']['sha256']==asset['sourceSha256']
        row['selected']['path']=asset['source']
    combined=dict(schema=1,status='approved human native bases; integration review pending',units=[samurai,dark],
        retainedDarkKnightCandidate=dict(path=str(priorpath.relative_to(ROOT)),sha256=sha(priorpath.read_bytes()),romSha1=prior['romSha1']))
    (out/'conversions.json').write_text(json.dumps(combined,indent=2)+'\n')
    print(json.dumps(dict(samuraiPoses=len(records),darkKnightPoses=len(dark['records']),out=str(out/'conversions.json'))))


if __name__=='__main__':main()
