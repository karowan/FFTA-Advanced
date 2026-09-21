> Historical record, archived September 21, 2026. For current guidance, see [the repository overview](../../README.md). Paths in code examples are relative to the repository root.

# Implementation acceptance checklist

## Current scope: full engineering with placeholder artwork

The user's clarification supersedes the earlier technical-preview completion
and latency waiver. Only final image quality and artist-authored animation frames
are deferred. Repeated temporary poses are allowed; broken action transport,
rendering, gameplay, memory lifetimes or unresolved performance regressions are
not waived by that permission. Historical checked gates retain only their stated
evidence scope. E01-E05 are now accepted and delivered on a28b624b through
Play Expansion.cmd; only final artwork/authored poses remain deferred. See
notes/native-art-engineering-delivery.md. The older7507ca5c preview is retained
separately. Chronological paragraphs below preserve prior failures/open statuses;
they do not reopen the final accepted engineering gates.

- [x] **E01 — Rendering performance.** Reproduced Move/cancel and deployment
  regressions resolved on native shared-palette candidatea28b624b. Independent
  original-renderer control and fresh paired entry66, response6191, deployment7891
  pass. Move/cancel start/end/duration match at offsets0/4 with zero extra frames;
  deployment has identical591 callbacks/99 shifts, raw palettes and input/update
  cadence. All2240 observed complete states/frames match ordinary execution.
  Root reviewed the comparisons and29 restored native graphics entries. See
  notes/native-art-native-performance.md and its pinned evidence index.
  Graph/getter6581 and all-ten capacity17696 are separately reused. E02-E05 stay
  open. The following earlier optimization failures are retained as historical
  evidence; they describe their own candidates, not the accepted native path.
  Two exact scanner trials are rejected; notes/native-art-bank-scan-trial.md
  records actual paired delays and the explicit failing response-budget gate.
  Later graphics/cache and exact-OAM work is recorded in
  notes/native-art-graphics-lifetimes.md. OAM traversal reduces measured work,
  but Move still starts1frame late and cancel1–2frames late. Its response gate
  fails seven metrics; neither it nor the incomplete queue-only cache is accepted.
  Combined ARM classification/exact scan473a6938 also remains unaccepted:
  Move duration+1 and cancel response+2 at both offsets; ten failed metrics.
  See notes/native-art-arm-classification.md; native phase proof passes separately.
  Latest private repeated-demand183c641a also rejected: Move+1/+3 duration and
  cancel+2/+4; nine failed response metrics. Two measured Move frames cross
  VBlank. Strong current-input proof5203 does not waive either failure. See
  notes/native-art-repeat-frame-trial.md; installed build remains unchanged.
  Native prefix trial12562f6f reduces mean composition to17–19scanlines and
  matches Move duration at both offsets. Response still fails four metrics:
  Move start/end+2 at offset0, cancel+1 at offset4. Phase/deadline6226 passes;
  all512 observed prefix applications independently prove their omitted tails.
  See notes/native-art-prefix-planning.md; this is partial progress, not E01 closure.
  Native-producer ownershipa42c04e1 further reduces the means to16–18scanlines.
  Actual copy/tag proof29084 and phase/deadline6226 pass; response still fails:
  Move start/end+1 at offset0 and cancel+1 at offset4. See
  notes/native-art-producer-ownership.md. No release or completion claim.
  Same-call fused candidate e1a87ecd is also unaccepted: means15.66-17.07lines,
  Move start/end+1 at offset0 and cancel+1 at both offsets; six failed metrics.
  Current-input/frame proof31131, phase6226 and complete compositor differential244
  pass separately, including explicit simultaneous split histories and highlight
  fallback. See notes/native-art-fused-composition.md; E01 remains open.
  Optional word-read e94c658a is rejected: slower owner pass and Move duration48
  versus47 at both offsets; four response metrics fail. Complete observation31112
  and corrected phase6226 pass separately. Default fused code restored exactly;
  see notes/native-art-word-read-trial.md. E01 is still unresolved.
  Compact Thumb leaves are also rejected: correct but slower, six response
  metrics fail. Default scalar code reproduces exactly. Controller profiling27027
  passes and locates cancellation work in callback97814/work-list processing and
  movement-display98A88. See notes/native-art-controller-profile.md. These are
  profiling leads, not native-equivalence or performance acceptance.
  Follow-up movement profiling27027 attributes4.36-4.47 inclusive cancel frames
  to150 nonmatching field queries, including repeated canonical peer-list
  construction. Current-query optimization and field/grid equivalence remain
  pending; the original gameplay callback is already expansion-hooked.
  Optional current-query a3937916 passes field/grid/copy differential44795,
  observed-state/frame31055, phase6226 and exact stage rebuild. The expensive
  cancel callback is faster, but response fails eight metrics, including Move
  duration48 versus47 at both offsets. It is not accepted; fallback nesting adds
  56 stack bytes and deep AI/interrupt coverage is open. See
  notes/native-art-field-query-trial.md. Continue reducing compositor overhead.
  Refinementb35fa9e4 restores exact original fallback stack (zero extra nesting).
  Contract60252, observation31042, phase6226 and rebuild pass; response still
  fails eight metrics, including Move duration+2 at both offsets. Entry ready
  comparison also remains failed. This optional stage is still unaccepted.
  Scoped ARM observer31227 now separates copy from execution; about2.51lines
  per interrupt copy the two leaves. Optional unrolled-copy0cca3494 preserves
  leaf bytes and stack/RAM contracts and saves about1.1-1.2 compositor lines.
  Ownership17068, plan488, compositor244, frame proof31105 and phase6226 pass;
  response still fails six metrics, including cancel+2 at offset0. Entry shadow
  also fails. No promotion; see notes/native-art-scoped-copy-trial.md.
  Direct current-demand plan94770ae8 passes extended exact-plan/cache4744,
  complete compositor244, observed-state/frame31105 and phase6226. It saves
  about0.3-0.4 compositor lines but leaves the same six response failures and
  entry-shadow failure. No promotion; notes/native-art-packed-plan-trial.md
  identifies the remaining8bpp peak cost and retains the initial oracle failure.
  Exact block/burst scanner trials lower peak work. Burst93a9cf2c passes scanner
  and boundary70360, plan/cache4744, full compositor244, observation31110 and
  phase6226. Both Move durations and cancel responses now match their controls;
  Move start/end still lag1frame at offset0. Entry-shadow comparison also fails.
  E01 remains open; see notes/native-art-block-scan-trial.md for both trials,
  all failed response metrics and the raised temporary-stack cutoff.
  Private390e4b04 exact-key confirmation passes7488, compositor244, frame
  proof31133, phase6226 and response13. All declared Move/cancel timings at
  offsets0/4 now match same-ROM bypass. Entry equality remains failed. Focused
  trace7169 identifies original deployment callback080BA66C: parent591 updates/
  99 shifts versus candidate583/97, with exact native full-shadow and counter
  semantics. This is a real remaining deployment cadence difference, not a
  completed E01. See notes/native-art-fast-confirm-trial.md. No promotion.
  Same-call preference plus rectangle200ca35b lowers deployment composition
  from22.1 to16.0lines and recovers two updates, but response fails cancel+3 at
  offset0 and Move onset+1 at4. Scanner48079, plan4744, compositor244, deployment
  proof8369, frame proof31134 and phase6226 pass. Raw entry equality still fails.
  No promotion; notes/native-art-deployment-preference-trials.md retains all
  three trials and distinguishes CPU cost from actual input response.
- [x] **E02 — Native action integration.** Root accepted on a28b624b after
  current UI365/30/8/21/21/206 and final consumer dependency audit10972 pass.
  All1680 land/water slots, full converted pixels, original commands/OAM/timing,
  allocation bounds, restored native hooks and all20 allowed Fight pairs are
  accounted for. Existing19 Combo initiations, current participation/casting/
  auxiliary graphics and historical all-ten water evidence are reused with
  explicit dependencies. See notes/native-art-engineering-consumers.md and its
  pinned index for root review, exact runtime coverage and remaining E03-E05
  boundaries. The following records retain the path to this acceptance.
  Reconcile actual land/water/action,
  weapon/effect and UI consumers for all ten classes. Diagnose the retained
  Samurai frame53 failure and distinguish test-oracle errors from engine faults.
  Placeholder frame content is allowed; animation transport must work.
  Frame53 diagnosed and observer corrected: native type8 holds the preceding
  graphics. Native control proof30/full Samurai Fight4915 pass without ROM changes.
  See notes/native-animation-control-evidence.md; other consumers remain open.
  All-ten historical water reconciliation13188 and seven new generic Fight
  flows pass on e1a87ecd. A real Moogle Chemist knife failure exposed null native
  action descriptors; cause proof48 confirms the constructor's invalid result.
  Private5a14e6c7 adds six missing Moogle land entries with generated placeholders.
  Moogle knife/staff and Bard knife each pass4916; full preservation/native
  four-facing/rebuild contract2219 passes. See notes/native-art-action-completion.md.
  Remaining weapon/Combo/secondary/effect/UI acceptance stays open. This final
  construction stage must be retained when composing subsequent candidates.
  Eight further generic weapon-family Fight flows pass4916 each on5a14e6c7;
  see notes/native-art-controller-profile.md. Historical Samurai/Viking graph
  reconciliation and auxiliary action/effect acceptance remain open.
  Current Samurai/Viking Fight each pass4915 on5a14e6c7 after confirming their
  consumed attack graphics differ from historical proofs. All20 permitted
  generic class/weapon-family Fight combinations now have evidence; auxiliary
  actors and other actions remain open. See notes/native-art-action-completion.md.
  Current5a14e6c7 held axe89812 and projectile/primary-impact4063 pass with
  four-class coexistence. A native opcode0 trail hold exposed an observer gap;
  pinned native control/full-actor proof95 passes, with negative controls and
  retained original failure. See notes/native-art-current-auxiliary-consumers.md.
  Other auxiliary families and casting/Combo/secondary consumers remain open.
  Current Viking Thunder4527 and Thundaga4569 pass with four-class coexistence
  and exact composition-bypass HP/MP outcomes. All19 permitted generic class/
  weapon Combo initiations now pass native Move/Combo/next-turn and608 consecutive
  body/palette observations each. Native-only banner proof793 and facing-reset/
  afterimage proof58 justify observer corrections; original failures are retained.
  See notes/native-art-current-combo-casting.md and its pinned evidence index.
  Participation-chain graphics, other casting/secondary/effect/UI consumers
  remain separate. No ROM change or E02 completion is claimed by this checkpoint.
  Native-palette candidatea28b624b now passes21801 actual Combo participation
  checks: fresh generic Dark Knight initiator and Viking participant, exact native
  membership,55 damage/native-donor outcome, both body transports and complete
  native OAM over1208 action frames per branch. Hidden-constructor36 and existing
  native-only OAM793 pass separately. See notes/native-art-native-combo.md; this
  adds representative new-body participation, not all remaining E02 consumers.
  Current native-palette primary Thunder4091, Thundaga4159, secondary entry66
  and secondary Thunder4087 pass. Each casting branch uses its own fresh
  original-renderer allocation; all450 sampled action modes/full OAM/palettes
  match its control. Native held axe124140 and projectile/impact9103 also pass,
  including both attachment channels, all three impact poses and native colors.
  Queued-trail proof26 reproduces the retained actor with an available native
  transfer queue and validates exact pixels/allocation tail. The failed fixture,
  observer/control attempts and null-queue proofs remain explicit and pinned.
  See notes/native-art-native-casting-effects.md. No candidate ROM changes;
  remaining E02 consumer/dependency review and E03-E05 are still open.
- [x] **E03 — Capacity and lifetimes.** Establish supported encounter/effect
  capacity against native limits and representative demanding combinations;
  verify memory, palette ownership, transitions and return paths. The existing
  13-actor result alone is not maximum-capacity acceptance.
  Root now accepts the combined native count/selection contracts, demanding
  all-ten13-actor effect/menu proof and current battle-result/world/save/ending
  lifetimes. See notes/native-art-final-engineering-review.md. No new actor-count
  domain is added; the synthetic14-actor native-sort failure remains failed and
  is not accepted as a supported scene combination. This is original-game
  compatibility plus demanding bounded capacity, not arbitrary formation mods.
  The following earlier checkpoints retain their original partial scopes.
  Current selection4273 covers all512 mission slots and executes1612 native
  event/location pairs plus258 scene values against current/clean code. Event203
  is the only initial-roster estimate above13 and is excluded by the audited
  mission, mission/random queue and descending-scene roots. All-ten13-actor
  Thundaga plus next-turn/two Status cycles pass a retained-action suffix195;
  read-only reconciliation134 proves exact heap restoration and125 evidence pins.
  Minimum11,052 free/8,776 largest; all13 actors and ten bodies survive. Earlier
  range/fixture/observer failures remain explicit. See
  notes/native-art-capacity-followup.md. Later script/scene-exit lifetimes and
  final capacity review remain open; no blanket maximum or campaign acceptance.
  Later current battle-exit/result/mandatory territory/menu/save and actual
  ending scene lifetimes pass as documented in native-art-campaign-compatibility;
  reuse them for the remaining root capacity review instead of replaying them.
  Static inventory450 passes across442 native formations;23 contain13 templates,
  distinct from the12-record non-party allocator. Reachability/selection remains
  open; see notes/native-encounter-capacity-inventory.md.
  Current static audit456 proves the primary scene loader's12-template bound.
  Scripted/secondary selection and empty-domain entry still require lifecycle
  reconciliation before maximum-capacity acceptance. No E03 completion claim.
  Static scripted-capacity465 proves judge/script spawns share12 nonparty
  slots and saved restoration visits24 party+12 nonparty records. Secondary
  consumers123694/123CC0 read metadata, not another bulk roster. Formation19
  has12 templates plus a judge selector: reachability, ordering and retirement
  need reconciliation. No demonstrated overflow or maximum-occupancy claim.
  Event audit471 now proves no native event selects formation19, including
  the script handler that searches that same event table. Formation29 supplies
  judge templates. This narrows the concern; other selector inputs and actual
  live occupancy remain open. The retained event links guide the next demanding
  encounter selection; see notes/native-encounter-capacity-inventory.md.
  Actual battle-loader audit484 distinguishes opcode4E primary/secondary
  constructors from the earlier4A bound and corrects8000 to opposing-side flags.
  A new all-ten class roster exposes missing opposing palette authentication.
  Private79e88695 fixes that path and passes1422 exact reference/negative checks,
  but deployment then fails: nine histories need banks when eight remain.
  The pinned pressure audit confirms the shortage; ready/Status/return checks
  are skipped. See notes/native-art-opposing-palettes.md. E03 remains open.
  Subsequent native shared-palette candidatea28b624b eliminates custom-bank
  demand and passes17696 checks through the same all-ten13-actor entry,120 idle
  frames, owned Status and120 returned frames. Every class has exact allocated
  body uploads; nine are on screen and Bard remains offscreen. This closes the
  reproduced deployment failure, not maximum reachable occupancy/effect coverage.
  See notes/native-art-shared-palettes.md for failures and test-route corrections.
  Formation23 transplanted into Giza reaches14 actors but fails native sort:
  a13-pointer stack array overwrites its count with the14th wrapper. Ordinary
  replay reproduces persistent corruption; native clean/candidate proof83 passes
  the diagnosis and13-actor controls, not capacity. Original event203/scene168
  follow-up stalls at deployment because its A-only plan lacks Start. Preserve
  failures and audit actual event eligibility/bounds before any engine expansion
  or maximum claim. See notes/native-art-sort-capacity.md and pinned evidence.
  The retained full-event deployment now reaches an actual12-actor command menu
  after its missing Start/confirm inputs; test-art-native-event-confirm passes10
  without repeating world entry or changing the roster. This fixes the route
  omission, not event eligibility, the14-actor failure or maximum capacity.
