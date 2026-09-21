# Fell Cleave and Exposed integration

September 14, 2026. Tests are local deterministic scripts; no testing agents.

## Implementation

Private candidate `dfc60bf91fde07f9b20254b084e3c4153df77e65` was built over the
accepted `ad1767f8b4c78276e711d7e89e669f6b0b272097`. The assembled candidate is
`d1565a7ee341621e58bd2bb791b065144fe51aec`. All91 declared regression steps now
have passing evidence on this ROM across resumed deterministic runs. The
verified per-step index is `build/expansion/d156-regression-coverage.json`;
the final25-step run is `20260914T221915.116494Z`. The six intervening test
changes corrected standalone oracles/readiness; application inputs were
identical across all seven runs. This does not establish expansion completion.

- Fell Cleave431 uses the primary axe, one adjacent enemy, symmetric height2,
  native physical accuracy and weapon elements, 16MP, and 1.80P.
- Paid execution applies Exposed before hit/miss and immediate reactions.
  Native Immunity prevents this drawback and makes the action unavailable.
- Exposed is bit0 of the explicitly owned saved/evaluated status byte. It adds
  a factor6/5 to positive direct physical HP damage; custom coefficients combine
  their rational factors before one final division. Healing, MP damage, neutral
  fixed/percentage effects and self-costs do not become incoming physical hits.
- Own-turn start, KO, Petrify, battle end, changed job and broad remedies remove
  Exposed. Native Esuna-family effect11 and Cureall79 retain their original
  admission and cure masks. Broad remedies preserve beneficial Centered bits.
- The status renderer reserves exactly four tiles at the upper OBJ allocation
  boundary. The cracked-shield icon represents Exposed; the focus-ring icon is
  reserved for Centered. Linking Centered storage/display does not enable Samurai
  actions or grant Centered automatically.
- Titan Axe460 teaches Bangaa lesson108, Fell Cleave, at400AP. Existing weapon
  acquisition and AP infrastructure remain in place. The assembled help entry
  describes its incoming-damage drawback.

## Recorded verification

`Test Expansion.ps1 -Suite fell` selects the private component suite. The normal
full suite includes separate `installed-fell` and status-display checks against
the assembled ROM. Reports identify each ROM; private success is not a claim
about the later assembled binary.

Native checks cover all packed byte values and native Immunity, signed rational
rounding, all44 original status bits across all36 owned units, job cleanup,
the eight original broad-remedy actions, read-only queries and foreign-copy
rejection. Incoming checks compare original physical stages, Fight and combos,
including independently owned evaluated copies. The complete native executor
replays all347 original actions and10 allocated custom IDs, including inert423,
against the accepted baseline, with no skipped cases.

Actual Fell input scripts exercise its menu, preview, cancel/repreview, fixed
hit/miss seeds, MP payment, next-unit turn, normal suspend SRAM and a fresh
emulator Resume. The independent native-P control removes only the final
coefficient hook. Private seed0 misses; seed1 deals88 compared with nativeP49.
Both spend16MP and gain Exposed.

The native Counter test assigns the existing Bangaa Counter lesson53/global8
to a disposable enemy. Its control suppresses only the paid Exposed grant.
On a missed Fell, the immediate counter increases from45 to54. The script also
requires positive counter damage after a successful Fell. It checks the native
reaction getter rather than assuming a reaction ID.

The weapon-effect regression enumerates native procs on primary/offhand weapons,
critical contexts, both stack alignments and restorative weapons. A composed
wrapper legitimately deepens a temporary native weapon-selection frame; the
test asserts its output pointer is exactly callerSP+4 before comparing that
relative location. Unit/result bytes, other arguments, registers and effects
remain compared.

Graphics tests separately verify all24 native icons, original atlas bytes,
reserved tile allocation, new icon cycling/removal and cold resume. Their
composed Fight graphics comparison uses two recorded RNG-return controls so
rendering time cannot shift random outcomes. These are test-only ROM variants;
normal-RNG combat tests remain separate and unmodified.

## Remaining work

The full approved expansion is unfinished. Samurai grants/actions, other new
abilities and supports/reactions, additional vanilla+ recovery work, complete
cross-class acceptance and final distribution remain open. This integration
does not replace the player's launcher or save. A final council review belongs
after the implementation and scripted verification, not in the test loop.
