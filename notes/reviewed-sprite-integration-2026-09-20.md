# Reviewed sprite integration goal

The user approved Samurai face revision v6 and requested all reviewed class
sprites integrated into a working, running game with actual in-game screenshots.
The goal is active. No new subagents are authorized. Existing player saves and
the installed v0.7 engineering release remain independent of the art candidate.
The user explicitly clarified: EVERY animation must be replaced, not only
walking. Repeated walking/idle fallbacks do not satisfy final acceptance.

## Inputs and scope

- Base: accepted engineering ROM `a28b624bb13c8f2f2597a4d4bd3999b17c234b99`.
- Artwork: `src/art/race-study/animation-generation-v1.json`, all ten designs,
  sixty 32x32 front/rear movement crops, Samurai exact face reuse v6.
- Contract: `ART-TEAM-CONSTRAINTS.md` and `notes/art-team-contract.json`.
- Authored poses currently cover front/rear neutral and walking steps only.
  Every other displayed pose/action now needs new-design artwork before final
  acceptance. Functional action timing is not complete animation artwork.

## Implementation sequence

1. Authenticate inputs and compare source pixels to native ally/enemy palettes.
2. Enumerate every final native slot, command and displayed pose for all twenty
   land/water body resources, including late Moogle completion. Map reused poses
   explicitly and generate every missing action pose from the original concept,
   approved sprite and matching native keyframe references. Preserve class/race
   anatomy and exact reusable identity pixels where appropriate.
3. Build an isolated final data-replacement stage after existing action completion
   and native palette conversion. Preserve all native command/timing/OAM records,
   named-character resources, shared palettes, code and gameplay data. Allocate
   only inside authenticated unused tails of existing graphics reservations.
4. Replace battle land/water, party/wheel miniatures and menu heads with explicit
   per-consumer conversions. Resolve the large-portrait source separately.
5. Verify final-ROM coverage, tile bytes, pointer bounds, allocation sizes,
   native commands and absence of undeclared writes. Reject unpainted-action
   fallbacks and water crops as substitutes for finished action coverage.
6. Through a declared `Test Expansion.ps1` plan, cold-boot the candidate from
   a separate test save, exercise affected movement/action/menu consumers and
   capture actual emulator frames. Reuse savestates only with their exact ROM.
7. Package the working candidate with isolated storage and launch the requested
   game visibly. Deliver linked in-game screenshots and explicit remaining limits.

No ROM, saves, native extracted assets or raw test logs are committed. No remote
publication is authorized. This note will be updated with build/test evidence.

## Full-animation inventory and first authoring checkpoint

`scripts/prepare-reviewed-actions.py` authenticates the accepted engineering ROM
and the clean native ROM. It enumerates all twenty final resources and associates
only command-1 display records with artwork. Native controls retain their actual
durations/parameters. Moogle's six added descriptors use their documented native
same-race command sources. Both graph directions (frame to pose and pose to all
uses) are retained in `src/art/race-study/full-animation-v1.json`.

There are **675 distinct native pose references**: 60 approved movement drawings
and 615 additional references to author/review. This is a native reference count,
not a claim that 675 finished drawings already exist. All null descriptors remain
explicit. The Samurai's land style reference is Soldier, not its engineering
donor; original concepts are authenticated actual generation inputs.

An eight-pose Samurai sheet was rejected for donor-color contamination and
costume drift. Its source and exact prompt remain in the catalog. Five individual
pose generations are retained as drafts (`p014`, `p015`, `p016`, `p018`, `p019`).
The individual workflow uses four native pose examples, the approved facing and
the original concept. Face reuse in upright `p018`/`p019` follows the user's
existing explicit authorization and changes only the pinned 8x6 face rectangle.
These drafts are not yet marked reviewed production art. Raised-arm extraction
now translates its 32px crop within the worksheet strip rather than clipping.

The declared static test `test-reviewed-action-inventory` passed in runner
`build/expansion/test-runs/20260920T091852.244642Z/report.json` before adding the
extra identity/keyframe checks; rerun those affected checks after that addition.
The first runner failed on a missing plan-level timeout field, not game behavior;
its log is retained at `20260920T091838.776040Z`. No runtime game was launched.
`gate-reviewed-actions-complete` deliberately rejects pending or unreviewed art.

## Palette engineering impact review

