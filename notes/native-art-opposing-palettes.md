# Opposing-side palette fix and all-class capacity failure

Full engineering remains required; this is not release acceptance. Private
candidate `79e8869552d580469e830c5d07504044ae59553e` includes the action-completion
stage. Selector: `build/art/opposing-palettes/current.json`. Installed7507ca5c,
action5a14e6c7 and performance200ca35b selectors are not promoted or replaced.

## Actual integration defect

The new deterministic `test-art-all-class-capacity` uses the complete original
formation324 record in the disposable Giza event shell. Six generic enemy
templates retain native race, level, position and side; their primary class,
secondary skillset and legal weapon loadout are declared preallocation inputs.
Four existing same-race generic party members provide the complementary classes.
Both fixed story records remain intact. The intended roster is six party, six
enemies and judge, with all ten added classes allocated before play.

The first run on5a14e6c7 fails at frame1571, before deployment, with twelve
variant/unsupported refusals and no allocator failure. Retained failure:
`build/art/all-class-capacity/20260919T062759.747459Z/failed.json`;
runner `20260919T062758.672321Z` is terminal and failed.

Native job property6 reads the low nibble of record+11 at C86DE; property7 reads
its high nibble at C86F4. The renderer authenticated only the first palette.
Opposing bodies use the other source, so their ordinary native palette failed
authentication. This was a missing engineering consumer, not an artwork issue.

Optional private `opposing_palettes=True` derives a second exact reference per
class from property7's source. Preparation, pretracking and reload use the same
full sixteen-color normal/dim comparison. Actual native source colors remain in
the binding for effects. The class's placeholder custom palette stays the same;
this does not author a distinct final enemy color design. No persistent RAM or
history capacity is added. The feature remains private pending full acceptance.

## Verified scope and retained test failures

The matching action-candidate configuration rebuilds its original palette
module4accdb08 byte-exact. Its new connected build and mandatory action-completion
stage produce79e88695. This build evidence is in runner20260919T063449.555676Z;
its five successful build assertions precede an emulator-setup failure.

`test-art-opposing-contract` passes1422 checks in terminal
runner20260919T063641.507146Z. Report:
`build/art/opposing-palettes/20260919T063642.340679Z/report.json`, SHA256
`6dff77521bb2ffef7e8a82e8564bb0654443483fe7b26f6d413b325b95b9d1a7`.
This executes native properties6/7 for every class, authenticates emitted source
tables, tests normal32 and dim19 scales, and rejects each single-color mutation
without changing variants, bindings, tags or visible colors. It does not prove
every opposing-side effect or reload lifetime.

Harness failures remain explicit:

- Runner063255.719695Z used default flags rather than the action candidate's
  fused configuration. Its failed comparison was corrected. The unintended
  rewritten default manifest was retained as observed-baseline-manifest.json
  beside the failed report; its historical provenance was reconstructed from
  the unchanged installed7507ca5c component. No ROM bytes changed.
- Runner063449.555676Z set the Unicorn CPU model after memory initialization.
  Moving that selection into initialization fixes the setup. Its built candidate
  is reused by the contract step, avoiding another identical build.
- Runner063605.022903Z completed1422 assertions but failed in cleanup because a
  local tuple shadowed the manifest backup dictionary. Renaming that dictionary
  fixes cleanup. The subsequent contract run exits successfully. The earlier
  report's passed field does not override its failed runner status.

## Remaining capacity defect

With the opposing-reference fix, the same full-class scenario reaches frame7527
with zero variant/effect refusals, then records three palette-allocation failures.
Retained failure:
`build/art/all-class-capacity/20260919T063642.661267Z/failed.json`.
The ready/idle/Status/return assertions were not reached and are not accepted.

`audit-art-opposing-pressure` passes on these pinned failed artifacts in terminal
runner20260919T064118.768348Z. Report:
`build/art/opposing-pressure/20260919T064119.532943Z/report.json`.
The source index `notes/native-art-opposing-pressure-evidence.json` freezes the
report, RAM, IWRAM, OAM and VRAM hashes and both candidate/fixture ROM identities.

Current OAM requests nine histories:0,1,2,3,4,5,6,7,9. Native graphics occupy
banks0,1,6,7,8,10,11,12, leaving eight. The visible portion of the64x64 8bpp
deployment portrait at(-32,88) uses45 nonzero indices across6/7/8. Native UI and
unmodified objects also visibly use the remaining occupied banks. Increasing
history slots alone cannot create another hardware bank.

This proves a shortage in the current exclusive-bank representation, not an
unsolvable hardware limit or an acceptable reduced class count. The next change
must address palette/tile representation or exact sharing, then rerun this
specific all-ten case and its skipped consumers. Native shared-palette transport
already exists earlier in the asset chain and is a relevant architectural input;
it would need an explicit conversion contract and complete action/performance
proof before replacing custom-color transport. E01-E05 remain open.
