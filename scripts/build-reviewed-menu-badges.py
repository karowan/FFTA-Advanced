"""Import approved sprite head crops into the existing native equipment badges.

Only the ten owned 256-byte images change. Native shared badge palettes, frame,
label lettering, pagination, eligibility and executable code remain intact.
This consumer intentionally uses the original game's two badge palettes.
"""
import argparse,copy,datetime,hashlib,json
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,pack_tiles


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--parent',type=Path,default=ROOT/'build/art/reviewed-integration/menu-candidate.json')
    parser.add_argument('--output',type=Path,default=ROOT/'build/art/reviewed-integration/complete-candidate.json')
    parser.add_argument('--conversion',type=Path,default=ROOT/'build/art/reviewed-integration/menu-assets/manifest.json')
    args=parser.parse_args();parent_path=args.parent
    parent=json.loads(parent_path.read_text());original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    conversion_path=args.conversion
    conversion=json.loads(conversion_path.read_text());rows=[];payload=[]
    for job in conversion['jobs']:
        source=ROOT/job['source']['path'];badge=ROOT/job['badge']['path']
        assert sha(source.read_bytes())==job['source']['sha256']
        assert sha(badge.read_bytes())==job['badge']['sha256']
        image=Image.open(badge);assert image.mode=='P' and image.size==(32,16)
        raw=pack_tiles(image,8);assert sha(raw)==job['badge']['tileSha256']
        at=job['badge']['paletteOffset']
        assert sha(original[at:at+32])==job['badge']['paletteSha256']
        rows.append(copy.deepcopy(job));payload.append(raw)
    assert [j['job'] for j in rows]==list(range(116,126))
    preview=copy.deepcopy(parent['components']['preview'])
    at=preview['symbols']['original_job_icons']-0x08000000
    blob=b''.join(payload);assert len(blob)==2560
    start,end=preview['reservation'];assert start<=at<at+len(blob)<=start+preview['bytes']<=end
    assert sha(original[start:start+preview['bytes']])==preview['binarySha256']
    rom=bytearray(original);rom[at:at+len(blob)]=blob
    assert rom[:at]==original[:at] and rom[at+len(blob):]==original[at+len(blob):]
    digest=hashlib.sha1(rom).hexdigest();folder=ROOT/'build/art/reviewed-menu-badges'/digest
    folder.mkdir(parents=True,exist_ok=True)
    def immutable(path,data):
        if path.exists():assert path.read_bytes()==data
        else:path.write_bytes(data)
    path=folder/'FFTA_Reviewed_All_Classes.gba';immutable(path,rom)
    preview['binarySha256']=sha(rom[start:start+preview['bytes']])
    preview['portraits']=rows
    preview['scope']='Reviewed sprite head crops in original native badge palettes; existing labels and eligibility preserved.'
    result=copy.deepcopy(parent)
    result.update(path=str(path),romSha1=digest,romSha256=sha(rom),source=parent['path'],baseRomSha1=parent['romSha1'])
    result['components']['preview']=preview
    result['components']['reviewedMenuBadges']=dict(offset=at,bytes=len(blob),sha256=sha(blob),
        previousSha256=sha(original[at:at+len(blob)]),jobs=rows,
        conversionManifest=str(conversion_path),conversionManifestSha256=sha(conversion_path.read_bytes()),
        parentManifest=str(folder/'parent-manifest.json'),parentManifestSha256=sha(parent_path.read_bytes()),
        sourceSha256=sha(Path(__file__).read_bytes()),scope=__doc__,productionAccepted=False)
    archive=folder/'manifest.json';result['archivedManifest']=str(archive)
    data=(json.dumps(result,indent=2)+'\n').encode();immutable(archive,data)
    immutable(folder/'parent-manifest.json',parent_path.read_bytes())
    args.output.write_bytes(data)
    print(json.dumps(dict(romSha1=digest,manifest=str(archive),badgeBytes=len(blob))))


if __name__=='__main__':main()
