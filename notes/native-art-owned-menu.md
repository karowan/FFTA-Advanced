# Connected consumers and menu ownership — September 18, 2026

Follow-up to c14ecc2. Built-in imagegen drafts only; final sprite refinement is
deferred. No external provider, agents, publication, game launch, package or
player-save change. G01–G04 remain open.

## Current candidate and reproduction

The current private connected ROM is **661853ea8e9850cf4352705ed506c4e49dee8505**,
resolved by `build/art/connected/current.json`. Its palette parent is
**767e73914b4a3b873fcfbc8c86a9afeab8c4f1ad**. Use the declared Python runtime:

```powershell
& $fftaPython scripts/build-live-art-palette.py --history-slots 20 --all-classes --workspace-low-address --provisional-history --fast-rotation --owned-menu-buffer
& $fftaPython scripts/build-connected-art.py --source build/art/live-palette/owned-menu-current.json
```

Build the palette parent before assembling its children. Parent compilation
rewrites its private manifest's compile-directory metadata even when ROM bytes
remain identical; reassemble afterward so the connected manifest pins that
exact metadata. The final native test authenticates this pin and reproduces all
four asset stages. Historical indexes and installed a6d883b5 preview remain
unchanged. Do not use the older default connected-builder source for this fix.

## Real item/ability list collision and fix

The original palette reservation at `0203C000..0203F000` collided with the
existing expanded party list. Failed inventory RAM contained palette magic
`50414C31` where the native list count belonged; the actual screen was empty.
The failure was not repaired by weakening the count or pixel oracle.

The accepted technical fix gives the list to its actual party context:

- Both party context allocations grow from `7280` to `9980` bytes. The list
  starts at context+`7280`, leaving the existing AP/status/job-copy tail intact.
  Its `2700` bytes hold the `230`-byte header and all 460 twenty-byte rows.
- All three parent allocation paths (`24644`, `30C06`, `30C78`) grow from
  `C600` to `ED00`; both world outer heaps grow `C640` to `ED40`.
- Native context+`2D50` points to that owned list. The recompiled Auto-Potion
  preference consumer compares against context+`7280`, including movable
  battle contexts, rather than assuming absolute `0203C000`.
- Native allocation/free still own the lifecycle. Battle heap limits and the
  12 KiB palette reservation remain unchanged. The party scene costs an extra
  `2700` bytes only while its parent allocation exists.

The item and Auto-Potion verifiers now follow the actual published list pointer
with explicit RAM/count bounds. They retain exact visible-pixel, state and
choice checks. Native constructor testing uses both modes, both stack residues,
world and movable battle addresses, real allocation/teardown, and a declared
synthetic all-460-weapon capacity case. Only that in-memory component case
changes item types; no ROM file or player inventory is changed.

## Passing evidence

| Test | Checks | Evidence |
| --- | ---: | --- |
| `test-art-owned-menu-bounds` | 80 | `build/art/owned-menu/native/20260918T164649.233894Z/report.json` |
| `test-art-owned-menu-preference-ui` | 24 | `build/art/generated-effect/661853ea8e9850cf4352705ed506c4e49dee8505/potion-menu-20260918T164649580694Z/preference-report.json` |
| `test-connected-art-equipment-ui` | 30 | `build/art/generated-equipment/tests/20260918T164659.060789Z/report.json` |
| `test-art-owned-menu-native` | 9807 | `build/art/live-palette/native/20260918T164822.002815Z/report.json` |
| `test-connected-art-native` | 3981 | `build/art/connected/native/20260918T164859.334084Z/report.json` |

The first three share terminal passing runner `20260918T164648.529351Z`.
The final two have passing runners `20260918T164821.390533Z` and
`20260918T164858.737045Z`. Inventory/Buy/Sell use actual native screens and exact
generated icon pixels, preserve roster/AP/inventory, and make no transactions.
Both Chemist races verify two real reaction rows, cancel, confirmation, labels
after reopening, and unchanged other preferences/AP/stock. The `--menu-only`
run deliberately does not repeat cold-save acceptance. Inventory and ability
screens were visually inspected; the corrupt stripes are gone.

Mixed battle entry passed on intermediate **5ee3099323fe1af8b2348b772786435d1e011cb6**:
`build/art/live-palette/battle/20260918T164311.010995Z/observed.json`, 632 checks.
Final changes add two missing party-parent allocation paths and one matching
outer-heap literal; that pass is not relabeled as an exact-final-ROM result.

## Retained failures

