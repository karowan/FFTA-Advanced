> Historical record, archived September 21, 2026. For current guidance, see [the repository overview](../../README.md). Paths in code examples are relative to the repository root.

# Playing FFTA

The emulator and ROM patcher are installed locally in this project. Your supplied game has been copied here and its SHA-1 matches the required clean US version.

1. Double-click **Play FFTA.cmd** to launch the original game.
2. The untouched backup is `roms/clean/FFTA_US_clean.gba`. The playing copy is `roms/play/vanilla/FFTA_US_vanilla.gba`. Your temporary source file was left unchanged.
3. To use a mod later, open **Open ROM Patcher.cmd**, choose the original game and the selected patch, and save the patched output in its own folder under `roms/play`.
4. Open the patched game in mGBA and begin a separate save unless the mod explicitly supports an existing one.

The recommended clean US version (sometimes named USA, Australia) has SHA-1 `4AC05441F4DE70A4EC3DD932116346C61B8783D9` and CRC32 `5645E56C`. A matching filename is not a substitute for checking the hash.

Default keys: X = A, Z = B, Enter = Start, Backspace = Select, A/S = L/R. Controls can be remapped in mGBA. Tab fast-forwards.

## Installed tools

- **mGBA 0.10.5**, official Windows 64-bit portable distribution. Settings remain with this portable copy. Normal saves default beside the loaded game unless you change the emulator's save directory.
- **Rom Patcher JS**, pinned revision `3183884086825c3a57c72026234debcef1e2240c`. The launcher serves only the tool's files at `http://127.0.0.1:18764`; game and patch file selections are handled in your browser. No website hosting account is needed. The local helper remains running until Windows restarts or its Node process is closed; it has no startup entry.

The project includes original tool download archives under `downloads` and your supplied FFTA ROM in the locations above. A separate experimental foundation ROM and BPS patch have now been built. See [implementation status](../../IMPLEMENTATION-STATUS.md) for exactly what is installed and what remains unfinished. **Play Development Build.cmd** opens that test build; the original launcher still opens vanilla. Our custom jobs and weapons remain design-only.

For testing without replaying the opening, use **Play Test Lab.cmd**, then **Continue → Load → File No. 1**. The [test lab guide](../../TESTING.md) explains the prepared save and automated menu/save checks. **Build Test Lab.ps1** regenerates that disposable lab in seconds. The lab has its own save, separate from vanilla and ordinary development play.

See [the research guide](../../FFTA-MODDING-GUIDE.md) for mod comparisons and creation tools.

## Our expansion design

Start with [the design principles](../../JOB-DESIGN-PRINCIPLES.md): preserve each job's spirit and design its mechanics for FFTA. [The full class specification](../../JOB-CLASS-SPECIFICATION.md) is version 0.7 and covers jobs, prerequisites, abilities, growths, and equipment. [The axe addendum](../../AXE-SKILL-EXPANSION.md) retains the adopted version 0.5 rules; [the support sheet](../../SUPPORT-SKILL-DESIGN.md) includes the expanded Spellweave categories.

The [original council balance pass](../../BALANCE-COUNCIL.md) explains the 116-entry foundation. The [approved Spellblade expansion](../../SPELLBLADE-EXPANSION.md) adds six actions, bringing version 0.6 to 122 abilities and 78 teaching items before the additions below. New numerical and teaching targets are provisional. These are design documents, not an installed patch.

All seven [additional council abilities](../../ABILITY-EXPANSION-COUNCIL.md) are adopted in version 0.7: Higanbana, The Blackest Night, Provoke, Nature's Refuge, Inoculation, Guarding Draught, and Passing Step. Current totals are 129 abilities and 85 teaching items. Numerical/teaching targets remain provisional; these new lessons are not yet installed in the development ROM.

The [weapon acquisition guide](../../WEAPON-ACQUISITION.md) maps all 129 lessons to 85 weapons with base prices, permanent shop locations, and exact opening/#005/#011/#017 story gates. Those planned items are not installed in the vanilla ROM yet.

The approved [vanilla+ foundation](../../VANILLA-PLUS-PACKAGE.md) covers completion safeguards, late rare-equipment recovery, manual clan sorting, visible Morpher transformations, and small menu improvements. The experimental build includes two refunds, one recruit retry, two monster substitutions, sorting, Morpher visuals and pub reordering. Remaining recovery work and campaign testing are listed in [implementation status](../../IMPLEMENTATION-STATUS.md). The ability and weapon plans above are unchanged.
