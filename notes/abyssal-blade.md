# Abyssal Blade integration

The primary agent implements and reviews this change. All earlier agents have
finished; no new agent or council is involved.

## Implemented behavior

Action 362 (DRK-A7) uses a cardinal line of three tiles, including allies and
excluding its caster. Each recipient rolls ordinary physical accuracy. The
coefficient is 140/100, 125/100 or 110/100 at distance one, two or three. It
joins the existing rational damage product before rounding and capping.

The primary sword, greatsword or broadsword supplies the physical reference
and weapon element. Offhand weapons do not qualify the art or add another
strike. The existing new-art weapon drain and proc exclusions include 362.
Native physical classification, primary-weapon law inputs, per-recipient
support/reaction factors and resource interception remain in the shared paths.

The native action charges 10 MP and ceil(15% maximum HP) once before recipient
rolls. Bloodcasting changes this to the sacrifice plus 20 HP; the combined
cost must leave at least one HP. Repeated recipients and complete misses do
not cause extra charges. This is a single action, not proof of the outstanding
compound Bloodcasting reservation for multiple subcasts.

The native directional range encoding is 0x40. The common Wind Draw list
routine also handles 362: it stops at the first invalid/impassable panel or
height difference outside +/-2. Its origin comes from descriptor bytes 4/5;
geometry receives the separate native eight-argument evaluated-coordinate ABI.

Damage receives explicit evaluated unit pointers. Native preview B55CC saves
their old F6/F7/F8, supplies wrapper coordinates at B5678..B56AC, calls the
formula at B572C and restores the old fields at B5832..B586C. The coefficient
reads those evaluated positions, never a roster-owner lookup or area center.
The deterministic stale-position cases execute that complete native routine.
Its C-style return is void: the test observes damage at B5730, before display,
and does not treat the epilogue's caller-LR value as damage.

Both racial lessons receive a bounded native help description. Teaching remains
the approved Abyssal Edge, 300 AP, S3 acquisition in WEAPON-ACQUISITION.md.
This change enables its previously allocated action; it does not itself certify
the equipment/AP/shop/campaign paths.

## Reproduction and evidence

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite combined`.
The declared Abyssal test also supports the isolated Dark Knight candidate via
its job plan. It reuses the candidate's verified native executor fixture and
retains fixed inputs, output logs and ROM hash in ignored build reports.

The first full run, 20260915T073515.457936Z, passed all 31 existing checks and
all 256 new three-recipient executor cases before the new preview harness
incorrectly read the native void return. The corrected ten-step rerun
20260915T073818.493993Z passed 17,209 Abyssal assertions on candidate
cc32952fe9696192faa97eb50825d226ce50b6ff. No gameplay change was needed for
that test correction. The earlier build-only run 073434.000801Z rejected an
overlong help description; the shortened text fits the native three-line limit.

The extended test adds Desperation activated by the sacrifice, enemy versus
friendly TBN recipients and full native rejection of insufficient HP or MP.
It covers real hits/misses, all four directions, both races, mixed allegiance,
Bloodcasting, all item IDs, 24 moved-preview cases, 2,592 area/terrain cases,
output guards, position restoration, unchanged preview RNG and one rounding.

Final consolidated run **20260915T074057.555611Z passed all 32 steps**, with
`inputsUnchanged: true`, on the same cc32952 candidate (shared state base
bc9626134a72cb64a3a06d9a14c1d96ae0fbef1c). The final Abyssal test passed
**18,736 assertions**, including 256 basic and 128 Desperation/TBN scenarios,
each executed against both native-reference and production images, plus the
preview, geometry, weapon and resource-admission matrices described above.
All existing combined Chemist, Viking, Dark Knight and native baseline checks
passed in this run. Review found no new shared-state allocation or save-schema
change; the player's ROM, saves and launchers were not modified.

## Remaining acceptance

Rendered animation and complete native menu navigation, autonomous AI scoring
and turn execution, broader law interactions, equipment teaching/acquisition,
save/cold-load regression and the rest of the expansion remain separate work.
The private combined candidate is not a finished expansion or a replacement
for the player's ROM/save.