Offline previews show substantial costume loss with the current original shared
banks, even when selecting the best of the first sixteen native palettes. A
single combined custom palette also loses red/blue accents. A three-group,
15-opaque-color trial is substantially closer to the approved sprites. Reproduce
it with `scripts/prepare-reviewed-palette-trial.py`; its private JSON pins source
hashes and RGB555-compatible colors. This is not runtime palette acceptance.

Consequently, the data-only integration proposed above needs a separate palette
engineering stage before final acceptance. Do not overwrite original palette
tables globally or simply reactivate the former ten-owner compositor. Its known
response/ownership limits remain relevant. A grouped-palette experiment may reduce
palette demand, but must independently prove allocation, native effects/fades,
opposing units, menus, capacity and input response against the native baseline.
The existing engineering ROM, source palette tables and player saves remain
unchanged. The subsequent private runtime checkpoint below supersedes the earlier
absence of a candidate; it does not complete the full-art gate.

## Private grouped-palette runtime checkpoint

The first candidate `135e1e1f8e6331cb8141bd7d915335e9fa56d336` contains the sixty
approved movement drawings. Its nonmovement repetition and water crops are
explicitly unfinished and prevent final delivery. Palette groups are
116/123/124, 117/119/121, and 118/120/122/125. The private build extends the live
component through the authenticated unused final ROM tail to 0x2000000 and maps
only the ten owned job selectors to source palette zero. Original palettes,
installed games, launchers and player saves are unchanged.

`test-reviewed-palette-cold-entry` passes 24 checks in runner
`build/expansion/test-runs/20260920T093559.038155Z/report.json`. Its own-ROM cold
SRAM route reaches twelve native actors, with actual uploaded Samurai, Viking,
Geomancer and Dancer resources and all three hardware palette groups. Evidence
and the real in-game screenshot are in
`build/art/reviewed-integration/runtime/20260920T093559.767365Z/`.
The initial route failure at `20260920T093359.040890Z` remains preserved: the
native pub had a pending modal message. The optional `--confirm-pub-exit` route
handles that message without changing the default fixture route.

`test-reviewed-palette-response` fails in runner
`build/expansion/test-runs/20260920T094231.230541Z/report.json`. Exact same-layout
mask-only controls show Move durations of 51/55 frames versus 48 at offsets 0/4,
and cancel begins 2/1 frames later. Ordered positions and party bytes match;
observed compose/display returns are within VBlank. Preserve the failure; the
first palette implementation is not accepted. Report:
`build/art/reviewed-integration/response/20260920T094231.967578Z/report.json`.

The next private build enables the existing unrolled-copy, packed-plan,
block/burst-scanner and fast-confirm chain. Its build and fresh cold-entry checks
pass in runners `20260920T094936.903371Z` and `20260920T095017.674380Z` respectively.
Its response acceptance remains pending. Each changed ROM gets a fresh cold
entry; `entry-latest.json` is updated only after a passed own-ROM entry test.

Four more individual Samurai attack drafts (p022/p023/p026/p027) retain actual
concept inputs and exact prompts. None is silently promoted to reviewed art.
The expanded static identity/keyframe audit previously passed in runner
`20260920T092440.235718Z`. Full artwork completion, action consumers, capacity,
menus/portraits, assembled acceptance and visible launch remain outstanding.

## Explicit action import and first real Fight checkpoint

The palette response gate remains failed. Candidate
`a288acdb3e39ff70cf9f7c149412afeddb8611b8` adds one Move frame and one cancel
frame at both sampled offsets. The next private candidate
`ea9fe09b4752be7131f35fd4058468dd9fa0e9ed` copies the authenticated scanner once
per scoped plan rather than once per span. Its compiled planner correctness
test passes 79,101 checks (`20260920T100012.254123Z` under `build/art/palette-plan`),
and cold entry passes. Response still adds one Move frame at offset zero and
one cancel frame at both offsets. Its failed response report is
`build/art/reviewed-integration/response/20260920T100240.301436Z/report.json`.
All observed compose/display return scanlines remain in VBlank; this does not
waive the failed strict response gate.

The cost observer passes with byte-identical end state and screenshots in
`build/art/reviewed-integration/costs/20260920T100935.287883Z/report.json`.
The live-apply path averages 4.75 scanlines, while 26 of 128 sampled frames need
the more expensive 8bpp scan (plan-input average 10.17 scanlines). Ownership and
publication wrapper costs remain significant. These are diagnostic measurements,
not production performance acceptance.

