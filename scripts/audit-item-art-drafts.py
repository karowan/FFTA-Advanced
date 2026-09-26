"""Audit selected generated item-icon drafts without accepting or importing them."""

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image
from native_art import pack_tiles


ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "build/art/item-drafts"
ORIGINALS = ROOT / "build/art/native-reference/equipment-original"
PROFILES = ROOT / "build/expansion/probes/content-data.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))["itemProfiles"]
    expected = {str(item["id"]): item for item in profiles}
    selected = json.loads((DRAFTS / "selection.json").read_text(encoding="utf-8"))
    if len(expected) != 85 or set(selected) != set(expected):
        raise ValueError("Selection must cover exactly the 85 new item IDs")
    original_report = json.loads((ORIGINALS / "report.json").read_text(encoding="utf-8"))
    if original_report["sourceSha1"] != "4ac05441f4de70a4ec3dd932116346c61b8783d9":
        raise ValueError("Original icon export is not authenticated")
    by_index = {entry["index"]: entry for entry in original_report["records"]}
    records = []
    by_family = defaultdict(list)
    by_pixels = defaultdict(list)
    for item_id, folder in sorted(selected.items(), key=lambda pair: int(pair[0])):
        item = expected[item_id]
        directory = DRAFTS / folder
        if directory.resolve().parent != DRAFTS.resolve():
            raise ValueError(f"Selection escapes draft directory: {folder}")
        metadata = json.loads((directory / "draft.json").read_text(encoding="utf-8"))
        raw, preview, prompt_path = (directory / name for name in ("raw.png", "native-preview.png", "prompt.txt"))
        donor = item["donor"]
        original = ORIGINALS / f"icon-{donor:03}.png"
        if not all((
            metadata["itemId"] == int(item_id),
            metadata["itemName"] == item["name"],
            metadata["status"] == "review-draft-not-approved-or-imported",
            metadata["originalReferenceId"] == donor,
            metadata["originalReferenceSha256"] == sha(original) == by_index[donor]["pngSha256"],
            metadata["originalPaletteBank"] == by_index[donor]["paletteBank"],
            metadata["cleanRomSha1"] == original_report["sourceSha1"],
            metadata["rawGenerationSha256"] == sha(raw),
            metadata["nativePreviewSha256"] == sha(preview),
            metadata["prompt"].strip() == prompt_path.read_text(encoding="utf-8").strip(),
            metadata["generationTool"] == "built-in image_gen",
        )):
            raise ValueError(f"Provenance mismatch for item {item_id}")
        icon = Image.open(preview)
        if (icon.mode != "P" or icon.size != (16, 16) or
                icon.info.get("transparency") != 0 or
                icon.getpalette()[:48] != Image.open(original).getpalette()[:48]):
            raise ValueError(f"Native format mismatch for item {item_id}")
        pixels = pack_tiles(icon, 4)
        if len(pixels) != 128 or metadata["nativePixelsSha256"] != hashlib.sha256(pixels).hexdigest():
            raise ValueError(f"Native pixel hash mismatch for item {item_id}")
        by_pixels[metadata["nativePixelsSha256"]].append(int(item_id))
        by_family[donor].append((int(item_id), list(icon.get_flattened_data())))
        records.append({
            "id": int(item_id), "name": item["name"], "donor": donor,
            "folder": folder, "rawSha256": metadata["rawGenerationSha256"],
            "nativePixelsSha256": metadata["nativePixelsSha256"],
            "horizontalMirror": metadata["horizontalMirror"],
        })
    duplicates = [ids for ids in by_pixels.values() if len(ids) > 1]
    if duplicates:
        raise ValueError(f"Duplicate native icon pixels: {duplicates}")
    closest = []
    for donor, icons in sorted(by_family.items()):
        for offset, (left_id, left) in enumerate(icons):
            for right_id, right in icons[offset + 1:]:
                changed = sum(a != b for a, b in zip(left, right))
                closest.append((changed, donor, left_id, right_id))
    closest.sort()
    result = {
        "status": "passed-review-drafts-only",
        "count": len(records),
        "families": {str(donor): len(icons) for donor, icons in sorted(by_family.items())},
        "closestPairsByChangedPixels": [
            {"changedPixels": count, "donor": donor, "items": [left, right]}
            for count, donor, left, right in closest[:20]
        ],
        "records": records,
        "scope": "Authenticated original references, exact prompts/raw/native hashes, 16x16 palette/index format and no byte-identical selected icons. Visual approval and final-ROM consumers remain pending.",
    }
    (DRAFTS / "audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "count": result["count"], "families": result["families"], "closest": result["closestPairsByChangedPixels"][:5]}))


if __name__ == "__main__":
    audit()
