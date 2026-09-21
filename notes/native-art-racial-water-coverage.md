# Correct racial profiles and ten-class natural water coverage

September18,2026; follow-up34e732d. Private candidate remains
`6443725d256252afae127393945934961eb9abd6`. No production engine, artwork or ROM
change this checkpoint. Current index remains
`build/art/live-palette/all-classes-workspace-current.json`. Built-in imagegen
only; final sprite refinement remains deferred. G01-G04 remain open.

## Correct the earlier mixed-test claim

The prior first/second mixed fixtures assigned job122/123 to race4. The
authenticated class manifest establishes122=Moogle Chemist and123=Moogle Bard,
both race5; Viera Dancer/Mystic Knight are124/125, race4. Likewise118 is Bangaa
Viking,119 Bangaa Dark Knight and120 Nu Mou Chemist. Some earlier notes used the
wrong names. Their raw hashes/results are retained, but their "same-race"
description is invalid. Those tests established palette transport for the
inconsistent declared profiles, not correct racial integration.

The updated test derives race from the authenticated class manifest rather than
duplicating those mappings. It checks actual deployed canonical profile bytes.
The two additional Moogle scenarios replace only generic slot5's presentation
profile before allocation, retaining its test stats; they do not claim a real
recruitment or legal class switch. Montblanc's full story record is unchanged by
these profile edits. Samurai uses the existing generic Human slot2.

All four declared mixed tests pass632 checks each in runner
`20260918T124300.593598Z`. Reports live under `build/art/live-palette/battle/`:

| Group / test suffix | Jobs in slots2/3/4/5 | Report directory |
| --- | --- | --- |
| moogle-chemist |116,118,120,122|20260918T124301.320721Z|
| moogle-bard |116,119,121,123|20260918T124319.677351Z|
| first |117,118,120,124|20260918T124338.387376Z|
| second |117,119,121,125|20260918T124356.711750Z|

IDs use prefix `test-live-art-mixed-workspace-`; each directory contains
`observed.json`, fixed inputs and raw captures. Actual deployment and21 ready/
idle samples check exact generated palettes, every unowned hardware bank and BG
color, native palette shadows, canonical units, refusal/allocation counters,
VBlank bounds and the reservation fence. This covers all ten jobs across four
groups, not ten simultaneously or movement/timing acceptance.

## Actual water consumer coverage

The existing original map92 fixture still redirects only the complete88-byte
map70 record, retaining original arrangement, clipping, heights and water flags.
Native Move chooses the water body and submerged height; cancel restores land.
No actor or water flag is edited during movement. The script now accepts an
explicit water job, takes its race from the authenticated class manifest and
waits for its actual turn. Explicit job profiles are unarmed. Moogle uses the
declared generic slot5 replacement; original Marche/Montblanc appearance
identities remain intact. This is not natural job acquisition or map92's campaign.

`scripts/live_palette_evidence.py` verifies each displayed custom owner against
the compiled class palette and native normal/dim multiplier, active-bank mask,
hardware colors and zero allocation/refusal counters. It is deliberately a
baseline-color movement oracle, not a general transformed-effect oracle.

| Job | Class | Land/water resource | Checks | Generated-actions/battle directory |
| --- | --- | --- | ---: | --- |
|116|Human Samurai|256/257|8675|20260918T125351.577876Z|
|117|Human Dark Knight|258/259|67185|20260918T125641.531303Z|
|118|Bangaa Viking|260/261|8679|20260918T124621.849763Z|
|119|Bangaa Dark Knight|262/263|67203|20260918T125704.085446Z|
|120|Nu Mou Chemist|264/265|67207|20260918T125721.341693Z|
|121|Nu Mou Geomancer|266/267|67205|20260918T125740.513038Z|
|122|Moogle Chemist|268/269|67207|20260918T125759.627512Z|
|123|Moogle Bard|270/271|67207|20260918T125818.832244Z|
|124|Viera Dancer|272/273|67207|20260918T125837.472940Z|
|125|Viera Mystic Knight|274/275|67207|20260918T125856.073625Z|

