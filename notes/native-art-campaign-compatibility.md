# Current engineering campaign and save compatibility

Root accepts E04 on `a28b624bb13c8f2f2597a4d4bd3999b17c234b99`.
Only final artwork/authored poses are deferred. E01/E02 remain accepted;
E03 final capacity review and E05 reproducible full delivery remain open.
Installed7507ca5c remains unchanged and is not the full engineering delivery.

## Current affected lifetimes

All runs below use the declared art plan. The runner header's generic
integration ROM is ba1c33ea; child reports authenticate the actual tested ROMs.
No player saves, current selectors or installed ROMs were written. All runners
and cleanup processes are terminal. No game launch, image generation or agents.

| Test / terminal runner UTC | Result and scope |
|---|---|
|test-art-campaign-saves / 20260919T093906.493084Z|54 checks. Cold Continue on exacta28 from both retained ordinary flash and actual historical ending flash. Complete24-slot roster/AP/inventory/preferences/history/gil, clear flag and transient retirement; full world party context and return; native mission/pub clear-flag positive/negative pair for202/378 across eight towns.|
|test-art-battle-exit / 20260919T094451.812353Z|Failed at premature world-menu assertion. Actual retained all-ten13-actor battle exits through original scene15, earns story3-to4 and receipt770, preserves all24 party job identities, and retires borrowed party/copy/action roots. Mandatory Lutia placement is still active, so Start correctly cannot open the party menu. The enclosing run remains failed.|
|test-art-battle-exit --resume-result / 20260919T094742.178038Z|16 additional checks. Authenticated exact earned-result state; actual cursor inputs place awarded Lutia (location12, tile19), full world context/item list, menu return, native normal save and unmodifieda28 cold load. Full saved profile and earned progression survive.|
|test-art-campaign-ending / 20260919T095034.550420Z|14 checks on currenta28 with an isolated observer fixture9bc4cd938fea2947201e454a4b095e4fb7cf15ac. Actual connected scenes101/102/104/105, rolling-credit opcodes, ending-save opcode089B83CA, scene-owned flash write, reset/title/Continue and unmodifieda28 cold load. Complete24-slot profile and transient retirement pass.|
|audit-art-campaign-compatibility / 20260919T095533.361272Z|484 read-only checks.188 new evidence pins,28 original report/log pins,52 historical note pins, original gameplay source comparison and whole campaign/scene/table regions. No emulator.|

Child report roots are respectively:

- build/art/campaign-saves/20260919T093907.228501Z/report.json
- build/art/battle-exit/20260919T094452.512705Z/failed.json
- build/art/battle-exit/20260919T094742.944213Z/report.json
- build/art/campaign-ending/20260919T095035.310874Z/report.json
- build/art/campaign-compatibility/20260919T095533.989211Z/report.json

`native-art-campaign-evidence.json` authenticates188 source/result/raw files.
`native-art-campaign-review-evidence.json` pins that index plus both reconciliation
attempts and their complete logs/reports. The accepted release's nested28 report
and52 note hashes are verified without relabeling historical tests.

## Root review and reuse

The corrected eight-stage gameplay base5065a9ea preserves every original shipping
gameplay source from release1b070824. Of those source files, only
chemist-preference.c and integrated-jobs.c now differ: context-owned preference
list recognition and the equivalent early native status-key advance. Current
native UI/status acceptance is documented in native-art-engineering-consumers.md.
Their source diff was reviewed; no new job formula, AP rule, mission chain or
save schema was added in this work.

Current ROM and historical1b070824 agree across the full mission/pub/result
consumer range0CFC00..0D2300, native formation records, mission/event tables,
expansion action/application tables and scene interpreter/actor region
120000..12D000, except the declared US keyboard allocation size at12A15E.
All ten original ending script/controller dependencies also match. The changed
heap/menu layout is covered by current cold/world-menu, demanding battle exit,
normal save and actual ending playback, rather than assuming old savestates
survive a ROM-layout change.

Reuse the accepted release matrix in release-acceptance.md for job learning,
AI/laws/Combo, acquisition, roster/copy lifecycles and campaign milestones. Its
actual connected early/middle/late territory and earned final-battle bridge
remain historical evidence; the original scripts and mission consumers are
unchanged. The current ending route deliberately retains the same one-time
scene101 entry, not a new claim of naturally playing through all final battles.

The battle fixture83dabe12 retains formation324-in-Giza and the existing all-ten
13-actor roster. Its six hostile HP values are declared result-boundary inputs.
No victory flag, receipt, scene result or territory placement is injected. The
party includes four added generic classes; saving this roster does not claim
all ten classes were simultaneously saved as party members. The separate full24
ordinary/ending saves use the historical native test roster, not a new all-ten
art fixture. Cold loads use flash only; no savestate crosses different ROMs.

## Retained failures and limits

The first ordinary-save run093717.767457Z (child093718.506926Z) failed an incorrect
world-map heap expectation. F434 is a battle-only pointer and is reused by world
mode; this was not heap corruption. The corrected check derives the actual
world menu's owner from context[0], verifies the full9980-byte allocation and
owned7280 item-list offset, and adapts only a read-only clone for the heap walk.

The first reconciliation095436.195171Z (child095436.864136Z) failed because
notes/all-new-jobs-ui-review.md was subsequently corrected to distinguish wheel
miniatures from equipment icons. Its exact original bytes are authenticated
at the release's recorded commita395a533; the later correction is retained and
recorded separately. Other51 notes still match their recorded bytes.

Full engineering compatibility is accepted from these bounded current checks
plus the reconciled existing gameplay evidence. No uninterrupted full-combat
playthrough, every cutscene/recruit variation, cross-overhaul save compatibility
or physical-GBA performance is claimed. E03 still needs its final supported
capacity/script-lifetime review; current ending and battle-exit evidence now
covers additional native scene teardown. E05 must rebuild the complete chain
through action completion and native-palette conversion, review the assembled
result, and replace the old preview package with independent-save delivery.
