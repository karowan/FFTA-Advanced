# Viking implementation state

Root continuation: this handoff is historical; the agent finished and its
source was merged. Root now works alone. Queued Absorb Damage/Gil Snapper
execution and native display-result values pass in combined candidate
`c32c11e88c6b228b1fd451cd5d4c30bdcf37b66c` and standalone Viking
`c60b181ba44b816a9fa754a573eb58434f3b68c2`, report
`20260915T080445.472975Z` (all 37 steps, unchanged inputs).
The independent builder now installs the shared native queue entry directly.
See `notes/queued-reactions-and-counter-draw.md` and the root
`IMPLEMENTATION-STATE.md` for current evidence and remaining rendered
playback/law/AI/save acceptance. Older hashes and gaps below describe the
original handoff, not current root progress.

Worktree `.worktrees/viking`, branch `jobs/viking`. Work in progress, not a completed job or accepted release. Player ROMs, saves and windows remain untouched.

## Source and reproduction

Committed checkpoints: `c12cc20` Viking foundations; `6268370` adoption of root `77efe09`; `d80bb14` portable common evaluated fixtures; `4bbad8c` fresh executor capture. Checkpoint `d6a512b` adds native War Cry/Provoke and native table relocation. Checkpoint `80ac1e8` adds visible icons. Adopted root `2eb9e52` as `b639713` and shared context `eff9489` as `b42171b`. Checkpoint `bbfe06d` adds Stormcall actual HP gating, strict peer cleanup and outgoing factors. Checkpoint d2c2071 adds Tsunami and corrects MP interception exclusions. Shared ce83f72 is adopted as 1a1c833. Current uncommitted integration sweep installs both Viking reactions, all fourteen help entries, all nine action UI scenarios, Combo UI/chain coverage, native legal-action/law checks and strict copied-state lifecycle scenarios.

Run `Test Expansion.ps1 -Plan scripts/jobs/viking/test-plan.json -Suite viking`, selecting focused checks with `-Only`. Tests use deterministic scripts and fixed seeds, never agent play. Reports and candidates remain ignored. Fresh fixture caches verify every relevant input and output hash before reuse.

Builder consumes `job-state/current.json`, currently `02d4fee3f935e410e2c88d1d41ce91f7ff03fcbf`, over the ce83f72 Samurai snapshot release and accepted engine `ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`. It does not rebuild newer engine sources and claim acceptance. Current tested private candidate: **19fd6f0829d2f7f18d7f4e2f613248489eb9d3cb**. Previous consolidated candidate **2d40ba56303a8fa12bd51f7f2046e198b3cd5e69** differs only at two bytes: offsets1031D79 and1031E05 changed60 to62, enabling native Silence bypass flag20 for War Cry and Provoke.

## Evidence

Newest bounded evidence:
- **20260915T054512.819689Z PASS:** nine-step affected acceptance on19fd: all nine real UI actions/cancel/payment/next-turn/cold owned records (254 checks); War Cry/Provoke timers/immunity/accuracy/icons (1443); all eight Bangaa jobs with Reaving and MP/Silence thresholds plus native element/weapon laws (6368); actual owned Snapshot/manager/evaluated lifecycle/copyback/roster cases (38).
- **20260915T054153.386209Z partial:** nineteen steps passed on2d40 before the new legal-action check caught the real Silence bypass bug. Passed native actions, Sea Legs, theft, all14 help entries, all9 actual menus/cold, inherited347, Stormcall, geometry/weapons, state/icons, teaching/growth/stock, outgoing factors (1808), Tsunami (1062), both reactions (4055), and actual Tempest Combo initiation/participation/native donor/cold (43). The test runner stopped on legal-actions; followup054512 fixes and passes that plus previously unreached owned lifecycle. Do not label054153 itself a passed full run.
- `20260915T052229.151904Z`: Tsunami256 native direction/water/SeaLegs scenarios plus32 illegal occupied/uphill landings, with exact cost, nonvacuous hit/miss and environmental flags. Outgoing512 native cases plus128 Damage-to-MP scenarios verify both HP factors leave intercepted MP unchanged.
- `20260915T052142.113529Z`: first native Tsunami acceptance. Selected native result object+A/+B controls center; native98E7C retains legal displacement. Additional cold/UI/law/displayMP and elemental tests remain.
- `20260915T051537.131181Z`: 512 native outgoing scenarios covering Thunder, Stormcall, Thundaga cross and Pillage, Opportunist and Challenged together; exact shared snapshots verify recipient-order independence, source KO affecting later actions, no self-qualification and reaction exclusion. More final-rounding/Counter/reflection cases remain.
- `20260915T051321.497431Z`: current rational finalizers retain all347 native/Iaido executor cases, 512 theft transactions, and Stormcall.
- `20260915T051047.984165Z`:128 native Stormcall scenarios plus64 query scenarios preserve complete EWRAM and RNG; Damage-to-MP never allows Slow.
- `20260915T050830.523147Z`: first739-based Viking inherited native and state/icon acceptance, including status4 forced-hit interception preservation.