- [x] **E04 — Full-game compatibility.** Root accepts currenta28 ordinary and
  actual-ending flash cold-load54, retained Giza result plus native Lutia
  placement/full world menu/normal save/current-cold suffix16, and actual current
  ending/credits/scene-owned clear save/reset/Continue/cold14. Read-only review484
  authenticates188 current pins,28 historical reports/logs,52 notes and the
  unchanged gameplay-source/mission/scene dependencies. Historical connected
  milestones and earned final bridge retain their own declared inputs and ROMs.
  See notes/native-art-campaign-compatibility.md and both evidence indices.
  Three failed heap/menu/history expectations remain preserved; corrected tests
  do not relabel them. No uninterrupted full-combat replay or cross-ROM savestate
  claim. E05 reproducible full delivery stays open.
- [x] **E05 — Final assembled review and delivery.** Root review and final audit
  pass1091 checks /592 authenticated evidence files. Fresh eight-stage source
  prefix plus corrected eleven-stage art suffix reproduce the completea28 ROM.
  Package/launcher runner103642.038969Z passes deterministic BPS roundtrip,
  wrong-source rejection and145 actual launcher/reference-link checks, including all independent
  storage overrides and wrong-ROM rejection without launch. 31 immutable
  documents and the acceptance certificate ship with bundle461ec79a7f20f413.
  Sourcef07411c passes the Git index asset guard. Existing games/saves preserved;
  all failed build/audit/sandbox outcomes and finite coverage remain explicit.
  See notes/native-art-engineering-delivery.md and its pinned evidence index.

The all-ten source override, inventory/gallery and byte-exact no-change rebuild
already pass. Reuse them. Final artwork production remains a later session.

- [x] Art-team limitations documented in ART-TEAM-CONSTRAINTS.md and
  notes/art-team-contract.json: all native consumers, exact palette selectors,
  animation/source-writer restrictions, readable UI, allocation limits and
  targeted replacement acceptance. Documentation only; final art remains deferred.

## Historical narrowed scope: usable placeholders

- [x] Preserve and identify the tested separately playable placeholder package.
- [x] Audit the immutable ROM/patch/guide/manifest and19 retained acceptance reports.
- [x] Inventory and link all ten class body/menu sources and additional assets.
- [x] Give all ten jobs the same source-override interface; prove exact no-change build.
- [x] Provide local gallery, replacement template, guide and user-openable shortcut.
- [x] Preserve player files, installed indexes and failed draft evidence.
- [ ] Final production artwork and bespoke animations: deferred to a different
  session by the user. G01/G03/G04 retain only their final-art review scope;
  G02 and all engineering requirements are accepted through E01-E05.

The user explicitly changed the finish line to **working placeholders that are
easy to replace in a later session**. Final sprite quality and bespoke animation
are deferred. Use `ART-PLACEHOLDERS.md`, `Review Placeholder Art.cmd` and
`Prepare Art Pass.ps1`; do not continue detailed art refinement without a new
request. This supersedes earlier next-action instructions below.

The installed placeholder bundle remains7507ca5c / bundle3ea62acebcc34792.
It already includes the ROM, deterministic BPS, manifest, player guide and
independent-save launcher. The new local art desk audits immutable package
files,19 exact-candidate evidence reports, all ten class sources/conversions
and gallery links:171 checks pass. Its inventory distinguishes installed battle
and menu art from newer experiments. `battle-overrides.json` supports all ten
jobs, including117; `test-placeholder-override-roundtrip` reproduces the complete
installed ROM exactly (14 checks, runner20260918T222615.997789Z). All historical
source manifests and current/delivery indexes are restored. No game launched,
player save changed or site published. All runners are terminal.

The two private Samurai attack-reference runs failed strict body-display checks
at frames23 and53; both are retained. The first matched the known cross-sequence
constructor contract; the second is undiagnosed. These unshipped drafts do not
replace the passing packaged baseline. Source syntax and the first art-desk
schema mismatch were fixed; no ROM engine fix was made. Full production-art
G01-G04 remain deferred, not declared passed. The revised placeholder deliverable
is complete; a later art session can use the inventory and replacement guide.

## Open follow-up: native artwork and equipment preview (September 17, 2026)

Follow-up to `10fbf46`: built-in imagegen created eight Samurai support poses
(raised arms, recoil, kneeling and fallen; both facings). Private candidate
`5fe7c35d4b4a89e71f3cdc059e5bff75e747ee33` maps104 original frame occurrences
across40 land slots, preserving v7 engine/palettes, native timing, unrelated
pixels and installed indexes. Read `notes/samurai-support-actions.md`.
Declared build/native checks pass12,662/797; source conversion reproduces exactly
and all104 opaque baselines match original poses. All runners are terminal.
Native widget/phase tests do not prove live battle action playback. Back-view
head continuity, attacks, water and matching UI remain unfinished. Current
palette reservation has9,568 bytes left; plan additional authenticated data
space before adding larger sets. Installed7507ca5c, saves and sessions unchanged.
No new agents, external provider, publication or game launch. G01-G04 remain open.

Follow-up to `ef1ca96`: built-in imagegen produced Samurai march v7/v8.
v7 is selected for a private preview; v8 does not improve the eye. Exact native
pixel review corrects the initial claim that v7 eyes disappeared: all front
frames retain two white pixels. Read `notes/samurai-v7-refinement.md`.
Private connected candidate`d80e763169223d98284b180a39fa047f650d50e5` passes
art-input/default-build preservation8490, mixed fresh entry/full idle3097 and
actual paired Move/cancel6674 checks. Three exact generated moving frames and
own-palette hardware output are verified. Compiled engine differs only in the
Samurai32-byte palette; other class pixels and native timing/commands stay exact.
Installed7507ca5c bundle and player files/session remain unchanged; all runners
terminal. No new agents, external provider, publication or game launch.

Six-pose sheets now pass through an authenticated optional art override, since
the all-class palette stage superseded the older v4 walk assignments. Full
Samurai action/water art and matching menus remain unfinished; other actions
still repeat march poses. No full production-art acceptance or G01-G04 closure.
Next generate actual Samurai action poses and matching UI, then remaining nine
racial jobs. Use saved imagegen sources/review artifacts and passing transport
evidence rather than restarting technical implementation.

Follow-up to `edc7167`: corrected technical preview
`7507ca5cb03c1db7a717fd6d21d97a9f5a4ae08b` is packaged and launcher-validated.
Delivery bundle`3ea62acebcc34792` and final launcher runner213728.439405Z pass.
Nineteen exact-candidate evidence reports cover131,184 checks; deterministic BPS
roundtrip/wrong-source rejection and three isolated storage paths pass. The
full art-stage rebuild is byte-exact and preserves the authenticated runtime
fixture independently of gameplay source-build provenance. Existing player
files and running sessions are unchanged; no game launch or publication.

Read `notes/native-art-capacity-delivery.md` and `ART-PIPELINE.md`. Actual13-actor
capacity/Status return passes (two custom classes, four native allies, four
native enemies, four party total, judge; minimum sampled20,888 free heap bytes).
Prior six-party expectations and incorrect zero-root assertion remain failed
records, with evidence-based corrections. Current portraits, preview pages,
status/Status, held axe, Tomahawk impact, phase/timing and native import checks
pass. Shared highlight/damage and real Thundaga evidence are reused. Bounded
Move/cancel still costs4–5extra frames; maximum capacity/all effects/full campaign
are not inferred. The full runner statuses and all limitations are retained.

`Play Art Pipeline Preview.cmd` now resolves this immutable corrected package;
older previews and vanilla/v0.7 remain separate. All runners terminal. Root
reviewed implementation and visible preview/Status captures. The technical
art transport/delivery milestone is complete within this stated scope. G01–G04
remain open for full final-art acceptance. Next: agree/refine actual class
artwork using built-in imagegen only, then replace temporary repeated poses and
water crops through the proved native consumers. Do not restart completed
technical checks or use Gemini/fal/new agents without new direction.

Follow-up to `734c937`: connected candidate
`7507ca5cb03c1db7a717fd6d21d97a9f5a4ae08b` fixes native area-target highlighting
and colors1..15 damage/restore effects. Actual Thundaga371 now passes through
cast/hit/next-turn return with matching control outcome (damage14, MP80), zero
palette refusals and minimum33,668 free heap bytes in the bounded12-actor scene.
All-ten-palette native oracles, strict negative controls and a byte-exact full
art rebuild pass. Read `notes/native-art-target-and-damage.md` for exact reports,
retained failures, two test-reset corrections and observation limits.
Installed preview remains4a7d55ce and still has these known limitations; no new
package, visible launch, saves, external provider, agents or publication.
All runners terminal. Next: concrete larger encounter/effect capacity, final
current-candidate consumer reconciliation and updated delivery. Reuse applicable
passes; Thunder365 already passed on4a7 and is not an exact7507 acceptance.
G01–G04 remain open under full final-art scopes. Built-in imagegen only; sprite
refinement follows technical acceptance.

Follow-up to `e60d435` / source checkpoint `a81cd1e`: connected technical
preview4a7d55ce09cd4a40965a0bb97de2701d276789c5 is now packaged. Seven bounded
current-ROM consumer checks pass (95,260 assertions), including all-ten portraits,
Item List/Buy/Sell job pages, status icons, held axe and Tomahawk projectile/impact.
The initial fixed-character comparison failure is retained; the corrected exact
ROM portrait-literal control passes, reusing completed generic cases.
Full art-stage source rebuild reproduces the tested ROM. Packaging requires12
current-candidate reports, verifies deterministic BPS roundtrip/wrong-source
rejection, and passes launcher/save-path validation without opening a game.
Read `notes/native-art-connected-delivery.md` and `ART-PIPELINE.md`.
`Play Art Pipeline Preview.cmd` now resolves the new immutable package; prior
preview folders, vanilla/v0.7, all player saves and running sessions are preserved.
All runners terminal. The first packaging attempt's still-open-run refusal stays
visible alongside its successful rebuild. No Gemini/fal, new agents or publication.
Next remaining technical acceptance: concrete larger encounter/effect capacity
and representative natural custom-class casting/action families. Reuse current
passes; do not restart timing optimization or the completed menu/asset paths.
G01–G04 remain open under full final-art scopes. Built-in imagegen only; final
sprite refinement remains deferred until technical acceptance is complete.

Follow-up to `95ace44`: direct live observation reconciles the current mixed
Move/cancel palette differences as original native rotation phases. All 1,024
complete states/frames match ordinary execution; 5,173 boundary checks and
6,225 independent phase checks pass. The failed pre-navigation OBJ oracle is
retained. Root accepts the measured four-to-five-frame cancel cost for this
bounded Windows technical preview; no zero-cost claim or rejected optimization
is accepted. Read `notes/native-art-live-phase-reconciliation.md`.
Connected4a7d55ce / palette5eff9a70, installed preview and player saves/session
are unchanged. All runners terminal. Next: remaining natural consumers and
capacity, then assembled review and reproducible technical-preview delivery.
G01–G04 remain open under their full artwork scope. Built-in imagegen only;
final sprite refinement remains deferred.

Follow-up to `da16841`: the whole-frame palette-plan cache is rejected and
removed from production source. Final trial8c988cf2/f48949dc passes10,714
component and9,814 native/rebuild checks, but its hit path is slower despite
89–91% hits. Matched exact-ROM original-planner control shows Move3–4 frames
longer; both actual entry variants fail native phase. The source patch, all
failures and raw traces remain private. Read `notes/native-art-plan-reuse-trial.md`.
The observer now supports a control that keeps all class composition enabled.
Production rebuild restores palette5eff9a70 and connected4a7d55ce byte-exact;
installed preview, player saves and session unchanged. All runners terminal.
Next locate long native foreground subroutine/task intervals and distinguish
native phase scheduling from palette-write corruption with direct events.
Do not repeat whole-frame key caching based on hit rate. Capacity, remaining
natural consumers and delivery remain open. G01–G04 remain open; built-in
imagegen only, final sprite refinement deferred.

Follow-up to `87cc1d4`: native instruction observation now matches ordinary
emulation across1,024 complete Move/cancel frames (1,069 checks). Read
`notes/native-art-instruction-trace.md`. The exact current4a7d55ce mixed battle
shows first-frame input reception but4–5 extra frames to cancel with composition
active. Mean composition is28.21–29.75 scanlines versus2.76–2.79 in the bypass.
This is diagnostic evidence, not a timing fix or acceptance. Rejected stepping
and three restoration/replay failures are retained; the final comparison uses
fresh cores, identical navigation and every native-state/framebuffer byte.
All runners terminal. Production/current palette5eff9a70 and connected4a7d55ce,
installed preview, player saves and session are unchanged. Next investigate
validated plan reuse across unchanged OAM/ownership/tile inputs; preserve
repeated-frame overlays and native palette phases. Larger-scene capacity,
remaining natural consumers and delivery remain open. G01–G04 stay open;
built-in imagegen only and final sprite refinement deferred.

Follow-up to `0c423ae`: a mixed-class planner experiment reduced composition
instructions by about24% and movement duration by one frame at five of six
input offsets, but response remained inconsistent (including a two-frame cancel
regression) and actual entry failed native palette-phase acceptance. The trial
is rejected; source and private current build are restored byte-exact to
connected4a7d55ce /palette5eff9a70. All runners terminal. See
`notes/native-art-multi-preferred-trial.md` for the failed run, component checks,
six-offset matched-state comparison and retained patch. Next trace actual native
input/scene/VBlank event boundaries; do not repeat micro-optimizations on counts
alone. Existing Status/world-menu evidence remains applicable. Package, player
saves and session unchanged. G01-G04 remain open; final sprite refinement deferred.

Follow-up to a2c8b5c: the actual read-only battle Status entry now uses the
native-sized context/list area, preserving the expansion copy tail. Free memory
while Status/help is open rises1,068 to11,052 bytes; return restores54,632.
Native lifecycle152 also passes with an extra8,192-byte held allocation.
Current private connected4a7d55ce09cd4a40965a0bb97de2701d276789c5 has palette
parent5eff9a70 (`build/art/live-palette/status-current.json`). Native/rebuild9814,
fresh mixed entry632, world460-row bounds80, both-race preferences24, equipment
UI30, connected rebuild3981 and actual Status/help/return38 pass. Read
`notes/native-art-compact-status.md` for source, exact reports and retained
harness failures. All runners terminal. Package/player saves/session unchanged.
Next: compositor/input timing, larger-scene/effect capacity, remaining natural
consumers and assembled delivery. G01-G04 remain open; built-in imagegen only,
final sprite refinement deferred.

