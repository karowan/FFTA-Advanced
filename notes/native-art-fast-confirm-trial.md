# Current-key confirmation and deployment palette attribution

Full engineering remains required. Only final artwork content and authored poses
are deferred. E01-E05 remain open; this checkpoint does not promote or package a
build. Private candidate `390e4b0420c546f7afb2c78d5771924e0b3c308e` resolves through
`build/art/performance/fast-confirm/current.json` and includes action completion.
Action candidate5a14e6c7, default palettefa3d12b4 and installed7507ca5c are unchanged.

## Optimization and exact response result

On the preceding burst-scanner candidate, common-frame confirmation still
walked20 history keys individually. The optional `FFTA_ART_FAST_CONFIRM` path
compares all five current aligned words to the confirmed keys. If all20 bytes
already match, the original scalar function would leave them unchanged for
every request mask. Otherwise the original scalar loop runs unchanged. Unaligned
pointers also use that loop. No cached validity assumption, RAM layout, palette
history lifetime or persistent state is added.

Compiled ARMv4T differential testing compares all256 bytes surrounding the two
inputs/outputs, including fences. It covers all256 equal byte values; all20
mismatch positions with0/127/159/160/254/255; zero, single and full request masks;
64 deterministic mixed cases; four alignment combinations and both stack residues.
936 cases times8 configurations =7488 passing comparisons.

The new confirm mean is about0.125 scanlines versus the prior0.435. Complete
composition means are14.910/14.906 scanlines for Move at offsets0/4 and
13.782/13.771 for cancel. Peaks are28.110 and22.454 respectively. These are
measurements of this bounded mixed battle, not worst-case engine limits.

| Input offset | Action | Candidate start/end/duration | Same-ROM composition bypass |
| --- | --- | --- | --- |
| 0 | Move | 24/71/47 | 24/71/47 |
| 4 | Move | 24/71/47 | 24/71/47 |
| 0 | Cancel | 30/30/0 | 30/30/0 |
| 4 | Cancel | 30/30/0 | 30/30/0 |

The response gate now passes all13 checks. This eliminates the measured paired
Move/cancel excess at the two declared offsets. It does not establish equivalent
deployment cadence, demanding encounters, every UI/action or full E01 acceptance.

| Declared ID | Checks | Report under build/art/ |
| --- | ---: | --- |
| test-art-confirm-contract | 7488 | fast-confirm/20260919T052435.335918Z/report.json |
| test-art-confirm-build | 8 | performance/fast-confirm/20260919T052436.229956Z/report.json |
| test-art-confirm-consumers | 244 | fused-consumers/20260919T052452.125069Z/report.json |
| test-art-confirm-frame-events | 31133 | native-frame-events/20260919T052554.814666Z/report.json |
| test-art-confirm-phase-evidence | 6226 | native-phase-evidence/20260919T052751.745450Z/report.json |
| test-art-confirm-response-budget | 13 | response-budget/20260919T052752.279647Z/report.json |

Runners052434.526701Z (entry failed after the first three passes),
052554.009473Z and052750.779971Z on20260919 are terminal with unchanged inputs.
The frame report SHA256 is
`4604a27713243e9649b62b6e2f3d25ac5b07c48d60f8c1fadb47dd538ea01b5f`.
All1024 observed complete states and frames match ordinary execution. Phase
proof covers full native shadow preservation, original BG phases, native DMA
decisions and VBlank boundaries; it does not waive the separate entry failure.

## Entry mismatch: actual native writer established

`test-art-confirm-entry` still fails raw native-shadow equality at ready:
`build/art/live-palette/battle/20260919T052453.374146Z/failed.json`.
The difference is exactly seven OBJ colors, bank10 indices2..8, at
`03003BA4..03003BB1` (full-shadow byte offsets836..849). Candidate and control
have different rotations of the same seven values. The other1010 bytes match
at every ready/idle sample. The ready input routes finish30 frames apart.

Existing entry samples locate the first divergence between entry6 and entry7;
the full shadows match at entry6. `test-art-confirm-entry-source` reuses the
existing deterministic route with a new optional `--entry-checkpoint 6`. This
only retains state/RAM/IWRAM and changes no inputs or acceptance. Runner
20260919T053400.261708Z reproduced the same raw ready-shadow failure at
`build/art/live-palette/battle/20260919T053401.085987Z/failed.json`. Later mixed
acceptance assertions are still skipped; neither failed report is relabeled.

`test-art-confirm-entry-trace` replays only that608-frame interval, twice per
ROM: ordinary execution and read-only observed execution. Each complete native
state and framebuffer must match. The source is authenticated by explicit pins
in the committed script. The paired parent here has only the status shortcut;
it is not the same-ROM composition bypass used for the response gate.

The first trace2467 found **no calls to08146864**. The native rotation-task
hypothesis was therefore rejected. Adding Thumb store observation found the
tail-color store at **080BA694**, inside original deployment callback080BA66C.
The final trace observes its actual start/end and counter too:

- The unchanged native code increments its signed byte counter at context+A0.
  Every sixth call it copies12 bytes from03003BA6 to03003BA4 and appends the
  saved first color at03003BB0. That is a left rotation of seven colors.
- Every observed callback leaves the entire1024-byte shadow exactly equal to
  that operation, or unchanged for an ordinary counter tick. Every actual
  counter follows the native0..5 progression. No phase normalization is used.
- Parent:591 deployment calls,99 shifts,591 foreground completions. Candidate:
  583 calls,97 shifts,584 foreground completions. Initial counters are4 and3.
  These raw counts and timings remain in the report.
- Every one of1216 compositor invocations preserves the entire native shadow.
  The final shadow in each replay exactly reproduces its original entry7 sample.

Final trace **7169 passes**, runner20260919T053954.688803Z:
`build/art/entry-palette-trace/20260919T053955.473091Z/report.json`, SHA256
`456852af14ede38eb3b71567fdc6dd6762e9e79a98865cf6d030d95aa42a826e`.
The earlier narrower traces remain at053626.821412Z and053741.967791Z in the same
artifact family; their2467 passing checks did not identify the complete writer.
Thumb stores alone omit the native ARM copy, BIOS and DMA: attribution instead
uses the unchanged native code and complete start/end shadow and counter proof.

This establishes native animation phase as the seven-color mismatch source in
the first divergent interval, rather than a malformed color produced by the
compositor. It also exposes a real deployment update-cadence difference. It
does not independently attribute all skipped foreground work, close the full
entry route, or accept the remaining latency. Keep the raw equality test failed.

## Next engineering work

Use the authenticated entry6 state to profile the deployment interval's actual
foreground/composition costs and native frame scheduling. Avoid repeatedly
rebuilding a full route. Establish the cause and acceptance of the remaining
cadence difference, alongside E02 action/UI consumers, E03 scripted/secondary
capacity, E04 full-game/save reconciliation and E05 final review/rebuild/package.
Reuse existing current Fight/Combo/auxiliary and historical campaign evidence
where applicable. No player save, launcher, installed build, agents or remote
publication was touched. All test runners and cleanup are terminal.
