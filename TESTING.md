# Deterministic testing

All runtime tests use [Test Expansion.ps1](Test%20Expansion.ps1) and a declared
plan. The default legacy plan is not the whole current release. Select the plan
for the behavior you changed and inspect its dependency expansion before running.

| Change | Plan / entry point |
|---|---|
| Current job-discovery hotfix | scripts/job-visibility-test-plan.json |
| Release archive or launcher | scripts/mod-release-test-plan.json, test-mod-release |
| Approved native art import | scripts/approved-art-test-plan.json |
| Earlier native-art engineering | scripts/native-art-test-plan.json |
| Integrated gameplay | scripts/integration-test-plan.json |
| Original component suites | scripts/expansion-test-plan.json |
| Public source and runtime selection | scripts/source-cleanup-test-plan.json |

```powershell
# Inspect selection only; no game or test runs.
& '.\Test Expansion.ps1' -Plan scripts/mod-release-test-plan.json -Only test-mod-release -List
# Run only the selected behavior and required prerequisites.
& '.\Test Expansion.ps1' -Plan scripts/mod-release-test-plan.json -Only test-mod-release
```

Before a runtime run, identify the affected behavior, exact test IDs and reason.
Include direct consumers and concrete cross-class interactions. Group edits and
fixes before running tests. Reserve a full suite for a major assembled milestone
or a documented regression that cannot be bounded with targeted checks.

The runner preserves logs, JSON/JUnit reports, source/input identities and ROM
hashes under ignored build/expansion/test-runs. It runs serially, holds an OS lock,
stops on failure/timeout and rejects changing inputs. Never edit/build concurrently
with a run. Preserve failures; do not rerun unrelated passing scenarios just to
refresh their dates. Review final results as well as automated assertions.

Some historical tests consume retained fixtures and private artifacts. A fresh
source checkout lacks those inputs. A passed partial suite proves its declared
scenarios, not a full campaign, maximum capacity or physical hardware acceptance.

Documentation-only work requires document/link/format validation and the staged
Git asset guard. It does not require a ROM build or gameplay run. Source tooling
changes use the source-cleanup plan; delivery wrapper changes also use the release
packaging plan. The latter reconstructs isolated patch outputs and validates
launchers without starting mGBA or modifying player saves.

The [historical testing guide](notes/history/TESTING.md) preserves the original
foundation/test-lab procedures and their dated evidence.
