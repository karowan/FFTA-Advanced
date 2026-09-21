"""Compose unchanged private native reference pixels; never draw character art."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/art/race-study-2026-09-19'
RACES = {'human': 4, 'bangaa': 13, 'nu-mou': 25, 'moogle': 39, 'viera': 29}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    overview = Image.new('RGBA', (96, 64 * 5), '#dddddd')
    for n, (race, actor) in enumerate(RACES.items()):
        folder = ROOT / f'build/art/native-reference/actor-{actor:03}'
        native = json.loads((folder / 'native.json').read_text())
        board = Image.new('RGBA', (96, 64))
        frames = []
        for row, slot in enumerate([0, 1]):
            for col, frame in enumerate(native['slots'][slot]['frames'][:3]):
                path = folder / (frame['pose'] + '-pose.png')
                source = Image.open(path).convert('RGBA')
                cropped = source.crop((32, 28, 64, 60))
                bbox = source.getbbox()
                assert bbox and bbox[0] >= 32 and bbox[1] >= 28 and bbox[2] <= 64 and bbox[3] <= 60, (race, bbox)
                board.alpha_composite(cropped, (col * 32, row * 32))
                frames.append(dict(row=row+1, column=col+1, slot=slot, frame=col,
                    source=str(path.relative_to(ROOT)), sourceSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    pose=frame['pose'], duration=frame['duration'], command=frame['command'],
                    crop=[32,28,64,60], bbox=cropped.getbbox()))
        board.save(OUT / f'{race}-reference-native.png')
        board.resize((1536,1024),Image.Resampling.NEAREST).save(OUT / f'{race}-reference-16x.png')
        overview.alpha_composite(board, (0,n*64))
        records.append(dict(race=race, actor=actor, frames=frames,
            sourceManifestSha256=hashlib.sha256((folder/'native.json').read_bytes()).hexdigest(),
            nativeSequence=[dict(slot=s,frames=native['slots'][s]['frames']) for s in [0,1]]))
    overview.resize((576,1920),Image.Resampling.NEAREST).save(OUT/'references-overview.png')
    (OUT/'reference-manifest.json').write_text(json.dumps(dict(scope='Private unmodified reference crops. Export preview palettes are style references, not verified per-job colors.',races=records),indent=2)+'\n')
    print(OUT)

if __name__ == '__main__':
    main()