`scripts/import-reviewed-actions.py` now supplies a default complete-art hard
gate and an explicit private `--draft` path. It preserves every native command,
duration and attachment field while replacing exact drawing bindings. The
additional 0x1DD0000..0x1E80000 reservation must be entirely FF in its exact parent.
Only twenty owned resource-table entries and that reservation may change.
Each output archives its catalog and parent manifest; pending/unreviewed counts
and every retained placeholder remain visible.

Draft `acbdbacb4ee835209d29f47d01ab1ba4769b8da2` contains the sixty movement poses
and 29 generated Samurai action drafts. Source inventory and build pass in
runner `20260920T101925.490679Z`. Fresh cold entry plus 14,300 native import
checks pass in runner `20260920T102019.928590Z`. The real battle screenshot and
own-ROM state are in `build/art/reviewed-integration/runtime/20260920T102020.716945Z/`.
The first Samurai katana Fight/next-turn test passes in runner
`20260920T102650.378017Z`. This verifies actual body playback and palette observations,
not every command family or auxiliary weapon/effect acceptance.

Subsequent source review adds head-turn/prayer drafts and exact approved-face
reuse to three running poses, for ten explicitly authorized face reuses total.
Closed-eye and crouch/defeat mismatches are being regenerated; their rejected
originals and reasons remain archived. No generated draft has been promoted to
production acceptance merely because it imports. All water poses, other classes'
actions, portraits/menu consumers, palette timing, final regression, packaging
and visible launch still require completion.

## Complete Samurai sources and natural-water checkpoint

The Samurai now has all 66 distinct land/water source drawings reviewed against
their native keyframes. Sixteen unchanged-orientation faces reuse the explicitly
authorized approved face pixels, with outside-rectangle identity checks. Bowed,
closed-eye, turned and collapsed faces remain individually generated. Human Dark
Knight has 39 reviewed drawings; five insufficient action poses are rejected and
being revised alongside its 22 water drawings. The other eight classes still
have their six approved movement drawings each. Source coverage is 153/675, not
full animation or runtime acceptance.

Private draft `cb7dca4cbda3720562747ac1951b71440320bd42` predates those latest
reviews: it includes 124 reviewed poses, 460/3025 draw records, and explicitly
retains 551 missing poses. Inventory/build pass in runner
`20260920T104448.977691Z` (21,739 static checks); native import passes in
`20260920T104545.022296Z`. Its own-ROM cold entry is
`build/art/reviewed-integration/runtime/20260920T104905.387858Z/report.json`.
Imports now archive immutable content-addressed source PNGs and a separate
provenance snapshot, including importer source, even when review-only metadata
leaves the generated ROM hash unchanged.

Natural-water Move/cancel passes 1,262 checks in
`build/art/reviewed-integration/water/20260920T105327.379852Z/report.json`
(runner `20260920T105326.607838Z`). The fixture substitutes intact original map92
for map70; height, arrangement and clipping data remain original. It verifies
land/water/land resource changes, visible water palette, native submerged height,
return position, root retirement, and unchanged inventory/AP/preferences/seed.
The actual `water-16.png` was visually inspected. This is a deterministic private
fixture screenshot, not a visible user desktop launch or campaign acceptance.

The first water run failed on stale palette tags while the relocated land actor
was off-screen. Read-only composition/display tracing proved no active custom
overlay or visible owned body then, with identical traced/untraced results:
`build/art/reviewed-integration/water-phase/20260920T105131.531118Z/report.json`.
The test now authenticates off-screen OAM separately and requires actual visible
water rendering. The original failed run is preserved.

Display-boundary timing diagnosis confirms the palette response gate is genuinely
still failed: candidate versus mask-bypass Move duration is 48 versus 47 frames
at offset0, 47 versus47 at offset4; cancel is32 versus31 at both. Evidence:
`build/art/reviewed-integration/display-response/20260920T103703.509014Z/report.json`.
The observer itself passes byte/frame identity, but that is not performance
acceptance. No final ROM, launcher, player save or installed release changed.

The five Human Dark Knight action revisions subsequently passed individual source
comparison, bringing source coverage to 158/675. Both Bangaa complete action sets
are generating from their original concepts, approved facings and four native
Bangaa examples. A phase-aware anchor fixes front/rear selection inside the
turning sequences. No pending generation is counted as reviewed art.

