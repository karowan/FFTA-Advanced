# Shara scene and recruitment lifecycle

Selected IDs: `verify-integrated-assembly-prerequisites` and
`test-shara-scene-lifecycle`. This closes the rendered scene/offer/acceptance
gap left by the existing native Shara arrival and candidate tests. Start from
the accepted actual cleared save, declare stage31 and dispatch381 completion,
and require ordinary town selection to queue129. No scene substitution or
candidate/acceptance injection. Compare full24-slot refusal/cancel with one
declared empty slot23, then save and cold-load the accepted unit on the original
candidate. No broad suite or other job implementation is part of this check.

The declared dispatch/stage inputs are not evidence of earning those campaign
conditions. Existing native dispatch/arrival evidence is reused separately.
## Accepted results

Candidate remains `1b070824a8dad4995434eee3ab40fa08187a6120`.
The ordinary current town (Sprohm) selects Shara through its native condition
program after those declared inputs. Scene129 runs its original dialogue and
recruit instruction `0x089BA91D`; the real constructor produces type12 Shara.
No initial scene argument, queued scene, candidate, accepted flag or UI result
is supplied. This condition path queues directly, without calling09AFC.

The full-clan decline leaves all24 offered member profiles, extra AP,
preferences and inventory unchanged, keeps acceptance603 clear and sets the
original unaccepted retry flag621. With slot23 declared empty, the same native
scene offers Shara and the actual acceptance UI assigns that slot and sets603.
All23 existing member records and their expansion data are retained. The new
slot's extra AP and preference begin cleared.

Run `20260917T113131.898291Z` passes the selected cold suffix in5.3seconds:
20 checks total, including14 retained completed checks and6 new checks.
The remaining scene returns to the observed original Law-tab/world screen;
the actual map cursor responds. Ordinary button-driven saving then persists
Shara and acceptance603. Cold Continue on the unmodified image restores all24
native records, extended AP, preferences, inventory and other compared profile
data. The reusable clear save remains unchanged.

Additional run `20260917T113426.935336Z`, `test-shara-full-capacity`, passes7
checks in1.0second. Native vacancy is null with all24 slots occupied. Selecting
Yes at the actual invitation and waiting for the transition returns to the
original unaccepted-recruit dialogue. It grants no unit or acceptance receipt,
preserves every offered profile and saved flash, and retains the retry state.
Root inspected the Yes prompt, resulting “Why not?” scene, saved-slot screen
and cold world image. An earlier capacity pass113319 had captured the transition
too early;113426 supplies the inspected completed branch.

## Evidence

All private paths below are beside the current candidate:

| Evidence | Private report | Report SHA1 |
|---|---|---|
|Completed UI checks and accepted scene endpoint|`shara-scene-20260917T112850.429399Z/report.json`|`74de8db0fdcc773bbd96b21329e6e4f4f7c17e1f`|
|Accepted save/cold suffix|`shara-scene-20260917T113132.588453Z/report.json`|`261d5cfe666f296fec668444462bf2b642cb05cd`|
|Completed full-capacity branch|`shara-scene-20260917T113427.606778Z/report.json`|`82d4dc3840021d8637cc6b4fb8803d0fcacb6d9e`|

The first report remains failed overall because its save attempt was premature;
only its14 explicitly completed checks and authenticated accepted endpoint are
retained. Every resumed file is hashed before restoration. Source SHA1s are
`bd52b4d359defe6d8f6ebd6c4cb835bd0638076c` (lifecycle) and
`e1f0290c21cb56b28392a0643e5900463500dd81` (capacity). Shared private observer
image SHA1 is `67ed6905876f0aa230ec83d6662d589924014094`. The actual starting
clear save SHA1 is `f2afe32c0c9d1edd94f362a9aad547b70f173594` from the accepted
ending-scenes producer. Reports contain fixed inputs and state/RAM/flash/image
hashes; script snapshots are retained.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-shara-scene-lifecycle-cold-suffix
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-shara-full-capacity
```

For full recreation, `test-shara-scene-lifecycle` starts from the cleared save.
`test-shara-scene-lifecycle-resume` starts at the retained full-clan offer.
The selected accepted suffix above avoids replaying those completed scenes.

## Failed assertions and limits

- Run112600 reached the correct native scene and offer but incorrectly required
  the09AFC observer to fire. The condition interpreter queues directly; actual
  scene identity and original opcode are now required instead.
- Run112726 compared the cancellation output to the pre-scene world. Native
  scene setup changes Marche's active/coordinate fields and candidate generation
  adds Shara's equipment (inventory184,276,320) before the offer. These changes
  were already present in the offered checkpoint. The cancellation boundary
  now compares that entire offered profile, and records the prior changes.
- Run112849 completed14 checks but its extra fixed confirmations re-entered
  the pub before saving. The accepted suffix observes the authenticated original
  Law-tab glyph/outline and proves cursor response before opening Save.

These failures remain visible. No shipping fix was needed. Late stage31 and
dispatch completion remain fixture inputs, not earned campaign evidence.
The one empty slot is declared, not a demonstrated dismissal. Other special
recruits retain their existing all-five native acceptance coverage; this test
does not claim playback of their distinct story scenes. Earlier campaign
scene/territory connections, other outstanding V06 milestones, final R02
acceptance/review and R03 packaging remain open. No broad suite, agent, player
save mutation, publication or unsolicited game launch occurred.
