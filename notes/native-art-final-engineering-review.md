# Full engineering review: original game plus v0.7 expansion

Root accepts E01-E04 on `a28b624bb13c8f2f2597a4d4bd3999b17c234b99`.
The engineering scope is the complete original USA game and approved v0.7
expansion, including the connected native graphics consumers. Only final
artwork and artist-authored poses remain placeholders. Repeated poses do not
excuse missing action commands, incorrect effects or broken game behavior.
E05 remains open until the separate package and launcher are verified.

## Acceptance matrix

| Gate | Authoritative evidence and root conclusion |
|---|---|
|E01 rendering performance|native-art-native-performance.md and its19-file index. Fresh original-renderer control, paired entry66, response6191 and deployment7891. Move/cancel match at both offsets, zero extra frames; deployment cadence and2240 complete observations agree. Build-time palette conversion replaces the costly runtime ownership/remapping layer. Earlier failed optimizations remain rejected.|
|E02 complete graphics consumers|native-art-engineering-consumers.md and its65 direct/267 referenced pins. All1680 descriptor slots, full pixel payloads and native command/OAM/timing metadata;20 permitted Fight pairs,19 Combo initiators, current Combo participation and primary/secondary casting, held axe/projectile/impact, current equipment eligibility/portraits/status UI. Original fixed story characters retain their original presentation. Water and other retained tests keep their original ROM and finite coverage.|
|E03 capacity and lifetimes|Native selection4273, demanding all-ten13-actor allocation17696, actual Thundaga with1800 consecutive heap observations, next-turn/two balanced Status cycles195 and exact heap reconciliation134. Current native battle result, territory placement, full world menu, normal save/cold and actual ending scene lifetimes supplement these. Original actor construction/selection remains unchanged; see the capacity decision below.|
|E04 full-game compatibility|native-art-campaign-compatibility.md,188 evidence pins and review484. Current ordinary/ending cold54, native battle result plus placement/menu/save/cold suffix16, actual ending/credits/scene-owned save/reset/Continue/cold14. Whole original scene/mission dependencies and original gameplay sources are reconciled with release1b070824. Retained connected milestones and earned final bridge remain their own evidence.|
|E05 source reconstruction component|Fresh eight-stage source base5065a9ea plus all eleven current art stages reproduce the entirea28 image. All eleven pixel conversions are regenerated from original PNGs; native references are extracted again. No old component ROM, tile binary, save or savestate is a build input. Full package/launcher verification is still required.|

## E03 capacity decision

The supported engineering target retains the game's existing encounter and
actor-count rules. The expansion adds class graphics and gameplay behavior,
not a new deployment or actor-count domain. All native mission/event tables,
the original scene interpreter/actor region, and the battle actor manager are
byte-preserved relative to the accepted gameplay release. The audited scripted
spawn, judge, saved-roster restoration and primary/secondary roster constructors
therefore keep their original selection, reuse and retirement behavior.

Native sort has thirteen pointer slots. The deliberately substituted formation23
inside the different Giza scene creates fourteen actors and corrupts that native
array. The exact original collector/sort reproduces the same counter overwrite
against clean US code; thirteen-actor controls return correctly. It is not caused
by the new sprite renderer. All512 mission slots and the audited native mission,
random-event and descending scene selectors exclude the sole over-thirteen
initial estimate (event203); scene168 actually selects event255. The corrected
full-event fixture has twelve actors, not fourteen. This evidence is sufficient
to reject that artificial combination as a required new capacity, without
claiming an exhaustive proof of every indirect script or malformed saved state.

The actual demanding supported-size fixture has six party, six opposing actors
and a judge, with all ten added class resources allocated. It retains all actors
through a two-target Thundaga, next turn, two complete Status lifetimes and then
native result/scene teardown. Each Status closes to the identical complete heap
block list. Minimum free space at Status is11,052 bytes, with8,776 contiguous;
the returned heap has54,632 free. Native shared palettes remove the reproduced
exclusive-bank shortage. Subsequent original ending scenes and full world-menu
allocations also complete on the changed memory layout.

Root accepts this combination of unchanged native count/selection contracts,
bounded demanding execution and actual scene/save lifetimes for E03. It is not
a promise to support arbitrary fourteen-actor formation transplants,36 simultaneous
actors merely because the iterator visits36 records, every conceivable effect
combination, or another overhaul. The fourteen-actor failure stays failed; no
hidden roster cap, actor removal or isolated sort-array enlargement masks it.

## Reproducible source chain

`build-full-engineering` in the declared art plan reconstructs the base from the
clean USA ROM, pinned local tools and versioned sources. Three explicitly pinned
historical source files reproduce the accepted gameplay stage; current menu and
graphics sources then compile in the later stage. The source profile is
native-art-gameplay-base.json; original PNG/conversion inputs and expected stage
hashes are in native-art-build-inputs.json. These are reproducible source stages,
not cached binary inputs.

Fresh base report: build/reproducibility/20260919T100752.819552Z/report.json.
Its eight stages pass in125.89 seconds and reproduce5065a9ea. Full art report:
build/art/engineering-rebuild/20260919T101346.342232Z/art-report.json.
Final ROM SHA256:029547bb57325915a7d4a97f9e0e19b096645bf3d25d131c35c216ef6da41e78.
The output equals the already accepted current ROM byte for byte.

The first enclosing run100752.047721Z fails after four exact art stages because
the new source-derived palette-reference path still referenced an old metadata
variable. Resume101232.400884Z fails before art execution because its report
directory already exists. Both are build-tool failures, not ROM acceptance.
Corrected resume101345.670886Z passes, reusing the exact authenticated fresh base
report and rebuilding all art stages. Reports now have independent directories.
native-art-engineering-rebuild-evidence.json preserves all three outcomes.

## Limits and final gate

This review uses the union of declared current and authenticated retained tests.
It does not relabel failed runs, claim one uninterrupted full-combat campaign,
every optional original story variation, or physical-GBA performance. Existing
renderer/AI/campaign limitations retain their scopes in release-acceptance.md.
Final art quality remains unaccepted and is intentionally a later session.

The final acceptance audit must authenticate this matrix, actual ROM/source
identity and referenced evidence. Packaging must verify deterministic BPS output,
patch roundtrip, wrong-source rejection, a complete player guide and dedicated
launcher/save paths while preserving existing games and saves. No game launch
or remote publication is part of completion.
