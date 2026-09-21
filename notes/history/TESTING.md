> Historical record, archived September 21, 2026. For current guidance, see [the repository overview](../../README.md). Paths in code examples are relative to the repository root.

# Fast testing without a campaign playthrough

## Deterministic expansion regression

Testing runs locally through scripts, without agents, model calls, or an
interactive game window. The declared sequence is in
`scripts/expansion-test-plan.json`. `Build Engine.ps1` builds the candidate and
then invokes that sequence. To test an already-built candidate:

```powershell
.\Test Expansion.ps1                    # All declared implemented-feature tests
.\Test Expansion.ps1 -Suite quin        # Recruitment and normal/suspend saves
.\Test Expansion.ps1 -Suite core        # Native components and storage checks
.\Test Expansion.ps1 -Suite battle      # Gameplay paths and their prerequisites
.\Test Expansion.ps1 -Suite fell        # Private Fell/Exposed component checks
.\Test Expansion.ps1 -Suite samurai     # Private Samurai native/gameplay checks
.\Test Expansion.ps1 -Only test-grace-in-game  # Named test and prerequisites
.\Test Expansion.ps1 -Suite full -List  # Inspect the commands without running
```

The runner executes the steps sequentially with fixed Python hashing and
assertions enabled. The individual game tests use scripted inputs, fixed or
bounded deterministic seed cases, explicit fixtures and native save/load paths.
It stops on failure or a declared time limit, retains each command's full log,
and writes JSON plus JUnit results under `build/expansion/test-runs`. The latest
report path is in that folder's `latest.json`. An OS lock prevents two runners
from changing shared fixtures simultaneously. Do not rebuild or edit the test
harness during a run: changes invalidate its overall result.

Each report records the tested ROM hash and source/harness fingerprints. Keep
the accepted report as evidence; select only affected tests during development,
then run the complete sequence on an assembled candidate. There is deliberately
no automatic pass cache yet: several older tests consume generated artifacts,
so a ROM hash alone cannot establish that every test input is unchanged.

The full runner currently schedules **91 steps** for implemented features,
including fixture preparation and assembled Fell/Exposed/status-display checks.
The separate private Fell suite has nine steps. Passing either suite does not
prove that all129 approved lessons are implemented, nor that campaign pacing
is balanced. Private results identify their own ROM and remain separate from
assembled-build acceptance.
The private Samurai suite covers four strikes, Centered/Exposed composition,
Dispel and equipment changes, native laws, fixed-input gameplay and immediate
Counter timing. It does not enable the remaining Samurai kit in the main ROM.
Some existing component tests use retained diagnostic inputs in this workspace;
a fresh-machine fixture bootstrap remains part of final reproducibility work.

The runner itself has deterministic checks in `scripts/test-test-runner.py` for
dependency selection, real child-process success/failure, fail-fast behavior,
timeouts, and rejecting input changes during a run.

Battle fixture creation now waits for the actual native command menu before
publishing a ready state. It checks both bright text strokes and dark outlines,
without pressing buttons, and fails at a fixed frame limit. This avoids sending
the first combat input during an intro when a larger engine changes timing.
The report records the extra frames and the observation anchor's hash.

We will implement the expansion end to end while extending focused tests alongside it. A full campaign playthrough is reserved for progression, pacing and balance once the expansion is assembled. It is not a prerequisite for starting each job or feature.

## Working test lab

Run **Build Test Lab.ps1** to generate a disposable starting save and exercise the actual game in mGBA. The first successful complete run took **9.55 seconds** on this computer. Timings will vary.

The setup process skips the opening in a temporary setup-only ROM, creates the original starting clan, places Sprohm and saves through the game's own save menu. It then starts the **normal development ROM** from scratch and loads that native save through Continue → Load. The setup-only ROM is not the ROM used for the feature tests or the user-facing lab.

The lab currently verifies:

