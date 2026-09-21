# Remaining job state capacity and schema2 migration

September15,2026. Source migration implemented and accepted within the recorded
storage/combat scope below. These reservations do not implement the remaining job effects.

The canonical bank remains at0203F400 inside its existing1KiB reservation.
Its header16 and36 records of22 bytes consume808 bytes, ending3F728, before
the inventory at3F800. Established effect offsets0..2 and4..14 stay fixed.
Byte3 was unused by Dark Knight; schema2 assigns it centrally to Dancer.

| Bytes | Reserved owner and representation |
|---|---|
|3|Dancer: Polka T2 bits0..2, Frolic T2 bits3..5, Fury charge/skip6..7|
|15/16|Geomancer field X/Y, full native coordinate bytes|
|17|Geomancer field kind0..1, field T2 bits2..4, Wisp T2 bits5..7|
|18|Geomancer Wisp strength0, Updraft Move T2 bits1..3, Jump T2 bits4..6|
|19|Geomancer Steady displacement immunity T2 bits0..2|
|20/21|Mystic Knight enchant0..3, primary item4..12, Spellweave sequence13..14|

Timers use the existing T2/application-turn-skip representation. Coordinate
validity reader1CC7C takes full bytes and runtime dimensions; there is no
proof that native maps fit nibble coordinates. Item width supports0..511.
The machine ledger and `src/engine/job-state.h` define the same reservation.

## Save transport and migration

Schema2 footer FFTAJS02 contains32 header bytes and792 record bytes,824 total.
Its native staging address3CA8 ends at3FE0 within the fourth4096-byte page.
Static clean-ROM inspection:13B2EC supplies CRC length3CA8;13B37A begins at
page3 and writes/verifies whole pages through14224C/141BE0. This establishes
the intended bounds, not runtime acceptance of the larger transport.

The native marker JST1 remains an extension-presence marker. Footer schema,
width, count, reserved zeros, payload length, generation and CRC are validated
before any canonical state is published. Schema1/FFTAJS01 remains readable:
preserve bytes0..2 and4..14; initialize old reserved3/15 and new16..21 empty.
Corrupt, unknown or mismatched generation footers reject publication.
The synchronous save wrapper restores all824 staging bytes and the marker.

## Copy ABI and testing

All shared record loops/arrays use FFTA_JOB_RECORD_BYTES. Native copy tails
are enlarged to snapshot1140, manager430, selection3840, party7280 (hex),
and evaluated frame304 bytes. Native offsets remain fixed; owner registration,
copy chains, roster reindexing and clearing carry independent full records.
The manager parent allocation also grows. Shared compile-time assertions
check sizes. Action snapshots stay820 bytes; their extra flags remain in
the separate heap-excluded bank, away from IWRAM renderer code6170..6D67.

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite state-capacity`
for the coherent storage suite, then the assembled `combined` suite. Oracles
cover every record byte, both schemas and independent CRC corruption grids,
copy ownership, native allocation/rollback, roster order and clearing,
law evaluations, native save/cold resume and an independently encoded legacy
footer in actual flash input. ROM hashes and full reports stay ignored.
No output masking or interactive agent testing. Root owns review.

## Acceptance evidence

### Fresh native result stack correction (scoped acceptance)

Real queued Counter playback on the a4722af integrated candidate revealed
173 overwritten IWRAM renderer bytes at6C8C..6D58. Keeping every fresh result's
820-byte frame on the already nested native stack is insufficient after all
job callbacks are composed. Root now reserves eight824-byte slots at
0203CE40..E7FF, ending immediately before Passing Step. Each slot contains a
four-byte pointer to an exact live stack token and the unchanged820-byte
snapshot. Both the token's stack bounds and its exact frame value are required
before the frame can become current or join a parent chain. Closing clears
the frame and token. There is no saved-state or unit-copy representation.

The three heap ceilings are reduced toCE40. The extra frozen-flags bank,
Passing Step owner, diagnostics and schema2 unit/save layouts are unchanged.
The optional provider is composed only in the root image; standalone overlays
retain their existing stack result path. Actual native queued results execute
sequentially with further reactions disabled, so eight slots exceed their live
result-scope requirement. The full assembled regression and targeted ownership
review are accepted below; this does not complete the remaining expansion.

Targeted9d2e4b8 evidence now includes138 actual Counter assertions in
`20260915T164246.035067Z` and68 native external-owner checks in the all-passing
11-step `20260915T164512.554505Z`. Native Counter under Fight and409 has an
independent actor and retains its original primary parent. The full bank and
active root are cleared afterward. Getter controls reject mismatched tokens,
foreign token pointers, expired stack owners, RAM copies, bad self pointers,
oversize counts and closed frames without repairing or mutating them.

Final combined run `20260915T164555.393527Z` passes55/55 with unchanged inputs
on9d2e4b8 (shared base0e26f625). It includes the full existing reaction playback,
native saves/cold resumes, five AI cases, twelve Counter cases and the external
ownership controls. Root review confirms distinct reservations, exact token
validation, clearing and parent restoration, and unchanged save/copy payload
layout. The earlier54-step run's two one-frame-input timeouts remain recorded;
corrected fixtures required no further production change.

### Earlier schema2 acceptance

Shared image3540440aafbeebb560a14669b92da252971a5174 passed the complete
storage coverage across `20260915T113600.922187Z` (8/9) and
`20260915T113649.577552Z` (5/5 affected steps). The only initial failure was
a constructor oracle still using the55-byte old copy-tail stride;61 is the
new ABI. No production change was needed. Serializer tests passed16,480
checks; owner/copy/roster tests28,662, with full payload comparisons. Native
save coverage includes old-format import, schema2 cold resume and corruption.

Assembled image2416455f0f8b0b3994b63dc71f3d49002d07300f passed44/46 steps in
`20260915T113723.698711Z`. Viking's fixture still allocated10F0/428 instead
of1140/430; Dark Knight's record predicate ended at3F660 instead of3F728.
The11-step affected run `20260915T114310.843826Z` passed after those test-only
corrections and reproduced the identical image. The other44 results remain
applicable. All four reports record inputsUnchanged=true. Native reaction
playback includes36 scenarios/five cold resumes; Move/undo/AI tracing includes
two more cold resumes. No new native storage regression was found.

Root review confirms the existing effect offsets, independent copy ownership,
fixed820-byte action snapshots and old-footer reserved-field initialization.
This is not evidence that reserved job effects, full campaign, every save-slot
replacement flow or final clean-source assembly are implemented.
