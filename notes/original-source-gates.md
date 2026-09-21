# Original acquisition gates

Current candidate: `eabce3b98536510e40a8ec5893ecd9bd2996566c`.
Source checkpoint September 16, 2026 Pacific. No gameplay bytes changed.

## Scope and reproduction

`scripts/test-original-source-gates.py` executes the installed native consumers
using the authenticated `fixture-two-geomancers` IWRAM and ordinary roster.
World progress, map placements, calendar, liberated territories and controlled
mission success are declared inputs. Results establish native eligibility and
repeatability under those inputs, not a played campaign, affordability, reward
collection screens or dispatch victory. V02/V05/V06 retain those obligations.

Use `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only` with:

- `test-original-source-variants-cached` for offline variant initialization;
- `test-original-source-renewable-cached` for original quest-source lifecycles;
- `test-original-source-pools-cached` for all seven original random pools;
- `test-original-source-shops-cached` for original shop teaching equipment.

The four plan entries share static source ledgers and assembly verification.
They do not rebuild the image, create new emulator fixtures or run other suites.
Source lifecycles and the interior reward-selector block use independent ARM
instances; the latter does not inherit translated whole-function state.

## Offline mission variants

Native name-task constructors `12B208` and `12B230` select kind1 and kind0.
The shared controller `12A084` copies that kind to context+6. Confirmation at
`12A3AE..12A3B4` calls `CEA80`, which generates the original identity values at
`02002168`/`0200216C` and uses another native RNG draw to set flag1445/1446.
Both outcomes are possible using the unchanged native RNG. No link consumer
is called by this path. Thus these flags are **not exclusively link-owned**;
this finding does not claim a full audit of every later networking consumer.

The deterministic test executes the actual confirmation call for both naming
contexts, with original RNG seeds0/1 (not substituted return values). It verifies
identities and flags, then runs full mission construction and pub enumeration:

| Flag1445 | Flag1446 | Original available mission records |
|---:|---:|---|
|0|0|326 Shining Lake|
|0|1|328 Sauce Recipe|
|1|0|330 Hero Of Yore|
|1|1|327 Shining Lake,329 Sauce Recipe,331 Hero Of Yore|

Original story gates778/779 remain required. These are variant-specific first
opportunities; the expansion must not manufacture completion receipts for the
unselected variants. Existing recovery authorization remains tied to an earned
original source. No link requirement or unconditional variant grant was added.

## Renewable quest sources

All24 acyclic witnesses from `mission-renewable-chains.json` now pass native
construction, pub listing, original reward construction, controlled successful
completion, cooldown and subsequent posting. Their direct story flag is also
tested absent, proving early posting is blocked. Twenty are ingredient-free;
four use the independently proven Magic Cloth/Mind/Body/Spiritstone recipes.
The witness's other original gates, month and map requirements are preserved.

The direct positive gates are original mission-completion receipts771..791,
905 and930, plus rumor-history1323 for the Ceffyl/Spiritstone family. Native
rumor43 enumeration, reading and persistence already have retained evidence in
`mission-item-dependencies.md`; that unchanged consumer was not rerun here.
Ingredients are declared inventory inputs in this lifecycle test. The existing
fixed-point proof supplies their acyclic routes, and existing native requirement
checks supply binding/consumption coverage. These are complementary proofs,
not a claim that this test collected every ingredient through reward dialogs.

## Random teaching-equipment rewards

Seven ingredient-free, repeatable original missions cover all seven used pools:

| Pool selector | Mission | Original progress gate | Calendar month |
|---|---|---:|---:|
|FFF1|215 Chocobo Help!|771|5|
|FFF2|219 Seeking Silver|781|1|
|FFF3|235 Into The Wood|784|4|
|FFF4|217 Ruins Survey|788|3|
|FFF5|218 Dig Dig Dig|789|2|
|FFF6|132 Water City|789|2|
|FFF7|131 Gulug Ghost|789|4|

The same native source lifecycle covers these seven (six also belong to the24
quest witnesses). Native second-reward selection at `D00C6..D010A` executes
20 fixed RNG-seed witnesses per pool against the actual original mission
record. All140 slots produce their exact table item. Their union includes all70
teaching items classified as repeatable random rewards. This proves positive
probability through renewable sources; it does not promise a fixed number of
attempts. The unused eighth pool remains excluded from acquisition claims.

## Original shops

The installed shop entry `CBDC0` enumerates all six categories in all five
original towns at native tier keys0/20 and liberated-territory counts0/30.
The territory count is read by original `CECF4`. Lists retain native byte-count
and output bounds. All109 original shop teaching items are present in the
late-tier/all-territory union. Original item records and stock bits remain
unchanged. Tier selection and appended town stock have earlier full native
comparison evidence in `acquisition-engine.md`; this check joins that behavior
to the exhaustive teaching-item ledger. Ordinary progress and territory inputs
are declared, not acquired by playing through this test.

## Accepted evidence

- Run `20260917T042942.286842Z`:86 assertions/four offline variant cases and
  124 assertions/20 shop combinations pass. The renewable consumer completes
  575 assertions/25 original mission lifecycles, then fails upon entering its
  separate interior random-selector block. That report remains failed, with
  its completed cases retained; it is not reported as a full pass.
- Run `20260917T043036.765508Z`: isolated selector passes281 assertions/seven
  pools. Only the failing independent component was rerun. The executable
  lifecycle and selector bodies retain their successful inputs; they are now
  separate plan entries for routine reproduction.

Private reports are under the candidate's timestamped `original-source-gates-*`
directories. The failed combined consumer is `20260917T042943.560128Z`;
accepted variants, shops and pools are respectively `20260917T042943.344188Z`,
`20260917T042943.949131Z` and `20260917T043037.825509Z`.
Each records candidate/fixture hashes, inputs and all completed cases.
The outer runner's legacy foundation hash is not the tested candidate;
assembly verification and each consumer report identify the candidate above.

No extra recovery service is justified by this bounded audit. A01/I10 retain
second paid recovery and broader campaign/save acceptance; the source audit
must not be presented as completed expansion acceptance.