- Runner `20260918T163257.399304Z`: status passed, equipment failed before its
  baseline inventory could be read. Empty screen and overwritten list at
  `build/art/generated-equipment/tests/20260918T163300.712492Z` on b4993232.
- Rejected separate-reservation trial: palette **587b43f9**, connected
  **0c5aac66**, palette RAM `02039000..0203C000`. Native reset/rebuild passed
  9799, but mixed battle stalled: runner `20260918T163854.797308Z`, captures
  `build/art/live-palette/battle/20260918T163859.212306Z`. Equipment step was
  unrun. `--separate-menu-ram` retains this diagnostic recipe, not acceptance.
- Initial owned-list trial **5ee30993** enlarged only one parent path. Mixed
  entry and native/rebuild passed, but Inventory had visible stripe corruption:
  runner `20260918T164306.027021Z`, captures
  `build/art/generated-equipment/tests/20260918T164329.205384Z`. Its captured
  parent-size global was still `C600`. Final fix covers all three paths.
- First preference-module compilation failed for missing `__aeabi_uidivmod`:
  `build/art/live-palette/compile/20260918T164151.275189Z/compile.log`.
  Explicit libgcc linkage resolves it; actual ARMv4T and UI tests pass.

## Earlier connected held weapon and status acceptance

These results are on **b4993232e05eeb20ce536cca6f4b9738aa4a2b12**, not silently
promoted to final-ROM runtime evidence:

- `test-connected-art-held-weapon`: 90,348 checks, runner
  `20260918T163032.287125Z`, report
  `build/art/generated-actions/battle/20260918T163032.975881Z/report.json`.
  Actual Viking Move/Fight/next-turn with four declared racial profiles;
  original resource128 vs generated276, both attachment channels, body colors,
  full allocation bytes, exact 14 damage / 47 HP / 14 MP outcomes and roots.
  Samples are every frame during the declared animation intervals. Story
  appearance identities remain fixed; fixture jobs/equipment are explicit.
- `test-connected-art-status`: 206 checks, report
  `build/art/generated-status/tests/20260918T163258.109196Z/report.json`.
  Exact b499 ready capture reused; control changes only the 128 status pixels.
  Native status outputs, actual Exposed/Centered/Protect cycling/removal,
  hardware colors and paired state/VRAM isolation pass. Grants are controlled
  fixture setup; this does not establish natural grant/expiry gameplay.

Held evidence required a decoder correction: command-only `(FFFF,FFFFFFFF)`
records have no tile/layout. Only that exact pair is skipped, never malformed
near-matches or extra arbitrary poses. `test-native-art-command-marker` passes
10 retained-input/rejection checks, report
`build/art/command-marker/20260918T132729.680867Z/report.json`.

Held failures remain in `build/art/generated-actions/battle/` at
`20260918T132505.952963Z`, `20260918T132729.904673Z` and
`20260918T133001.530271Z`. They exposed the marker, un-emitted pending uploads,
and a mismatched exact-frame/pose comparison. Pending allocations count as
display evidence only with the bounded existing direct-byte anchor; invisible
queued uploads are explicitly not displayed-frame proof. Trail colors must
equal the current native palette shadow and the one steady palette across the
complete original action. There is **no timing acceptance**: trail first appears
at attack57 vs control58 (99 vs98 visible samples); blade samples are60 each.

## Remaining work and limits

### Follow-up: actual battle Status allocation fails

After checkpoint b109a28, `test-art-owned-menu-battle-ui` exercises the real
Status command from the retained mixed ready state. It authenticates the prior
ROM and requires exactly three changed bytes (`24644`, `30C78`, `30C9D`) in the
final ROM, all parent allocation immediates/literals; serialized pointers and
layouts are unchanged. Initial raw RAM/IWRAM must match before any input.
No new battle fixture or broad playback is created.

Runner `20260918T165426.338377Z` failed in the harness before input: a restored
state has no rendered frame yet. Its full runner traceback is retained; that
attempt's screenshot failure also prevented its child failure report. The
harness now obtains one frame after the exact-state check and can record raw
failure captures even without a frame.

Runner **20260918T165502.509792Z** then failed on the actual menu allocation.
Evidence: `build/art/owned-menu/battle/20260918T165504.119896Z/failed.json` and
the adjacent `ready`/`status` raw captures. Three Down presses and A select
Status. The screen turns black; parent pointer `03002778` is zero while its
requested size global `03000E54` is `ED00` (60,672 bytes). The native constructor
subsequently publishes an invalid party pointer. This is a game-capacity
failure, not an image comparison or list-pointer verifier problem.

