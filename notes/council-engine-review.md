# Engine council review: persistence components

September 14, 2026. Read-only implementation review; only this report was written. Scope: `src/engine/persistent.c`, `src/engine/load-hooks.s`, `scripts/generate-expansion-registry.mjs`, `Build Engine.ps1`, and their immediate runtime/probe dependencies. Reviewed engine binary SHA1: `1f25f029bb47be5c205a8b55e5ee50f64b60ed88`. This is a component review, not approval of a playable expansion.

## Decision

The current persistence components have no remaining demonstrated blocker within their stated scope. One rejection-lifecycle defect found during review was corrected by moving migration before the native commit. The registry and persistent allocation fit the current approved counts. Inventory consumers, AP consumers and unit lifecycle hooks remain necessary before these components can be installed in a playable build.

## Corrected finding: reject before replacing live state

The first load-hook version migrated after the native CpuSet copied the save into live EWRAM. A conversion failure then reached the native error menu after live state had already been replaced. A non-mutating migration function alone did not make rejection atomic.

The reviewed current version hooks ROM `0x13AA48` and `0x13AAD8`, migrates the staging block in r5, and commits only after success. `load-hooks.s:24-29` and `:52-57` reproduce the four displaced setup instructions: r4/r1 become `0x02000000`, r0 becomes staging, and r2 becomes `0x1E54` halfwords. They resume at `0x0813AA50` and `0x0813AAE0`, respectively. Both call BIOS CpuSet through `0x0814186C`, copying `0x3CA8` bytes.

Failure targets are correct: `0x0813AA30` plays the native error sound and selects state `0x19`; `0x0813AACA` selects state `0x1A`. Both join `0x13ADD8`, which stores the state through r7. The shim preserves r7 and the remaining live callee registers. Its r3 clobber is harmless at these specific continuations. Generic loader `0x13B480` remains untouched, so merely previewing a save does not migrate it.

Independent execution of the compiled current hooks covered both success and rejection for both load branches, with entry SP congruent to both 0 and 4 modulo 8. All eight cases preserved SP and r6/r7, reached the expected native continuation, kept live state byte-identical before commit, preserved staging on rejection, and produced the expected CpuSet arguments on success. This exercises the current binary; it does not replace real suspend-menu testing.

## New-game migration timing

Native new-game routine `0x977C` clears `0x3CA8` state bytes at `0x9780..0x9788` before constructing units and before the initial inventory grants. The size literal is at `0x984C`. The initial grant sequence at `0x9812`, `0x981A`, `0x9822`, `0x982A` calls `0xCA900` with `(362,10)`, `(367,4)`, `(373,4)`, `(375,2)`.

Therefore `ffta_native_give_item`'s lazy migration can initialize a clean new-game inventory on the first grant, after the clearing operation. The persistent version marker makes later grants idempotent. Independently executed all four native ID/quantity pairs against the compiled wrapper on a zeroed state: counts, marker and zeroed 816-byte AP extension were correct. A real emulator new-game run with the complete inventory port is still required; the current storage-only probe installs load hooks, not CA900.

## Allocation and ABI checks

- The 512-byte count inventory occupies `[0x1940,0x1B40)`. The 24-by-34 AP extension occupies `[0x1B40,0x1E70)`. Metadata occupies `[0x1E70,0x1F1C)`. Their sum is exactly the original `0x5DC` inventory bytes. Potion preferences at metadata+16 through +39 fit without overlapping the format header or adjacent names.
- Migration validates legacy nonzero IDs, counts, equipped counts and duplicate IDs before writing. The 48-byte seen bitmap covers IDs through 375. The magic cannot occur in a valid legacy inventory at that location because its encoded item IDs exceed 375. Current-format migration leaves the extension intact.
- Human new indices `0x90..0xB1` map to 34 extension bytes per roster slot. Reserved indices `0x8E/0x8F` are rejected. Current other-race totals 111/124/118/116 stay below the existing AP capacity. This helper intentionally rejects non-roster pointers rather than aliasing them into another unit's extension.
- Registry name-ID ranges use separate native tables: item/job names use `0x526680` (753 native entries), while ability names use `0x5567F0` (767 native entries). Their numeric overlap is not a collision. Current native type values Action=1, Reaction=2, Support=3, Combo=5 agree with the native race-ability format.
- The linker rejects mutable data and BSS. The reviewed build links the required division support, and the existing 55,808-case report matches the reviewed engine hash. Build Engine currently builds/tests the component binary; it does not claim to build or validate the final expansion ROM.

## Required integration evidence

1. Finish the legacy inventory reader/writer port before installing the count format in a playable ROM. The storage-only emulator result is appropriately limited to load/save menus.
2. Connect every Human AP reader/writer and all relevant constructors, recruitment/copy, sorting, departure and temporary battle-unit paths. The correct standalone address/swap/clear helpers do not themselves provide those hooks.
3. Exercise a real suspend save and cold resume, plus a rejected format from both gameplay-load routes and retrying a valid slot afterward. Ordinary native save/cold-load has evidence; suspend currently has compiled-hook evidence only.
4. Add build-time assertions or generated constants for the duplicated race totals/storage sizes when the registry starts changing. Current hard-coded C totals agree with generated data and are checked by the existing address tests; there is no present mismatch.

No implementation files were changed by this review. Earlier failed exploratory execution used the old post-copy calling setup while the parent was replacing the hooks; the final eight-case execution used the current staging-pointer contract and passed.
