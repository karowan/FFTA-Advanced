# Next Samurai composition work

**Superseded progress note:** The builder is now promoted, and the four-strike
candidate is `c683be6ff39ba02b4a1e9f650705f8b254fd59e5`. The composition,
Dispel/equipment events, Protect law prediction, native gameplay and immediate
Counter tests below have been implemented and pass. See
`samurai-integration-review.md` for current evidence and remaining work.
The rest of this file preserves the earlier implementation research.

Read-only source review during the deterministic Fell regression, September14.
No Samurai gameplay has been added to the assembled build by this note.

A staged builder at `build/expansion/staged/build-samurai-probe.py` now compiles
private candidate `dac3d53cd7f925fabb425bcc80e984e7c00317c3` over d1565a7e.
It combines the coefficient/Centered/Exposed factors once, binds the shared
payment behavior, and replaces the incoming-stage classification to exclude
the four Samurai actions from a second Exposed factor. It compiles cleanly;
fresh gameplay acceptance and the remaining lifecycle/law work below are still
pending. Main source, ROM and the running regression were not changed by this
staging step. Promote the staged builder into `scripts` only after the current
regression ends, restoring its root calculation from parents[3] to parents[1].

1. Update `build-samurai-probe.py` to consume the composed main build. Its old
   literal replacement of the physical multiplier no longer matches the
   Exposed-aware rational formula. Multiply class coefficient, Centered5/4
   and incoming Exposed6/5 together before dividing once.
2. Keep one payment hook atA45C6..D4. The new wrapper calls the existing Exposed
   gate first, then marks Centered consumption. Replace the existing Exposed
   payment binding explicitly; do not demand untouched native bytes there.
3. Bind both `ffta_exposed_paid_commit` and
   `ffta_exposed_incoming_numerator` in the private builder. Weak omission of
   the former would silently remove Fell's drawback after the shared payment
   hook is replaced.
4. Extend the Exposed native-stage exclusion when Samurai physical actions are
   enabled. Otherwise their finalizer would apply6/5 and the original stage
   wrapper would apply another6/5. Prefer a single authoritative predicate for
   enabled custom physical definitions, with explicit standalone-test bindings.
   Include a non-divisible reference and active target Exposed in the oracle.
5. Wire Dispel and actual primary-weapon changes to Centered's typed events.
   Broad harmful-status remedies must preserve it; own-turn starts must not
   replace its T2 end-turn duration. Preserve every upper packed bit and
   Exposed bit0 when clearing Centered.
6. Implement Guarding Draw's Protect law prediction on owned evaluated actor
   state and validate it against actual Protect application, including misses,
   incompatibility and immediate retaliation. Do not bypass original law rules.
7. Generate fresh matching native UI fixtures. Require hit/miss, Centered
   grant/consumption/retirement, non-Iaido retention, native MP/HP loss and
   suspend/cold resume. Add those deterministic stages to the declared plan.
   Historical native matrices remain useful evidence, not a substitute for the
   newly linked ROM.

The existing four direct-action candidate covers347 Ashura,349 Osafune,
352 Guarding Draw and353 Kiku-ichimonji. The remaining approved Samurai actions
are still outstanding, as are the broader expansion's supports and reactions.

## Native lifecycle entry points identified

- Original Dispel is action10, stage106, descriptor `[8,53,23,0]`.
  Effect53 points to132C0C, a no-op callback. As with Esuna, the native common
  dispatcher handles original status removal separately. A query-guarded
  Centered-only callback can preserve native admission/removal masks and clear
  only the explicitly selected recipient's Centered bits. Validate all44
  statuses, query mode, Exposed preservation and Centered-only admission.
- Native equipment settersCAF78 andCB0D8 remove the old item, update teaching
  and assigned abilities, then store the new item. Compare ordered primary
  weapon before and after the complete operation. Same item, unchanged primary,
  armor changes and rejected operations must preserve Centered. Changes on
  explicitly owned evaluation copies must stay local to that copy.
- Direct nativeCAF78 callers found in the executable region:7815A,7AF06,CB4CE,
  CB58E,129366,12938C,132000,132A68,132D3A,1332BC,133356. CB0D8's direct caller
  is7B622. These include battle effects as well as equipment menus; inspect
  them when validating loss/steal/break and not just manual equipment changes.
  These are identified addresses, not yet accepted lifecycle hooks.
