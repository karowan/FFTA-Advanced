# RAM/heap audit fixes (release 0.7.3)

Status: released in v0.7.3 (game `40c9bbb9115c53ddbab6381e93c963ae0bd31ee4`, acceptance run `20260926T065902.911740Z`,
all 28 steps of `scripts/memory-fixes-test-plan.json`; the released game is the
item-icons stage built on this one).

On September 25 a six-part audit looked for RAM, heap, stack and table
overflows that the mod introduced. Every finding was then verified and either
fixed or shown safe. The fixes are a bounded patch stage,
[build-memory-fixes.py](../scripts/build-memory-fixes.py), on top of the
[palette-removal](palette-removal-2026-09-25.md) stage. Chain: teaching rows →
equipment revision → enchant weapons → help pages → palette removal → memory
fixes.

## What the stage changes

Compiled code goes into blank ROM at `0x1FD0000..0x1FDFFFF` (1,280 bytes used).
Calls back into installed code go through generated Thumb stubs. Each stub's
target is authenticated against the integrated build, with earlier stages'
declared patches masked. There are six patches, each checked against its
expected original bytes:

| Site | Change | Why |
|---|---|---|
| `ffta_samurai_execute` (`0x91C3370`) | Trampoline to [samurai-execute.c](../src/engine/samurai-execute.c) | The executor entry runs for every action. It held an 820-byte action snapshot (a 920-byte frame) on the IWRAM stack below every nested result, reaction and Doublecast chain. It now borrows a root result-bank frame ([snapshot-lend.c](../src/engine/snapshot-lend.c)); its own frames total 160 bytes. |
| `stack_result` (`0x9302D5C`) | Trampoline to [result-fallback.c](../src/engine/result-fallback.c) | When no bank frame is free, results used to add an 880-byte stack snapshot, overflowing deep chains by up to about 150 bytes. |
| `ffta_job_load` (`0x91D05CC`) | Recompiled [job-save.c](../src/engine/job-save.c) | The `JST1` suspend marker leaked from a loaded suspend image into live RAM and then into later normal saves. It is now cleared from loaded state. |
| `0x7A094`, `0x8D0C4` | Trampolines to the C builders their siblings `799C0`/`8CBDC` already use | These original item-list builders still read the old 4-byte inventory records. `7A094` runs after every equip (`7AF22`) and from sorting (`7ACDC`); `8D0C4` runs from `8E838`. They produced fake entries (IDs such as 1296), dropped owned items, and could overflow their stack list after 270 matches. |
| `0x1339EC` | Literal back to `0x08527D5C` | The integrated table relocation had moved the reaction mask base into the new application-mask copy. As a result, 109 reaction/status cases stopped blocking reactions: for example, Return Magic fired while Petrified and Counter fired under status bits 31, 32 and 43. [build-integrated-jobs.py](../scripts/build-integrated-jobs.py) now leaves that literal native. |

Three more patches came from the whole-game pass on September 26 (below):

| Site | Change | Why |
|---|---|---|
| `0x8B890` | Trampoline to [bg-recolor.c](../src/engine/bg-recolor.c) | The native menu recolor writes two map rows at a caller's pointer. The unit menu (`0807EA00`) un-highlights its "previous row", which the menu constructor sets to 0xFF, as row 512, about 12 KiB past the window's map buffer. In the original heap that was free memory. With the lower heap end it ran through the fixed state and wrapped past the end of EWRAM into the party's unit records: opening unit Info or Status set 0xC0 on every other byte of one unit's record from +0x36 to +0x61. The replacement recolors only inside the layer's own map buffers. |
| `ffta_chemist_payment_gate` (`0x91E6D44`) | Trampoline to [chemist-payment.c](../src/engine/chemist-payment.c) | A refused payment takes the executor's "cannot pay" branch at `A4968`, which never ends the turn. Single-ally Chemist recipes let targeting pick an enemy or an empty tile (for example Potion on an adjacent enemy), and the gate refused, so the battle stopped with no menu. The gate now pays only for a party recipient and always continues. Per-recipient eligibility keeps other units unaffected, and nothing is consumed. |
| `0x857EC` | CpuSet fill 0x160 → 0x180 halfwords | Before drawing a job name, the job wheel clears 11 glyph columns. The 11-tile "Mystic Knight" draws a 12th column (VRAM `0x0600B7A0`), which stayed on screen after the next, shorter name. That column is blank in the original game. The three other 11-column clears (`4A960`/`4ACC0`/`4AD34`) draw item names, which measure at most 11 tiles. |

