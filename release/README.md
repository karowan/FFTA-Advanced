# Public releases

The [release workflow](../.github/workflows/release.yml) builds a player ZIP from
an accepted BPS file attached to a draft GitHub release. The checksum-pinned
[input record](input.json) identifies the clean and patched game, patch and local
acceptance. No ROM, generated patch or archive is committed to Git.

GitHub Actions verifies source/privacy checks, tests the packaging code, checks
the BPS SHA-256, size, header and CRC values, renders MOD-README.md, and builds
the four-file ZIP plus SHA256SUMS.txt. It uploads the outputs and publishes the
draft only after those steps pass. Actions are pinned to commits, pull-request
CI is read-only, and only the release job receives contents:write permission.

This is release-packaging CI. It does not compile the ROM or repeat gameplay
tests. Current-art rebuilding still needs the local inputs described in
[REPRODUCIBLE-BUILD.md](../REPRODUCIBLE-BUILD.md). The first public game is exactly
the locally accepted art/job-visibility build; its public release number is 0.7.0.

## Publish another accepted version

1. Build and accept the game locally through its declared deterministic plan.
2. Update input.json with that accepted BPS and source/target identities; update
   its tag/version and NOTES.md. Keep raw local reports and ROMs outside Git.
3. Pass source and packaging CI, then create/push that exact version tag.
4. Create a **draft** release at the existing tag and attach only its accepted
   FFTA_Expansion.bps as the workflow input. Do not attach a ROM or private log.
5. Dispatch the release workflow **at the same tag**, not the main branch:

```powershell
gh workflow run release.yml --repo karowan/FFTA-Advanced --ref v0.7.0 -f tag=v0.7.0
```

That example is for the initial release. Use a new version for future game or
documentation changes. The job refuses to modify an already published release.
Failed draft runs can be retried; the patch must still match the tagged input
record. A local equivalent is:

```powershell
python scripts/ci_release.py --patch build/ci-input/FFTA_Expansion.bps --tag v0.7.0
```

The accepted patch remains a standalone release asset so the ZIP can be rebuilt
without a circular dependency on an older ZIP. Players normally need only the ZIP.
The checksums file covers both the ZIP and standalone BPS.

GitHub documentation: [workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions),
[draft releases](https://cli.github.com/manual/gh_release_create), and
[asset upload](https://cli.github.com/manual/gh_release_upload).
