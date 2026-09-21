# Auto-Potion pre-battle choice

Candidate `eb9e6b15c5915b22aa19787f8a4415ebb922f78d` implements I06 for
Nu Mou and Moogle. In **Pick Abilities → Reaction**, Auto-Potion has two choices:
Potion and Hi-Potion. The saved medicine is marked `- set`; the other row says
`Auto: Potion` or `Auto: Hi-Potion`. Confirm equips the same Auto-Potion lesson
and saves that medicine. Cancel changes neither. Default is Potion. Changing
to another reaction preserves the medicine preference for later use.

No new ability ID or save field is introduced. Existing saved metadata at
`02001E80 + roster slot` remains authoritative through `ffta_job_potion`.
Selection consumes no inventory. When the selected medicine is unavailable,
the reaction consumes nothing and does not substitute the alternate medicine.

## Native interface ownership

- `0807D96C` constructs the editable Pick Abilities list. Type2 is reactions;
  `0807C28C` constructs a different, read-only AP browser.
- The existing expanded list at `0203C000` owns20-byte rows from+230. One
  additional row duplicates the actual racial lesson (Nu Mou121/Moogle100),
  eligibility flags and help ID; names and row ordinals differ. Context+1134
  maps both rows to the same lesson, and+1132 carries the updated count.
- Confirmed reaction assignment at `0807E004` writes the native lesson and
  reads the still-owned native selected row with `08017B68`. Only the two
  authenticated Auto-Potion rows can update the preference. Native cancel,
  secondary-command, support and combo branches retain their original paths.
- Both hooks are explicitly imported by the central composer as well as the
  private Chemist builder. Code remains in Chemist's existing ROM reservation.

## Reproduction and evidence

Run through `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only`
with the named IDs below. Keep the generated ROMs, images, states and logs
ignored. The test runner records source hashes and complete output.

1. `test-auto-potion-preference`: fresh native town/roster navigation for both
   races, cancellation, Hi-Potion confirmation, reopening, actual cold save/
   reload and Potion confirmation. Run `20260916T131702.725462Z` passes10/10
   required steps and28 UI assertions. Screenshots confirm both labels fit.
2. `test-auto-potion-preference-controls-cached`: verified unchanged build and
   retained successful UI captures. Run `20260916T132007.604411Z` passes758
   assertions over64 native constructor inputs, both stack residues, exact
   ordinary-menu controls, list-write boundaries, AP/inventory preservation,
   ordinary-reaction confirmation and actual character switching.
3. `test-auto-potion-selected-stock-cached`: run `20260916T132128.954473Z`
   passes1,027 assertions over256 unequal-stock executor cases. It transfers
   actual UI-produced preference values to the owned native executor target;
   this is a tested interface composition, not continuous campaign playback.
   Includes168 positive recovery and56 empty-chosen/full-alternate controls,
   both racial owners and Pharmacology on/off.

The earlier `20260916T131526.581205Z` passes6,257 original backend assertions
but fails UI because the combined builder initially omitted the two hooks.
That failure is retained; the final correction imports them. The original
backend matrix uses equal stocks, so the later unequal-stock cases are needed
to prove no substitution. No full integration suite was repeated.

I06's bounded choice/persistence/no-fallback contract is complete. The all-job
presentation, final assembled regression and campaign gates remain open in
`IMPLEMENTATION-CHECKLIST.md`.
