# Moon Blossom integration evidence

September 14, 2026. Private engineering build; no player ROM or save replaced.

Eight-action Samurai candidate `e6e2ba03b53a4df80a8a4c17f96af490d28eb3ff`
passes the complete seventeen-step deterministic Samurai suite in
`build/expansion/test-runs/20260914T234811.104349Z/report.json` with unchanged
inputs. The base is assembled d1565a7ee341621e58bd2bb791b065144fe51aec.

Moon Blossom354 uses sixteen MP, the native fixed-self cross selector,
height two, primary-katana admission and 1.35P non-elemental physical damage.
Centered multiplies the whole action and retires once, including misses.
Native accuracy, damage, recipient selection, payment and reaction handling
remain in the executor. New direct actions suppress weapon drain/status procs;
restorative weapons remain restorative and cannot produce a Regen trigger.

One native Regen application occurs after the executor finishes when a row
records positive HP damage to an enemy. The initial A4672 hook was too early:
it has selected recipients but no completed damage. The accepted implementation
inspects A433C's returned output. The native Regen compatibility, setters,
removal mask, status cleanup and refresh are retained. It has no invented
three-turn timer. Full native status differentials cover all44 status bits.

Scripted cases cover misses, several damaged enemies, allied cross occupants,
Damage-to-MP with zero/nonzero MP, synthetic drain/proc/restorative katana
effects, Silence, payment, Centered, inventory/AP preservation, end-turn and
cold suspend resume. Native law checks use disposable owned units, respect
MP interception and preserve the additional prediction's RNG footprint.
Ordinary native law evaluation itself can sample RNG; this is not a claim
that the whole law path is RNG-free. Inner removal checks track Regen's native
Poison cure without inventing a harmful-status law for that cure.

## Subsequent restoration correction

Candidate `46a0d51567965ae0136e4c0a0f01d16ab87d2540` adds the approved
non-undead restriction to Murasame350 eligibility and its magnitude query.
Kiyomori351 keeps its ordinary native buff compatibility. Focused six-step
restoration coverage passes in
`build/expansion/test-runs/20260914T235536.833910Z/report.json`.
New cases cover undead allies under Charm/confusion/KO combinations, all256
packed state values, both stack residues and actual native executor rejection.
The in-game restoration replay also passes. The latest candidate has not
received another complete Samurai suite; unchanged earlier coverage remains
separately identified above.

Higanbana, Composure, Poise, Blade Ward and Counter Draw remain pending.
