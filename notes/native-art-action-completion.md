# Native class actions: retained water proof and missing Moogle streams

Full engineering remains required. Only image quality and authored poses are
deferred. E01-E05 remain open. No installed package, player save or launcher was
changed; all declared runners below are terminal.

## Actual defect and correction

Private candidate `e1a87ecde67f265f666d3ab9d7e50ba401370633` failed generic
Moogle Chemist122's legal knife74 Fight. At attack24, wrapper020229D8+44 became
FFFFFFFF. Its old body02020E28 still contained valid idle resource268 graphics;
that stale memory was not evidence of a valid native owner or successful attack.
The real wrapper requested mode87 (base84, facing3). Both corresponding native
descriptor slots42/43 were empty. The body observer correctly rejected the
invalid pointer and was not weakened.

Native21618 returns -1 when its selected descriptor's sequence pointer is zero.
Wrapper975DC stores that result at9768A. Detached execution reproduces that
exact store for all four facings while leaving the old body untouched. A
same-race knife command-stream control keeps the valid body instead. The full
native constructor21618 is unchanged from clean ROM; wrapper975DC contains the
existing gameplay allocation/status hooks and is authenticated against the
gameplay parent. An initial diagnostic incorrectly required the whole wrapper
to equal clean ROM; that failed baseline assertion is retained.

`scripts/complete-generated-actions.py` adds an explicit reproducible final
construction stage over the connected parent. It completes six formerly absent
land entries:

| Class | Slots | Native command template | Actual weapon flow |
|---|---|---|---|
| Moogle Chemist122 |42/43|Moogle job39/resource37 knife stream|knife74|
| Moogle Chemist122 |60/61|Moogle job42/resource40 rod/staff-family stream|staff149|
| Bard123 |42/43|Moogle job39/resource37 knife stream|knife74|

These are command/timing templates, not replacement donor characters. Graphics
reference the focus class's existing generated idle pixels. Each native graphics
entry gets an aligned32x32 layout; commands, durations and events retain their
original bytes. Non-graphics/control entries are copied intact. Existing slots
are never overwritten, native jobs are unchanged, and no runtime code or RAM
layout changes. Repeated placeholder poses remain explicitly unfinished art.

The stage uses3604bytes at ROM1F00000 inside the existing action reservation's
unused tail, with a checked1F80000 limit. Two owned-resource table entries change;
every other byte outside the new data is checked unchanged. The resulting
private candidate is **`5a14e6c7b69f9f9984a6965faf5740d3b318e41a`**:

`build/art/connected/5a14e6c7b69f9f9984a6965faf5740d3b318e41a/live-palette-view.json`

Its private selector is `build/art/action-completion/current.json`. The installed
7507ca5c package and defaultfa3d12b4 palette build remain unchanged. This stage
must be carried into the final E05 pipeline, including after any later compositor
candidate. Its parent source manifest is pinned in the component. Running the
old connected builder alone does not apply this newly separate final stage.

## Evidence

The generalized `test-samurai-fight.py` selects the requested native job/race and
an actually permitted weapon before native allocation. It retains the original
Samurai default and its baseline-comparison contract. Each flow uses the existing
authenticated world checkpoint, native menus, fixed formation/HP/RNG inputs,
608 every-frame action observations, real positive damage and next-turn return.
Moogle cases explicitly repurpose the generic Viera slot before allocation;
inherited stats are fixture inputs, not growth/save acceptance. Auxiliary weapon
and effect actors are recorded but not independently accepted by these checks.

On e1a87ecd, the following flows passed without repeating earlier passing cases:

| Class/weapon | Report under build/art/class-fight | Checks |
|---|---|---|
| Human Dark Knight/sword1 |20260919T021830.835448Z/report.json|4915|
| Bangaa Dark Knight/sword1 |20260919T022029.368917Z/report.json|4915|
| Nu Mou Chemist/knife74 |20260919T022045.758767Z/report.json|4915|
| Geomancer/rod135 |20260919T022103.836272Z/report.json|4915|
| Bard/instrument201 |20260919T023133.522400Z/report.json|4916|
| Dancer/knife74 |20260919T023149.181150Z/report.json|4915|
| Mystic Knight/rapier88 |20260919T023205.366892Z/report.json|4916|

Moogle failure: `build/art/class-fight/20260919T022121.606456Z/failed.json`.
Its runner022028.682828Z stopped before Bard/Dancer/Mystic; those were subsequently
run once in023132.501946Z. Cause proof passes48 checks at
`build/art/native-missing-action/20260919T023133.194358Z/report.json`, SHA256
`2abb52ece284d16e187d1d97d6ee19e66fdccc35e16b305d40fc2f13c09f10c1`.
Earlier diagnostic wrapper-authentication failure remains at023041.072491Z;
runner023040.418709Z skipped its three later flows.

On corrected5a14e6c7, runner023438.208627Z passes construction and all three
affected flows, each4916checks:

