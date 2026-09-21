# Enchanted Fight and native laws

Accepted bounded checkpoint, September 16, 2026. Candidate SHA1:
`f224e4f93dfd1bd293b6767ae32609f38122a4ea`, independently rehashed.
This closes elemental prediction and committed elemental/status law transport
within I01, not all effect simulation or campaign Judge acceptance.

## Event ownership

Native Fight deliberately skips action-descriptor element and status laws.
The new selector at `08134410` retains the original actor, KO and movement
gates. Other actions/law kinds continue through the original selector.
Elemental prediction reads the owned enchantment. Committed decisions instead
use actual native result rows, because reactions can consume the enchantment
before the Judge evaluates the action.

A 32-byte receipt at battle-pool offset `2620` binds the native result
container, actor, wrapper and enchanted primary component. Native result
execution records that identity; status success is never fabricated or copied
into a persistent status. The native recipient mask and wrapper must still
belong to the recorded container. Successful primary rows supply element or
actual Poison, Sleep, Silence or Slow application evidence. Stronger offhand
ordering and identical weapons retain equipment-primary identity.

The next executing primary action clears the receipt. Pure queries cannot
create it. The manager owns its lifetime; the pool grows to `2640` bytes.
Fresh and reused pools are zeroed, and retirement rejects the old owner.
No unit or save schema changes. Source: `src/engine/mystic-knight-laws.c`
and `.s`, with result recording in `mystic-knight-fight.c`.

## Focused verification

Use `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only <ID>`.
Normal IDs include declared build/native prerequisites; cached IDs require
strict source, image and capture verification. Raw logs, ROMs and fixtures
remain ignored under the candidate directory and `build/expansion/test-runs`.

- `test-mystic-knight-fight-laws`: 31,597 assertions across 264 real native
  executions. All eleven enchantments, three weapon pairs, eight fixed RNG
  seeds, both stack alignments, element prediction, actual status masks,
  misses, retired/copy masks, movement gates and query purity.
- `test-mystic-knight-fight-law-playback`: 367 assertions in 32 fixed player
  flows. Actual Fight inputs execute under declared elemental, specific-status
  and harmful-status laws. Twenty-four reach the real late Judge query;
  eight misses complete without a Judge query. Every supported element/status
  has a positive actual law decision, alongside unrelated-law controls.
- `test-battle-workspace-cached`: the allocation and retirement matrix includes
  both the Fight receipt and Doublecast slots. Actual native allocator reuse,
  malformed ownership, scene clears and reclamation are covered.
- Startup reaches native name entry and Snowball (13 checks). Existing native
  comparison/build prerequisites passed. No broad integration rerun.

Evidence: initial `20260916T102301.956990Z` passed 11/12; corrected test enum
constants for Ice/Thunder/Holy passed in `20260916T102420.409057Z`. Native
element IDs are Fire 1, Ice 5, Thunder 6 and Holy 7. Playback first exposed a
test observation error: miss results retire before the final snapshot. Capturing
the actual transaction before rendering corrected that test without game
changes; `20260916T102711.417181Z` passed 2/2. Final workspace-only follow-up
`20260916T103127.816897Z` passed 2/2 on the same candidate.

## Remaining scope

Status-law prediction now has bounded acceptance in
`notes/mystic-knight-fight-prediction.md`. I01 stays open for AI effect scoring,
recovery prediction and applicable healing/MP laws.
Playback stops immediately after the actual native Judge query; card animation
and persistent penalty behavior remain campaign/release verification. These
checks do not establish full Mystic AI turns or all custom-status law coverage.