Follow-up to fb3889c: `test-art-scheduler-phase` passes109 diagnostic checks
in runner20260918T181759.118342Z. Six input-arrival offsets on the same exact
mixed battle show both native phase variation and remaining compositor cost:
Move47..50 versus46..47 frames, cancel1..5 frames later. Ordered logical motion
and canonical player records match in all12 cases. This does not accept timing
or normalize prior phase failures. Read `notes/native-art-scheduler-phase.md`.
Production/current d9acd723 and its package/save/session state are unchanged.
The20 retained water endpoints have the same heap capacity as this12-actor
shell; no new worst-case acceptance. Next trace battle Status list consumers
before restricting its large allocation to editable menus. All runners terminal;
G01-G04 remain open, built-in imagegen only, final sprite refinement deferred.

Follow-up to a56dac6: investigated the remaining movement delay with a scoped
IWRAM planner. Rejected it after an exact-state comparison: planning fell from
11.8625 to9.3942 scanlines, but Move began one frame later; movement duration and
cancel were unchanged. Both actual trial battles still failed phase/timing.
Read `notes/native-art-scoped-planner-trial.md`. Trial implementation is removed;
restored source rebuilds the existing connected `d9acd723` byte-exact. Its prior
menu/name-entry/equipment evidence remains applicable. No new runtime acceptance,
package/save/session change or G-gate closure. Next investigate the native
scheduler/entry-phase relationship and worst-case scene/menu capacity before
another timing optimization. All runners are terminal.

Current private connected candidate: `d9acd7234186a77561a2fb4ee91fdae2197c197d`,
resolved through `build/art/connected/current.json`; palette parent `ff6a50ea`.
Read the shared-heap/keyboard follow-up in `notes/native-art-owned-menu.md`.

Actual mixed-battle Status now opens and returns with the class artwork intact.
It borrows the native battle heap for individually owned menu allocations;
exact caller guards preserve ordinary world heap initialization and teardown.
Native fragmented-heap lifecycle44, fresh mixed entry632, actual Status25,
world bounds80, both-race preference24 and equipment UI30 pass on `7b966543`.
The final candidate differs by exactly one byte, the US keyboard allocation.

Fresh name entry now allocates two actual native pages (16,896 bytes), replacing
the unused six-page allocation (50,688 bytes). Both tabs/wrap directions, native
lettering, letter/digit editing, committed story name and allocation release pass.
The actual cold run's first pixel comparison included two animated cursor pixels;
its complete captures are authenticated and reconciled with the established
native glyph crop:182 checks. Free name-entry heap is22,780 bytes. Final palette
rebuild/reset9811 and connected rebuild/native3981 pass. All runners terminal.

Retain all failures, including the original black Status screen and the keyboard
harness/control mistakes. No package, player save or session was changed.
Next: remaining movement/phase timing, worst-case encounter/menu heap capacity,
remaining natural consumers, final assembled acceptance and reproducible delivery.
G01-G04 remain open. Built-in imagegen only; final sprite refinement deferred.

### Prior retained failures and scoped evidence

Latest live gate: `test-art-owned-menu-battle-ui` **FAILS** on661853ea. Native
Status parent request60,672 exceeds total free53,596 and largest block41,640;
actual screen black, parent NULL. Runner20260918T165502.509792Z and raw evidence
are documented in `notes/native-art-owned-menu.md`. World-menu and bounded
constructor passes below do not close this live lifetime/capacity gate.

Latest: `notes/native-art-owned-menu.md`. Candidate661853ea8e9850cf4352705ed506c4e49dee8505
fixes the actual palette/item-list overlap with a context-owned list and all
three parent allocations. Final bounds80, preference UI24, Inventory/Buy/Sell30,
palette rebuild/reset9807 and connected rebuild3981 pass. Earlier mixed632,
held90348 and status206 retain their original ROM/input scopes. Rejected extra
reservation and initially incomplete parent fix remain explicit failures.
Live in-battle party-menu capacity, opening heap pressure, timing, remaining
consumers and delivery are still open. G01-G04 are not complete; final sprite
refinement remains deferred and uses built-in imagegen only.

Read `notes/native-art-connected-consumers.md`. Follow-up2d18368. New private
connected candidateb4993232e05eeb20ce536cca6f4b9738aa4a2b12 resolves through
`build/art/connected/current.json`; palette parent remains6443725d. Explicit
status, equipment/projectile, held-axe and impact stages preserve all current
actor pointers and palette hooks. Historical indexes and installed builds stay
unchanged. Native/rebuild3981 and four-class mixed-entry632 pass.

Actual connected Soldier Tomahawk with four new racial allies passes4069:
moving axe, all three impact poses, exact class/effect colors, natural Dancer
bank6->7->8 handoff,18damage/4MP and following turn. Both controls share the
generated impact. Four-frame samples are not every effect/caster-class coverage.
The earlier HUD `WHT` diagnosis was wrong: the visible `WT` is native turn order.
No missing HUD class-label consumer was established; no HUD patch was made.

G01-G04 remain open. Movement timing/phase failure is inherited and unresolved;
other action/effect lifetimes, maximum heap, assembled status/equipment consumer
review and delivery remain. Existing all-ten water evidence stays scoped to its
unchanged palette parent; not replayed on the connected candidate. Built-in
imagegen only, final sprite refinement deferred. No package, save, session,
external-provider or publication change. Reuse applicable passing evidence.

Read `notes/native-art-racial-water-coverage.md`. Follow-up34e732d. Candidate
remains6443725d256252afae127393945934961eb9abd6; no production ROM change.
Corrected a test-fixture race error: jobs122/123 are Moogle,124/125 are Viera.
The older mixed results are retained but no longer claimed as same-race proof.
Four corrected groups now pass632 checks each and cover all ten jobs.

All ten classes now pass native land/water/cancel resource and generated-palette
checks on intact original map92 geometry through the declared encounter shell.
Samurai/Viking use retained eight-frame samples; the other eight use every-frame
samples. A strict queued-facing proof addresses the original Judge upload
boundary; two failed runs remain recorded. Read-only reconciliation310 verifies
all ten focus bodies and actual palettes from authenticated raw captures.

G01-G04 remain open. The subsequent connected-consumer checkpoint corrects the
misread HUD WT indicator; it is not a donor job abbreviation. Other action/effect
lifetimes, battle timing, cross-bank/maximum heap, final art and delivery remain
open. Built-in imagegen only; final sprite refinement deferred. Installed package,
vanilla, player saves and session unchanged. Reuse applicable passing evidence.

Read `notes/native-art-rotation-permutation.md`. Follow-up31aa28d. Current
6443725d256252afae127393945934961eb9abd6 adds optional `--fast-rotation` to the
20-history/all-class/workspace/provisional build; state11312, stage243876.
Whole-state permutation168, native/rebuild9797 and full-mask first-visible
rotation1595 PASS. The prior one-update unowned palette lag is fixed without
mask reduction or a changed acceptance comparison.

Actual Move/cancel still FAILED: all1205 samples differ in native palette phase;
Move starts one frame late, cancel three, while both walks take47 frames.
Exact-state compositor bypass isolates zero extra Move frames and three cancel
frames. A separate deferred-allocation-preparation trial showed no reliable
improvement and was removed; its source/evidence are retained in the note.

Next diagnose remaining compositor/scheduler cost using the exact retained
checkpoints, and complete Samurai/Moogle mixed/natural-lifetime/cross-bank/heap
coverage and delivery. All G gates open. Built-in imagegen only; final sprite
refinement deferred. Existing installed package, player saves and session intact.

Read `notes/native-art-provisional-history.md`. Follow-up854c420. Current
f36376dee8303a4220dd0fc5c2cf37a8e2ac094e uses low-address workspace placement and
provisional palette identities; state11312, stage243788, same12KiB reservation.
Component43, native/rebuild9797, late-entry731 and both four-class actual mixed
entry groups622 each pass. Opening fade now has zero refusals. Confirmed absent
actors retain strict unknown-target checks; fresh appearances require a genuine
palette baseline. Legacy single-history and stale-backup test failures are
retained and corrected using native evidence, not ignored.

All-class late rotation remains FAILED: one unowned native bank update lags at
first appearance. The prior e1c22b01 fails identically; changing only the current
custom enable mask1023->2 passes1595. This isolates additional history work.
Next optimize repeated history rotation/update work and recheck the exact
full-mask hardware-phase comparison. Do not drop unseen histories or waive it.
Samurai/Moogle mixed coverage, other natural lifetimes/cross-bank/timing and
remaining assets/delivery stay open. All G gates open; imagegen only; final sprite
refinement deferred. Installed package, player saves and session unchanged.

Read `notes/native-art-workspace-placement.md`. Follow-up dbe4fe0. Diagnosed
mixed turn failure: a late persistent9824-byte expansion pool fragments native
RAM, causing a39944-byte allocation failure and subsequent NULL-free corruption.
New optional low-address pool placement resumes native allocation/split/free.
Candidate e1c22b0153d2510786e42f7b9645f752122a5f3a resolves via
`build/art/live-palette/all-classes-workspace-current.json`; component246 passes.
Earlier337a26c9 passes the former turn stall but mixed acceptance still FAILS on
seven palette target refusals. Second group unrun; no promotion.

First target refusal now captured at frame2011: seven speculative class matches
on native bank12, no custom actor emitted, followed by a different palette table.
Next distinguish provisional matches from real actor history without weakening
strict target checks or losing off-screen/first-visible effects. No such fix yet.
Rejected early-allocation trials and all diagnostics remain explicit in the note.
All G gates remain open. Built-in imagegen only; sprite refinement deferred.
Existing package/player saves/session unchanged; reuse applicable passing evidence.

Latest: `notes/native-art-history-capacity.md`. Twenty-history component115,
private native1153/appearance1595 pass. Separate4b35081b enables all ten generated
class palettes; native9793 and individual menu963 pass. Mixed battle remains
FAILED: candidate turn timeout plus seven target refusals after preserving
Montblanc; two earlier five-profile control deployment failures retained. Second
group unrun. Default05c66b38 and installed builds unchanged. No all-class battle,
maximum heap, timing, final-art, delivery or G-gate acceptance.

Latest: `notes/native-art-composition-memory.md`. Private05c66b38 reduces actual
palette-planning work (11.48 versus13.15 scanlines) and matched-state cancel cost
(+1 versus+3 frames). Profile286/isolation3912/native1153/planner48009/ownership712/
transitions2933 pass. Full battle phase/input failure remains; no G-gate closure.
ARM-mode trial rejected. Before enabling all ten classes, address observed-color
potential history demand17 versus capacity10. Only Human Dark Knight currently
uses custom palettes. Natural lifetimes/cross-bank/final art/delivery remain open.

Latest: `notes/native-art-compose-profile.md`. Instruction profiler added;
grouped-marker trial7cb635d5 passes components but fails actual timing/phase.
Its lower instruction count does not establish acceptable gameplay performance.
Trial rejected and2908487c restored byte-exact; expanded planner48009 passes.
Prior live evidence remains applicable. All G gates remain open; no package,
player/session or final-art acceptance change.

Latest: `notes/native-art-unseen-rotation-live.md`. Unchanged private2908487c
passes1595 actual unseen-rotation/cycling appearance checks, including the first
visible frame in eight scenarios. Native clear/rebuild1153 now explicitly runs
ARMv4T. Current exact-ROM timing diagnostic30 still measures Move+1 start/+1
moving frame and cancel+3; it does not close the full battle timing/phase failure.
Natural transitions, mixed-class capacity/cross-bank, complete assets/final art/
delivery and all G gates remain open. No player/package/session changes.

Latest: `notes/native-palette-timing-followup.md`. Private2908487c adds BG-only
callback bypass, aligned bank copying and correct unseen-rotation DMA latching.
Current isolation3912/late-entry4834/native1153 pass, with explicit reuse of
unchanged bank-copy/rotation checks. Initial cross-ROM timing reports are invalid;
saved actor pointers require exact ROM identity. Corrected9d577c53 replay and
1fdf40a6 full battle retain timing/phase failures. No performance closure, current
full battle claim or G-gate closure. Live unseen-rotation appearance, natural
lifetimes, capacity/cross-bank, other assets/final art/packaging remain open.

Latest: `notes/native-art-rotation.md`. Private21f24d6f adds type2 rotation of
colors/fade state and type4 literal cycling, including partial single-bank
ranges and concurrent fades. Component38146/live1297/native rebuild1153/binding32
pass. Static audit prioritizes reachable rotation/cycle/script consumers over
unreferenced teardown/stream/frame helpers; dynamic reachability is not proven.
Cross-bank mapping, natural lifetimes, capacity, prior timing/phase failures,
remaining assets/final artwork/packaging and all G gates remain open. No player
or package changes; no broad suite. Built-in imagegen only.

Latest: `notes/native-art-task-controls.md`. Privatedebb7445 adds full/range
cancellation, direct/all deletion and completed collection. Generated colors
follow only surviving ranges; native pause/resume holds interpolation. Component
40352/live2013/native rebuild1151/binding32/fade7284 pass, with exact native state
and ABI preservation. No batch failures or broad run. Palette heap destruction,
separate constructors/rotation/copy, natural scene lifetimes, capacity/assets,
prior timing/phase failures, final art/packaging and all G gates remain open.
No package/player/session changes. The task-selector assumption was corrected.

Latest: `notes/native-art-table-colors.md`. Private98cfcfc8 adds the two source-table
target setters with class/brightness mapping, exact original conversion and no
source/current-color mutation. Component17400/live599/native1147/late-entry4834/
binding32 pass. Fourteen common-setup target setters are hooked; arbitrary unknown
tables, separate cancellation/control/rotation/copy, natural scene/heap/stack,
maximum mixed-class capacity and remaining assets are still open. Prior timing/
phase failures, all G gates, final art and packaging remain open. No player change.

Latest: `notes/native-art-extended-colors.md`. Privatef637b43f adds weighted mix,
fractional bright/dark and uniform/RGB exposure with exact native immediate source
floor. Component13000/live854/native1145/late-entry4146/binding32 pass. The failed
short-hook r3 overwrite is retained and fixed with16-byte preserving entries and
a builder guard. Remaining table-source setters, task-control/rotation/copy paths,
natural scene/heap/stack lifetimes, maximum capacity/assets, phase/response gates,
final art and packaging remain open. No G-gate closure or player/package change.

Latest: `notes/native-art-late-entry.md`. Privateaf008a20 tracks supported native
effects before first ownership and preserves absent active/completed histories.
Current component2426/live hide-reveal727/native1140 pass; prior74c07 direct
color6344/live791/reload699/deployment587/variant23 remain applicable. Alternate
slots start with their source-class colors; absent DMA latches track native phase.
Fixed-slot test failure retained and corrected using recorded class/bank identity.
This is controlled late-entry proof, not every natural scene or maximum capacity.
All G gates, remaining consumers/lifetimes/assets, timing/phase, final art and
packaging remain open. No player/package changes or broad regression run.

Latest: `notes/native-palette-reloads.md`. Privateae167efa adds normal/dim native
copy reloads preserving active fade state and the hardware latch. Native1140,
ARMv4T229 and actual deployment587 pass; reuse22d8 hardware reload694 and
transitions2933. Unknown displayed data refuses; dormant history retires with
future reauthentication. A real black-screen ARM/Thumb bug is fixed; its false
newer-CPU component pass and all failures remain explicit.22d8 battle still
fails phases/response, with47-frame movement and exact1205 generated overlays.
Late entry, remaining consumers/lifetimes/assets, final art, packaging and all
G gates remain open. No player/package changes or broad regression run.

