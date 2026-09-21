# Combined job image

The primary agent owns all further implementation and review. The three
implementation handoffs are merged; no agents remain assigned.

`scripts/build-integrated-jobs.py` builds one private Samurai/Dark Knight/
Viking/Chemist image from the same shared-state base. It copies only declared
disjoint module reservations, then assigns one owner to every shared native
hook. It creates common action, descriptor, application and mask banks;
composes providers and damage factors; chains lifecycle consumers exactly once;
and allocates Viking then Dark Knight help against the preceding help table.
It does not overlay overlapping whole-ROM patches.

The integrated code/table reservation is `0x11E0000..0x11FFFFF`, declared in
`shared-job-allocations.json`. Compiled imports use explicit Thumb veneers.
Native reaction queue entry is installed directly because its native ABI
preserves registers beyond the ordinary C calling convention.

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite combined`
for the assembled suite. The plan builds dependencies and prepares a headless
battle/executor once per exact image hash. `run-integrated-check.py` explicitly
selects that image for the original job scenarios; ordinary isolated job checks
retain their default candidate. No player ROM, save or game window is used.

The runner collects independent failures in one pass, skips dependent checks
after a prerequisite fails, and retains all logs. Source fingerprints must stay
unchanged during a run. Group corrections before rerunning affected checks.

Native differential checks compare all original action outputs, including RAM
and RNG. Two context pointers may be canonicalized only after verifying the
same original table index/interior offset and identical pointed-to bytes:
descriptor at `0x0200F420` and action vector at `0x0200F41C`. No result, resource,
unit, ledger or other scratch field is excluded.

## First assembled evidence

Candidate `ec87e2d3563efe901fab64215de8d973f70ac143` uses common base
`e38fd42b6b606578d97eef5f97019a65d8222ac9`.

- `20260915T063504.761531Z`: 26 steps, 23 passed, three harness failures;
  source inputs unchanged. All original native actions and accepted Samurai
  checks passed, as did the listed Chemist, Viking and Dark Knight subsets.
- `20260915T063732.415525Z`: all 12 selected dependency/check steps passed on
  the same candidate after correcting those three harness assumptions.
  Viking's native control now edits its own action table, its raw physical
  control removes the combined finalizer, and Desperation checks HP price at
  the actual payment boundary rather than after possible spell self-damage.

These reports jointly cover the declared initial suite; they do not establish
full expansion acceptance. In particular, cross-job behavior needs dedicated
checks beyond running each job's individual scenarios on the assembled image.

The next sweep adds explicit owned Blade Wound/Exposed harmful tags to the
combined snapshot provider, so Opportunist benefits on later attacks while
remaining frozen for the current hit. Candidate
`b62e0cb9ce88eaef8a0a125cf29a0c07beffba66` passed all 26 build/gameplay steps in
`20260915T064633.898817Z`, including `test-integrated-synergies.py`. That report
is correctly failed overall: the independent runner self-test encountered a
Windows access denial while atomically replacing its own temporary report.
Bounded retry now preserves the old complete report and still raises persistent
or unrelated permission errors. All nine runner self-tests pass in
`20260915T064835.026455Z`; that runner-only correction changes no game bytes.

Cross-job coverage includes legal one-support/one-reaction combinations of
Desperation or Opportunist with Last Resort, Challenged, TBN, Poise and Blade
Ward/Dark Ward; one rational division; preview RAM/RNG preservation; beneficial
versus harmful tag policy and frozen action-start tags; Inoculation/Auto-Cureall
versus actual composed Wound/Challenge application entrypoints; and simultaneous
status keys/timers. The prevention and lifecycle cases use declared API phase
fixtures and do not imply full UI or reaction playback acceptance.

## Open implementation obligations

- Extend the verified direct-HP boundary below to remaining reaction edge cases
  and acceptance scenarios; do not infer action/turn scope from HP changes.
- Complete remaining rendered reaction playback (Gil Snapper, Dark Ward and
  Chemist; see `reaction-playback.md` for the three bounded accepted cases),
  audit legal compound Bloodcasting
  actions, and finish Chemist preference UI and its remaining mechanics.
  Abyssal and queued Viking/Counter Draw execution now have the bounded
  acceptance recorded in `abyssal-blade.md` and
  `queued-reactions-and-counter-draw.md`.
- Finish Samurai Composure and the four jobs without handoffs; retain the
  outstanding full Counter Draw UI/save/AI acceptance.
- Complete native custom-status Judge reporting, actual queued playback,
  full UI/AP/equipment/acquisition, AI and copy/save/replacement acceptance.
- Reconcile final help addresses after common table allocation and produce a
  reproducible final build from source instead of relying on a frozen base.

Allocated rows, source merges, compilation and bounded passing checks do not
count as completed lessons. Keep the live checkpoint in IMPLEMENTATION-STATE.md.

## Direct HP and displacement boundary

Candidate `d387fe665fa5debc882cbe682cae783e66382486` installs a native HP entry
which receives the actual caller LR before C or import veneers run. Native
direct result-row `+1E` sites are `A2602`, `A2B86`, and `A328E`; the ordinary
descriptor route at `A315A` uses an explicit direct helper through the composed
Dark Sword/Samurai rider. Each preserves the original native writer exactly
once and measures actual before/after HP. The ordinary descriptor rider source
is compiled into the central module with only its HP helper and entry renamed.

Displacement reads row `+1C` at `A2CC8` (Fight) or `A3590` (descriptor effect).
The HP/MP swap at `A337E` and unknown callers also retain their native writes
without entering direct-damage bookkeeping. This prevents fall damage from
inflating the shared damage ledger or triggering another Tsunami MP drain.
It adds no persistent state or guessed unit identity.

`20260915T065411.390098Z` passed 29 of 30 assembled steps, including native
differentials, all previous cross-job checks, original Tsunami and Viking
reaction scenarios. The new trace harness initially missed central metadata;
`065604.190254Z` then exposed its incomplete list of fall callsites. Disassembly
confirmed the descriptor-specific `A3590` row+1C writer. Neither harness fix
changed the game image. Final `065716.579001Z` passed all ten selected dependency
and check steps. The trace covers 64 fixed native executions, including 15
positive fall cases, hits, misses and Sea Legs. One observed case loses 5 direct
HP plus 31 fall HP, reports only 5 HP to job consumers and drains exactly 8 MP.
The exact ROM hash is common to these reports. This evidence does not accept
unfinished reaction presentation, TBN rounding or the whole expansion.

The subsequent barrier/reaction batch is documented in `dark-knight-reactions.md`.
Final combined run `20260915T072047.890256Z` passes all 31 steps, including native
zero-rounded TBN consumption, Fight, Shatter Guard's temporary defender, actual
queued Shell/retaliation, elemental responses and two-weapon no-recursion checks.
Use that note and IMPLEMENTATION-STATE.md for current evidence; the earlier
hashes and limitations above describe their own historical candidates.

Soldier's Recuperation and Haft Guard are now composed in root integration.
`soldier-supports.md` records callback ownership, fractional healing, snapshot
allocation and bounded native evidence. Candidate
`ff7369a8700614ec4f0e456d142662439c59cfb0` passes all 39 combined steps in
`20260915T084056.050238Z` with unchanged inputs. This includes the existing
reaction playback/cold-resume regression and 2,898 new Soldier assertions;
the full expansion still requires the remaining jobs and final acceptance.
