# AP count publication council review

2026-09-14. Reviewed `src/engine/ability-counts.c`, import/give entries in `ability-hooks.s`, appended ability-load entries in `load-hooks.s`, and `build-ability-probe.mjs`. Frozen ability-core SHA-1 `5dcc9329f84963bb181d4161c81292d772bf7c3e`, engine SHA-1 `fbb8c7217402af650dd9212249fb974e811ca620`. No engine files edited by this reviewer.

## Result

**1,121 behavioral assertions pass** in `scripts/test-ap-counts.py`. The script reads and verifies the current ROM, baseline and engine hashes, freezes the ROM/manifest/symbols under `build/expansion/probes/ap-count-council/<hash>/`, and runs native Thumb code with real boot IWRAM. It does not rebuild or modify user saves.

The proposed count publication is separate from template import, preserves original bounded imports, initializes nonhuman padding only during first native-save conversion, and retains already-format1 AP even when its count byte is still the old value. Human count178 is published only where an extra-AP owner exists, except staging-roster normalization where those exact24records will become live roster records after commit. Other race totals111/124/118/116 fit the original inline byte capacity.

The initial audit found a fixed24-byte stack save in the ability-load macro that allowed C entry at SP modulo8 equal4. Parent corrected all four normal/suspend load entries to preserve the exact incoming frame and align the C-call stack. The fresh ROM passes a **hard assertion** that both tested native stack residues reach C aligned to8, together with native SP/LR/r4–r11 preservation. No unresolved count-publication finding remains in this bounded review.

## Native import contract

A direct Thumb BL scan below ROM150000 finds **one C9F88 caller**, at `C9AAE` inside constructor `C9644`. It passes destination unit inr0 and template inr1. Immediately after return, `C9AB2` overwritesr0 with the unit for innate-lesson helper `CA22C`, followed by `CA2E8`. C9F88's epilogue pops its return address into r0 and branches through it; the caller does not consume a semantic return value. Forwarding the trampoline result is harmless, but its numeric value is not a meaningful import status.

The importer obtains the AP structure via native unit getter selector22 (unit+34), and obtains race count from `C9ED8`. That count is stored before the loop. `C9ED8` itself has only direct caller `C9FAA` in this importer. Its return values remain unchanged for all256 possible byte inputs in the test.

The original import loop uses lessons1..<count, template bitmap at `template+14+(lesson-1)/8`, and AP destination `unit+40+lesson`. If Human count were widened before this loop, lesson144 would overwrite non-AP unit data and lesson161 would consume template+28, a separately used support field. The new wrapper calls the intact original importer first and publishes afterward. The trampoline correctly replays the displaced prologue before resuming atC9F90.

Differential fixtures cover five races, live roster versus unowned unit, format0 versus1, three learned-bitmaps (00/55/FF), and both SP residues. The entire264-byte resulting unit equals the original import result except for the deliberately eligible count byte. Unit guards and the template remain unchanged. Existing Viera coupled-learning native code is exercised when its corresponding template bits are set. This is a direct importer test, not an independent full C9644 constructor test; its only scanned native caller clears the complete record beforehand.

## Publication and migration contracts tested

- Publication rejects null/inactive/invalid-race contexts and only changes recognized original or expanded count values; unrelated or inconsistent count values are preserved.
- Unowned Human records keep the native import count142. Owned live Human records reach178. Nonhuman imported records may publish their expanded inline counts without an extra-AP owner.
- Migration tests use all24 staging roster slots, all five races, original and expanded count bytes, deliberately nonzero former AP padding, an inactive slot and an invalid-count slot.
- First native conversion clears only newly allocated nonhuman AP spans: Bangaa77..110, Nu Mou95..123, Viera85..117, Moogle88..115. It preserves all other unit bytes except recognized counts. Human sidecars are zeroed by inventory conversion.
- Already-format1 saves retain both Human sidecars and nonhuman additions even when count remains native. They are not treated as fresh saves merely because the count is old.
- Unsupported format and malformed native inventory are rejected atomically. Staging tests verify that live state is untouched.
- Actual installed CA900 dispatch exercises lazy migration/publication for quantities0,1,255, including saturation and unsupported-format behavior. Native return/transaction semantics remain the inventory layer's responsibility; these tests check committed amounts and publication state.
- Installed normal/suspend entry branches are executed at13AA48/13AAD8 to their native success/failure continuations. Tests verify SP, LR, r4–r11, staging Human count and absence of pre-commit writes to live state. The subsequent BIOS commit/save-menu interaction is not simulated here.

## Count-exposed readers and writes

Count publication does not itself widen native templates or relocate AP. The following existing interior hooks remain required and are present in the current ability-core builder:

| Count-driven path | Storage protection |
| --- | --- |
| Command discovery C8F64 onward | Hook C8F76 reads through the AP accessor. |
| Typed usable/known lists CCFB8/CD0EC | Hooks CD072/CD19E redirect Human AP reads. The table iterations can reach new definitions without accessing inline Human stats. |
| Scripted AP loss12919C onward | Filter1291AC, read129224 and write129264 are hooked. |
| Ability theft matching/transfer/count |132E62,132FC6,132FF8 and133D30 hooks protect both owners. |
| Equipment removal/replacement and results | Existing reader/writer hooks remain necessary even where the loop is driven by teaching records rather than count. Publication does not replace them. |

Two additional count-driven routines, `132DDC` and `1340F8`, search relocated **ability definition records**, not AP bytes. Their loops remain byte-indexable through177 and do not need an AP-address shim. Their callers' subsequent AP operations still require the existing hooks.

The unhooked low-seven-bit AP read at620EC is in roster replacement prerequisite reconciliation61F54. It follows original prerequisite job first/last ranges, rather than unit+34; publishing a larger count does not newly expose it to Human extension bytes. It does, however, ignore appended Soldier/Gladiator lesson membership in that separate reconciliation path. Parent was notified of this design-integration limitation. The direct innate grantCA22C and Blue Mage writes likewise remain governed by their native lesson identities, not the expanded count; new job records currently have no nonzero free-innate index.

This is a bounded followup to `notes/ap-consumer-audit.md`, using native call scans, count-base candidates and concrete disassembly. It found no additional count-triggered raw Human AP write beyond already installed hooks. This is not a proof against every indirect access or a certification of expanded menu output capacities, battle effects, AI or all recruitment flows.

## Acceptance boundary

Behavioral count/import/migration evidence and the corrected C-stack boundary pass. Run this validator alongside the existing AP inline/writer/copy suites and retain separate real load/new-game and menu tests. Expanded counts are necessary infrastructure; they do not mean all ten new jobs, lesson lists, animations and effects are ready to enable.
