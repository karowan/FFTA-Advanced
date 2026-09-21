# Word-read trial rejected; phase diagnostic corrected

September18 local / September19 UTC. Goal remains full engineering with only
artwork content deferred. E01–E05 stay open. All runners terminal; no installed
build, player files, game launch, publication or agents changed.

## Result and cause

Private `e94c658af61b996b5808ee595df9cf58d22804e3` tested aligned word reads of
native OAM and owner records. It preserves attribute0..2 comparison and excludes
affine attr3 and reserved owner bytes. The native-only caller rejects unaligned
owner state, IWRAM and hardware pointers before publishing tags or demands.

This is correct but slightly slower. The compiled scalar predecessor already
loads attribute1 only after a candidate owner passes its early tests. The word
version reads it for unowned objects as well and introduces different spills,
masking and address calculations. In the original leaf, offsets170/18C guard
the owner byte and conditional attribute1 load; in the trial, offsets1A8–1C0
perform both OAM word reads unconditionally. Source-level load counts did not
predict the actual generated instruction stream or GBA cycles.

The scoped leaf grows832 to848bytes; stack decreases72 to64bytes. Minimum
post-save SP becomes030072F8. Stage251088bytes, live state11316bytes unchanged.
Measured fused owner/classifier cost rises from4.56–4.69 to4.71–4.85scanlines.
Total means17.12/17.22 for Move and15.90/15.90 for cancel; peak32.27.

| Offset | Action | Active start/end/duration | Bypass start/end/duration |
| --- | --- | --- | --- |
|0|Move|24 /72 /48|24 /71 /47|
|4|Move|23 /71 /48|23 /70 /47|
|0|Cancel|30 /30 /0|30 /30 /0|
|4|Cancel|30 /30 /0|30 /30 /0|

Cancel matches here, but Move duration regresses at both fixed offsets. The
response gate fails four metrics. This does not supersede or waive the previous
candidate's one-frame onset/cancel failures; each has its own exact-ROM control.

## Reproduction and evidence

The rejected implementation is retained only as `fused_word_reads=True` /
`--fused-word-reads`, which requires fused composition and all its existing
private-build prerequisites. Default fused composition returns to the scalar
implementation. The builder reports the optional flag and uses a separate
`build/art/performance/fused-words/` index. The default private fused index again
selectse1a87ecd; neither candidate is accepted for delivery.

All runtime IDs used Test Expansion.ps1 and scripts/native-art-test-plan.json,
announced before execution. Timestamps below have20260919T prefix; child paths
are relative to build/art.

- Runner015147.737760Z: ownership17140 at palette-owners/015152.935043Z/report.json,
  private build8, and full compositor consumer244 at
  fused-consumers/015208.466261Z/report.json pass. Owner tests include36 malformed
  input alignments across scoped and fallback stacks, preserving every output.
  Existing count/affine/stale-owner/geometry/history/highlight contracts remain.
  Entry fails the raw native-shadow snapshot at
  live-palette/battle/015209.389689Z/failed.json; later entry assertions are skipped.
  This run preceded isolation of the trial behind its explicit option.
- Runner015306.065779Z: complete observation31112 at
  native-frame-events/015306.771232Z/report.json passes. All1024 complete native
  states/framebuffers equal ordinary replay. All512 actual current ownership,
  prepared-demand and omitted-tail invocations are independently checked.
- Static compilation after option isolation reproduces every scoped leaf byte,
  stack size and threshold of both originale1a87ecd and triale94c658a exactly:
  performance/word-leaf-reproduction/015715.542620Z/report.json. This is scoped
  compilation, not another full ROM rebuild. The initial full build evidence
  remains separate; the two historical candidate manifests are untouched.
- Runner015737.975721Z: ownership17140 passes again through the explicit option
  at palette-owners/015738.701529Z/report.json. Phase audit fails after6225 checks
  at native-phase-evidence/015741.081908Z/failed.json, described below. The runner
  stops there, so its response check is skipped.
- Runner015824.000144Z: corrected phase/deadline6226 passes at
  native-phase-evidence/015824.900471Z/report.json. Response fails four metrics,
  with13 authenticity/coverage checks passing, at
  response-budget/015825.428294Z/failed.json.

Immutable trace SHA256:
`0f777a8ce17b28896b3c667313f37bd35ca45e65666dda0a196ccd404c187cee`.

## Phase-auditor correction

The failed phase assertion demanded at least one paired BG-phase mismatch in
every action window. Offset4 cancel instead has zero differences. All actual
native-phase, object-shadow, DMA, background-write and VBlank deadline checks
had already passed. A diagnostic property of an older candidate was incorrectly
treated as an invariant. The auditor now requires a complete128-frame paired
comparison and records the raw difference list, including an empty list. It
still validates every native phase and all hardware/deadline constraints; it
does not realign inputs or weaken the independent response acceptance.

## Next work

Do not pursue wider reads as an assumed optimization. Inspect actual compiled
loop work and register pressure before another change; repeated descriptor loads
and per-object branches remain in the scalar ownership/classification pass.
Any reduction must preserve the complete current-input contract and pass real
paired response measurements. No prior-frame cache or unproved relocation of
work outside VBlank is justified. Other full engineering gates remain open;
reuse applicable historical gameplay, transport and campaign evidence rather
than restarting completed jobs or relabeling this private trial as completion.
