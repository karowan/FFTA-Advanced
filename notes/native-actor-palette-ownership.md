# Native actor ownership through OAM composition

September 17, 2026 local. This follows commit 5acf231's palette allocator.
The ownership bridge is implemented and verified against actual native ARM
renderer/compositor execution. It is not installed in a playable ROM. G01-G04
remain open. No artwork generation, player save/session changes, launch,
packaging or publication occurred.

## Native frame contract

The actor renderer at 080216F8 emits through 08001F34 into the main OAM buffer:
active bank byte 03000028, counters 03000020 + bank*4, entries at
03000030 + bank*1024. Native 08001194 resets that bank's main/priority buffers.

Native 080012BC consumes the opposite bank and composes hardware OAM in this
order. The second selector is independent: 03002F58 XOR 1.

| Group | Counter base | Entry base | Per-bank bytes | Capacity |
| --- | --- | --- | --- | --- |
| Priority, first selector | 03002C50 | 03002C58 | 384 | 48 |
| UI, second selector | 03002F60 | 03002F68 | 256 | 32 |
| Main actors, first selector | 03000020 | 03000030 | 1024 | 128 |
| Tail, second selector | 03003168 | 03003170 | 128 | 16 |

UI count is limited by 128 minus both priority count and requested main count.
Main and tail then clip against remaining hardware entries. The main group's
starting index therefore depends on both other groups, and can change without
the actor changing. Affine matrix words are copied separately into attr3 after
these transfers. Ownership authentication compares attr0/1/2, not attr3.

These are disassembly findings exercised by actual native 12BC, including cases
where priority plus requested main exceed 128. DMA0 is synchronously modeled
at native completion points 08001322, 08001396, 080013E2 and 08001430. The test
does not measure hardware DMA timing or execute a complete VBlank handler.

## Implemented bridge

`src/engine/art-palette-owners.c` / `.h` provide caller-owned transient state:

- Reset one of two banks alongside native buffer reset.
- Record the emitted range after native actor rendering, snapshotting its exact
  three attributes. Resources 256..275 map land/water pairs to ten owners.
  Other resources, including held weapon 276, clear ownership for that range.
  Only the imported ordinary 32x32 4bpp body format can acquire a tag.
- Translate ownership into the actual composed hardware list using the native
  selectors/counts. Verify the entire visible main span against its source
  before publishing tags. An overwritten entry loses its old ownership.
- Refuse invalid selectors/counts, uninitialized banks or hardware/source drift
  without writing output. Invalid record ranges leave state unchanged.

The state is 2,056 bytes on ARM. **No RAM reservation has been claimed.** A real
hook must own this storage, initialize it, reset the same bank as 1194, record
216F8 emissions, and keep interrupt/buffer handoff ordering valid. It must not
borrow existing Passing Step, job, inventory or save/copy storage. Current
permanent memory ownership excludes casually treating upper EWRAM as free.

Combined owner + palette modules compile to 1,412 bytes, SHA-256
`f0b036eb57f83bdf34fa4317890457fa844651b8cd2f2c00072d0f889767aa57`.
Linked test address 09F90000 is mapped only into the isolated test machine;
neither the private 0fa7d170 ROM nor packaged a6d883b5 was modified.

## Targeted evidence and failure

Declared test: `test-art-palette-owners` through
`Test Expansion.ps1 -Plan scripts/native-art-test-plan.json -Only test-art-palette-owners`.
Runner 20260918T022244.171697Z passes 352 checks. Component report:
`build/art/palette-owners/20260918T022244.722935Z/report.json`.

The script pins ROM 0fa7d1707e2d85fb2a8602f061b5eb4479ff3211 and the previously
authenticated Samurai capture at explicit-walk/20260918T013433.309654Z. The
runner's generic default-ROM field is not the component's tested ROM identity.
No new game or player fixture was created.

Evidence covers real Samurai emission on both banks; native priority/UI/main/
tail translation; all bank-selector combinations; UI/main clipping; all twenty
land/water resource IDs; reset/reuse; overwritten source; ordinary/held redraw;
invalid selectors/counts/spans; and uninitialized state. Actual native output
provides the ordering oracle. Composed tags feed the compiled palette allocator
for two simultaneous custom actors, with complete OAM and color comparisons.
The test colors are function inputs, not new artwork or visual acceptance.

Failed runner 20260918T022159.274999Z and component directory
`build/art/palette-owners/20260918T022159.837928Z` remain intact. The first run
failed an overly broad exact-IWRAM assertion which included the test calls'
stack at 03007000. Corrected evidence permits changes only in the bounded
03006E00..03007000 test stack and records every changed offset. Native buffers
and every other compared byte remain exact. This was an assertion correction,
not a change to the native ownership implementation. Only this test reran;
the prior 81/351/408 renderer/inventory/allocator passes remain applicable.

## Remaining integration

Install an authenticated native renderer/reset/composition hook with owned
transient storage. Preserve fresh original palette state across frames before
overlaying custom colors; disappearing owners must restore their slots. Resolve
native palette transfer, fades/color modes and interrupt ordering explicitly.
Then verify live menu cancel/reopen, battle coexistence and cycle budget.

Static investigation also confirms 080008E0 configures DMA channels and
080007C8 executes queued transfers. Neither finding establishes that the full
OBJ palette is refreshed every frame. Do not restore from an assumed palette
source or treat this isolated synchronous DMA test as live-frame acceptance.
