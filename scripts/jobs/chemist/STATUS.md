# Chemist implementation status

Final agent checkpoint, September 15 UTC. Worktree `.worktrees/chemist`, branch
`jobs/chemist`. Implementation commit **97d641b**; shared queue **04453bd**.
All writes stayed in this checkout. No player saves, visible windows, main or
sibling files changed. Root takes over remaining work after this current batch.
**The whole Chemist job is not accepted end to end.** See HANDOFF.md.

## Sources and builds

Chemist checkpoints: 1ea9d54 medicines/choices, 9e1b822 fresh captures, 2dc3192
Inoculation, df4dc80 Auto-Cureall/payment ownership, 97d641b queued item reactions.
Shared prerequisites adopted: 77efe09 as cf9456f; d80bb14 as 52836c9; eff9489 as
768d01d; 2eb9e52 as 3806afd; ce83f72 as e7ed4e9. Queue 04453bd is separate.
Missing runner test copied exactly from root 2d4e630, as root instructed.

Frozen main input: ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7.
Final private Samurai: 4d0110964db2a11fa4e28c7042dc483ab0980b66.
Owned state: e38fd42b6b606578d97eef5f97019a65d8222ac9.
Chemist: 1d4ac0da9caf3a0f42f23bf5a05e0ac80a265b16.
All ROMs, captures and raw reports remain ignored under build/expansion.

## Implemented and tested

Ten records 383..392, explicit Field Remedy/High Tonic native menu rows, original
racial lesson/AP identity, exact recipes, atomic payment and execution-time cure
usefulness checks. Active and automatic spending require exact party origin
1..24, including authenticated copies. Native medicine/revival/Guard handlers,
Pharmacology and Long Throw retain their original native integration.

Inoculated uses owned CHM byte8 bits0..2 for T2/application-turn skip. Harmful
whitelist 6/8/9/10/26/27/28 excludes beneficial Conceal12. Native Slow, Stop, KO
and actual Cureall item semantics remain. Inoculation precedes Auto-Cureall;
query never spends or changes live state. Both-race actual Inoculation menus,
cancel/payment/turn/native suspend+cold and display were tested.

Auto-Cureall freezes admission: live HP, no Petrify6 or native common R blockers
0/31/32/43. No invented Sleep/Confuse/Silence veto. Native Break/Sleep/Poison
execution preserves damage/RNG and spends exactly once on successful prevented
applications, using authenticated claims and exact inventory ownership.

Auto-Potion captures permitted positive enemy HP loss during RESULT. At queue
exhaustion it rechecks survival, half-HP, explicit saved preference, stock and
consumption-only own-turn lock, then queues the real native Potion/Hi-Potion.
Native debit A2EB8..A2EC4 sets byte8 bit3 only after actual stock decrement.
1536 full native cases cover both races, SP0/4, both preferences, Pharmacology,
stock, locks, lethal/threshold/miss controls: 6257 checks, 112 positive recoveries.
No invisible post-result healing stub replaces native item execution.

## Final evidence

Paths below are directories under build/expansion/test-runs.

| Run | Passed scope |
|---|---|
|20260915T060243.400797Z|5 shared steps: original executor, build/capture, 4073 context and 2339 queue checks|
|20260915T060259.940652Z|15 composed steps: runner, build/fresh fixtures, native medicines921, reactions4217, Auto-Potion6257, queue2339, supports/menu/state/prevention/display, actual Potion and Inoculation save/cold|
|20260915T060421.469709Z|Final candidate's explicit native medicine-choice routes|

060058 failed on the missing root test-git-content.py. Exact source was restored;
runner self-test passed060259. That failed whole-suite run is not called passed.
Earlier diagnostics caught/fixed relocated scratch pointer normalization, an
r12-clobbering entry veneer, and a second native item-debit branch.

Repeatable commands:

```powershell
& '.\Test Expansion.ps1' -Suite samurai -Only test-action-context,test-reaction-queue
& '.\Test Expansion.ps1' -Suite job-state -Only build-job-state-private
& '.\Test Expansion.ps1' -Plan scripts/jobs/chemist/test-plan.json -Suite chemist
```

After rebuilding Samurai, rebuild job-state before Chemist. The job builder
consumes local job-state/current.json. Fresh fixture hashes must match; never
reuse another heap/layout or label newer compilation as accepted main ba1c.

## Allocation

ROM1280000..12BFFFF, erased-FF guarded: code1280000, descriptors1290000,
apps1291000, masks1292000,436-row action bank1294000. Preserve native209
Descriptors/93 apps and432 assembled actions. CHM descriptors209/210/215/220,
apps95/96, hidden432 only. Private peer holes are inert, not implementations.
Inoculated key30, OBJ1EA..1EB, central pool1F0/native97098=F8.
Owned byte8 bits0..2 Inoculated, bit3 Potion lock; byte9 unused. Saved preferences
use existing24-byte metadata through ffta_job_potion. No private RAM allocation.
Snapshot flags11/12; claims1/2 consumption,4 HP admission,2048 scheduled,
4096 presentation. Root composes shared providers/lifecycle and other jobs.
Detailed contracts and remaining gaps: HANDOFF.md and notes/native-reaction-queue.md.
