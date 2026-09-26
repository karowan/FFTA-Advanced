"""Record exact selected imagegen prompts and hashes without private images."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "build/art/item-drafts"
OUTPUT = ROOT / "src/art/imagegen/new-item-icon-drafts.json"


def main():
    audit = json.loads((DRAFTS / "audit.json").read_text(encoding="utf-8"))
    if audit["status"] != "passed-review-drafts-only" or audit["count"] != 85:
        raise ValueError("Run the complete draft audit before exporting provenance")
    items = []
    for record in audit["records"]:
        metadata = json.loads((DRAFTS / record["folder"] / "draft.json").read_text(encoding="utf-8"))
        items.append({
            "id": record["id"],
            "name": record["name"],
            "donorOriginalIconId": record["donor"],
            "donorOriginalIconSha256": metadata["originalReferenceSha256"],
            "donorPaletteBank": metadata["originalPaletteBank"],
            "tool": metadata["generationTool"],
            "prompt": metadata["prompt"].strip(),
            "rawGenerationSha256": metadata["rawGenerationSha256"],
            "indexedPreviewSha256": metadata["nativePreviewSha256"],
            "nativePixelsSha256": metadata["nativePixelsSha256"],
            "horizontalMirror": metadata["horizontalMirror"],
            "conversion": metadata["conversion"],
        })
    result = {
        "status": "review-drafts-not-approved-or-imported",
        "cleanRomSha1": "4ac05441f4de70a4ec3dd932116346c61b8783d9",
        "count": len(items),
        "items": items,
        "scope": "Text and hashes only. Original game images and raw generated PNGs remain private ignored inputs; no ROM import or visual approval is claimed.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "count": result["count"], "path": str(OUTPUT)}))


if __name__ == "__main__":
    main()
