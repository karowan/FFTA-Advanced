# Council: selective axe visual hooks

2026-09-14. Independent native disassembly and Unicorn review of `src/engine/axe-visual-hooks.s` and `scripts/build-axe-visual-probe.mjs`. Tested frozen axe-visual SHA-1 `3d664d20c82b09a13aaa227057fc55a5e422d3f4`, engine `a0bc1d4f3d00e693126517d151ba86ce31091c3b`, reconstructed job-ui baseline `3afc19bd7031df7e2c501e0c653a54b04f7e5ee2`. Frozen input: `build/expansion/probes/axe-visual-test-input.gba/json`. No engine files were edited.

**Accept these four visual-only mappings within the tested scope.** `scripts/test-axe-visuals.py` passes64,512 assertions,41,352 complete native getter/function calls, and13,872 actual installed/native control-flow segments. No source defect was reproduced. Results are recorded in `build/expansion/probes/axe-visual-test.json`. Rendered battle appearance and actual audio playback remain the parent's emulator acceptance task.

## Native switch contracts

| Patched raw ROM span | Input and retained real values | Accepted continuation / fallback | Category5 native case |
|---|---|---|---|
|986DA..986E5|r5 contains actual item category; r7 retains actual item ID|986E6 /98758|9873C sets derived visual class r5=1|
|A58A0..A58AB|r0 contains category; r4 retains actual item ID|A58AC /A597C|A5900 requests sound7B|
|A7EDC..A7EE7|r0 contains category; r4 retains actual item ID|A7EE8 /A7FB8|A7F3C requests sound7B|
|B3C64..B3C6F|r0 contains category; r6 retains effect-state pointer|B3C70 /B3D88|B3D08 selects callback080AE7D9|

Native Barong is item52 and its category is5. Only derived switch input31 maps to5; the real item records remain category31. Original switch domain1..19 still indexes its existing19-entry table. Types0,20..30,32..255 and sentinel-1 preserve native fallbacks. B3C70 still performs the native table-base addition; its shim deliberately does not add twice. The other three shims replay their displaced addition before continuing at the table load.

The actual installed stubs are tested for every uint8 value0..255 plusFFFFFFFF, at native SP residues0/4 and incoming NZCV patterns0000/F000. Continuation address, r0..r12, resulting NZCV, caller stack frame and effect-state memory agree with the native control, apart from the intentional category31-to5 switch choice. For the actor switch, the control's r5 is adjusted back to real31 when comparing the pre-case continuation, explicitly ensuring the shim did not change that register. The switch itself writes only its temporary four-byte stack save and restores SP.

## The downstream r5 question

Preserving real category31 in r5 at986E6 is safe **because the chosen native case overwrites it**. Table986F0 entry4 points to9873C, which executes `movs r5,#1` before9875A. From that point r5 means the derived visual class, not the raw weapon category. Later switches at987A8 and987E8 therefore receive1, matching native Barong behavior, rather than falling back on31.

The test follows every switch case/fallback to its shared continuation, then separately follows all eight axes453..460 from986B2 through the real category getter at986C0, property9 getter at986CA (saved at SP+0C), property8 getter at986D4 (r9), and pose selection up to988A4. It covers all12 native animation codes6..17 and four facing values at both SP residues. Registers, flags, frame values and effect state match a baseline that changes only the visual switch input. No item-ID substitution is used to hide a property difference.

## Sound, effect state and data preservation

Both sound case bodies execute their native sound request. The test also executes the complete A7EC4 swing-sound function, including CA7A4, for all461 valid item IDs0..460 at both SP residues; all eight axes request7B. The sound playback entry141520 is intercepted to record its requested ID and return. This validates sound selection and function ABI, not the hardware/audio backend.

The effect path executes through the case assignment and common native writes, stopping at B41BC. For the donor case, B3D08 obtains destination `r6+148C` and callback080AE7D9; B3D8E stores it. The existing native state flag/timer writes also execute and match the control. The selected callback itself is not rendered/executed as a complete effect by this harness.

Every supported CA7A4 selector0..18, default19, and255 is compared across item0..460 at both SP residues. All19,362 getter results are identical between baseline and probe; each axe still returns31 for selector3. Exact full-image comparison allows only the four12-byte hook spans, so item records, AP data, law/category semantics and other gameplay structures are not rewritten by this stage.

The wrappers make no C calls. Function-level tests verify native callee-saved registers and SP; inline comparisons check all general registers except LR. Their tail trampolines use LR as a branch scratch. LR is dead at these native insertion sites: the enclosing routines already save return addresses and their later returns restore saved addresses, and the complete A7EC4 function-return test confirms this in the directly callable sound path. This acceptance does not extend to custom axe damage, hit accuracy, lesson effects, equipment rules or new battle animations.
