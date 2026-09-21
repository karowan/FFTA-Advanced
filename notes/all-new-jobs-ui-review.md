# All new jobs: native party UI review

The repeatable test is `scripts/test-all-new-jobs-in-game.py`. Its default input is the verified `command-label.gba/json` stage; `--frozen` reruns the retained snapshot and `--job N` isolates a case. It uses the bundled Python/mGBA runtime, freezes ROM/engine/symbols/manifest under `build/expansion/probes/all-new-jobs-in-game/<ROM SHA1>/`, and writes its report, disposable saves and screenshots there. Per-hash input/state paths prevent another build/test from replacing a running emulator's fixture. A latest-report copy remains in the parent output directory. Original `build/test-lab/early-town.sav` remains byte-identical.

Final test snapshot: command-label ROM `98c0a4fa82cf0c6cc7ed06d963348111ee5401f9`, engine `fca13898693a59f8f7322ab138a5520093c51713`. Earlier status updates named52ed93af, but a subsequent default test invocation correctly froze the parent's newer98c0a4fa stage. The source stage was verified against its live manifest/embedded engine; the retained manifest was reconstructed from the completed verified report and frozen bytes when the parent rebuilt subsequent stages during review. Future runs save that manifest automatically at freeze time. The final rerun uses `--frozen` and the per-hash paths.

## Native lifecycle coverage

All ten job IDs116..125 are exercised independently from a fresh cold-loaded copy of the original seed. The existing seed already has all five races: Marche/Human (canonical slot0), Montblanc/Moogle (1), Ford/Human (2), Jona/Bangaa (3), Leonard/Nu Mou (4), Colette/Viera (5). The visible No1..No6 ordering is the same canonical order; the script verifies the actual native selected pointer at menu `+1D0C` before opening the job wheel.

The fixture changes only AP to100 in every racial lesson byte, including all34 Human extension bytes. It preserves initial jobs, characters, gear, inventory and clan flags. This intentionally satisfies prerequisites for UI testing; it is not a natural AP progression test.

For every job the test:

1. Opens the native wheel, pages and rotates with normal controller input, and verifies the chosen record's real job ID.
2. Cancels from the wheel and verifies the complete source unit is unchanged, then replays the selected state and confirms through the native flow. Marche opens a confirmation dialog, whose cancel path is separately verified. The generic units and Montblanc commit through the immediate native selection path.
3. Checks the published current job, command byte116..125, racial AP count, character identity, race and named aliases. Marche retains alias50 and Montblanc alias52; generic records become the selected job.
4. Checks equipment cleanup and owned inventory. In this seed, the native job-change path clears all five equipment slots for all ten jobs. Owned quantities remain unchanged. Native CABA8 and CB48C validate the resulting layout; this does not claim that a legal item is retained automatically or that an empty layout exercises every equipment permission combination.
5. Reopens the wheel and verifies the current job is selected on its proper page.
6. Uses native save and a fresh emulator cold load, comparing the complete264-byte source unit, owned inventory and all AP low-seven-bit progress values.
7. Opens Pick Abilities after cold load, then selects the other new job of the same race as its secondary command. Each of the ten command IDs is therefore rendered once as primary and once as secondary. Selecting the identical primary command as secondary is rejected by native UI; the paired-job fixture respects that rule.

All stages check guard `0203FF44..0203FFFF`. Native progress bytes may acquire their normal availability high bit; AP low-seven-bit values remain100. No battle effect, reaction, gameplay AP earning or combat animation is claimed by this test.

## Visual results

The selected-wheel, changed-job, reopened-wheel, cold-load, primary-command and paired-command screenshots cover every job. All ten approved command labels fit their native rows and display the expected text:

| Job | Command | Donor job |
| --- | --- | --- |
|116 Human Samurai|Iaido|6 Ninja|
|117 Human Dark Knight|Dark Arts|3 Paladin|
|118 Bangaa Viking|Reaving|13 Warrior|
|119 Bangaa Dark Knight|Dark Arts|15 Defender|
|120 Nu Mou Chemist|Items|25 Beastmaster|
|121 Nu Mou Geomancer|Geomancy|27 Sage|
|122 Moogle Chemist|Items|41 Gadgeteer|
|123 Moogle Bard|Song|36 Animist|
|124 Viera Dancer|Dance|29 Elementalist|
|125 Viera Mystic Knight|Spellblade|30 Red Mage|

Seventy native C8570 getter comparisons establish equality with donor animation/palette selectors4/5/6/7 and portrait selectors9/A/B. The generic Bangaa, Nu Mou and Viera screens show the corresponding donor portraits and sprites. Marche and Montblanc correctly retain their dedicated named-character presentation while the job wheel uses donor animated miniatures. These were reused visuals in the original acceptance, not newly drawn job artwork.

September 17 art-investigation correction: the wheel uses animated miniatures,
not the 32x16 face/abbreviation icons decoded by CB9E0. Those icons are consumed
by the equipment teaching panel and other menus. The newly requested original
artwork and missing equipment eligibility grid have separate open gates G01-G04.

## Found and fixed: primary and secondary command label truncation

The original `3afc19bd...` job-ui stage stored correct command IDs116..125 and loaded the approved command descriptors, yet actual Pick Abilities screenshots displayed unrelated old names: Human Dark Knight showed Debilitate, Viking showed Spirit Magic, Bangaa Dark Knight showed Battle Tech, and Nu Mou Chemist showed Work Tech.

The cause was **text-ID byte truncation**, not a six-bit command mask:

- `74AE0..74AE4` gets the unit's ability data through C7EA4 selector22.
- Primary `74AEC..74AF6` indexes the command descriptor with the complete command byte but reads only its first name-ID byte and stores it at stack `+C`.
- Secondary `74B2C..74B38` reconstructs the complete halfword name ID, then `74B3A` stores only its low byte at stack `+D`.
- `74BF0..74BF4` and `74C30..74C32` reload those byte-sized names. New names896..905 consequently wrap to128..137 before the other-text lookup.

The bounded fix is `src/engine/command-label-hooks.s`, installed by `scripts/build-command-label-probe.mjs` on top of axe-visual. It replaces only aligned `74C34..74C3C`, guarded against original bytes `8000401902683fe0` (`lsls r0,#2; adds r0,r0,r5; ldr r2,[r0]; b74CBC`).

Entry contract: r0 contains the native truncated name byte, r4 is primary/secondary row0/1, r5 is the other-text pointer bank, and r7 is the source unit. For command byte116..125 at `unit+35+r4`, the hook rereads the complete descriptor name halfword through the already relocated command-table pointer at literal `74C0C`. Every other command retains the original byte lookup exactly. The hook returns to `74CBC` with native r0 pointer-slot and r2 text-pointer semantics; r1, r4-r11 and SP are preserved. r3 is dead at this boundary and is explicitly set to0 at `74CC2` before89AAC. There is no C call, persistent scratch allocation, widened stack layout, or reinterpretation of slot/ability flags.

The test executes **1,024 native boundary comparisons**: all256 possible command bytes, both label positions, and both four/eight-byte entry-stack alignment cases. Nonnew commands preserve their native text pointer and live registers. All ten new commands resolve the full approved text pointer in both slots. EWRAM and source units remain unchanged. The emulator instruction cache is invalidated when switching the eight-byte native/patched fragment, so the differential does not accidentally execute a previously cached version.
