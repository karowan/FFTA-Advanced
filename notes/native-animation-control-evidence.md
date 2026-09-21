# Native animation controls and Samurai Fight

September 18, 2026. This corrects an observer error, not ROM animation code.
Full engineering E02 remains open across the other consumers and classes.

Private Samurai candidate `5fe7c35d4b4a89e71f3cdc059e5bff75e747ee33` failed
the former body-display assertion at attack frame53. Retained evidence is
`build/art/samurai-fight/20260918T221953.470284Z/failed.json` and its RAM,
IWRAM and VRAM companions. Do not delete or relabel that failure.

Native dispatcher080210E4 reads sequence-command byte+9. Type1 publishes
graphics; types2..8 perform offsets, flags, layout/event controls or no-ops.
At frame53, entry2 is type8. It preserves entry1's displayed tile source and
layout while recording its event at actor+1E. The old observer incorrectly
interpreted entry2's unused graphics fields as a newly displayed image.
Actual VRAM exactly matched the recorded source and graphics entry1.

`actor_render_evidence.py` now walks backward only through known control
commands to the nearest executed type1. This requires an exact native cursor,
index, recorded source and layout match; it does not search arbitrarily for
matching pixels. The report exposes `controlHold`. Graphics candidates must be
type1. Actor observations now include the existing native tile offset needed
by bounded reset checks.

Runner `20260918T234705.898119Z` completed successfully:

- `test-native-animation-controls`:30 checks. Authenticates all four retained
  inputs and byte-identical native210E4..21378, executes controls2..8 on an
  ARMv4T clone, and reproduces the complete72-byte frame53 actor using native
  update08021290. Pixel/source/cursor/opcode negative mutations are rejected.
  Report: `build/art/native-animation-controls/20260918T234706.535056Z/report.json`.
- `test-samurai-attack-reference`:4915 checks,608 per-frame action samples.
  Native Fight with katana106 deals28 damage, preserves HP60/MP17 and returns
  to the next turn. Native action slot42 observed. Report:
  `build/art/samurai-fight/20260918T234706.911715Z/report.json`.

The earlier frame23 constructor mismatch and frame53 failure remain historical
records. This result does not establish all class action families, water,
weapons, effects or maximum capacity. Installed ROM, artwork and saves unchanged.
