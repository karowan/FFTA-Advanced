# Original draw-sort boundary diagnosis

Full engineering remains required. Candidate
`a28b624bb13c8f2f2597a4d4bd3999b17c234b99` is unchanged; E03 remains open.
This investigation identifies a native failure boundary, not a new supported
actor count or a full-game regression. See `native-art-sort-inputs.json` and
`native-art-sort-capacity-evidence.json` for authenticated private evidence.

## Reproduction and cause

The original formation23 has ten templates: five opposing and five allied.
Replacing Giza's formation32 record with that complete original record leaves
Giza's scene/deployment consumers in place. The resulting fixture can deploy
Montblanc, Dark Knight117 and Viking118 alongside the ten templates and judge.
Formation Marche is a nonparty record at020030CC; canonical Marche is absent
from this fourteen-actor list. This is an explicitly substituted combination.

`test-art-native-largest-entry` fails during Start/confirmation with an invalid
heap header at020161D8. `test-art-largest-heap-diagnostic` replays its retained
pre-confirmation state, without changing inputs or installing emulator hooks.
The first invalid heap walk is at frame507; all102 remaining samples through608
are invalid, with no recovery and no final command menu. Native PC remains in
08098C6E..08098CA4. This is persistent corruption/hang, not a transient allocator
snapshot. The diagnostic's four passing checks mean reproduction only.

The original routine08098C20 reserves68 stack bytes. The first52 bytes hold
thirteen wrapper pointers. Its counter is atSP+34, cursor atSP+38, and callback
context atSP+3C/+40. The native linked-list collector0809AC20 has no limit:
the fourteenth pointer overwrites the counter, then increments that pointer
value. Sorting consequently consumes a huge malformed count. The retained
fourteenth wrapper is02022B88 (the judge); the collected count becomes02022B89.

`test-art-native-sort-capacity` passes83 checks in runner
20260919T083341.695495Z. It executes the exact original collector and sort on
private memory clones, with both clean US and candidate code and both stack
residues0/4. The thirteen-actor control changes only the last next-list edge:
it returns with its stack restored, all draw-order values0..12, descending
native position order, and no EWRAM changes outside native order/dirty fields.
The fourteen-actor branch stops immediately after collection, before the bad
sort; it proves the two exact counter writes at0809AC22 and0809AC28. It does not
run a reconstructed whole game or accept fourteen actors.

Native body rendering is not the cause of this isolated overflow. Expanding
this one stack buffer would not prove other native arrays or supported scene
limits safe. No production buffer expansion, roster cap or actor removal has
been implemented to conceal the failure.

## Retained failed routes

| Runner UTC | Result |
|---|---|
|20260919T081529.236513Z|Old formation1 deployment inputs moved existing Marche; six allies remained. Extra confirmation reached a Ritz Move grid; menu budget failed.|
|20260919T081739.238575Z|Inputs selected already-deployed Montblanc and hit the removal refusal. Native command menu arrived, but required party identity/count failed.|
|20260919T081941.718802Z|Correct DK/Viking deployment produced fourteen actors and persistent native corruption.|
|20260919T082312.866338Z|Read-only interval diagnostic passes4 reproduction checks; capacity remains failed.|
|20260919T083341.695495Z|Isolated native sort diagnosis passes83, including clean-code controls; no encounter acceptance.|
|20260919T083825.755600Z|Full original event scene substitution reaches deployment, then fails its fixed6400-frame command-menu budget.|

The persistent failure's original child capture also raised while walking the
damaged heap, after saving raw artifacts. Therefore that child directory has
no failed.json; the enclosing runner log/report and raw snapshots are the
evidence. The capture helper now retains heap errors as data so future failures
can write their report. No repetition was needed for this reporting fix.

## Full event follow-up and remaining scope

`test-art-native-event-entry` replaces only event3's record with original203,
retaining placed location8. Its scene168, formation23/0, original flags and
all scene bytes remain intact. It preserves original formation records rather
than transplanting formation23 into scene14. Fixed A-only inputs reach the
deployment screen, with healthy heap, ten template actors plus canonical Marche
and a six-of-eight allied display. The input plan never presses Start, so its
first-command-menu expectation fails. It supplies no battle/menu acceptance.
The retained `failed.state` can support a declared bounded Start/confirmation
follow-up without recreating the preceding route.

Original event203 byte7 is1, which influences native setup at08122258; however
Giza event3 has the same value. That flag alone does not explain the difference
or exclude fourteen actors. Scenes14 and168 have different subsequent scripts.
A static scan of all301 native mission records at0855AE4C finds no mission
selecting events201..210. This is only a selection lead, not an exhaustive
unreachability proof: direct/scripted events, alternate modes and saved inputs
need their applicable consumers reconciled. Do not infer multiplayer or demo
status solely from unrecognized records or a flag13 branch.

Next establish the actual encounter roots and supported roster bounds; use
existing passing thirteen-actor/all-ten evidence where applicable. Resolve any
demonstrated supported-path failure rather than silently accepting it as native.
Then finish remaining demanding effect/menu lifetimes, E02 review, E04 campaign/
save compatibility and E05 final clean build and independent-save delivery.
No player data, installed7507ca5c package, current selector or production ROM
was modified; the documented disposable fixtures remain private evidence.