Latest: `notes/native-art-color-operations.md`. Private6fa4fd9c supports native
gray/preset tint/RGB/solid target operations with exact original conversion.
Native1139/component6344/live hardware782/binding32 pass, including interruption
and restoration. State8096 unchanged, status shortcut retained. Prior29453
same-input compositor3900 proves unowned color/OAM/native memory isolation over
seven BG phases and both DMA cases. This does not close full-route phase/timing
failures. Reload/late entry, remaining effects/lifetimes/assets, final art and
all G gates remain open. No package/player change; failed harness runs retained.

Latest: `notes/native-status-iterator-cost.md`. Private29453def adds a32-byte
native status shortcut with equivalent future-build C source. Component104472
and native/rebuild1135 pass. Actual movement126->47 frames; a parent with the
same status fix also47. Battle still FAILS on phases and two/four response frames;
all1205 generated overlays exact, zero refusal/failure/wrap, maxdisplay205.
Matched-state diagnostic1212 isolates one/three response frames, zero moving-frame
overhead. Initial dead-flag test failure corrected at authenticated native flag
consumer; all failures retained. Remaining lifetimes/consumers, final art and
all G gates stay open. No package/player changes or broad regression run.

Latest: `notes/native-palette-composition-cost.md`. Matched-state diagnostic2424
proves current21052's composition adds four moving frames; a counted-tail trial
was slower and removed. Current21052 reproduced byte-identically; existing
evidence/failures remain applicable. Investigate native skipped-update cadence
and repeated-frame work next. No G-gate, timing, final-art or package closure.

Follow-up to06c5fdc: native OBJ cycle2673 proves the actual source and six-call
rotation; retained parent/candidate colors are exact native phases. Scheduling
and timing remain unaccepted. Slower multirow scan trial discarded; current21052
reproduced byte-exactly, native1134 and expanded planner47961 pass. No gate closure.

Latest: `notes/native-deployment-palette-variants.md`. Private21052ed6 supports
simultaneous normal/dim deployment bindings with exact native brightness and
source-class identity. Component23/native1134/fades610/transitions2933 and
deployment587 pass, including65 consecutive simultaneous observations with zero
refusals. Exact retained replay proves a queued constructor rewind (13checks;
prior queued8 also pass). Battle remains FAILED:126 versus123 movement frames,
cancel12 frames late and native phase differences. All1205 overlays retain exact
colors, no wrap (max206), unsupported0. State8096 fits8KiB. All G gates, remaining
color/lifetime/asset consumers, package and final-art acceptance remain open.

Latest: `notes/native-palette-scan-performance.md`. Private7e2b8b86 trims exact
native hidden-object markers and executes the pixel scan from bounded temporary
IWRAM with a ROM fallback. Planner47479/native1128/transitions2933/fades610 pass.
Battle remains FAILED: movement126 versus123 frames (previous135), cancel11
frames later, native phase differences and unsupported149 atready. Complete1205
sample audit preserves exact generated colors, no wrap (max204) and available
native-code fences. Native cycle264 and portrait draw7 prove only their stated
diagnostic scopes. All G gates, lifetimes, variants, remaining assets, packaging
and final-art acceptance remain open. Player/package files unchanged.

Latest: `notes/live-palette-preferred-bank.md`. Private `4cf2dcb9` validates
preferred banks against current OAM/pixels, combines ownership collection and
backs up only overwritten palettes. Native 1128, planner 32089, ownership 496,
transitions 2933 and fades 610 pass. Eight-frame battle inputs complete the route,
but battle acceptance remains FAILED: native color differences, 135 versus 123
movement frames and a 12-frame cancel delay. All 1205 sampled overlays retain
exact generated colors without scan/display wrap (max 207). Unsupported variants
already count 147 at ready. Slower row-cache trial removed; failed evidence and
complete retained-trace audit preserved. All G gates, packaging and final art
remain open; player files unchanged.

Latest: notes/live-battle-palette-lifetime.md. Privatefb62e2e0 adds actual battle
ownership and fixes palette dropout on ordinary skipped-DMA frames. State8060
fits8KiB. Native1128/planner775/transitions2933/menu99/fades610/queued-reset8 pass.
Battle remains FAILED on strict native-shadow equality. Its1205-sample Move/cancel
trace has no wrap (max220), but native motion is slower; earlier8-frame input misses
are not accepted by the new16-frame scenario. Variants report151 unsupported events
beforeMove. Keep all G gates open; package and final-art acceptance unchanged.

Latest: notes/live-native-palette-fades.md. Private267d310f proves native fade
binding through actual callback/DMA playback: black/white/baseline restore,
interruption and cancel/reopen. Fade610, native1127, menu99, transitions2915 and
binding32 pass. Original-bank identity is captured before remapping; reservation
is now8KiB at0203D000. Remaining operations, reloads, late entry/variants, battle
coexistence, heap capacity, worst-case timing and final art stay open. Failed
compile and obsolete-private-endpoint run retained. No package or G-gate closure.

Latest: notes/native-palette-transitions-and-fades.md. Private19c8d9e0 fixes seven
transition scan overruns and a one-frame native palette delay. All571 paired
frames pass with actual display enable by221; suspension/resume is directly
covered. Planner426, transitions2710, native1122 and menu99 pass. Native fade
sidecar7284 checks pass in isolation, but live fade target/ownership binding,
color variants, battle coexistence, heap capacity and worst-case timing remain.
Three failed runs retained. No final-art or G01-G04 closure; package unchanged.

Latest: notes/live-dark-knight-palette.md. Private caff9140 proves live generated
Dark Knight colors through wheel/header/cancel/reopen/world return, with native
shadow/unowned-color isolation and restoration. Planner 413, menu 99 and native
rebuild/clear/transport 1121 pass. Native hooks and a private 4KiB heap reservation
are implemented. Fades/suspension/variants, battle coexistence, heap capacity,
worst-case timing and final art remain open. Six failed runs are documented.
Packaged a6d883b5 is unchanged; this does not close G01-G04.

Latest: notes/native-actor-palette-ownership.md. Native renderer/compositor plus
compiled owner tracking and allocator connection pass 352 targeted checks.
Both buffers, clipping, reset/reuse and stale ownership are covered in isolated
ARM execution. Live hooks, owned storage, original-palette restoration, fades,
timing and production art remain open; no playable ROM replacement or G closure.

Latest technical implementation: notes/native-actor-palette-planner.md. Compiled
frame planner/applicator passes408 checks, native palette-offset contract81,
and50-capture ownership inventory351. All sampled actor banks are shared;8bpp
portrait demand is measured from pixel indices. Live owner tagging, frame hook,
restoration/fades, battle/coexistence/timing and production art remain open.
Two failed runs retained; no playable candidate replacement and no G closure.

Latest: notes/samurai-motion-dark-knight-palette-review.md. Imagegen Samurai v6
now shows alternating lifted feet in native conversion; face/helmet drift stays
unaccepted. New Dark Knight study confirms assigned-palette color loss (violet
to green, burgundy to brown); a generated palette improves color retention but
has no native allocation proof. Prioritize the open independent actor palette
consumer work next. No draft import/runtime/package change; all G gates open.

Newest art progress: notes/samurai-refined-imagegen-review.md. Built-in-imagegen
v4 converts consistently to 16x27 with clearer front features, and private
0fa7d170 displays three generated phases in real Move/cancel. Import/rebuild
10,644 and movement 3,649 checks pass. Visual stepping/costume continuity is
unaccepted; no final-art G gate closes. Conversion evidence now separates
same-name revisions by source/settings/palette. Packaged a6d883b5 unchanged.

Latest: notes/explicit-generated-animation-transport.md. Optional per-frame
imagegen assignments now preserve default output and native timing/metadata.
Private a860ad38 passes 10,641 import/rebuild and 3,649 paired Move/cancel checks;
four explicit payloads appear during actual Samurai movement. Native manual
phase/reset controls pass 9/19. Four failed runs remain retained. Visually the
draft is oversized and unaccepted. Packaged a6d883b5 remains the technical
delivery; final-art and full-scope G gates stay open.

Newest water evidence: notes/native-natural-water-proof.md. Original map92's
intact native geometry/rendering in the declared encounter shell now passes7,889
paired Viking water-transition/cancel checks on a6d883b5-derived fixtures. Native
pending-upload controls pass16; both failed runs are retained. This supplements
the older synthetic Giza water flag proof. Original map92 campaign, every class/
action in water, independent actor palettes and final art remain open.

Newest: notes/samurai-three-pose-transport.md. Direct native-palette conversion
passes51 checks; PNG-to-native three-pose Samurai idle transport passes613 native/
actual-menu checks on private352df0a6. Packaged a6d883b5 remains unchanged. Original
idle is a three-pose stepping cycle; the older fixed-feet criterion was incorrect.
Retain that study's measurements without treating foot movement alone as failure.
The first allocation assertion failed and was corrected against retained native
evidence. Current drafts remain unaccepted art; G01-G04 are not closed.

Latest art study: notes/samurai-native-scale-revision.md. Built-in imagegen
improves the Samurai's native human proportions and eye/crescent readability,
but its four-frame idle sheet fails costume/foot consistency. It is not imported
or accepted production art. Exact prompts/hashes, native reference dimensions
and reproducible conversion/continuity evidence are retained. Packaged a6d883b5
and all prior runtime evidence are unchanged. Final-art gates remain open.

Latest delivery supersedes older private-candidate statements below: see
notes/assembled-art-technical-delivery.md. a6d883b5 is now a separately playable
expanded technical preview through Play Art Pipeline Preview.cmd, with verified
BPS/manifest/guide and independent save storage. All ten actual portrait/idle/
wheel combinations, axe UI, both-page native eligibility and Item List/Buy/Sell,
eight-stage art reproduction and affected native map loaders pass. Failed fixture
lookup and premature packaging runs are retained; completed passes reused.
Launcher validation passes without launching or changing player files. Existing
native actor palettes remain a declared conversion constraint; expanded actor
palette allocation is deferred to final sprite refinement. G01-G04 remain open
for final art and explicitly uncovered full-scope acceptance; technical delivery
alone is not whole-checklist completion.

Latest direction: stop Gemini/fal; use built-in imagegen and complete technical
integration first, then refine actual sprites. Temporary generated assets are
allowed for consumer proofs, without closing production-art acceptance. The
older provider-comparison phase below is discontinued.

Latest: notes/native-status-equipment-transport.md. Status glyphs pass201
native/actual checks; axe icons pass5,131 native and27 combined Inventory/Buy/Sell
checks. These are temporary imagegen transport assets, not final artwork.
Clean reference export also discovered139 data-word corruptions in shipping
1b070824's broad relocation scan. All522 original icons are valid; the earlier
malformed-original explanation was wrong. Verified native literal provenance
and private repair pass1,234 checks; copied-palette repair/copy audit passes839.
Latest private child37afe0a7 is uninstalled. Full repaired-data impact review,
clean build and assembled acceptance remain required. Historical R02/R03
completion below does not establish acceptance of this newly discovered defect.
Fresh integration-base source rebuild now passes225624.478523Z; exact base
reconciliation and15 repaired map component decodes pass87 checks230044.156917Z.
The generated-art chain now rebuilds from that base with authenticated preview
replacement and three rejection controls. Held weapon276 and all17 axe icons
are integrated in private be82fceecd0f05d9935091f3f2400c6ebacfa2c3. Native held
checks5,176, actual Inventory/Buy/Sell26 and fresh paired battle8,325 pass in
232447.092244Z. Native equipment acceptance5,133 includes all522 original icons.
See notes/native-held-weapon-transport.md for retained failures and exact reports.
Actual generated Tomahawk projectile now passes52 checks233434.673903Z. Its
separate primary impact pipeline passes29 reference/native/DMA checks, then3,707
native selector/loader/rebuild and42 actual three-pose/next-turn checks on
a6d883b5d7657f10c3eb6d9b8407c489d287dbc7 in234709.326823Z. Built-in imagegen
created the temporary impact; original Throw stays unchanged. See
notes/native-projectile-effect-transport.md. Custom palettes/other actions,
other effect formats, native repaired-data consumers and assembled delivery
are open. Temporary poses are not final art.

Latest technical water proof: notes/native-water-render-proof.md. Paired Viking
Move into a declared water-flag tile and B cancel back to land complete with
native261/260 body rendering. Retained acceptance passes40 checks, reusing7,885
recorded checks and rejecting six corruptions; both earlier failed runs remain.
This does not close natural water-map, all-class/action, auxiliary graphics,
custom-palette, final-art or delivery coverage. All G gates remain open.

Historical correction (provider/council phase now discontinued): current
designs/conversions were rejected by the user. See
notes/art-provider-comparison.md. Do not treat earlier favorable concept
comments or the published gallery as acceptance of any production artwork.

The user-requested three-member art council reviewed all ten imagegen designs.
All remain drafts; no G gate was closed by the review or gallery. See
notes/art-council-2026-09-17.md for per-class findings and revision priorities.
The separate Sites gallery pairs generated sheets with unfinished game-size
conversions, preserving their failures for review.

The historical v0.7 acceptance below did not cover the equipment eligibility
grid shown in the user's Bronze Helm screenshot. Its omission of new classes
is a confirmed display gap; the earlier blanket completion statement must not
be read as acceptance of that screen. Custom artwork is newly authorized scope.

- [ ] G01: Trace and extend the equipment preview grid to include all ten new
  racial jobs, with correct equipment eligibility and readable icons/labels.
  Inventory/Buy/Sell pagination and native eligibility now pass targeted checks.
  Original portrait drafts and revised labels are in the private candidate;
  final art/readability review and assembled delivery remain open.
  The separately packaged prototype now combines temporary imagegen portraits
  with all three grids. Final art and complete-scope delivery remain open; see
  notes/art-pipeline-technical-preview.md.
