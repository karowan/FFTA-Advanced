# Dark Knight barrier and queued reaction integration

The primary agent implements and reviews this integration. No additional agent
or council is assigned. The historical job handoff remains a record of what
was delivered before integration, not the current acceptance state.

## Barrier execution contract

Fight has a dedicated native executor and does not initialize the global
descriptor context. Its authenticated direct HP writer establishes physical
damage for Dark Knight consumption; unrelated old descriptor data is ignored.

The combined physical/magical finalizers retain one rational damage division.
Before that division, they determine whether other mitigation leaves positive
HP-payable damage without TBN. The exact current recipient receives transient
snapshot bit 24, already reserved as `TBN_CONSUMING`. The shared setter accepts
only RESULT phase and native primary origin. It changes no frozen equipment or
status tags, persistent state, snapshot layout, or save schema.

Only the successful direct native HP writer converts that candidate into
consumption claim 32. This also works when TBN rounds one damage to zero.
The marker is cleared at that write. A preview, miss, wholly MP-redirected
action, recovery or displacement cannot claim the barrier this way. The
existing queue completion consumes the ward once after all eligible components,
while the action-start snapshot preserves its reduction for the whole action.

Shatter Guard deliberately calculates against a temporary defender with Protect
removed. Its marker uses the original recipient explicitly supplied by the same
native effect context, after validating action, actor and execution phase.
It never resolves a unit through a roster identity or writes to a retired copy.

## Queued reactions

Vengeful Pulse's original hidden descriptor used application 1, a native no-op.
The formula and immutable queue payload were correct, but no HP effect followed.
Descriptor 219 now uses native HP application 21, retaining eligibility 8,
Sure accuracy 23 and its fixed magnitude callback 0. The combined weapon hooks
explicitly suppress weapon drain/procs for hidden action 434.

The magnitude uses the existing authenticated RESULT-only kind/value getters.
A speculative internal-preview payload API was tested during diagnosis and
removed when actual return-value tracing showed it was unnecessary. No broader
query access to reaction payloads remains in the implementation.

Dark Ward creates actual hidden Shell action 433. Vengeful Pulse creates actual
hidden damage action 434, once after the complete incoming action, using the
direct-HP ledger rather than direct-plus-fall injury. Native two-weapon Fight
produces two primary result objects; the single return follows both. Its disabled
reaction permission prevents the original attacker's Counter from answering it.

## Reproduction and evidence

Run:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Suite combined
```

`20260915T072047.890256Z` passed all 31 steps with unchanged source fingerprints.
The image is `0d5646f09eab0cd4f962de383794c6fb110d9dd3`, on shared-state base
`a63550b5ab50ebaca38963bbd067fb389e7752ac`. The new reaction script passes 3,303
assertions, including 434 native hits rounded from one damage to zero: Fight 35,
original magic 119, Crushing Blow 119, Viking magic 126 and Shatter Guard 35.
`test-integrated-dark-reactions.py` includes real native Fight, original magic,
Dark Arts, Viking magic/physical and Soldier Shatter Guard execution; both Dark
Knight races; Poise combinations; unchanged MP payment/RNG; wholly MP-redirected
damage; queued Shell and fixed retaliation; survival, range 3/4, five affinity
values and two-weapon/no-recursion cases. Its fixed low-stat input grid finds
native zero/one/two-damage boundaries and checks every such selected control
against the same warded setup. It never replaces a calculated magnitude, hit,
resource result or RNG value. Isolated phase fixtures additionally cover the
transient marker and pre-TBN rounding contract.

The reports preserve earlier failures: `070438.297812Z` exposed absent retaliation
HP; `070736.932768Z` had a temporary missing import; `070810.026338Z`,
`070947.970872Z`, `071138.620363Z` and `071232.754966Z` retain successive native
diagnostic traces. `071509.674981Z` passed the first 31-step suite.
The expanded `071824.080151Z` exposed Shatter's retired-copy marker, fixed before
`071932.567847Z`; the latter then exposed a test assumption that two-weapon Fight
would have one primary object. The final test requires the exact two-primary,
one-return ordering instead of weakening the recursion check.

## Remaining scope

This is native executor acceptance of the covered mechanics, not completion of
Dark Knight or the expansion. Abyssal, compound Bloodcasting upfront reservation,
full legal secondary-command/UI/AP/acquisition coverage, visible reaction
playback, complete save/copy/new-game flows and voluntary multi-subcast grouping
remain separate implementation and acceptance obligations. Later final coverage
must also include additional interception combinations and cross-job effects.
