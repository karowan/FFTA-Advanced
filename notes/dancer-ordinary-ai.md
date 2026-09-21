# Ordinary Dance admission and AI

Candidate: `37e423e27099f951b00e006c79303735166640b5`.
This is a bounded A05/A06 correction, not final expansion acceptance.

## Corrected behavior

All nine dances are now available while Silenced. Native `133E18` calls
`CDB3C` to detect Silence, then reads action field 20 through `CCD50`.
Field 20 is bit 9 of the flags word and means **allowed while Silenced**.
The combined Dance builder had cleared it. Native executor tests could still
cast dances directly, so their earlier Silenced execution results did not
prove normal menu or AI admission. The two hidden Dance reaction carriers
receive the same allowance; their existing effect/queue handlers are unchanged.

The other 76 new action records already matched the approved Silence contract.
The new audit queries field 20 for all 85 actions: Samurai, Dark Arts,
Chemist, Dance, axe techniques, non-incanted Reaving and Hide allow Silence;
incanted Reaving, Geomancy, other songs and Spellblade do not.

Native AI gives Witch Hunt a fixed positive component even with no target MP,
and gives Slow Dance value when Slow is already present. The two ordinary
row/area consumers now suppress only these no-op cases. Other native values,
probabilities, prevention, laws, damage forecasts and command costs remain.
The helper reads the target's MP/status only; it adds no prediction copies,
mutable state, save fields or allocation. Polka/Frolic damage remains useful
against an already weakened target. This is not a strategic AI overhaul.

## Deterministic evidence

Run through `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only`.
Use `test-dancer-ordinary-search` for the build, one current-ROM capture,
ordinary row/menu checks and placement. The corresponding `-cached` IDs use
verified assembly and the existing exact capture. For the player gate use
`test-dancer-silenced-player-cached`.

| Run (UTC) | Evidence |
| --- | --- |
| `20260917T005107.424177Z` | Baseline sweep on d559572; 812 assertions identify the Silence admission and two no-op AI failures. |
| `20260917T005740.395529Z` | Current assembly and one exact-ROM capture; 1,033 row, admission, native menu, purity and flag checks pass. Placement fails because the initial harness orders the groups incorrectly. |
| `20260917T005935.942962Z` | Corrected placement passes 72 assertions across 12 cases. Player replay stops at its old fixed-delay menu transition. |
| `20260917T010054.200953Z` | Only the player subset reruns. All 137 assertions pass across three Silenced Blind Dance casts (seeds 0, 3, 18), with actual hits and misses on two native enemies. |

The 128 ordinary row scenarios cover eight commands, valid/invalid factions,
self, KO/Petrify, MP depletion, existing Slow/weakening, wrong/missing weapon,
Silence/Confuse, Astra and Fury. Forbidden Dance's existing option search and
Passing Step's existing route tests retain their separate scope. Native menus
include every dance and all four Forbidden Dance choices, both as the primary
command and as a secondary command on the original captured Viera job. Their
enabled flags respond to MP, not Silence; AP and inventory remain untouched.
The historic `bow` label meant the same wrong-weapon input and is now named
`wrong-weapon`; the supplied item and tested behavior did not change.

Placement uses actual native rows, `BEF28`, a declared flat board and one legal
origin. Useful and Silenced cases produce legal positive placements; empty MP,
existing Slow, insufficient caster MP, blocked origins and distant targets do
not. Unit/stock/RNG, buffer boundaries and resident IWRAM arithmetic are guarded.
`BE5F4` interprets node group 0 as intended recipients and group 1 as collateral,
not an unconditional friends/enemies order. Offensive dances therefore put
enemies first. No production group-order change was needed.

The player script retains the real Viera sprite and native movement, command
selection, four-option list, preview, final prompt, execution, rendering and
turn handoff. It verifies the caster is still Silenced at confirmation, pays
14 MP once and applies only the selected ailment. Both enemies have positive
applications across the fixed seeds. Root inspected the captured choice list;
all four labels and MP values fit. The old 180-frame movement delay reached
the next input too early; the script now waits for the existing native menu
readiness observer. Failed reports remain retained, and passed row/placement
checks were not repeated after this test-only timing correction.

Captures and full reports remain ignored under `build/expansion/`. No full
integration run was warranted: this batch changes nine Dance admission flags,
two reaction-carrier flags and two no-op AI cases, with direct native/menu/player
consumers covered. No campaign, acquisition, cold-save or final assembled
acceptance is claimed. Remaining work is tracked in
[the implementation checklist](../IMPLEMENTATION-CHECKLIST.md).
