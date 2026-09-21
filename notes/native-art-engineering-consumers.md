# E02 native graphics/action integration review

Root accepts E02 on `a28b624bb13c8f2f2597a4d4bd3999b17c234b99` after reviewing
the implementation, dependency boundaries and current consumer results below.
This closes the graphics/action integration gate, not the complete expansion.
E03 capacity/lifetimes, E04 full-game compatibility and E05 final assembled
acceptance/build/delivery remain open. Only final artwork and authored poses
are deferred; no known transport failure is waived as an art placeholder.

`native-art-engineering-consumer-evidence.json` pins65 files and the20 distinct
Fight pairs. Its referenced indices were checked against267 retained raw/report
hashes. Existing passes are reused for their actual dependencies and scenarios;
their ROM identities and failed enclosing runs remain explicit.

## Final-stage dependency review

`audit-art-native-consumers` passes10972 checks in terminal runner
20260919T085238.622031Z; report:
`build/art/native-consumer-audit/20260919T085239.324326Z/report.json`.
It reads ROM bytes; it does not emulate, rebuild or relabel historical playback.

- All1680 descriptor slots across20 land/water resources preserve null selection
  and complete non-pointer metadata. Every present command keeps its count,
  duration, events and OAM layout. Complete512-byte draw payloads equal the
  declared native-palette conversion of their original generated pixels.
- Every original resource and independent held-weapon resource retains routing;
  all277 allocation-size entries remain unchanged. The new body pointers in the
  shared table are separately authenticated, including those residing inside
  the held-weapon stage's reservation.
- The28 restored rendering/fade entries exactly match clean US. The29th entry,
  OBJ-copy pointer36D4BC, matches the preexisting gameplay copy handler rather
  than clean US. Treating all29 as clean bytes would be inaccurate. Custom
  palette ownership remains disabled, as established by the native-stage proof.
- The independent class/wheel, portrait, equipment/eligibility, status, held
  weapon and impact payloads remain unchanged. The complete final ROM differs
  from its completed-action parent only at authenticated native-palette stage
  patches and data. No hidden action, ability, save or event change is accepted
  by a broad shared-file assumption.
- Actual current equipment permissions yield exactly20 class/weapon pairs.
  Every pair has a retained successful generic Fight report. This is verified
  against current permissions, not inferred from a count or test name.

The all-slot audit strengthens the earlier6581 native-getter/command proof by
covering the empty descriptor slots and every converted pixel payload too. The
earlier getter execution remains applicable. The six Moogle/Bard land-stream
additions are retained; the old null-descriptor failure has not been restored.

## Consumer evidence and engineering judgment

