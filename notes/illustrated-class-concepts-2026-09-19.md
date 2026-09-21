# Illustrated class concepts, 2026-09-19

The user clarified that class concepts mean full character illustrations matched
to the original game's concept art. Costume review precedes sprite adaptation.
The preceding sprite-concept preparation is superseded, not accepted artwork.

Created one full-body illustrated draft for each of the ten new racial class
options: Human Samurai/Dark Knight, Bangaa Viking/Dark Knight, Nu Mou
Chemist/Geomancer, Moogle Chemist/Bard, Viera Dancer/Mystic Knight.

## Inputs and process

Original FFTA illustrations were retrieved from Creative Uncut's
[FFTA art gallery](https://www.creativeuncut.com/art_final-fantasy-tactics-advance_a.html):
[Human Paladin](https://www.creativeuncut.com/gallery-01/ffta-h-paladin.html),
[Human Fighter](https://www.creativeuncut.com/gallery-01/ffta-h-fighter.html),
[Bangaa](https://www.creativeuncut.com/gallery-01/ffta-bangaa.html),
[Nu Mou](https://www.creativeuncut.com/gallery-01/ffta-nu-mou.html),
[Moogle](https://www.creativeuncut.com/gallery-01/ffta-moogle.html), and
[Viera](https://www.creativeuncut.com/gallery-01/ffta-viera.html).

Each built-in imagegen call used its race's original illustration as a visual
reference; Human calls used both Human illustrations. The prompt asks for an
original class illustration matching the ink linework, simple shaded colors,
racial anatomy and proportions, followed by a short costume/prop description.
Only prompt and reference paths were specified. The model version and remaining
settings were tool-managed and not exposed. No sprite or prior generated image
was used as a concept-generation input.

The [generation manifest](../src/art/race-study/illustrated-class-concepts-v1.json)
preserves every exact prompt, source page/image URL, local reference path, input
hash and output path/hash. The original outputs remain untouched.

## Review files

Private illustrations and references are saved under
`build/art/illustrated-class-concepts-2026-09-19/`.
`index.html` provides labeled full-size image links; `all-ten-concepts.jpg` is
the comparison sheet. Each class also has its own `<race>-<class>.png`.

Run `python scripts/package-class-illustrations.py` with Pillow to regenerate
the gallery, verify all ten PNGs and source hashes, and update output provenance.
This performs thumbnail/layout packaging only, without painting or changing art.

## Review status

All ten illustrations were visually inspected. The distinct race proportions,
ears, muzzles, tails and pom-poms follow the supplied illustrations. Class
costumes and props are present, and full characters fit their canvases. Armor
and accessories have more surface detail and texture than the reference art;
this is a simplification candidate for the next design revision, not a claim
of an exact style match. User selection/approval remains pending.

These are illustrated design drafts only. No sprite conversion, native import,
animation work, build or runtime test is implied by this delivery.
