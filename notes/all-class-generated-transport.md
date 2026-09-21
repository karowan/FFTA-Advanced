# Ten-class generated transport checkpoint

September17,2026. Latest steering: built-in imagegen only; technical integration
first, artwork refinement later. All images here are existing temporary drafts.
No G gate or production artwork is accepted by this checkpoint.

## Candidates

- All-class ownership and menu width base:
  `5d8fcf3a36d128c646c2628c41b4bcfe83924e42`, resolved through
  build/art/class-resources/current.json.
- Generated ten-class candidate:
  `595782ba32f4a20ff2053218f8722ab5e491112d`, resolved through
  build/art/generated-classes/current.json. Not packaged or installed.
- The earlier separate packaged preview0edf9489 remains unchanged, as do
  vanilla, the release/showcase, all player saves and the running session.

## Real widget defect fixed

The initial dispatch test reached the actual embedded sprite widget and found
that animation changes at08029cd8 still read the legacy byte. Its full field
already contained258, but the actor was recreated as2 in mode24. The additional
read atROM29cf8 and literal29d1c now use the owned halfword. This completes the
identified fifth common-widget read; earlier helper tests covered only create
and full update, and therefore did not catch animation-only replacement.

Declared run20260917T205906.062111Z passes:

- test-native-menu-width:512 checks, adding modes24/0 after updates. The prior
  racial-header capture is reused only after exact ROM comparison limits the
  difference to29cf8..29cfa and29d1c..29d20. No arbitrary hash compatibility.
- test-native-widget-ui:197 checks. Real dispatch selector, generic Human117,
  idle frames, changing members, cancellation and reopening twice. Full frames,
  VRAM/OAM/palettes/owned-state match the original; no fee or dispatch occurs.
  The existing early-town seed and paid-recovery preparation are declared inputs.

Retained failures205617.260526Z (reentry sent during pub exit transition) and
205715.460993Z (real mode-change ID truncation) remain. The latter supersedes
any implication that35a80141 fully supported common-widget lifetime changes.

## Connected temporary assets

scripts/generated_class_transport.py authenticates every catalog source PNG,
conversion manifest and indexed frame, then composes all ten jobs on5d8fcf3a.
It adds73,868 bytes, for356,660 bytes used in the existing actor reservation.

- Each land resource receives generated idle descriptors0/1, preserving the
  original four-frame timing, commands and metadata. All other descriptors and
  every water resource stay unchanged and explicitly unfinished.
- Eight-cell sources use existing phases0/4 and2/6. Four-cell sources repeat
  their existing facing0 and2; no motion is invented or claimed as complete.
- Each class aligns to its own native opaque foot baseline and keeps its native
  palette route and16-tile sprite allocation. Palette mapping is provisional.
- The separate menu container retains all54 originals and appends ten images
  at54..63. Only private land-resource mappings change.
- The accepted equipment-preview implementation and ten generated head crops
  are composed unchanged. Its code/icons and all hooks match0edf9489 exactly,
  so its applicable runtime evidence is reused rather than repeated.

## Evidence

20260917T210432.238170Z, test-generated-classes-native, passes463 checks:
actual native actor/palette queries, original non-idle descriptors and water
pointers, all idle frame metadata/references, ten native miniature decodes and
canaries,54 originals, preview-byte equality and exact source-stage rebuild.

20260917T210701.742206Z, test-generated-classes-ui, captured all ten generic
classes on both base and generated ROMs. Every generated header and selected
miniature passed actual native sequence/upload/OAM/palette checks. The final
comparison **failed** at116-cancelled because its screen-label heuristic omitted
the header that remains visibly alive after cancellation. Preserve that failure
and the complete captures at build/art/generated-classes/ui/20260917T210702.246719Z.

The corrected scripts/generated_class_ui_evidence.py reads actual actor records
in every snapshot, including cancellation. It authenticates capture hashes,
checks class/descriptor/frame ownership, preserves allocation boundaries and
allows only exact identified miniature replacements plus native actor ranges.
No broad pixel tolerance is used. Declared test-generated-classes-retained
passes1,123 additional checks in20260917T211029.025187Z against those retained
captures, preserving560 previously passed checks/input records. No emulator
replay was necessary. Final run211610.800703Z passes1,127 checks, adding ROM/seed
authentication and a background corruption control whose updated supplied
checksum still cannot bypass allocation boundaries. The regression is pinned
to the immutable595782ba manifest. The corrected verifier is also wired into future UI runs.

All-class UI profiles set the displayed job on an existing same-race member
before menu entry; Montblanc is made generic for the two Moogle cases. This is
presentation coverage, not acquisition or story-character behavior acceptance.

## Visual review and next path

Native captures for Samurai, Nu Mou Chemist and Moogle Bard visibly show the
new temporary idle bodies and separate wheel figures. Detail/color quality is
not accepted. The large portraits still show original donor artwork, including
the Ninja face next to Samurai. This is an explicit remaining consumer.

Static tracing identifies that portrait path for the next implementation:

- Generic job selector9 / record byte13 chooses portrait ID;103 original IDs.
- Native080cb868(dest,unit) resolves the portrait through080071a8 and decodes
  via0800543c. Index form080cb8b4 uses the same data. Size helpers080cb808 and
  080cb84c call0800588c. Data archive atROM3e105c;32-bit relative offsets are
  relative toarchive+4. Decoded sizes vary (Samurai donor4 is3,200 bytes).
- OAM archive atROM417f88 uses16-bit relative offsets, also relative tobase+4;
  helpers080cb928/080cb968. Layout records are count plus six-byte objects.
  Attribute0 has the8bpp flag: the existing4bpp actor renderer must not be used.
- Portrait palettes use separate A7 containers3d5a1c/3d965c/3dd360 for color
  modes. Each has165 entries of96 bytes (48 colors). Native080cb8d4 selects
  by mode; job selectors10/11 supply the two palette IDs. Exact OBJ destination
  indices and full native decode/roundtrip/runtime proof still need tracing.
- Archive pointers appear atcb828/cb864/cb88c/cb8d0; layout pointers atcb948/
  cb97c; palette literals atcb924/cb910/cb900. Audit all references before edits.

Next complete this distinct portrait import, then full action/water/palette,
weapon/equipment/effect/status paths and assembled delivery. Original native
sprites remain style/format references. No external generation, council,
publication, game launch or player-save change occurred. The incident note is
unread and untouched.
