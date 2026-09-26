"""Apply the pub acceptance return fix to the accepted v0.7.3 ROM."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT_SHA256 = '4b972fc6d4c6db712c1c026e4c951228cf89bb8b6c6d54bd3411f11c87033eb3'
PARENT = ROOT / 'build/play-cache' / PARENT_SHA256 / 'FFTA_Reviewed_All_Classes.gba'
OFFSET = 0x5D76C
OLD = b'\x01\x20'  # movs r0, #1: original Missions action, now Rumors
NEW = b'\x00\x20'  # movs r0, #0: reordered Missions action


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parent = PARENT.read_bytes()
    assert len(parent) == 0x2000000 and sha256(parent) == PARENT_SHA256
    assert parent[OFFSET:OFFSET + len(OLD)] == OLD
    rom = bytearray(parent)
    rom[OFFSET:OFFSET + len(NEW)] = NEW
    changed = [i for i, (a, b) in enumerate(zip(parent, rom)) if a != b]
    assert changed == [OFFSET]
    dest = ROOT / 'build/expansion/probes/pub-return/candidate'
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / 'FFTA_Reviewed_All_Classes.gba'
    path.write_bytes(rom)
    manifest = dict(path=str(path), romSha1=hashlib.sha1(rom).hexdigest(), romSha256=sha256(rom),
                    pubReturn=dict(parent=str(PARENT), parentSha256=PARENT_SHA256,
                                   offset=OFFSET, old=OLD.hex(), new=NEW.hex(), changedBytes=changed))
    manifest_path = dest / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(status='passed', romSha1=manifest['romSha1'], manifest=str(manifest_path))))


if __name__ == '__main__':
    main()
