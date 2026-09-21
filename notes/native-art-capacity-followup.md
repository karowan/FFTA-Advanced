# Encounter selection and demanding action/Status lifetimes

Full engineering remains the scope; only final artwork/authored poses are
deferred. Candidate `a28b624bb13c8f2f2597a4d4bd3999b17c234b99` is unchanged.
E01/E02 remain accepted. This follow-up narrows E03 and proves a demanding
action/menu combination; it does not close all scene/spawn lifetimes or E04/E05.

## Actual encounter selection

`test-native-event-roots` passes **4,273** checks in terminal runner
`20260919T091247.440032Z`. Its report is
`build/art/native-event-roots/20260919T091248.211528Z/report.json`.

The earlier scan covered301 mission records. The actual table has512 slots;
all512 current event selectors match clean US, including expansion recovery
records, and none selects event203. The native mission-entry path616AC reads
the70-byte table's byte69. The mission queue producerD0BFA..D0D5A also packs
that field. Random queue generationCF8EC instead uses225+location for1..30.
These audited consumers, the world lookup and entry paths remain original code.

The secondary-map lookup at9C18 uses the pointer085644FC, equivalent to the
event-table base plus225 records. It is **not** the beginning of the event
table. All30 location substitutions are evaluated against that actual pointer.
The test executes original selector instructions for1,612 event/location pairs
on both current and clean code and checks exact output writes. For each pair,
the initial-roster estimate is opposing templates plus the greater of allied
templates/deployment display limit, plus a possible judge. Only event203 yields
more than13: formation23 gives14. This estimate is a selection inventory, not
proof of every original script's later actor creation or scene eligibility.

The descending native scene-search prefix123898 executes for every scene0..255
and absent256/65535, against both ROMs. Scene168 actually selects event255;
event203 is shadowed. The scan also records direct Thumb calls to9C04,9C18 and
A040 within the original code region. That bounded direct-reference scan is
not advertised as exhaustive indirect-call or arbitrary saved-state analysis.

These results exclude203 from the audited mission, mission/random queue and
scene-search roots. They do not label203 as multiplayer/demo or claim every
possible direct-state mutation is impossible. The retained14-actor transplant
still fails; its original native13-pointer overflow is not patched or hidden.
Native75574 also reserves52 stack bytes for its deployment enumeration, and
92CEE allocates52 bytes for an actor list. Enlarging only the sort buffer would
therefore leave other original13-entry consumers unsafe.

## Thundaga and repeated Status at thirteen actors

`test-art-capacity-action.py` reuses the exact passing all-ten allocation from
`build/art/all-class-capacity/20260919T070003.108000Z/ready.state` and its fixture
ROM `83dabe12f029e83e459bf95c47ff7f4e2b58a901`. This is the existing formation324
inside the disposable Giza event shell, **not** a newly claimed original mission
route. All13 actors, positions and class identities remain intact. Only Viking
Thundaga mastery, declared HP500/MP100 for the caster/two targets, and RNG1 are
scenario inputs. The native range-three center11,8 hits Mystic125 at11,8 and
Human Dark Knight117 at10,8. The initial center10,8 was range four and refused.

The actual cast in runner`20260919T092036.268664Z` executes1800 frames, with a
valid heap walk after every frame. It pays exactly20MP and deals1HP to each
declared enemy. Other existing actors may react or take incidental damage;
this is not a controlled combat-damage comparison or a no-reaction claim.
The enclosing run fails only at its later incorrect sentinel-zero assertion.
Its full result remains failed and is reused only for its recorded action and
memory observations.

The Samurai-only execution root0203FF44 startsD7D7D7D7 in the retained fixture
and remains that exact sentinel. `execution-scope.c` admits only valid aligned
stack scopes, and standalone non-Higan actions do not touch that root. The
actual action snapshot at0203FF48 is zero after the cast. Correct acceptance
requires the sentinel unchanged and the action snapshot retired; it does not
clear memory to manufacture the expected result.

`test-art-capacity-action-return` passes **195** checks in terminal runner
`20260919T092805.491239Z`, report
`build/art/capacity-action/20260919T092806.315981Z/report.json`. It authenticates
the earlier executed state/RAM/IWRAM, verifies damage/payment/root invariants,
selects native Wait, reaches the next turn, and opens/closes Status twice.
All13 unit/wrapper identities and all ten configured class resources survive.
Each Status context owns its expanded list; shared battle-heap ownership and
copy roots balance on return. No all-ten on-screen or every effect-pose claim
is added here; E02 and the original all-ten idle evidence retain their scope.

Retained heap inspection proves the **complete allocation-block list**, not
just totals, is identical at next-turn, returned-0 and returned-1. Both Status
captures likewise have identical block lists. Actual free capacity:

| Phase | Free payload | Largest free block |
|---|---:|---:|
| Next turn and each returned menu |54,632|41,640|
| Each Status screen |11,052|8,776|

The cast's minimum observed free payload is33,572 bytes. The combined minimum
is11,052 during Status. Menu sampling occurs at input boundaries; every cast
frame is sampled, but not every allocation instruction or every menu frame.

## Failed attempts retained

All runner IDs below have prefix`20260919T` and suffix`Z` under
`build/expansion/test-runs/`. No candidate engine change was needed.

| Runner | Actual result |
|---|---|
|091649.033772|Failed before emulation: test looked for renderer metadata outside `components`.|
|091732.960103|Exact memory loaded, then menu check ran before any framebuffer was published.|
|091813.084586|Native game correctly refused the range-four spell center.|
|092036.268664|Legal cast/damage/payment/per-frame heap checks pass; sentinel-zero expectation fails.|
|092300.859032|Post-cast route selected Move instead of Wait; next-turn budget fails in the move grid.|
|092501.260904|Menu observer used transient orange background and wrong BGRX channel order.|
|092626.379420|Wait reached; old black-outline text anchor rejects highlighted Wait lettering.|
|092805.491239|Corrected native-marker/unselected-label observer and return suffix pass195.|

The deterministic menu helper locates the actual yellow selection marker,
then requires the original unselected Wait/Status glyphs at unchanged pixel
thresholds. Three retained native captures independently validate the row0/1/2
observer before the successful suffix. It never selects a command by changing
the game's menu state. The original shared menu observer remains unchanged.

`notes/native-art-capacity-action-inputs.json` pins original ready, failed
targeting and completed-cast inputs. `native-art-capacity-followup-evidence.json`
pins125 files, including all nine runner outcomes and raw captures.
`audit-art-capacity-followup` passes **134** read-only checks, terminal runner
`20260919T093049.047073Z`, report
`build/art/capacity-followup-audit/20260919T093049.778474Z/report.json`.
Report SHA256: `612efb58e2205f5b2baf1633857c852e40f76dc1dc5ef289cd80a8ad4251f943`.
It verifies every pin, the1800 consecutive action observations and complete
heap restoration. Future full-route/suffix runs include heap equality checks;
the existing playback was not repeated merely to add these static assertions.

## Remaining work

E03 still needs final review of supported scripted spawns/retirement and scene
exit/return lifetimes. Initial event arithmetic and the demanding action/menu
case do not establish those longer paths. E04 must reconcile the unchanged
gameplay evidence and verify affected campaign/ending/save consumers with the
retained menu/heap changes. E05 requires the clean complete build, final review
and separately playable reproducible package. Reuse accepted performance,
graphics, selection and action/menu evidence unless dependencies change.
Installed7507ca5c, selectors and player files remain unchanged; no launch,
publication, new artwork or agents occurred. Every runner is terminal.
