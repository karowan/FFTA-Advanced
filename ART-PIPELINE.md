# Art pipeline preview

Scope correction: the user requires a full engineering implementation with only
artwork placeholders. This document describes the existing historical preview
package and its evidence, not completion of that requirement. In particular,
the4–5-frame cancel cost below describes the historical installed package. It is
resolved on engineering candidatea28b624b; that candidate also has accepted E02
consumer integration. E03-E05 remain open. The prior preview acceptance does not
waive them. See IMPLEMENTATION-CHECKLIST.md for current gates.
The immutable packaged copy of this guide remains preserved with that package.

This is a separately playable **technical preview with temporary imagegen
artwork**. Final sprite design and animation refinement are deferred. It is
not a completed-art release or completion of G01–G04. Built-in imagegen is the
artwork provider; Gemini/fal drafts are not part of this package.

Candidate `7507ca5cb03c1db7a717fd6d21d97a9f5a4ae08b` fixes the reproduced
area-target highlight and damage-flash failures in the older4a7d55ce preview.
Its final consumer checks and byte-exact source rebuild pass. The delivery
manifest identifies the installed package and its19 required evidence reports.
See `notes/native-art-target-and-damage.md` and
`notes/native-art-capacity-delivery.md`.

## Play and save isolation

Run `Play Art Pipeline Preview.cmd` as a normal Windows desktop application.
Packaging and validation do not launch the game. The launcher verifies the ROM
and keeps saves, states and screenshots in `saves/art-pipeline/<candidate SHA-1>/`.
It does not import a player save. A new save starts at the ordinary opening.

Vanilla, the existing v0.7 installation, older preview packages and any running
game remain separate. Do not replace or close an existing game to inspect this
build. The delivery manifest records the exact ROM, BPS patch, coverage and
acceptance reports. Failed enclosing runs remain visible in reused evidence.

## What is connected

- All ten new classes appear on a second L/R equipment-eligibility page in
  Item List, Buy and Sell, with readable labels and temporary portrait crops.
- All ten classes have independent battle resources, job-wheel figures and
  large portraits. Land and water action slots preserve native animation
  commands and timing while displaying temporary generated poses.
- All ten class body palettes are enabled together. Portraits have independent
  palettes; the wheel miniatures remain converted to their native menu palettes.
- All 17 axes use the generated inventory icon and an independent held-weapon
  resource. Tomahawk has a generated projectile and separate three-frame impact.
  Exposed and Centered have generated status icons.
- Fixed story appearances, including Marche and Montblanc, remain independent
  of their jobs. Generic recruits show the new class bodies.
- Battle Status and its help panels use repaired memory ownership. The new-game
  name keyboard retains both original US tabs while allocating their actual size.

The repeated poses are **not finished action animations**. Water figures are
technical crops. Some conversions lose face and costume detail; these are not
accepted final designs. Other weapon and effect families retain their existing
presentation. Replacing these drafts is the next artwork phase, using imagegen
and the proven import paths rather than manually drawn replacement pixels.

## Verified scope and limits

The connected package requires19 exact-candidate reports, including all ten large
portraits, fixed-character isolation, equipment pages, axe inventory screens,
status glyphs, a mixed-class held-axe action, Tomahawk projectile/impact and
battle Status/help/return. Native area-target highlighting, colors1..15 damage/restore
operations, actual Thundaga cast/hit/next-turn return and the declared larger
encounter also pass. The full art-stage rebuild must reproduce the tested
ROM. Patching must be deterministic, apply byte-exactly to the clean USA ROM and
reject a different source. Launcher validation checks all three independent
storage paths and rejects a changed ROM without launching.

The mixed Move/cancel scene adds four to five frames to cancel response (about
67–84 ms at 60 Hz). Direct observations confirm original native background
rotation phases, unchanged native palette shadows and completion within VBlank.
This bounded cost is accepted for the technical Windows preview. It is not a
promise of equal timing in every scene.

A private test fixture using an intact original mixed formation reaches13 actors,
including two new-class party members. Status opens and returns safely; minimum
sampled free heap is20,888 bytes. This establishes that declared larger scene,
not maximum capacity or the original mission's campaign eligibility.

Earlier all-ten natural-water checks are retained for their unchanged assets
and original inputs; they were not all repeated on this final ROM. Maximum
encounter/effect capacity, every natural caster/weapon/effect family and a full
campaign replay on this art build remain unverified. The Status component also
passes an extra 8 KiB allocation case, which does not establish maximum encounter
capacity. These limits prevent a blanket finished-expansion claim.

The corrected gameplay source preserves the 139 native data words repaired
before this art chain. Its prior gameplay/source-build evidence remains within
its documented scope; a successful graphics check is not a campaign completion.

## Reproduce

Keep the clean USA ROM, compiler and generated images private as described in
`REPRODUCIBLE-BUILD.md`. Builds use exact image bytes authenticated by the
catalogs in `src/art/imagegen/`; image generation itself is not deterministic.

1. Run `test-connected-art-rebuild` through `Test Expansion.ps1` with
   `scripts/native-art-test-plan.json`. It authenticates the retained corrected
   eight-stage gameplay rebuild, rebuilds the class resources, generated class
   and menu figures, portraits, action transport, current palette/menu hooks,
   status glyphs, equipment, held weapon and impact. It requires byte equality
   with the tested connected ROM and refreshes only its final provenance.
2. Reuse applicable passing evidence. If implementation or inputs change, run
   affected declared consumer checks and review failures. The connected
   packaging step names its exact required reports; historical and current
   reports must not be silently interchanged.
3. Wait for the rebuild runner to finish, then run `package-connected-art` and
   `test-art-pipeline-launcher` in a separate runner invocation. Packaging
   intentionally refuses evidence from a still-running enclosing test run. The private
   output is `build/art/pipeline/delivery/<candidate SHA-1>/bundle-<revision>/`, with the ROM,
   BPS patch, manifest, candidate description and this guide. Launcher testing
   uses validation mode and does not launch or create a player save.

The source gameplay rebuild, private input hashes, runtime inputs and evidence
limits are in the associated manifests and checkpoint notes. Never commit ROMs,
images, patches, saves, local tools or raw generated evidence. Older package
folders remain available. Guide/evidence revisions get distinct immutable bundle
folders even when ROM bytes are unchanged; save paths remain ROM-specific. Only the preview launcher's current delivery index is
advanced after packaging succeeds.