The water test now accepts an explicit job116..125, resolves its real race,
resource pair and palette group, and uses the existing same-race preallocation
pattern (declared Moogle inputs precede native actor allocation). Samurai,
Human Dark Knight and Moogle Chemist pass in runner
`20260920T110905.823036Z` with1262/1262/1254 checks. Reports are under
`build/art/reviewed-integration/water/20260920T110906.552302Z/`,
`20260920T110916.241408Z/` and `20260920T110926.208076Z/` respectively.
This validates the reusable test on the unchanged cb7d candidate, including its
explicitly unfinished water art; it does not accept the pending new poses.
The declared plan now includes each class's Fight, Combo and water cases using
existing native input procedures. Remaining cases have not yet executed.

### Complete source sets and portrait checkpoint

Samurai, Human Dark Knight, Bangaa Viking and Bangaa Dark Knight now have all
66/66/64/64 source drawings reviewed. Nu Mou Chemist has 44/68 reviewed; the other
five classes retain six reviewed movement drawings each. This 334/675 snapshot
precedes the next review batch. All remaining source generations are queued,
with exact per-image receipts retained for resumable extraction. Bangaa Dark
Knight p052 required a source-hash-bound extraction strip adjustment to exclude
the upper-row reference; no generated pixels were drawn or repaired in code.

All ten concept-referenced portraits passed source inspection. Two Moogle
portraits needed a second generation because the first placed artwork in the
wrong worksheet cell. Rejected sources and prompts remain archived.
The first native portrait import passed bytes but visibly cropped faces in the
menu. A first placement correction exposed mirrored-origin behavior and failed
the new whole-silhouette window assertion. Both runs are retained:
`20260920T121717.638629Z` and `20260920T122054.580037Z` under
`build/expansion/test-runs/`.

Corrected private portrait candidate SHA1
`ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7` passes build, native decoder/import,
and all ten actual menu checks in runner `20260920T122205.516208Z` (exit0).
Screenshots under `build/art/generated-portraits/ui/20260920T122209.845701Z/`
show the complete Samurai, closed Dark Knight helmet and Moogle Bard headgear.
The importer preserves 103 original portrait images/OAM and 495 original
palettes; only the ten owned images/OAM and sixty owned palette records change.
The menu test now checks real flipped OAM placement against the visible window.

This portrait candidate still inherits the older cb7d action draft. Wheel
miniatures and small icons need palette work; strict palette-response timing
remains failed. No final assembled acceptance, visible launch, installed-release
replacement or player-save mutation has occurred.

### Identity correction and native scheduler evidence

Both Nu Mou full sets now pass primary source review, including explicit
attack/casting-arm and submerged rear/defeat corrections. Enlarged comparison
against the approved Moogle/Viera facings exposed a shared prompt error: the
illustrated concept sometimes replaced the sprite's blue-gray head/ears with
cream fur, white hair, taller ears and a red pom. Earlier source reviews of those
affected poses were superseded and retained in their attempt histories. They
must not be counted as accepted source art. Four p006 pilots correct the
reference priority and now match approved size, identity and running pose.
The remaining251 Moogle/Viera drawings are being regenerated with that explicit
identity constraint; original concepts remain attached to every request.
Reviewed coverage at that point is424/675, with six complete classes. No further
action ROM was built from that source snapshot yet.

`test-reviewed-native-scheduler` passes observation identity in terminal runner
`20260920T130030.350868Z`; report
`build/art/reviewed-integration/display-response/20260920T130031.151967Z/report.json`.
It observes the same retained palette-pilot Move/cancel inputs at native input
poll, main-loop return, VBlank and display boundaries. The candidate performs
116/117 input polls during128 Move display frames versus118 in the mask bypass;
cancel has106/107 versus109. The previously measured positive one-frame deltas
remain. The scene-update03FC site is not executed on this native branch.
This is diagnosis, not a relaxed response gate. See also the earlier native
control-flow and incomplete-writer cautions in `native-art-scheduler-phase.md`
and `native-art-graphics-lifetimes.md`; no speculative stale-frame cache was added.

Read-only menu evidence locates Samurai miniature pixels at VRAM offset70912
(OBJ tiles168..187), emitted as32x32 plus32x8 objects with palette bank3. Human
Dark Knight uses offset70272 (tiles148..167), bank0. Actual miniature palette
ownership is separate from the portrait's48-color range and the header actor.
Menu-color implementation and final assembly remain pending.

