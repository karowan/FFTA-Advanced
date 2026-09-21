"""Verify the final reviewed artwork adds no palette system or runtime hooks.

Authenticate every source pose and independently quantize it directly to the
unchanged native shared palette. Allow only reviewed image/archive data and
declared graphics pointers in the complete ROM relative to accepted engineering.
Portraits use their existing native per-portrait 48-color archive format.
"""
import argparse,datetime,hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,pack_tiles
from native_miniatures import decode


def main():
    basepath=ROOT/'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json'
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',type=Path,default=ROOT/'build/art/reviewed-integration/native-complete-candidate.json')
    path=parser.parse_args().manifest
    base=json.loads(basepath.read_text());meta=json.loads(path.read_text())
    original=Path(base['path']).read_bytes();rom=Path(meta['path']).read_bytes()
    out=ROOT/'build/art/reviewed-integration/native-contract'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);checks=[];failure=None
    def check(ok,label):
        assert ok,label
        checks.append(label)
    try:
        check(hashlib.sha1(original).hexdigest()==base['romSha1']=='a28b624bb13c8f2f2597a4d4bd3999b17c234b99','Accepted native engineering parent')
        check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Final assembled ROM authentication')
        c=meta['components'];a=c['reviewedActions'];m=c['reviewedNativeMiniatures']
        check(a['paletteMode']=='native-shared' and not a['draft'] and not a['missing'] and not a['provisional'],'Complete approved native-palette import')
        check(len(a['assets'])==675 and a['importedDrawRecords']==a['drawRecords']==3025 and a['controlRecords']==1116,'Every reviewed pose and animation record retained')
        jobs=struct.unpack_from('<I',rom,0xc8598)[0]-0x08000000
        selector_changes={p['job']:p for p in a.get('nativeSelectorChanges',[])}
        declared=json.loads((ROOT/'src/art/race-study/nonhuman-native-color-v1.json').read_text()).get('selectorChanges',[])
        if selector_changes:
            check([{k:p[k] for k in ('job','before','after','reason')} for p in selector_changes.values()]==declared,'Exact documented native class-side choices')
            for job,p in selector_changes.items():
                check(p['offset']==jobs+52*job+11 and original[p['offset']]==p['before'] and rom[p['offset']]==p['after'],'Exact selector byte '+str(job))
        for asset in a['assets']:
            label=str((asset['job'],asset['pose']));at=asset['nativePaletteOffset']
            check(rom[at:at+32]==original[at:at+32] and sha(rom[at:at+32])==asset['paletteSha256'],'Unchanged native palette '+label)
            selectors=rom[jobs+52*asset['job']+11]
            expected=selector_changes.get(asset['job'],{}).get('after',original[jobs+52*asset['job']+11])
            check(selectors==expected and selectors&15==asset['nativeSelector'] and selectors>>4==asset['opposingSelector'],'Declared existing native ally/enemy selectors '+label)
            source=ROOT/asset['source'];check(sha(source.read_bytes())==asset['sourceSha256'],'Authenticated reviewed source '+label)
            im=Image.open(source).convert('RGBA');colors=struct.unpack_from('<16H',rom,at);pixels=[]
            for r,g,b,alpha in im.get_flattened_data():
                word=round(r*31/255)|(round(g*31/255)<<5)|(round(b*31/255)<<10)
                pixels.append(0 if not alpha else min(range(1,16),key=lambda i:sum((((word>>s)&31)-((colors[i]>>s)&31))**2 for s in (0,5,10))))
            indexed=Image.new('P',(32,32));indexed.putdata(pixels)
            check(pack_tiles(indexed,16)==rom[asset['tile']:asset['tile']+512],'Direct source to native indices; transparency preserved '+label)
        for p in c['nativePaletteTransport']['patches']:
            if p['offset'] in c['nativePaletteTransport']['restoredNativeHooks']:
                check(rom[p['offset']:p['offset']+p['bytes']]==bytes.fromhex(p['after']),'Native graphics hook '+hex(p['offset']))
        live=c['livePalette'];at=live['symbols']['ffta_art_custom_mask']-0x08000000
        check(rom[at:at+4]==bytes(4),'No custom palette ownership demand')
        for at,size in ((0x89660,8),(0x87b90,12),(0x87c28,12),(0x87d58,12),(0x88060,8)):
            check(rom[at:at+size]==original[at:at+size],'Original menu palette/upload code '+hex(at))
        check(rom[0x94eddc:0x94eddc+512]==original[0x94eddc:0x94eddc+512],'Complete original menu OBJ palette unchanged')
        for i in range(54):check(decode(rom,m['container'],i)==decode(original,base['components']['classes']['container'],i),'Original miniature '+str(i))
        for j in m['jobs']:
            check(sha(decode(rom,m['container'],j['index']))==j['tileSha256'],'Reviewed native miniature '+str(j['job']))
            if j.get('conversion','').startswith('Exact native base indices'):
                source=Image.open(j['source']);check(sha(Path(j['source']).read_bytes())==j['sourceSha256'],'Native menu base provenance')
                canvas=Image.new('P',(32,40));canvas.paste(source,(0,j['offsetY']))
                check(pack_tiles(canvas,20)==decode(rom,m['container'],j['index']),'Menu preserves exact native sprite indices')
        allowed=set(range(*a['used']))|set(range(*m['used']))
        allowed.update(p['offset'] for p in selector_changes.values())
        for r in a['resources']:allowed.update(range(a['table']+r['id']*4,a['table']+r['id']*4+4))
        for p in m['pointers']:allowed.update(range(p,p+4))
        for p in c['reviewedPortraits']['patches']:allowed.update(range(p['offset'],p['offset']+p['bytes']))
        for p in c.get('approvedRound8',{}).get('patches',[]):allowed.update(range(p['offset'],p['offset']+p['bytes']))
        badge=c['reviewedMenuBadges'];allowed.update(range(badge['offset'],badge['offset']+badge['bytes']))
        check(len(rom)==len(original) and all(x==y or i in allowed for i,(x,y) in enumerate(zip(rom,original))),'Only declared graphics data/pointers changed; every other byte remains accepted engineering')
    except BaseException as error:failure=repr(error)
    report=dict(status='failed' if failure else 'passed',romSha1=meta['romSha1'],manifest=str(path),manifestSha256=sha(path.read_bytes()),
        baseRomSha1=base['romSha1'],checks=checks,failure=failure,scope=__doc__)
    dest=out/'report.json';dest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(checks),failure=failure,report=str(dest))))
    assert failure is None,failure


if __name__=='__main__':main()
