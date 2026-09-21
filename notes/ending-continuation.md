# Ending continuation and postgame consumers

September 17, 2026. Accepted bounded suffix; A01/V06 remain open.

## Selection and native trace

Run `test-clear-save-continuation` with its sole prerequisite
`verify-integrated-assembly-prerequisites`. This fills the previously unobserved
suffix of the accepted clear-save checkpoint, without recreating its profile
or repeating the original save transaction. Shipping source/image are unchanged.
The consumer authenticates the retained report, emulator state, SRAM and private
instrumentation, then resumes native execution. Full final battle, credits and
natural campaign entry to the ending-save opcode remain separate obligations.

Static inspection found that native ending controller `0x0812C2B8`, state
`0x106`, counts down 60 ticks and calls `0x080231C0`. That function writes
the reset signature and loops on native frame synchronization; it does not
return. The alternate `0x107` branch writes parent byte6. Therefore the prior
synthetic-parent failure is not evidence that the real ending must return to
that parent. The required observable continuation is title then Continue.
The scene opcode handler at `0x081224B8` dispatches operand14 through
`0x0812257E` to the same original clear-save constructor `0x0812C510`.
These shipping regions are checked byte-for-byte against the clean USA ROM.

The suffix checks retained cleared flash, full24-member/AP/preference/inventory
profile, and retired battle state after same-core reset/Continue. It then runs
native mission generation and pub listing with actual loaded inputs, paired
with a negative control removing only flag54. Lucky Night202 and Left Behind378
must appear only after clear. All six rare-gear recovery services must still
reject missing original entitlements. This is native listing coverage, not
rendered postgame mission execution or natural campaign completion.

## Reproduction

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-clear-save-continuation
```

Run `20260917T093625.140550Z` stopped at the assembly verifier; no emulator ran.
Its recorded Python executable hash and runner source differ from the current
environment. The runner cleanup was explicitly requested; current Python is
3.12.14, SHA256 `766b4f956edf378917adc33c84e7d4c8b295a71e8aebcfdd2de7970f1f0ca0b6`.
Do not exempt these inputs or relabel the failed report. Rebuild only the six
assembly steps (`build-samurai-private`, `build-job-state-private`,
`build-chemist`, `build-dark-knight`, `build-viking`, `build-integrated-jobs`)
and require the same candidate hash before the targeted suffix. This is an
input-drift assembly check, not broad integration or the final clean rebuild.

## Accepted evidence

Assembly run `20260917T093710.889444Z` passed all six stages and reproduced
`1b070824a8dad4995434eee3ab40fa08187a6120`. Targeted run
`20260917T093754.785155Z` then passed both selected steps; the suffix consumer
took 3.4 seconds and passed 46 assertions. Root inspected the title and restored
world captures. No shipping code, candidate bytes or player saves changed.

The private output directory beside the candidate is
`clear-continuation-20260917T093756.842891Z/`. It contains the report, tested
script snapshot, input trace, and state/RAM/IWRAM/images at title and Continue.
The preceding producer's native SRAM remains unchanged. The paired native
postgame listings preserve every compared profile byte; no calendar, placement,
later receipt, equipment entitlement or mission ingredient was added.

| Artifact | SHA-1 |
|---|---|
| Report | `9968b6be3d1076756ecf598cb133103afeb624c7` |
| Tested source | `98994ed9b600f33aaa6adfa2040fc2f36c3fdba9` |
| Title capture | `ea73ca74ec63dd163e7caf9b4ddfcf8f3e46d6e0` |
| Continued world capture | `bb5d38cd792316d8239a25282b2a8fb7355af986` |
| Continued EWRAM | `db6ef9459ef9708ef6a692a9f92d57857573a810` |

This resolves the save-task reset/Continue suffix and two real loaded-clear
postgame listing consumers. It does not resolve actual final scenes/credits,
their connection to opcode `18 0E`, or special recruitment/campaign territory
milestones. The producer's old synthetic-parent failure remains failed; its
assertion expected an alternate branch that the actual reset path does not use.
