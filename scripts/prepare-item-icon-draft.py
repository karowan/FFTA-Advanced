"""Make review-only native-palette previews from generated equipment icon drafts."""

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from PIL import Image
from native_art import pack_tiles


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(source, reference, output, item_id, name, prompt, mirror=False):
    output.mkdir(parents=True, exist_ok=True)
    report_path = reference.parent / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("status") != "passed" or report.get("sourceSha1") != "4ac05441f4de70a4ec3dd932116346c61b8783d9":
        raise ValueError("Original icon report is not from the authenticated clean ROM")
    reference_id = int(reference.stem.split("-")[-1])
    entry = next((record for record in report["records"] if record["index"] == reference_id), None)
    if entry is None or entry["pngSha256"] != digest(reference):
        raise ValueError("Original reference PNG does not match the authenticated export")
    original = Image.open(reference)
    if original.mode != "P" or original.size != (16, 16) or original.info.get("transparency") != 0:
        raise ValueError("Expected an authenticated indexed 16x16 original icon")
    colors = original.getpalette()[:48]
    if len(colors) != 48:
        raise ValueError("Original icon does not expose a complete 16-color palette")
    native_hex = {
        index: f"#{colors[index * 3]:02X}{colors[index * 3 + 1]:02X}{colors[index * 3 + 2]:02X}"
        for index in range(1, 16)
    }
    requested_hex = {value.upper() for value in re.findall(r"#[0-9A-Fa-f]{6}", prompt)}
    if requested_hex - set(native_hex.values()):
        raise ValueError("Prompt requests a color outside the authenticated native palette")
    allowed_indices = [
        index for index, value in native_hex.items()
        if not requested_hex or value in requested_hex
    ]
    if not allowed_indices:
        raise ValueError("Prompt does not permit an opaque native palette color")
    image = Image.open(source).convert("RGBA")
    bounds = image.getchannel("A").point(lambda value: 255 if value >= 128 else 0).getbbox()
    if bounds is None:
        raise ValueError("Generated draft is fully transparent")
    cropped = image.crop(bounds)
    if mirror:
        cropped = cropped.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    cropped.thumbnail((14, 14), Image.Resampling.BOX)
    raw_path = output / "raw.png"
    if source.resolve() != raw_path.resolve():
        shutil.copyfile(source, raw_path)
    indexed = Image.new("P", (16, 16), 0)
    indexed.putpalette(colors + [0] * (768 - len(colors)))
    indexed.info["transparency"] = 0
    left = (16 - cropped.width) // 2
    top = (16 - cropped.height) // 2
    for y in range(cropped.height):
        for x in range(cropped.width):
            red, green, blue, alpha = cropped.getpixel((x, y))
            if alpha < 128:
                continue
            choice = min(allowed_indices, key=lambda index: sum(
                (channel - colors[index * 3 + offset]) ** 2
                for offset, channel in enumerate((red, green, blue))
            ))
            indexed.putpixel((left + x, top + y), choice)
    if not indexed.getbbox():
        raise ValueError("No opaque native pixels survived conversion")
    native_pixels = pack_tiles(indexed, 4)
    if len(native_pixels) != 128:
        raise ValueError("Native icon must pack to four 4bpp tiles")
    preview_path = output / "native-preview.png"
    indexed.save(preview_path, bits=4, transparency=0)
    decoded = Image.open(preview_path)
    if (decoded.mode != "P" or decoded.size != (16, 16) or
            decoded.info.get("transparency") != 0 or
            decoded.getpalette()[:48] != colors or
            pack_tiles(decoded, 4) != native_pixels):
        raise ValueError("Saved PNG does not round-trip to the selected native pixels")
    enlarged = indexed.convert("RGBA").resize((256, 256), Image.Resampling.NEAREST)
    enlarged.save(output / "native-preview-16x.png")
    record = {
        "status": "review-draft-not-approved-or-imported",
        "itemId": item_id,
        "itemName": name,
        "generationTool": "built-in image_gen",
        "prompt": prompt,
        "originalReference": str(reference),
        "originalReferenceId": reference_id,
        "originalReferenceSha256": digest(reference),
        "originalPaletteBank": entry["paletteBank"],
        "cleanRomSha1": report["sourceSha1"],
        "rawGenerationSha256": digest(raw_path),
        "nativePreviewSha256": digest(preview_path),
        "nativePixelsSha256": hashlib.sha256(native_pixels).hexdigest(),
        "rawSize": list(image.size),
        "alphaBounds": list(bounds),
        "croppedScale": list(cropped.size),
        "horizontalMirror": mirror,
        "allowedPaletteColors": [native_hex[index] for index in allowed_indices],
        "conversion": "alpha>=128; crop alpha bounds; optional horizontal mirror; BOX fit within 14x14; center in 16x16; nearest RGB among prompt-listed original palette colors, or indices 1..15 when none are listed",
    }
    (output / "draft.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--item-id", type=int, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--mirror", action="store_true")
    arguments = parser.parse_args()
    print(json.dumps(prepare(arguments.source, arguments.reference, arguments.output,
                             arguments.item_id, arguments.name,
                             arguments.prompt_file.read_text(encoding="utf-8"),
                             arguments.mirror)))
