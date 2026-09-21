"""Check local movement art provenance and preview packaging, not aesthetics."""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/art/approved-class-animation-2026-09-19'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / 'src/art/race-study/animation-generation-v1.json').read_text())
    count = 0
    colors = {}
    checked = set()

    def check(path, expected):
        key = (str(path), expected)
        if key not in checked:
            assert digest(path) == expected, ('Hash mismatch', path)
            checked.add(key)

    assert len(manifest['units']) == 10
    for unit in manifest['units']:
        check(ROOT / unit['baseSource'], unit['baseSha256'])
        check(ROOT / unit['base'], unit['baseSha256'])
        assert len(unit['poses']) == 5
        for pose in unit['poses']:
            assert pose['status'] == 'generated', (unit['slug'], pose['id'])
            for field in ['source', 'output', 'template', 'anchor', 'designReference']:
                if field + 'Sha256' in pose:
                    check(ROOT / pose[field], pose[field + 'Sha256'])
            for ref in pose['references']:
                check(ROOT / ref.get('source', ref.get('path')), ref['sha256'])
                if ref.get('manifestSha256'):
                    check(ROOT / f"build/art/native-reference/actor-{ref['actor']:03}/native.json", ref['manifestSha256'])
            if pose.get('mechanicalCorrection'):
                correction = pose['mechanicalCorrection']
                check(ROOT / correction['source'], correction['sourceSha256'])
                check(ROOT / correction['before'], correction['beforeSha256'])
                source = Image.open(ROOT / correction['source']).convert('RGBA').crop(tuple(correction['sourceBox']))
                output = Image.open(ROOT / pose['output']).convert('RGBA')
                before = Image.open(ROOT / correction['before']).convert('RGBA')
                x, y = correction['position']; box = (x, y, x+source.width, y+source.height)
                assert output.crop(box).tobytes() == source.tobytes(), ('Face mismatch', pose['id'])
                before.paste(source, (x,y))
                assert output.tobytes() == before.tobytes(), ('Collateral pixel changes', pose['id'])
            for attempt in pose.get('rejectedAttempts', []):
                if attempt.get('sha256'):
                    check(ROOT / attempt['source'], attempt['sha256'])
            count += 1
        folder = OUT / unit['slug']
        for facing in ['front', 'back']:
            hashes = set()
            for name in ['step-a', 'neutral', 'step-b']:
                path = folder / f'{facing}-{name}.png'
                with Image.open(path) as image:
                    assert image.size == (32, 32) and image.mode == 'RGBA', path
                    assert image.getbbox(), ('Empty frame', path)
                    hashes.add(hashlib.sha256(image.tobytes()).hexdigest())
                    colors[str(path.relative_to(OUT))] = len({pixel[:3] for pixel in image.getdata() if pixel[3]})
            assert len(hashes) == 3, ('Duplicate movement images', folder, facing)
            with Image.open(folder / f'{facing}-walk.gif') as gif:
                assert gif.n_frames == 4 and gif.size == (192, 192)
                timing = []
                for index in range(4):
                    gif.seek(index)
                    timing.append(gif.info['duration'])
                assert timing == [270, 130, 270, 130], timing
                protected=[p for p in unit['poses'] if p['id'].startswith(facing+'-') and p.get('mechanicalCorrection')]
                for pose in protected:
                    c=pose['mechanicalCorrection'];x,y=c['position'];box=c['sourceBox']
                    face=Image.open(ROOT/c['source']).convert('RGBA').crop(tuple(box))
                    expected=Image.new('RGBA',face.size,(228,226,220,255));expected.alpha_composite(face)
                    expected=expected.convert('RGB').resize((face.width*6,face.height*6),Image.Resampling.NEAREST)
                    for frame_index,position in [(pose['phase'],(x,y)),(1,tuple(box[:2])),(3,tuple(box[:2]))]:
                        gif.seek(frame_index);px,py=position
                        actual=gif.convert('RGB').crop((px*6,py*6,(px+face.width)*6,(py+face.height)*6))
                        assert actual.tobytes()==expected.tobytes(),('GIF changes approved face colors',unit['slug'],frame_index)
        with Image.open(folder / 'movement-sheet.png') as sheet:
            assert sheet.size == (96, 64)
    page = (OUT / 'index.html').read_text(encoding='utf-8')
    links = re.findall(r'(?:href|src)="([^"]+)"', page)
    for link in links:
        assert (OUT / link).is_file(), ('Missing gallery link', link)
    assert count == 50 and len(colors) == 60
    report = dict(result='PASS',units=10,generatedPoseRecords=count,bodyCrops=60,
                  authenticatedFiles=len(checked),galleryLinks=len(links),
                  opaqueColorCounts=colors,
                  limitations='Packaging/provenance only. Generated palettes and aesthetics are not production accepted; no native integration.')
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'opaqueColorCounts'}))


if __name__ == '__main__':
    main()
