# FFTA Advanced v0.7.0

The first public release of FFTA Advanced: eight new jobs across ten race/job
options, 129 added abilities, 85 teaching weapons, new spritework and
quality-of-life improvements for Final Fantasy Tactics Advance (USA).

Download **FFTA-Advanced-v0.7.0.zip**. It contains the BPS patch, installation and
gameplay guide, release notes, and checksum manifest. Apply the patch to your own
clean USA ROM using [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/)
or another BPS-compatible patcher. No ROM or emulator is included.

- Clean ROM SHA-1: `4ac05441f4de70a4ec3dd932116346c61b8783d9`
- Patched ROM SHA-1: `267fd273bffe2c26a7ed3507d236af80a29b74a8`

This release includes the job-wheel discovery fix and the new AI-generated
spritework. Artist contributions to improve or replace the artwork are welcome.
Game bytes match the locally accepted `0.7-art1-job-visibility` build.

Existing saves from the preceding expansion build remain compatible. Back up
your save and use an in-game save followed by a cold Continue after updating;
do not carry emulator save states across versions.

Tested with mGBA. A full campaign playthrough and physical GBA testing remain
outstanding. Geomancer field outlines can temporarily disappear during
memory-heavy animations while their effects remain active.

GitHub Actions verifies the accepted patch and builds this ZIP. It does not
compile the game or receive a ROM; gameplay acceptance was performed locally.
