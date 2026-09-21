# Clean art assembly and held-axe transport

September 17, 2026. Temporary built-in imagegen pixels only. No production-art
acceptance, installed game changes, player-save changes or visible launch.

## Clean assembly

`build-clean-art-chain` now passes from the authenticated fresh integration base
5065a9eaadd5de1094a38c8724d3d9d308e1194f. Source stages accept explicit parent
manifests and can suppress changes to historical component current pointers.
The existing preview is authenticated in full before replacement: module hash,
empty reservation tail, six native hooks, dispatcher and clean preimages.
Three deliberate conflicts fail before any mutation.

Runner20260917T230625.021334Z passed15 checks, reproducing the independently
repaired37afe0a7be1b80355d395d3d10685a9034b123d1 exactly. The later all17-axe
icon dispatcher intentionally changes only its module/hook. Runner
20260917T232302.365010Z passes the revised15-check clean chain and5,133 native
equipment checks, including every522 clean icon and every461 item at all
declared callers. Exact reproduction is checked for the new357-byte module.
All bytes outside its reservation/hook still equal the repaired reference.

Current six-stage manifest: `build/art/clean-chain/current.json`, hash
badd468a3a7fbcdf388ddc4f200f4e2c7b586708. The authenticated input is copied to
`build/art/clean-chain/input/5065a9eaadd5de1094a38c8724d3d9d308e1194f/`.
The original rebuild report is still required for provenance. No previous
release, component-current pointer or delivery package is overwritten.

## Held weapon implementation

`generated_weapon_transport.py` installs independent resource276 in
ROM1f84000..1f88000, using3,406 bytes. Original resource128 is byte-preserved.
The animation pointer and allocation tables extend276 to277 entries; all old
entries stay exact. Native item getter selector9 points all17 category31 axes
at276. Item stats, categories, palettes and every other selector stay unchanged.
IDs are392..399,448,453..460. The icon dispatcher covers the same17 IDs.

Weapon descriptors differ from the earlier body-only work: both primary and
secondary sequence pointers are live. All three words of all ten descriptor
slots are preserved or relocated. Four distinct sequences have42 frames.
Command-only frames contain tileFFFF/OAMFFFFFFFF and must remain exact, not
pass through an OAM parser. All visible-frame timing, commands, attachment
parameters and OAM are exact; only tile references change. Existing generated
16x16 axe pixels occupy the first four tiles, with transparent auxiliary tiles.
This proves transport; it is not a finished swing or trail animation.

Eight clean original tile/layout references are privately exported under
`build/art/generated-weapon/original-reference/`. Built-in imagegen source and
prompt hashes are inherited from the authenticated equipment stage.

## Actual acceptance and retained failures

- Runner20260917T231358.898929Z fails on the original secondary weapon palette.
  This was a bad test assumption: native98976 assigns trail palette bank6,
  whereas the blade uses the item palette. The corrected check requires bank6
  and exact paired original colors; it does not weaken the blade check.
- Runner20260917T231532.366579Z completes its baseline, then fails generated
  attack48 because item392 still uses resource128. This is a real importer
  coverage omission: only453..460 had been changed. The fixture is not changed
  to hide it; the implementation now covers all17 axes.
- Runner20260917T232127.189680Z passes5,176 native and8,334 combined retained/new
  battle checks on140fa5297f32eb1384a975cb39f7ae9ae2ca11b0. The completed old
  baseline is authenticated and reused; partial generated failures are excluded.
- Runner20260917T232447.092244Z passes5,176 native held-resource checks,26 actual
  Inventory/Buy/Sell icon checks, and8,325 fresh paired battle checks after the
  corrected icon module is assembled. Both battle outcomes are14 damage,
  47HP,14MP. Source seed and owned gameplay state are preserved. Actual hardware
  OAM, palette and tile uploads are checked for both attachment-owned channels,
  alongside body frame/allocation checks and following-turn return.

Latest weapon candidate **be82fceecd0f05d9935091f3f2400c6ebacfa2c3** resolves
through `build/art/generated-weapon/current.json`. Native report:
`build/art/generated-weapon/native-tests/20260917T232447.604692Z/report.json`.
Equipment UI report:
`build/art/generated-equipment/tests/20260917T232450.692185Z/report.json`.
Fresh battle report and captures:
`build/art/generated-actions/battle/20260917T232507.501276Z/report.json`.
The actual captures were visually inspected as temporary transport evidence.

## Remaining scope

All G gates remain open. No new package is installed. Existing native colors,
repeated temporary action poses and transparent trail padding remain explicit
limitations. Other weapon families, actual projectile/effect playback, custom
actor palettes and remaining action consumers need separate acceptance. The
earlier repaired native data still needs remaining consumer classification and
native map playback before assembled delivery acceptance. Final sprite design
and aesthetic acceptance remain deferred by the user.

Next continue those native consumers, then assemble the separately playable
technical package with authenticated reused evidence and targeted acceptance.
Do not redo the completed class implementation or the clean gameplay rebuild
merely because the held-weapon stage changes the final hash.
