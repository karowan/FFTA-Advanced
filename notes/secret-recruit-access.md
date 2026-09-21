# Secret recruit access audit

The installed candidate `55f231768cfffdbfc2383191f8648716d452375d`
preserves all eleven original named/special recruitment rules and their fallback
rows. All 128 mission-item records are unchanged. The added Quin route remains
the only recruitment change; its original reward and saved-history guard remain
covered by [Quin's review](quin-history-review.md).

## Sources

Record numbers below are internal mission IDs, not the player's displayed
mission numbering. Carried items feed the native selector on eligible missions;
they do not directly grant the character. Candidate tests use the original,
repeatable Prison Break record60 as that consumer.

| Recruit | Native source | Retry policy observed |
|---|---|---|
| Eldena | Elda's Cup, mission item4 | Carried-item selection; duplicate name excluded |
| Littlevili | Clan League46 | Repeatable mission; original League prerequisites remain |
| Cheney | Snake Shield, item101 | Carried-item selection; duplicate name excluded |
| Pallanza | Wyrmstone, item22 | Carried-item selection; duplicate name excluded |
| Quin | Missing Prof66; added Mythril Rush111 | Added route keeps its extra monotonic acceptance history |
| Lini | The Hero Gaol, item64 | Carried-item selection, including original +10 chance bonus |
| Ezel | Reconcilliation377; Bored?384 | Original completion unlocks monthly retry dispatch |
| Babus | With Babus379; Doned Here!385 | Original completion unlocks monthly retry dispatch |
| Ritz | Mortal Snow380; Ritz's Offer386 | Original completion unlocks monthly retry dispatch |
| Shara | A Maiden's Cry381; hidden candidate template400 | Failed dispatch reposts; successful return unlocks original town arrival. Unaccepted arrival clears its temporary gate on the next offer. |
| Cid | Cleanup Time382; Cid's Mission387 | Original completion unlocks monthly retry dispatch |

The six ordinary named recruits use normalized name pointers for uniqueness.
The five story characters use their original unit types. Current job does not
control either identity. Ezel and Babus use special races, so an ordinary-race
job substitution is not a valid fixture for them.

## Acceptance and history

Native acceptance writes flags600..604 for Ezel, Babus, Ritz, Shara and Cid.
These are **acceptance receipts**, not dedicated death detectors. The candidate
routine rejects an offer when the corresponding flag is set, including after
the character is absent. The audit executes the real Yes copy/receipt block
`080807D0..0808083A`, verifies the copied candidate and flag, removes the character
as a declared absence input, and executes all relevant candidate routes again.
It does not claim to animate a death, dismissal or the complete recruitment UI.

The additional native gates618..622 retain their original behavior. The monthly
Ezel/Babus/Ritz/Cid retry records bypass their respective additional gate, while
still obeying the acceptance receipt and current-roster exclusion. Shara's
template has no such exception. The meaning and writers of618..622 are not
established by observing their readers alone.

Do not add blanket recruitment retries or clear any of these flags. The added
Quin route already has its separate saved-history safeguard. Preserve the
original six ordinary named recruits' absence policy on unchanged sources.

## Deterministic evidence

All checks use the hash-verified current fixture, unchanged current ROM and
native ARM routines. No fresh battle fixture or broad integration run was used.

- `20260916T234736.447526Z`: candidate access, **90 assertions** across16 routes
  and seeds0..15. Every intended character was produced; ordinary random offers
  also had failed seeds. Unaccepted offers retried, duplicates were excluded in
  roster slots6/23, and original history/acceptance gates were preserved.
- `20260916T235119.723155Z`: posting, **110 assertions** across14 records.
  Whole native generation and all eight town filters yield13 visible sources
  plus hidden400. All13 visible offers expire, enter their original cooldown,
  retire and return under the same declared eligibility. Four original special
  mission completions write the native completion flag and unlock their real
  monthly dispatch, which then generates the correct special candidate.
- `20260916T235404.206285Z`: acceptance, **38 assertions**, all five story
  characters. Native copying and receipt writing succeed; all nine original/
  retry candidate routes remain blocked with the character present or absent.

Private reports are under the candidate's `secret-recruit-access`,
`secret-recruit-posting` and `secret-recruit-acceptance` folders. Runner logs
preserve each script revision and its ROM/fixture inputs. Early failures caught
two fixture assumptions: special races cannot take ordinary jobs, and expiry
includes a cooldown before queue removal. Neither required a gameplay change.

Run only the affected plan ID through `Test Expansion.ps1`:
`test-secret-recruit-access-cached`, `test-secret-recruit-posting-cached`, or
`test-secret-recruit-acceptance-cached`. Their declared prerequisites refresh
read-only source ledgers and verify assembly reuse. Candidate generation is
not rerun by the acceptance-only phase.

## Shara dispatch and arrival connection

Current candidate `eabce3b98536510e40a8ec5893ecd9bd2996566c` preserves these
original routes. `test-shara-arrival-cached` executes native construction,
pub listing, member assignment, ten daily countdowns, completion and the
20-day cooldown. Failure leaves completion1148 clear and dispatch381 returns;
success writes1148 and generates automatic hidden400, without accepting Shara.

Town scene group31 (native event217) runs the original condition program at
`08A1AB3E`. With the dispatch completed and acceptance603 clear, town arrival
through `080D17C4` selects400 and queues Shara scene129. Current town position
and scene are declared transition inputs; output selectors are not supplied.
Scene129 begins at`089BA688` with native opcode`1A 6D 02 00`, clearing temporary
gate621. Its actual recruit instruction at`089BA91D`, `36 0C`, schedules a
type12 offer through `08123294`; the continuation at`081222C8..0812232C`
selects400 and calls the real candidate constructor. The test stops before the
visual recruitment scene launch. Merely generating her does not set603.

An unaccepted-exit instruction from the same scene (`089BA9A5`) sets621.
Executing that original instruction and repeating native town selection still
queues scene129; its entry clears621 and the real recruit bridge produces
Shara again. This connects the retry gate without inventing a new dispatch or
clearing acceptance history. The test supplies the unaccepted exit, rather
than playing every dialogue branch leading to it. Existing all-five-special
acceptance/duplicate controls remain applicable to the unchanged consumer.

Reports preserve the diagnostic history:

- `20260917T041342.032374Z`:66 completed checks for success/failure dispatch,
  cooldown and hidden arrival. Overall run failed because its arrival query
  omitted active town context; no game defect was found.
- `20260917T041845.964973Z`:22 checks pass for native town selection, original
  scene opcodes and candidate bridge, both first and unaccepted-repeat offers.
  The continuation authenticates the earlier native dispatch output and failed
  report by hash. It does not repeat the completed countdown cases.

Use `test-shara-arrival-cached` for full reproduction, or
`test-shara-arrival-continuation-cached` for the retained arrival-only input.
Both run through `Test Expansion.ps1 -Plan scripts/integration-test-plan.json
-Only <ID>` with only read-only prerequisite checks. Private timestamped
reports and states live under the candidate's `shara-arrival-*` directories.

## Remaining acceptance scope

These checks establish original eligibility consumers, not acquisition of every
campaign flag or carried item. The subsequent
[native clan-cycle audit](repeatable-encounter-access.md) now proves the next
Clan League qualification through the four colored-clan missions, plus another
cycle after a missed Brown Rabbits mission and its native cooldown. Outcomes
are declared inputs to native completion, not played battles.
Shara's dispatch381-to400 source and unaccepted retry are now connected through
native town selection, scene opcodes and candidate construction. A03's source
audit is complete within those controlled-consumer boundaries. Complete
cutscene navigation, roster replacement/full-roster behavior and cold saves
remain V02/V05/V06; this audit does not claim they were played.
Carried-item recovery and broader campaign reachability remain with A01/V06;
the already accepted Quin save evidence remains applicable to its unchanged code.