| Flow | Report under build/art/class-fight | Damage | SHA256 |
|---|---|---|---|
| Moogle Chemist knife |20260919T023440.726333Z/report.json|17|21b063e43d11bfa82e2963074e4a4b556f21fcc4764d5cdb6269e527f6823ef7|
| Moogle Chemist staff |20260919T023459.071301Z/report.json|26|b92c61b23919ebd07132de2c1c2c5d441cb1fcdfd0d69a7e93ee62fb63fa10db|
| Bard knife |20260919T023517.172690Z/report.json|17|894200ca191af1c09df366a0643820496af09252276213db9c0a07be8e49ea4f|

Root inspected the retained Moogle knife next-turn screenshot. Native menus
returned. This visual inspection is not final-art acceptance.

`test-completed-action-contract` passes2219 checks in runner023748.398636Z.
It independently proves all1680 old land/water descriptor slots unchanged except
the six explicit additions, complete existing graph/code preservation, exact
native commands and generated payloads,12 native constructor cases across four
facings, and a byte-exact deterministic completion-stage rebuild. Report:
`build/art/action-completion/contracts/20260919T023749.032200Z/report.json`, SHA256
`2f46194a4dab2fee0216dc63c7def2de78d5ffb8a3e380b5b387d99ef5a3399b`.

## Historical water evidence reconciled, not rerun

`test-engineering-water-reuse` passes13188 checks in runner021255.106156Z.
It authenticates every retained report/fixture/raw capture from the all-ten
water index, then follows actual ROM pointers to prove the20 original resource
graphs equivalent to e1a87ecd:1680 descriptor slots,596 distinct sequence pairs,
3401 frames, complete command metadata/layout/tile payloads, actual job/race/
land/water routing and allocation tables. Current palette interpretation agrees
with the retained actual hardware data. The observed ROM remains historical
6443725d; the candidate hash is separate and `newRuntime:false` is explicit.

Report: `build/art/all-class-water-evidence/20260919T021255.737230Z/report.json`,
SHA256 `29451e28620d30d484b01bcddf1576f80712eb30c82592151cff5345a31e571c`.
Initial020600.602710Z failed because raw pointer equality ignored relocation;
020809.241506Z failed because a local loop variable shadowed the evidence index.
Both are retained. The corrected pointer-following audit first passed13157 checks
at020853.960347Z before actual routing/allocation checks were added.

The completion contract establishes transitive preservation of every old e1a87ecd
graph in5a14e6c7, including all water resources; it adds only six previously empty
land entries. No old actor pointers are resumed, rewritten or relabeled as a new
runtime. Water sampling remains8frames for jobs116/118 and1frame for the others.
Neither audit proves water attacks or changed compositor/heap/effect lifetimes.

## Next engineering work and reproduction

E01 remains unresolved: this stage preserves the e1a87ecd compositor, whose
response gate still fails six metrics. No new timing result is claimed. E02
still requires remaining permitted weapon families, Combo/secondary/action and
effect consumers, and UI reconciliation. E03 still needs reachable demanding
capacity/lifetimes; E04 must reconcile real campaign/save evidence; E05 must
integrate this final stage, review and package the accepted assembled build.
Do not rerun passed generic Fight flows merely for a changed ROM hash.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/native-art-test-plan.json -Only build-moogle-action-completion
& '.\Test Expansion.ps1' -Plan scripts/native-art-test-plan.json -Only test-completed-action-contract
& '.\Test Expansion.ps1' -Plan scripts/native-art-test-plan.json -Only test-moogle-completed-knife,test-moogle-completed-staff,test-bard-completed-knife
```

These are separate construction/contract/playback steps. Their presence in a plan
does not itself justify repeating them. No broad integration suite ran here.

## Current Samurai and Viking generic Fight closure

Read-only comparison followed actual ROM tables and both attack slots42/43.
The graphics opcode is the byte at frame+9, not the whole halfword at+8 (which
also contains duration); the initial diagnostic read the latter and found zero
graphics. That empty diagnostic was not accepted as equivalence. Corrected
comparison finds8/10 graphics entries per slot and changed tile payloads for
both classes. Thus old Samurai5fe7c35d and Viking714f45eb Fight evidence cannot
be reused for the current graphics, despite preserved command counts. This is
a consumed-asset change justification, not merely a changed ROM hash.

Runner20260919T034833.506569Z passes both targeted current5a14e6c7 flows:

| Test | Report | Checks | Outcome |
|---|---|---|---|
|test-current-samurai-fight|build/art/samurai-fight/20260919T034834.276542Z/report.json|4915|katana106; damage28; HP60/MP17|
|test-current-viking-fight|build/art/class-fight/20260919T034853.152620Z/report.json|4915|axe392; damage14; HP47/MP14|

Both observe actual native action slot42,608 every-frame action samples, real
positive damage and next-turn return. Together with the previously recorded18
class/weapon-family flows, generic Fight now covers all20 permitted combinations.
This does not independently accept auxiliary weapon/effect bodies, Combo,
secondary abilities, other action kinds, natural acquisition or full-game timing.
All runners are terminal. E02 stays open; no installed package/save change.
