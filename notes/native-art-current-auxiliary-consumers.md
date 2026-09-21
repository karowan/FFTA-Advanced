# Current held weapon, projectile and impact acceptance

Full engineering remains required. Only artwork content/authored poses are
placeholders. E01-E05 remain open; no installed package, player save, launcher,
art source or ROM changed in this checkpoint. All runners below are terminal.
Current action candidate:5a14e6c7b69f9f9984a6965faf5740d3b318e41a.

## Held trail observer defect

Runner20260919T035251.952506Z failed test-current-held-weapon; the later
projectile check was skipped. Retained failure and raw captures:
build/art/generated-actions/battle/20260919T035252.698820Z/failed.json.
The six failures were original secondary trail frames57..61 and generated trail
frame57. Both controls still dealt14 damage and returned with47HP/14MP. Those
outcomes alone did not waive the unverified displayed frames.

The actual secondary sequence has opcode0 at entries2 and4, between graphics
entries. Native210E4 reads byte+9, subtracts1 and returns unchanged when the
unsigned result is outside0..7. In particular, opcode0 is a no-op. The observer
only followed controls2..8, so it missed the directly displayed entry1 at57.
Its missing direct anchor then prevented the original pending frames58..61 from
being verified. Repeated generated placeholder pixels masked those later misses.

actor_render_evidence.py now explicitly includes opcode0 in the known control
chain. It still requires the exact cursor, nearest executed graphics entry,
recorded source/layout and actual uploaded pixels. Unknown opcodes remain
unaccepted; command-only sentinels do not become image evidence. No ROM code,
command timing, generated source or palette was changed.

test-native-animation-controls passes95 in runner20260919T035659.315442Z:
build/art/native-animation-controls/20260919T035700.014872Z/report.json.
It retains the old Samurai control proof and adds the actual held failure:

- Pinned raw original/generated frame57, opcode0 and secondary descriptor.
- Original native full update reproduces the entire72-byte captured actor.
- Original frames58..61 retain the complete directly proven allocation within
  the existing pending-upload bound. No inferred anchor or enlarged timeout.
- Altered source/cursor/pixel, unsupported opcode9, missing pending flag, expired
  anchor and changed allocation tail are rejected.

Exact failed-input pins are in notes/native-held-control-evidence.json.

## Current live acceptance

Runner20260919T035750.568007Z passes both targeted checks:

| Test | Checks | Report |
|---|---|---|
|test-current-held-weapon|89812|build/art/generated-actions/battle/20260919T035751.222560Z/report.json|
|test-current-projectile-impact|4063|build/art/generated-projectile/20260919T035837.343332Z/report.json|

The held run constructs native battle objects from the authenticated world
checkpoint. It checks Viking Fight with original128/generated276, both
attachment-owned channels, exact palette/OAM/allocation and original command
semantics, four generic racial classes, persistent storage/roots and next turn.
Every-frame observation covers the declared input/animation intervals. Both
controls preserve14damage,47HP and14MP.

The projectile run selects actual Soldier Tomahawk with four generic new-class
allies. Original/generated projectile controls share the same generated impact.
All three impact poses, moving projectile, exact native color cycling, disjoint
body/effect banks and next turn pass. Both outcomes are18damage,4MP paid
(12remaining) and8EXP. Four-frame sampling observes Dancer bank6 changing to7,
then8 as the original effect demands change, without losing generated colors.

These close the current generated held-axe, Tomahawk projectile/primary-impact
coexistence paths. Other weapon families' auxiliary actors, custom-class casting,
Combo/secondary abilities, all effects, capacity, response timing and campaign
acceptance remain distinct. Old passing body/weapon-family evidence remains
applicable; do not replay it just because the observer now understands opcode0.