### Complete pose import and ten-class Fight checkpoint

All675 distinct poses are now primary source-reviewed. The251 identity-v2
Moogle/Viera revisions and their receipts are complete. Exact decisions are
retained in the three `identity-v2-*-review.json` files and the catalog's
per-pose review/attempt histories; Bard p061 was the final source review.
No earlier superseded review is counted as acceptance of its replacement.

First full import failed in runner `20260920T133359.178532Z`: the importer still
hardcoded a six-pixel registration limit despite the catalog's already reviewed
source-bound seven-pixel exceptions. It now applies the same bounded approval
contract rather than discarding those source approvals or loosening every pose.
Runner `20260920T133510.020558Z` exits0 for complete action build/import/coverage
and the subsequent reviewed portrait build/import.

- Complete action ROM: `6e7624dbcf80b8b1100359dc4945d2882f904743`.
  All3025 drawing records replaced,1116 control records preserved, no missing
  or provisional source poses. Action payload uses439824 bytes.
- Combined portrait ROM: `0ab5d3a8cbcf952a1e0574ca7c9d184aad609f15`.
- Own-ROM cold entry passes at
  `build/art/reviewed-integration/runtime/20260920T133644.381381Z/report.json`,
  authenticated through `action-entry-latest.json`.
- All ten declared Fight cases pass in terminal runner
  `20260920T134159.497899Z`. Each uses the exact6e7624 action candidate and its
  own-ROM cold route; these checks do not substitute for Combo/water/casting.

### Separate menu miniature implementation

The first miniature observer comparison failed because only its second branch
reloaded a serialized emulator state. Both branches now use fresh emulator
instances and load the identical own-ROM state. The failed run
`20260920T133643.644119Z` remains retained. Observer identity and all menu checks
then pass in terminal runner `20260920T133835.790469Z`; trace is
`build/art/generated-portraits/ui/20260920T133836.527006Z/miniature-producer-trace.json`.

The trace authenticates miniature layout0894EAE4, caller08088062 and its tile,
priority and palette arguments. Native OBJ palette block0894EDDC contains bright
job banks0..2 and dim variants3..5. The earlier exploratory sixteen-palette
comparison starting at94EE3C crossed into other UI data; it is rejected evidence.
The corrected comparison script uses the three actual bright palettes and a new
output folder, retaining the old study. No original palette was modified by it.

Private menu candidate `c09f3498800cbcecd783cdf16a85c877b7fa6630` combines all poses,
portraits and the new miniatures. Its dedicated module binds generated image
indices54..63 at native upload sites87B90/87C28/87D58, preserving original figure
uploads and invalidating overlapping old ownership. The exact miniature draw
site88060 selects custom bright banks9..11 or dim13..15. Constructor89660 clears
the bounded map and supplies cloned menu palettes; it preserves original
banks0..8/12 and all background palette pointers. Battle code is unchanged.
These six banks were unconsumed by native objects in all ten retained wheel
captures; actual new-palette coexistence is tested, not inferred from emptiness.

Source conversion review inspected all ten bright/dim miniatures. Native535 and
actual UI815 checks pass in terminal runner `20260920T135331.066979Z`:
`build/art/reviewed-integration/menu-tests/20260920T135331.944323Z/report.json` and
`build/art/generated-portraits/ui/20260920T135334.137552Z/report.json`.
Samurai, Human Dark Knight, Moogle Chemist and Viera Dancer screenshots were
inspected enlarged. Whole portraits, header sprites and both miniature parts
render together with the intended colors; selected locked jobs remain dim.
The failed initial ARM MOV assembly and linker `_stack` classification runs
`20260920T134939.407892Z` and `20260920T135016.713690Z` are retained.

Remaining: small equipment badges, further native action/Combo/water/casting
coverage, menu lifecycle/capacity beyond the wheel, the unresolved strict
one-frame palette-response failure, final assembly/packaging and visible launch.
No release ROM, player save or installed launcher has been replaced.

### Complete Fight, Combo and water checkpoint

All ten class Fight, Combo and natural-water cases now pass. Combo/water
evidence spans terminal runners `20260920T135752.278976Z` (two passes before
failure), `20260920T140609.195808Z` (Human Dark Knight two passes before failure)
and `20260920T140749.096824Z` (remaining sixteen pass, exit0). Each uses the
authenticated complete-action6e7624 ROM, not the stale runner headline hash.