- [x] G02: Extract a large, authenticated private native reference library;
  final native import/consumer acceptance is established by E02 and the complete
  source rebuild in E05. The chronological partial proofs below stay historical.
  Original requirement:
  prove lossless donor export/import including palette, tiles, OAM, sequences
  and metadata, then an isolated custom replacement through actual consumers.
  Unchanged land/water relocation passes3767 native checks; separate menu38
  and actual land deployment/idle105 checks pass on7d9355d7. Generated idle
  pixels pass actor/frame/allocation isolation and hardware palette checks on
  06cc1297:2303 generated battle checks. Retained-capture oracle2212 checks and
  four corruption controls pass. The earlier fixed-block failure is preserved.
  Custom palette/action/water acceptance is still missing.
  Miniature decoder/rebuild passes1,447 checks; generated Samurai wheel image
  passes91 display/palette/isolation checks. A caught palette mismatch is fixed
  and its failure retained. Other jobs' figures and larger portraits remain open.
  All20 private land/water resources now pass28,037 native preservation checks
  on8c28684b; their payloads are byte-exact in35a80141. The real8-bit menu
  truncation is fixed in two distinct components. Five-race display comparison
  passes425 checks; native header/widget lifetime checks pass464. Failed runs
  remain retained. Generic-widget full display/teardown, all-class generated
  transport and remaining consumers remain open. See notes/native-class-resource-width.md.
  Subsequent real dispatch-widget tests found and fixed the missing animation-
  mode reader: base5d8fcf3a passes512 native and197 actual UI checks. Ten-class
  generated candidate595782ba passes463 native/rebuild checks and1,127 retained
  display checks. Its original cancellation-comparison failure remains retained;
  corrected native-record ownership verifies the full captured cohort. Large
  portraits and other native consumers remain open; see notes/all-class-generated-transport.md.
  Large-portrait transport now passes on75029dea:4,020 original roundtrip,
  1,796 current native/rebuild and355 actual menu checks. All ten independent
  faces render alongside their idle actors/wheel figures, including cancel/reopen.
  Originals and actual named-character controls are preserved. See
  notes/native-large-portrait-transport.md; temporary crops are not final art.
  All770 present non-idle land/water descriptor slots now have temporary
  generated transport on714f45eb;26,640 native/rebuild checks pass. Actual paired
  battle proof fails on its75029dea baseline at Fight selection before the new
  action build runs. No battle/action/water acceptance: isolate this failure
  first. Reports and full failed state retained; see notes/native-action-water-transport.md.
  The preceding Fight-entry failure is now resolved as test setup; no ROM fix.
  Candidate714f45eb passes8,131 paired actual Move/Fight/return checks, four
  generic deployed bodies and Viking modes3/7/87. Canonical formation and
  named identities are preserved. All historical failures remain, with corrected
  frame/root/auxiliary-effect oracles; see notes/native-action-battle-proof.md.
  This is not real water playback or every weapon/action-family acceptance.
- [ ] G03: Generate and integrate original-style artwork for the ten racial jobs,
  their menu/party/portrait consumers and new equipment/effect/status assets.
  Start every class character design on a blank canvas with distinct silhouette,
  clothing and equipment; the Ninja-with-crest Samurai was explicitly rejected.
  Original FFTA characters are references only. Inventory each consumer separately;
  do not count reskins, construction drafts or concept sheets as finished imports.
  Latest instruction: all artwork creation/revisions must use imagegen. Earlier
  manually coded portraits are superseded drafts. The generated Samurai model
  v2 is a design reference. Generated idle v4 has a private native import POC,
  not completed animation or aesthetic acceptance; v3 and initial median-cut
  conversions lost facial details and are superseded/rejected conversions.
  Imagegen also produced Human Dark Knight, Bangaa Viking, Bangaa Dark Knight
  and Nu Mou Chemist idle design drafts. Viking v1 crossed a cell boundary;
  imagegen v2 fixes spacing. Dark Knight facial detail still loses clarity at
  native scale. These designs are neither imported nor production accepted.
  All ten classes now have imagegen design drafts, including Geomancer, both
  Moogles and both Viera. Their32x32 conversions expose lost face/outline details
  and a rejected Moogle Chemist palette shift. See the per-job imagegen catalog;
  no complete actor animation set has been accepted or installed.
  Ten original menu portraits now dispatch through the native icon decoder;
  direct pixel/canary checks and Samurai teaching-panel playback pass. These are
  source-row drafts. Full actors, wheel miniatures and other consumers remain open.
  All ten existing generated drafts now have technical land-idle and separate
  wheel-figure imports. The real ten-class menu displays are verified; four-cell
  drafts repeat poses and are not complete animations. Large portraits now have
  temporary generated imports, with final crop/design acceptance deferred.
  Water/action art and other assets remain unfinished and unaccepted.
- [ ] G04: Targeted native/runtime acceptance, final artwork review and
  reproducible delivery without modifying the currently running player build.
  Connected prototype0edf9489 passes seven consumers (6,525 checks), exact
  art-source rebuild, BPS roundtrip and isolated launcher validation.
  ART-PIPELINE.md labels temporary art and unfinished consumers. Full-scope
  acceptance remains open; the historical release has not been replaced.

The running showcase and its saves must remain untouched. Use the existing
release evidence for unchanged behavior. See `notes/native-art-integration.md`
for the investigation and `IMPLEMENTATION-STATE.md` for progress.

Release checkpoint, September17,2026: all approved v0.7 gates are complete
within their documented acceptance scopes. Candidate1b070824 is delivered
through `Play Expansion.cmd`; see `EXPANSION-PLAYER-GUIDE.md` and
`notes/release-delivery.md`. R02 reconciles retained evidence; R03 verifies the
patch and isolated launcher without opening the game. The older narrative
below records implementation history, not additional currently open work.

Initially audited September 15, 2026 Pacific, after source commit `771ee6f`;
updated September 16 through the repeatable encounter-source checkpoint below.
This is the current backlog. `IMPLEMENTATION-STATE.md` retains chronological
evidence; older status/handoff notes describe their historical checkpoints.
Approved scope remains `JOB-CLASS-SPECIFICATION.md` v0.7,
`WEAPON-ACQUISITION.md` and `VANILLA-PLUS-PACKAGE.md`.

## Realistic assessment

Most of the individual combat kits have working implementations. Mystic Knight
now has bounded end-to-end combat evidence: its fourteen commands execute and
persistent Fight damage, recovery, four status riders and ordinary weapon-effect
replacement are implemented. Native damage forecasts are now connected;
Fight resource prediction and native AI resource values now share the execution
formula. Native HP-law domains are verified for resource results. Status AI
value and Spellbreak choice now have native and full-turn evidence. Tactical command/area AI now has bounded native and complete-turn evidence;
campaign penalty playback remains open. Autonomous
self preparation and fuel rejection now have complete-turn evidence. Status-law
prediction uses native prevention on owned copies and considers ordinary damage
variation, preceding misses and secondary-weapon special effects.
Elemental prediction and committed elemental/status Judge transport now have
focused native and actual player-input evidence.
Magic Shell execution and damage previews are implemented with targeted native
evidence; its opportunity now carries across Doublecast and its execution-time
threshold includes eligible damage from the second selected spell. Combined
menu prediction, healing-aware thresholds, buff/reflect controls and five
rendered pair flows now pass. Actual cancellation/re-entry also passes.
Spellweave now commits once at the outer Doublecast boundary. Frozen benefits,
claims, cumulative damage and new queued reactions now span the pair. Twelve
fixed player flows also verify both casts, Spellweave, final Absorb recovery,
renderer preservation and next-turn return. Four additional native caster-KO
flows verify cancellation, partial-action recovery and cleanup. Shared
Doublecast ownership is complete within that contract; combined Shell-menu
prediction and the bounded interaction audit now pass. Final assembled
acceptance remains open.
Spell Parry's
physical interception is implemented, with multi-weapon evidence.

The remaining workload also includes actual player controls/displays, some AI
and law integration, vanilla+ completion content, and release verification.
Those are substantial tasks; a nearly filled ability table does not make the
expansion nearly ready for a campaign. No percentage or time estimate is
justified yet. The greatest engineering uncertainties include remaining effect
field rendering and late Judge reporting.
Primary-hand ownership is verified for Fight execution and the native damage
forecast callers documented in `notes/mystic-knight-fight.md`.

The registry contains 129 lessons: 85 actions, 18 supports, 18 reactions and 8
combos; 85 teaching items; eight job concepts implemented for ten racial jobs,
plus Soldier/Gladiator additions. These are content totals, not completion
counts. No additional jobs, overhaul mods or general vanilla rebalance are
part of this checklist.

Current targeted-tested candidate: `1b070824a8dad4995434eee3ab40fa08187a6120`.
It fixes Viera Mystic Knight's missing saber pose, verified by32,640 scoped
native pose assertions and405 actual cast/cold-save checks. Retained rapier
Osmose plus the two saber cases close the specific enchantment/sequence cold
gap. See `notes/mystic-knight-cold-lifecycle.md`.
The semantic review corrected Healing Mist's explicit base rounding and
Spellblade's rapier/saber weapon predicate in prior candidate a6626e7e.
Prior9fef4cbe also corrects Absorb's percentage-damage trigger, with
245 assertions across80 native executions. Focused native execution/AI,
weapon-family and Parry evidence is in `notes/semantic-contract-review.md`.
Prior candidate `eabce3b98536510e40a8ec5893ecd9bd2996566c` retains unrelated
combat/acquisition evidence; final assembled acceptance remains open.
The A06 martial/AI fixes are documented below. Remaining automatic reactions,
all Bard player commands and Updraft now have targeted playback/cold evidence
in `notes/reaction-song-playback.md`; Updraft and both timed songs also expire
through actual recipient turns. These results do not replace release acceptance.
Native roaming generation/regeneration now closes A02 for all20 learnable
monster actions and all20 capturable species. All five remaining rare theft
items have renewable encounter sources; native colored-clan outcomes restore
another League/Oathbow opportunity. No extra recovery content was needed.
See `notes/repeatable-encounter-access.md` for corrected formation identities
and the controlled-native scope of this evidence.

Previous candidate: `12f790448f2fc95e259b78a403895ce0320468d2`.
It adds medicine AI and shared stack fixes documented in `notes/medicine-ai.md`.
All ten commands have current-ROM actual execution evidence, with 152 checks
aggregating retained positive cases; failed seed sweeps remain failed reports.
Prior candidate `8b31d4918e8bdf2c161e4adbbc102dd6637e3e7d` adds the martial
utility AI fixes documented in `notes/martial-utility-ai.md`.
Prior candidate `37e423e27099f951b00e006c79303735166640b5`
adds Dance Silence admission and no-op AI fixes to the prior Bard candidate
`d559572aa6bb20bb44139644d6c91d0898fe38ac`. Previous candidate
`7908cc6e3ee78206cc0df16bee627e86f88c68d4` changes only help from 55f231;
clean-source assembly reproduced 55f231. Field ownership, native
animation/camera handling, real casts, two-caster overlap and three original
spell/control pairs have bounded evidence below. Native allocation pressure can
reclaim the optional graphics cache while field mechanics remain active. Earlier
cold-save evidence retains its recorded layout scope; final release-layout cold
acceptance remains required. I07 stays open for readability/performance and
final mixed-job acceptance.

Retained recovery candidate: `1dbb18a25a96b0a383b5196506d46f1d141454fd`.
Six I10 services recover Materia Blade, Zeus Mace and Genji Armor after their
original mission opportunity, plus Cinquedea/Madu/Sage Robe after their original
clan gifts were claimed. All require game completion. Native gates/lifecycles,
actual pub payment/stale rejection and20-day reward/cold-save flows pass across
retained9d874955 and current evidence. A fully stocked equipment inventory also
accepts the missing Sage Robe without changing any other count. The
remaining A04/I10 scope is below. All17 Mythril weapons are confirmed eligible
through the original roaming-clan reward selector at every tier.

Previous content candidate: `ea9ed600d38fb8b3a5662fc1f116852be8b97548`.
It adds the 64 A01 recovery routes with bounded predicate/queue/text/acceptance
and native dispatch/retirement evidence, real pub payment/stale rejection, and
34 accepted-dispatch cold-save assertions, 22 actual return/reward/full-bag/save
assertions and 14 post-cooldown pub assertions. A01 campaign audit remains open.
Prior combat candidate: `5a01c78e45a32768a7568617a931c50a7b5300f3`.
I09 is complete within its implementation/classification scope. Native buff
transport, authenticated self-copy forecasts and occupied/empty field reporting
pass4,888 targeted assertions, six actual AI rows and22 racial player flows,
plus direct Bard/Dark Knight/native controls. Campaign penalties remain V06;
persistent outlines remain I07. See `notes/carrier-law-audit.md`.

Earlier Spellbreak candidate: `a2a1958f9a5809a66e682cb38be7890f9010565e`.
Spellbreak now joins the weapon-element carriers:9,116 assertions across72
actual casts and eight AI rows, plus112 assertions/eight player-to-Judge flows.
The following96ff carrier evidence remains applicable; only421 was added.

Earlier theft/element candidate: `96ff816d6bad946c34f9c5e07e109b52ddce5e48`.
Theft-family and14 weapon-elemental carriers now reach native AI and Judge;
Last Resort has corrected primary damage/element and actual self targeting.
Retained/focused evidence includes26 real menu-to-Judge flows and both racial
self modes. Spellbreak421 is completed by the follow-up above.
See `notes/carrier-law-audit.md` for exact hashes, reports and limitations.

Earlier category candidate: `1427bd3de8bf54c7b0803c624bb33c8f1fc60683`.
Recipe Items laws and primary-only weapon classification now pass the all-command
matrix; native medicine HP/MP domains and ten actual Judge casts pass. One
empty-ground selection correctly rejects without payment; see the carrier note.

Earlier elemental candidate: `3255000cfb2293c08a753c259239617c27fbd2d7`.
Fixed Mystic command elements, consumed Release fuel and selected Gaia elements
now reach native law predictions/AI and actual late Judge calls. See
`notes/carrier-law-audit.md`. The rest of I09 remains open.

Earlier status prediction candidate: `9ac4fa5bf776bc13d7e465e1442e3375ae11743a`.
I09 custom harmful-status prediction, actual Cureall prevention/debits and
native AI law flags pass localized checks. See `notes/custom-status-laws.md`.
Carrier restrictions, remaining content and final acceptance are still open.

Earlier geometry candidate: `ecfa1755355cc1e5e512e2ec825dc5be8c0782ea`.
I07 geometry groundwork passes173,314 targeted assertions, including native
quarter-plane comparisons for24,731 tiles across162 maps. The new helpers are
unconnected to live display; field rendering remains open. See
`notes/geomancer-field-presentation.md`.

Earlier Auto-Potion candidate: `eb9e6b15c5915b22aa19787f8a4415ebb922f78d`.
I06's explicit Auto-Potion choice now passes28 real menu/cold-save assertions,
758 bounded native/menu controls and1,027 unequal-stock executor assertions.
Both races can confirm either medicine, cancel safely, retain choices through
saving and character changes, and never substitute unavailable medicine.
Evidence: `notes/chemist-preference.md`. This is targeted acceptance, not a
full-suite pass. Next implementation gap: I07, Geomancer field outlines.

Earlier Magic Shell candidate: `020d043ebca6208365faf874e938d6deca697dd3`.
Retained run `20260916T125758.949041Z` passes 2,975 pair-Shell, 749 menu and
182 whole-playback assertions. Final mixed-spell follow-up
`20260916T130137.691256Z` passes3,929 assertions; cancellation follow-up
`20260916T130022.048247Z` passes46. I02 is complete within its bounded contract:
healing-aware paired thresholds, native area/cost rules, buff/reflect controls,
actual menu cancellation/re-entry, mitigation and rendered next-turn return.
See `notes/mystic-knight-shell.md`. These targeted reports are not a full-suite
pass.

Earlier tactical-AI candidate: `0cd1f531075e2125405c7f41a6356f7217bd4f6d`.
Final localized run `20260916T122406.818596Z` passes1,890 tactical AI assertions.
Retained/follow-up runs add21 complete turns: six Release area cases, two
Break cases, eleven useful strikes and two actual recovery casts. Earlier
self/fuel/Spellbreak evidence remains applicable. I05 is complete within its
stated decision scope; this is a union of declared targeted checks, not a
full-suite pass. See `notes/mystic-knight-ai.md` for exact reports and limits.

Earlier resource candidate: `e4e00a0a04d54a58c80fb73346d7e6ec7f1b6f31`.
Run `20260916T110457.901633Z` passed 12/12 selected steps: 12,652 resource,
7,496 status-law and 15,202 native preview assertions. Resource forecasts/AI
values, native HP-law domains and the 228-input secondary-weapon status matrix
are accepted within `notes/mystic-knight-resources.md`. No full suite rerun.

