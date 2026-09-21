# Campaign scene, territory and final-entry acceptance

Candidate SHA1 remains `1b070824a8dad4995434eee3ab40fa08187a6120`.
Run `20260917T122656.766531Z` passes assembly verification and
`test-campaign-territory-scenes`:45 checks in28.0seconds. This is the completed
targeted milestone procedure, not a full integration suite or an uninterrupted
campaign played through combat. No shipping code or player save changed.

## Native paths now connected

| Milestone | Original behavior observed |
| --- | --- |
| Desert Patrol19 | Earned native mission eligibility/acceptance, ordinary map selection, scenes63→64, native result receipt786 and story stage21→22, then actual cursor placement of location20/Della Dunes for the next Quiet Sands mission. |
| Over The Hill25 | Earned native eligibility/acceptance, map selection, scenes89→92, native result receipt792 and stage29→30, then original creation of location30/Ambervale at fixed tile9. All30 declared/final placements remain unique. |
| Royal Valley26 | The real Over The Hill result makes26 eligible. Saving at Ambervale writes real flash and sets native gate75. Selecting another destination invokes the original departure controller, which chooses event26, enters scene93 and reaches its original battle-start opcode `0x089B644B`. Native flag572 records entry; final receipt793 and cleared54 remain absent. |

The final screenshot shows the original unit-deployment notice. Root also
reviewed both placed-territory images. Scene93 connects to the previously
accepted three-battle exit bridge in [final-battle-scene-bridge.md](final-battle-scene-bridge.md),
which connects to101 and the actual ending/credits/save/reset/cold sequence in
[campaign-ending-scenes.md](campaign-ending-scenes.md). Those suffixes were
not replayed. Existing early Herb Picking/Lutia Pass placement and cold-save
evidence remains in [morpher-native-preservation.md](morpher-native-preservation.md).
The actual Shara scene/acceptance/capacity/save lifecycle is retained from
[shara-scene-lifecycle.md](shara-scene-lifecycle.md).

The important native distinction is `D17C4` versus `D1A18`. The former builds
the location menu. `D1A18`, called at `0x080325E6`, evaluates the post-save
condition before departure. Repeated A on Ambervale only revisits its save
question. After saving and closing the picker with B, selecting Sprohm lets
the original controller start Royal Valley before travelling away. No scene,
event, completion result or final-entry flag is substituted by the observer.

## Inputs and limits

The milestone boundaries reuse authenticated receipt flags from the connected
progression report `campaign-progression-20260917T083905.312061Z/report.json`,
SHA1 `8f5325761e1604d2a0c61af665014570cc9eec1f`. Its earned stage2/stage3 snapshots
are authenticated individually. Native services complete the short intervening
prefix and accept the selected mission. Every changed native service byte is
recorded and carried forward, including original bookkeeping outside the queue.

These are representative milestone fixtures: surrounding map ownership and
unique positions, story stages21/29 and all24 party slots'999HP are declared.
They are not a claim that the surrounding map was placed through earlier play.
The prospective award starts unowned/unplaced. Ambervale's fixed tile9 is
reserved, and its availability bit starts unset. Native actors are enumerated;
only hostile actors' HP is zeroed after deployment (7 for19,6 for25). Every
party/judge/guest/story actor is unchanged by this controlled defeat input.
Actual result scripts, receipts, stage updates, awards, saving and final entry
run normally. This verifies connections; it does not prove winning combat,
every intermediate cutscene or every special recruit's distinct story script.

Earlier recipe/rumor/teacher/recovery reachability, law outcomes, encounter
access and recruitment mechanics retain their separately scoped evidence.
Together these meet the requested representative early/middle/late/postgame
milestone coverage. Release-wide evidence reconciliation and root review remain
R02; this note alone is not release certification.

## Evidence and reproduction

Private reports are beside the current candidate, resolved through
`build/expansion/probes/integrated-jobs/current.json`:

- Completed procedure: `territory-scenes-20260917T122700.200984Z/report.json`,
  SHA1 `17471033eb3011b057f9bcc3736fea312d87d4e3`.
  Tested source SHA1 `d514a34cd354ccf69a0b9826494eb77785eb7d1c`;
  observer image SHA1 `d3583e0e04a813ce135ea3a3d7b6c71bdad43c9e`.
- Isolated successful departure suffix: run `20260917T122359.637283Z`,5 checks,
  3.5seconds; `final-departure-20260917T122400.314767Z/report.json`, SHA1
  `04ed1fc1849ec463e031d9e22e7f10462e19bf2b`. It authenticates the actual saved
  endpoint from the preceding diagnostic; the completed procedure supersedes
  that diagnostic prefix. The suffix loader's helper pin was updated during
  consolidation; the private observer image is unchanged.
- Original/candidate condition comparison: run `20260917T122148.218777Z`,8 checks,
  0.2seconds; `final-condition-20260917T122148.917904Z/report.json`, SHA1
  `8da6af9e007e468d6c4a1d94df251b32f9c4ee96`. Native `A5D4(0)` queues93 only
  for the real saved-arrival case, not the no-save75, already-cleared54 or
  already-entered572 controls. Candidate and clean-ROM outputs/traces match.
  This comparison proves the predicate, not rendered entry; the completed
  procedure above proves entry.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-campaign-territory-scenes
```

Use `test-campaign-final-departure` only for its authenticated existing endpoint,
or `test-campaign-final-condition` for the bounded original/candidate comparison.
Both have the declared assembly prerequisite. Reuse the completed procedure;
there is no reason to repeat it for documentation changes.

## Failed and superseded diagnostics

All dated reports/logs and their available captures remain ignored/private.
No earlier failed overall run is relabeled as passing. The accepted full
procedure replaces the intermediate fixture/setup variants:

- `114736` never travelled to the target. `114830` called the wrong selector
  from an entry hook after the native game had already selected the event.
  `114933` retained the incorrect special-menu selector assertion. The final
  observer never changes scene arguments or dispatches events.
- `115022` completed Desert Patrol and reached Over The Hill's real scene92;
  its expected91 oracle was wrong. `115210` incorrectly expected a cursor-
  placed Royal Valley region: the original scene creates Ambervale at tile9.
- `115351`, `115548`, `115630`, `115741`, `120034`, `120250` and `120454`
  cover intermediate late/save/entry diagnostics. Corrections included the
  reserved tile9, native ownership bytes, deferred Ambervale availability,
  16-bit image decoding, closing the saved slot picker, and distinguishing
  the menu selector from the departure selector. The repeated-save diagnostic
  overwrote repeated capture labels; its images are not accepted evidence.
- `120859` confirmed that transferring all native service changes did not
  itself solve entry. `121138`, `121236` and `121345` investigated save-menu
  choice and travel; after saving they still selected the current location.
  The condition/controller trace, followed by the successful122359 departure
  suffix, resolved that input error.
- `121822` accidentally executed the producer because its helper boundary
  did not normalize CRLF. It is excluded. `121927` correctly cold-loaded the
  real save and passed29 member/profile checks, but failed its assumption that
  cold Continue alone should start the final event. That diagnostic source
  remains in its private report; it is not a declared acceptance test.

The consolidated source removes the failed diagnostic modes from the test plan,
keeps bounded inputs and checked helper boundaries, and runs only the working
native save/departure path. No gameplay patch was made to satisfy an oracle.
