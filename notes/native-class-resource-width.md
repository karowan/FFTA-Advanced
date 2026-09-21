# Animated menu width fix and remaining coverage

September17,2026. Technical integration remains first; built-in imagegen only.
Candidate `35a801411311db14d38b0895bb2c043bbe90698b` resolves through
`build/art/class-resources/current.json`. It is not packaged or installed.
The previous connected preview and player games/saves are unchanged.

## Two distinct consumers

The earlier common-widget trace identified a real narrowing path, but the
racial job-wheel header uses a separate component. Treating its actor pointer
as a common-widget pointer caused baseline harness failure203459.794289Z.

The header task pointer is at IWRAM03002818. Fields434/435 are resource byte
and palette;440 is collection,444 manager,448 actor. Do not widen434 in place.
The header-specific allocator copies the native021b1c manager construction,
using20 bytes instead of16. Its new halfword at manager+16 is exclusively owned;
all existing16 bytes and native list registration remain intact. The native
size-aware free path still owns cleanup; direct teardown execution is pending.
Initial allocation mirrors the legacy byte. Unit update0717cc stores the full
resource and its legacy low byte; its immediate creation and the state0/state2/
state3 paths at088984/0889de/088ae8 read the manager halfword. This does not claim
a new resource survives collection destruction without its normal unit update.

The common widget is different: its private buffer spans object+84..1084.
Its native allocator extent is reduced from4096 to4080 bytes, reserving the
final16 bytes. The full resource lives at1080; legacy byte1085 remains mirrored.
Constructor and update hooks preserve the independent mode/palette/control
fields. Seven narrowing pairs, four resource literals, and four read sites are
patched with source-byte assertions. The three header state reads and direct
update are separately patched. Source is scripts/native_menu_actor_width.py.

## Accepted evidence and limits

- test-native-class-menus,20260917T204258.603573Z:425 checks. Four generic land
  figures plus Montblanc across five racial wheels match original full frames,
  VRAM, OAM, palettes and owned data. Actual native actor IDs and neighboring
  header fields are checked at the wheel and three idle captures. It does not
  display all20 resources or a generic Moogle. The original report's phrase
  "with all20 private resource IDs" describes the candidate, not its coverage;
  the source report wording is corrected accordingly.
- test-native-menu-width,20260917T204827.216767Z:464 checks. Native direct
  replacement and state2/state3 recreation across ten generic classes, with ABI
  checks on complete calls. Native generic constructor, post-readiness lifecycle
  allocation and update cover IDs4,256,274,275 and repeated transitions. All
  neighboring fields match the native constructor, and allocator size1018 words
  excludes the owned tail. The widget owner is an isolated test buffer outside
  game memory: this does not prove menu capacity, rendering, transition timing,
  shadow drawing or teardown. Partial state branches stop after actor creation;
  they are not claimed as complete native function or display runs.
- Reproducible capture discovery/source hashing rerun205144.141973Z also passes464 checks.
- Earlier276-check header-only pass204540.821608Z remains valid within its scope.
- Exact rebuild produced the same35a80141 hash. All bytes in the previous
  resource reservation and all resource metadata match8c28684b exactly, so its
 28,037 native resource-preservation checks remain applicable without rerun.

The fixed candidate uses282,792 bytes of the existing ROM reservation, including
208 bytes of menu hooks. No new artwork is introduced by this width fix.

## Retained failures

The prior consumer failure202449.474367Z remains evidence of258 truncating to2.
The traversal failure202356.352917Z and baseline owner-assumption failure
203459.794289Z also remain. Helper run204653.745953Z failed because the test
allocated an embedded widget from the header's small heap. Run204746.729508Z
passed storage/allocation/actor update but failed a mislabeled neighboring-field
assertion; it now compares exact constructor fields. Neither failure was hidden
by changing game pixels or tolerating unexpected differences.

Next prove the common widget in its actual owning menu and through teardown,
then compose all-class generated transport and the remaining native consumers.
All G gates remain open. No game launch, player save changes or publication.

---

## Historical discovery checkpoint (superseded where corrected above)

# All-class graphics ownership and remaining menu width defect