Two more came from a player report on September 26 ("Chemist items give no EXP"):

| Site | Change | Why |
|---|---|---|
| `0x12E5B4` | Trampoline to [exp-job-gate.s](../src/engine/exp-job-gate.s) | The native EXP formula treats every job above 82 as a special unit: EXP only for a few story characters behind story flags, otherwise 0. **Every unit in an expansion job (116–125) earned no EXP from any action.** It wasn't only Chemist items: Fights, spells and songs were affected too. Those ten jobs now take the ordinary path; other jobs above 82 keep the special path. Measured afterwards: new-job Fights earn +6 to +10, and a Chemist Potion on a hurt ally earns +12, the same as the original Item Potion from an original-job unit at the same level. |
| Chemist action records +9/+10 | Shape/size 5/2 → 1/0 for CHM-A1–A4, A6–A10 | Every Chemist recipe carried Healing Mist's cross area, so single-ally recipes also hit adjacent units. For example, one Potion healed two allies, and a revival could raise several KO'd allies. By design only Healing Mist is a cross. A check of all 85 new actions' shapes against their designs found no other mismatch. |

**The reported "Shieldbearer" label:** your Viera Archer's record had exactly the unit-menu recolor pattern. Her abilities 1–33 read as mastered, and her Support (+0x3B) and other slots held 192, past the Viera table. That value displayed as "Blizzara" in Pick Abilities and "Shieldbearer" in battle. The saved damage stays in that save file; the game can no longer produce it.

**Stack guard.** Both fallbacks use `ffta_stack_room`
([action-snapshot.h](../src/engine/action-snapshot.h)). They keep a stack
snapshot only when the frame, the deepest measured nesting below it and IRQ
room all fit above resident IWRAM code at `0x03006D68`. The reserves are 3,328
bytes under the executor and 2,944 under a result. Otherwise the action or
result runs without a snapshot, just as bank-less forecasts already do.
[action-snapshot.c](../src/engine/action-snapshot.c) carries the same guard for
future rebuilds.

## Measured stack depth

Unicorn stack probe, using the audit's tests with the stage's code overlaid.
The test SP stands in for the battle state machine's `0x03007DC0`, which leaves
a 4,184-byte budget above resident code.

| Chain | Before | After |
|---|---|---|
| Mystic Knight Doublecast into a Shell target | 4,128 (56 bytes left, less than a VBlank) | 3,368 |
| Counter-draw | 3,288 | 2,528 |
| Mystic Knight Shell | 3,284 | 2,524 |

All three tests still pass under the probe.

## Findings verified as safe, or handled without a ROM change

- **Geomancer renderer pressure:** with the AI workspace back at its native
  size, `test-geomancer-field-ui` (8 checks) and
  `test-geomancer-field-lifecycle` (enemy turns with fields, native waits) pass.
- **Display buffer (`0x1E00`):** peaks at 5,920 bytes (Equip Items, every item
  owned), 2,592 in battle Status, 2,336 in deployment Info and 2,328 on the job
  wheel.
- **Mystic Knight name (11 tiles, one more than any original job name):** the
  native glyph writer does not clip. Deployment Info on all six units, one of
  them a Mystic Knight, uses the same 2,336 bytes, the heap is restored after
  each close, and the name renders in full. Battle Status uses the same
  layout. World menus are covered by `test-all-new-jobs-in-game`.
- **Passing Step path buffer:** its budget is at most 2
  (`ffta_turn_step_remaining`), so the native path builder returns at most 3
  of the 32 entries.
- **Blue Magic lesson write** (`A7BCA`, `unit+0x40+index`): unreachable,
  because no expansion action 347–445 carries the learnable flag. The native
  learnable set is unchanged. Checked in `test-memory-fixes`.
- **VBlank free hook** (`ffta_copy_owner_free` from the native VBlank task
  free): it writes only for owner-registered allocations. VBlank frees only its
  own task entries. Nodes are linked after `next`/`magic` are set, and unlinked
  before they are cleared, so an interrupted walker never sees a half-built
  node.
- **Fixed high EWRAM:** compile-time asserts now guard the tight boundaries:
  - the job bank ends at the AI choice root (`0x0203F728`);
  - the inventory view (460 × 4 bytes) ends at the copy-owner root
    (`0x0203FF30`);
  - the owner root ends at the scope pointers (`0x0203FF44`).

  The shop tail and list capacities were already covered by guard tests.
