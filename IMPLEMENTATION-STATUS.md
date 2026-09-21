> Historical foundation status; current scope is in HANDOFF.md. See [the current overview](README.md) and [release workflow](MOD-RELEASE.md).

# Implementation status

**Historical foundation status.** For the current expansion, read
[the maintained implementation checklist](IMPLEMENTATION-CHECKLIST.md) and
[latest tested checkpoints](IMPLEMENTATION-STATE.md). The pending lists below
describe older builds and must not be treated as the current backlog.

September 14, 2026 â€” **foundation-dev-1, experimental**.

## Current expansion engineering build

Accepted assembled ROM: `ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`.
It contains ten enabled new actions, two supports and eight combos, plus the
job/equipment/AP/save foundation. All91 declared assembled regression steps
have passing deterministic evidence across resumed runs on that exact ROM.
`build/expansion/ba1c-regression-coverage.json` reconciles the evidence; the
accepted ROM, engine, sources and scripts are frozen under
`build/expansion/accepted/ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`.

This does **not** complete the approved129 lessons. Creating a job, item or
lesson record does not mean its battle effect is implemented. All testing uses
deterministic local scripts and retained reports. Per the user's newer worktree
instruction, implementation agents may invoke those scripts in their isolated
checkouts; there are no separate testing agents. Final council review is ahead.

Latest private Samurai candidate: `b6daf87deb52ad84d72021e7bc6ea359ebd8bce1`, based on
ba1c. It implements all nine Samurai actions, including Centered, Murasame's
healing, Kiyomori's protection, Wind Draw's line, Moon Blossom's Regen, and
Higanbana's initial hit and two scheduled Wound pulses. It also adds the Wound
status icon, all nine action descriptions and a dedicated harmful-status law
check. Poise now has a partial defensive implementation, action-start snapshots,
copy-lifetime handling and native help. Its native arithmetic/ownership checks,
four actual Counter timing cases and native cold-save persistence pass. Broader
category, law/AI and gameplay acceptance remain unfinished. The newest revision
fixes Poise discounting redirected MP, preserves the native executor's resolved
reaction choice, and passes native HP/MP and status-restriction matrices. Its
35-step Samurai regression now has passing evidence across two resumed runs,
including actual Counter confirmation. A Counter still bypasses Damage-to-MP,
and Poise correctly reduces its35HP damage to26 whether MP is empty or remains.
The evidence and exact source snapshot are reconciled by
`build/expansion/checkpoint-poise-mp.py`. This covers implemented features only.
That c8e3 checkpoint remains frozen. The newer b6da candidate adds Blade Ward's
primary-katana defense, native Reflex status restrictions, whole-action
snapshots and Poise/Exposed composition. Native formula and full-executor checks
pass; actual battle, cold save/resume, and Wound exclusion tests also pass in
`20260915T033027.038366Z` and `20260915T033607.581604Z`. This newer candidate
has focused evidence, not the c8e3 checkpoint's complete regression. See
`notes/blade-ward-implementation-review.md` for that feature's scope.
Composure, Counter Draw and the rest of the expansion remain
unfinished. This private build has not replaced the player game. See
`notes/poise-implementation-review.md` for exact scope and current test runs.

The c8b9 Judge integration now passes: a successful Wound under the harmful-status
law receives a yellow card; a miss and a specific Poison-law control do not.
Native turn return and cold-save card persistence pass in
`20260915T020354.562671Z`. Composure's native Move/cancel/turn-reset timing is
recorded in `notes/composure-native-timing.md`; this investigation does not
enable the support yet.

The previous Higanbana checkpoint `d7d6e31967d9a4627c08542d96f059bb499fb03e`
has frozen focused native execution, lifecycle, actual battle and cold-save
proof. The earlier bf941 display passes native renderer preservation, exact
graphics, coexistence, expiry and cold-save tests. All25 declared private Samurai steps now pass across two resumed runs with
identical inputs. This includes native object lookup and explicit starting
formations. The reconciliation is `build/expansion/samurai-bf941-regression-coverage.json`.
Exact results and remaining reference/law/help work are recorded in
`notes/samurai-wound-review.md`. See `notes/samurai-help-reference-review.md`
for the latest help/reference/law evidence and remaining integration limits.

The main source tree contains newer private work than the accepted main engine.
Use the frozen accepted snapshot to reproduce ba1c; current source files alone
must not be represented as that accepted build. Earlier checkpoint summaries
are retained in `notes/engineering-checkpoint-history.md`.

The player launcher still opens the foundation described below. Separate test
ROMs under `build/expansion/probes` now contain the ten additional racial jobs,
85 teaching weapons and permanent stock gates, expanded AP storage, equipment
and command menus, and preserved native battle/save lifecycles. These test ROMs
have not replaced the player's game or save.

The full expansion still requires the remaining action and support/reaction
implementations, cross-class synergies, law handling, remaining vanilla+
safeguards, final assembled regression, council review and packaging.
Continuation details are in [expansion engineering](notes/expansion-engineering.md)
and the individual implementation notes. The following section describes only
the older foundation that the player launcher currently opens.

## Foundation launcher build

A separate ROM and BPS patch now exist. This is a partial implementation of the approved vanilla+ foundation, not the complete package or job expansion. The original playing ROM and save have not been edited. The approved version 0.7 design remains unchanged.

**Testing update:** [The fast test lab](TESTING.md) now creates and loads a native starting save automatically, tests actual roster sorting and native save/reload, and reaches the pub mission list. Its first complete run took 9.55 seconds. We will extend these scenarios alongside end-to-end implementation rather than require a campaign playthrough before adding jobs.

