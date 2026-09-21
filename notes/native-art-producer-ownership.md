# Native producer ownership: one-frame response gaps remain

September18 local / September19 UTC. Full engineering remains the goal. This
is another private candidate, not a release. E01–E05 remain open; only final art
and artist-authored frame content may be placeholders. No player files, installed
indexes, launches or publications changed. No agents. All runners terminal.

## Implementation and authority

Candidate `a42c04e18e3584a8447564aef4d06ac8f10ed93e` builds on the verified prefix
candidate12562f6f. `native_owner_producer=True` requires both the native-prefix
proof and scoped ARM leaves; the builder remains private. Stage249800bytes,
unchanged11316-byte live state and12KiB reservation. Defaultfa3d12b4 reproduces
exactly; installed7507ca5c and its source/index manifests are restored unchanged.

The new `ffta_art_owners_compose_native` entry is used only immediately after
the authenticated native12BC compositor. Its DMA copies already establish that
every shown main-object attr0..2 equals the selected source. There is no OAM or
source writer between that native call and ownership composition. Thus this
specific entry avoids revalidating the entire hardware/main-source span and
avoids a second128-byte scratch tag array. It still authenticates each enabled
custom owner's recorded attributes against all three current source attributes,
applies native clipping, and rejects invalid counters/uninitialized owner banks
before publishing anything. Stale or overwritten owner records remain unowned.

The generic filtered ownership function is unchanged and still refuses actual
hardware/source mismatches atomically. Do not use the new entry for arbitrary
hardware snapshots or imply it independently detects such a mismatch. Its
authority is the same-invocation native producer, not a prior-frame cache.

The compiled native-only ARM leaf is528bytes, stack24bytes; the wrapper's
post-save minimum SP is03007190, preserving512 interrupt bytes above native
resident code03006D68. Exact deep/external-stack fallbacks remain. The ordinary
scoped ownership and publish leaves are retained for their existing consumers.

## Evidence

All tests use Test Expansion.ps1 and scripts/native-art-test-plan.json. IDs and
purposes were announced before execution. Complete failures/logs are preserved.
All timestamps below have20260919T prefix; child paths are under build/art.

- Runner011807.453018Z: `test-art-native-owners-contract` passes9436 checks at
  palette-owners/011808.134924Z/report.json. Native composition plus all756 count
  combinations compare native-only tags/requested classes/bank masks against
  the general hardware-authenticated bridge. Both bank selections, clipping,
  actual affine tail writes, stale/reset records, land/water resources, output
  alignment, both scoped stack alignments, ROM fallbacks and malformed-counter
  atomic refusals are covered. Generic hardware mismatch refusal still passes.
- Same runner: private build8 and isolated profile292 pass. Profile is
  compose-isolation/011822.321584Z/report.json. Entry fails the raw paired native
  palette-shadow comparison at live-palette/battle/011822.564846Z/failed.json.
  Later entry assertions remain skipped; later evidence does not relabel them.
- Runner012019.786073Z: `test-art-native-owners-frame-events` passes29084 checks,
  native-frame-events/012020.476681Z/report.json. Every observed frame matches
  ordinary execution's complete native state/framebuffer (1024 total). Every
  one of512 actual native-only ownership invocations independently validates
  arguments, ready bank/counters, ALL copied main attr0..2, and ALL resulting
  owner tags/requested classes. It also retains the complete omitted-tail proof
  for all512 actual prefix applications and actual inclusive cycle observations.
- Runner012123.658506Z: native phase/deadline6226 passes at
  native-phase-evidence/012124.486291Z/report.json. Response-budget fails four
  metrics, with13 authenticity/coverage checks passing, at
  response-budget/012125.016514Z/failed.json.

Trace SHA256:
`021a28e408e437dbd563cf6e1826e63e5e57d8ba9cc9d870f3dd5a19cdd2acd1`.
The immutable frame/phase/response IDs pin this exact ROM and entry capture.
The actual class mask is the all-ten-class builder's1023. No reduced-artwork
scope, palette-phase realignment or response waiver is used.

| Offset | Action | Active start/end/duration | Bypass start/end/duration |
| --- | --- | --- | --- |
|0|Move|25 /72 /47|24 /71 /47|
|4|Move|23 /70 /47|23 /70 /47|
|0|Cancel|30 /30 /0|30 /30 /0|
|4|Cancel|31 /31 /0|30 /30 /0|

Ownership costs2.56–2.57scanlines, down from3.86–3.90. Mean total composition
is17.44/17.65 for Move and16.22/16.23 for cancel; minimum13.53, peak32.58.
Move duration still matches47frames at both offsets, but Move start/end at
offset0 and cancel at offset4 remain1frame late. The bypass starts differ from
the prior candidate's seed; compare each candidate only with its own exact-ROM
control, not by cherry-picking absolute frame numbers between experiments.

No measured VBlank overrun; nevertheless this does not close E01. Native
producer proof29084 and phase proof6226 do not override the failing response
gate. This is further measured progress, not a complete performance fix.

## Next work

The largest remaining block is palette planning/publication, roughly7.1–8.5
scanlines inclusive in these windows. It classifies the current native sprite
prefix again after fresh ownership has examined it. Investigate combining those
same-invocation passes: derive unowned4bpp bank demand and8bpp object indices
while authenticating current ownership, then map requested classes to current
histories before exact pixel planning. Preserve late native-highlight filtering,
split histories, refusal-before-hardware-write, complete8bpp pixel reads, and
single-owner preferred-bank semantics. Independently compare any precomputed
demands with the complete current OAM/tags at every observed use. This is a
proposed next implementation, not implemented or accepted here. No generic
repeated-frame cache or queue-only writer assumption is justified.

The earlier full-game campaign work is real and should be reused where still
applicable: historical A01/V06 and R02/R03 on1b070824 cover representative earned
territory/final-entry connections, ending/credits/clear-save/reset/Continue,
postgame consumers, Shara capacity/cold lifecycle and separate delivery. See
notes/release-acceptance.md and the historical checklist rows. That does not
automatically establish current art-hook/heap/save compatibility. E04 still needs
the final engineering impact/evidence reconciliation; do not restart completed
job implementation or replay all campaign tests merely because ROM hashes differ.