- **Stale bounds** (`0x0203F800`/`0x0203F400` in persistent.c,
  action-snapshot.c, unit-copies.c and evaluated-units.c) are looser sanity
  limits. The real heap end is `0x0203F000`, and magic/self checks prevent
  misuse. The dead `0x0203F800` clear test in `ffta_on_unit_clear` is superseded
  by `ffta_job_clear` (heap end `0x0203F000`). The installed code is unchanged;
  editing sources that aren't rebuilt would leave untested divergence.
- **Art source limits:** `art-party-heap.c` and `art-workspace-allocation.c`
  build only the historical art stage, which palette removal patches by
  authenticated bytes. They keep their original values so that parent
  reproduces, and now say so.
- **Auto-Potion roster:** the installed code compares against context+`0x7280`,
  the restored list tail. The `0x0203C000` branch applies only to standalone
  builds.
- **Law checks and the menu figure arena:** a failed law copy under heap
  exhaustion falls back to the native "false", which is conservative and
  memory-safe. The new menu figures have the same tile and object sizes as
  their donor jobs, so their demand on the 4,080-byte arena matches the
  original figures'.
- **Quest namespace (IDs 376–460):** display only. Quest records cover
  376–502, so nothing overflows (`notes/reward-popup-review.md`).

## Whole-game pass (September 26)

Deterministic real-core sweeps on the final ROM with the [game_pass](../scripts/game_pass.py) monitor. At every checkpoint it verifies:
- resident IWRAM code is unchanged;
- the stack low-water mark stays above resident code;
- unused high EWRAM is untouched;
- the heap chain is valid;
- the screen renders.

- [test-game-pass.py](../scripts/test-game-pass.py):
  - **world:** Sprohm pub, all 8 shop Buy and Sell tabs with teaching info, Prison, every party unit's Equip Items slots, Pick Abilities slots and job wheel, Item List, Area List, System, Law and map Info;
  - **deploy:** unit Info with every submenu on all six units;
  - **battle:** 40 party turns of enemy AI;
  - **save:** a normal save and load round trip;
  - **reactions:** forced enemy attacks on holders of every new reaction.

  Browsing must change no unit record, clan inventory/AP/format data or job-state bank. The exceptions are native fields: the job-discovery bits, the leader's town position and the derived Jump cache.
- [test-action-sweep.py](../scripts/test-action-sweep.py) runs all 85 new actions through the native battle menus with the declared Giza layout. The two party profiles cover the ten new jobs (Human sidecar lessons, Montblanc as the Moogle). Each action is checked for its effect, item consumption and the monitor. Expected no-target cases: Field Remedy needs a curable ailment and Requiem an undead enemy.
- Also run on a copy of the player's own save: the world pass passes.

Checked and safe during the pass:
- The AI workspace (`0x4504`) is a pathfinding node pool bounded by map size, not content.
- Measured stack margins: battle 1,720, reactions 1,372 and actions 1,436 bytes.
- Reactions fire as designed: Counter Draw, Vengeful Pulse (50% of HP lost), Nature's Wrath, Stone Skin (Protect) and Counter Rhythm (Slow).

## Evidence

- [test-memory-fixes.py](../scripts/test-memory-fixes.py), 42 checks:
  - only declared bytes differ, and each trampoline reaches its declared target;
  - reaction masks for 15 reactions × 44 status bits equal the clean game (the
    parent differed in 109 cases);
  - `7A094` and `8D0C4` match their siblings on all five tabs (337 weapons,
    for example);
  - no expansion action is learnable;
  - frame bounds;
  - both fallbacks run without a stack snapshot at low SP and keep it at
    ample SP;
  - `ffta_job_load` clears `JST1`.
- [test-memory-fixes-ui.py](../scripts/test-memory-fixes-ui.py), 24 checks,
  real core, Giza fixture with a Viera Mystic Knight
  ([profile](../scripts/fixtures/mystic-knight-profile.json)):
  - Info on all six units;
  - equipping runs the traced `7A094`, and the rebuilt list holds 337 valid,
    unique IDs;
  - Save Now writes `JST1` to flash, and a cold resume restores the job bank
    with no marker in live RAM.
- The final ROM also reruns
  [test-palette-removal-ui](../scripts/test-palette-removal-ui.py) (Info, all
  item lists, battle start and Status) and
  [test-enchant-weapons-ui](../scripts/test-enchant-weapons-ui.py) (real
  enchanted strikes through the new executor path) with `--current`.

Not covered: campaign playthrough, physical hardware, and the 13-actor art
capacity scenarios.
