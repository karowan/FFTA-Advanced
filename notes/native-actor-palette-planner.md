# Native actor palette ownership and planner

September17,2026 local. Prior f10ef94 was progress: imagegen motion and a concrete
Dark Knight palette mismatch. This continuation implements a freestanding ARM
frame planner/applicator and verifies native renderer semantics. It is not yet
hooked into a game ROM. No artwork was generated; no game launch, package,
player-save/session mutation or publication occurred. All G gates remain open.

## Native contract and retained ownership

Native actor rendering at080216F8 eventually calls08001F34/080014C8. The palette
offset is render-context byte9 plus actor bytes0x1C and0x1D, added modulo16 to
the native layout palette nibble. Context byte10 is priority, not palette.
The relevant writes are at0800166A..1684 (priority) and08001686..1698 (palette).

`test-native-actor-palette` executes the actual renderer against an authenticated
retained Samurai body on ROM0fa7d170. All16 offsets produce the expected palette
nibble while geometry, tile owner, actor object and input context remain exact.
This is a native renderer contract test, not palette allocation or live VBlank.

`test-retained-palette-ownership` reuses50 authenticated menu captures (ten
classes, four wheel phases and reopen). Whole VRAM/OAM/palette hashes are checked
against the passing source report. Exact generated tile payloads identify the
custom actor; the independently decoded8bpp portrait identifies its palette use.
Portrait pixels occupy OBJ color banks6,7,8, regardless of its OAM palette nibble.

All50 custom actors share their original bank with other enabled4bpp objects.
Overwriting their current bank would recolor unrelated displayed graphics.
Banks2,5,9,10,11,13,14,15 are unused across these particular captures, but this
does NOT establish a permanent free-bank reservation or battle/future safety.
Conservative4bpp accounting includes enabled offscreen objects.

Historical capture source ROM75029dea8310b93cd5e462ee7517248c9452fa0a and report:
build/art/generated-portraits/ui/20260917T213052.159909Z/report.json.
This is retained component evidence, not new acceptance of the current package.

## Implemented primitive

`src/engine/art-palette-plan.c` and `.h` implement:

- Full128-entry OAM examination, with caller-authenticated per-object custom
  owner tags. Ordinary4bpp consumers reserve their bank.8bpp consumers reserve
  every bank containing a nonzero color index in their complete tile footprint.
- Deterministic allocation among remaining slots for up to ten distinct custom
  palettes. Multiple objects for one owner reuse that owner's slot.
- Application of exact16-color source palettes and replacement of only the
  palette nibble on owned objects. Tile IDs, priority, geometry and all other
  OAM bytes remain unchanged. Unallocated color banks remain unchanged.
- Refusal without output writes on exhaustion, unsupported2D mapping, invalid
  shape/owner, out-of-bounds8bpp footprint or unsupported custom8bpp object.

The module currently requires1D OBJ mapping and non-affine32x32 4bpp custom
bodies. It has no heap/global state, native hooks or libc dependency. Compiled
ARM module624 bytes, SHA-256:
`5d84ce8287411e28bf5239443be9ca3b70321b1ba12a5b2a5cdff31f6c92b2ca`.

The caller must supply fresh native palette/OAM state and trusted owner tags.
This primitive does not discover actor ownership, restore a previous overlay,
handle color-mode/fade lifetimes, or establish a VBlank cycle budget. It is not
in the assembled build. Do not claim the Dark Knight is correctly colored in
the playable game yet.

## Declared targeted evidence

All invoked through `Test Expansion.ps1 -Plan scripts/native-art-test-plan.json`
with explicit `-Only` selections announced before execution.

| Test ID | Runner | Result / private report |
| --- | --- | --- |
| test-native-actor-palette | 20260918T020302.007900Z |81 passed; build/art/native-palette/20260918T020302.584786Z/report.json |
| test-retained-palette-ownership | 20260918T020302.007900Z |351 passed; build/art/palette-ownership/20260918T020302.811405Z/report.json |
| test-art-palette-plan | 20260918T020824.989236Z |408 passed; build/art/palette-plan/20260918T020825.546191Z/report.json |

Planner/application executes compiled ARM code on all50 retained frames. Each
chooses bank2 based on that frame's demand; this is computed, not hardcoded.
Whole output OAM and palette comparisons prove changes are confined to the
owned nibble and selected bank. Source pixels/tags/colors remain exact. The
Dark Knight's pinned generated palette supplies test colors; these are primitive
contract tests, not visual acceptance of all ten classes with that palette.

Additional explicit isolated inputs verify two simultaneous owners and seven
fail-closed cases, including8bpp occupancy of all16 banks. These are deterministic
function inputs, not modified player saves or new game fixture playthroughs.

## Retained failures and corrections

- Runner20260918T020131.558075Z failed the first native renderer assertion:
  context byte10 was wrongly treated as palette, and the actor's own palette
  offset was omitted. Native instruction inspection established byte9 plus
  actor1C/1D. Failure retained at
  build/art/native-palette/20260918T020132.192655Z/failed.json. The second selected
  step did not run in this failed runner; both passed in the corrected run.
- Runner20260918T020714.797704Z failed compilation/linking before native tests:
  struct assignment generated an unresolved memcpy. Explicit volatile field
  stores remove that freestanding dependency. Original runner log retained;
  corrected static ELF remains separately named in its private build directory.
  Compilation output is now retained by the declared planner test. Only that
  test was rerun; renderer/ownership passes were reused.

## Next integration work

Retained IWRAM identifies the VBlank handler as080004B1. Static inspection shows
it calls080012BC (hardware OAM composition/transfer), then080008E0 (DMA channel
setup). This is not yet evidence of a safe palette-overlay hook or completed
hardware color transfer: inspect the actual timing and fade/stream consumers.

Connect authenticated custom actor ownership through the native render/frame
lifetime, including OAM ordering/buffer changes. Preserve original native colors
as the base for every frame; release/reuse slots when owners disappear. Verify
actual menu cancel/reopen and battle coexistence, including original actors,
weapons/effects,8bpp graphics and transitions. Measure timing before accepting a
frame hook. Do not reserve bank2 globally just because this retained menu set
leaves it unused. Reuse these passing primitive checks while integrating the
real consumer. Private0fa7d170 and packaged a6d883b5 remain unchanged.