Earlier status candidate: `b16841d2cad3ed2f75eb88920ec787a25babe5b6`.
Status-law prediction is covered by the retained native matrix and corrected
follow-up: 212 distinct kind/condition/weapon inputs, each with eight execution
seeds, plus pure law queries. Final follow-up passed 2,640 assertions; see
`notes/mystic-knight-fight-prediction.md` for exact failed/passed evidence.

Earlier law-transport candidate: `f224e4f93dfd1bd293b6767ae32609f38122a4ea`.
Fight elemental/status law transport passed 31,597 native assertions, 367
assertions across 32 actual player flows, and 415 allocation/lifetime checks.
No full-suite rerun; exact evidence and remaining scope are documented in
`notes/mystic-knight-fight-laws.md`.

Earlier interface candidate: `0b871a07b572b0e1baac5a7122c3ba9786fec26f`.
Mystic interface I04 is complete within its stated scope: all19 native help
entries, owned enchantment/next-category indicators and26 fixed player flows
across the initial matrix and bounded corrections. Spellbreak rendering now
uses the equipped weapon while retaining its chosen buff. Final correction
checks passed732 playback assertions and3460 native ABI assertions; see
`notes/mystic-knight-interface.md` for exact images, reports and retained
coverage. The full-suite baseline below remains the last broad gate.

Earlier shared Doublecast candidate: `c1fee872002c58941114f2d80aae2073ce910244`.
Shared queue ABI, Mystic continuation and pair-Shell checks passed in
`20260916T091435.519188Z`. The new reaction test passed 1,649 assertions in
`20260916T092033.285820Z` after test-control corrections and strict prerequisite
reuse; the game source/image were unchanged. Coverage includes seven queued
reactions, Auto-Cureall, first-only targets, partial actions and survival gates.
Completed-pair player playback passed 306 assertions in cached run
`20260916T093237.538737Z` after initial 10/10 preparation/playback acceptance.
Interruption-only run `20260916T093642.303229Z` passed 2/2 and 73 assertions:
four natural caster-KO flows, no second cast/cost, pending recovery once,
continuation retirement and next-turn return. No game-source change.
Earlier pair-forecast candidate: `1bf83980ac3d339e82d862c39148c18d29aa9bd7`.
Pair-forecast run `20260916T090133.174042Z` passed 10/10 selected steps with
2,975 assertions. The preceding 12/12 targeted run covered the shared Shell
storage change and Doublecast continuation; the last correction only added
nullified-first-element coverage. See `notes/mystic-knight-doublecast.md`.
Earlier continuation candidate: `8b1ffe992fa9731156ceed1f9de6bc998cdefd42`.
Doublecast/relocation run `20260916T084408.356171Z` passed11/11 selected steps;
Doublecast has1,258 assertions, including exact native completion-hook ABI.
Shell/workspace checks passed on the preceding candidate before that isolated
assembly preservation correction. See `notes/mystic-knight-doublecast.md`.
Earlier Magic Shell candidate: `b8aaa1b7f10d8d53739e365046c52f1bf749b66b`.
Shell/Parry run `20260916T082043.287202Z` passed11/11 selected steps;
Shell lifetime follow-up `20260916T082628.578337Z` passed2/2 using verified
unchanged build/capture prerequisites. See `notes/mystic-knight-shell.md`.
Most recent full-suite baseline: `0be70587c636f5f9fea3896986b8ab632507e431`.
Combined run `20260916T074143.381019Z`: **79/79 passed**, unchanged inputs,
independently rehashed. The new forecast suite checks 15,202 assertions across
4,266 native calls; earlier Fight damage, status and Parry coverage also passes.
These checks accept their declared coverage; they do not close every campaign
or release gate below. The user has now explicitly resumed autonomous
implementation with targeted testing; the overall expansion remains incomplete.

## Working baseline to preserve

Checked entries mean the named bounded work exists with evidence, not that
every related release obligation is closed.

- [x] **D01 — Job/content foundation:** ten added racial job records, approved
  prerequisites/growth/equipment data, 129 lesson records, 85 teaching items,
  expanded AP/inventory/menu storage and shop gate infrastructure. Evidence:
  `notes/all-new-jobs-ui-review.md`, `notes/acquisition-engine.md`,
  `notes/ap-count-publication-review.md` and frozen foundation tests.
- [x] **D02 — Established combat kits:** Samurai, Dark Knight, Viking, Chemist,
  Bard, Dancer and Soldier/Gladiator core effects have native implementations
  and bounded tests. Their remaining interfaces, laws and release coverage
  are listed below; these kits do not need to be reimplemented wholesale.
- [x] **D03 — Geomancer core:** all nine command effects, supports/reactions,
  162-map terrain catalog, native player choice flow, Torrent/Gaia choice AI,
  field persistence and native expiry. Outlines/utility AI remain open.
- [x] **D04 — Mystic command backend:** fourteen native commands, selected
  Spellbreak removal, Release/Break, resource caps, prepared-state lifecycle,
  Arcane Ward and single-transaction Spellweave factors. See
  `notes/mystic-knight-commands.md`; persistent Fight is expressly excluded.
- [x] **D05 — Spell Parry interception:** actual hit consumption, zero-damage
  hit policy, whole native-action physical reduction, multi-weapon/copy/query
  exclusions. Source `771ee6f`; `notes/mystic-knight-parry.md`.
- [x] **D06 — Shared saves and memory:** owned records, migration/copy/retirement
  machinery and lazy battle workspace; fresh new game reaches native name
  entry and Snowball. This closes the prior startup blocker.
- [x] **D07 — Native Combo foundation:** all ten owners, animation return,
  JP/cancel and cold-save checks have earlier main-build evidence in
  `notes/combos-in-game-review.md`. Final composed-candidate regression remains.
- [x] **D08 — Initial vanilla+ work:** two mission refunds, Goblin/Thundrake
  edits, Quin retry/history, sorting, Morpher visual hook and pub ordering
  exist. Monster-source audit maps all 20 learnable actions to repeatable
  source records. These do not establish complete campaign availability.
- [x] **D09 — Primary Fight damage/resource carriers:** native element/neutral
  conversion, Flare effective WDef reduction, capped Drain/Osmose and undead
  reversal; exact equipment-primary ownership through attack-sorted and
  identical dual weapons; Counter exclusion. Evidence and explicit remaining
  gaps: `notes/mystic-knight-fight.md`, combined run `20260916T060545.691544Z`.

- [x] **D10 — Primary Fight status and weapon-effect execution:** positive-HP
  Poison/Sleep/Silence/Slow riders after native wake cleanup; ordinary weapon
  effect replacement, restorative protection, native prevention and Astra,
  Counter exclusion, dual-hand ownership and Auto-Cureall interactions.
  Evidence: `notes/mystic-knight-fight.md`; final candidate and runs above.

- [x] **D11 — Native Fight damage forecasts:** player preview, AI damage
  scoring/detail, reaction eligibility and the native law damage query use
  the authenticated sorted hand. Element/neutral, Flare defense, ordinary drain
  replacement and restorative sign rules agree with independent controls.
  Units, job state and RNG remain unchanged. Evidence: current 79/79 run and
  `notes/mystic-knight-fight.md`. This does not close effect predictions,
  complete rendered UI/AI turns or late Judge reporting.

- [x] **I03 — Shared Doublecast ownership:** full frozen snapshots, both
  extension banks, one-shot claims and cumulative damage span both subcasts.
  New queued reactions resolve once after the pair or completed partial action;
  exact first-only recipient wrappers remain owned. Spellweave commits once,
  and native interruption/payment rules and original eligibility are preserved.
  Constructor/ABI matrices plus twelve completed-pair and four natural-KO
  player flows verify costs, reactions, cleanup, rendering and turn return.
  Evidence: `notes/mystic-knight-doublecast.md`. Combined Shell-menu prediction
  and its bounded interaction audit now pass within I02. Final all-job
  presentation and assembled regression remain V01/R02.

## Confirmed implementation still required

- [x] **I01 — Persistent Fight effect predictions and laws.** D09–D11's
  execution and damage carriers now have resource and status values in both
  native AI consumers. Resource plans share caps/reversal with actual execution.
  Status-law prediction covers prevention, lower ordinary damage bounds,
  preceding misses and sorted secondary drain/removal/healing. Elemental and
  committed primary status effects reach late native Judge queries. Native
  HP-law domains keep actor recovery/target MP separate from recipient HP.
  Evidence: `notes/mystic-knight-fight-laws.md`,
  `notes/mystic-knight-resources.md`, `notes/mystic-knight-ai.md`. This closes
  implementation and bounded native/late-query coverage. Full campaign penalty
  verification remains V06; complete Mystic AI turns remain I05.
- [x] **I02 — Magic Shell completion.** Successful native magical HP hits now
  forecast once without this reaction and grant ordinary Shell before damage
  at the approved threshold. Native previews use an owned copy. Exclusions,
  existing Shell/timers, RNG, legal Viera jobs and later-action reapplication
  have targeted evidence in `notes/mystic-knight-shell.md`. Its opportunity now
  carries across both Doublecast transactions. Execution-time prediction now
  includes eligible second-spell damage using native recipient construction,
  remaining MP and continuation status checks. Combined threshold, mixed
  elements, area edges, excluded recipients and non-damage/cost failures have
  targeted evidence. Combined player-menu numbers and five whole rendered
  pair controls now pass, including actual Shell timer and next-turn return.
  The mixed-heal/buff/reflect audit and actual cancellation/re-entry now pass.
  Native prior healing projects the second decision HP; first-buff controls
  preserve native results/RNG and do not refresh Shell. The bounded reaction
  contract is complete. Final assembled presentation remains V01.
  No private save field was added.
- [x] **I04 — Mystic player interface and feedback.** Real scrolling command
  menu, self/strike selection, exact Spellbreak choice, Release/Break targeting,
  all19 lesson help, enchantment indicators and next eligible Spellweave category
  are implemented with native UI and playback evidence. The discovered
  Spellbreak pose stall is fixed without replacing choice metadata. See
  `notes/mystic-knight-interface.md`; broad all-job release checks remain V01/R02.
- [x] **I05 — Mystic AI integration.** Legal self/strike/buff choices reach
  native decisions, movement, payment, rendering and handoff. Fight status/
  resource value, all21 Spellbreak choices, eleven self enchants, no repeated
  preparation, Release fuel/area ranking and useful Break are implemented.
  All eleven strikes have useful whole turns; Drain/Osmose have real recovery
  turns. Owned native prevention and exact tactical scoring are verified.
  Native willingness/law flags remain intact; critical-health strategy can
  prefer self preparation. This closes the bounded implementation scope,
  with broader all-job/campaign/release checks still below. Evidence:
  `notes/mystic-knight-ai.md`.
- [x] **I06 — Chemist Auto-Potion preference screen.** Both races have explicit
  Potion/Hi-Potion choices in the native reaction list, default Potion, a saved
  choice marker and confirm-only persistence. Cancellation, ordinary reactions,
  character changes, AP/stock preservation and actual cold saves pass. Unequal
  stock cases prove no substitution or cooldown when the chosen item is empty.
  Evidence: `notes/chemist-preference.md`. Existing lesson/save IDs are preserved;
  broader presentation and assembled acceptance remain V01/R02.
- [x] **I07 — Geomancer persistent field outlines.** Live Rime/Refuge terrain
  rings, original animation-source ownership, native camera origins, ROM/heap/
  VRAM ownership and restoration are installed. The unchanged all-map bound is
  669 unique tiles against672 available slots. Metadata18332 and graphics21504 bytes
  are separately owned; native allocation failure reclaims the optional display
  and retries. Initial creation waits for battle setup and does not recur during
  enemy planning. Gameplay fields remain active during cache absence.
  Run20260916T212146.775575Z passes488 native assertions,146 assertions across
  four real occupied/empty casts with VRAM publication/next turns, and634 across
  four native suspend/cold-resume/two-caster-turn expiry paths. Pixel equivalence
  and allocation-bound guards pass in210635; original-animation and all-map
  capacity evidence is retained without an unrelated rerun.
  Source transfer ordering is now corrected:213408/213609 pass160 steps across
  four visible animated maps,320 independent published-plane comparisons,
  final-frame drain and actual no-compose-in-pump checks. Native scroll/wrap/
  two-axis shake and terrain-priority deferral also pass. Display intentionally
  uses the last completed source snapshot; no save/ownership ABI change.
  Native Move/Act/Status coexistence now passes12 display/control comparisons
  across214134's retained six successes and214423's corrected six cases (110
  follow-up assertions). Actual movement endpoints, targeting/cancellation,
  field records, HP/MP and inventory/AP agree; Status text pixels also agree.
  Exact incremental animation refresh now uses cache provenance, shared-pixel
  and opacity guards; full rebuild remains the fallback. Pure atomic/pixel,
  160-step native timing and larger-owner pressure/cold gates pass across
  215205/220137/220450. Cycle run220313 measures79.4–83.2% less CPU work in
  three map cases; map67 falls back correctly. Full rebuilds still cost4.25–5.74
  frame budgets in the isolated mGBA benchmark: performance is not accepted.
  Prepared immutable tile/flip sources and improved hash distribution now pass
  both pure pixel paths, all-map asset validation and native animation checks
  in221340/221513/221844/222505. Current3b034053 metadata18324 passes native
  pressure, four fresh casts and all12 UI/control cases in222612; four cold
  resume/expiry flows pass222741. Assets4439284 bytes use09400000..099FFFFF.
  Full rebuilds now cost4.01–4.86 isolated frame budgets. Measured Move readiness
  adds19–27 emulated frames versus the native-display control (12.1–16.8%).
  This is measured responsiveness evidence, not performance acceptance.
  Candidate55f23176 now composes only the exposed camera fringe.225427 passes
  repeated672-slot reuse, exact pixels and large-move fallback;225033 passes
  native heap/timing and four CPU pairs (56.9–66.8% less camera redraw work).
  225232 passes four actual casts and12 UI/control flows: Move overhead7–25
  frames (4.1–16.4%). Starting states differ from earlier measurements, so this
  is not an exact historical speedup comparison. Release-layout cold acceptance
  remains a final gate; prior evidence is retained in its original scope.
  Original map-backdrop HBlank coexistence now passes:223929 covers all32
  native gradient selectors and both fields (64 cases);223637's retained
  raster consumer compares actual Rime/Refuge sky frames with the native
  display control, including positive gradients and exact DMA descriptors.
  Two-caster overlap now passes135 assertions in230858: ten actual casts from
  independently constructed Nu Mou, same/mixed fields at identical/adjacent
  centers, separate MP payment and exact published union. Native HUD obscures
  part of these retained views; unobstructed readability remains a visual gate.
  Original Fire/Fira/Firaga now pass six display/control flows in231717 with
  equal seeded damage21/29/36, MP6/12/24, preserved fields/AP and valid final
  heap/menu/publication. The cache remains present at eight-frame samples;
  this exercises actual spell effects but does not force allocation failure.
  Current1f197f6c adds a bounded dark shadow/light core.073430 passes240,847
  detached assertions and the162-map669/672 bound;073649 passes488 ownership,
  146 actual cast and220 paired UI checks. Root accepts the measured11–17-frame
  Move overhead within these Windows-emulation cases. Four-map074039 terrain
  review (full run20260917T074039.055238Z) and retained grass show distinguishable
  dashed/continuous shapes. Details and rejected initial halo/offscreen artifact
  are in `notes/geomancer-outline-readability.md`.
  Current-layout074302 also passes four actual suspend/cold/expiry flows634
  checks and160 native animated steps with320 exact published-plane comparisons.
  Final mixed-job acceptance closes I07 on1b070824. Actual Doublecast exposed
  failed cache-construction churn; absent-cache creation now waits for player
  command/facing boundaries before projecting the board.080703 passes554 native
  ownership/pressure checks and146 actual cast checks.080830 passes634 current
  cold/expiry and3612 paired Doublecast/Spellweave/Absorb/summon checks. Current
  paired overhead is16 frames for Doublecast and64 for long summons, with exact
  gameplay agreement and display restoration before the next command. Existing
  all-map pixel/capacity/backdrop/animation evidence is retained in scope.
  Root reviewed restored outlines and native summon/darkening captures; accepts
  bounded Windows-emulation performance. See `notes/geomancer-mixed-pressure.md`.
  Final assembled R02 remains separate; this is not every animation or hardware.
  See `notes/geomancer-field-presentation.md`.