Read-only parsing of the retained actual native heap headers gives:

| Point | Total free payload | Largest free block | Heap end |
| --- | ---: | ---: | --- |
| Ready | 54,632 | 41,640 | `0203C000` |
| Failed Status | 53,596 | 41,640 | `0203C000` |

The original `C600` parent also exceeds that largest free block, so merely
reverting the new tail allocation does not resolve this captured fragmentation.
The failed heap retains the 9,824-byte expansion workspace at `020159D8`, plus
free blocks of10,644,1,312 and41,640 bytes. A 60,672-byte request exceeds even
their total; changing best-fit placement alone cannot make it succeed.

The current candidate remains unaccepted and uninstalled. Next investigate
scene-owned palette/list memory and native parent lifetimes rather than adding
another permanent reservation. Original party list storage at context+`4340`
ends at the next buffer+`5AC0`, but reusing/repacking it requires proving all
native consumers, not simply shifting the pointer. Preserve the passing world
menu, ability, bounds and rebuild evidence while fixing this live path.

The prior movement/phase failure remains unresolved. Native construction at a
movable battle address did not establish live party-menu capacity; the ordinary
mixed battle above now supplies a concrete failing case. That allocation and the existing
opening/name-entry heap pressure require bounded acceptance. Earlier original
heap research in `notes/ap-copy-storage-review.md` already found a 16 KiB
reservation insufficient for the native name keyboard; do not infer all-scene
capacity from the mixed battle pass. Other natural action/effect lifetimes,
maximum heap, final assembled acceptance and delivery remain open. Existing
all-ten water, held and status evidence is retained with its exact ROM/input
scope. No broad suite was run. Final animation/art quality remains deferred.

## Follow-up: shared battle Status heap and two-page US keyboard

Current connected ROM **d9acd7234186a77561a2fb4ee91fdae2197c197d** resolves through
`build/art/connected/current.json`. Palette parent **ff6a50eaa9e477c30482a136b38da12dea229295**.
The immediately preceding shared-menu connected ROM is **7b966543796975a6dea474d0a360495b57d8e6a3**,
parent **d26f46cac25de20908083338c08e4ab18ef8e78d**. Exactly one production byte
changes between these connected ROMs: offset `12A15E`, `C6` to `42`.

### Native battle menu ownership

The prior contiguous `ED00` request could not fit the measured live heap.
The native party destructor already individually frees its context, glyph buffer,
secondary buffer and nested text heap. `art-party-heap.c/.s` therefore borrows the
actual battle root for those allocations instead of reserving an outer block.
It bypasses outer initialization/close only for that exact root and native callers:
`080710B3`, `08071131`, `08071275`, `080712BF`. Parent release retires borrowing
without freeing the battle root. World-menu and unrelated heap operations remain
native. State is16 bytes at `0203EFF0`, beyond the live palette state ending
`0203EC30`, and cleared by the existing scene reset hook.

Hooks: parent setup `24642` (18 bytes, unaligned Thumb veneer), release `24684`,
heap init `70C8`, heap close `718C`. Original prologues/continuations and incoming
stack alignment are preserved. Native size global `03000E54` remains `ED00` for
compatibility, but is not a real contiguous outer allocation in shared mode.

The retained fragmented heap test reproduces native1,024-byte Status palette
backup, then calls the real constructor/destructor at both stack residues. It
checks all preexisting allocated payloads, exact free-list restoration, wrong
roots/near-miss callers and copy retirement. Before opening:53,596 free,
41,640 largest. During opening:1,068 free,464 largest. This is narrow headroom,
**not maximum encounter acceptance**.

| Declared check | Result | Evidence |
| --- | --- | --- |
| `test-art-shared-menu-lifecycle` |44 pass| `build/art/owned-menu/shared-native/20260918T171509.925084Z/report.json` |
| `test-art-shared-menu-native` |9810 pass| `build/art/live-palette/native/20260918T171510.087894Z/report.json` |
| `test-art-shared-menu-mixed-entry` |632 pass| `build/art/live-palette/battle/20260918T171708.832178Z/observed.json` |
| `test-connected-art-native` on7b966543 |3981 pass| `build/art/connected/native/20260918T171729.276496Z/report.json` |
| `test-art-shared-menu-battle-ui` |25 pass| `build/art/owned-menu/battle/20260918T171936.852610Z/report.json` |
| `test-art-owned-menu-bounds` |80 pass| `build/art/owned-menu/native/20260918T172030.940267Z/report.json` |
| `test-art-owned-menu-preference-ui` |24 pass| runner `20260918T172030.268141Z`, second log |
| `test-connected-art-equipment-ui` |30 pass| `build/art/generated-equipment/tests/20260918T172041.677867Z/report.json` |

