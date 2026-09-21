# Council: installed AP interior hooks

2026-09-14. The nineteen reviewed hooks are accepted within the explicit live-roster and registered party-copy scope below. Reviewed `src/engine/abilities.c`, `src/engine/ability-hooks.s` and `scripts/build-ability-probe.mjs`, and independently executed the actual installed instructions through `scripts/test-ap-inline.py`. No engine files were edited. The additional primary-list display read found during review is now fixed and tested; see the follow-up below.

Tested immutable in-memory ROM: `ability-core.gba` SHA-1 **8dd238a15f4a3df6649ed66e0f4df0c7edd7adf0**, baseline `content-inventory.gba` SHA-1 **d3aaee20cb8f7c29f5033e620b3c54383d8625a7**. Both manifest hashes and the base relationship are checked before testing. Helper entrypoints are resolved from the frozen ROM, avoiding concurrent symbol changes. Later builds can rerun this test; acceptance here identifies the exact inspected artifact. This supersedes the earlier nine-site acceptance on179fe529d45e0aa186200b7c05581b945fa46697.

## Results

**4,465 checks passed; zero failures.** The test uses boot-installed native IWRAM in Unicorn and does not launch the user's game or modify saves.

| Coverage | Passing cases |
|---|---:|
| Original inline AP register/memory differential against content-inventory | 432 |
| Reproduced N/Z result flags | 192 |
| Human sidecar interior hooks, indices144/160/177 | 324 |
| Complete original CCF44/CAF78/CB0D8 calls | 360 |
| New-item teaching grant and complete native removal/replacement, across item owners | 632 |
| Complete CCFB8/CD0EC typed-list calls | 100 |
| Native result award continuation for all34 Human extension indices | 1,224 |
| Original AP UI register/continuation/write differential | 600 |
| Human extension UI register/continuation/write differential | 600 |
| C-boundary alignment aggregate | 1 |

The aggregate covers **18,466 measured helper entries**, with no SP alignment violation. It records each helper address once when installing callbacks. Both incoming SP residues0 and4 are tested throughout the interior, new equipment, typed-list, results and UI matrices. Complete ordinary native calls check SP balance and r4..r11 preservation. Interior calls compare all native live low registers and callee-saved registers relevant at each continuation, and compare full EWRAM for original lessons.

## ABI and continuation review

The nine reviewed installation sites areCAFEA,CB148,CAEC4,49032,CCF7E,CB036,CB192,CD072 andCD19E. The builder preserves r3 before its aligned literal-load/BX jump. `ap_call` pops that original r3, saves r0..r7/LR, supplies the unit/lesson arguments, rounds SP down to an eight-byte boundary for C, restores the original frame and returns the helper result inr0. Original r4 remains protected through the saved frame while a preserved r4 holds its address during C execution. No changed live r1/r2/r3 value was demonstrated.

- Mastery-read shims reproduce r4=`AP & 0x7F` and resumeCAFF6/CB154/CAED0. Their helper result is the original raw AP byte inr0 at the boundary. The next native code loads race and cost before comparingr4.
- Results resumes4903E with r7 pointing at the actual sidecar byte, r4 containing the prior byte, r5=unit and r0=race. It leaves r6=lesson and other retained locals intact. Executing through490A6 proves that this pointer remains valid for the eventual native store4909C.
- Item grant resumesCCF8C, which reloads r1 from the teaching row before callingCD620. The displaced instruction's r0/r1/r2 values are dead there; the full CCF44 executions confirm subsequent behavior.
- Removal/replacement clear resumesCB044/CB1A0. Those instructions reconstruct unit and lesson forCD620; r0/r1/r2 produced by the displaced native write are dead. Complete CAF78/CB0D8 calls match native behavior for original lessons and clear only the availability bit for unmastered new lessons.
- Typed availability returns toCD07E withr0=`AP & 0x80`,r1=raw byte, preserving lessonr2 and slotr3. The native comparison atCD07E produces its branch flags.
- Typed-known returns toCD1AA for nonzeroAP orCD1BC forzero. Complete list execution checks both sides, with no equipment supplying an alternative lesson.

**Flag difference investigated and resolved as harmless:** C calls can change carry. A preliminary test comparing allNZCV bits therefore found differences after the mastery/availability ANDs. These are not live carry regressions: CAFF6..CB002,CB154..CB160 andCAED0..CAEE2 establish fresh flags before branching; CD07E explicitly comparesr0 before branching. The reproduced N/Z values match all192 cases. The final test checks those meaningful results instead of requiring dead carry to match.

## Semantic coverage

