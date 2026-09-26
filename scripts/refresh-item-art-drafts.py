"""Rebuild selected review previews from immutable raw generations and prompts."""

import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "build/art/item-drafts"
ORIGINALS = ROOT / "build/art/native-reference/equipment-original"


def main():
    profiles = json.loads((ROOT / "build/expansion/probes/content-data.json").read_text(encoding="utf-8"))["itemProfiles"]
    by_id = {str(item["id"]): item for item in profiles}
    selected = json.loads((DRAFTS / "selection.json").read_text(encoding="utf-8"))
    if len(by_id) != 85 or set(by_id) != set(selected):
        raise ValueError("Selection must cover all 85 new weapons")
    prepare = runpy.run_path(str(ROOT / "scripts/prepare-item-icon-draft.py"))["prepare"]
    for item_id, folder in sorted(selected.items(), key=lambda pair: int(pair[0])):
        item = by_id[item_id]
        directory = DRAFTS / folder
        if directory.resolve().parent != DRAFTS.resolve():
            raise ValueError(f"Selection escapes draft directory: {folder}")
        prior = json.loads((directory / "draft.json").read_text(encoding="utf-8"))
        if prior["itemId"] != int(item_id) or not prior["itemName"].startswith(item["name"]):
            raise ValueError(f"Draft identity mismatch: {item_id}")
        prompt = prior["prompt"]
        prompt_path = directory / "prompt.txt"
        if prompt_path.exists() and prompt_path.read_text(encoding="utf-8").strip() != prompt.strip():
            raise ValueError(f"Prompt changed: {item_id}")
        prompt_path.write_text(prompt.rstrip() + "\n", encoding="utf-8")
        refreshed = prepare(directory / "raw.png", ORIGINALS / f'icon-{item["donor"]:03}.png',
                            directory, int(item_id), item["name"], prompt,
                            prior.get("horizontalMirror", False))
        refreshed.update({key: value for key, value in prior.items() if key not in refreshed})
        if prior["itemName"] != item["name"]:
            refreshed["variantLabel"] = prior["itemName"]
        (directory / "draft.json").write_text(json.dumps(refreshed, indent=2) + "\n",
                                              encoding="utf-8")
    print(json.dumps({"status": "refreshed-review-drafts", "count": len(selected)}))


if __name__ == "__main__":
    main()
