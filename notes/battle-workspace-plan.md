# Battle workspace and fresh-game startup

September15,2026 Pacific. Current bounded acceptance:
`351a3c1ca99288b564a8b36e93be173a217b300d`, full75/75 combined steps in
`20260916T045059.259911Z`, `inputsUnchanged=true`, independently rehashed.
Shared prerequisite: `cd34eabe22e5c8aef64bfabcf2b06e22508d6569`.
Frozen foundation: `ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`.
This accepts storage and the scripted opening, not the whole expansion.

## Current allocation and ownership

All three native heaps now end at0203F000 instead of0203CA40. The permanent
reservation falls from13,760 to4,096 bytes. Passing Step moves toF000..F1FF;
diagnosticsF220..F3FF, job bankF400..F727, AI pointerF728, Mystic formula
pointerF72C and compatibility/owner rootsF800 upward retain their reservations.
Persistent22-byte unit records, the820-byte action frame,824-byte result slot
and260-byte extra snapshot ABI are unchanged. No save-schema change is needed.

The native manager is also constructed during opening dialogue. Its integrated
allocation therefore grows only430 to440 bytes, with a16-byte header at430:
magic, exact manager self, optional pool pointer and pool heap. Standalone430
managers remain valid copy owners and are rejected by workspace accessors before
reading a nonexistent appended header.

Explicit action snapshot/fresh-result creation allocates a9,760-byte2620 pool
from the current native global heap. Getters never allocate or repair state.

| Pool offset | Owned content |
|---|---|
| 0000..000B | Magic, owner and self header |
| 000C..000F | Boundary padding |
| 0010..19CF | Eight824-byte native result frames |
| 19D0..19DF | Boundary padding |
| 19E0..21FF | Eight260-byte extra snapshots |
| 2200..220F | Boundary padding |
| 2210..260F | Eight128-byte compressed extension snapshots |
| 2610..261F | Boundary padding |

Lookup requires the exact registered native manager and native global, valid
native manager capacity, matching header/self, current pool heap, pool bounds,
native allocation marker/capacity and matching pool owner/self. Result frames
add their existing exact live stack-token checks. Null, unaligned and non-EWRAM
frame pointers return before external ownership lookups.

Native6EC0 writes requested words+3 at6EF8..6F00, then6FA6..6FBA adds an
unsplittable remainder of zero..three words. Valid capacity is consequently
requested through requested+12 bytes, with complete allocation bounds checked.
The tests exercise all four sizes through the actual native allocator.

Freeing the pool alone clears its owner pointer and allows later recreation.
Freeing the exact manager or a containing parent retires the pool and manager
ownership before native memory release, including parents that never created
a pool. Clearing the pointer before nested free makes recursive observation
inert. Scene clear observers recognize both integratedF000 and standaloneF400
heap ends. No transient pointer or pool enters persistent job/save records.

## Native integration points

- Parent96ED4 calculates resource capacities and aligns them. A checked stub
  replaces96EF4..96EFA, adds trailing capacity4C0 rather than4B0, restores
  r4/r0 and continues at96EFC. Native allocation, clear and heap creation stay
  at96EFC,96F08 and96F10;96F1E publishes manager at0200F4B0.
- The existing97000 branch points to an aligned wrapper retaining the native
  saved-register/frame ABI. Its trampoline uses440 and continues at97000's
  original allocation sequence9700A. Native9700C allocates,970018 clears the
  requested size and97001C stores its heap. Registration follows construction.
- `ffta_owned_battle_manager` exposes the existing exact copy-owner identity.
  `ffta_snapshotted_owner_free` observes frees before allocator metadata changes.
  The workspace observer retires containing-parent ownership explicitly.
- All three native clear and allocator limits change together. Updating only
  allocation bounds would allow the earlier clear to erase reserved state.

## Deterministic acceptance

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Suite battle-workspace
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Suite battle-workspace-review
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Suite combined
```

The303 ownership assertions cover real constructor and parent budgets, both
incoming stack alignments, reuse, empty pools, forged/retired/detached owners,
small standalone managers, no reads beyond their allocations, native slack,
independent pool free, containing-parent free with/without a pool and scene
resets. Existing result-frame, Bard/Mystic and Passing Step tests use current
production accessors/addresses rather than old global pool locations.

The13 opening assertions start from erased cartridge memory. They detect the
actual live50,688-byte keyboard allocation, compare alphabet and default-name
crops against the clean original, confirm by Start/Up/A, then reach the original
Snowball instruction dialogue and scene background within declared bounds.
The candidate has1,276 bytes of free heap at name entry. Complete inputs,
heap observations, states and screenshots remain in ignored candidate output.
A blank panel or intact canary alone is not acceptance.

Terrain validation preserves all static and animated byte comparisons. A capture
may contain the first1,024 bytes of animation phase2 and the last1,024 of phase1
while upload is in progress. The revised check verifies native chunk phases and
order over32 frames and requires distinct complete frames; this final run
observes complete phases2 and3. Raw output is stored under the candidate hash.

Focused run044940.374819Z passes12/12 before the final75/75 run. The final suite
also covers original combat, existing jobs/reactions, menu and movement playback,
AI, Geomancer field cold saves and code relocation. Root's review is complete
for this batch. Central code uses31,920/32,768 bytes; Mystic/workspace code uses
11,056 bytes in its separately bounded reservation.

## Retained failures and corrections

- 041523.339505Z failed assembly before runtime: two low-register Thumb moves
 needed the correct spelling. No runtime acceptance is attributed to that run.
- 041619.895734Z rejected7cf797f56795e895972570381237b21df0878818. The original
 proposal eagerly enlarged the manager to2A50/parent capacity2AD0. Because that
 manager exists during dialogue, it left44,184 free bytes and prevented the
 keyboard. The original proposal remains in source history; it is not the layout.
- 042219.855951Z passed20 gameplay/build steps onf6197b83d34daefa78f1d79eb41984eb60671ff5.
 The two new harness failures were a missing imported ARM constant and historical
 fixed key timing that typed into a late keyboard. The keyboard itself allocated.
- 042653.527822Z passed10/10 on that candidate,208 ownership and13 opening
 assertions. Review then added parent retirement and additional edge cases.
- 042922.461080Z passed74/75 on53f790698afc16623884ea26382448374ee71d6c. Its sole
 failure assumed complete terrain animation phase2 at a fixed capture time.
 The preserved mismatch was exactly a native two-phase upload boundary. Further
 review corrected unused-parent retirement and native allocation slack before
 the final candidate; older passes do not certify those later changes.

Mystic enchanted Fight, defensive reactions, whole Doublecast, remaining native
presentation/AI, broader acquisition/law/campaign checks and final playable
release acceptance remain open. See `IMPLEMENTATION-STATE.md` for current scope.