Actual Status starts from the exact7b966543 mixed capture; initial RAM/IWRAM must
match. Native inputs open Status, observe allocated context/list and borrowed
root, then return to the battle. Both class palettes, actors, roster, inventory,
AP and retired ownership pass. Returning keeps Status selected; Up three times
restores the Move-selected state expected by the existing strict pixel anchor.
The two earlier failures remain:

- `20260918T171343.441845Z`: component guard treated heap header+4 as constant1;
  it is the actual free-block count. Child `shared-native/20260918T171344.103240Z`.
- `20260918T171814.534479Z`: actual Status opened/returned, but the harness checked
  a white Status label while the selected label was orange. Child
  `battle/20260918T171815.195323Z`; corrected inputs, no gameplay patch.

### Native US keyboard capacity

US initialization at `12A250..12A276` builds only pages0/1. Shoulder-key handlers
at `12AC08` wrap right at1 and left below0 back to1. `12B468` clears/builds exactly
`2100` bytes per page; `12B44C` submits that page's `840` words. The associated
character lookup has two `78`-byte pages. These are two tabs (Aa and123), distinct
from the six character rows per tab. Allocation at `12A15E` nevertheless requested
`C600` bytes. `--compact-us-keyboard` verifies native page-bound opcodes and changes
that request to `4200`; native page construction, letters, fonts and input logic
are unchanged. It releases33,792 bytes of unused allocation.

Cold runtime `20260918T173653.587250Z`, captures under
`build/art/keyboard/20260918T173655.140043Z`, runs both the authenticated pre-palette
parent0fa7d170 (native original allocation/F000 heap) and the actual final candidate.
Both begin with erased isolated SRAM and bounded dialogue inputs. Both native
pages, L/R wraps, deleting the default name, adding a letter/digit, Start/Left/A
confirmation, committed native story-name bytes at `02001F1C` and allocation
teardown pass. Candidate heap ends at `0203C000` and has22,780 bytes free at the
keyboard; reference has1,276. Full raw/state/screenshot/input/heap evidence stays
ignored and local. Neither player saves nor a visible game session is used.

That runtime's first pixel comparison failed because x15 included two pixels of
the animated selection arrow. Both rendered sheets were visually inspected and
both `4200`-byte native glyph buffers match. Reconciliation uses the established
original lettering crop `(17,33,176,126)`, authenticates the complete retained
RAM/PNG/report set pinned in `native-art-keyboard-evidence.json`, verifies heap
and buffer observations from actual RAM, and verifies the committed name. It
reuses completed runtime instead of replaying it merely for a crop correction.

- `test-art-keyboard-evidence`:182 pass, runner `20260918T173919.355134Z`,
  `build/art/keyboard/20260918T173920.946286Z/report.json`.
- `test-art-keyboard-native`:9811 pass, same runner,
  `build/art/live-palette/native/20260918T173921.201003Z/report.json`.
- Final `test-connected-art-native`:3981 pass, runner `20260918T174009.049313Z`,
  `build/art/connected/native/20260918T174009.725141Z/report.json`.

Retain failed keyboard runners173026.509995Z,173119.808523Z,173229.608293Z,
173359.401402Z and173525.481742Z (all date20260918). The first derived reference
incorrectly enlarged the connected heap into palette state; the later parent
reference attempts omitted explicitly erased SRAM and did not exercise a reliable
fresh-start keyboard. They are harness/control failures, not candidate acceptance.
The actual erased-SRAM run173653.587250Z remains failed as a whole due to its crop;
the separate authenticated read-only reconciliation supplies the corrected scope.

### Remaining scope

All runners are terminal. Current byte-exact rebuilds pass; one-byte keyboard
delta permits reuse of preceding battle/world consumer evidence in its exact
scope. Prior movement/phase mismatch, worst-case live menu/battle capacity,
remaining natural consumers, assembled final acceptance and delivery remain open.
This does not prove a complete campaign or final animation quality. G01-G04 stay
open. Built-in imagegen is the artwork route; final sprite refinement is deferred.
No package, installed preview, vanilla, player save/session or publication change.