Retained failures exposed observation boundaries rather than changed game
behavior: Dark Knight's offscreen Combo constructor and a previously queued
upload completing during return to idle; Viking also rewinds idle while its
prior queued drawing commits. `test-samurai-fight.py` now requires complete
actual native OAM reconstruction and absence of the entire body allocation for
the hidden case. `completed_pending_facing` additionally accepts exact queued
source/layout evidence across a sequence switch or rewind, with original
allocation identity, both pending flags, direct preceding proof, exact first
command/timer and bounded age. No arbitrary pose search, pixel waiver or game
code change. Failed runs140423 and the two partial runners remain preserved.
Viking and Nu Mou Chemist actual Combo screenshots were visually inspected.

Next declared checks: reviewed badge import/native renderer and party/buy/sell
lifetimes, followed by Viking Thunder365 and Thundaga371 from the authenticated
own-ROM action entry. Badge artwork uses approved neutral head crops converted
to the original two native badge palettes, preserving all palette consumers
and UI lettering. Large portraits and wheel miniatures retain their separately
reviewed custom palettes. Casting checks retain native HP/MP/outcome comparisons.

### Combined playable preview, September20 14:40 UTC checkpoint

Combined ROM `3db563a978a17ae517a5c2b4e7b39dd00b1c2fb7` adds only the ten reviewed
badge images (2,560 bytes) to c09f3498. Original badge palettes, labels, eligibility
and executable code are untouched. `build-reviewed-menu-badges.py` authenticates
every conversion/source and the prior module before replacing its owned images.
Its immutable manifest is under `build/art/reviewed-menu-badges/3db563a.../`;
`complete-candidate.json` selects it privately.

Badge native rendering and all party/buy/sell lifetime checks pass in terminal
runner `20260920T141603.070515Z` before the unrelated casting failure. The earlier
native test141419 failed on missing historical fixture provenance; explicit
reviewed-entry IWRAM now seeds detached native renderer checks without loading
foreign actor pointers. Actual party badge screenshot was visually inspected.

`test-reviewed-animation-modes` passes7,184 assertions and1,592 real widget mode
transitions on all20 resources in runner `20260920T142035.270180Z`. The original
test141910 used battle heap bounds for the widget-private arena; corrected bounds
authenticate the widget's native4080-byte arena, not an arbitrary memory range.

Viking Thunder passes final every-frame checks in142828. Thundaga passes18,120
checks in terminal runner `20260920T143034.462273Z`, report
`build/art/connected/casting/20260920T143035.344987Z/report.json`. Both keep exact
paired damage/MP outcomes and native return-to-turn checks. Retained preceding
failures are observation/fixture boundaries: the cold-entry D7 canaries had to be
replaced by declared empty action roots before executing abilities; four-frame
sampling missed an intermediate idle upload during a constructor. Reviewed cases
now sample every frame, retain the last direct proof separately from the last
configured queue record, require exact previously observed queued bytes, retain
the four-frame reset bound and reconstruct actual native composition geometry.
No ROM/code/art change was made to obtain these passes. Failed reports141620,
142044,142240,142636,142731 and142837 remain available under casting/.

Terminal runner `20260920T142453.442139Z` passes the four combined-ROM steps:
cold entry, all ten menus815, Samurai Fight and Bard Combo9070. Its later
Thundaga failure is superseded only by the separate corrected passing report
above; the enclosing mixed runner is still recorded as failed. Combined native
battle screenshot and all menu assets use the exact3db563a9 ROM.

The strict combined timing test **FAILS** in terminal runner
`20260920T143353.220795Z`; report
`build/art/reviewed-integration/response/20260920T143354.116360Z/report.json`.
At idle offset0, Move starts equally but ends one frame later; cancel starts
three frames later. At offset4, Move starts/ends one frame earlier with equal
duration; cancel starts two frames later. Ordered motion and canonical player
bytes match, and measured composition/display remain within VBlank. No response
threshold was weakened. The earlier one-frame-only summary is superseded by
these actual combined-ROM measurements (approximately17–50ms).

