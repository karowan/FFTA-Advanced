# AI timing regression and v0.7.7 optimization

**Later benchmark correction:** the measurements below preserve the historical
frame-sampled phase-zero seed procedure. Current tests pin the same declared
seed once at native candidate-constructor entry, because changing hook costs
can move a main-loop RNG advance across the earlier sample. The planning timer
still begins at phase zero; all locked vanilla frame counts remain identical.
See the [fully learned follow-up](ai-under-four-seconds-2026-09-28.md) for the
trace evidence, current procedure and final local candidate.

The v0.7.6 baseline had a substantial AI planning regression in these controlled
comparisons. With original starting abilities, mean planning time was **1.193 s
in vanilla and 4.353 s in v0.7.6 (3.65 times as long)**. With fully learned primary
jobs, it was **3.129 s versus 11.331 s (3.62 times as long)**.

The initial investigation changed no game code, ROM, release selector or player save.
The v0.7.6 desktop game was relaunched and its visible window verified separately.
Initially only measurement scripts, fixture support and documentation were added.
The subsequent authorized optimization and its acceptance are documented below.

## Results

Each cell below averages three native decisions with seeds 0, 5 and 18. There
are 24 matched pairs / 48 decisions in the final two runs. Every pair had the
same canonical unit inputs, ordered available-action list and final action and
choice IDs. Each decision completed successfully.

| Original job | Starting abilities: vanilla | Starting abilities: mod | Fully learned: vanilla | Fully learned: mod |
|---|---:|---:|---:|---:|
| Human Soldier | 0.960 s | 2.913 s | 2.584 s | 7.144 s |
| Moogle Black Mage | 1.842 s | 9.275 s | 4.459 s | 22.932 s |
| Nu Mou White Mage | 0.904 s | 2.662 s | 2.735 s | 6.474 s |
| Viera Archer | 1.066 s | 2.562 s | 2.740 s | 8.773 s |
| Equal-weight mean | **1.193 s** | **4.353 s** | **3.129 s** | **11.331 s** |

For the broader interval from unit activation to published choice, including
camera/turn preparation but still excluding subsequent movement and attacks:

| Profile | Vanilla | Mod |
|---|---:|---:|
| Starting abilities | 3.231 s | 7.438 s |
| Fully learned primary job | 5.168 s | 14.415 s |

Raw planning-frame counts, in seed order 0/5/18:

| Job | Starting vanilla / mod | Fully learned vanilla / mod |
|---|---|---|
| Soldier | 54,59,59 / 166,179,177 | 167,137,159 / 448,395,437 |
| Black Mage | 110,110,110 / 555,552,555 | 272,263,264 / 1378,1362,1369 |
| White Mage | 54,54,54 / 157,160,160 | 135,197,158 / 350,418,392 |
| Archer | 74,44,73 / 170,119,170 | 139,158,194 / 483,512,577 |

## What was measured

The unmodified US ROM and the exact installed mod each cold-load the same
disposable early-town SRAM and construct their own Giza battle through native
menus. No emulator state crosses ROMs. Vanilla owns its original heap; its
fixture never receives expansion-only canaries. Vanilla requires Down to select
Missions because its pub starts on Rumors; the mod puts Missions first. All
fixture navigation is outside the timed interval.

The measurement uses the existing twelve-object Giza formation, including the
judge. The focus actor is AI-controlled; the other ten combatants are on the
opposing player-controlled side and are deterministically Waited. This gives
each focus actor the same target population without preceding autonomous turns
altering the case. HP/max HP are 999 and MP/max MP 100; reactions, supports,
combos and secondary commands are cleared. The starting-skills profile retains
original mastery; the fully learned profile sets all mastery bytes for the
primary job. Original equipment and combat values come from the vanilla fixture.
These are controlled workload comparisons, not a sample of ordinary campaign
turns or a balanced six-versus-five encounter. White Mage results are not a
healing-party benchmark. New jobs, later maps, lower resources and active custom
effects remain outside this measurement.

Every pair hashes the same 262 non-name bytes of all twelve canonical unit
records at the actual planning boundary. Only the two native enemy-name bytes
are excluded. The native action-list order is also compared. The RNG seed is
set at phase 0, after camera/setup delays; it is not repeatedly forced during
the search. The earlier activation-only seed pilot is retained as exploratory
evidence, not included in the final averages.

The planner owner is `0x020101FC`; its phase halfword is `0x020156EC`.
The script requires observing phase 0 for the focus wrapper, then measures until
the planner first publishes phase 8. Native disassembly at `0x080C045C` dispatches
these phases; phase 0 creates candidate data, phase 1 advances its evaluation,
and the phase-7 tail publishes phase 8 at `0x080C1058`. Inputs are observed every
video frame, even while a button is held, to avoid missing the start boundary.

