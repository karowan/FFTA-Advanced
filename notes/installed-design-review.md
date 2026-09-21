# Installed design reconciliation

Latest static reconciliation: `1f197f6c8ca0a28445dd6c3fec245bacf5660df2`,
run `20260917T074520.692367Z`, all2,131 assertions pass. The original help-only
checkpoint below used `7908cc6e3ee78206cc0df16bee627e86f88c68d4`.
Approved scope remains the version0.7 class specification and equipment plan.
This review distinguishes installed data from effect execution and campaign
access; A05 is not closed by matching table rows alone.

## Completed data review

`audit-installed-design.mjs` reads the current ROM through native table pointers,
then compares it with approved Markdown/data rather than an old probe's profiles.
It covers all129 lessons, their158 racial records,85 teaching items and10 jobs:

- Names, action MP costs, magical power references where explicitly specified,
  racial owners, native lesson type/identity and AP requirements.
- Every teaching association, equipment category, attack/magic bonus, base
  buy/sell price, absence of unapproved bonuses/procs, and axe handedness.
- Level-one generation templates, growth bytes, race, status resistance,
  elemental neutrality, Move/Jump/Evade, equipment masks and prerequisites.
- Every lesson has assigned expansion help, including both races of shared jobs.

The audit found15 missing descriptions: Chemist's ten actions, two supports and
two reactions, plus Axe Reprisal. It also found that the existing Geomancer and
Chemist combo descriptions incorrectly called maces staffs. These17 descriptions
are now installed in the final help stage. Existing compact labels such as
Nature Wrath and Counter Rhy. are retained; they are deliberate native UI limits.

`src/completion-lesson-help.mjs` owns the new text. The patcher reserves
`0x1380000..0x138FFFF`, appends ordinary help entries and preserves every old
entry/pointer. It changes only the17 lessons' help IDs, the help-bank pointer,
the range endpoint and new text/table allocations. There is no code, combat
record, saved-state or graphics-layout change.

## Evidence and reuse

Run `20260917T000600.467678Z` selected only
`test-installed-lesson-help` with its six assembly and static-audit prerequisites.
All eight steps passed: **2,131 static assertions** and **846 native assertions**.
Native CD480,19A50 and13E9C resolve and decode all129 descriptions, including
both racial versions of shared lessons. Every description is nonempty and
fits the existing three-line,27-character-per-line contract.

The complete pre-help image is exactly
`55f231768cfffdbfc2383191f8648716d452375d`, the already-tested candidate.
The test reconstructs every permitted changed byte and requires equality with
the new ROM; all previous help pointers remain byte-identical. This is the
reason for retaining prior combat/camera/cold-layout evidence, not merely an
assumption that a text edit is harmless. No battle fixture, native combat suite,
campaign replay or repeated clean-source build was needed for this change.
Final release assembly/acceptance still has its own gate.

Detailed private reports: `build/reports/installed-design.json` and the current
candidate's `installed-lesson-help.json`. The latter contains all actually
decoded descriptions. The runner preserves complete logs and input hashes.

## Remaining A05 review

The content ledger records effect contracts, action descriptors and teaching
sources for each lesson. It does not independently establish the meaning of
every descriptor or every formula/flag/mixing rule. Reconcile those against
their current implementation and scoped behavioral evidence before closing A05.
Do not substitute this static pass for V01/V03 presentation/acquisition or
final assembled acceptance. Original donor artwork remains approved.

V03's separate current-build learning/menu/acquisition acceptance is now complete
within its declared native-consumer and player-flow scopes; see
[`final-learning-acquisition.md`](final-learning-acquisition.md). Remaining A05
presentation reconciliation and V01/I07 gates are not inferred from data matches.
