# Twenty histories and ten-class palette transport

September 18, 2026; follows `3591d34`. Built-in imagegen only. Existing drafts
are technical inputs; final sprite refinement remains deferred. This checkpoint
does not close G01-G04 or install a new player build.

## Candidates and implementation

- Original ten-history candidate remains
  `05c66b387e415d59d519ca409d911311b39019d8` through
  `build/art/live-palette/poc.json`; stage161244/state8096.
- Separate twenty-history, Human Dark Knight-only candidate:
  `394e96abc4b28befca33353a0c60d45227b12c2d` through
  `build/art/live-palette/history-current.json`; stage161412/state11292.
- Separate all-ten-class candidate:
  `4b35081ba8d69f6ebf997607c119931e303a6106` through
  `build/art/live-palette/all-classes-current.json`; stage242976/state11292.
  Enabled mask1023. Both larger candidates reserve0203C000..0203F000 (12KiB).

`art-palette-limits.h` separates ten source classes from configurable history
capacity. History is a (class,native-bank) pair. Bindings, visible colors,
variant mappings, task retirement and planner request masks support twenty
slots. Extra slots reset without reading nonexistent source-class palettes.
Request bits above15 use32-bit storage; physical palette capacity stays16.
Unknown/overflow demands still refuse, and transformed absent histories are
not evicted. The advertised compile limit excludes32 to avoid a32-bit shift
at the planner's upper-mask check. Builder options intentionally allow10/20.

All three heap-limit veneers use the chosen reservation. Larger builds export
twelve compiled layout offsets; selected tests consume those offsets instead
of assuming the old layout. Default compilation reproduced05c66b38 byte-exact.
The native battle-wrapper observer now selects TI925T ARMv4T before mapping.

All-class transport authenticates the ten catalog draft sources, palettes,
converted indexed frames and original native palette references. Human Dark
Knight retains its six-frame march-v2 input; other jobs use their catalog
technical conversions. These are repeated placeholder poses, including the
Samurai catalog idle draft, not complete production animations. It replaces
790 populated land/water action descriptors and preserves4064 frame timing/
command records. Identical sequence blobs are shared to stay inside the existing
ROM reservation. Exact input hashes and assignments are in the private manifest.
The separate wheel miniature/portrait consumers are unchanged by this builder.

## Passing evidence

All paths below are private, ignored artifacts. Runtime used the declared runner.

| Runner (20260918T prefix) | Declared test | Result and report |
| --- | --- | --- |
| 104843.690960Z | test-art-palette-history-capacity | 115; build/art/history-capacity/20260918T104844.388249Z/report.json |
| 105234.680530Z | test-live-art-history-native | 1153; build/art/live-palette/native/20260918T105235.340822Z/report.json |
| 105234.680530Z | test-live-art-history-appearance | 1595; build/art/live-palette/fades/20260918T105237.928542Z/report.json |
| 110046.629063Z | test-live-art-all-classes-native | 9793; build/art/live-palette/native/20260918T110047.265672Z/report.json |
| 110046.629063Z | test-live-art-all-classes-menu | 963; build/art/live-palette/menu/20260918T110050.719766Z/report.json |

The component uses ten authenticated catalog palettes and retained deployment
colors:17 histories, off-screen black/restore, late appearance in a high slot,
20-slot retention,21st-history refusal,16 hardware banks and atomic17-bank
refusal. This is not an installed all-class effect proof. Its Dark Knight input
is the catalog palette, distinct from the live march-v2 selection.

The twenty-history native test covers byte-exact rebuild and three heap starts,
new/legacy clear endpoints and unrelated-clear controls. The appearance test
checks eight actual hide/reset/rotate-or-cycle/reveal cases, including the first
visible frame. Only Dark Knight is enabled in that candidate.

The all-class native test checks every declared patch/sequence/pixel and clear
boundary. The menu test cold-loads all ten same-race profiles separately, checks
five idle samples, cancel/reopen/second cancel/world return, exact generated
hardware colors, paired native shadow/unowned palette and canonical unit bytes.
One Geomancer wheel screenshot was inspected; that is no final-art review.

Read-only capacity audit now accepts `--candidate-manifest` and checks compiled
layout provenance. All-class report
`build/art/palette-capacity-audit/20260918T110430.872609Z/report.json` finds17
potential histories, capacity20 and mask1023. This is not maximum reachable
demand or simultaneous all-class hardware acceptance.

## Failed mixed-battle attempts retained

`test-live-art-mixed-classes-first` failed in each following runner; the runner
stopped before `test-live-art-mixed-classes-second`, which remains unrun.

1. Runner110445.057365Z, battle110445.789977Z: changing Montblanc to a generic
   Moogle plus four other same-race profiles reaches a different control roster.
   The old fixed formation refuses it. Retained actor records contain player
   slots0..4 and an additional native object at unit35F4; Viera slot5 is absent.
2. Runner110625.822251Z, battle110626.440732Z: one extra deployment selection
   still fails the explicit five-profile deployment assertion in the control.
   This did not test candidate mixed rendering.
3. Runner110742.737729Z, battle110743.414156Z: keep Montblanc unchanged and use
   four profiles (Human Dark Knight117, Bangaa Dark Knight118, Scholar120,
   Bard122). The control reaches the required turn; the candidate fails
   `Native turn did not advance` after the declared6300-frame bound while
   waiting from unit020004A0. Failed state/image/RAM/IWRAM/VRAM and inputs remain.

The final failed RAM records binding starts/completions/unsupported14/14/7,
refusals(variants/setup/target/tick)=0/0/7/0, applied/restored6918/6918,
allocation failures0, last compose168..191 and display164. Keys include
105,16,32,64,96. These are observations, not a causal explanation: seven rejected
target mappings and the turn timeout require separate diagnosis. Do not claim
successful mixed coexistence, zero unsupported effects or a fixed timing gate.
The four-class test narrowing is explicit; it does not close the earlier
five-class deployment failure or Moogle coexistence coverage.

## Continue here

Inspect the exact4b35081b failed state/inputs before another runtime run. Resolve
the candidate turn progression and identify the seven natural target-mapping
refusals without weakening their checks. Then rerun the affected first group;
run the second group once that is justified. Preserve Montblanc's story identity
in this fixture. Samurai/Moogle mixed coverage, all-class effects, natural scene
lifetimes, maximum heap use, cross-bank identity and timing remain open.

The old05c66b38 full-battle phase/input failure remains applicable to that ROM;
no new all-class movement acceptance exists. Reuse the passing menu/import/
capacity evidence. No broad suite, final artwork, new package or G-gate closure.
Existing player saves, launchers, installed preview and running game are unchanged.
