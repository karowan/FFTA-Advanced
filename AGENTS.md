# FFTA project instructions

## Documentation

- Keep reusable procedures documented in `PARALLEL-IMPLEMENTATION.md` and
  update them when the workflow changes.
- Keep this file limited to stable project instructions. Record implementation
  assignments, current progress, test evidence and handoff checkpoints in
  separate project documents, not in `AGENTS.md`.
- Commit source documentation explaining how to reproduce the work; keep
  private binaries and raw generated logs ignored.

## Testing

- Run tests through deterministic scripts. Do not use agents to play the game,
  drive test inputs interactively, monitor tests, or generate one-off fixtures.
- Implementation agents may author and invoke deterministic test plans
  in their own worktrees and fix failures. No separate testing agents. Root owns
  combined regression and merge acceptance.
- Default to substantial implementation sweeps with compilation/static checks,
  or narrowly targeted runtime tests of the behavior being changed. Localized
  tests are normal verification, not limited to implementation blockers.
  Group related edits and fixes before testing; avoid edit/test cycles for
  every small change and repeated fixture creation for each lesson.
- Before a runtime run, identify the affected behavior, exact test IDs and why
  those checks are needed. Prefer `-Only` plus required prerequisites over broad
  suites. Include direct consumers and concrete cross-class interactions.
- Do not run the full integration suite after each small batch or commit.
  Reserve it for a very substantial completed milestone, final assembled
  acceptance, or a documented widespread regression that cannot be bounded by
  targeted checks. A changed ROM hash or shared source file alone is not a
  reason. Record the full-run justification in the implementation checkpoint.
- Long battle playback, cold saves and campaign checks run only when the
  changed behavior/lifetime makes them relevant, or at those major gates.
  After failures, fix related issues together and rerun affected checks only;
  broaden coverage if a failure supplies evidence of wider impact.
- Documentation-only changes require document/link/format validation and the
  Git asset guard, not game builds or runtime tests.
- Use `Test Expansion.ps1` and its declared test plan for runtime tests.
- Preserve each run's ROM hash, fixed input scenarios, complete logs and pass/fail
  report. Reuse existing evidence when its tested inputs remain applicable;
  do not repeatedly run passed checks without changes or unresolved concerns.
- A partial suite or allocated lesson record does not prove expansion completion.
  The primary agent performs the final implementation review after automated
  checks.

## Artwork

- Use the game's existing native palettes. Adapt and review artwork inside
  those color constraints; do not introduce custom palette banks, runtime
  ownership/remapping, or palette allocation systems. Palette choices are
  native class/side properties, not race-wide restrictions. Approve native-size
  color conversions before propagating them across animation frames.
- Match the original jobs' bright colors and clear contrast. Preserve readable
  faces, dark silhouettes and distinct costume colors at native size; avoid
  muddy automatic color substitutions. Use palette-constrained generated
  revisions when direct conversion loses those distinctions.
- Use image-generation models for artwork creation and visual revisions.
  The built-in imagegen tool is the default; external provider APIs are allowed
  when explicitly requested by the user. Keep credentials encrypted locally
  and outside Git; preserve exact prompts, models, settings and source images.
  Do not draw replacement art manually, in a pixel editor, or as coded pixel
  patterns. Code is for technical conversion, native import and verification.
  This supersedes the earlier preference for desktop drawing.
- Generate new class character artwork from blank designs. Original FFTA sprites
  are references for style, proportions, anatomy and animation, not character
  bases to recolor or decorate. Each new class needs a distinct costume and
  silhouette appropriate to its race and role.
- Keep construction drafts, technical import proofs and accepted production
  artwork distinct. Prove each native graphics consumer separately; a menu icon
  or PNG sheet does not establish actor, portrait, weapon or effect integration.
- Match native lettering proportions, spacing and contrast. Do not stretch a
  tiny font to fill job labels. Inspect the actual rendered UI at native scale
  and keep placeholder/donor artwork explicitly unfinished until replaced.

## Git and parallel implementation

- Do not start additional subagents or councils without a new explicit user
  request. Existing agents may finish their assigned work; the primary agent
  handles all subsequent implementation, integration, testing and final review.
- Never add ROMs, saves, memory dumps, local tools or generated builds to Git.
  Run `scripts/check-git-content.py` against the index before every commit.
  Never force-add ignored assets. No remote or publication is authorized.
- Each implementation agent works only inside its assigned `.worktrees/<job>`
  checkout, with an explicit working directory for shell commands. Do not edit
  the primary checkout or another agent's worktree. Each owns its own branch.
- Read `PARALLEL-IMPLEMENTATION.md` and the assigned `scripts/jobs/<job>/` plan.
  Local ROM/compiler/fixture copies remain ignored; do not replace them with
  links to writable outputs in the primary checkout.
- Complete the job's approved behavior end to end, including native UI, AP,
  equipment, battle execution, laws, AI and save/copy lifecycles. Report actual
  gaps; allocated records and passing scaffold checks do not complete a job.
- Shared hook or save-schema changes must be recorded for root integration.
  Never silently relocate another job's IDs, ROM reservation or state.

## Launching the game

- When the user asks to launch FFTA or mGBA, open it as a standalone, visible Windows desktop application outside Codex. The user's phrase "a thread outside Codex" means an independent desktop process, not a new Codex conversation.
- Do not launch the game hidden, inside an embedded Codex panel, or only on an isolated automation desktop. If the normal sandbox launch produces a process the user cannot see, use the approved external/interactive desktop launch path.
- Prefer bringing the correct existing game window forward to opening duplicate instances. Do not close a running game or discard its progress without authorization.
- Verify the visible window where desktop tools permit; a process ID alone does not establish that the user can see it. If visibility cannot be verified, say so rather than claiming it is visible.
- Verified on this machine: a sandboxed `Start-Process` created an mGBA window that was absent from the interactive desktop's window list. Running `Start-Process` through `exec_command` with `sandbox_permissions: "require_escalated"` and `-WindowStyle Normal` opened the game on the user's desktop. Follow the tool approval mechanism for that launch, then select the returned mGBA window with Computer Use and bring it forward. Do not repeat the sandbox-only launch when the user reports this symptom.
- Keep the original and development games distinct: `Play FFTA.cmd` opens vanilla; `Play Development Build.cmd` opens the experimental foundation. Preserve their separate ROM and save paths.
- `Play Expansion.cmd` uses the independently packaged expansion ROM and explicitly overrides mGBA save, state and screenshot paths to `saves/expansion-v0.7-engineering/`. `Play Previous Expansion.cmd` retains the previous release and its `saves/expansion-v0.7/` storage. Preserve that separation. Use the launcher's `-ValidateOnly` mode for verification without opening a game; never import player saves as part of packaging.
