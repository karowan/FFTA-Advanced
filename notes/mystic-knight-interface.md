# Mystic Knight player interface

Accepted September 16, 2026. This closes checklist I04's player interface;
AI decisions, remaining forecasts/laws and release acceptance remain separate.
Later saber-pose and three native cold-state flows are documented in
[`mystic-knight-cold-lifecycle.md`](mystic-knight-cold-lifecycle.md). That record
supersedes the earlier rapier-only presentation coverage where specified.

## Player controls

Spellblade uses the native scrolling command menu. Its 34 rows contain eleven
enchantments, 21 named Spellbreak buff choices, Arcane Release and Break Blade.
Choose the caster for an enchantment without a strike, or an enemy for the
strike plus enchantment. Spellbreak removes exactly the chosen buff on a hit
and retains the current enchantment. Release consumes its eligible elemental
enchantment; Break attempts Petrify without preliminary HP damage.

All 19 lessons now have native help, including both supports, both reactions
and the Combo. Each description fits the native three-line, 27-character
layout. Earlier help entries remain intact.

The native status cycle shows two-character enchantment indicators:

| Indicator | Enchantment |
|---|---|
| FI / IC / TH | Fire / Blizzard / Thunder |
| PO / SL / SI | Poison / Sleep / Silence |
| DR / FL / SW | Drain / Flare / Slow |
| OS / HO | Osmose / Holy |

**M+** means Spellweave's next eligible magical damage is empowered; **P+**
means its next eligible physical damage is empowered. They describe the next
category, not the previous action. Indicators are derived from owned live
state, with the same KO, support and weapon validity gates as their effects.
The captured native next-turn screen visibly displays M+ after Spellbreak.

## Native rendering correction

Spellbreak carries its selected buff in result offset12, a native field also
used for item IDs. Gameplay formulas already resolved the real primary weapon,
but native rendering interpreted choices7/8 as different weapons. The real
Viera playback stalled in controller phase60 while waiting for a pose.

`mystic-knight-visual.s` separates presentation reads at seven native sites:
category A6238, projectile direction A6412, projectile operand A6424, actor
pose A662C, impact category A5730, hit sound A588C and deferred magic pose/item
DDFCE. Only action421 substitutes its equipped primary. Result offset12 is
never overwritten; effect selection and subsequent Judge consumers retain
their original operand. The deferred DDFCE path was necessary to resolve the
actual stall; correcting only the first six consumers was insufficient.

No persistent schema or RAM field was added. Status keys43..55 use OBJ tiles
204..21D, followed by padding21E..21F. The native graphics allocator starts
at220. Help occupies the separately reserved ROM arena1330000..133FFFF.

## Reproduction and evidence

Run declared tests through `Test Expansion.ps1` with
`-Plan scripts/integration-test-plan.json -Only <IDs>`:

| Change under test | IDs |
|---|---|
| Help and status ownership/tile bounds | `test-mystic-knight-ui` |
| Complete fixed player command matrix | `test-mystic-knight-playback` |
| Presentation hook compatibility | `test-mystic-knight-visual` |
| Isolated Osmose/Spellbreak follow-up | `test-mystic-knight-remaining` |

The corresponding `-cached` IDs require matching source, image and native
prerequisite evidence. They are for test-only follow-ups, not bypassing changed
build inputs. Navigation-only playback selects the first self-enchantment.

- Image `533403a1d86029fa0effcf301cc5f61509241f35`: 611 UI assertions and
  3,691 native help assertions passed in `20260916T095118.186660Z`.
  Fixed playback `20260916T095434.339870Z` passed23/26 cases with738 checks
  before reporting the two Spellbreak stalls and the Osmose oracle error.
  Those passed cases remain applicable: the later hooks preserve non421
  behavior; help, state and glyph logic were unchanged.
- Final image `0b871a07b572b0e1baac5a7122c3ba9786fec26f`: all nine build,
  capture and native prerequisites passed in `20260916T101020.802702Z`.
  The Spellbreak animation now finished. Follow-up test corrections account
  for native result retirement and flush Unicorn's translated blocks before
  tracing newly installed observers; they do not change the game image.
- `20260916T101146.526398Z`: prerequisite verification and the three affected
  player flows passed, **732 assertions**. The aggregate report still failed
  on the separate tracing check. Osmose completes in684 frames; Shell-choice
  Spellbreak674 and Protect-choice673. All reach the next unit's native menu.
  Actual MP, exact buff removal, retained enchantment, live choice preservation,
  next-category glyph upload, renderer bytes, AP and inventory are checked.
- `20260916T101218.295155Z`: **2/2 passed**, **3,460 assertions** for presentation
  compatibility. Seven sites, ordinary-action controls, Spellbreak choices,
  two caller stack alignments and projectile styles match original instruction
  behavior with the appropriate weapon operand. Headers remain read-only.

Raw captures, instrumented test ROMs, fixed inputs and complete reports remain
in ignored build directories. The player-flow logger observes results and
fixes only the declared RNG seed; it never supplies hit or damage outcomes.
The instruction-level test observes graphics calls at their ABI boundaries;
the separate mGBA playback establishes real rendering and turn completion.
No full integration suite was run for this bounded interface milestone.
