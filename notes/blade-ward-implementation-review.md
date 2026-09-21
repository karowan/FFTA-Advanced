# Blade Ward private implementation

September14,2026. Current private ROM
`b6daf87deb52ad84d72021e7bc6ea359ebd8bce1`, over accepted main
`ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`. The c8e3 Poise/MP checkpoint remains
frozen separately. No player ROM, save or launcher has changed.

## Approved behavior and implementation

SAM-R1 is reaction128, Human lesson155,300AP. A primary katana and an able
defender at incoming-action start grant35% reduction to enemy physical direct
HP damage for the whole action. It does not counter, impose a cross-action
lock, prevent status riders, or apply to ally/self damage, magic, combos, other
reactions, costs, healing or damage over time. Legal transfer still uses the
native racial lesson and equipment rules; a learned reaction grants no weapon
permission.

Availability uses the actual native Reflex restrictions: native incapacity
getterC8280 and status-compatibility function133ADC with global reaction5.
The native Human lesson20 name decodes to Reflex; reaction9 is not Reflex.
No new ID indexes the original16-row reaction/status bank. Native reaction128
remains behind the existing staging guard, while the explicit incoming damage
modifier supplies its defensive effect without a fabricated counter command.

The action snapshot now has532bytes, adding one reactions-enabled field on the
CPU stack. Per-unit flags retain the existing Poise, actor/copy provenance and
native MP-routing bits, and add Ward assignment/readiness and initial
allegiance/Charm. Even an assigned but unready Ward opens a snapshot, so adding
a katana partway through an action cannot retroactively enable it. Losing the
weapon partway through a qualifying action does not split its mitigation.
Exact evaluated/native copies inherit these flags and existing copy/free
observers retire them.

The actual native A23B8 result argument controls reactions-enabled for the
whole result; nested queries inherit it, and return restores the parent's
setting. Native Counters therefore do not trigger Ward, although independently
eligible Poise still reduces their incoming HP damage. Initial Charm reverses
only the acting side for hostility, matching the existing native/custom action
policy. An exact copied actor is also excluded as its own recipient.

Custom physical finalization combines the action coefficient, Centered,
Exposed, Poise and Ward in one rational product before division and native
clamping. Native physical stages and Fight combine incoming factors once;
magic and combo paths explicitly omit Ward. Higanbana captures its P reference
before these defensive multipliers, so Ward does not reduce its stored wound.
The dedicated native help description uses three lines and the existing
guarded help allocation.

## Deterministic evidence

`20260915T032539.865402Z` passes native Ward tests, the Poise native/status tests,
the full-executor Poise/MP matrix and the expanded help checks. Ward coverage
includes every status bit, empty/nonkatana/primary/offhand equipment cases,
native Reflex availability as an independent oracle, native physical and magic
previews, both stack alignments, Poise/Exposed composition, custom coefficients
and Centered, hostility/Charm/self exclusions, combos, changing weapons after
snapshot, copied recipients and disabled-reaction nested queries.

`20260915T032832.539696Z` passes the full native executor: eight attack types,
Poise on/off, Exposed on/off and eight fixed seeds. The oracle disables the new
factors and returns native P for the two Iaido coefficients, without changing
gameplay results during execution. HP results round once, RNG is unchanged,
incoming MP is unaffected, and Wound retains half of P. Separate native Counter
executions confirm Ward exclusion and Poise coexistence.

Actual battle replays and prior Poise/Counter/cold-save regressions pass in
`20260915T033027.038366Z`. Run `20260915T033607.581604Z` additionally passes
the expanded ten-attack full-executor matrix, Ward plus Poise cold save/resume,
the original Poise cold-save regression, and Wound pulses with both equipped.
These are focused results on b6da, not a complete assembled regression.

## Still required

- Multi-hit/multi-cast boundaries and native AI/law previews; status changes
  within an incoming action and high-damage/cap boundaries.
- Legal external-job equipment and native reaction selection, including Ninja.
- Additional native DoT categories beyond the verified Wound exclusion.
- Full assembled regression after remaining features, then final council.

Composure, Counter Draw and the remaining expansion are still unimplemented.
All tests and fixtures are deterministic scripts; no testing agents are used.
