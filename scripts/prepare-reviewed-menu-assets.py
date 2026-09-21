"""Convert approved neutral sprites for the separate badge and wheel consumers.

No character art is drawn; head crops and palette mappings remain reviewable.
Original native palette tables and the right-hand job lettering stay intact.
"""
import argparse,json,hashlib,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw
from native_art import ROOT,sha,palette,tile_image,pack_tiles
from native_miniatures import decode


def mapped(part,rgb):
    image=Image.new('P',part.size);image.putpalette(rgb+[0]*(768-len(rgb)))
    def index(p):
        if p[3]<128:return 0
        return min(range(1,16),key=lambda c:sum((p[k]-rgb[c*3+k])**2 for k in range(3)))
    image.putdata([index(p) for p in part.convert('RGBA').get_flattened_data()]);image.info['transparency']=0
    return image


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--parent',type=Path,default=ROOT/'build/art/reviewed-integration/action-candidate.json')
    parser.add_argument('--output',type=Path,default=ROOT/'build/art/reviewed-integration/menu-assets');parser.add_argument('--native-conversion',type=Path)
    args=parser.parse_args();parentpath=args.parent.resolve();parent=json.loads(parentpath.read_text())
    rom=__import__('pathlib').Path(parent['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==parent['romSha1']
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
    banks={p['job']:p['paletteBank'] for p in json.loads((ROOT/'src/art/job-portraits.json').read_text())['portraits']}
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    conversions={}
    if args.native_conversion:
        conversions={u['job']:u for u in json.loads(args.native_conversion.read_text())['units']}
        spec=importlib.util.spec_from_file_location('study',ROOT/'scripts/study-reviewed-native-color.py')
        study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)
    jobs=[];sheet=Image.new('RGBA',(1000,((len(catalog['units'])+4)//5)*220),(228,226,220,255));draw=ImageDraw.Draw(sheet)
    icons=parent['components']['preview']['symbols']['original_job_icons']-0x08000000
    classes=parent['components']['classes']
    def record(p):return dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p.read_bytes()))
    for n,u in enumerate(catalog['units']):
        source=ROOT/'build/art/approved-class-animation-2026-09-19'/u['slug']/'front-neutral.png'
        if u['job'] in conversions:
            conversion=conversions[u['job']];source=ROOT/conversion['approvedNativeBase']
            assert sha(source.read_bytes())==conversion['approvedNativeBaseSha256']
        im=Image.open(source).convert('RGBA');assert im.size==(32,32)
        x,y,right,bottom=im.getbbox();crop=(x,y,right,y+(bottom-y+1)//2)
        head=im.crop(crop);head.thumbnail((16,14),Image.Resampling.NEAREST)
        bank=banks[u['job']];paloff=0x419d60+32*(bank-13);_,rgb=palette(rom,paloff)
        badge=tile_image(rom[icons+n*256:icons+(n+1)*256],rgb,32)
        # Clear only the existing UI head panel, preserving its frame/label area.
        badge.paste(3,(1,1,17,15));part=mapped(head,rgb)
        if u['job'] in conversions:part,_=study.convert(head,[rgb[i:i+3] for i in range(0,48,3)],'neutral')
        badge.paste(part,(1+(16-part.width)//2,1+(14-part.height)//2),head.getchannel('A'))
        badgepath=out/(u['slug']+'-badge.png');badge.save(badgepath,bits=4)
        old=next(j['miniature'] for j in classes['jobs'] if j['job']==u['job'])
        _,mrgb=palette(rom,old['paletteReference']);figure=mapped(im,mrgb)
        donor=tile_image(decode(rom,classes['container'],old['donor']),mrgb,32)
        dy=donor.getbbox()[3]-im.getbbox()[3];assert 0<=dy<=8,(u['slug'],dy)
        mini=Image.new('P',(32,40));mini.putpalette(figure.getpalette());mini.paste(figure,(0,dy));mini.info['transparency']=0
        minipath=out/(u['slug']+'-miniature.png');mini.save(minipath,bits=4)
        jobs.append(dict(job=u['job'],slug=u['slug'],source=record(source),status='converted-awaiting-review',
            badge=dict(**record(badgepath),crop=list(crop),size=list(head.size),paletteBank=bank,paletteOffset=paloff,paletteSha256=sha(rom[paloff:paloff+32]),tileSha256=sha(pack_tiles(badge,8))),
            miniature=dict(**record(minipath),index=old['index'],donor=old['donor'],paletteReference=old['paletteReference'],paletteSha256=sha(rom[old['paletteReference']:old['paletteReference']+32]),offsetY=dy,tileSha256=sha(pack_tiles(mini,20)))))
        cx=n%5*200;cy=n//5*220;draw.text((cx+5,cy+4),u['label'],fill='black')
        sheet.alpha_composite(im.resize((96,96),Image.Resampling.NEAREST),(cx,cy+26))
        sheet.alpha_composite(mini.convert('RGBA').resize((96,120),Image.Resampling.NEAREST),(cx+100,cy+26))
        sheet.alpha_composite(badge.convert('RGBA').resize((192,96),Image.Resampling.NEAREST),(cx,cy+124))
    path=out/'manifest.json'
    encoded=json.dumps(dict(schema=1,parent=record(parentpath),parentRomSha1=parent['romSha1'],jobs=jobs,scope=__doc__),indent=2)+'\n'
    if path.exists():assert path.read_text()==encoded,'Preserve existing conversion/review provenance'
    else:path.write_text(encoded)
    sheet.save(out/'review.png');print(path)


if __name__=='__main__':main()