Reports under `build/expansion/test-runs/` preserve source hashes, ROM hashes, fixed scenarios and logs:

- `20260915T050415.866087Z`: native icon getter, 256-value status enumeration, two distinct glyphs, exact shape and neighboring VRAM guards pass together with all state effects. Native visual display is installed; screen rendering acceptance remains pending.
- `20260915T050008.247869Z`: prior candidate174377 passes all original 347 executor actions plus inherited Iaido/axes, all 461 weapons across eight Bangaa jobs, native height/range and cross geometry, War Cry/Provoke state effects and lifecycle. The inherited RAM comparator checks exact descriptor relocation and identical native descriptor contents before normalizing only global context+0x30's pointer; all other EWRAM bytes remain compared.
- `20260915T045436.353161Z`: current candidate passes 336 native Thunder/Pickpocket/Thundaga differential cases. Its inherited comparison was initially red on that relocated descriptor pointer; resolved by the exact semantic assertion above.
- `20260915T045240.117778Z`: War Cry self/ally cross, exact three cures, Poison preserved, enemy untouched, T2 own-turn skip, Provoke64 seeds and native Immunity, S minus25 floor0 with friendly/beneficial exceptions.
- `20260915T044104.216475Z`: first fresh larger-owner Viking executor and inherited native regression accepted.
- `20260915T043754.645320Z`: adopted common state constructors, fresh game/save/cold/corrupt resume and evaluated copies pass with matching fresh fixtures.
- `20260915T043327.190465Z`: earlier candidate passes 512 theft-strike cases, independently matching original Steal Accessory/Armor inventory and equipment transactions; geometry/equipment and inherited native execution passed.
- `20260915T041944.850206Z`: earlier native growth/base getters, prerequisites, equipment teaching/mastery and every town acquisition gate.
- `20260915T041039.074190Z`: earlier native menu/preview/cancel/commit/payment/next turn and cold suspend resume for Thunder, Pickpocket, Strong-Arm, Pillage, Thundaga. New state effects still need actual menu/save tests on final assembly.
- `20260915T041517.017048Z`: **Stormcall red**. Slow can apply after damage miss or Damage to MP. The failing test remains in the declared suite; magnitude/result flags are not accepted proxies for actual HP loss.

## Actual scope and gaps

Thunder, Pickpocket, Strong-Arm, Pillage, Thundaga and Sea Legs have native behavioral coverage. War Cry and Provoke now install native applications, compatibility masks, status accuracy and lifecycle callbacks. War Cry cures Blind/Silence/Confuse and tracks T2 protection. Provoke currently applies/clears its owned mark; its outgoing per-recipient damage reduction is installed with frozen action-start challenger association. Opportunist and Challenged share a denominator1000 numerator before the sole final division, including native physical/magical/Fight and generated shared custom finalizers.

Absorb Damage and Gil Snapper are installed in the current sweep. Native main768 reaction cases plus32 KO cases passed in 052840 before the repeated-action fixture hit a stale native heap handle; the harness now renews native handles while carrying only observed persistent records/money. That failed run is not acceptance. Pending: shared reaction presentation queue; direct-HP writer provenance for displacement/fall versus primary damage; successful custom-status late-Judge transport (especially zero-HP refresh/miss and automatic cures); expanded cross-job reaction/reflection and final-rounding edge cases; actual icon/MP feedback visual inspection. Complete Combo execution, all14 help entries, native legal action/resource filters, all9 UI/cold, and owned lifecycle now have the bounded evidence above. Pure War Cry/Provoke custom-state AI valuation has not been enhanced; tactical understanding of Provoke is not promised. Fourteen allocated lessons are not fourteen implemented lessons. Existing old reports are bounded evidence, not acceptance of untested later code.

