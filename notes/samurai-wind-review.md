# Wind Draw implementation and scripted evidence

September14,2026. Private candidate
`f71fceb6a7d6d183cd1fcb8de4513f6e18376320`, based on assembled d156.
Wind Draw348 adds a seventh implemented Samurai action. The previous six
actions retain their historical complete-suite acceptance on41c51aa1; this
new candidate has focused Wind and law evidence, not complete-class or full
expansion acceptance. Main assembled action count remains10.

## Behavior

Wind Draw costs4MP once, requires the primary katana, and deals1.00P Wind
damage independently to enemies in a cardinal three-tile line. Centered
applies5/4 once to the entire action and is consumed even on a complete miss.
The existing physical finalizer combines distinct damage factors before one
division. New-action proc, drain and primary-only classification includes
Wind Draw; its element is Wind regardless of the weapon's element.

`samurai-area.c` uses the explicit evaluated origin rather than stale unit
coordinates during Move previews. Each successive tile must be in bounds,
valid, nonzero height, free of native impassable terrain flags1/8, and within
two height levels of the origin. The first invalid tile ends the line.
Units do not block it. Native area records retain their unused fourth byte;
at most three records are written.

The native directional selector requires range mode0x40. A numeric range3
allowed the first prototype's east/south cases but failed west selection.
After this fix, the installed custom area and geometry routines still enforce
the approved three-tile maximum. The UI hook preserves the native caller's
direction; every other action delegates to the existing area dispatcher,
including the previously fixed Soldier/Gladiator arcs.

## Evidence

- `test-samurai-wind.py`:55,203 checks. Native area-list differentials for347
  original actions and10 implemented actions; all four directions; map edges;
  obstruction positions1/2/3; height and terrain boundaries; preserved unit,
  map and descriptor; output guards; installed geometry; and Wind element
  across461 item IDs and both stack residues.
- `test-samurai-wind-in-game.py`:220 checks. Six fixed scenarios cover all
  four directions after actual Move, a middle obstruction, and a friendly
  unit within the line. Native recipient-list instrumentation and unmodified
  execution agree. Two fixed seeds exercise real hits and misses. A separate
  native-P control verifies Centered damage. Silence, preview/cancel, one MP
  payment, turn completion, AP/inventory preservation and native suspend/cold
  resume pass. Friendly units take no Wind Draw damage.
- The focused six-step run passed with unchanged inputs:
  `build/expansion/test-runs/20260914T233148.912398Z/report.json`.
- Extended `test-samurai-laws.py`:43,840 checks, including Wind element2,
  primary katana weapon laws, all347 original actions across20 law kinds and
  existing Guarding Draw status-law coverage. Its focused four-step run passed:
  `build/expansion/test-runs/20260914T233400.023604Z/report.json`.

The runner now declares the retaliation test's dependency on its matching
in-game fixture/report. Its seven deterministic self-tests pass. They are
also available as `Test Expansion.ps1 -Only test-runner-self`.

## Remaining work

Moon Blossom and Higanbana/Blade Wound, Samurai supports/reactions, broader
AI and cross-class acceptance, main integration and the complete expansion
regression remain outstanding. The player launcher and save were untouched.
