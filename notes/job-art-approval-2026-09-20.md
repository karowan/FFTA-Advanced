# Complete user art approval round

The current game is technically integrated, but its artwork is not fully accepted.
The user flagged the Samurai portrait's face, an unwanted blue bandana in the
Bangaa Dark Knight portrait, and the Viera Mystic Knight portrait. All ten jobs
are now presented for explicit visual review, including equipment badges and
all animations. Existing sprite-base approvals, including the muted Samurai
scarf, remain intact; no additional approvals are inferred.

## Deliverable

`build/art/job-art-approval-2026-09-20/index.html` is one offline page. It includes:

- Ten current in-game portrait crops, original concepts, generated/extracted
  sources, native imported portraits, original-game references, exact prompts,
  and full menu/battle screenshots.
- All ten equipment badges in native eligible/ineligible colors, including
  actual runtime lettering, plus native-size views and bright/dim wheel figures.
- All 675 distinct native poses in both ally/enemy colors and all 796 populated
  land/water sequences, with 3025 ordered drawing records and 1116 control records.
- The 884 native null slots, explicitly distinguished from missing artwork.
- Pause and individual frame-step controls, mirrored views, review decisions,
  local notes and JSON note export. Each displayed image is separately annotatable
  through browser comments. No page action changes the ROM or production catalog.

Animation previews display the drawing records at their recorded durations,
assuming 60 ticks/second, and repeat for inspection. They do not interpret control
commands or simulate weapon attachments, effects, actor movement or battle events.
Controls are shown in order with their raw parameters. Unknown action names retain
sequence numbers rather than invented semantic labels. Mirroring is an inspection
view; primary front/rear sequences are exported independently.

## Portrait provenance and findings

The original generation input combined original-game portrait examples with the
class concept. The prompt requested a 64x64 portrait in a worksheet cell. The
worksheet was then reduced, background-cleared and extracted/fitted to 64x64.
Import fitted it again into a 44x54 silhouette window inside the 64x64 texture and
quantized to 47 opaque RGB555 colors in the native portrait archive format.
That repeated reduction is a plausible source of facial detail loss; it is not
proven to be the sole cause. The Bangaa Dark Knight's unwanted blue cloth already
appears in the original generated worksheet, before native conversion.

The archived review was explicitly primary-agent source review, not user approval.
Its positive conclusions missed the defects visible to the user. Keep that history
and the rejected output; do not relabel it as user-approved or silently regenerate
portraits before this review. Future revisions should be checked in the actual
portrait viewport at native size before propagation. Use imagegen for artwork
changes, with concept and original portraits attached, and keep exact generation
and conversion stages visible for approval.

## Reproduction and verification

Run [build-art-approval-page.py](../scripts/build-art-approval-page.py) with the
bundled local Python. The page template is
[art-approval-page.html.txt](../scripts/art-approval-page.html.txt). The extra
`.txt` suffix keeps the reusable source within the repository's source-only
asset allowlist; the generated deliverable is ordinary `index.html`.

Input is final-ROM SHA1 `316a40524b960c49ad7213ac4b0bea539bfa9513` and its
authenticated archived catalogs, generation plan and existing screenshots.
The exporter authenticates hashes, decodes exact ROM tiles/OAM and palettes,
checks every native sequence binding/timing/command, verifies portrait pixels
and palette, preserves the full actor footprint, and verifies live badge head
pixels against the ROM. Badge labels come from previously captured VRAM, not a
new approximation. Runtime screenshot crops use nearest-neighbor reduction from
the existing exact 3x captures; no artwork pixels are authored or repaired.

`export-proof.json` inventories all 1521 exported source/image records and hashes.
`review-data.json` contains full sequences and pose bindings. The exporter checks
all counts above. Static page-script syntax and local image links were validated.
Browser visual QA was unavailable: the browser tool explicitly blocked the local
file URL. No alternate browser, local server or other workaround was used.
The user can open the supplied local page link for annotation.

No new game runtime checks were needed: this round exports and presents existing
evidence and artwork, changing no ROM, save, launcher, gameplay or image-generation
source. The running game and historical evidence remain untouched.