Full new equipment tests begin with one AP point, call nativeCCF44 to grant availability, then call each native setter to remove the teaching item. They verify129 becomes1 while the equipment slot becomes empty, including Human sidecar owners and other races' native-capacity additions. Full typed-list tests use five AP-byte patterns and five exact ability types, verifying output lesson IDs and count against the race records.

Results tests cover each Human index144..177 with zero progress, one point below cost and mastered progress; availability clear/set; gains1/5/50; both stack residues. They execute the installed pointer hook followed by the original native cost comparison, gain, clamp, mastery marking, notification-list update and store. Expected notification is written at the native result context+696. The low7 value caps at the lesson's native cost and mastery setsbit7. Already-mastered values remain unchanged. All tests preserve a poison pattern over unit+D0..107, proving these paths did not alias extended lessons into native stat/status bytes.

The accessor correctly keeps ordinary indices below142 inline and uses the ownership helper for Human extension indices on a validated live-state format. The additional UI matrix now covers registered party copies. Other transient-copy ownership and registration lifecycle are separate from these interior tests.

## Follow-up: ten party and command UI hooks

The new matrix compares all r0..r11, balanced SP, the exact reached continuation, and EWRAM mutations. It covers original lessons1/20/141 and Human extension144/160/177; raw bytes0/1/100/128/228; both stack residues; live and registered party-copy owners. The party copy is exactly `menu+1BE4`, registered through the five-word root at0203FF30, with its independent AP tail at`menu+7240`. The copied-owner tests deliberately retain a different live-sidecar value, proving they do not accidentally read the live unit's AP. Registration is seeded by the fixture; it does not test the constructor/copy callbacks themselves.

| Site | Native input retained | Continuation and result |
|---|---|---|
|7B9AA|unit=`*r1`, lessonr6|nonzero7B9B6, zero7B9FE|
|7B9CC|unit=`*r1`, lessonr6|7B9D8; rowr4+0E=AP, r1=r10|
|7C362|unit=`*(r2+r1)`, lessonr6|nonzero7C36E, zero7C410|
|7C49C|unit=`*r0`, lessonr6|nonzero7C4A8, zero7C53A|
|7C5D6|unitr1, lesson=`*(SP+524)`|7C5E6; row+0E=AP; r3 retains the actual lesson index|
|7C694|unitr1, lesson=`*(SP+524)`|7C6A4; row+0E=AP; r3 retains the actual lesson index|
|7C770|unitr3, lesson=`*(SP+524)`|7C780; row+0E=AP; r1 retains lesson, r3 retains unit|
|C8F76|unitr7, lessonr4|C8F82; r0=AP, r3=r8=lesson+1|
|7C4D8|menu=`*r3`, lessonr6|7C50E; r0=preview AP, r1=1C24|
|7C392|menur1, lessonr6|7C3D6; r0=preview AP, r1=menu+1C24|

The reaction/support lesson inr3 is subsequently used for native row identity, so testing only the displayed AP byte would miss a material ABI error. The full-register comparisons demonstrate that this contract survives. The zero/nonzero filters take the original exits; flags at unconditional row continuations are not treated as live because subsequent native arithmetic/comparisons replace them.

**Additional gap found and fixed:** primary-list display7C392..7C398 originally read`menu+1C24+lesson`, then branched to7C3D6. This was distinct from the primary AP filter7C362 and read the copied unit's stat/status tail for Human extensions. The parent added the preserving hook, using owner`menu+1BE4`, lessonr6, finalr1=`menu+1C24`, andr0=AP. A fresh independent run on8dd238a1 includes this tenth UI site and passes all120 additional original/extension cases; `primaryPreviewInstalled=true`. The earlier900201d5 acceptance covered only the other eighteen hooks.

## Remaining scope

Constructor/load count normalization, temporary-copy ownership, native battle snapshot rollback, live-slot reuse, sorting and the remaining direct AP readers/writers remain governed by `notes/ap-consumer-audit.md`. The fixture sets expanded unit counts explicitly; the passing lists are not evidence that existing saves or constructors now normalize them. AP-bearing copies with different preview equipment and full mission result UI are not executed here. The central job-mastery helper's broad matrix is in the separate ability-core test; this review concentrates on installed interior branches and their consumers.

Run:

```powershell
. ./scripts/resolve-python.ps1
& (Resolve-FftaPython) scripts/test-ap-inline.py
```

Machine-readable evidence: `build/reports/ap-inline.json`. No defect was demonstrated in the nineteen reviewed hooks on the tested artifact. The primary display gap identified above is resolved on the current tested artifact.
