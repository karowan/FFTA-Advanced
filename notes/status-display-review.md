# Native status display extension

Private ROM `de421e6eeb26d694e607fb45d77951650461864c`, based on accepted
`ad1767f8b4c78276e711d7e89e669f6b0b272097`. This is an isolated display layer;
the gameplay that grants Exposed and Centered is not yet fully composed.

The new visual selector keys are25 for Exposed and26 for Centered. The native
keys1..24 retain their original status predicates, including all three Doom
counter icons. The getter reads the existing explicitly owned packed byte:
bit0 for Exposed; bits1..3 for Centered. A consumed Centered execution marker
does not display. The native cycling state machine includes the new keys only
while at least one corresponding effect is active.

The original zero visual slot was rejected as storage: unrelated native fixed
UI descriptors at3915B8 also use tile143. The accepted private approach changes
the battle graphics constructor's MOV at97098 fromF0 toF2. Its shift therefore
moves the upper dynamic tile pool from1E0 to1E4. Its end400, low pool0..120,
original fixed graphics, and every other graphics constructor stay unchanged.
The four reserved tiles at06013C00 hold two original8x16 glyphs: a cracked shield
and a focus ring. They use one native status sprite each, with no extra OAM
objects and no persistent global display allocation.

`patch-status-display.mjs` guards every displaced byte. The getter entry is
9DA0C..14, selector increment9DD52..62, and visual selection97AD0..AE6.
`build-status-display-probe.py` compiles and applies this same helper privately.
The main builder does not yet include it.

Deterministic evidence:

- `test-status-display-native.py`:13,884 checks. All native selectors across
  64 status bits, all256 packed byte values for the new predicates, original
  cycle transitions, custom cycles, all24 original rendered IDs, both stack
  alignments, live registers/flags/frame, and exact VRAM write boundaries.
- `test-status-display-in-game.py`:24 assertions on separately generated
  matching-ROM fixtures. Native Protect and both new icons cycle together;
  removing custom bits stops those icons while Protect remains. Actual Move,
  Fight and end-turn facing return to the next unit's menu. Native, overlay,
  and active-icon cases all deal24damage and preserve actor47HP/14MP. Original
  status graphics and the following-turn HUD match the native control. Native
  suspend followed by a fresh emulator Resume preserves the packed state and
  reconstructs the reserved graphics pool and both icons.

Two test assumptions were corrected from observed native behavior. The fixed
UI region contains animated/text tiles, so a before/after byte equality is not
an appropriate whole-region oracle; the idle comparison uses an actual native
control, and the attack comparison checks all24 original icon tiles plus the
stable HUD. The private build's fixed-frame fixture can precede the first turn
menu by a few frames. The input script now waits for the observed native menu
before issuing keys. Move+Act then requires end-turn facing confirmation, not
an immediate return to the same unit's command menu.

The general fixture generator now uses `battle-menu-observation.py` before
publishing `battle-ready.state`. Its recorded native font anchor contains136
bright text pixels and371 dark outline pixels; all-black and all-white frames
are rejected. The12 observation checks pass on actual native and pre-menu
snapshots, and a fresh `fixture-observed` generation on this private ROM passes
all existing heap/party/guard checks after a150-frame input-free readiness wait.
The older frozen fixture is retained for the accepted tests and timing evidence.

Remaining: integrate with the completed Exposed/Centered gameplay, add the
display to the composed regression and weapon/animation cases, and include a
player-facing status legend/help. No main ROM, player save or launcher changed.