- [x] **I08 — Geomancer utility AI.** Native row and recipient values account
  for existing effects, Float/flight, Surefoot and Light Foot. Native self/area
  placement evaluates deployed recipients, spell threats, friendly damage and
  the cost of replacing the caster's field, preserving other fields. Bounded
  search and real AI turns demonstrate all three utilities, zero choice operands,
  MP payment and actual effects without changing native willingness. Evidence:
  `notes/geomancer-utility-ai.md`. This closes the utility implementation scope;
  I07 display, I09 laws and assembled/campaign acceptance remain separate.
- [x] **I09 — Custom-status law integration.** Successful-effect
  transport to the late Judge for custom buffs/debuffs/fields where applicable,
  and elemental/weapon/item/healing restrictions for the new carriers are
  accepted within the evidence below.
  Miss, prevention, refresh and authenticated copy predictions have bounded
  evidence below. Final campaign penalties remain V06, not this completion.
  **Accepted:** all five custom harmful applications now carry authenticated
  success receipts to the late Judge, including refresh and later cleanup.
  Final4546ccef:1,823 native transport assertions; retained20 real menu casts
  plus targeted final Wound playback. See `notes/custom-status-laws.md`.
  Prediction now passes6,157 assertions, including owned-copy parity, actual
  Auto-Cureall debits and stronger-Wisp boundaries. Another2,190 assertions
  verify90 native AI law rows on9ac4fa5b. Player confirmation has no native
  predictive-law consumer; no new warning screen is implied.
  Later carrier and buff/field acceptance below completes the remaining I09 scope.
  **Elemental carriers accepted:** Mystic410..420, consumed Release422 fuel
  and selected Gaia381 elements now pass27,578 native assertions and144
  assertions across12 real menu-to-Judge casts on3255000c. Other restrictions
  remain open; see `notes/carrier-law-audit.md`.
  **Item/weapon categories accepted within bounds:**1427bd3d passes45,560
  assertions,56 actual two-race recipe casts and ten real menu/Judge flows.
  Explicit primary-only delivery covers all85 commands; MP and zero recovery
  keep native HP-law semantics. Retained failed playback and corrected
  empty-selection follow-up are documented in the carrier note.
  **Theft/weapon elements accepted within bounds:**96ff816d, with retained
  f545cb2e consumer evidence, covers Steal/Reaving identity,14 primary-element
  arts, real AI rows, independent theft and corrected Last Resort damage/self
  targeting.26 real menu-to-Judge flows pass across retained/focused runs.
  **Spellbreak follow-up accepted:**a2a1958f adds primary-element transport,
  selected-buff/enchantment isolation, immunity and late identity with72 native
  casts, eight native AI rows and eight real player/Judge casts.
  **Buff/field completion:**5a01c78e passes60 actual composite buff casts,
  96 copy-ownership inputs, six native AI rows and22 real buff/field menu flows.
  Dark Mind/Hide forecasts now recognize authenticated self copies. Empty
  fields preserve native no-recipient Judge behavior and still place/pay once.
  Kind3 bits are clear in all347 original and85 new actions; no invented
  mapping was added. Final assembled/campaign card acceptance remains open.
- [x] **I10 — Late-game vanilla teaching-equipment recovery.** Implement
  appropriate recovery missions/routes after the completeness audit below.
  Retain original sources and avoid requiring unique-character dismissal.
  Materia Blade, Zeus Mace and Genji Armor now have services471–473, requiring
  cleared-game flag54, completed original source22/16/101 and a missing copy.
  Services474–476 add Cinquedea/Madu/Sage Robe after claimed original clan gifts
  23/15/8, preserving the native Negotiate30/40 and Magic45 gates.
  Native20-day dispatch/base10000gil/30-day cooldown; no new save flags.
  Current native gear coverage is834 checks; retained/new playback covers all
  six services (150 pub/payment/stale checks and204 real travel/reward/cold-save
  checks). Pub and return use separate fixtures. The full-stock Sage Robe case
  confirms every other equipment count and original gift receipt survives.
  Five other rare items have native theft witnesses (137 checks/15 loadouts);
  Their native repeatable encounter access now passes: four roaming sources
  and Brown Rabbits109 for Oathbow, including the next colored-clan cycle
  after success or a missed Brown Rabbits mission. See the repeatable-access note.
  A continuous Materia Blade cycle now passes actual first payment/20-day
  return, shop sale,30-day cooldown, second payment/20-day return and cold
  Save/Continue, with121 recorded checks across authenticated checkpoints.
  Final inventory has one blade and20500gil after two15000gil fees and a500gil
  sale. See `notes/paid-recovery-cycle.md`. Final campaign/release acceptance
  remains V02/V05/V06; quest-item repeat payment remains A01.

## Audits that may reveal additional implementation

These are open obligations, not assertions that every audited feature is broken.

- [x] **A01 — Mission-item dependency ledger.** Reconcile all consuming/later
  required items and repeatable routes. Static ledger now covers406 missions,
  88 required items and119 consumed slots:24 independent repeatable candidates,
  64 finite/self-dependent candidates. See `notes/mission-item-dependencies.md`;
  native pre-construction pub predicates/duration pass6,943 fixed cases. The
  audit now covers all512 table slots/400 posting-enabled records; earlier406
  coverage and calendar metadata were incomplete. The 64-route recovery implementation now passes 5,542 entitlement, native
  posting/text, capacity, acceptance and completion cases; 326 native lifecycle
  cases cover full construction/list/assignment, five-day returns, cancellation,
  success/failure retirement and consumed/retained controls. Another 6,111
  original pub controls pass. No new flags or saved counters; full caches never
  evict original offers for recovery. Actual pub payment and stale rejection
  pass; 34 cold-save assertions cover three accepted routes. Another 22 checks
  cover actual five-day return, collection/full-bag rejection and cold saves;
  14 checks prove repeat pub availability after rejection versus held-copy
  suppression. A continuous current-build player-input case now passes57
  checks: two actual300-gil payments, both five-day dispatches, first full-bag
  rejection, native cooldown, second chosen-slot replacement and exact cold
  save. No source/consumer flags or existing items are lost. See
  `notes/vanillaplus-final-paths.md`. Connected native progression now passes
  1,344 checks from authenticated opening history:34 story/battle receipts,
  all85 teachers at their earned stages,149 additional original source/side
  completions,13 earned rumor acknowledgments and all24 renewable witnesses
  with native ingredient binding/consumption. No later flags or ingredients
  are inserted. See `notes/campaign-progression.md`. The remaining scene and
  territory connections now pass45 checks in `20260917T122656.766531Z`: native
  Desert Patrol/Over The Hill results, Della Dunes placement, fixed Ambervale
  creation, real pre-final save and earned Royal Valley departure/deployment.
  See `notes/campaign-territory-scenes.md` for declared milestone inputs and
  reuse of the early/ending suffixes. This is representative connection
  coverage, not an uninterrupted full-combat campaign playthrough.
  Native source gates/reposting and offline naming variants now have
  bounded evidence in `notes/original-source-gates.md`. The new fixed-point source audit closes ingredient
  cycles for all24:20 ingredient-free and4 acyclic recipes. Another130 native
  checks trace all14 prerequisite rumor topics and prove1323 survives rumor43
  retirement after Spiritstone completion. Native name confirmation now proves
  flags1445/1446 are not exclusively link-owned: all four ordinary RNG outcomes
  produce the appropriate original optional-mission variants. Original gates
  and never-earned recovery restrictions remain intact.
  Retain the two verified refunds;
  implement only actual remaining lockouts. Original Caravan Guard now passes
  35 checks covering its actual20-day travel/return and normal/full-bag refund,
  using a native-assigned, explicitly bound prerequisite fixture.
- [x] **A02 — Monster-ability availability through progression.** Reuse
  `scripts/audit-monster-ability-sources.mjs` and native learning evidence;
  establish dynamic event branches and post-opportunity repeatability for
  all 20 actions. Native generation/visibility/map selection passes649 checks
  in60 placement cases; expiry and battle-return retirement/regeneration pass
  795 checks in60 cases. All20 actions and20 capturable species have renewable
  roaming sources after the original progression gate. No encounter changes
  needed. Controlled native consumers establish availability; campaign playback
  remains V06. See `notes/repeatable-encounter-access.md`.
- [x] **A03 — Secret recruits.** Check every applicable missed/failed offer
  against original eligibility and uniqueness/death/history policy. Reuse
  Quin's existing native/save evidence; do not assume Quin alone proves all
  secret-recruit retry requirements or add duplicates.
  Native audit now covers all11 recruits:90 candidate assertions across16
  routes,110 posting/expiry/cooldown/completion assertions, and38 actual native
  acceptance-copy/receipt assertions. All four existing special retry dispatches
  unlock from original native completion. Flags600..604 are acceptance receipts
  and block reoffers with a retained acceptance receipt after absence. Native
  Shara381 dispatch success/failure, cooldown and automatic400 pass66 retained
  checks;22 continuation checks connect town selection, original scene129
  gate-clear/recruit opcodes and first/unaccepted-repeat candidate generation.
  Complete cutscene controls/full-roster/cold acceptance remain V02/V05/V06.
  The next Clan League qualification cycle now passes
  native posting/acceptance/completion/cooldown checks, including a missed
  colored-clan mission. See `notes/secret-recruit-access.md`.
- [x] **A04 — Rare teaching-equipment ledger.** Enumerate remaining vanilla
  missable teaching equipment, original source, eligibility and recovery
  route, then reconcile I10 with the final list.
  Static ledger now covers all375 original equipment records,216 teaching
  items/457 racial lessons, shop stock, mission pools,63 clan gifts,442 full
  formations and Throw/Hurl pools. All original equipment records are preserved.
  Native clan-gift gates/one-time receipts pass424 assertions in149 scenarios.
  Source classification:109 shop entries,70 repeatable random-mission candidates,
  17 combo weapons,9 Souls and11 rare source reviews. Actual native roaming-clan
  reward code now proves all17 combo weapons eligible at every tier, with1383
  seeded selector assertions. Six of the11 rare items now have installed
  recovery routes. Native theft passes137 checks for the remaining five across
  15 repeatable-source loadouts, preserving real mastery/reactions/supports:
  14 successful native awards and one Maintenance rejection. Each item has an
  unprotected witness; native roaming and colored-clan cycles now establish
  repeatable access for all five. Corrected native formation indexing places
  Oathbow in Brown Rabbits109/273, not Blue Geniuses108. Historical template
  theft results remain applicable; their shifted formation labels are superseded.
  Another446 native checks
  cover all20 capturable species/all9 Souls: first award, disposal, alternate
  species, full bank, native release and same-species recapture. No one-time
  Soul grant gate was found. A02 now establishes renewable roaming access
  for all20; actual Capture/menu/
  save playback is separate from this bounded source-consumer evidence.
  All109 original shop teachers are present through the installed shop builder
  at declared late progression/territory inputs. Seven ingredient-free renewable
  missions cover all70 random-pool teachers; native construction/reposting and
  every original reward slot pass. See `notes/original-source-gates.md` and
  `notes/vanilla-teaching-equipment.md`. Campaign progression, actual collection
  and final save acceptance remain V02/V05/V06 and I10. No additional recovery
  is needed for these sources, the five rare theft items or nine Souls.
  Source-audit reconciliation is complete: the bounded source proofs above
  cover all216 teachers and the six installed recoveries. Campaign/collection
  acceptance remains in its explicit V05/V06/I10 gates, not an unenumerated
  source-ledger gap. This closure reuses recorded evidence; no runtime rerun.
- [x] **A05 — Lesson/design reconciliation.** Compare every one of 129 lessons
  with installed cost, power, AP, flags, race, weapon, reaction/support mixing,
  growth/progression and help. Identify any other placeholder, inherited donor
  behavior or missing visible effect. Allocated IDs and donor graphics alone
  cannot close an entry. Keep approved donor art; new art is not a requirement.
  Current-ROM data reconciliation passes2,131 checks for all129 lessons/158
  racial records,85 teaching items and10 job profiles. Filled15 missing lesson
  descriptions and corrected two mace combo descriptions. Another846 native
  help checks prove every lesson has readable, bounded text and shared-race
  consistency. Full byte comparison proves this patch changes only help data.
  Remaining scope is semantic effect/flag/formula/mixing reconciliation and
  applicable presentation evidence; see `notes/installed-design-review.md`.
  Root source review and1,703 accepted focused assertions corrected Healing
  Mist base rounding and Spellblade's shared weapon family. See
  `notes/semantic-contract-review.md`. Absorb's overly narrow category gate is
  now removed:245 native assertions include normal/percentage damage, a lethal
  fixed-damage control, allies, KO and reaction-blocking status. Presentation
  and remaining lifetime reconciliation were still pending at that checkpoint. The newly
  exposed Mystic saber animation stall is corrected in687ed5d4, with scoped
  native pose and actual cast/cold-save evidence.
  Final reconciliation now closes A05: root source review plus V01–V05,
  current2131 installed-data checks and550 exact-help reuse checks (074520),
  and current field animation/cold consumers (074302). No lesson blocker remains
  identified. See the final table in `notes/semantic-contract-review.md`.
  Campaign A01/V06, remaining field-display I07 and final release R02/R03 stay
  separate; historical runtime evidence keeps its original candidate/scope.
  The A06 sweep also corrected Ether's inherited no-AI byte for Ballad and
  Witch Hunt; native admission now respects their command costs. Actual
  Chemist item rules remain separate and are not blanket-rewritten.
  The next sweep reconciles native Silence field 20 across all 85 actions and
  fixes its reversed allowance for all nine dances. Native primary/secondary
  menus and three actual Silenced casts now prove the admission path that
  earlier direct-executor tests omitted. See `notes/dancer-ordinary-ai.md`.
