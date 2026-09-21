# Tomahawk projectile and help review

2026-09-14. Council owns `scripts/probe-tomahawk-animation.py`, `scripts/test-projectile-icons.py`, this note, and the two authorized equipment icon call-site additions. No user saves or original frozen evidence were changed.

## Visual comparison and decision

Original frozen combat `e967ee06310e0358348298d574c06cc956f8578f` uses Nighthawk's animation **144 / 0x90**. The native global action is **147**, not144; global144 is Swallowtail. Native Throw is global action148, animation **145 / 0x91**.

Nighthawk has an ordinary weapon windup, a darkened scene, a violet streak arriving from above, and a large purple slash on the target. It reads clearly as a ranged magical strike, but no recognizable axe rotates through the air. The uncorrected Throw variant instead sends a large pale-purple flat rectangular object directly from actor toward target, followed by a yellow-white impact star. That shape was a real icon-namespace bug, not evidence that all native projectile animations look alike.

After supplying native icon donor52 only to the diagnostic renderer, Throw shows a small recognizable steel blade traveling toward the target. This is preferable for the current physical Tomahawk presentation. It is **Barong blade artwork**, consistent with the expansion's existing Axe visual/icon donor; it is not bespoke axe artwork or a claim of a visibly rotating axe.

Diagnostic images and report: `build/expansion/probes/tomahawk-animation/e967ee06310e0358348298d574c06cc956f8578f/`. Compare `nighthawk/projectile.png`, `throw/projectile.png`, `throw-primary-454/frame-224.png`, and `throw-icon-donor-52/frame-224.png`. Four variants change only action425 animation field at ROM `010323B8`, plus the two explicitly labeled diagnostic variants replacing the four-byte item lookup call at `FE41A` with a constant454 or52. Gameplay descriptors, effect callbacks, MP cost, equipment, inventory and saved fixture are unchanged.

All four actual native replays produce18 damage,4MP paid once,8EXP on seed1 and a miss with4MP paid once/0EXP on seed0. Inventory, extra AP, preferences, equipped gear and reserved guard remain byte-identical. Actor/target coordinates stay `[2,13]` / `[5,14]`; native Wait/facing after the miss advances to actor02000188. The baseline parent lifecycle additionally covers suspend/cold Resume Battle. Diagnostic variants do not certify fresh-build suspend persistence.

## Exact selector and icon defect

Animation table `083947D8` row `(145-1)*8` points to callback **080FE2E9**. Throw's callback calls `DD488` at `FE41A`; `DD488` calls the identity accessor `A880C` and returns the action context's halfword at+0x12. `FE420` stores that item ID into projectile descriptor+0x14. `FDFEC..FDFEE` transfers it into projectile state; `FE078` calls `D5FD8` with the same ID.

An actual mGBA breakpoint at `FE41E`, immediately after the native lookup, returns **r0=454** for this Tomahawk fixture. Saved PC is080FE420 because the Thumb pipeline is advanced. This disproves the earlier item0/default hypothesis. Forcing454 produces the same incorrect icon. No additional item selector/helper is needed: the original action context already carries the equipped axe.

`D5FD8` calls native palette getter `CB99C` at **D601A**. Its spawned graphics task `D65D4` calls native icon decoder `CB980` at **D6614**. Those two equipment projectile call sites were absent from `equipment.c`'s scoped namespace allowlist, so item454 reached the native overlapping quest-icon namespace. Both sites now use the existing item-to-icon donor map. The ID stays454 everywhere outside icon lookup, and native Throw's selected item remains untouched. Global icon APIs and mixed reward popup thresholds remain unchanged.

Compiled acceptance ROM **5b90d5fb623457405d96948e33df623b342da14c**, engine **5959a34892515efcceab5e88d49f79163341caad**, includes only the two additional icon routes and parent-selected Tomahawk animation145 for this change. `test-projectile-icons.py` passes **3,856** actual native decoder/palette/ABI checks at both stack residues: all original IDs0..375 preserve pixels and palettes, all 85 additions map to their approved donors, and generic namespace0..502 remains exact. `test-reward-popup.py` additionally passes all502 native popup branches and68 source decoders, including every overlapping quest ID376..502. Reports and immutable input snapshots are under `projectile-icons` and `reward-popup`.

Fresh-build acceptance now passes on the same5b90 ROM: the parent recreated the battle from native SRAM, then completed hit/miss,4MP once, cancel/reopen, native turn advance, suspend and cold Resume Battle with inventory/AP/preferences/gear/guard preserved. This council inspected that filmstrip and independently replayed its own fresh confirmation state at four-frame sampling using `probe-tomahawk-projectile-frames.py`. Frame224..232 shows the steel blade moving from actor toward target; frame240 begins the yellow-white impact. The purple rectangle is absent. The dense strip is `build/expansion/probes/tomahawk-projectile-frames/5b90d5fb623457405d96948e33df623b342da14c/projectile.png`; frame228 is a clear full-size comparison. Accept the mapped Throw animation within this scope, retaining the explicit Barong-art limitation.

## Cost display and concise help

The existing actual `tomahawk-menu.png` already displays **4** in the MP column next to Tomahawk. Actor MP16 becomes12 only upon commitment; preview/cancel does not spend it. Cost rendering needs no fix. Do not confuse racial/command help index0 with action record+22: the latter creates the independent top preview banner, and should stay0 for these abilities.

Suggested help, preserving the approved effects:

- **Chop:** “A strong axe strike against an adjacent foe.” Optional numeric detail: “110% weapon power. 0 MP.”
- **Tomahawk:** “Hurl your axe up to 4 tiles along a clear path. The axe stays equipped.” Optional numeric detail: “90% weapon power. 4 MP.”
- **Combo template:** “A combo technique. Requires [weapon].” Use the already approved weapon requirements: Samurai katana; Dark Knight sword/knight sword/greatsword; Viking axe; Geomancer rod/staff; Chemist knife/staff; Bard instrument; Dancer knife/rapier; Mystic Knight rapier/saber. Native JP and chain rules remain in force; do not promise automatic participation, fixed JP spending, or new side effects.

These are content recommendations, not installed strings. Wrap with the existing help encoder and verify actual rendered width before installation. Keep full approved names in help; do not restore long list labels that overflow narrow menus.
