# Repeatable encounter sources

Candidate `eabce3b98536510e40a8ec5893ecd9bd2996566c`, September16 Pacific.
No game bytes changed in this checkpoint. The changes correct source audits
and add deterministic native selection/lifecycle checks.

## Correct formation identity

The original audit mixed the randomizer's shifted record layout with native
event IDs. Native records are IDs1..442 at `0854CD54 + 40*id`, with member count
at+0 and the48-byte unit-template pointer at+4. Templates span
`0852A4D0..0854BB30`. Native ID442 is valid;443 starts text, not another record.
The earlier441-record audit omitted the first record and mislabeled the rest.

`08009C18` publishes a primary map/deployment formation and an optional
secondary enemy formation. `0800A024` selects the secondary when nonzero;
the battle setup caller at`08092E92..08092EA6` passes that record to`0808F8E8`.
Moving a roaming clan changes its map formation while retaining its enemy
roster. Reading event+2 alone is insufficient. All three source enumerators
now use event+4 when nonzero, otherwise event+2, with native IDs throughout.

The mistake did not change the unit templates used by the previous theft or
Capture tests. It did misattribute some templates to adjacent missions.
In particular, Max's Oathbow is in **Brown Rabbits109, native formation273**,
not Blue Geniuses108. Dark Gear's color-clan witness is White Kupos110,
native formation274. Earlier report labels are historical; use the corrected
current ledger for encounter attribution.

## Native roaming coverage

`test-roaming-source-access-cached` uses authenticated boot-installed IWRAM
from the exact candidate and declared world inputs. It runs original routines,
without substituted callback results or scripted queue outputs:

- `CF7F4`: progression gate, weighted selection across placed locations,
  native queue insertion, duplicate exclusion and four-occupied-slot limit.
- `CF690`: reveal/aging; `D17C4`: world-map event selection.
- `9C18`, `A018`, `A024`: map and enemy formation resolution, including another
  map location while preserving the clan's actual enemy roster.
- Lifecycle mode: `D2E6C` finishes appearance; six native daily updates expire
  the offer; `30168` marks the selected encounter on battle return; `D0F74`
  retires it. Both branches regenerate the same encounter and select it again.

All30 origins pass two map permutations. All30 also pass expiration and
battle-return retirement with ordinary mission completion receipts already
set. No persistent one-time gate prevents later generation. Every one of the
20 learnable monster actions has an actual generated enemy-template/mastery
witness. All24 original monster jobs occur, including all20 capturable jobs.
The approved Goblin and Thundrake edits remain sufficient; no further encounter
change was found necessary.

Four rare items have these native repeatable roaming witnesses:

| Item | Clan | Native enemy formation |
|---|---|---:|
|68 Vajra|Brass Dragoons20|214|
|116 Zanmato|Clan Belmia4|182|
|313 Dark Gear|Clans22/23/29/30|218/220/232/234|
|314 Wygar|Clans11/24/29/30|196/222/232/234|

Use the retained native theft controls to distinguish actual stealability:
formation196's Maintenance unit is not the required positive witness.

## Colored-clan and League cycle

`test-clan-league-cycle-cached` declares late story completion and the first
earned League qualification. Subsequent flags, offers, acceptance, completion
effects and cooldowns are native outputs. The all-win path is:

`Clan League46 -> Yellow Powerz107 -> Blue Geniuses108 -> Brown Rabbits109
-> White Kupos110 -> Clan League46 -> Yellow -> Blue -> Brown`.

The controlled failed-Brown path instead returns from White Kupos to Yellow,
then Blue and Brown. The remaining16-day posting cooldown is honored before
reaccepting Yellow; calendar eligibility is an explicit input. White Kupos
resets the native four-result counter; four successes restore League
qualification, while fewer restart the colored-clan route. The next League
qualification and recurring Oathbow source are therefore connected, rather
than inferred from repeat bits. The native selected Brown roster contains the
same Oathbow-bearing Sniper used by the retained successful theft test.

These are complete native consumer chains with controlled battle outcomes,
not a rendered campaign, actual victory, first qualification acquisition,
recruit offer, equipment theft playback or save acceptance. Those broader
acceptance scopes remain in V03/V05/V06 and R02. Shara's arrival remains A03.

## Reports and reproduction

Use `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only` with
the IDs below. Its prerequisite checks reuse the unchanged assembly and exact
capture; read-only ledgers do not require a rebuild.

| Run (UTC) | Accepted evidence |
|---|---|
|`20260917T035842.347875Z`|649 roaming-selection checks/60 cases;795 lifecycle checks/60 cases; corrected source ledgers; nine completed all-win League cases. Overall run remains failed at the missed-cycle cooldown.|
|`20260917T035947.913651Z`|105 checks/eight missed-cycle cases, including its native cooldown and second Brown opportunity. Only the failed branch was repeated.|

IDs: `audit-current-monster-sources`, `audit-vanilla-teaching-sources`,
`test-roaming-source-access-cached`, `test-roaming-source-lifecycle-cached`,
`test-clan-league-cycle-cached`, `test-clan-league-missed-cycle-cached`.
Full reproduction uses the combined cycle ID; the missed-only ID preserves
earlier successful-branch evidence when investigating that branch.

Private artifacts live in the candidate directory under timestamped
`roaming-access-*` and `clan-league-cycle-*` folders. Reports record ROM/capture
hashes, fixed seeds, input scope, assertions and actual queue/cycle outputs.
The runner's top-level ROM label is the historical foundation image; the
consumer reports and verified assembly identify the tested candidate.

Earlier diagnostic failures remain preserved: `034429` caught an overbroad
prerequisite fingerprint of the read-only audit; `034930` caught a test's
unnecessary equality check across a mission-only hook; `035424` exposed the
formation identity error. No full integration or fresh capture was run.
