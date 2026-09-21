# Exact pixel scanner block transfers: Move onset still fails

September 18 Pacific / September 19 UTC. Full engineering remains required;
only artwork content is deferred. E01-E05 remain open. These are private trials,
not installed fixes. No player saves, launches, agents or publication changed.

## Implementation

`block_scan=True` extends the packed-plan/unrolled-copy candidate with three
changes in `art-palette-bank-scan.s`: unroll the 512-byte scoped-code copy;
compare four current tile words per loop; copy four cache words per loop through
two ARM block transfers. It still checks every cached byte before reuse, branches
on any word mismatch, rescans from the original tile start, and copies exactly
the existing tile footprint. Pixel masks, transparent index zero, clipping,
source stride, cache indexing and the uncached tail after tile 31 are unchanged.

`burst_scan=True` further compares two source/cache words per ARM load pair and
copies four cache words in one transfer. It frees R7 by retaining the row stride
in eight additional temporary stack bytes. The leaf stack is 48 rather than 40
bytes, so the minimum post-wrapper SP is raised from `03007190` to `03007198`.
The 512-byte code copy and 512-byte interrupt reserve above native resident end
`03006D68` remain unchanged. The incoming wrapper threshold, including its
24-byte saved-register area, is `030071B0`. Deep/external stacks execute the same
leaf from ROM. No persistent RAM or cache-validity assumption is added.

The options are private and disabled by default. The burst option requires the
block option; its test builder includes packed planning, unrolled owner/publish
copies and the mandatory final action-completion stage. Each builder verifies
the default installed palette rebuild and restores existing indexes/manifests.

| Candidate | Selector under build/art/performance | Stage bytes | State bytes |
| --- | --- | ---: | ---: |
| 4f3f4c78f66127e87e031520ac8d7ae04896559b | block-scan/current.json | 252576 | 11316 |
| 93a9cf2cfa306938a83456a25e4b0a0b862dc282 | burst-scan/current.json | 252576 | 11316 |

Both add 232 ROM bytes over packed-plan94770ae8, within the existing reservation.
The block/burst 512-byte bank-leaf SHA256 values are respectively
`3ebbacc5a596bb7065aba1a1756861f5565ebc8d0a55b740305e3a3c04a6c569` and
`1e1bc280b0b2a2cb0e0198a1059a1ef77df28428894fd47ae54e97763f45789f`.

## Verification and retained failures

Every invocation used the declared native-art plan through `Test Expansion.ps1`.
Runner timestamps below have prefix `20260919T`; child paths are under build/art.

| Runner | Exact ID | Result / child report |
| --- | --- | --- |
| 050930.828922Z | test-art-block-scanner | 65091 pass; palette-plan/20260919T050931.547348Z/report.json |
| same | test-art-block-plan | 4744 pass; frame-high-slots/20260919T050935.058710Z/report.json |
| same | test-art-block-build | 8 pass; performance/block-scan/20260919T050936.234427Z/report.json |
| same | test-art-block-consumers | 244 pass; fused-consumers/20260919T050949.887618Z/report.json |
| same | test-art-block-entry | Failed ready palette-shadow equality; live-palette/battle/20260919T050950.795619Z/failed.json |
| 051049.089937Z | test-art-block-frame-events | 31100 pass; native-frame-events/20260919T051049.748327Z/report.json |
| 051243.186493Z | test-art-block-phase-evidence | 6226 pass; native-phase-evidence/20260919T051244.035490Z/report.json |
| same | test-art-block-response-budget | Five metrics fail; response-budget/20260919T051244.557756Z/failed.json |
| 051414.953375Z | test-art-burst-scanner | 70347 pass; palette-plan/20260919T051415.733062Z/report.json |
| same | test-art-burst-plan | 4744 pass; frame-high-slots/20260919T051418.754232Z/report.json |
| same | test-art-burst-build | 8 pass; performance/burst-scan/20260919T051419.898995Z/report.json |
| same | test-art-burst-consumers | 244 pass; fused-consumers/20260919T051434.475358Z/report.json |
| same | test-art-burst-entry | Failed ready palette-shadow equality; live-palette/battle/20260919T051435.530656Z/failed.json |
| 051605.423948Z | test-art-burst-frame-events | 31110 pass; native-frame-events/20260919T051606.061880Z/report.json |
| same | test-art-burst-scanner | Extended boundary proof70360 pass; palette-plan/20260919T051618.301291Z/report.json |
| 051751.403667Z | test-art-burst-phase-evidence | 6226 pass; native-phase-evidence/20260919T051752.203176Z/report.json |
| same | test-art-burst-response-budget | Two metrics fail; response-budget/20260919T051752.699275Z/failed.json |

