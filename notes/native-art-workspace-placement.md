# Mixed battle heap placement and speculative palette histories

Follow-up dbe4fe0, September 18, 2026. Built-in imagegen only; final sprite
refinement remains deferred. All G gates remain open. No installed package,
launcher, save or running session was changed.

## Root cause and bounded fix

The original all-class 4b35081ba8d69f6ebf997607c119931e303a6106 stalls because
its native 39944-byte battle workspace allocation fails. The subsequent native
cleanup passes NULL through 080BDB18 -> 08022854 -> 08007170. Native free then
corrupts its free list; a later allocation follows a bogus link0203FFF4 and
canonical player/enemy names are eventually erased. The final text loop at
0801535C is a downstream symptom, not a missing Wait input.

At the first failed allocation there are54352 free bytes, but largest contiguous
space is22148. At the earlier expansion workspace request there are free blocks
20480(low address),2080 and19480(high address). Native best-fit puts the persistent
9824-byte expansion pool in the high block, between a temporary22148-byte AI
allocation and the remaining9644-byte tail. Freeing the AI block cannot create
the39944-byte span. This is fragmentation, not total free-memory exhaustion.

New optional builder mode `--history-slots 20 --all-classes --workspace-low-address`
patches only the expansion pool's allocation call literal at ROM013078C4. It
selects the first suitable low-address physical free block for that exact9824-byte
request, verifies bounds, physical links and free-list neighbors, then resumes
the original native allocator at08006ED8. Native unlink, split, coalescing and
free remain unchanged; other allocation callsites keep native best-fit behavior.
No NULL guard or ignored failure is used to pass the test.

Latest candidate e1c22b0153d2510786e42f7b9645f752122a5f3a resolves through
`build/art/live-palette/all-classes-workspace-current.json`. Stage243400,
state11292, RAM0203C000..0203F000. Default05c66b38, history394e96ab and uncorrected
all-class4b35081b indexes remain separate. Rebuilds are deterministic. Existing
generated drafts remain unaccepted/repeated transport poses.

## Evidence and limitations

All paths below are private under build/art unless stated. Timestamps begin
20260918T. Announce exact test IDs before invoking the declared native-art plan.

- `test-art-workspace-placement`: runner115451.659098 initially179 checks on
  337a26c9; expanded physical/free-list consistency and malformed-input checks
  pass246 on e1c22b01, runner120023.442918, report
  `workspace-placement/20260918T120024.226011Z/report.json`. Executes actual owned
  pool preparation, native free of22148 bytes, then39944-byte allocation.
  Original pool020373E8 fails the larger request; corrected pool020159E4 lets
  it succeed at02031D58. Free/coalesce restores identical physical shape;
  owner detaches; unit bytes and art RAM remain untouched. No gameplay or video
  model in this ARMv4T component proof.
- `test-live-art-mixed-workspace-first`: runner115451.659098, battle115452.580797
  on337a26c9 reaches actual Dark Knight turn and all four required profiles.
  It FAILS the unchanged no-effect-refusal assertion with seven target refusals.
  This demonstrates passage beyond the old stall only; no mixed-art acceptance.
  Second group was skipped by fail-fast. e1c22b01 adds selector validation and
  has the component proof; it has no new full mixed playback evidence yet.
- Prior native/menu/history/import evidence remains applicable to unchanged
  palette mechanisms. Do not rerun all passing tests merely because code/assets
  relocated. Exact-ROM state replay still requires a new matching fixture.

## Retained failed diagnostics and rejected trials

`test-live-art-mixed-write-trace` adds private clear/copy/free callbacks and an
allocation ledger in unused owned RAM; it preserves source asset addresses.
The final helper supports a first failed-allocation trap or an earlier explicit
workspace-request trap. Reports are diagnostics, never gameplay acceptance.
The ledger can include subordinate heap allocations; physical heap/free-list
validation is authoritative for outer heap topology.

- battle111926.787475: first unit erasure at frame12637, initial callback ring.
- battle112523.117303: same erasure, enriched source/destination words and exact
  preceding state/RAM/IWRAM retained. Snapshot-copy sources still had valid names.
- `test-art-unit-erasure-cpu` reports112719.045852 and112809.160062 used incorrect
  saved-PC offsets and are invalid causal evidence. The interrupted Thumb clear
  loop requires saved PC-2, proven by remaining-size/register relation. Corrected
  report113035.638353 still follows a previously corrupt free-list link and stops
  at unmapped0204B934. No BIOS/IRQ/DMA model; not gameplay acceptance.
- `test-art-heap-exact-fit`, report113337.528066: observed an already corrupt
  free list. This does NOT prove an exact-fit bug in the original allocator.
- battle113541.892263 and114003.538685: first NULL free at frame9953; public wrapper
  caller08022861, outer caller080BDB27. Both diagnostic runs intentionally fail.
- battle114154.936088: first failed39944-byte allocation at frame9840, before
  corruption. battle114413.185301 adds a live allocation ledger identifying the
  persistent9824-byte pool caller09307899. Both intentional diagnostic failures.
- Early-allocation trial eaa41357, battle114732.030114: registration precedes
  publication of native manager pointer; prepare therefore did nothing. FAILED.
- After-publication trial b92ee43d, battle114949.427575: moved pool but left only
 31804 contiguous bytes. FAILED. Both early-reservation approaches rejected;
  current source implements low-address selection at the original lazy request.
- `test-art-workspace-request-trace`: runner115149.380466,
  battle115150.012859, stops at frame9753 before the pool request. Confirms the
 20480/2080/19480 free blocks. Its RAM/IWRAM hashes are pinned in the component
  regression; this diagnostic intentionally reports failure after capture.

## Next: palette ownership, then remaining acceptance

`--trace-target` additionally compiles a diagnostic halt on the first rejected
explicit target; separate `target-trace-current.json`, never a deliverable.
`test-art-palette-target-trace`: runner115843.313991, battle115844.020648,
ROM eac22a2ec40e70722cbd57c42521263b03b30355, frame2011. The trace intentionally
fails after capturing the target. The second selected placement test was skipped;
it was subsequently run separately and passed as recorded above.

The first refusal is a30-frame table fade for native indices448..463(bank12),
task03003C7C, table020164FC. Seven class histories (owners1,2,4,5,6,7,8) were
speculatively matched to the same native bank12 before any custom actor appeared.
All emitted masks, owner-ready flags, applied/restored counts are zero. Their
native baseline is `334a42040c3aff77252935053d02df03446d0b7e2f77d877145be4050813b013`.
The new target is `91424204f121ff774c0555053d02bf03b701bb029d23de5f194be029223fae4f`;
current native bank is black. It is not their authenticated baseline or a uniform
color, so the strict target mapper rejects it. Do not weaken that mapper or hide
its counter. Distinguish provisional palette matches from confirmed actor-owned
history, while retaining actual off-screen transformations and first-visible
appearance behavior. No ownership fix has been implemented at this checkpoint.

Then rerun the affected first mixed group and, when justified, the second. Still
open: Samurai/Moogle mixed coverage, natural scene/effect lifetimes, maximum heap,
cross-bank effects, timing, remaining assets, final artwork and delivery.
