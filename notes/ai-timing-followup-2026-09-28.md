# AI timing follow-up after v0.7.7

Public v0.7.7 is tag `f1f575f075ee726ca05be578464127172bf5cf1a`, released via
PR #5 and successful workflow run `36360250815`. The downloaded player ZIP
SHA256 is `ab0f9811e6152b65f8e369150091a5f8cb87ac8935bc815a45c173c8dfb65699`,
matching local packaging. Its accepted ROM remains
`97e3c99087d206001b968c760270ef46223e10a4`; the public release and local play
channel are not modified by these follow-up experiments.

The v0.7.7 frame-boundary profile replayed the complete final RAM exactly for
Black Mage and Archer seed 5. Black Mage phase 1 has 374 samples versus 133 in
vanilla. The old unconditional status scan no longer dominates. Remaining
samples include native damage/stat calculation, heap ownership validation and
physical-action lookup. These are samples, not exact inclusive function costs.
Evidence: `build/expansion/ai-timing/profile-20260927T235254.552001Z/report.json`.

The first experiment checks modifier values before HP/MP interception and
checks Spotter eligibility before its other predicates. It preserves the
full/dynamic effects rather than assuming a unit's job proves a neutral
multiplier. ROM `990c8a57841c16ae3c4e3e4c67811e8e9835e98a` passed native
effects, expanded formula equivalence and timing, but the full-skill mean only
fell from 5.4958 to 5.4274 seconds. Retained run:
`build/expansion/test-runs/20260927T235827.682599Z/report.json`.

The second experiment removes duplicate barrier-ledger calculations from pure
forecasts. The existing publication helper already rejects non-RESULT phases;
the extra calculation therefore had no consumer. Real execution retains the
ledger. In particular, native Fight executes within a child QUERY and publishes
after closing it: that caller explicitly requests the deferred amount, while
pure effect/menu previews do not. Trauma Ward's actual damage calculation and
candidate publication still run. The custom physical composition is guarded
at its generated call site with an exact-match builder assertion.

Acceptance scope: `cp-effects` now includes original Fight and Fire with
Trauma Ward, recovery reactions, and actual TBN consumption/miss retention.
Run the eleven-step `chemist-progression` assembled gate because this completed
batch changes shared physical and magical calculation used by every class,
including the deferred native executor path. Follow with `ai-forecast-fast`,
new `ai-timing-fixtures`, both timing profiles and `ai-timing-budget`. This is
a final assembled candidate check, not a full campaign acceptance. Preserve
the released v0.7.7 channel until a subsequent release is explicitly packaged.

## Final local result

Candidate `32d199815e4530ed18587f22bc7ea88250b87e5a` is on
`codex/ai-forecast-followup`, separate from the published release. The compiled
overlay contains 92,432 bytes; its SHA256 is
`8b90191e2bc8f6a0f4d5e277fd28ad9341a562983d178fcceefdabfb678fabe5`.

| Mean planning time | Vanilla | Published v0.7.7 | Follow-up |
| --- | ---: | ---: | ---: |
| Fully learned primary skills | 3.1295 s | 5.4958 s | 5.2363 s |
| Starting skills | 1.1929 s | 2.0189 s | 1.9198 s |

This is another 4.72% / 4.91% improvement, still 1.67 / 1.61 times vanilla.
The 24 paired cases cover Soldier, Black Mage, White Mage and Archer, seeds
0/5/18, and both skill profiles. Every matched available-action list and final
choice agrees. The controlled Giza workload uses one planning actor against
ten other combatants with deterministic Wait behavior; it is not a campaign
average or a normal balanced-party battle. Times measure emulated planning
frames, excluding camera preparation and attack execution.

Final candidate evidence (private, ignored):

- `build/expansion/test-runs/20260928T000800.711770Z/report.json`:
  `cp-effects`, `cp-fixture` passed. The effects check includes 1,059 assertions,
  35 Trauma Ward hits, 21 TBN hits and three TBN misses.
- `build/expansion/test-runs/20260928T000834.505656Z/report.json`:
  `ai-forecast-fast`, `ai-timing-fixtures`, `ai-timing-original-jobs`,
  `ai-timing-starting-jobs` passed.
- `build/expansion/test-runs/20260928T001119.538667Z/report.json`:
  `ai-timing-budget`, `ai-timing-profile` passed, without raising budgets.
- Measurements: `build/expansion/ai-timing/measure-20260928T000902.606797Z/report.json`
  and `build/expansion/ai-timing/measure-20260928T001003.219891Z/report.json`.
- Profile: `build/expansion/ai-timing/profile-20260928T001120.587078Z/report.json`.
  Black Mage and Archer seed-5 replays reproduce final RAM byte for byte.

The preceding candidate `329db87382c9715a24eeb86364e603c5501cca6d` passed
all eleven assembled checks across runs `20260928T000427.543242Z` and
`20260928T000529.450813Z`. The first run passed the state codec, then stopped
on a test-harness symbol lookup: the inherited TBN grant helper was not an
overlay export. The test now authenticates its retained parent entry before
calling it. The remaining checks then passed. The final candidate additionally
restricts the deferred Fight ledger to its enclosing RESULT consumer; only
affected effects, fixture, equivalence and performance checks were repeated.
There is no eleven-step final-ROM acceptance receipt or campaign acceptance
for this follow-up; it has not been packaged or promoted to the play channel.

## Remaining bottleneck and next investigation

Black Mage phase-1 samples fell from 374 to 341 (vanilla 133); Archer fell
from 178 to 173 (vanilla 79). Repeated temporary-unit ownership and snapshot
lookups remain prominent. Black Mage has 26 PC samples in `heap_container`,
14 in `extra_slot`, and 38 return-address samples in workspace `allocated`.
These are coarse frame-boundary samples, not inclusive costs or call counts.

The manifest symbol dictionary collapses duplicate static function names.
Consequently its profile labels some overlay helpers as `native/unresolved`.
For this analysis, extract `.text` and `.rodata` from `jobs.elf` with
`arm-none-eabi-objcopy -O binary`, require byte equality with the authenticated
`jobs.bin`, then resolve the retained PC/LR samples against every sized `t`/`T`
row from `arm-none-eabi-nm -n -S`. Preserve address-qualified duplicate names.
This identifies `allocated@09a538f4` rather than misattributing its samples to
native code. Relabeling uses the existing samples and needs no new gameplay.

The next substantial experiment should measure repeated validations within a
single forecast and consider a validated view with that exact lifetime. Do not
remove ownership checks or cache raw temporary pointers across free/reuse,
mutation, or snapshot boundaries. Keep frozen action values authoritative and
retain the forged-pointer, reused-copy and binary-equivalence checks. Additional
native stat calculations and custom physical-action lookup remain candidates;
the present measurements do not establish their inclusive cost.
