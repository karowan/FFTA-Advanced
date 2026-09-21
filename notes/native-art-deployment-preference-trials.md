# Deployment preference and rectangle scan trials

Full engineering remains required; E01-E05 are open. Only final art content is
deferred. No candidate in this note is promoted. All runners are terminal.
The last committed starting point wasefd1efa; its390e4b04 candidate passed the
two-offset battle response gate but retained a deployment cadence difference.

## Measured result and retained failure

| Candidate | Deployment composition mean/peak, scanlines | Deployment calls / color shifts in608 frames |
| --- | --- | --- |
| Status-only parent | 2.796 / 2.817 | 591 / 99 |
| 390e4b04 current-key confirmation | 22.081 / 22.554 | 583 / 97 |
| 20fa53f7 joined full-width rows | 22.077 / 22.551 | 583 / 97 |
| eae534ca same-call preferred-bank validation | 19.244 / 19.658 | 583 / 97 |
| 200ca35b rectangle conflict scan | 15.981 / 17.380 | 585 / 98 |

The rectangle candidate recovers two deployment updates, but **fails the battle
response gate**: cancel start/end at offset0 are+3 frames, and Move start at
offset4 is+1. Faster aggregate rendering does not imply equal response timing.
Native phase proof6226 passes; neither that nor faster Move duration waives the
three failed metrics. Raw entry-shadow equality also remains failed in every
trial. Keep those failures and later skipped entry assertions explicit.

| Rectangle input offset/action | Active start/end/duration | Same-ROM bypass |
| --- | --- | --- |
| 0 Move | 23/70/47 | 23/71/48 |
| 4 Move | 25/71/46 | 24/71/47 |
| 0 Cancel | 32/32/0 | 29/29/0 |
| 4 Cancel | 29/29/0 | 29/29/0 |

Joined and prepared-preference traces retain exact24/71/47 Move and30/30/0
cancel results on both offsets, matching their controls. They were not promoted
or independently subjected to a new final phase/response gate; the formal final
gate this batch ran on rectangle200ca35b and failed as above.

## Implementation and cost attribution

`art_composition_costs.cost_sites` accepts extra declared callers while retaining
exact compiled BL authentication. The entry observer supports a committed input
index for each exact-ROM source, and still verifies every complete native state
and framebuffer against fresh ordinary emulation. It now independently rebuilds
the complete current OAM demand classification at the actual fused consumer.
All recorded native cycle callbacks preserve exact counter/color semantics.

Initial profiling located11.434 scanlines inside `preferred`, which includes
OAM reclassification as well as pixel checks. Treating that inclusive number
as only pixel scanning was too broad. The joined-row trial preserved correctness
but did not materially change this scenario. The actual expensive object is
8bpp64x64 at(-32,88), horizontally flipped, with attributes2058/D1E0/0640.
Its visible source rows are strided, not fully contiguous.

- `FFTA_ART_JOINED_ROWS` combines adjacent full-width source rows into a single
  existing exact scan. Horizontally clipped rows retain the old path. Kept as an
  isolated reproducible trial; no target-scenario speedup is claimed.
- `FFTA_ART_PREPARED_PREFERENCE` uses the current invocation's already verified
  occupied/requested masks instead of reclassifying every4bpp OAM object. It
  preserves the prior single-owner preferred bank and plan diagnostics, and
  scans every actual8bpp footprint. No demand survives a composition invocation.
- `FFTA_ART_RECT_CONFLICT` computes the identical conservative visible rectangle
  and copies the existing160-byte ARM scan leaf once for its strided rows. It
  does not scan gaps, change clipping or cache pixels across frames. The wrapper
  preserves R4-R10/LR, uses32 stack bytes and then the same160-byte code/28-byte
  leaf scratch. Post-push cutoff03007024 preserves native resident memory through
  03006D68 plus the full512-byte interrupt reserve. Actual incoming SP below,
  at and above03007044 and an EWRAM stack are tested, including exact copied
  leaf bytes, stride gaps and last-row conflicts. ROM fallback remains available.

No persistent RAM, heap endpoint, save field, history count or art source changes.
Each private builder includes the mandatory action-completion stage and checks
that its default palette build remains byte-exact. The unaccepted trial selectors
are `build/art/performance/{joined-rows,prepared-preference,rect-conflict}/current.json`.
Full rectangle SHA1: `200ca35b0c48671d7d96874e14ec6cef082287fa`.
Full prepared SHA1: `eae534ca40d16f3034e5ed84d0836a04624f1cfc`.
Full joined SHA1: `20fa53f741593901049b984125a6a97637d8cd54`.

## Reproduction and evidence

All runs use `Test Expansion.ps1 -Plan scripts/native-art-test-plan.json -Only`
with the exact IDs below. No broad integration, gameplay job restart or player
save/installed launcher mutation occurred. Runners retained unchanged inputs.
Only a source comment was clarified after the rectangle runtime runs.

| Run / declared IDs | Result and report under build/art/ |
| --- | --- |
| 20260919T054522.418595Z: test-art-confirm-deployment-costs | 7170; entry-palette-trace/20260919T054523.208935Z/report.json |
| 20260919T054810.798119Z: test-art-joined-scanner, -plan, -build, -consumers, -entry | 48009/4744/8/244 pass; entry fails at live-palette/battle/20260919T054832.319893Z/failed.json |
| 20260919T054950.020560Z: test-art-joined-deployment-costs, -frame-events | 7170/31133; entry-palette-trace/20260919T054950.788590Z/report.json and native-frame-events/20260919T054959.946901Z/report.json |
| 20260919T055334.162855Z: test-art-preferred-plan, -build, -consumers, -entry | 4744/8/244 pass; entry fails at live-palette/battle/20260919T055352.720540Z/failed.json |
| 20260919T055530.500745Z: test-art-preferred-deployment-costs, -frame-events | 8361/31133; entry-palette-trace/20260919T055531.304982Z/report.json and native-frame-events/20260919T055541.313225Z/report.json |
| 20260919T055950.440713Z: test-art-rect-scanner, -plan, -build, -consumers, -entry | 48079/4744/8/244 pass; entry fails at live-palette/battle/20260919T060011.122589Z/failed.json |
| 20260919T060114.137442Z: test-art-rect-deployment-costs, -frame-events | 8369/31134; entry-palette-trace/20260919T060114.898310Z/report.json and native-frame-events/20260919T060124.827800Z/report.json |
| 20260919T060403.839540Z: test-art-rect-phase-evidence, -response-budget | 6226 pass, response13 evaluated/three metrics failed; native-phase-evidence/20260919T060404.775785Z/report.json and response-budget/20260919T060405.306831Z/failed.json |

The abbreviated suffixes in this table expand with the same `test-art-joined-`,
`test-art-preferred-` or `test-art-rect-` prefix as the first ID in their row.
Exact source pins are committed in native-art-joined-row-evidence.json,
native-art-preferred-evidence.json and native-art-rectangle-evidence.json.
Rectangle deployment report SHA256:
`342b7d376f92af50ef7fa7f90aca602dc857407ca46316d4957023071b6db3d3`.
Rectangle frame report SHA256:
`7b233f5bfdd45598974dd297f1d0a1fe6338447c1ac420068a5a3545b3f77515`.

Next separate the remaining controller/input scheduling differences from raw
render cost using the retained paired events. Do not treat matching two offsets
on390e4b04 as broad phase-independent acceptance, nor promote200ca35b based on
its lower CPU cost. Continue E02-E05 using existing applicable evidence. The
new static capacity findings are in native-encounter-capacity-inventory.md.
