# Quin retry safeguard: integration and evidence

The approved Mythril Rush recruit row keeps the native 20% Quin offer and original Silvril reward. Native recruitment already excludes a currently present Quin, but has no history check for an accepted character who later dies or is dismissed. The new guard affects only internal mission111. Original Missing Prof66 and all other native mission candidate routines delegate unchanged.

## Persistent ownership

Reserved byte state+1E79: bit0 means accepted Quin, or a conservative legacy block; bit1 means tracking initialized. Other bits are preserved. The magic/version stays FFTAEXP1/version1. Quin is identified by the native special-name pointer0855165F, nonempty roster type, race3. Current job is deliberately irrelevant: the initial job27 is Sage.

`ffta_quin_prepare(state)` supports both live and staging blocks. It must run after every successful normal/suspend decode, including already-expanded saves, and during lazy new-game inventory initialization before mission play. Uninitialized saves with Missing Prof completed (flag341 = state1FD8 mask2) are conservatively blocked even if Quin is absent: historical failed offers and deaths cannot be distinguished. Pre-offer imports are tracked normally. Existing Quin is marked accepted. Accepted history is never cleared by absence, dismissal, or death.

## Actual native commit sites

- Regular Yes acceptance: native807D0 copies264 bytes from party context+1D0C into `[02002C78]`; the real mGBA trap captured source02002FC4, destination020006B0, LR080807D5. Hook807D4..DC observes the committed roster, then executes originalD2F2C and replays native continuation.
- Swap/replacement: hook62004..62010 runs originalCA1BC, stores the normalized name into the accepted roster record, observes it, then resumes the intact job-reconciliation loop at62010. The earlier diagnostic span6200A..14 was rejected because native62156 branches back into62010. It is not the final implementation.
- CandidateD241C entry delegates through a native prologue trampoline. A blocked mission111 produces the original empty264-byte candidate and returns0 without consuming RNG. Candidate previews and failed/declined offers never set history.

No broad copy hook or native flag-writer hook is installed. Full candidate/output clearing and native original-reward behavior remain visible to callers.

## Evidence

`test-quin-history.py` runs all406 native mission candidate IDs with two deterministic RNG seeds, compares candidate bytes/returns/RNG, exercises staging migration/invalid formats/monotonic history, and executes whole native61F54 with the real UI encoded name form (special index97/type1). It scans all native code halfwords for direct branch targets into all three hook interiors, including a positive control that catches the rejected swap span. The corrected private probe265a540d9d39081c2908e3957ace973519436c70 passes1,831 checks.

The corrected installed build **ad1767f8b4c78276e711d7e89e669f6b0b272097** passes the1,831 native checks, including whole native replacement61F54. `test-quin-history-in-game.py --current` passes22 checks using a freshly generated matching battle/results fixture: actual native failure, decline, Yes acceptance, unchanged Silvril reward, ordinary Save, fresh emulator Continue/Load, all24 roster records/history, and genuine native New Game through the snowball scene with tracking initialized. No supplied SRAM or tutorial patch is used for that New Game check. The results fixture substitutes a native-generated Mythril Rush accepted record after a native Herb Picking victory; it does not claim to test Mythril's battle or campaign unlock.

`test-ap-counts.py` requires Quin initialization from installed lazy-give and both normal/suspend staging-load entries, preserving atomic rejection and staging/live separation. Corrected main's ability-core601636a0 passes1,141 checks, with8-byte alignment at C entries.

`test-quin-lifecycle-in-game.py` passes62 checks on installedad1767: four history/completion policies through each actual normal and suspend Save/Load path, plus two genuinely native-format saves created with the foundation ROM and imported through native Continue/Load. It verifies adjacent preference bytes and mission completion remain intact. All24 unit records survive, except native suspend reconstruction explicitly reindexes the six battle wrapper indices at unit+FB from5..10 to0..5; these exact native remaps are separately asserted. Old expanded saves with completed Missing Prof and absent Quin become conservatively blocked; tracked failed offers remain eligible despite completion; accepted-but-now-absent history persists.

The normal recruitment confirmation and whole native replacement routine are accepted. A full20-unit replacement UI playthrough and a death animation are not exercised; death/absence policy is verified by retained saved history, not by claiming native historical death detection.