| Scenario | Evidence |
|---|---|
| Load a prepared clan without replaying the intro | All 24 roster records restored in the normal development ROM. |
| Sort two ordinary units | Actual Select-button menu interaction; all bytes of both units preserved; every other slot unchanged. |
| Keep story characters fixed | Actual menu rejects selecting Marche and Montblanc for sorting. |
| Save and reload after sorting | Native save menu, emulator shutdown, fresh boot, Continue → Load; all 24 roster records match the expected result. |
| Pub entry and mission selection | Actual pub interaction, Missions shown first, first option opens Herb Picking's mission list. Screenshots visually reviewed on September 14, 2026; menu text is not asserted by OCR. |

The seed is before any completed missions. This is not a postgame save or an all-content unlock.

The report is `build/test-lab/report.json`; screenshots are in `build/test-lab/screenshots`. The existing 4,372 routine cases and ROM/patch checks remain available through **Build Foundation.ps1**. They complement these in-game tests.

## Opening or resetting the lab

Double-click **Play Test Lab.cmd**, then choose **Continue → Load → File No. 1**. You start with the clan on the world map, with access to the party and pub. Loading this save requires no intro playthrough.

The lab's ROM is byte-identical to the current foundation build, but lives at `roms/play/test-lab/FFTA_test_lab.gba` with its own `FFTA_test_lab.sav`. The vanilla and ordinary development saves are protected during lab generation and checked for changes afterward.

Re-running **Build Test Lab.ps1** resets the lab to its generated seed. An existing lab save is copied to `build/test-lab/save-backups` before replacement. Close the lab window before regenerating it so the emulator does not later overwrite the reset save with an old in-memory copy.

The script uses the locally installed tools and bundled Python runtime. It does not launch a visible emulator or install a background service. If asking Codex to open the lab interactively, follow the standalone desktop launch instructions in `AGENTS.md`.

## How this supports the full expansion

For each new job, build one complete path: obtain its teaching equipment, select the job, use its action and cross-class skills, earn AP, master a lesson, save, and reload. Add a prepared scenario that exercises that path immediately. Chemist remains the first implementation target.

Expand the lab with disposable scenarios rather than ask for hours of setup:

- **Combat scenarios:** specific allied jobs, equipment, mastered/unmastered lessons, MP/HP, enemies and status effects. Cover action resolution, reactions, support combinations, targeting and AI.
- **Progression boundaries:** saves immediately before and after each actual story gate, checking stock and job access. Player-facing #005/#011/#017 translate to internal mission records 7/13/19.
- **Recovery scenarios:** the affected quest available or completed, required items present/missing, full inventory, recruit absent/present, and repeated claims.
- **Dispatch scenarios:** a known unit assigned to a known mission, then roster sorting, completion and native save/reload.
- **Persistence scenarios:** save newly learned AP, equipment and class combinations; cold-load the current ROM and verify the restored data.

These additional scenarios are not implemented yet. The current lab proves a practical automated setup/save/menu route; it does not establish battle or postgame coverage.

Prepared scenarios must distinguish setup changes from the behavior under test. Set only verified fields, record the seed and ROM hashes, and execute the actual game code for the tested action. Do not enable every story flag indiscriminately or substitute emulator save-state replay for testing the game's save system. Emulator snapshots are useful for retrying a case on one build; regenerate them when code or data layouts change.

## Development gate

Continue implementing complete features with the fast checks already available. Extend the lab when a feature needs additional coverage. Fix failures in the feature being added, but do not block all job implementation on an exhaustive campaign audit. Track untested cases explicitly in the report.

Once all approved jobs, weapons and foundation features are integrated, use a full playthrough to judge the things isolated scenarios cannot establish: progression flow, economy, encounter variety, difficulty and whether the class combinations are enjoyable.


The runner also fingerprints generated compiler `.h`/`.inc` inputs, content
metadata, the clean ROM and the early-town fixture SRAM. Changing those inputs
during a run fails its immutability check, just like source or engine changes.
Private Samurai runs report their exact ROM in their individual logs; the
runner's top-level ROM field identifies the accepted base used to build them.
