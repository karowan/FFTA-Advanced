"""User-authorized exact face reuse; no new pixels or colors are authored.

Run once to preserve v5 and apply the approved region. Later runs verify it.
"""
import copy
import json
import runpy
import shutil
from pathlib import Path
from PIL import Image

H = runpy.run_path(str(Path(__file__).with_name('assemble-class-animation.py')))
ROOT, OUT = H['ROOT'], H['OUT']
RECORD = ROOT / 'src/art/race-study/samurai-face-correction-v6.json'


def verify(output, original, source, box, position):
    after = Image.open(output).convert('RGBA')
    before = Image.open(original).convert('RGBA')
    face = Image.open(source).convert('RGBA').crop(tuple(box))
    x, y = position
    target = (x, y, x + face.width, y + face.height)
    assert after.crop(target).tobytes() == face.tobytes(), 'Face differs from approved pixels'
    changed = 0
    for py in range(after.height):
        for px in range(after.width):
            if not (target[0] <= px < target[2] and target[1] <= py < target[3]):
                assert after.getpixel((px, py)) == before.getpixel((px, py)), ('Outside face changed', px, py)
            changed += after.getpixel((px, py)) != before.getpixel((px, py))
    return dict(faceExact=True, outsideRegionChangedPixels=0, changedPixels=changed,
                sourceBox=box, targetBox=list(target))


def main():
    record = json.loads(RECORD.read_text())
    recipe = record['proposedReuse']
    source = ROOT / recipe['source']
    assert H['sha'](source) == recipe['sha256']
    face = Image.open(source).convert('RGBA').crop(tuple(recipe['sourceBox']))
    m = H['read']()
    unit = next(u for u in m['units'] if u['slug'] == 'human-samurai')
    checks = {}
    for pose in unit['poses']:
        if pose['id'] not in recipe['targets']:
            continue
        output = ROOT / pose['output']
        archive = output.with_name(pose['id'] + '-before-face-v6.png')
        position = recipe['targets'][pose['id']]
        if pose.get('consistencyRevision', 0) < 6:
            assert not archive.exists(), 'Archive already exists; inspect interrupted operation'
            old = copy.deepcopy(pose)
            shutil.copy2(output, archive)
            old['output'] = str(archive.relative_to(ROOT))
            im = Image.open(output).convert('RGBA')
            im.paste(face, tuple(position))  # Exact RGBA replacement, not alpha blending.
            im.save(output)
            pose.update(previousGeneration=old, consistencyRevision=6,
                        outputSha256=H['sha'](output),
                        mechanicalCorrection=dict(operation='exact-rgba-region-reuse',
                            source=recipe['source'], sourceSha256=recipe['sha256'],
                            sourceBox=recipe['sourceBox'], position=position,
                            before=str(archive.relative_to(ROOT)), beforeSha256=H['sha'](archive),
                            authorization='User: yes do whatever you need to, in response to exact-face-pixel reuse request'))
        checks[pose['id']] = verify(output, archive, source, recipe['sourceBox'], position)
    H['save'](m)
    record.update(status='Applied and verified: user-authorized exact face reuse',
                  authorization='User explicitly approved copying the existing face pixels with code.',
                  verification=checks)
    RECORD.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(checks))


if __name__ == '__main__':
    main()
