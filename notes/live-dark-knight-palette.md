# Live Dark Knight palette proof

September 17, 2026 local. Previous 7a1e205 proved ownership translation in
isolated native execution. This continuation installs private native hooks,
reserves transient storage, imports the existing Dark Knight generated draft
with its own colors, and proves actual menu rendering and restoration.

Private candidate: `caff91408c17c17a3ad8f410c8a8f1fc0064857e`.
Resolve it from `build/art/live-palette/poc.json`. Parent remains
`0fa7d1707e2d85fb2a8602f061b5eb4479ff3211`; packaged a6d883b5 is unchanged.
No player ROM/save/session, launcher or external service was changed. No game
window was launched and no new artwork was generated. G01-G04 remain open.

## Implementation

`scripts/build-live-art-palette.py` assembles the private stage from the pinned
parent. Source C/assembly is in `src/engine/art-palette-live.*`; it uses the
existing planner and ownership bridge. Authenticated eight-byte native entry
hooks at 080006D0, 08001194, 080012BC and 080216F8 preserve original prologues
through explicit trampolines. Reset/emission/composition follow native banks.

The native full palette transfer is **08147A44**: DMA0 copies 1,024 bytes from
03003860 to 05000000. It runs before 080012BC in VBlank, except when the native
03000E10 suspension flag is nonzero. 080008E0 is DMA setup, not this transfer.

At VBlank start, after native forced blank, the hook restores the previous
overlay's saved hardware colors. Native queued writes and full palette transfer
then run unchanged. After OAM composition, the hook authenticates ownership,
allocates a free bank and writes only the custom actor's palette nibble and
that bank's colors. Native palette shadows remain untouched. Suspended frames
skip a new overlay. This suspension path is implemented but not yet directly
accepted by a dedicated live transition test.

All three existing native heap-limit veneers lower their end from 0203F000 to
0203E000. The new page 0203E000..0203F000 contains 2,736 bytes of transient
state; existing Passing Step/job/inventory/copy storage stays in its own range.
The existing job-clear endpoint check at 091D0714 now recognizes the new end,
initializes palette state and retains existing copy-owner retirement. The three
exact native heap-start conditions and old endpoint handling are preserved.
This is a private integration reservation, not yet promoted to the main build.

ROM reservation: offsets 01F90000..01FD0000; 149,500 bytes used. Most of it is
a deterministic 131,072-byte two-pixel palette-bank lookup table. Source
`scripts/art_palette_build.py` generates it locally; no generated table/binary
is committed. Every nonzero 8bpp pixel index reserves its actual bank; index
zero remains transparent. The scan processes eight pairs per loop to reduce
branch overhead. All 65,536 lookup entries are checked independently.

Only owner 1 (Dark Knight, resources 258/259) enables custom colors in this
proof. The existing built-in-imagegen march-v2 source and own-palette conversion
are hash pinned. Six poses repeat through all present land/water sequences;
water uses the previously declared technical crop. Native commands, durations,
counts and metadata are preserved. The draft's cape/stepping defects remain
unaccepted. This is not finished animation or final art for any class.

## Passing evidence

All runtime checks used the declared `scripts/native-art-test-plan.json` via
`Test Expansion.ps1 -Only`, with IDs/purposes announced before execution.

| ID | Runner | Checks | Component report |
| --- | --- | --- | --- |
| test-art-palette-plan | 20260918T024713.371925Z | 413 | build/art/palette-plan/20260918T024713.945916Z/report.json |
| test-live-art-palette-menu | 20260918T024914.399945Z | 99 | build/art/live-palette/menu/20260918T024914.965413Z/report.json |
| test-live-art-palette-native | 20260918T025350.668853Z | 1,121 | build/art/live-palette/native/20260918T025351.220175Z/report.json |

The live test cold-loads paired parent/candidate machines using the authenticated
isolated showcase save. It samples five wheel frames, the retained header after
cancel, reopening, a second cancel and full world return. Exact generated colors
reach hardware. The complete native palette shadow matches the parent, as do
all hardware colors outside the exact allocated bank. Canonical unit bytes and
the source save remain unchanged. The allocator chooses bank 2 in the wheel,
bank 1 in the header, then releases the overlay on world return.

Observed overlay work spans scanlines 166..224 in the wheel and 166..223 in the
header. This meets those samples' VBlank window but has little remaining margin;
it is **not worst-case cycle acceptance** or proof for multiple large 8bpp
objects. The retained screen images were inspected: the earlier blank top is
gone and the Dark Knight's purple/burgundy colors display. Example:
`build/art/live-palette/menu/20260918T024914.965413Z/candidate-wheel0.png`.

Native acceptance proves a byte-exact rebuild, every declared patch, every
changed sequence's timing/commands/metadata and pixels, the full lookup table,
and real native clear dispatch for all three heap starts at new and both legacy
ends. Boundary canaries and unrelated-clear controls pass. It does not establish
worst-case allocation capacity after reducing the heap by 4 KiB.

Prior renderer/inventory/ownership evidence remains applicable. The planner
was rerun because its hot loop changed. The final same-ROM live pass was reused
after adding layout assertions and build provenance fields that did not change
ROM bytes. Generic runner default-ROM metadata is not the component identity;
the component reports pin the actual parent/private candidates.

## Retained failures

| Runner | Candidate / failure |
| --- | --- |
| 20260918T023741.853898Z | 556a7b84: correct hardware colors, scalar scan overran VBlank (166..54 with wrap), visible blank top. |
| 20260918T024057.361512Z | 661f42f3: word-signature optimization still overran (166..112); capture caught the subsequent restore before overlay. |
| 20260918T024243.899401Z | 597bf85d: transparent fast path / 4bpp prepass still overran (166..30). |
| 20260918T024551.744401Z | 8c23786e: two-pixel lookup reduced cost but scalar loop still overran (166..13). |
| 20260918T024732.002350Z | caff9140: timing passed (166..224); test incorrectly expected cancel to remove the still-visible header actor. Corrected the actual consumer lifetime and added full world exit. |
| 20260918T025220.111935Z | Native acceptance called the clear notification callback, which retires ownership but does not zero memory. Corrected to call the actual dispatcher at the ROM 036D4B8 pointer, including its IWRAM zero-fill. |

All failed runner logs and component directories remain. Intermediate planner
passes 024225 and 024532 are retained but superseded by the final 413-check pass.
When a live failure stopped a multi-selection runner, its later planner step
did not run; it was subsequently selected explicitly.

## Next work

Verify the real suspended-frame path, software fades/color modes and same-class
palette variants. Verify battle actor/weapon/effect coexistence, new heap
capacity/scene lifetimes and remaining frame budget, using bounded tests. Extend
custom palettes to all required production assets only with authenticated
source conversion and consumers. Then assemble/package the accepted pipeline;
do not promote caff9140 as final artwork or a completed expansion.