- [x] **A06 — Ordinary AI decision audit.** Audit legal use of songs,
  custom utility/status effects and shared supports outside the already proven
  scenarios. Fix unusable decisions or missing required handling; do not add
  an unapproved strategic-AI overhaul. Sophisticated Provoke tactics were not
  promised by the design.
  Bard useful-component scoring now passes 2,160 native recipient assertions
  and 293 placement/admission checks, including Recuperation and Magick Boost.
  Redundant songs are rejected; native Requiem forecasts and consideration
  chances are preserved. Three autonomous Ballad casts and one Chant cast
  verify actual benefits, spending, rendering and handoff; failed positive
  Chant cases were resolved with a declared reachable support scenario.
  Further command groups and the support-boundary review are recorded below.
  Reproduction, exact reports and limitations: `notes/bard-ai.md`.
  Ordinary Dance now rejects Witch Hunt at zero target MP and Slow Dance at
  existing Slow, retaining native values otherwise. The grouped sweep passes
  1,033 row/admission/menu/flag checks and 72 placement checks. Three Silenced
  player casts add 137 assertions. These close the stated Dance defects;
  Samurai/Dark Arts/Reaving/medicine and shared supports are covered below.
  The six-command martial utility group now passes 2,470 recipient checks,
  411 native placement checks and 2,076 filter/ABI checks. Actual Last Resort,
  TBN, Silenced War Cry and Kiyomori AI casts pass on the current candidate;
  the successful Dark Mind case is retained separately. Fixes cover empty
  benefits, restorative support factors, Last Resort's false enemy-buff value,
  War Cry self admission and custom wards' native filter categories/policy.
  Original movement/search and Kiyomori's native status heuristics remain.
  Medicine now has stock/ownership admission, useful-component scoring,
  recipe transport and Long Throw destination handling. The grouped native
  audit passes 2,406 checks and 629 placement checks. All ten commands have
  actual autonomous cast evidence with exact payments/effects and renderer
  integrity; 152 aggregation checks verify the retained current-ROM artifacts.
  Targeted Fight, preview, barrier and storage regressions pass after fixing
  a real interrupt-time stack spill. See `notes/medicine-ai.md` for exact
  reports and the distinction between individual positives and failed sweeps.
  The 30-command ordinary martial attack/status sweep now passes 13,256
  checks across 1,316 cases, including both Dark Knight races and legal shared
  support ownership. Last Resort's hostile score rejects unarmed/Healer strikes
  while keeping self preparation. Provoke rejects a duplicate challenge from
  the same caster and now passes native filtering after actual compatibility;
  the original switch otherwise rejected its custom effect94. Another 3,986
  filter checks and 285 checks across 42 placement scenarios pass. See
  `notes/martial-attack-ai.md` for exact hashes, retained neighboring-consumer
  evidence and the distinction between forecasts, native filtering and casts.
  The prospective-movement question is now resolved: native command scoring
  uses the current position before its ordinary placement policy chooses a
  destination. An optimal movement/damage planner is outside the approved
  vanilla+ scope. The real move/undo boundaries and public previews pass 174
  checks across six planning and thirty completed-movement cases, preserving
  actual Composure/Follow Through conditions. See `notes/ai-movement-policy.md`
  for the native trace, requirement review and precise limits. Final mixed-job
  AI acceptance remains part of R02.
  This does not establish an autonomous Provoke cast or final assembled
  acceptance. See `notes/martial-utility-ai.md` for the utility group's scopes.

## Verification gaps for implemented behavior

- [x] **V01 — Native playback gaps.** Gil Snapper, Dark Ward and both racial
  Chemist automatic reactions now pass paired actual playback and six cold
  saves (1,073 checks). All eight Bard commands plus silenced Hide have native
  preview/cancel/commit/render/Wait cases; three song cold saves and two timed
  song expiry flows also pass. Exact report chain and limitations are in
  `notes/reaction-song-playback.md`. Informative text/presentation review
  and remaining Mystic controls/reactions are reconciled with later evidence.
  This final review is now complete: all129 decoded descriptions were reviewed
  and550 read-only checks establish exact current-byte/racial-route reuse.
  Actual Spell Parry adds eight paired saber/rapier hit/miss flows and two cold
  resumes (221 assertions), with root-reviewed prediction/reaction labels.
  Magic Shell, cancellation and later Mystic pose/lifecycle reports were
  reconciled. See `notes/final-presentation-review.md`; I07/R02 remain separate.
  Existing Counter Draw/Absorb/Vengeful/Bard/Dancer/Geomancer playback is reusable
  within its recorded scope. Check informative text as well as turn return.
- [x] **V02 — Remaining persistence/lifetimes.** Updraft's dedicated actual
  cast/cold-save/two-recipient-turn case now passes, including native Move+1,
  conditional Jump+1, no immediate displacement and both bonuses' expiry.
  Mystic enchantment/sequence now has three actual cast/cold-resume cases:
  Fire self-preparation, Osmose and Spellbreak, using rapier and both original
  and added sabers. Both sequence categories and exact item bindings persist.
  See `notes/mystic-knight-cold-lifecycle.md`; retain existing native lifecycle
  controls. Full24-slot native replacement/removal now passes96 cases/7,296
  checks; both normal save slots preserve independent full-clan/AP/preferences
  profiles through file1/file2/file1 cold loads, with transient job banks reset.
  See `notes/roster-save-slot-lifecycles.md` for retained phase evidence.
  Another51 player-flow checks prove an actually dispatched member's sorting,
  return and cold save, with Marche/Montblanc fixed. A73-check retained phase
  chain proves ordinary full-clan recruitment refusal and actual offer/accept/
  cold load with a vacancy. Native ordinary recruitment skips offers at capacity;
  it has no replacement menu to implement. The whole native replacement commit
  retains its separate96-case proof. Sorted deployment subsequently passes27
  checks in V05; complete special recruitment scene acceptance remains V06. Reuse accepted
  field expiry, allocation/free, migration and copy tests instead of rebuilding
  those fixtures for each lesson.
- [x] **V03 — Teaching/AP/acquisition on the final candidate.** All 85 items and
  129 lessons must have reachable intended stage/town access, accurate prices,
  legal equipment, correct display/learning/mastery and saves. Reuse existing
  85-item native price/purchase and stock matrices; fill actual unlock/menu gaps.
  Candidate687ed5d4 now passes6,639 learning assertions for all158 racial
  associations/both stack residues, all ten actual job-menu/cold-save/secondary
  command flows,2,160 native stock combinations,1,275 prices and170 purchase
  commits. The installed0.7 audit passes2,131 checks. Actual opening purchase,
  equipment lesson, mastery-removal and cold save also pass. See
  `notes/final-learning-acquisition.md`. Controlled completion flags establish
  intended availability; campaign earning/visits remain V06, final assembly R02.
- [x] **V04 — Final Combo and synergy regression.** Rerun relevant baseline
  Combo/JP/animation checks on the composed candidate, plus targeted remaining
  whole-action, refund, status, damage/MP, undead and legal cross-class cases.
  Do not reopen already closed mechanics merely because old notes say pending.
  Candidate687ed5d4 passes432 actual Combo assertions across all ten owners,
  participation/donor controls and cold saves; all39 weapon-family playback
  cases return correctly. A retained six-case Bard-knife continuation supplies
  the missing positive hit (45 total cases/180 checks). Six focused native
  suites pass12,661 assertions covering combined factors, refunds, undead,
  Doublecast/reaction ownership and movement-support Combo exclusions. See
  `notes/final-combo-synergy.md` for failed-run provenance, limits and exact
  reproduction. The game image is unchanged; final R02 remains open.
- [x] **V05 — Vanilla+ gameplay preservation.** Sorting with dispatch/story/
  deployment identities; Morpher movement/attack/casting/damage/exit visuals;
  remaining pub options; actual recovery claim/repeat/full-inventory/save flows.
  Dispatch/story sorting is accepted through actual payment, manual party
  sort, native return and cold save (51 checks). Another27 current-build
  checks prove sorted deployment and exact identities/AP/equipment/preferences
  through native battle construction. All four pub options have18 native/menu
  access/cancellation checks and root-reviewed captures. Continuous quest-item
  repeat/full-bag/cold recovery adds57 checks. See
  `notes/vanillaplus-final-paths.md` and `notes/roster-save-slot-lifecycles.md`.
  Morpher now passes all nine native transforms/48 selectors each, all nine
  movement/damage/monster-ability lifecycles, eight Unmorphs, actual Blowup KO,
  ten exit cases and KO/territory-placement/normal-save/cold continuation.
  Root reviewed all form captures and cold restoration. See
  `notes/morpher-native-preservation.md` for fixed scenarios and limitations.
  Complete special story scenes and campaign milestones stay V06.
- [x] **V06 — Campaign milestones and laws.** Deterministic scripted early,
  middle, late and postgame checks for unlocks, encounter/recruit access,
  original campaign constraints, new content and Judge outcomes. A fresh
  opening and representative native campaign connections are proven. No
  uninterrupted full-combat or agent-driven playthrough is claimed.
  Connected native receipt/rumor/ingredient progression and all four teaching
  stages now pass1,344 checks on1b070824; see `notes/campaign-progression.md`.
  Native clear-save writing/dialog dismissal and unmodified cold Continue now
  pass 12 checks, preserving the full expansion profile and cleared flag 54;
  see `notes/clear-save-lifecycle.md`. A 46-check retained suffix now verifies
  native reset to title, same-core Continue and two original postgame pub
  listings from the saved clear flag. All six rare-gear services retain their
  original-entitlement gate. Native state0x106 resets rather than returning to
  a parent; see `notes/ending-continuation.md`. A14-check native ending-scene
  chain now executes101/102/104/105,19 credit instructions and its actual
  ending-save opcode through reset/Continue/cold load; see
  `notes/campaign-ending-scenes.md`. The initial scene is a declared one-time
  queue substitution. A19-check retained Royal Valley bridge now verifies
  native deployment and three battle exits through93/95/96/97/98/100 into101,
  preserving all non-hostile actors; see `notes/final-battle-scene-bridge.md`.
  Initial event dispatch and hostile defeat are declared inputs in that older
  suffix. The incoming earned path is now independently verified by45 checks
  in `20260917T122656.766531Z`, including actual19/25 map entry and result scenes,
  Della Dunes placement, fixed Ambervale creation, the real save, and original
  post-save departure selection of26/scene93. An8-check original/candidate
  comparison verifies its positive and three negative native condition gates.
  See `notes/campaign-territory-scenes.md`; existing early Lutia placement and
  ending/credits/postgame evidence are reused rather than replayed.
  Shara's actual town-selected scene129, full-clan decline/Yes refusal, vacant
  slot23 acceptance and unmodified cold-save lifecycle now pass20 retained/new
  lifecycle checks plus7 capacity checks; see `notes/shara-scene-lifecycle.md`.
  Late stage/dispatch completion are declared inputs. Distinct story playback
  for every other special recruit is not claimed; the accepted native
  acceptance/uniqueness, law and repeatable-encounter evidence remains in scope.
  Representative milestone acceptance is complete; release-wide evidence
  reconciliation and final implementation review remain R02.

## Delivery gates

- [x] **R01 — Clean-source build chain.** `Build Expansion.ps1 -CompareCurrent`
  reconstructs all eight stages in a fresh private workspace from the clean
  USA ROM, pinned local tools and versioned source, including the explicitly
  reconstructed historical bootstrap source. No generated binary, fixture,
  save or manifest is an input. Run233352.061042Z produces a32MiB image exactly
  equal to55f231768cfffdbfc2383191f8648716d452375d; all four old bootstrap hooks
  are replaced in the final image. Source/tool inventories, logs and output
  hashes are preserved; the existing candidate is untouched. See
  `REPRODUCIBLE-BUILD.md`. R02 must select the final release candidate and R03
  must package it; build equivalence alone does not close gameplay coverage.
- [x] **R02 — Final assembled acceptance and root review.** Reconcile foundation
  and integrated suites against the release candidate; resolve actual failures;
  freeze source/ROM/report hashes and review all open checklist entries. A
  partial suite or passing scaffold never substitutes for required coverage.
  After Python/runtime and requested runner-cleanup drift, six assembly steps
  in `20260917T093710.889444Z` reproduce the current candidate byte-for-byte.
  The subsequent isolated eight-stage clean-source rebuild also passes:
  run `20260917T094234.326368Z`, source checkpoint `a5ac1e5`, byte equality with
  `1b070824a8dad4995434eee3ab40fa08187a6120`. Source/tool/log/output hashes are in
  `REPRODUCIBLE-BUILD.md`. Final root review and evidence reconciliation now pass
  in20260917T124951.415017Z:218 shipping files unchanged from the clean build,
  52 evidence notes and28 exact reports/logs frozen. Only the two field-display
  sources changed since the accepted broad job/Combo checkpoint, with later
  current-candidate consumer coverage. See `notes/release-acceptance.md`.
  Representative milestones/ending/postgame are accepted above; no full-suite
  rerun or uninterrupted full-combat playthrough is claimed.
- [x] **R03 — Separate playable delivery.** Produce and verify the final patch,
  build manifest and player guide, update the separate expansion launcher/save
  path, and clearly distinguish it from the older foundation launcher. Keep
  vanilla and player saves intact; ROMs/tools/builds stay outside Git. No remote
  publication or unsolicited game launch is part of this step.
  Approved resource guards/retention are reviewed and pass18 bounded tooling
  checks in20260917T124457.556144Z; see `notes/resource-tooling-review.md`.
  Delivery run20260917T125641.116392Z passes patch roundtrip, wrong-source
  rejection, deterministic patch output and actual launcher validation mode
  with a wrong-ROM negative. The guide/manifest and independent expansion ROM
  are produced. Nine game/save/launcher files remain unchanged in verification.
  Exact hashes and retained failures are in `notes/release-delivery.md`.
  A later user-requested sandbox is separately documented in
  `EXPANSION-SHOWCASE.md`: native seeded save/cold verification passes240 checks;
  its independent desktop launch was requested and observed. It does not change
  the release image or claim naturally earned progression.

## Execution and maintenance

Suggested order: I01–I03 as a combat batch; I04–I09 as coherent interface/AI/law
batches; A01–A06 with I10 as completeness work; then close V01–V06 and R01–R03.
Implement very substantial sweeps or use targeted checks of changed behavior
and direct consumers. Select exact test IDs with `-Only`; localized tests are
normal verification, not restricted to blockers. Full integration is reserved
for major completed milestones, final acceptance or a documented widespread
regression. A checklist update or commit does not trigger it. Follow the impact
selection and evidence-reuse procedure in `PARALLEL-IMPLEMENTATION.md`.

Keep these IDs stable. Update this file in the same source/documentation
checkpoint as each accepted batch. Check a box only when its stated behavior
and appropriate deterministic verification are complete; add the commit and
report/hash evidence beside it or in a linked note. If only part is done,
leave it open and narrow its remaining text. Add newly discovered gaps here
with their evidence and dependency, rather than leaving them only in chat.

Keep test chronology in `IMPLEMENTATION-STATE.md`, reproducible procedures in
`PARALLEL-IMPLEMENTATION.md`, and stable project rules in `AGENTS.md`.
Do not put this checklist or progress updates in `AGENTS.md`.

The September 15 audit used the current registry/build manifest, current engine
sources and 76-step plan, latest root checkpoints, approved scope documents,
Chemist handoff/consumers, native Combo/acquisition/refund/Quin evidence and
current reaction-playback scenario list. It was a root source/evidence review;
it did not rerun the campaign or certify every unchecked gate.