## What is in this build

| Feature | Installed change | Verification still needed |
|---|---|---|
| Wyrmstone safeguard | A Dragon's Aid returns Wyrmstone in its second reward slot. Its first random equipment reward remains. | Complete the quest, repeat it, and test a full mission-item inventory. |
| Elda's Cup safeguard | Caravan Guard returns Elda's Cup in its second reward slot. Caravan Musk remains the first reward. | Complete the quest, repeat it, and test a full mission-item inventory. |
| Recruit retry | Mythril Rush uses Missing Prof.'s native Quin recruitment rule. Its existing prerequisites and repeatability remain. | Failed chance, success, already-recruited exclusion, permanent-death policy, save/reload. |
| Goblin encounter | Tricky Spirits replaces its Red Cap with a Goblin carrying Goblin Punch. | Encounter availability throughout the campaign; enemy action use and Blue Magic learning. |
| Thundrake encounter | Wild Monsters replaces its Icedrake with a Thundrake carrying Dragon Force and Bolt Breath, with native Reflex/Geomancy. | Encounter availability, AI action use and normal learning/control requirements. |
| Clan sorting | Select chooses two units to exchange positions. Marche and Montblanc remain fixed. Actual menu swaps and a native save/cold-load now pass. | Dispatch references, unique events, deployment, full roster layouts and broader campaign cases. |
| Morpher appearance | All nine morph families use their monster visual fields. The hook was adapted to preserve ordinary job-stat queries. | Movement, attacks, casting, damage, defeat, battle exit, and special-character behavior in actual battles. |
| Pub menu | Missions, Rumors, Quit Mission, Leave. Actual first-option entry opens the mission list. | Full interaction with the remaining options and later campaign cases. |

The two refunds each replace **one random equipment reward**; they are not additional third rewards. Encounter edits preserve enemy count, positions, level fields, equipment and unrelated template flags. They do not yet establish complete coverage of all monster abilities.

## What is not in it yet

- The remaining mission-item, monster-ability and secret-recruit completeness audits.
- Late-game vanilla equipment recovery missions, including the audited candidates Zeus' Mace, Materia Blade, Dark Gear and Genji Armor.
- The ten racial implementations of our eight new job concepts, their custom effects, the Soldier/Gladiator axe additions, and their AP/save/menu integration.
- The 85 new teaching weapons and their shops/story unlocks.
- Expanded lesson/equipment displays.

The full design still contains 129 approved lessons. None of those new lessons is playable in foundation-dev-1. No vanilla job has been renamed or replaced as a substitute.

## Trying the development build

**Play Development Build.cmd** opens `build/foundation/FFTA_vanillaplus_dev.gba` in the installed mGBA. Its distinct filename and directory separate its default saves from the vanilla game. Use a disposable new save for testing; main-playthrough readiness and existing-save compatibility are not established. If you have changed mGBA's save-directory setting, check where it writes saves.

**Play FFTA.cmd** continues to open the original game.

The patch is `patches/development/FFTA_foundation_dev1.bps`. It applies to the clean US ROM with SHA-1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`. It is a development artifact for this partial build, not a patch stack to apply over other mods.

## Checks completed

- **3,792 Thumb routine cases:** 70 original jobs Ã— 48 stat selectors, plus nine morph families Ã— 48 selectors. Checked returned values, stack balance, preserved registers and unit-data preservation. Only four intended visual selectors change while morphed.
- **580 menu routine cases:** all 576 pairs of roster selections plus the four pub-option routes. Unit swaps preserve every byte of each unit record and keep Marche/Montblanc fixed. Drawing/audio calls are stubbed, and ARM7's legacy BL instruction is explicitly emulated in this test.
- **Actual mGBA smoke check:** title and initial snowball-story scene match the clean ROM pixel for pixel. Emulator save-state replay is deterministic. This is not a test of the game's save menu or a completed battle.
- **Actual mGBA test lab:** a native prepared save loads in the normal ROM; the party menu rejects sorting Marche/Montblanc and correctly swaps two generics; all 24 roster records survive native saving and a fresh emulator boot/load. Pub and first-option mission-list screenshots have been visually checked. No complete battle is covered yet.
- **ROM boundaries:** only 111 bytes in the original 16 MiB differ, all within reviewed hook/data ranges. Vanilla job, ability and equipment tables remain byte-identical. Added code lives after the original ROM, inside a 32 MiB output.
- **Patch verification:** applying the BPS back to the clean ROM produces the exact development output; a corrupted base ROM is rejected.
- Existing validators still cover the unchanged 129-lesson design and 85-item acquisition plan. These validate documents, not installed gameplay.

Reports are in `build/reports`. The exact ROM edits, original values and upstream engine revision are in `build/foundation/manifest.json`.

## Rebuilding

Run `./Build Foundation.ps1` in PowerShell from this project. It rebuilds from the hash-checked clean ROM, runs the design/data/routine/emulator checks, then creates the BPS. It overwrites generated development ROM/source/report files, not vanilla ROMs or saves. A failed check stops packaging.

The script uses the bundled Python runtime on this computer; a different interpreter can be supplied with `-Python <path>`. Required local dependencies are already installed under `tools`: Event Assembler/ColorzCore, the engine source, mGBA's test core, and the Unicorn/Capstone libraries. No service or startup task is required.

For exact integration findings and the remaining work, see [engineering notes](notes/foundation-engineering.md). The [approved package](VANILLA-PLUS-PACKAGE.md) remains the scope authority.
