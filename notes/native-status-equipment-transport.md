# Status/equipment transport and native data repair — September17

Latest private child: `37afe0a7be1b80355d395d3d10685a9034b123d1`, resolved
through `build/art/native-repair-complete/current.json`. Nothing installed or
launched; vanilla, release, player saves and running sessions are untouched.
Built-in imagegen only. Final artwork remains deferred; all G gates stay open.

## Separate generated consumers

`generated_status_transport.py` extends action candidate714f45eb to
`d0629836319f42b0a6201011b0dec990a6f120ca`. Only128 bytes at ROM110653c
change: two8x16 Exposed/Centered glyphs. Original native bank0 at419d60,
selectors, shape, status timing, gameplay and other glyphs remain exact.
Imagegen source/prompt hashes are in src/art/imagegen/status-transport-prompts.json.
No coded/manual artwork. Actual battle evidence uses controlled custom statuses
plus native Protect; it does not repeat status grant/expiry gameplay acceptance.

Declared test-generated-status passes201 checks in runner222746.259521Z;
report `build/art/generated-status/tests/20260917T222746.891968Z/report.json`.
All56 renderer outputs, exact rebuild, actual hardware OAM/palette/upload,
cycling/removal, full paired EWRAM/palette/OAM, bounded VRAM difference and
unchanged source fixture pass. Root inspected the actual status captures.

`generated_equipment_transport.py` extends that candidate to
`377330c4c16a1c8d3352bf6ae748f45a4fc90a00`. It appends337 bytes in owned
ROM1f80000..1f84000 and redirects CB984; no persistent RAM. A generated16x16
axe goes through native A7 decode only for item453..460 at six verified equipment/
projectile callers and equipment shop mode4. Quest/mystery modes5/6 and generic
calls retain their namespace. Palette selection remains native; held weapon art
and actual projectile playback are separate, still-open consumers. Source/prompt
hashes are in src/art/imagegen/axe-transport-prompts.json. The palette-constrained
conversion is a temporary technical asset, not accepted art for eight weapons.

test-generated-equipment-native passes5,131 checks in223543.318930Z;
report `build/art/generated-equipment/tests/20260917T223543.858427Z/report.json`.
461 IDs at six callers plus shop modes, ABI/destination guards, unchanged palette
API and exact rebuild pass. Its generic archive coverage was520/522, with the
two failed entries explicitly skipped. The old report's explanation of those
entries as malformed originals is WRONG; see the corruption findings below.

Actual paired Inventory/Buy/Sell proof totals27 checks in223851.560899Z;
report `build/art/generated-equipment/tests/20260917T223852.105300Z/report.json`.
Inventory and Buy reuse complete results in failed223706.865550Z authenticated
by SHA256c7bd766b3986a43c5bb13d0cb418ac9b814b6c8cb30a9fd40b25ef18f6d69631.
Only Sell reran with the corrected tab input. All three show the complete opaque
icon on the actual native-resolution screen, exact VRAM payload and identical
paired owned unit/inventory/AP state. Viewing performs no transaction. Private
early-town seed SHA1b0199e7490f7c22f84512825a4a1bde08d3b3eec is unchanged.

Failures remain retained: native223426 stopped at record467; UI223546 used an
incorrect green-channel screen oracle; UI223706 completed Inventory/Buy then
selected the wrong Sell tab. libretro RGB565 expands GBA green as
`g5*2*255//63`, unlike red/blue`v5*255//31`. The exact corrected oracle has no
color tolerance. Sell needs one Right to weapons; Buy needs two. Initial compile
attempt rejected an incorrectly transcribed ABI prologue before any ROM write.

## Real preexisting corruption discovered, not an original-game limitation

The clean-ROM exporter failed224020.303998Z because its assertion incorrectly
expected the same two invalid records. Clean SHA1
`4ac05441f4de70a4ec3dd932116346c61b8783d9` actually has522 valid records.
Do not change old failed/pass artifacts to erase this mistaken interpretation.

Shipping1b070824's integration manifest records139 false table relocations in
native data, in addition to30 genuine native literals. All139 recorded preimages
equal clean original bytes and were unchanged in the common upstream image.
The broad aligned-word scan rewrote compressed/data tokens that happened to
match expansion table addresses. Examples3d26dc and3d2780 broke equipment/quest
records467/469. Six changed bytes there are part of399 changed bytes overall.
These errors predate all current art work. Other affected data is spread across
14f980..a1a2fc; this is not just a two-icon defect or merely a new image converter
problem. Full consumer classification and assembled regression remain necessary.

`native_table_literals.py` lists30 authentic clean Thumb LDR instructions and
their literal/table values. The integrated builder uses that provenance for
native sites and existing ELF mapping/object provenance for compiled modules.
Unregistered unchanged native data is preserved. An unregistered word changed
upstream, or a changed load instruction, fails closed for explicit review.
A raw LDR-pattern search is insufficient: even the corrupted icon region has
a coincidental LDR-shaped token pointing at3d2780. No guessed code cutoff is used.