September17,2026. Latest user direction remains technical integration before
sprite refinement, built-in imagegen only. No external calls or generation.

`scripts/native_class_resources.py` creates20 independent complete resources:
jobs116..125 own land256+2n and water257+2n. All original248 animation table
entries, sizes and256 miniature mappings are preserved. The same private
ROM0x1d10000..0x1d80000 reservation fits282,584 bytes, including complete
sequences, metadata, tiles and OAM. No original character artwork is modified.
These are temporary unchanged donors, not new artwork or completed animation.

Candidate `8c28684b4828fb324fe772689711cc3a34cb44b9` resolves through
`build/art/class-resources/current.json`. It is **not packaged or installed**.
The previous connected preview remains separate.

## Evidence

`test-native-class-resources` passes28,037 checks in
`20260917T202117.992057Z`: native job/graphics lookups for all jobs,20 full
resource/mapping/allocation queries, all descriptor/frame metadata, visible and
hidden tile bytes, native OAM and ownership. This verifies resource transport;
it does not establish every consumer's ability to retain16-bit IDs.

`test-native-class-menus` uses the existing authenticated showcase seed with
five real racial members (slots2/3/4/1/5), identical baseline/candidate input,
whole framebuffer, OAM, palette, VRAM and owned-state comparisons.

- `20260917T202356.352917Z` **failed** because its initial roster traversal used
  rows instead of the established four-column layout; it stayed on Marche.
- The test now reuses the established Down-if-slot>=4, Right-slot%4 traversal
  and verifies the actual selected roster pointer before opening the wheel.
- `20260917T202449.474367Z` **failed** on actual original/private framebuffer
  inequality. All five cases ran and their captures remain in
  `build/art/class-resources/menus/20260917T202449.988834Z/`.

Every initial roster capture matches. Generic Human, Bangaa, Nu Mou and Viera
wheel/header displays differ, while their OAM, palettes and owned data remain
exact. Montblanc's fixed-character path matches. Human differences occupy
VRAM0x13e80..0x13fbd in the animated upper figure, not the separate static wheel
miniature. This is a real consumer defect, not animation phase or test noise.

## Confirmed narrowing chain

Retained slot2 wheel RAM shows native actor record0x020168c8:

- Original resource1, mode0, sequence142957632, displayed native frame1.
- Private candidate resource2, mode0, sequence142964608, displayed frame1.
- Correct private resource is258. Thus258 was truncated to2 before creation.
  Both actors independently match their selected native sequence and upload;
  allocation and rendering are working on the wrong resource.

The unit graphics helper0x08022238 returns16 bits, forwarding0x080cb714.
Static disassembly identifies six immediate8-bit narrowing pairs after calls:
ROM0x57496,0x5752e,0x60ecc,0x60fc6,0x65d94,0x65e96. These feed generic menu
figure creation0x08029864 and update0x08029c34. Merely widening those six pairs
is insufficient:

- Creation0x08029864 also narrows its resource argument in R8 at0x2989c/0x2989e.
- It stores the resource as a byte at object+0x1085 via0x29904.
- Update0x08029c34 stores R2 as a byte at the same field via0x29c58.
- Update reads that byte at0x29c9e before native actor creation0x08021618.
- Adjacent fields0x1086..0x108c contain independent mode/palette/control state;
  do not widen the existing byte store in place and overwrite them.
- Another helper caller0x71800 stores the result with STRB at0x7180a. Its
  consumer/lifetime still needs classification before declaring full width support.

Next: trace the generic menu figure's complete storage lifetime and establish
owned space or an explicit compatible extension for16-bit IDs. Audit all reads,
creation, update and teardown; preserve adjacent native fields and ABI. Then
rerun the affected racial menu test and add direct bounded lifetime/width tests
for the changed paths. Do not hide this by remapping new jobs back to donors or
using broad image-difference tolerances. Do not ship this candidate yet.

The earlier Samurai miniature proof used Marche, whose fixed upper figure
bypasses the generic path. It remains valid for its narrow static wheel consumer
but does not cover generic animated headers. This new evidence adds that gate;
all G gates remain open. Player games/saves and the unrelated incident note were
untouched. No broad gameplay suite or game launch occurred.
