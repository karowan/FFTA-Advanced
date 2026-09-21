# Actual Move/Fight proof and resolved test setup, September17

Current technical candidate remains `714f45eb9997ad39d11b13f92c35d5b0de1a0e7f`.
No ROM change was needed to resolve the apparent Fight-entry stall. This note
supersedes the open-failure status in native-action-water-transport.md; its
original failed artifacts and investigation remain preserved.

## Corrected actual proof

Declared `test-generated-actions-battle` passes8,131 checks in runner
`20260917T220413.150282Z`. Full artifact directory:
`build/art/generated-actions/battle/20260917T220413.738647Z/`.
Baseline75029dea and candidate714f45eb each have162 sampled snapshots. The
same native Move/Fight sequence deals14 damage; actor47HP/14MP is unchanged,
and the next native turn menu returns. Viking modes3/7/87 are actually observed
(idle/walk/weapon action). Four generic generated bodies are deployed (Human
Dark Knight, Viking, Nu Mou Chemist, Dancer), alongside required named Marche
and Montblanc identities. Their current body references, sequences, allocation
bounds and actual uploaded frames are verified. One baseline snapshot uses a
bounded native transfer delay; every other sampled body has direct frame proof.
The two transient action roots retire and their following guard stays intact.

The original source seed is unchanged. The earlier26,640-check native/rebuild
proof still applies because ROM bytes did not change. Temporary idle-pose
substitutions are not finished action artwork. This is one weapon family and
four generic classes' deployed graphics, not every action or real water playback.
Auxiliary weapon/effect/status objects are recorded, not accepted by the body
oracle. Large-portrait, palette and final delivery scope remain distinct.

## What was wrong with the test

1. Live Giza enemy placement depends on travel RNG. The initial script assumed
   the old canonical formation from stale unit coordinates. The actual target
   wrapper was at6,15; the intended scenario places it at5,14. Confirmation
   inputs hit an empty tile, then waited for an attack that was never requested.
   Reuse existing `native_battle_wrappers.fixed_giza_formation` before Move and
   assert real wrapper positions. This is a declared disposable formation input.
2. Making Marche/Montblanc generic before a story encounter causes native guest
   replacements and changes the deployed roster. Preserve appearance2/ID80 and
   appearance8/ID82. Change their fallback job/equipment only. Recruited units
   provide the generic-body proof; don't claim generic Moogle from Montblanc.
3. Command-manager mode5/result1 persists during ordinary target selection; it
   is not sufficient evidence of a stall. The corrected entry oracle checks
   the actual final confirmation mode11. Original-party and Viking-only release
   controls pass176 checks in215752.512893Z (capture215753.065844Z).
4. A queued mode change can leave the last walking frame in VRAM while the
   actor record already describes idle. In failed215843, the retained VRAM
   equals the previous verified walking frame exactly and native0x100000 marks
   transfer deferral. Allow only one sampled hold, pending/deferred native flags,
   unchanged resource/tile/allocation identity and exact complete prior block.
   Do not broadly accept any pose or skip the check.
5. The old seed's D7 guard predates allocated transient roots at3ff44/3ff48.
   Normalize those eight bytes to zero as existing integrated tests do. Guard
   starts at3ff4c; verify roots retire separately. The220041 failure changed
   only the action-snapshot root, which is legitimate owned state.
6. An attack creates separate effect objects, including resource128. The idle
   body scanner must not treat these as unit bodies. Resolve actual body record
   addresses from native enumerated wrappers'44 pointer at each snapshot.
   Record auxiliary objects separately; their own pipeline remains unaccepted.

## Retained failed runs and limits

- 214236.390277Z /214507.237020Z: original empty-target timeout, before this turn.
- 214935.842557Z: idle-only frame oracle fails on release movement, aborting the
  first attempted build-stage diagnostic.
- 215026.660083Z: all four stages reach the same incorrectly classified target
  selection state; proves no introduced difference but not a game stall.
- 215323.632743Z: unchanged party and Viking-only release show the same setup issue.
- 215606.093325Z: canonical formation guard rejects unexpected guest roster.
- 215843.571081Z: bounded cross-mode upload delay described above.
- 220041.542822Z: action-root guard boundary was stale.
- 220208.158158Z: auxiliary effect was mistaken for a unit body.

The initially passing profile diagnostic215752 writes714f45eb in its top-level
ROM field despite executing release1b070824 only. Its per-case hashes correctly
identify both actual release controls. The reporter is now corrected to list
actual tested hashes; that report-field-only edit does not require replay.
The later full paired battle report authenticates the actual two executed ROMs.

The four-stage diagnostic was not replayed merely to turn historical failures
green: corrected release controls plus the actual previous/current battle pair
resolve the issue and directly verify the affected path. All failures remain.

Next: actual water transition/rendering and further affected action/weapon
families, custom actor palette allocation, equipment/effect/status pipelines,
then assembled technical packaging. Final sprite artwork remains deferred by
the latest user instruction. G01-G04 remain open; no player ROM/save/session
was changed and no external generation, council or publication occurred.
