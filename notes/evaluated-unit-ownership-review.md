# Explicit ephemeral evaluator ownership

This layer gives Exposed storage to the two previously unsupported evaluator contexts. It does not enable Fell Cleave, multiply damage, apply a status or install expiry events. Saved layout, existing AP owner roots and the reserved memory guard are unchanged.

## Containers and lifetime

`FFTA_EvaluatedUnit` in `evaluated-units.h` is exactly276 bytes: the original264-byte unit, a32-bit registration marker, a self pointer, one independent Exposed byte, and three reserved bytes. It does not add a Human AP sidecar or infer AP ownership for formerly unregistered units.

Heap ownership requires a valid marker/self pointer and an exact live allocated payload start in the current native heap rooted at0200F434. The walker uses the native physical block chain starting at heap+8, validates allocated/free markers and bounds, and requires capacity for the complete276-byte container. An interior pointer with copied tags is rejected. Common untagged buffers fail before the heap walk. The existing native free hook retires the tag before the allocator releases the block. A later unregistered allocation at the same address remains unowned.

Stack initialization is explicit and copies the supplied unit/state into a local container. It requires aligned IWRAM storage above the active stack pointer with the whole container in bounds. This rejects an arbitrary lower IWRAM buffer, including runtime code/data, as a claimed stack scope. The caller explicitly retires magic, self pointer and state before returning. Nested copied scopes remain independent after the source scope changes or retires. No name, character ID, race, job, global-source cache or live-roster fallback participates.

`unit-copies.c` consults this explicit owner after saved-domain lookup; native264-byte copy transfers the one owned byte independently of AP. Exact whole-unit clear zeroes state without retiring a still-live container; whole-container native clear naturally erases its tag. Source AP/native bytes remain governed by their existing contracts.

## Native law allocation patch

Native1343C8 has two branches, each allocating an actor and target with22840, copying264 bytes with142250 and freeing with22854. Only those four allocations grow. The original unit offsets,264-byte copy lengths, query1342CC and free entry points remain native.

| Patched span | Entry | Restored native result | Continuation |
| --- | --- | --- | --- |
| 1347D0..1347DC | ffta_law_actor_a | R5=264, R8=allocated actor | 1347DC |
| 1347DC..1347E4 | ffta_law_target_a | R5=264, R6=allocated target | 1347E4 |
| 13488C..134898 | ffta_law_actor_b | R4=264, R7=allocated actor | 134898 |
| 134898..1348A0 | ffta_law_target_b | R4=264, R6=allocated target | 1348A0 |

The veneers use R0 scratch, reconstruct the native size input, align C entry and preserve the surrounding frame/callee-saved registers. Successful calls allocate276 bytes, initialize only the ownership tail, and return to the native264-byte copies. Free sites remain13481E/134824 and1348F4/1348FA. If the first allocation fails, the wrapper returns through native false-result epilogue1344E2. If the second fails, it first frees the actor. This deliberately avoids dereferencing a null copy after the small allocation increase; no simulated effect or persistent mutation is committed on that failure.

`scripts/patch-evaluated-units.mjs` exports `patchEvaluatedUnits(rom,symbols)`. It checks the exact original byte spans and returns the four change records. The isolated test executes that production helper and compares its complete output with the tested installation.

## Shatter prediction

The only change in `physical-riders.c` is its predicted target container. It explicitly initializes a local `FFTA_EvaluatedUnit` from the evaluated target, removes Protect in `predicted.unit`, invokes the original native physical formula, and retires the tag before returning. The formula's supplied target pointer is therefore independently owned during the query. Source Protect, Exposed, AP and persistent data are unchanged. The native formula and current coefficients are otherwise untouched.

Future incoming Exposed multiplication can resolve this evaluated target's own byte. It must still use the actual evaluated recipient and the approved direct-physical-HP classification; this storage change does not implement that multiplier or its sequencing.

## Tests and integration

`test-evaluated-units.py` passes **11,245 assertions** against an isolated ROM based on d658e596e13febd725a0c312c204f844d2b92e62. Isolated ROM is575ca525f85638610ab51262b8da5f7dd3f616f7, binary3bfc7793f0ed8098c573031a1327fb3079ec15a7. It executes all347 original native outer-law actions at both stack residues and compares result/RNG against the native allocation path. There are692 observed inner native law evaluations, with deliberately different actor/target Exposed values. Tests also exercise both law branches, including21-query status iteration, first/second allocation failure, live allocation retirement/reuse, interior-pointer rejection, partial/full clears, nested stack scopes, null initialization, and actual Shatter native-formula entry/retirement. Across1,400 outer-law calls, live allocations, source units, AP/preferences, state, owner root and guard remain unchanged. All2,846 observed native C entries are eight-byte aligned.

The script's `--current` mode verifies the installed four veneers and uses an independent control ROM with those four original allocation spans restored. It does not compare the current ROM with itself as a supposed native differential.

`test-exposed-storage.py` and `test-exposed-storage-in-game.py` now accept `--current`, freeze under a per-ROM-hash directory and verify the matching engine image. Both already passed the integrated canonical-state foundation d658e596:212,567 assertions and real native normal-save/cold-load plus Fight preview/cancel/suspend/cold-resume. Those runs predate this ephemeral layer; repeat them on the parent's next compiled build for its gameplay regression acceptance.

Required compiler inputs: `src/engine/evaluated-units.c` and `src/engine/evaluated-units.s`, in addition to the already integrated battle-state source. In the combat builder, import `patchEvaluatedUnits` and append `changes.push(...patchEvaluatedUnits(rom,symbols))` after creating the ROM/change list and before writing the artifact. No other production builder or assembly hook is needed. The parent owns that integration and shared rebuild. The physical-rider isolated test compiler needs the new C dependencies; its `--current` path can test the integrated build directly.