Time is emulated frames divided by `16777216 / 280896` (59.72750057 Hz).
Boundary observation is quantized to frames (approximately 16.7 ms), not a
stopwatch or a host CPU throughput measurement. Running the desktop game at the
same time can change how quickly tests finish on Windows, but does not change
these emulated-frame intervals. The private test core is distinct from desktop
mGBA 0.10.5; results describe emulated game latency, not a measured desktop FPS.

## Where the delay is

In the fully learned cases, phase 1 used 1,224 total frames in vanilla and 6,894
in the mod. Its 5,670 additional frames account for **96.46% of the total added
planning time**. Later movement/attack animations have not started at the end
boundary, so they cannot account for this result.

A second, read-only replay samples CPU PC/LR once per video frame for the seed-5
Black Mage and Archer. It uses the authenticated core ABI without entering an
instruction-hook context. All four replays reproduce the original final EWRAM
byte for byte, with the native host dispatch pointer unchanged.

For the mod's Black Mage, 1,193 phase-1 samples include:

- 210 in native status scanning around `0x08133ADC`;
- 161 in `ffta_storage_format`;
- 121 in `heap_container`;
- 56 in `ffta_job_state`;
- 41 in canonical-unit lookup and 33 in unsigned division;
- 131 in the native `0x08000000` page, also represented by 131 vanilla samples.

These periodic samples identify candidates for investigation; they are not
exact function costs or additive inclusive profiles. Native status-scan samples
return predominantly to `0x09240FD5`. Disassembly of the installed ROM maps this
to the Viking reaction-readiness call of `0x08133ADD(unit+0xE8,5)`, which scans
44 status bits. The source in `viking-state.c` checks reaction readiness before
checking whether the unit actually equips either Viking reaction. The measured
profiles explicitly equip no reactions, yet this work still appears repeatedly.

The other prominent path is validation of copied/evaluated units and their job
state: repeated save-format checks, canonical-origin arithmetic and traversal
of the native heap to validate a tagged temporary unit. This cost is paid while
forecasting ordinary original-job actions too.

A next optimization should investigate early eligibility checks before reaction
readiness work and reuse of already-validated ownership within one forecast.
Do not weaken pointer/ownership validation, cache across lifetimes without
invalidation, or remove real cross-class effects. A fix needs identical-input
timing replay plus the affected snapshot, law, reaction and copy-lifetime tests.
No optimization or causal ablation was performed here, so this report does not
claim a particular change will recover a particular fraction of the delay.

## Reproduce

