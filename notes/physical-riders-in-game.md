# Shatter Guard and Armor Splitter: fresh game acceptance

Both player-selected techniques pass on ROM `214e6722bbd68e53e9bb583f5074ad84241860e1`, engine `69dcde5cefeefc77d612cee5df2654a7fc466e36`. `scripts/test-physical-riders-in-game.py` completed **340 checks** across four fresh cases: each action with Protect absent and present.

The private fixture was generated from ordinary early-town SRAM through native pub, world travel, deployment and battle entry. It is under `build/expansion/probes/physical-riders-in-game/214e6722bbd68e53e9bb583f5074ad84241860e1/fixture`. The shared battle fixture was not overwritten. The generator now also accepts an explicit `--out` for future private fixtures; its default output is unchanged.

The test uses legal Soldier Marche with Breaching Axe456/mastered Shatter427 and Bangaa Gladiator Jona with Bearded Axe457/mastered Armor428. Disposable fixture setup assigns job/gear/AP,50MP,250 targetHP and native Protect/timer. All subsequent movement, ability selection, targeting, accuracy, application, turn advancement, suspend saving and cold loading use the running native game. Seeds only initialize the native RNG at confirmation; hit flags and damage are not forced. No user save or game file is modified.

Verified in each case:

- Native Move reaches4,14 while uncommitted unit coordinates remain stale; the technique correctly targets Ocyth at5,14.
- Preview leaves live HP, MP and Protect/timer untouched. Cancel restores the exact target record, retains the uncommitted movement state and releases the preview heap. Reopening does not grow allocations.
- Actual hits and misses both pay exactly6MP for Shatter or8MP for Armor, once. Neither knocks back the target. Facing confirmation advances to the next unit.
- Shatter clears Protect and its timer on a hit; a miss preserves them. Armor preserves both on hit and miss. The stored target stat range+1C..+29 remains unchanged.
- Inventory, extra AP storage, sorting preferences, gear and the reserved memory guard remain unchanged.
- Native Save Now writes SRAM. A new emulator instance cold-loads that SRAM and resumes the battle with MP expenditure, hit outcome, positions, Protect/timer, stored stats, inventory, AP and gear intact. The resumed Action menu still opens and cancels.

Screenshots of the actual previews were inspected. Shatter displays32 damage/40% both with and without Protect, agreeing with removal before P while the live Protect remains intact during preview. Armor's protected-target preview displays28 damage/40%. No stale Knock back banner appears.

Observed native outcomes (damage varies with native RNG):

| Action | Protect | Successful seed/damage | Miss seed | Remaining MP |
| --- | --- | --- | --- | ---: |
| Shatter427 | absent |0 /35|1|44|
| Shatter427 | present |0 /33,1 /32,2 /30|3|44|
| Armor428 | absent |1 /36|0|42|
| Armor428 | present |3 /31|0,1,2|42|

All captures, private states/SRAM and the combined report are in the hash directory. `report-427.json` and `report-428.json` preserve the separate170-check runs. The script defaults to the current shared battle fixture, accepts `--fixture <directory>` for a private fixture, and supports `--action 427` or `--action 428` for a bounded rerun.

This accepts the ordinary single-enemy gameplay lifecycle on the stated four-action build. The separate native suites cover exact arithmetic, primary3F/absorption, weapon-effect exclusions, original IDs and law simulations. Later builds must rerun against their own fresh matching fixture; these results are not evidence for untested future changes or every defensive reaction/interception route.
