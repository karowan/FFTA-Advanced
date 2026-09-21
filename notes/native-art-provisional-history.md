# Provisional palette histories and verified mixed-class entry

Follow-up854c420, September18,2026. Built-in imagegen only; final sprite refinement
remains deferred. No package, launcher, player save or running game was changed.

## Change and candidate

Native palettes can be shared by unrelated actors and UI consumers. Matching a
class reference before any custom body emits is a provisional identity, not proof
that the class owns that bank. In the retained opening fade, seven such matches
were attached to bank12 before any actor appeared. The next unrelated native
table caused seven false unsupported-effect reports.

Optional `--provisional-history` builds now retain one confirmed key per history
slot. Actual authenticated actor composition confirms it. A provisional match
still follows every supported fade/rotation, including effects completed before
first appearance. A whole-bank explicit table that is neither its native
baseline nor a uniform target discards only an unconfirmed identity. The strict
mapper remains unchanged. Confirmed identities, including absent actors, still
report unsupported targets. Retired identities cannot inherit old confirmations;
a later appearance must authenticate a fresh native baseline.

Current private f36376dee8303a4220dd0fc5c2cf37a8e2ac094e resolves through
`build/art/live-palette/all-classes-workspace-current.json`. Build using
`--history-slots 20 --all-classes --workspace-low-address --provisional-history`.
Stage243788, state11312, same RAM0203C000..0203F000. Confirmed keys start at
compiled offset11292. The existing12 layout fields are unchanged; a thirteenth
exports this new offset. Old default/history/all-class indexes remain separate.
No final-art acceptance: these are authenticated existing imagegen transport
drafts, including repeated poses.

## Passing evidence

All timestamps below start20260918T. Reuse these checks while inputs remain valid.

- `test-art-provisional-history`: runner121015.352023, report
  `build/art/provisional-history/20260918T121016.112835Z/report.json`,43 checks.
  Uses authenticated frame2011 native table capture. Provisional unrelated
  targets retire exactly seven keys without changing colors; one/all confirmed
  absent identities retain strict one/seven refusals. Baseline/uniform targets
  retain correct generated targets. Partial tables remain explicit refusals.
  A later unknown palette cannot silently authenticate a class; a fresh genuine
  baseline can. Confirmation retirement/reuse is checked.
- `test-live-art-workspace-native`: same runner, report
  `build/art/live-palette/native/20260918T121016.231075Z/report.json`,9797 checks.
  Byte-exact rebuild, all metadata/pixels, native clear boundaries and new
  confirmation initialization. Rebuild now preserves all candidate mode flags.
- `test-live-art-workspace-late-entry`: runner121149.925657, report
  `build/art/live-palette/fades/20260918T121150.575217Z/report.json`,731 checks.
  Controlled hide/reset/black-or-RGB/reveal, active and completed effects, exact
  native/generated hardware oracle and unchanged native colors/unit bytes.
  This is not every class/effect or a naturally triggered scene.
- `test-live-art-mixed-workspace-first` and `second`: runner121455.226477,
  `build/art/live-palette/battle/20260918T121455.854509Z/observed.json` and
  `.../20260918T121514.315046Z/observed.json`,622 checks each. First includes
  HumanDK117, BangaaDK118, Scholar120, Bard122; second HumanDK117, Viking119,
  Geomancer121, Dancer123. Montblanc identity retained. Actual native turns and
  four-class coexistence plus20 idle samples pass exact generated palettes,
  zero effect/allocation refusals, paired native shadow/background/unowned
  hardware colors, canonical unit bytes, VBlank checks and memory-tail fence.
  These cover seven distinct classes, not Samurai/Moogle mixed deployment,
  movement/combat/action/water playback or final timing acceptance.

## Retained failures and checker corrections

- runner121015.352023, fades121019.957887: late-entry FAILED its legacy final
  counter expectation[1,1,0]. Every color and per-frame check matched; actual
  counters[7,7,0] are correct for seven authenticated provisional class matches.
  The test now derives exact expected identities from enabled source references
  and the original native dim multiplier148104, and checks the actual keys.
  It does not relax counters to an inequality or ignore unsupported effects.
- runner121255.529747, battle121256.228744: mixed first FAILED an invalid test
  oracle comparing unowned banks to nativeBackup. That backup only records banks
  overwritten by the custom compositor; unowned values can be stale/unwritten.
  The complete untouched banks actually matched the paired native control.
  Corrected tests now compare every unowned hardware bank, all background colors
  and the full native shadow to that control. Both groups subsequently pass.
- `test-live-art-workspace-late-rotation` still FAILS: runner121149.925657,
  fades121157.593064. Label `late-rotate0-active-2`: unowned native bank0 is one
  rotation update behind the paired control. Native shadow is identical, the
  generated overlay matches its own actual native displayed phase, no refusals.
  Do not waive the strict hardware comparison or call all-class rotation done.
- `test-live-art-workspace-rotation-prior` reproduces the SAME failure on pinned
  e1c22b01 without the provisional change: runner121610.207063,
  fades121610.836847. Thus the ownership change did not introduce this issue.
- `test-live-art-workspace-rotation-mask-control` passes1595 checks across all
  eight rotate/cycle direction/range/active/completed cases: runner121753.336389,
  fades121753.962604. This diagnostic changes only the custom mask1023 ->2 in
  the f36376de ROM; code, asset addresses and RAM layout are identical. Its
  generated ROM and changed-byte proof are retained in mask-control.json.
  It is NOT an all-class deliverable or an acceptance shortcut.

Fail-fast skipped later selected steps after failed checks; subsequent runs are
listed explicitly above. No hidden reruns or broad integration suite.

## Continue here

The mask-only experiment isolates the hardware-phase delay to the extra work
from tracking multiple class histories. Next reduce repeated update work and
measure actual full-mask rotation again. Inspect `ffta_art_binding_rotate`: it
currently shifts every color, target and interpolation accumulator once per
rotation step for every matching history, even with no live interpolation task.
Preserve concurrent-fade targets/errors, literal-cycle semantics, full/partial
ranges, first-visible phase and all unowned native hardware. Use the native
rotation oracle and actual all-class late-rotation test, not instruction-count
claims or a single-enabled-class release. Do not discard legitimate unseen or
off-screen histories to save work.

Other open scope: Samurai/Moogle mixed coverage, natural scene/effect lifetimes,
maximum heap, cross-bank effects, movement/timing, remaining assets and final
artwork/delivery. All G gates stay open. Current mixed proof and strict lifetime
checks are reusable; installed preview, vanilla and player saves remain unchanged.