Use [the declared plan](../scripts/ai-timing-test-plan.json), sequentially:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/ai-timing-test-plan.json -Only ai-timing-fixtures
& '.\Test Expansion.ps1' -Plan scripts/ai-timing-test-plan.json -Only ai-timing-original-jobs
& '.\Test Expansion.ps1' -Plan scripts/ai-timing-test-plan.json -Only ai-timing-profile
& '.\Test Expansion.ps1' -Plan scripts/ai-timing-test-plan.json -Only ai-timing-starting-jobs
```

Reuse the paired fixtures only while their authenticated ROMs and setup inputs
remain applicable. After a ROM change, rebuild the two fixtures. The profiler
authenticates the compiled code bytes before assigning source names to sampled
addresses; a different binary or core must fail closed. Do not substitute an
old mod savestate into a new ROM just to make a timing comparison run.

The runner's successful status means the investigation and its integrity checks
completed, **not** that the mod met a performance threshold. This run establishes
a regression. The exact binary and evidence identities are:

- Vanilla SHA1: `4ac05441f4de70a4ec3dd932116346c61b8783d9`.
- v0.7.6 SHA1: `b7d011755c998e23935a53d416bea252fef356ef`.
- Test core SHA256: `b7008c1a834fef42c9c2b66594855f63924d419fb33af2863e86b1a032d03560`.
- Fixture run: `build/expansion/test-runs/20260927T223808.092368Z`.
- Final fully learned run: `build/expansion/test-runs/20260927T224532.523586Z`.
- Read-only profile run: `build/expansion/test-runs/20260927T224826.790857Z`.
- Starting-skills run: `build/expansion/test-runs/20260927T225122.597807Z`.
- Detailed full-skill report: `build/expansion/ai-timing/measure-20260927T224533.860263Z/report.json`.
- Detailed starting report: `build/expansion/ai-timing/measure-20260927T225123.905229Z/report.json`.
- Profile: `build/expansion/ai-timing/profile-20260927T224828.135095Z/report.json`.

Private ROMs, disposable states, screenshots, complete logs, input scripts and
per-frame phase transitions remain under ignored `build/`. Preparatory failures
and exploratory results are retained and excluded from final averages. No full
integration suite was run: this request concerned AI latency only.

## Optimization acceptance (v0.7.7)

The follow-up request authorized fixing the measured slowdown. The candidate
SHA1 is `97e3c99087d206001b968c760270ef46223e10a4`. Full-skill decisions now
average 328.25 frames (5.4958 seconds), versus 676.75 frames (11.3306 seconds)
in v0.7.6 and 186.9167 frames (3.1295 seconds) in vanilla. This removes 51.5%
of total mod planning time and 71.1% of the added delay in this workload;
it does not establish vanilla parity or a campaign-wide average.

Changes avoid readiness checks for unequipped reactions, use an authenticated
native permission mask instead of repeatedly scanning 44 status bits, and let
damage formulas request only the status flags they consume. Narrow queries
retain frozen action values when an action is active. Canonical unit lookup
uses exact bounded arithmetic instead of ARM7 division, and aligned format
signatures use word comparisons. Ownership, heap-chain and copy-lifetime
validation remain in place. No cross-action flag cache was introduced.

`ai-forecast-fast` passed for this binary, comparing full/projected flags and
damage factors against the previous binary, including active cross-class buffs
and reactions, all five races, frozen snapshots, allocation/copy lifetimes,
freed/reused memory and forged interior pointers. Its accepted run is
`build/expansion/test-runs/20260927T233135.241432Z/report.json`.
Full-skill timing is recorded in
`build/expansion/ai-timing/measure-20260927T233255.701814Z/report.json`.

Final assembled acceptance is justified because this completed optimization
changes shared damage forecasts, reaction readiness and unit-state resolution
used by all jobs. Run the 11 declared `chemist-progression` checks: state-codec,
effects, fixture, periodic, movement, AI, save, UI, learning, laws and status-records.
These exercise real effect execution and cross-class/copy/save consumers beyond
the paired original-job timing sample. Also run `ai-timing-starting-jobs` and
the release package checks. This is the bounded assembled acceptance gate,
not a claim of full campaign coverage. Final results follow below.

### Accepted results

| Workload | Vanilla | v0.7.6 | v0.7.7 | Reduction from v0.7.6 |
|---|---:|---:|---:|---:|
| Starting abilities, all four jobs | 1.193 s | 4.353 s | 2.019 s | 53.6% |
| Fully learned, all four jobs | 3.129 s | 11.331 s | 5.496 s | 51.5% |
| Fully learned Soldier | 2.584 s | 7.144 s | 4.219 s | 40.9% |
| Fully learned Black Mage | 4.459 s | 22.932 s | 8.740 s | 61.9% |
| Fully learned White Mage | 2.735 s | 6.474 s | 4.398 s | 32.1% |
| Fully learned Archer | 2.740 s | 8.773 s | 4.627 s | 47.3% |

All 24 matched pairs across both skill profiles retain identical canonical
inputs, available-action lists and published action/choice IDs; all succeed.
The same fields also match the preserved v0.7.6 runs. The new fully learned
maximum is 528 frames, versus 1,378 previously and 272 in vanilla. The result
still has measurable overhead: 1.76x vanilla in the full-skill workload and
1.69x with starting skills. Remaining expansion-state/snapshot validation has
not been removed to obtain a faster number.

Accepted final runs, all against the candidate SHA1 above:

- All 11 assembled checks: `build/expansion/test-runs/20260927T233903.605277Z/report.json`.
- Starting timing: `build/expansion/test-runs/20260927T234104.174066Z/report.json`;
  raw evidence `build/expansion/ai-timing/measure-20260927T234105.220959Z/report.json`.
- Timing acceptance: `build/expansion/test-runs/20260927T234426.726457Z/report.json`;
  receipt `build/expansion/ai-timing/budget-20260927T234427.763288Z/report.json`.

The reusable `ai-timing-budget` step reads both completed reports, authenticates
the current ROM, original core and preserved fixture hashes, requires all 24
pairs and matching choices, and rejects any decision more than 5% above the
reviewed v0.7.7 frame count (rounded up). Original vanilla frame counts must
also stay exact so workload drift cannot silently pass. In-memory negative
checks confirm that partial, stale-ROM, slower and changed-choice evidence is
rejected. This protects the measured improvement; it is not a vanilla-parity
gate. Never raise the budgets automatically after a failure.

After running both timing profiles, invoke:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/ai-timing-test-plan.json -Only ai-timing-budget
```

Release packaging reuses the passed 11-step assembled run, validates the clean
ROM/BPS roundtrip and preserves the existing save directory. The already-open
desktop game continues on its old ROM until the player saves and reopens it.

Local release `0.7.7.zip` was built and selected successfully; archive SHA256
`d272c175bb3fd2a32d2684568e6b67fddfcfd51fa7e184bffb97551402e6763d`.
The launcher validated SHA1 `97e3c99087d206001b968c760270ef46223e10a4`
without opening a game. All 32 package checks passed in
`build/release-tests/20260927T234612.340987Z/report.json`, including patch
reconstruction, corrupt-input rejection, release switching and save isolation.
Runner receipt: `build/expansion/test-runs/20260927T234611.522278Z/report.json`.
That static packaging plan's generic runner ROM field names the unrelated
historical combat probe; the package test authenticates the selected release
archive and its actual target independently. It is not new gameplay evidence.
The Git content guard and diff whitespace check also passed. No upload, commit,
player-save migration or running-game interruption was performed.
