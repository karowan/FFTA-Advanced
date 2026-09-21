# Native Ivalice battle fixture

## Result (2026-09-14)

`scripts/create-battle-fixture.py` reproducibly cold-loads the isolated `build/test-lab/early-town.sav`, accepts Herb Picking through the ordinary pub, travels to Giza Plains, deploys all six original party members, and reaches the first battle command menu. It writes only under `build/expansion/probes/battle-fixture`. It never opens or changes a user ROM/save or visible game session.

Accepted frozen ability-core ROM SHA1: `8dd238a15f4a3df6649ed66e0f4df0c7edd7adf0`. `frozen.gba` must accompany `battle-ready.state`; save states are tied to that exact ROM. `battle-ready.ram` and `battle-ready.iwram` provide the matching live memory snapshots for bounded native routine tests. The script can recreate the fixture against a newly built ability-core ROM in about eleven seconds.

There are no extra progression flags, gameplay RAM writes, artificial map placements, forced scene transitions, or modified mission records in this route. The only test RAM write after loading the supplied SRAM is the reserved-region canary at `0203FF44..02040000`. The quick-start flags used to create the pre-existing seed are not altered.

## Why movement seemed blocked

The world map uses a freely moving cursor. Eight-frame directional taps do not necessarily reach the next region. Cursor coordinates are native halfwords at `02002C16` and `02002C18`; this follows native world cursor owner `*03002810`, its pointer at +4, and coordinate fields +6/+8.

The existing seed already has Cyril at tile18, Sprohm at13, and Giza Plains at20. Native location placement is `02002CC3 + 12*(locationID-1)`. Location identities are2 Cyril,3 Sprohm,8 Giza Plains, verified against native world label lookup. `36330(locationID)` returns the placed tile. With the live world RAM loaded, native `35A20(tile-1)`/`35A44(tile-1)` give coordinates; Giza is104,288. The native cursor target adds6,4, giving110,292. Calling these coordinate routines against an empty synthetic world returns zero, so their data context matters.

The fixture evaluates those native getters in a separate copied ARM memory image, then steers ordinary D-pad input toward that target. It does not write the cursor or region location. Native A input travels the clan to Giza and opens its Herb Picking mission menu.

## Repeatable input route

After the standard Continue/Load flow, three A taps enter the pub path, twenty A taps complete introductory dialogue/mission acceptance, and four B taps return to the world. The fixture intentionally records the world screenshot and route coordinates; it does not infer success from a guessed dialogue count alone. Successful native Giza mission entry, rendered mission name and populated battle are the downstream evidence.

Seven A taps from the Giza mission menu advance the intro and two deployment notices. Marche and Montblanc are already deployed. Three A taps deploy the currently selected Ford; for each of the three remaining generic members, Right followed by three A taps selects a unit, places it and confirms facing. Start opens Begin battle; A confirms, then the next A reaches the first normal battle command menu. The accepted image shows Jona with Move/Action/Wait/Status and WT1/12.

## Populated heap evidence

All observed live battle heap snapshots have root `020159D0` and end `0203F800`. The linked physical-block walk verifies each allocated/free marker and bounds. The smallest sampled free payload during deployment is54,052 bytes, entirely in the largest free block; allocated payload is117,352. At the first normal turn, allocated payload is92,572, total free78,868 and largest free56,040. These are measurements of this specific populated mission, not a worst-case bound for every map or action.

Native `99CDC(manager,destination)` enumerates12 live battle actors from manager `0201F134`; six underlying pointers exactly equal the six canonical party slots `02000080..020005A8` at264-byte stride. The six other records are `02002FC4..020034EC`; do not label all six enemies because the native judge is also an actor. The canary after the compatibility view and20-byte AP owner roots survives title, world, native battle construction, all deployments and first turn.

This establishes a usable real Ivalice battle fixture and populated allocation capacity. It does not by itself validate every AP rollback/AI preview path, new-job command, suspend save or mission completion. Those tests can now operate on this matching state/ROM pair or regenerate it after a rebuild.
