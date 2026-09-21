# Full engineering delivery accepted

Root accepts E05 and the complete E01-E05 engineering scope. The delivered game
is the original USA campaign plus approved v0.7 gameplay and connected native
graphics. Only final artwork and artist-authored poses are deferred. This
supersedes technical-preview completion; it does not waive broken engineering.

## Delivered identity

- Source checkpoint:f07411c4c1c236fedeedaea38283cf8a8e519666.
- ROM:a28b624bb13c8f2f2597a4d4bd3999b17c234b99,33,554,432 bytes.
- ROM SHA256:029547bb57325915a7d4a97f9e0e19b096645bf3d25d131c35c216ef6da41e78.
- Bundle:build/releases/v0.7-engineering/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/bundle-461ec79a7f20f413.
- BPS SHA256:8b18d8f831bcb29f8f0c0eb2731d684b55b8db6bc7c93d9633ffa55d2a695a49.
- Player ROM:roms/play/expansion-v0.7-engineering/FFTA_Expansion_v0.7.gba.
- Launcher:Play Expansion.cmd. Independent storage:saves/expansion-v0.7-engineering.
- Previous gameplay launcher:Play Previous Expansion.cmd, retaining its old ROM
  and saves/expansion-v0.7 storage. Vanilla/development/showcase/preview retained.

## Final verification

Declared runner20260919T103642.038969Z passes package-full-engineering and
test-full-engineering-launcher. Package verifies all accepted current/historical
source pins, evidence hashes, exact current ROM and full source rebuild report.
BPS generated twice is identical; clean-source patch application yields exactly
the delivered ROM, and mutated source is rejected. 31 immutable guide/reference
files and the full engineering acceptance certificate accompany the patch.

Actual launcher test passes145 checks, including ValidateOnly with the shipped
ROM and all three explicit mGBA save/state/screenshot overrides. An isolated
wrong-ROM fixture, in a path containing spaces, is rejected before launch.
The test preserves all17 protected files including the newly installed ROM;
the package preserves its16 pre-existing protected games/saves/launchers.
No game was launched, save imported, running session closed or remote published.
Sourcef07411c passed the index asset guard; no ROM, patch, tools, generated art,
private inputs or raw logs were committed.

Initial runner20260919T103249.838227Z failed at Node's read-only Git child process
with EPERM before delivery writes. Same source and two declared IDs passed under
the approved external execution permission. Keep the original failed log/report;
this was a sandbox process restriction, not a fixed game or package algorithm.
See native-art-engineering-delivery-evidence.json for exact package/test pins.

The first package/launcher run103324.196882Z passed22 checks. A subsequent
static link audit found a reference linked from the class specification was
absent from the standalone bundle. That audit failure is retained separately;
the original22-check result is unchanged. Packaging sourcef07411c now includes
the transitive local Markdown/JSON references, and the final145-check run
verifies every relative file link. The ROM and deterministic BPS are identical
to the earlier package. Earlier bundleb57a77d3f5996896 remains immutable; current
bundle461ec79a7f20f413 supersedes it for complete reference documentation.
Packaged checkpoint documents are snapshots and retain their historical bundle
references; this later final note identifies the selected delivery.

The preceding final assembled audit passes1091 checks /592 authenticated files;
E01-E04 reasoning is in native-art-final-engineering-review.md. Fresh eight-stage
source gameplay prefix plus corrected complete eleven-stage art suffix reproduce
the shipped ROM byte for byte. The original failed enclosing build stays failed;
the successful suffix reused the exact fresh prefix, not a historical binary.

## Root completion and remaining art work

The measured Move/cancel delay and deployment cadence regression are resolved.
Runtime custom palette ownership/scanning/remapping consumed additional CPU and
changed foreground/input cadence; native shared-palette conversion moves that
work to build time and restores29 native graphics entries. Paired controls at
both tested offsets have zero additional Move/cancel frames. Earlier attempted
optimizations, failed oracles and artificial capacity failures stay documented.

E02 accepts native consumers and action/effect transport. E03 accepts original
encounter-count contracts and demanding all-ten supported-size lifetimes; it
adds no arbitrary actor-count expansion. E04 accepts the union of connected
progression, current battle/territory/world/save lifetimes, actual ending/credits/
clear-save/Continue and postgame consumers. It is not a claim of one uninterrupted
full-combat campaign, every optional variation, every effect combination or
physical-GBA timing. Finite coverage is explicit, not an unfinished accepted gate.

Final visual quality remains intentionally unaccepted: generated images, repeated
poses, crops and palette compromises await the next art session. Use
ART-PLACEHOLDERS.md and notes/native-art-build-inputs.json for source/catalog/
conversion replacement; preserve native shared-palette transport in that chain.
Historical G01/G03/G04 retain their final-art review items; their engineering
requirements are covered by E01-E05. G02 native reference/import proof is complete.
The fresh private rebuild workspace remains retained for diagnosis; standalone
output, complete logs and pinned reports are also preserved outside it.
