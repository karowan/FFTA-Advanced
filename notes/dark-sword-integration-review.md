# Dark Knight single-target resource sword arts

Implemented privately: **Sanguine Sword357** and **Infernal Strike358**, exactly the approved DRK-A2/A3 rows. Both require the ordered primary Sword1/Greatsword5/Broadsword6, r2 enemy, symmetric height3, ordinary A accuracy, non-elemental primary-weapon P, one strike, and no Fight crit/offhand/weapon drain/3E. Sanguine is95/100P and6MP; Infernal is75/100P and4MP. Existing physical support/defense inputs and native reaction compatibility remain in the native formula/dispatcher.

The accepted private ROM is `e3193a7e639d935e4c722011975029dc26177776`, built over frozen production `69a844aee6a536f29e2b00959acce62de1658e27`. The new code bank at `091C0000` is checked entirely FF before insertion. Private outputs are separated by input and output ROM SHA1. Shared production sources/build outputs were not edited.

## Exact native phase contracts

| Hook | Contract and reason |
| --- | --- |
| `12F8A4..12F8B0` | Native element helper(actor,action,item) falls back from action+02 zero to primary item+09 whenever weapon mode is nonzero. The new entry returns element0 only for357/358; originals replay their entire displaced prologue and continue at`0812F8B1`. Keeping action+05=1 preserves the approved P scaling. Changing only action+02 would be incorrect. |
| `A315A..A3166` | r6=result row, r9=action object. Native code loads `**row`, its signed HP delta at+1E, then calls`A2210`. New aligned entry calls exactly that native HP application once and measures unit+18 immediately before/after. Only actual positive HP removed qualifies, after HP versus MP redirection and overkill. It resumes`080A3167`, preserving native KO/critical-result bookkeeping. |
| `13467A..134686` | Native law kind10 calls`12F0D8`, which sorts/enumerates both weapons. For357/358 only, the replacement supplies the ordered primary weapon to the native category-law loop. It uses actor at originalSP+14, output buffer originalSP+08, action originalSP+1C, and resumes`08134687` with r5=count and native compare flags. Double Sword cannot make an unused offhand category violate this technique's weapon law. All other actions retain the original enumerator. |

All three use guarded12-byte push-r3 veneers. Entry C stacks are dynamically aligned for either native SP residue. There is no new global frame, provenance registry, permanent state, or allocation.

`ffta_dark_sword_plan` is a pure explicit-unit resource calculation. Sanguine computes floor(actualHPremoved/2), capped by floor(userMaxHP/5), then by missing HP for ordinary recovery. Its signed actor delta is added to native action-object+06. Native `A487A ->A22F0` applies that pending delta, including recovery clamping and KO bookkeeping for undead reversal. This is the same actor-delta mechanism used by native weapon drain; recovery never enters an enemy reaction chain.

Infernal removes min(floor(actualHPremoved/5),16,targetCurrentMP), restores exactly that amount subject to missing MP, and records target MP loss in result-row+20 with flag+0C bit2. Against undead, attempted recovery becomes actor MP loss capped at actor's current MP. The target's actual removed MP remains the accounting basis. Costs have already been paid by native action commitment; recovery cannot make the original4MP payment free.

Both riders reject actual same-side recipients. They receive the explicit result recipient after native recipient selection, rather than guessing from stale shared context or resolving a simulation unit to a live owner. A restorative primary cannot produce a positive damaging reference or a drain rider. Offhand restorative metadata does not affect the strike.

## Verification

`scripts/test-dark-sword.py`: **45,427 assertions** on the accepted private ROM.

- All347 original actions plus seven enabled axe actions retain full captured native executor results. All347 original actions retain results and EWRAM across all20 native law kinds.
- Original element getter and geometry differentials, both SP residues, aligned C entries, explicit target/source isolation,8,064 cross-job primary-category cases, and full r2/height3 map geometry.
- Independent native P control restores only the final coefficient hook;95/100 and75/100 match after full native P. Non-elemental formula cases vary primary element and resistance/null/absorption affinities; primary Healer remains restorative, offhand Healer does not change P.
- Actual recipient execution checks overkill, zero MP, capped HP/MP recovery, undead reversal, miss/hit, weapon3D/3E exclusions, one primary formula call and absence of Fight paths. Native law copies never invoke the battle-only drain entry and do not mutate live HP/MP/AP/storage.

`scripts/test-dark-sword-in-game.py`: **124 assertions**, all four racial-job/action combinations. A new fixture is generated from ordinary early-town SRAM through native pub, world travel and deployment. Legal Human Dark Knight Marche and Bangaa Dark Knight Jona select the correct teaching sword/learned lesson, move, choose the actual ability, preview, cancel, hit/miss, pay MP once, recover resources, advance turns, Save Now and resume in a new emulator from SRAM only. No AP/inventory changes or displacement occur. Screenshots were inspected for the ability names, MP costs and native preview.

`scripts/test-dark-sword-resource-edges.py`: **80 assertions** in20 additional actual executions from those verified UI confirmation frames. A target with3HP yields only1HP Sanguine recovery and no Infernal MP drain. Empty/3MP pools cannot overdraw. Actual undead Sanguine reversal kills a1HP user through native KO handling; the next unit takes its turn. Actual undead Infernal removes user MP and never creates recovery.

These tests validate the two actions privately. Future support-state multipliers, unrelated Dark Arts, broader AI tactical valuation and the rest of the expansion are not claimed complete here. The existing native law selector remains active; the only new law behavior is primary-only weapon classification for these two single-weapon techniques. No invented drain-specific law exemption is introduced.

## Required shared integration

1. Compile `src/engine/dark-sword.c` and `dark-sword-hooks.s`.
2. Add generated IDs DRK-A2/A3 to the shared physical definitions at95/100 and75/100; use categories1/5/6 for them and the existing axe predicate for the current axe family. Add both IDs to existing3D and3E exclusions. The private builder makes these exact changes to disposable copies of the shared sources for review.
3. Install the three guarded spans above, preserving all original bytes and continuations. Keep the current final physical hook, magnitude callback and eligibility callback as the common entry points.
4. Native action147 supplies a verified single-target physical donor. Set names from registry, MP6/4, element+02=0 with the explicit element hook, weapon mode+05=1, range+06=2, height+07=3, stages3F/01/01/01 and preview hint+16=0. The native147 animation completes correctly with both racial sword donors. No native action is replaced.
5. Extend the explicit-coordinate geometry wrapper to symmetric height3 for357/358 after native terrain/range checks. Do not read unitF6/F7 during Move previews.
6. Adapt the new private tests to `--current` after composition and regenerate a fresh matching battle fixture. Parent owns shared combat/build integration; no shared source mutation is necessary to inspect the complete private result now.
