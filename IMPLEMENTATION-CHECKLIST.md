# Acceptance checklist

Use [the current handoff](HANDOFF.md) and the recipe's declared test plan when
changing the release. The [archived E01-E05 checklist](notes/history/IMPLEMENTATION-CHECKLIST.md)
applies to the earlier engineering build, before accepted character artwork.

For each change:

1. Identify affected behaviors, direct consumers and exact deterministic test IDs.
2. Make a coherent implementation batch, then compile/check the changed source.
3. Run affected checks and required prerequisites through Test Expansion.ps1.
4. Preserve input identities, ROM hashes, logs and failures; review the final result.
5. Package only a candidate accepted by the matching recipe/adapter.
6. Validate archive reconstruction and launcher save isolation for delivery changes.
7. Check documentation links and staged source assets before committing.

Passing allocated lesson or resource records does not establish gameplay
completion. A full integration run needs a substantial milestone or documented
widespread regression. [Testing details](TESTING.md).