Each directory above is under `build/art/generated-actions/battle/` and contains
`report.json`, private actually executed map-fixture ROM, fixture proof, inputs,
screenshots and raw RAM/VRAM/OAM/palette captures. All gameplay outcomes equal
the corresponding native control. Every water and land-return focus has its
declared actual resource and visibly owns the exact generated hardware palette.

Viking passed `test-live-art-workspace-natural-water`, runner
20260918T124621.211083Z. Samurai passed `test-live-art-water-class-116` in runner
20260918T125346.625944Z before a later step failed. These use eight-frame movement
samples and are reused within that scope. The other eight class IDs use prefix
`test-live-art-water-class-`, every-frame sampling, and all pass in runner
20260918T125640.832999Z through `scripts/native-art-water-test-plan.json`.
That plan explicitly continues independent cases after failure; no failure is
converted into a pass. An initial invocation omitted `-Suite art` and selected
no steps; no game ran. The corrected invocation is:

```powershell
& '.\Test Expansion.ps1' -Suite art -Plan scripts/native-art-water-test-plan.json
```

Do not rerun this passing set merely for context. Individual IDs and their
declarations also remain in the main art plan for targeted follow-up.

## Native pending-frame boundary and retained failures

Samurai runner20260918T124918.818889Z failed its final body oracle at native
Judge resource102, `move-56`; failed report directory20260918T124919.470171Z.
The custom water/cancel outcome and palettes already matched. The actual640
bytes are the exact native command decoded at the preceding facing, not an
arbitrary pose from the new sequence. Previously, the oracle accepted only the
unchanged preceding display and missed a queued upload completing at that boundary.

New `completed_pending_facing` requires a directly verified preceding record,
both pending flags, unchanged actor allocation/resource, a facing-only sequence
change, the first queued new frame, exact old decoded source/layout, an age of
at most8 frames, exact ROM pixels and an unchanged unused allocation tail.
It never searches all poses or extends the bound. `test-native-pending-facing`
passes24 evidence/rejection controls in runner20260918T125346.625944Z:
`build/art/pending-facing/20260918T125351.354605Z/report.json`.
The older missing raw tail/source values are explicitly only rejection-control
inputs; fresh live playback captures the complete real anchor and source.

That runner then passed Samurai but FAILED Dark Knight at a similar native
Judge transition: directory20260918T125413.576143Z. Eight-frame sampling missed
the decoded command needed for the proof. No wider pose allowance was added.
The remaining scenarios now sample every video frame. To avoid repeated full
heap scans, the actor reader can inspect the exact body addresses obtained from
the native wrapper enumerator. Default full scanning is unchanged; weapon and
auxiliary consumers retain their separate paths. Dark Knight then passes67185.
All failed reports and fail-fast skipped selections remain explicit.

## Retained evidence reconciliation and visual inspection

`notes/native-art-all-class-water-evidence.json` pins the ten reports, fixture
proofs and both endpoint raw captures. `test-live-art-all-class-water-evidence`
passes310 checks in runner20260918T130210.521414Z; report
`build/art/all-class-water-evidence/20260918T130214.651298Z/report.json`.
It independently reads actual canonical race/job records, ROM frame data, VRAM,
OAM and palette bytes, verifies focus-class visibility at water and land return,
and reconciles native outcomes. No emulator or new fixture is used.

Visually inspected the mixed Samurai/Moogle ready capture and Dark Knight water
capture. Draft bodies are visible alongside original characters and submerged
at the native water position. They remain repeated-pose transport art. The battle
HUD was initially misread here as a donor job abbreviation (`WHT`). Correction:
it is the native `WT` turn-order indicator, not a class label. No missing HUD
class consumer was established. See `native-art-connected-consumers.md` for the
corrected interpretation and fresh capture. The donor wrapper in source alone
does not identify a live consumer; the equipment decoder is separately hooked.

Next: finish remaining action/effect consumers, plus unresolved timing,
cross-bank effects and maximum heap coverage. The supposed HUD label task is
withdrawn by the correction above.
The latest movement timing failure and exact-state diagnostics from the previous
checkpoint remain unresolved, not waived by these water tests. Full action
animation artwork, final visuals, assembled review and reproducible updated
playable delivery remain open. Installed preview, vanilla, player saves and
running session are unchanged. No broad integration suite or external provider.
