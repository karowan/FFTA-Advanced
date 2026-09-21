# Council: native AP loss, theft and prerequisites

2026-09-14. **Accepted within the tested live-owner scope: 2,315 checks passed, no failures.** Reviewed the eight installed hooks in `src/engine/ability-hooks.s`, the helpers in `src/engine/abilities.c`, and their installation in `scripts/build-ability-probe.mjs`. Independently executed native instructions using `scripts/test-ap-writers.py`; no engine source was edited.

Frozen ROM SHA-1: **8dd238a15f4a3df6649ed66e0f4df0c7edd7adf0**. Native-consumer baseline SHA-1: **d3aaee20cb8f7c29f5033e620b3c54383d8625a7**. The script validates both manifest hashes and their base relationship, freezes the bytes, and resolves helper entrypoints from installed ROM trampolines rather than mutable build symbols. Native IWRAM comes from an isolated boot. No user game window or save is touched.

## Results

| Scope | Passing checks |
|---|---:|
| Original inline loss/theft register and full EWRAM comparison |528|
| Human extension AP and stat isolation at interior continuations |210|
| Original prerequisite counting, jobs2..43 |672|
| Explicit prerequisite lists, twelve affected jobs |192|
| Original native post-write equipment/availability continuations |144|
| Original Viera Cure coupling after loss/theft |24|
| Human extension post-write continuations, all34 new lessons |544|
| C-boundary alignment aggregate |1|

All **11,198 measured C-helper entries** have SP divisible by8. Both incoming SP residues0 and4 are exercised. Every tested interior segment and continuation restores its incoming SP. The script compares native live registers at each continuation, distinguishing low scratch registers killed by subsequent native instructions/calls from genuinely retained values.

## Native contracts preserved

| Installation | Verified inputs, result and continuation |
|---|---|
|C8B26|unitr10, required jobr5. The replacement computes countr2 and resumesC8B94, preserving outer rule indexr3 andr8..r11. NativeC8B94 compares the count with the requirement byte; C8BAA increments preservedr3.|
|1291AC|unitr8, lessonr2, maskr7=7F; retains raw AP inr1 and masked value inr0. Zero branches1291BE, nonzero1291B8. Native candidate-list construction stays intact.|
|129224|unitr8, lessonr5; returns raw AP inr0, native baser1=unit+40, low7 inr4; resumes129230. The retained native base is not subsequently used for the redirected write.|
|129264|unitr8, lessonr5, replacement AP valuer4. Writes through the ownership helper, calls nativeCD1FC and resumes129270 with its boolean result inr0. Subsequent native code restores availability if equipment teaches the lesson, otherwise removes incompatible selected abilities/recalculates equipment state, then callsCD620.|
|132E62|unitr8, lessonr5; returns raw AP inr0 and low7 inr4 at132E6E. Native cost comparison and selection behavior are retained.|
|132FC6|recipient=`*r6`, lessonr4. Writes nativeE4, setsr5=0 andr1=E4, resumes132FD2. The next native instruction reloads recipientr0; the old inline AP pointer inr0 is dead. CD620/CD364 remain native following this hook.|
|132FF8|victim=`*(r6+8)`, input lessonr0, cleared valuer5. Reproduces byte-truncated lessonr4, writes the victim sidecar and callsCD1FC, resumes13300E with its result. NativeCD544/CD620 postprocessing remains intact.|
|133D30|unitr6, lessonr8; raw AP inr0, low7 inr4, resumes133D3C before the native cost comparison.|

The original prerequisite loop atC8B62..68 accepts **type1 only**. The new helper matches this; type4 is intentionally not counted here even though general battle action lists accept types1/4. Its mastery predicate is `(AP & 7F) >= cost`, not equipment bit7. The original672-case matrix confirms equal counts and live outer registers across all regular jobs2..43 with eight AP patterns. The separate192-case matrix checks the twelve generated lists, including the six added Soldier and six Gladiator lessons, against their actual record type/cost. No widened interval or unrelated lesson contributes.

The old native prerequisite loop modifiesr4..r7 as scratch, but these values are dead atC8B94; the subsequent rule iteration reloadsr5 atC8BB2. Its saved temporary SP+20/+24 values are also not live after the replaced loop. The tested contract therefore compares count and outer control registers, not arbitrary dead loop scratch values.

For loss and theft writes, low r1..r3 after nativeCD1FC are call-clobbered scratch; the next continuation consumes onlyr0 and retained registers. The tests compare those live values and all EWRAM. Direct read hooks compare allr0..r11. The grant hook also checksr1=E4,r3 and all retained registers; its temporaryr2=E4 is dead before the next ordinary call.

## AP storage and native postprocessing

The Human interior matrix uses indices144/160/177 with five raw AP patterns and poison overunit+D0..107. Reads and writes reach the sidecar and leave that native stat/status region unchanged. The full post-write matrix then covers **all34 Human additions** with and without their actual teaching item, replacement AP0/25, both write paths and both stack residues. AfterCD1FC and native continuation, equipped lessons holdreplacement|80; unequipped lessons holdreplacement. Equipped cases also verify the poisoned stat/status tail is unchanged.

Unequipped scripted-loss continuation deliberately calls nativeCB54C afterCD654, so it can legitimately recalculate native unit state; the immediate write test separately proves no AP/stat alias. The original full-continuation differential checks the resulting native state byte-for-byte. Two Viera Cure indices26/33 are additionally tested through nativeCD620 for both write paths, preserving the original coupling.

No live-register, stack-alignment, AP-owner-address or original-semantic defect was demonstrated. The hooks continue using literalE4 for theft acquisition because the original native function does so; this audit does not introduce a different cost/mastery rule.

## Limits and rerun

The fixtures use live roster owners. Actual battle actor/victim copy registration, allocation and rollback remain governed by the separate unit-copy lifecycle tests. The script enters the installed effect segments and executes post-write continuations; it does not perform a complete theft battle, randomized scripted-loss selection from full battle state, or theft's laterCD364 job-unlock side effects. Template/count normalization and noncontiguous combat membership are separate work.

```powershell
. ./scripts/resolve-python.ps1
& (Resolve-FftaPython) scripts/test-ap-writers.py
```

Machine-readable evidence is `build/reports/ap-writers.json`. A fresh `scripts/test-ap-inline.py` run on the same ROM also passed4,465 checks, including the newly fixed primary preview7C392 and18,466 aligned helper entries; see `notes/council-ap-inline.md`.
