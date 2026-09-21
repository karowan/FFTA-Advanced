# Native battle lifecycle review

2026-09-14. Scope: existing native battle behavior with the expanded inventory/AP storage and published lesson counts. No engine edits; no new combat effects were invoked. All ROM/state/SRAM files are private artifacts under `build/expansion/probes/battle-lifecycle`.

## Accepted result

`scripts/test-battle-lifecycle-in-game.py` passes against frozen ability-core SHA1 `d505e1fff9babb8ef0c44504af3e11acd80236c8`. The previous `9b5eb534860cb7189f23decc13309ccbca4ddfcd` also passed the same interaction/suspend path; the final complete run regenerated the battle against the newer current artifact and additionally asserts every participating party member's published lesson count.

Default invocation first runs `create-battle-fixture.py` against the current ability-core ROM, then copies that exact frozen ROM and matching first-turn state into its own output directory. `--reuse-fixture` intentionally uses the existing matched battle-fixture state/ROM. The suspend persistence phase always destroys the emulator and cold-loads SRAM through the game's native Resume Battle UI; it never restores an emulator state for that phase.

The test assigns each of24 roster sidecars a unique34-byte AP pattern. Each AP byte has bit7 clear and is strictly below its actual Human lesson cost, read through native `CD480(1,index)` for indices144..177. Native costs range10..40. This prevents the fixture from mastering or enabling new, unimplemented abilities. Valid preference values0/1/2 cycle through all24 metadata slots. Existing gear, inventory, native abilities and stats are not edited. Non-Human/empty-slot Human sidecars are also checked for exact preservation; their AP is inert.

## Actual interaction and persistence evidence

- At Jona's first turn, open Action > Fight, target adjacent Montblanc and inspect the native18-damage/95-percent preview. Three B presses return to the original command menu. HP, all816 extra AP bytes and all24 preferences remain unchanged.
- Re-enter the same target, open the native Do it/Cancel confirmation, and confirm. Native Fight reduces Montblanc from43 to25 HP and awards Jona12 experience. No other roster HP, inventory or gear changes. This friendly target is used only in the disposable fixture to exercise native execution without modifying movement, equipment or accuracy inputs.
- Wait and confirm facing; native turn order advances to Colette. B exits her uncommitted command menu, then Start opens System. Up wraps to Save Now; two A presses advance its notice and confirmation, and the final A writes the native suspend SRAM. The rendered screen says Save complete.
- A fresh emulator receives only that suspended SRAM. The route is Saved Game > Resume Battle > slot > warning > confirmation; the final confirmation defaults to No, so Left then A selects Yes. The resumed image shows Colette's ordinary command menu. All816 AP bytes,24 preferences, inventory, gear, battle HP and Jona's12 experience are retained.
- Colette's native Action menu opens after cold load and cancels normally, proving the restored battle remains interactive.

Images for preview, cancellation, confirmation, execution, native Save complete, cold resume and resumed Action are saved and visually inspected. The reports additionally assert memory values; screenshots alone are not treated as proof of serialization.

## Published counts, actors and allocation

Every active-state sample enumerates12 native battle actors through `99CDC` on the live manager and proves six underlying pointers are exact canonical roster slots. For each participating unit, `unit+34` equals its expanded race count: Human178, Bangaa111, Nu Mou124, Viera118, Moogle116. These checks include both initial play and cold suspend load.

The battle heap remains `020159D0..0203F800`. First-turn free payload is78,868 bytes. Preview and confirmation reduce it to74,408; cancel/commit restore78,868, and the native snapshot owner root is zero again at each sampled UI boundary. Thus this flow does not retain its preview allocation. The separately regenerated full deployment fixture's minimum sampled free payload remains54,052. These figures describe this specific mission/flow, not a worst-case bound for every AI or action.

The reserved-region canary at `0203FF44..02040000` survives all active samples and the cold-load reconstruction. The compatibility view occupies `0203F800..0203FF30`; current20-byte owner metadata occupies `0203FF30..0203FF44`, so neither is incorrectly included in the canary. The test validates allocated/free block markers and bounds through the existing native heap walker.

## Limits

This closes the concrete first-turn native Fight preview/cancel/commit, turn advancement and native suspend/cold-load regression requested for the current count publication. It does not establish new job combat effects, every AP-mutating simulation, extended AI workloads, results awards, full mission completion, every battle terrain, or arbitrary suspend points. Direct copy/snapshot transaction tests remain necessary for AP mutations that this ordinary Fight does not perform.