| Consumer | Accepted evidence and reuse boundary |
|---|---|
| Native resource/facing/action dispatch | Native getter6581, completed-action contract2219, current all-slot/pixel audit10972. All required owned tables and original control commands remain present. |
| Generic Fight | All20 permitted class/weapon pairs, each4915/4916 checks. Seven older e1a87ecd cases retain their graphs through the explicit completion contract; later5a14e6c7 cases include current Samurai/Viking and corrected Moogle/Bard. Native palette conversion changes colors, with complete command/pixel mapping and current renderer/auxiliary checks rather than a claim those historical runs used a28. |
| Combo | All19 allowed initiator/weapon pairs; Bard knife is intentionally Fight-only. Current a28 participation21801 additionally proves new Dark Knight initiation plus new Viking membership, exact native outcome, both body transports and full OAM. |
| Casting, secondary commands and target effects | Current primary Thunder4091, Thundaga4159 and secondary Thunder4087 after fresh secondary entry66. Own-ROM allocations, exact command outcomes, actual caster graphics, full sampled native OAM/palettes, target highlighting, damage and next turn. |
| Held weapon and projectile/impact | Current axe124140 and Tomahawk9103: both held channels, native color behavior, three impact poses, allocation/rendering, damage/cost and root retirement. Queued-upload proof26 is bounded to the exact prior command and full uploaded pixels/tail. |
| Land/water representation | All-ten natural-map movement/return evidence, independently reconciled13188 to the preserved graph parent. Current conversion audit covers both complete resources and their allocation/command/transparent-pixel contract. This reuses actual historical movement; it is not new a28 water playback or a claim of every water attack. |
| Portraits/wheel/menu bodies | Current all-ten portrait UI365, including independent8bpp uploads,48-color palettes, body/wheel coexistence, idle, cancel/reopen and exact fixed-character control. |
| Equipment graphics and eligibility | Current axe UI30 in inventory/Buy/Sell; second eligibility page in inventory8, Buy21 and Sell21. Navigation and native bookkeeping preserve money, inventory/AP and original-page access. Existing bounded icon/legality contracts remain applicable to unchanged dispatch and payloads. |
| Status graphics | Current206 checks: all56 renderer outputs, Exposed/Centered plus Protect cycling, native OAM/palette, removal, preserved storage and exact paired state/other-tile isolation. Actual grant/expiry mechanics retain their gameplay evidence under E04. |
| Native rendering/fade/color transport | Original native entries plus current E01 paired deployment/Move/cancel and actual casting/auxiliary/UI consumers. The obsolete custom remapper's refusals and latency results are historical failed builds, not execution on a28. |

The integration is a shared native transport, not a separate implementation per
spell. Preserved command/descriptor semantics and native renderer restoration
support reuse across those consumers. This review does not claim exhaustive
playback of every spell, facing, reaction combination, water attack or video
frame. Capacity peaks and scene/save lifetimes remain independent E03/E04 gates;
final assembled regression still belongs to E05. Any new demonstrated shared
failure reopens affected acceptance rather than being dismissed by this matrix.

## New runtime results and visual review

All six targeted UI checks pass in terminal runner20260919T084510.795191Z:

| ID | Checks | Report under build/art |
|---|---:|---|
|test-art-native-portraits-ui|365|generated-portraits/ui/20260919T084511.599379Z/report.json|
|test-art-native-equipment-ui|30|generated-equipment/tests/20260919T084554.026234Z/report.json|
|test-art-native-preview-inventory|8|equipment-preview/ui/20260919T084611.154560Z/report.json|
|test-art-native-preview-buy|21|equipment-preview/ui/20260919T084613.847931Z/report.json|
|test-art-native-preview-sell|21|equipment-preview/ui/20260919T084620.325250Z/report.json|
|test-art-native-status-icons|206|generated-status/tests/20260919T084626.794540Z/report.json|

Root inspected the new eligibility-page and Samurai wheel captures: ten new
class entries, native label proportions, large portrait, current generic body
and wheel figure are visible. This confirms the observed UI arrangement, not
final costume, sprite detail, palette artistry or completed animation drawings.
No artwork was generated or modified during this review.

## Separate E03 route correction

`test-art-native-event-confirm` passes10 in terminal runner
20260919T085417.539868Z; report
`build/art/native-event-entry/20260919T085418.256330Z/report.json`.
It authenticates and loads the previous failed deployment unchanged, supplies
the missing eight-frame Start and confirm inputs with600-frame waits, then
reaches an actual command menu with12 native actors and healthy heap. There is
no repeated world entry or extra roster member. Original event203 scene/data
remain inside the explicitly substituted world-location fixture.

This fixes the test input omission. It neither accepts the failed fourteen-actor
formation transplant nor establishes the original event's campaign eligibility
or maximum live capacity. Preserve the original timeout and native overflow
evidence in `native-art-sort-capacity.md`. No production fix is justified solely
by this synthetic overflow, and supported-path failures still require resolution.

Next finish E03 supported encounter/effect/menu lifetimes, E04 campaign/save
compatibility and E05 final review, clean complete build and independent-save
delivery. Current/installed selectors and player saves remain unchanged.
