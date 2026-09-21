> Historical preview; current play uses Play Mod.cmd. See [the current overview](README.md) and [release workflow](MOD-RELEASE.md).

# Reviewed class artwork preview

**Historical preview â€” retired.** The user requires the existing native palette
system and rejected the subsequent nearest-color conversion visually. Do not
treat this older custom-palette build as the current artwork direction. See
[the native-color review checkpoint](notes/reviewed-native-color-2026-09-20.md).
The instructions and evidence below describe the preserved historical preview.

Run **Play Reviewed Art Preview.cmd**, then choose **Continue**. This opens the
combined artwork build with the existing disposable showcase profile: all ten
new class options and their abilities are available. START opens the party menu;
the normal job-change wheel lets each race select its alternate new class.
Named story characters retain their original character designs.
The standalone mGBA window was brought forward and its running title sequence
visually verified. No gameplay inputs were sent to the desktop session.

This preview is separate from **Play Expansion.cmd**. Its saves, states and
screenshots live only in `saves/reviewed-art-2026-09-20/`. Installation never
overwrites an existing preview save or copies a player's progress.

## Included artwork

- All 675 reviewed poses across the ten classes and twenty land/water resources.
- Every 3,025 body drawing record replaced; all 1,116 native control records
  and original animation durations preserved. No walking-only fallback set.
- Separate large portraits, job-wheel miniatures and small equipment badges.
- The latest Samurai face, charcoal trousers and teal scarf, and the approved
  closed Human Dark Knight helmet.

Actual screenshots are in
[the local gallery](build/art/reviewed-in-game-2026-09-20/index.html).
Its provenance index identifies the tested ROM and report for each capture.
Menu captures use the combined build; the ten Fight captures use its byte-identical
reviewed body artwork from the preceding action stage.

## Verification and remaining limit

The all-class Fight, Combo and natural-water cases pass. All 1,592 available
resource/mode combinations pass native construction/selection checks. Viking
Thunder and Thundaga pass every-frame observation and paired outcome checks.
The combined build passes cold battle entry, all ten portrait/wheel menus,
Samurai Fight, Bard Combo, and native save/cold Continue. Badges pass native
rendering and party/buy/sell opening, paging, wrapping and exit checks.
The demanding six-versus-six scenario also passes with all ten classes among
thirteen actors. Thundaga damages both declared enemy targets, all actors remain
present, and two repeated Status lifetimes restore the complete heap structure.

**Performance acceptance is still open.** In the combined-build comparison,
one Move case takes one additional display frame; cancel starts two or three
frames later (approximately 17â€“50 ms at 60 Hz). The strict no-added-delay check
fails. These are retained failures, not waived or relabeled passing results.
This preview does not replace the accepted engineering release or claim a new
complete campaign playthrough. The integration goal remains active.

Reproduction and exact evidence are recorded in
[the integration checkpoint](notes/reviewed-sprite-integration-2026-09-20.md)
and [the reusable workflow](PARALLEL-IMPLEMENTATION.md).
