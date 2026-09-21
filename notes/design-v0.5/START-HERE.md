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

The project includes original tool download archives under `downloads` and your supplied FFTA ROM in the locations above. No gameplay mod has been selected or applied, and no editor that would change gameplay has been installed yet.

See [the research guide](../../FFTA-MODDING-GUIDE.md) for mod comparisons and creation tools.

## Our expansion design

Start with [the design principles](JOB-DESIGN-PRINCIPLES.md): preserve each job's spirit and design its mechanics for FFTA. [The full class specification](JOB-CLASS-SPECIFICATION.md) contains jobs, prerequisites, abilities, passives, growths, and equipment; [the axe addendum](AXE-SKILL-EXPANSION.md) covers Soldier and Gladiator. The adopted class and axe specifications are version 0.5; [the support sheet](SUPPORT-SKILL-DESIGN.md) explains transferable skills and example builds. The [adopted council balance pass](BALANCE-COUNCIL.md) explains the decisions and strongest combinations. All 116 abilities and their AP/teaching details are updated. The [adopted council balance pass](BALANCE-COUNCIL.md) explains the decisions and strongest combinations. All 116 abilities and their AP/teaching details are updated. These are design documents, not an installed patch.
