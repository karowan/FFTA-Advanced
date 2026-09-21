# Generated projectile and primary impact transport

September 17, 2026. User direction remains technical integration first, final
sprite refinement afterward. Built-in imagegen only. No external API, council,
publication, visible game launch or player-save/session changes.

## Projectile acceptance

`test-generated-projectile` constructs a native encounter from the authenticated
shipping world checkpoint using current be82fceecd0f05d9935091f3f2400c6ebacfa2c3.
Marche keeps his named identity and gets the legitimate Soldier command, axe454
and Tomahawk learning as declared disposable inputs before battle allocation.
Original menu selection, targeting, action execution and next turn remain native.
The control changes only the equipment-icon dispatcher pointer to its previous
implementation; held weapons and gameplay bytes remain identical.

Runner20260917T233318.964973Z failed a test field assertion before projectile
playback. The screenshot already selected Tomahawk correctly. Manager+16 is a
choice field; +20 is the action ID. Correcting that assertion gives52 passing
checks in233434.673903Z. Report and captures:
`build/art/generated-projectile/20260917T233435.237211Z/report.json`.
Both outcomes are18 damage,12MP after4MP payment,8EXP, no gear/inventory/AP
changes and a native following turn. The generated axe moves through actual
visible hardware OAM with exact tiles and palette8; held weapon palettes0/6
cannot satisfy the projectile oracle. Actual captures were visually inspected.
This accepts the current Throw-derived projectile path, not every projectile.

## Native impact format and original references

Throw animation145 callback080FE2E9 loads its four resource records through
the pointer at FE36C to39D844. Primary impact resource39D82C points at912E78,
with header0202FD7F and BIOS LZ data. Native D758C decompresses to scratch;
D7674 invokes D6F64 to expand2bpp to4bpp. The27-tile864-byte atlas is uploaded
to OBJ VRAM17C80..17FE0. Native2bpp expansion clears one terminal staging byte;
tests measure that explicit slack, with guards beyond it.

Layout4FE8B0 holds flags0C, a relative control offset5C and four relative OAM
offsets8/34/60/86. Three poses each arrange16x16,8x16,16x8 and8x8 objects into
a24x24 square; the fourth pose is empty. Source palette8EA7F0 has7 phases of
3 opaque colors, animated through hardware bank6. Other secondary resources
and timings remain original and are not falsely included in primary acceptance.

`test-native-effect-format` passes29 checks in234110.366007Z, verifying clean
source identity, current-candidate equality, lossless4bpp container encoding,
the actual native2bpp expansion at both stack residues, and retained actual
DMA/palette equality. Original reference exports include all21 frame/phase
combinations. Report:
`build/art/native-effect-format/20260917T234110.882381Z/report.json`.

## Generated primary impact

Built-in imagegen produced a new three-frame slash/burst/dissipation sheet.
The exact prompt, tool designation, default-setting disclosure and source hash
are in `src/art/imagegen/impact-transport-prompts.json`. Private source:
`build/art/imagegen/effects/impact-transport-v1.png`, SHA256
35a0dbd5701347d4c973ed702e105ecf6ea4b5c53f2e515906d90c2a43acfb63.
No hand-authored replacement pixels. Conversion uses equal cells, a common
nearest-neighbor scale to24px, alpha threshold128 and the three native colors;
original OAM determines tile packing. This is temporary transport art.

`generated_effect_transport.py` uses1,076 bytes within1F88000..1F8C000. It adds
a4bpp LZ atlas, private graphic reference, copied resource list and selector.
The8-byte FE358 hook replaces only its authenticated native instructions.
The selector reads action-context+10h, selecting the new list only for425;
every other action retains39D844. Original table, original Throw art and all
other source resources are preserved. Stolen stack stores and live registers
are verified; r0 is dead at the preserved FE360 continuation instruction.

Latest candidate **a6d883b5d7657f10c3eb6d9b8407c489d287dbc7** is private at
`build/art/generated-effect/current.json`. Runner234709.326823Z passes:

- `test-generated-effect-native`:3,707 checks, all461 action IDs plusFFFF at
  two stack residues, installed hook/continuation, registers/stores/canaries,
  native resource-loader stages with an explicitly emulated BIOS LZ peripheral,
  original-resource preservation and exact generated build reproduction.
- `test-generated-effect-battle`:42 checks, paired actual original/generated
  primary effect, all three displayed OAM poses, exact VRAM atlas, native palette
  cycling,18damage/4MP/no storage mutation and next turn. Uses the previously
  accepted current-parent confirmation before any effect allocation, retaining
  its report/seed hashes and checking exact RAM. No title/deployment replay.

Reports:
`build/art/generated-effect/native-tests/20260917T234709.865790Z/report.json`
and `build/art/generated-effect/battle/20260917T234713.036225Z/report.json`.
Actual impact screenshots and the24px conversion were visually inspected.
The native palette deliberately changes the cyan source burst to warm impact
colors during playback. This is preserved behavior, not a color fidelity claim.

## Remaining work

The effect primary path is now proven separately from body, held weapon,
projectile, portrait, miniature, menu and status paths. This does not establish
every spell/background effect format, other action families, custom actor
palettes or finished animation. Continue actor palette integration and remaining
affected consumers, plus repaired-data consumer classification/native map
playback, before assembled technical delivery. All G gates stay open; final art
remains deferred. No launcher/package or installed game has been updated here.
