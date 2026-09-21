# Murasame and Kiyomori implementation

September 14, 2026. Private candidate
`41c51aa1f597b1bb6419166ccca3ddaa91597176`, based on assembled d156.
This adds two actions to the four-strike Samurai candidate. Main integration,
the remaining Samurai actions and supports/reactions are still outstanding.

## Implemented behavior

- Murasame350 requires a primary katana and costs8MP once. It targets an
  r2 center and heals living allies in the center/orthogonal cross. Healing
  is35% of each recipient's maximum HP, capped at140 before Centered and at
  missing HP afterward. One rational division preserves fractional base
  contributions before the25% Centered bonus. Centered is consumed once for
  the entire action, including multiple recipients.
- Kiyomori351 costs10MP and uses native fixed self-centered selection, with
  preview help. Its allied cross applies the native Shell and Protect stages,
  preserving compatibility, removal masks and timer cleanup. It retains
  Centered and receives no bonus from it.
- Both crosses have symmetric two-level height limits relative to the center.
  Murasame's selectable center also has the two-level height limit relative
  to the actor. Neither technique requires an unused named sword, consumes
  equipment, triggers Counter/Return Magic, reflects, enters Doublecast, or
  becomes unusable under Silence. Effective Charm allegiance and Confusion
  admission are explicit; KO recipients are rejected.

The callback for native magnitude selector25 delegates unchanged for every
action other than Murasame. Only Murasame substitutes target-max-HP recovery
for native White Wind's actor-current-HP reference. Original Barrier's effect
stages are reused directly for Kiyomori.

## Issues found and fixed by scripts

1. A preview cancellation recenters native targeting on an affected unit.
   The old test therefore executed on an ally's tile instead of its intended
   empty center. A diagnostic executor-entry breakpoint now asserts the exact
   selected coordinates. The production image separately executes the saved
   pre-cancellation preview; cancellation itself is tested for no resource or
   Centered consumption.
2. Barrier's inherited Doublecast flag was removed and the Silence-independent
   technique flag set. Native command-list code uses selector19 for Doublecast.
3. Barrier's zero area-height field was replaced with2, independently tested
   against native area enumeration at map corners and height boundaries.
4. Kiyomori uses native selection type3, as self-centered Chakra does, rather
   than a free cursor with nominal range0. Native range0 is not a reliable
   stand-alone self-targeting restriction.

The [Data Crystal ability structure](https://datacrystal.tcrf.net/wiki/Final_Fantasy_Tactics_Advance:Abilities)
provided targeting/property-field research leads. The source ROM, native
getters, disassembly and executed tests establish the behavior used here.

## Deterministic evidence

Focused six-step run
`build/expansion/test-runs/20260914T231748.349700Z/report.json` passed on this
candidate. It includes formula, native execution, actual menu use, both fixed
RNG seeds, MP costs, Centered, friendly/hostile area membership, native turns
and cold suspend-save resume. Test fixtures explicitly set only starting
jobs/equipment/AP/resources/statuses; native input and battle code produce
the results. Inventory and expanded AP are compared before/after/resume.

The complete twelve-step Samurai suite passed in one uninterrupted run with
unchanged inputs:
`build/expansion/test-runs/20260914T231932.500064Z/report.json`.
It includes the additional native Barrier status-differential and actual
Reflect cases. `restoration-native-report.json` records51,853 checks;
`restoration-game-report.json` records132 checks and six fixed action/seed
outcomes. The previous four-strike, lifecycle, law, retaliation and Protect
tests also pass on this same ROM. Exact source snapshots are retained in its
`source-review` subdirectory alongside the eight test reports.

These are deterministic local scripts, not delegated agent tests. This note
does not establish completion of Samurai or the full vanilla+ expansion.
