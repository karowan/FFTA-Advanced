# Bard native AI decisions

Candidate: `d559572aa6bb20bb44139644d6c91d0898fe38ac`.
This closes the bounded song valuation/admission work in A06, not the entire
ordinary AI audit or player presentation checklist.

## Implementation

Both native recipient rows (`C2618`) and area placement scores (`BDECC`)
now use the same marginal benefit for BRD-A1..A8, except Requiem. Native
admission still decides eligibility, faction, Silence and available resources.
Requiem retains native damage, element and absorption prediction.

| Component | Planning value |
| --- | --- |
| Soul Etude / Angel Song healing | Twice actual capped HP restored |
| Each Soul Etude cure | 20 only when Poison, Blind, Silence or Confuse is present |
| Protect, Shell, Regen | 20 per absent applicable status |
| March / Inspired | 20 when the corresponding owned buff is absent |
| Hide | 20 when Invisible is absent |
| Magick Ballad | Actual missing MP, capped at 20; never the caster |

Values are negative in native recipient rows for beneficial effects. Empty
benefit clears the candidate; mixed songs retain any useful component. These
are modest planning weights, not changes to spell strength or costs. Healing
reuses the execution magnitude with Recuperation and Magick Boost. Native
probability, law flags, effect classification and random willingness remain
intact. A positive original area score alone did not establish ally-harm choices:
native placement also uses absolute values and the recipient's row sign.

Magick Ballad and Witch Hunt inherited Ether's byte 25 value of zero, which
`133E18(actor, action, 128)` rejects during native AI discovery. Their build
records now use one: both are nonconsumable commands. This does not authorize
rewriting actual Chemist item admission, changing MP costs or using enemy stock.
The player-menu interpretation of that byte is not claimed by this audit.

The scorer must remain small. A discarded implementation invoked a second full
native forecast inside placement and overwrote resident IWRAM arithmetic at a
low test stack. Reusing existing admission and the small healing calculation
removes that extra pair of evaluated units. Current placement guards the
resident arithmetic, and complete turns guard native renderer code.

## Reproduction and evidence

Use `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only @(...)`.
Select `test-bard-ai-search` for assembly, one exact-ROM capture, recipient
checks and placement. On an already assembled current capture,
`test-bard-ai-review-cached` and `test-bard-ai-search-cached` avoid rebuilding.
`test-bard-ai-turns-cached` executes the fixed full-turn cases;
`test-bard-ai-chant-turns-cached` selects only the Chant case.

All following report timestamps have prefix `20260917T` and suffix `Z`:

- `002745.847632`: nine selected steps pass. All 320 song/condition/stack
  combinations pass 2,160 assertions, including shared supports, self/enemy,
  status prevention, fully buffed targets and small resource deficits. The
  42 native placement scenarios and eight Ballad/Witch Hunt admission cases pass
  293 checks: movement, range, affordability, Silence, redundancy and memory
  purity. The fixture is an exact capture of the candidate above.
- `003003.147195`: eight complete turns finish with 143 passing checks, but
  the report correctly fails its positive-Chant requirement. Three Ballad
  seeds (0, 3, 18) actually restore ally MP, do not restore the caster, spend
  zero MP and return through rendering/handoff. No-MP Chant and full-MP
  Ballad controls make no cast. Those passed cases remain accepted.
- `003647.881679`: three more Chant seeds (1, 2, 4) also finish without a cast;
  no positive acceptance is claimed for them.
- `004118.187221` and `004245.286440`: short, read-only diagnostics of the
  retained turn explain discovery and placement separately. Native `C1EB4`
  filters the command using its original 20% consideration probability.
  Seeds 0..4 exclude it; seed 5 admits it but later considers a distant ally.
  The AI working object is the pointer at `020101F8`, not a fixed adjacent
  scratch address. `test-bard-ai-trace` is intentionally a historical diagnostic
  pinned to this candidate/capture, not a release acceptance test.
- `004349.153646`: only Chant is replayed, with seed 5 and a declared nearby
  ally formation. All 22 assertions pass: one autonomous cast, 12 MP payment,
  actual Protect and March, intact renderer and clean handoff. No command,
  target, outcome or native probability is forced. Ballad is not replayed.

The initial placement harness also needed two corrections: distinct friendly
and opponent groups, and the native center-list allocation. MP admission occurs
before placement, so testing the placement callback alone cannot establish it.
Those failed runs remain in ignored reports; they were not production defects.
The recipient test also corrects its label for native bit 28 to Confuse; the
previous label said Sleep, but the actual tested bytes are unchanged. Sleep
is native bit 26 and is not claimed by that mislabeled case.

Raw captures, instrumented ROM hashes, input sequences and complete reports are
under ignored `build/expansion/`. Source scripts and this note are committed.
No broad regression was justified by this bounded change. Dedicated player
song controls, remaining ordinary utility/support AI and final assembled
acceptance stay open in [the checklist](../IMPLEMENTATION-CHECKLIST.md).
