# Geomancer utility AI

## Recipient evaluation

`geomancer-utility-ai.c` supplies the shared native candidate-row and detailed
recipient-score consumers. It occupies the existing Geomancer code reservation;
it adds no saved state, action IDs, field records or choice operands.

Native values are signed from the recipient's perspective. Updraft is a modest
benefit (-16), with four additional points for its actual lower-target Jump
bonus. Existing Updraft is a no-op for AI planning. Grounded recipients already
protected by Refuge are also excluded: granting Float would remove their
shelter. Innate Float/flight and transferable Light Foot/Surefoot still benefit
from Move+1. Players retain normal refresh/override eligibility.

Refuge is valued at -20 for a grounded ally without friendly Refuge already
covering that tile. Hostile fields do not supply allied protection. Updraft,
Float and flight prevent claiming a shelter benefit.

Rime keeps its native signed HP forecast and adds six points of movement
hindrance when the target is grounded, lacks Surefoot and is not already on
Rime. That penalty applies to allies too; it must not become a friendly bonus.
Float/flight/Surefoot suppress only the terrain term, preserving Ice damage.
These are planning weights, not changes to ability potency.

Alive/KO/Petrify and native target eligibility remain authoritative. Benefit
rows use native beneficial-status category82 only for AI classification;
execution retains each actual action/application. Row count, probability and
law flags remain native. Inert rows are cleared after their action identity.
The detailed score uses the same signed utility. Queries preserve units, job
records, RNG and the authenticated choice scope.

## Evidence and limits

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only
test-geomancer-utility-ai,test-geomancer-ai`. For unchanged production inputs,
`test-geomancer-utility-ai-cached` verifies retained prerequisites first.

Run `20260916T140421.622651Z`: 11/11 selected steps passed, including required
build/native-capture preparation. Production ROM
`1c9388c4332e7ddb04635a6fef211e2b9792d089`. The recipient matrix passes1,392
assertions across96 utility scenarios and12 ordinary-action controls. It covers
both stack alignments, both native query entry points, charm/factions, existing
fields, transferred supports, lower recipients, KO/Petrify, sleeping casters,
probability/law preservation and read-only/output bounds. Existing Torrent/Gaia
search and choice transport pass196 assertions. No full suite was run.

The earlier observational audit135644 inherited an allied target for its
Updraft enemy label; that row is not enemy-admission evidence. The new matrix
declares factions explicitly, and the audit script has been corrected.

That recipient checkpoint alone did not close I08. The placement/turn work
below supersedes its remaining utility-search work; field display, custom laws
and final assembled/campaign acceptance remain separate checklist obligations.

## Native placement and storage

`geomancer-utility-search.c` handles the actual native non-self and self search
callbacks. It uses the native admission row, usable-action gate, movement map,
range/height/area geometry and publication coordinates. Each callback examines
one reachable origin. Utilities publish extra0; they are never Item choices.
The caster's proposed location is carried by the existing authenticated scope,
and live units are not moved during planning.

Deployed recipients come from both native candidate groups, with the caster
included. Updraft retains its recipient policy and requires a deployed opponent.
Refuge additionally requires a real learned/equipped, affordable offensive magic
forecast from an opposing deployed unit. Move+range+2 is a conservative threat
bound, not proof of a legal enemy path or a prediction of its next action.

For fields, compare before/after coverage for each recipient, retaining all
other casters' fields. Replacing one's Refuge can lose protection outside the
new cross; replacing Rime can remove friendly hindrance. Float/flight and
Surefoot suppress the applicable terrain term. Rime's native expected HP damage
remains separate, including friendly damage and absorption. Penalize friendly
harm and hostile benefit twice; credit useful relief at its base value.
Ties retain the shortest caster movement. No-op refreshes score zero, while
moving ice away from an ally without losing enemy coverage can be useful.

The constructor atC01D0 allocates1024 bytes for node+204. Scratch uses the first
512 bytes; native center and cross records occupy512..767, peer pointers768..911
and the native40-action discovery list912..991. No new heap/save allocation.
The existing multi-choice search is dispatched separately before its larger
local matrix is allocated. Forecasts reuse the authenticated heap-backed
effect-query bank, including the existing Shell policy. This avoids lending
large nested snapshots to the native IWRAM stack.

## Placement and whole-turn evidence

Production candidate `61c0dda425260c1858c297e3a851d21c19036df2`:

- `20260916T142252.681505Z`: placement passes410 assertions across70 fixed
  scenarios and both stack alignments. Includes self/moved-self, MP, sleep,
  blocked paths, learned/unlearned spell threats, Float, Surefoot, Light Foot,
  existing shelter, harmful area casts, useful ice relocation, redundant fields,
  exact1024-byte guards and read-only unit/job/RNG/executable bytes.
- `20260916T142015.474020Z`: the changed Geomancer dispatch passes196 existing
  Torrent/Gaia search assertions. Earlier141417 also passes2,056 Mystic command
  assertions for the shared self-search dispatch and1,392 recipient assertions.
  Its later utility-only stack correction does not change those recipient or
  Mystic branches; no unrelated reruns were made.
- Whole-turn run142252 completes11 actual AI turns. Rime casts, pays12MP and
  creates its owned field in all three combat seeds. Unlearned Updraft and
  unaffordable Refuge controls select no forbidden action. The report correctly
  fails positive benefit coverage because its attack-focused scenario chooses
  Fight instead of Updraft/Refuge; these completed cases remain recorded.
- `20260916T143151.828652Z`: six explicit support-opportunity turns pass77
  assertions. Planner seed0 casts Updraft and Refuge with native movement,
  zero extra, one8/12MP payment, actual recipient/field state, rendered frames
  and handoff. Seeds3/18 retain native move/wait decisions. Native willingness
  is unchanged; utilities are not forced on every turn. Together with the
  retained Rime/admission cases this accepts all three utility flows.

The first compiler run141328 failed a strict indentation warning, corrected
before runtime. Runs141417/141530/141657 exposed the nested stack overwrite;
dispatch and heap-backed snapshots fixed it. Run141825 completed execution but
its refresh assertion wrongly rejected useful ice relocation;142015 corrected
that scenario and exposed an overcounted expected relief weight. The final
matrix requires the actual600-point base relief and a separate true no-op.

The first replay142433 reset planning onto the prior unit's stale movement
allocation and is invalid as gameplay evidence. Correct replay142610 matches
the actual Fight decision. Later diagnostics also corrected embedded planner
offsets: its target groups/lists begin18 bytes into the outer AI object.
Support run142849 repeated one planner input because the old logger seeds only
combat execution. The accepted support test explicitly seeds planning before
native setup as well as combat. No production weight was changed to fit those
test assumptions.

Use the declared `test-geomancer-utility-search`, `test-geomancer-utility-ai`
and `test-geomancer-utility-turns` steps with build prerequisites for new source.
Their cached variants verify retained inputs first. Use
`test-geomancer-utility-benefit-turns-cached` to isolate benefit playback after
a Rime/admission prefix already passed. The trace step is a retained-scenario
diagnostic only. All runs keep full logs, fixed inputs, hashes and outcomes.
No full integration suite or unrelated save/campaign replay ran for this work.