All runner input fingerprints remained unchanged; all runners/cleanup are
terminal. No component failure was discarded. Entry failures remain failed,
with later entry assertions skipped. Independent phase checks are not a waiver.

Scanner coverage retains the prior exact independent pixel-mask oracle and
50 authenticated menu captures, plus zero-primed changes at every byte of a
64-byte tile, including the final comparison lane. Values 1 and 240 distinguish
opaque bank-zero pixels from transparency and distant banks. Subsequent stack
variants exercise exact cache hits; row/stride matrices exceed the 32-tile cache.
Source and cache fences are checked. Burst checks include both word alignments.

The final scanner run adds exact threshold observations: incoming SP `030071AC`
uses ROM; `030071B0` and `030071B4` execute the copied leaf. An external stack
uses ROM. The complete native region plus 512-byte interrupt reserve through
`03006F68` is unchanged in each boundary case, and the leaf remains exactly 512
bytes. These are component stack bounds, not an exhaustive interrupt workload.

The plan test compares complete OAM, palette, plan/padding, cache and backup
against the same-input original planner. The complete composition test includes
split histories, highlight fallback and skipped palette-DMA states. Each live
instruction-observation report verifies all 1024 complete state/frame pairs
against ordinary emulation, plus current-demand and phase observations.

Trace SHA256 values, block then burst:
`459b9e45284701d98708b664f7a8dca506019f66c4208d7babf71f063d449a96`
and `0f507592220e1badf05c9399c9eda9176b3866d1d7ba901a54c2b55194a3b7d8`.

## Response and cost

| Trial | Offset | Action | Active start/end/duration | Same-ROM bypass |
| --- | ---: | --- | --- | --- |
| Block | 0 | Move | 24/71/47 | 24/70/46 |
| Block | 4 | Move | 25/73/48 | 24/71/47 |
| Block | 0 | Cancel | 29/29/0 | 29/29/0 |
| Block | 4 | Cancel | 30/30/0 | 30/30/0 |
| Burst | 0 | Move | 25/72/47 | 24/71/47 |
| Burst | 4 | Move | 24/71/47 | 24/71/47 |
| Burst | 0 | Cancel | 30/30/0 | 30/30/0 |
| Burst | 4 | Cancel | 30/30/0 | 30/30/0 |

Burst still fails Move start/end by one frame at offset 0. Both Move durations
and both cancel responses match its control, but that is not E01 completion.
Absolute ready/onset phases differ across candidates: compare each candidate to
its own bypass, not to another candidate's starting frame.

Mean bank-span calls at offset 0 fall from packed-plan9.868/9.719 lines
(Move/cancel), to block8.162/8.001, to burst7.410/7.193. Burst composition means
are 15.130/15.214 lines for Move and 14.092/14.083 for cancel at offsets 0/4;
maximum28.419. The block maximum was28.927; packed-plan31.071. These are real
cycle reductions but not full response acceptance.

The remaining common costs in burst at offset 0 are owner composition3.802/3.935
lines per frame, variants preparation0.878, provisional confirmation0.435 and
palette publication2.072/2.066. Native original composition itself is2.778/2.815.
Full 8bpp plan calls occur25 Move/9 cancel frames; those calls include bank-span
costs, so do not add nested measurements twice.

Next target common ownership/publication or related current-frame work while
preserving all native/history/color proofs. Retain the unresolved entry-shadow
comparison and the one-frame Move onset failure. Continue other action/UI,
capacity, campaign/save and final delivery gates using applicable existing
evidence. Action5a14e6c7, defaultfa3d12b4 and installed7507ca5c stay unchanged.
