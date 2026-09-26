"""Create a private visual comparison of original, raw, and native icon drafts."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "build/art/native-reference/equipment-original"
DRAFTS = ROOT / "build/art/item-drafts"
SETS = {
    "pilot": {376, 384, 392, 400, 408, 416, 424, 432},
    "pipes": set(range(424, 432)),
    "rods": {*range(432, 440), 449},
}


def paste_icon(page, source, x, y, size, method):
    icon = Image.open(source).convert("RGBA")
    icon.thumbnail((size, size), method)
    if method == Image.Resampling.NEAREST:
        icon = Image.open(source).convert("RGBA").resize((size, size), method)
    plate = Image.new("RGBA", (size, size), (45, 48, 55, 255))
    plate.alpha_composite(icon, ((size - icon.width) // 2, (size - icon.height) // 2))
    page.alpha_composite(plate, (x, y))


def render(rows, destination):
    width, row_height = 780, 176
    page = Image.new("RGBA", (width, 48 + len(rows) * row_height), "#eeeeee")
    draw = ImageDraw.Draw(page)
    draw.text((18, 14), "NEW ITEM ART — ORIGINAL REFERENCE / RAW IMAGEGEN / 16x16 NATIVE PREVIEW", fill="#222222")
    for index, (item_id, name, donor, folder) in enumerate(rows):
        y = 48 + index * row_height
        draft = DRAFTS / folder
        for file_name in ("raw.png", "native-preview.png", "draft.json"):
            if not (draft / file_name).is_file():
                raise FileNotFoundError(draft / file_name)
        draw.text((18, y + 10), f"{item_id} {name}", fill="#222222")
        draw.text((18, y + 30), f"Original {donor:03}", fill="#555555")
        paste_icon(page, REFS / f"icon-{donor:03}.png", 175, y + 10, 128, Image.Resampling.NEAREST)
        paste_icon(page, draft / "raw.png", 352, y + 10, 128, Image.Resampling.LANCZOS)
        paste_icon(page, draft / "native-preview.png", 529, y + 10, 128, Image.Resampling.NEAREST)
        draw.text((174, y + 143), "Original", fill="#555555")
        draw.text((351, y + 143), "Raw draft", fill="#555555")
        draw.text((528, y + 143), "Native palette", fill="#555555")
    page.convert("RGB").save(destination)
    print(destination)


def main(selection):
    profiles = json.loads((ROOT / "build/expansion/probes/content-data.json").read_text(encoding="utf-8"))["itemProfiles"]
    selected = json.loads((DRAFTS / "selection.json").read_text(encoding="utf-8"))
    if selection != "all":
        rows = [
            (item["id"], item["name"], item["donor"], selected[str(item["id"])])
            for item in profiles if item["id"] in SETS[selection]
        ]
        render(rows, DRAFTS / f"review-{selection}.png")
        return
    families = {}
    for item in profiles:
        families.setdefault(item["donor"], []).append((
            item["id"], item["name"], item["donor"], selected[str(item["id"])],
        ))
    for donor, rows in sorted(families.items()):
        render(rows, DRAFTS / f"review-family-{donor:03}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("selection", choices=[*SETS, "all"])
    main(parser.parse_args().selection)