`test-reviewed-preview-save` passes21 in terminal runner143630, report
`build/art/reviewed-integration/preview-save/20260920T143631.285432Z/report.json`.
It reuses the prior authenticated all-class showcase, saves through the native
menu and cold-Continues on3db563a9, preserving canonical roster/AP/items/gil and
early campaign stage. This is a disposable showcase, not natural progression.
The installer copied it only to a previously absent
`saves/reviewed-art-2026-09-20/FFTA_Reviewed_All_Classes.sav`; all eight preexisting
save/release files were hashed and preserved. No player save was imported.

`Play Reviewed Art Preview.cmd` and its `-ValidateOnly` launcher authenticate
3db563a9 and explicit independent save/state/screenshot paths. An escalated
interactive launch succeeded. Computer Use listed desktop mGBA window17042122
at59.8fps; subsequent activation/screenshot approval timed out. Thus process
launch and desktop-window existence are verified, foreground/image verification
is not. No interactive gameplay test was performed.

The21-image local review gallery is
`build/art/reviewed-in-game-2026-09-20/index.html`. Images are intact actual emulator
captures. Every image's hash, ROM and passing report are in its JSON index; the
ten Fight captures deliberately retain6e7624 provenance while menus/overview
use3db563a9. The reviewed body payload is unchanged between those candidates.

Source catalog storage is now ten per-class JSON documents plus an index.
Export/verify reconstructs the original7,064,057-byte CRLF aggregate exactly,
SHA256`f038b566acd855254ae1d0c0d21d4fe13e30d37fcab386d6213c1602aa69983a`.
The generated aggregate is ignored; no source prompts, references, superseded
attempts or decisions were removed. This preserves existing import hashes while
keeping each tracked source document under the four-MiB asset-guard limit.

The goal remains active. User was offered the choice to continue timing
optimization or accept the measured delay for this preview; no answer has been
received at this checkpoint. Do not infer acceptance from elapsed time. Further
palette coexistence/capacity/lifetime acceptance remains distinct from completed
art coverage. The installed engineering release and its launcher are unchanged.

### All-class battle and repeated Status, September20 15:51 UTC

Combined3db563a9 passes18,761 checks in terminal runner
`20260920T154902.810784Z`, report
`build/art/all-class-capacity/20260920T154903.556989Z/report.json`.
The declared formation324 scenario includes all ten classes among13 actors,
with custom classes on both sides; all three custom palette groups reach the
actual display and every actor survives Status entry/exit. Final battle and
Status images were inspected and added intact to the screenshot gallery.
The fixture differs from the combined ROM only in the predeclared encounter
and enemy class/loadout data; its SHA1 is recorded separately by the report.

Retained runner154654 failed at the old2400-frame entry limit. Diagnostic
154818, report `build/art/capacity-entry/20260920T154819.589268Z/report.json`,
replays the failed state without input and with one confirmation: both reach
native menu at240 more frames. The reviewed case now has a bounded3000-frame
limit; historical cases keep2400. No gameplay or sprite bytes changed.

`test-reviewed-capacity-spell-status` passes5,805 checks in terminal runner
`20260920T155055.587222Z`, report
`build/art/capacity-action/20260920T155056.569288Z/report.json`. It reuses the
same authenticated own-ROM13-actor ready allocation. Thundaga charges20 MP and
causes positive damage to both declared enemy targets; all actors remain, the
next native turn is reached, and two Status cycles restore the entire heap
allocation structure. Minimum observed free space is11,052 bytes. Live palette
allocation/effect counters stay clear and baseline colors are verified after
return. This establishes this demanding scenario, not arbitrary actor counts
or every campaign encounter. The strict response failure remains open.

### Desktop and source checkpoint

Source commit `19e352e` records the complete reviewed-art workflow and functional
preview checks; ROMs, saves, generated media and unrelated provider work remain
outside it. Source syntax/JSON/document links, exact catalog reconstruction and
the Git asset guard passed. Art JSON receipts preserve original line endings
through a narrow `.gitattributes` rule; they are still UTF-8 checked source.

A fresh Computer Use selection found exactly one existing mGBA window17042122.
Activation and screen capture succeeded on recovery. The first image caught a
black title-sequence transition; the next showed the animated native intro at
approximately60 FPS. This supersedes the earlier foreground-verification gap.
No new instance, gameplay input, save change or session reset was performed.
The source gallery now has23 authenticated screenshots. The strict response
performance failure is still explicitly open; source/launch success does not
waive it.
