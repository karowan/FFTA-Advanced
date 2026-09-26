"""Create a private visual comparison of original, raw, and native icon drafts."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "build/art/native-reference/equipment-original"
DRAFTS = ROOT / "build/art/item-drafts"
PILOT_ROWS = [
    (376, "Ashura Echo", 106, "376-ashura-echo-retry"),
    (384, "Gloom Sword", 1, "384-gloom-sword"),
    (392, "Storm Axe", 52, "392-storm-axe"),
    (400, "Ember Saber", 32, "400-ember-saber"),
    (408, "Tonic Knife", 74, "408-tonic-knife"),
    (416, "Minuet Foil", 88, "416-minuet-foil"),
    (424, "Etude Pipe", 201, "424-etude-pipe"),
    (432, "Stone Rod", 135, "432-stone-rod-retry"),
]
PIPE_ROWS = [(item_id, name, 201, folder) for item_id, name, folder in (
    (424, "Etude Pipe", "424-etude-pipe"),
    (425, "Battle Pipe", "425-battle-pipe"),
    (426, "Refrain Pipe", "426-refrain-pipe"),
    (427, "Requiem Pipe", "427-requiem-pipe"),
    (428, "Angel Pipe", "428-angel-pipe"),
    (429, "Traveler Pipe", "429-traveler-pipe"),
    (430, "Ballad Pipe", "430-ballad-pipe"),
    (431, "Nameless Pipe", "431-nameless-pipe"),
)]
ROD_ROWS = [(item_id, name, 135, folder) for item_id, name, folder in (
    (432, "Stone Rod", "432-stone-rod-retry"),
    (433, "Root Rod", "433-root-rod"),
    (434, "River Rod", "434-river-rod"),
    (435, "Zephyr Rod", "435-zephyr-rod"),
    (436, "Wardstone Rod", "436-wardstone-rod"),
    (437, "Wisp Rod", "437-wisp-rod"),
    (438, "Rime Rod", "438-rime-rod"),
    (439, "Gaia Rod", "439-gaia-rod"),
    (449, "Refuge Rod", "449-refuge-rod"),
)]
SETS = {"pilot": PILOT_ROWS, "pipes": PIPE_ROWS, "rods": ROD_ROWS}


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
    if selection != "all":
        render(SETS[selection], DRAFTS / f"review-{selection}.png")
        return
    profiles = json.loads((ROOT / "build/expansion/probes/content-data.json").read_text(encoding="utf-8"))["itemProfiles"]
    selected = json.loads((DRAFTS / "selection.json").read_text(encoding="utf-8"))
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
