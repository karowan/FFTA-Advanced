# Mixed-class planner experiment — September 18, 2026

Follow-up to `0c423ae`. The experiment is **rejected for adoption**, and the
verified connected candidate is restored byte for byte to
`4a7d55ce09cd4a40965a0bb97de2701d276789c5`, palette parent
`5eff9a7044165dd639d47163b44e8f315a722ddd`. Resolve the connected path from
`build/art/connected/current.json`. No installed build, launcher, player save,
session or publication changed. Built-in imagegen remains the artwork source;
the user has deferred final sprite refinement. G01–G04 remain open.

## Measured target and implementation

The earlier instruction profile used one custom class. A new profile uses the
exact four-class raw capture from `20260918T183919.610099Z`, with its RAM,
IWRAM, OAM, VRAM and palette individually authenticated. It executes composition
only, never serialized actor animation pointers. It checks native DMA transfers,
unowned colors/OAM, native shadows/VRAM, allocation failures and memory isolation.

On the current mixed input, the full planner executes 10,798 of 17,919 measured
instructions. The single-owner preferred-assignment validator refuses mixed
frames immediately. This identifies a different cost from the earlier rejected
tail-scan and scoped-planner experiments.

The trial validates multiple prior assignments against the current OAM and
visible 8bpp pixels. It rejects bank zero, invalid or duplicate banks, missing or
new owners, changed class geometry and any current native bank conflict before
applying colors. Conflicts fall back to complete planning and native-bank backup.
There is no palette history eviction, new RAM reservation or stale-frame reuse.

First trial `d81a55a39e827d2128826a0d78a4a1af6c64a551` scanned pixels with an ARM
bank-mask predicate. It passed component checks but increased mixed composition
to 18,711 instructions. It was superseded before gameplay testing.

The revised trial reuses the existing exact-byte tile cache: every cached tile
is compared against current VRAM before reusing its palette mask. A changed tile
is rescanned. Palette parent `001f17b8ef4b1a092585b38d3d8078969da2e970` assembles
to connected `d420c346c57af58ead2edbe074d2e7c4b306c220`. Both have live state
11,312 bytes; the palette stage uses 246,108 bytes. The mixed profile falls to
13,647 instructions, about 24% less than the verified baseline. Counts describe
executed instructions, not hardware cycles or a playable timing improvement.

## Evidence and failed actual acceptance

All runs used the declared native-art plan through `Test Expansion.ps1`; IDs and
purposes were announced. All runners are terminal. Dates below are 20260918.

| Check | Runner | Child report under build/art | Result |
| --- | --- | --- | --- |
| Baseline mixed profile |185551.120174Z|compose-isolation/20260918T185551.802766Z/report.json|292; 17,919 fresh /17,667 skipped-DMA instructions|
| First mask scan |190006.844313Z|multi-preferred/20260918T190007.431890Z/report.json|5,917 component checks|
| First mask profile |same|compose-isolation/20260918T190008.220922Z/report.json|292; 18,711 /18,459 instructions|
| First planner boundaries |same|palette-plan/20260918T190008.426251Z/report.json|48,009|
| Cached multi-owner component |190152.720496Z|multi-preferred/20260918T190153.328600Z/report.json|5,917|
| Cached mixed profile |same|compose-isolation/20260918T190154.137250Z/report.json|292; 13,647 /13,395 instructions|
| Cached native/rebuild |same|live-palette/native/20260918T190154.321900Z/report.json|9,814|
| Cached planner boundaries |same|palette-plan/20260918T190158.496189Z/report.json|48,009|
| Actual mixed entry |190425.311094Z|live-palette/battle/20260918T190426.040661Z/failed.json|**Failed**, after 47 checks|
| Matched-state timing |190544.254986Z|scheduler-phase/20260918T190544.896943Z/report.json|134 diagnostic checks|
| Retained compiled trial |190834.190864Z|multi-preferred/20260918T190834.834586Z/report.json|5,918; source restoration does not erase the experiment|

The actual entry fails `candidate/ready paired native palette shadow preserved`.
Its complete exact-ROM ready capture and 21 ready/idle palette observations are
retained. This is a failed acceptance run, not corrected into a pass. Later
mixed-entry assertions were not executed after that failure.

The new component matrix covers two, four and fifteen owners; history slots
above 15; every byte value in every word lane against five independent bank
sets; missing/new owners; invalid/duplicate banks; current-pixel changes across
cache boundaries; exact full-planner fallback and backup; clipping, flips,
affine and mosaic footprints. It is not natural scene/effect acceptance.

## Actual matched-state timing

Each case loads the same failed run's exact candidate state. The private control
changes only four bytes at the authenticated Thumb `preferred` entry to return
zero. It retains the entire compositor and forces full planning. No actor
pointer is relocated and no saved memory/input is edited. All sampled action
frames retain multiple palette owners. This bypass is a diagnostic control,
not a replacement playable build or literal previous-build cycle identity.

| Extra idle frames | Trial Move start/end/duration | Full-planner control | Trial/control cancel start |
| ---: | --- | --- | --- |
|0|17 /64 /47|17 /65 /48|25 /27|
|1|17 /64 /47|17 /65 /48|25 /26|
|2|17 /64 /47|17 /65 /48|26 /27|
|3|17 /64 /47|16 /64 /48|25 /26|
|4|17 /64 /47|16 /64 /48|26 /24|
|5|16 /63 /47|16 /63 /47|25 /25|

Mean sampled planner intervals fall from 25.16–25.22 to 17.76–17.86 scanlines.
The same ordered movement positions, final coordinates and canonical player
records hold in all twelve cases. Raw native phase/input/profile records remain
in the report; they are not aligned or normalized into equivalence.

The improvement is real within the measured planner and movement duration, but
not consistent at input response: Move begins a frame later at offsets 3/4,
and cancel is two frames later at offset 4. Combined with failed actual phase
acceptance, this does not justify replacing the verified candidate. Do not claim
that the trial universally worsens performance, or that instruction reduction
alone fixes the outstanding timing issue.

## Recovery and next step

Production engine changes were removed. The trial diff is retained at
`build/art/multi-preferred-trial/001f17b8ef4b1a092585b38d3d8078969da2e970/rejected-source.patch`,
SHA256 `4fecf6c188733813ad462f51c16000b7fc2acd3e9a7179966428a6a1ca2728c8`.
The compiled candidates, source hashes, logs and failed report remain private.
The declared trial profile/component IDs pin the immutable rejected candidate;
they do not silently compile or test the restored production source as the trial.

The ordinary build reconstructs palette `5eff9a70` and connected `4a7d55ce`
exactly. Restoration report:
`build/art/connected/rebuild/20260918T190717.722128Z/report.json`.
Reuse the original Status/world-menu/rebuild evidence from
`notes/native-art-compact-status.md`; no repeated broad integration is justified.

Next timing work should locate the actual native input-poll, scene-update and
VBlank scheduling boundaries with deterministic cycle/event observations.
Frame-boundary flag samples and faster inner loops alone have not explained the
response discontinuities. Retain this trial as evidence rather than repeating
it solely for its instruction count. Larger encounter/effect capacity, remaining
natural consumers, assembled acceptance and reproducible delivery remain open.
