# Connected campaign receipts and renewable sources

September17,2026. Candidate `1b070824a8dad4995434eee3ab40fa08187a6120` is
unchanged. This is targeted native verification, not a game implementation edit.

Run `20260917T083904.320777Z` passes1,344 assertions in the declared
`test-campaign-progression` plan entry. Its native consumer takes1.3seconds.
The ordinary current-candidate fixture is reused; no second battle fixture or
full integration suite is built or run.

## Connected history

The authenticated opening fixture contains only three mission receipts:
Snowball Fight768, Another World769 and First Mission1083. The test starts
with that actual flag bank, clan and inventory. It executes the original native
mission generator, acceptance and successful completion continuously through
34 original battle/story records. It never writes a later completion flag.

The previously untraced flags1084–1090,1092 and1126 are original interstitial mission
receipts, not separate magic unlocks. For example, Thesis Hunt4 earns771,
Encounter359 then earns1126, and The Cheetahs5 becomes eligible. Original
Marche's317, I'm Ezel!318, MonBro319, Bounty320, Llednar321, Into322,
Where's323 and Cid's Message325 similarly connect the main route. Mission27
connects Jagd Hunt14 to The Bounty15. The exact34-step route and every changed
flag are committed in the script and retained in its private report.

All34 original70-byte mission records remain byte-identical to the clean USA
ROM. Native selected-ingredient binding, consumption, quest-reward insertion,
rumor enumeration/reading and their relevant literal tables are independently
authenticated against the clean image. The installed native mission-completion
entry retains the expansion's intentional recovery behavior.

The installed shop consumer runs in all five town identities after each earned
stage. Every town-specific item set matches the approved acquisition ledger:

| Stage | Earned gate | Unique expansion teaching weapons |
|---|---|---:|
|S0|Opening|18|
|S1|Twisted Flow7|41|
|S2|Pale Company13|64|
|S3|Desert Patrol19|85|

## Earned ingredients and original rumors

After the main route, the same machine reaches all24 original renewable supply
witnesses. There are149 additional original source/side-mission completions,
including110 finite side missions used to free space in the original64-offer
queue. No cached offer is manually deleted. Original daily ticks retire expired
offers/cooldowns; already available side missions are completed with controlled
successes and their actual required inventory. No prerequisite item is inserted.

Examples of connected finite prerequisites now executed:

- Help Dad233 supplies item43 used by Cheap Laughs185; its Tonberry Lamp106
  pays You, Immortal163, earning930 for the Adamantite source221.
- Frozen Spring187 supplies Dragon Bone109; Hungry Ghost138 consumes it and
  earns905 for the Zodiac Ore source222.
- Original missions and13 actual rumor acknowledgments connect the Borzoi
  chain to Free Baguba81 and rumor43/history1323. The Mind Ceffyl211,
  Body Ceffyl212 and Spiritstone213 recipes then consume their earned inputs.
- Cotton Guard232 supplies Magic Cotton for Magic Cloth231.

The pub's original two selected-item commit blocks bind each acquired copy to
the accepted mission before native completion consumes or releases it. The
test checks quantities, including retained-item controls encountered on side
missions. Quest rewards use the original insertion code, stopped before its
graphics refresh. Random ordinary-equipment rewards are declined. If the bag
fills, native disposal removes an unneeded item while retaining the renewable
witness supplies and their finite prerequisites. The report records original
mission IDs, requirements, constructed rewards and selected calendar windows.

This joins the prior independent recipe fixed-point proof and575 native
source/reposting checks to earned history and inventory. See
[the dependency ledger](mission-item-dependencies.md) and
[original source gates](original-source-gates.md).

## Limits and remaining acceptance

Success outcomes are controlled. All30 territory identities are declared
placed, and recurring calendar months are selected directly. Story scenes,
battle victories, map placement and travel are not played by this test. Native
mission acceptance is called directly, not submitted through the rendered pub.
The original scene dispatcher and ending/postgame transition therefore remain
part of V06; a mission receipt alone does not prove their execution. All88 item
dependencies have the existing ledger/recovery coverage, but this test's earned
source endpoint is specifically the24 renewable witnesses. It does not claim
a complete campaign, all optional mission sequences or final release acceptance.

A01 stays open for the remaining campaign-placement/scene connection, with the
renewable receipt/rumor/ingredient gap now resolved. V06, R02 and R03 remain open.
No shipping ROM or player save changed.

## Evidence and reproduction

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-campaign-progression
```

The plan selects only this consumer, assembly verification and its two static
ledger prerequisites. Private output lives beside the candidate in
`campaign-progression-20260917T083905.312061Z`. It retains the full report,
script snapshot, four stage RAM captures and final RAM, with fixture, source,
ledger, candidate and capture hashes.

| Artifact | SHA-1 |
|---|---|
|Consumer source|`8e1891034f15d6f2408860cf96d2add5ac59ecbf`|
|Accepted report|`8f5325761e1604d2a0c61af665014570cc9eec1f`|
|Final native RAM|`ed7cff78fdc26893146d6d68d9ec02ef4f4f5c2d`|

Run082724 originally passed the178-assertion main-route/stock subset. Extending
the consumer exposed missing test orchestration: offer saturation in083005,
083109,083644 and083709; omitted pub item binding in083237 and083312.
These failed reports remain failed. They did not establish a shipping defect.
Run083740 passed the whole source chain;083904 added original-code/record
authentication and complete artifact fingerprints. None triggered a full suite.