`repair-native-table-collisions.py` authenticates the immutable shipping manifest
(SHA2565133b37443b6112ffacccf85b5754e14cfda5f13ba0c457ae17c79e80a140e12),
shipping ROM, clean ROM and377330c4 parent. It restores exactly139 data words,
399 actual bytes, producing `0c7d5fe7c79565727d2c2da63c21f303c9c25661`.
The30 real relocated table references and all other bytes remain exact.

Runner224853.314809Z passes both export-native-equipment-reference (all522
indexed PNG/palette/4bpp roundtrips) and test-native-table-collisions (1,234
checks). Repair report:
`build/art/native-data-repair/tests/20260917T224854.733068Z/report.json`.
The test executes the actual production relocation-loop AST against reversed
recorded native relocations and authenticated upstream table extents. All30
real references survive and all139 false positives stay clean. Fail-closed
controls, complete-ROM delta, exact rebuild, all522 actual native generic icon
decodes and repaired shop quest/mystery consumers pass. Unsafe historical467/469
native decode is not executed; strict Python decoding reproduces their failures.
This is a targeted production-loop proof, not a full clean integration rebuild.

## Inherited copied palette also repaired

Repairing original bytes alone left one decoded copy wrong: large-portrait
color mode1/palette149, copied from original archive3d965c before the repair.
The original corruption was at3dca04. `native_repair_copies.py` rebuilds the
same fixed-length literal archive from clean original palettes plus unchanged
generated palettes. Exactly two further bytes at ROM1dca6ac/1dca6ad change,
producing latest37afe0a7. (The manifest is the authoritative byte-address list.)

test-native-repair-copies passes839 checks in225210.345532Z;
report `build/art/native-repair-complete/tests/20260917T225210.870487Z/report.json`.
No collision intersects copied source extents of the20 new actor resources.
All103 original portrait pixels/OAM,54 original miniatures and495 original
portrait palettes match clean ROM;60 generated palette records stay exact.
Native palette149 and its two neighbors pass in3 color modes and2 stack
alignments with guards. The inherited incorrect palette is a negative control;
exact reproduction and whole-ROM bounded delta pass.

Earlier parent gameplay/screens remain valid evidence for their stated hashes,
not automatic acceptance of37afe0a7 across all139 restored data consumers.
The icon repair evidence remains applicable because the later child changes
only the copied portrait palette. All failures and limitations remain explicit.

## Fresh source assembly and repaired map consumers

Declared rebuild-native-literal-policy passes in225624.478523Z. Fresh isolated
source/tool/clean-ROM assembly completes all8 stages; report
`build/reproducibility/20260917T225624.978478Z/report.json`. Its result is
5065a9eaadd5de1094a38c8724d3d9d308e1194f; the kept workspace contains this
foundation, not the later generated-art stages. No prior build or save was copied.
It is intentionally different from corrupt shipping1b070824. Normal resource
tooling pruned the older reproducibility workspace after preserving its report.

test-native-repaired-data passes87 checks in230044.156917Z; report
`build/art/native-repair-complete/data-tests/20260917T230044.667302Z/report.json`.
It authenticates every build log, production relocation source and final ROM.
Every fresh-build byte equals the repaired shipping base plus the separately
declared preexisting equipment-preview module (4458 differing bytes). All30
genuine native references remain correct; all139 data collisions are preserved.
This closes fresh integration-base assembly/reconciliation. Rebuilding the
complete generated-art chain from that fresh base remains a separate gate.

Eleven false relocations affect15 exact compressed map component consumers:
map0/1/17/18/34/56/57/60/100/101/141/142/151 clipping, and map2/3 arrangement.
The repaired candidate's decoded components equal clean originals. Historical
shipping fails strict LZ77 decoding for map0/1/60, fails arrangement resolution
for map2/3, and produces different clipping bytes for the other ten. This is a
real map-data regression, not just cosmetic damage. These are static data proofs,
not native movement/rendering acceptance on those maps. Other affected data
words still need consumer classification; do not call the scan repair fully
accepted across the game yet.

## Remaining work

Inventory remaining restored data words' consumers and finish assembled validation.
Rebuild the generated-art chain over the fresh isolated integration base. One
known assembly issue must be handled explicitly: the clean integrated builder
already installs equipment_preview, whereas generated_class_transport calls
apply_preview assuming its reservation/hooks are blank/original. Authenticate
and replace that owned earlier preview during generated-art assembly; do not
silently overwrite an arbitrary occupied module or drop the generated portraits.
Complete held weapons/projectiles, effects, custom actor palettes and remaining
affected action families, then assemble the separate technical playable package.
Final animation/sprite artwork and readability acceptance follow that technical
milestone. Do not close G01-G04 or treat the old v0.7 all-clear as current blanket
acceptance after this confirmed corruption discovery. Existing shipping files
remain untouched until a verified replacement is ready.