## Shared allocations and integration

Own ROM offsets `0x1240000..0x127FFFF`, checked erased before installation. Code begins `0x09240000`; descriptors `0x1260000`, applications `0x1260400`, compatibility masks `0x1260C00`, help `0x1270000`.

Root state owns heap reservation `0x0203F400`, records and native/footer lifecycle. Viking bytes4..7: War Cry timer, Challenged origin, Gil Snapper battle cap, transient critical HP accumulator (saturated100). Byte7 resets at primary action start/completion and lifecycle termination; no new persistent allocation. Use `ffta_job_state` and `ffta_job_origin`; copied events never mutate canonical peers by fallback. Root `2eb9e52` peer/roster release is adopted and strict same-owner cleanup is installed; no private persistence allocation.

Native applications93/94 and Tsunami99; descriptors211/212 and Tsunami218; visible keys31/32. Native tables have100 application/mask rows and219 descriptors, leaving other jobs reserved slots untouched. Root confirmed icons31/32 use OBJ tiles **1EC..1EF**, and shared dynamic pool begins1F0 (`0x97098` operand F8); icons are installed and native getters/VRAM guards passed050415. Root composes the pool once with DRK28/29 and Chemist30.

Shared hook overlays: compatibility133A58; S accuracy131220; physical final1300E2; weapon drain/effect exclusions130654/130688; post-magnitude131B4A; physical eligibility/magnitude callbacks; five theft callbacks; all bounded caller references to prior Centered event/end-turn callbacks. Manifest records every relocation and hook. Descriptor/application/mask native literal users now target expanded banks; root must centrally combine all jobs' table additions and hook dispatch.

Adopted DRK action-context `eff9489`: actual HP loss, explicit origin/category, exact copies, claims, result object. Viking frozen flags reserve bit9 harmful and bit10 Opportunist; root also assigned bits16..21 for challenger token with named SHIFT/MASK constants. Same-action source KO does not change remaining recipient multipliers; cleanup affects subsequent actions. War Cry beneficial uses the separate beneficial provider. Do not infer reaction origin from incoming reactions_enabled. Selected native center is result object+A/+B.

Chemist optional `ffta_chemist_prevent_custom(context,2)` protects against Challenged after native hit/immunity, using actual recipient+8. Inoculation precedes Auto-Cureall, query does not spend. Provider absent locally until common composition.

Before handoff: update source/checkpoint and immutable reports here, stage source only, run `scripts/check-git-content.py`, commit to jobs/viking. Root cherry-picks source, composes shared hooks and state, then runs combined regression and council review.

## Current sweep and acceptance boundary

Following the user's large-sweep workflow, no new narrow runtime loops were run after 052840. Static investigation and coherent integration edits precede one consolidated deterministic run. Native critical provenance is A29DE..A29E8 setting recipient row+C bit20 after the critical formula. Flags25/26 and claim masks8/16 are root-reserved. The shared optional HP callback now also publishes Tsunami water MP loss to native row+C bit2 and signed row+20 at actual HP loss, including lethal hits; displacement still requires survival.

The custom successful-status late-Judge transport remains unaccepted: see notes/viking-result-transport.md. No native unit status or unused result-mask bit was silently assigned. Native legal action generation is in scope; tactical AI understanding of Provoke is explicitly not promised by the approved design. Root will integrate this branch and handle all later work and review alone after this handoff.

## Final handoff boundary

Root requested this agent finish its existing assignment and stop; no new job, queue expansion or testing agent is started. Source checkpoint parent is1a1c833; the final integration commit follows it on jobs/viking. The source-only handoff includes the native result-boundary investigation without an unverified event-bit allocation. Root must compose the five optional providers, shared outgoing finalizer, descriptor/application banks, lifecycle dispatch and OBJ pool with other jobs before combined regression.

The final gameplay change after2d40 is only the two verified native Silence-bypass flag bytes. Reuse unchanged native effect evidence rather than rerunning passed fixtures merely to attach a new global hash. A final source comment clarifies byte7 without changing emitted ROM bytes. The user player's ROM/save/window were not changed. This is an implementation handoff with explicit integration gaps, not an expansion release or full-game completion claim.
