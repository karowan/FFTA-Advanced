# Experimental provider comparison

These are retained screening prompts and offline preparation tools, separate
from the [accepted native-art workflow](../native-ui-review/README.md).
Gemini request generation and its submission tool were removed at the user's
request. No remaining tool here submits API requests or decrypts credentials.

- [brief.txt](brief.txt): shared text-only front/rear character brief.
- [reference-brief.txt](reference-brief.txt): separate reference-conditioned brief;
  do not present it as an identical text-only comparison.
- [prepare-art-comparison.py](../../../scripts/prepare-art-comparison.py): prepares
  four request configurations through fal, with prompt/request hashes and an
  explicit `paidInferenceAllowed: false` manifest.
- [prepare-comparison-reference.py](../../../scripts/prepare-comparison-reference.py):
  composes existing native reference poses using a recorded crop and integer
  enlargement. Requires ignored local native-reference inputs.

Run the preparation scripts from the repository root using the project's Python
environment. Their output is under ignored `build/art/provider-comparison/`.
The preparation manifest lists the active request files; do not glob older
numbered files left from previous experiments into a new run. Preserve historical
responses and diagnostic evidence separately from current request preparation.

Provider model names and request options are historical experimental settings,
not a claim of current API availability or live validation. Recheck provider
documentation before a separately authorized external generation run. Numeric
seeds across different model families do not identify equivalent latent inputs.

The briefs limit color count but do not supply the approved native palette words.
Their output is therefore a style experiment, not import-ready or approved art.
Production revisions must use existing native palettes, the appropriate native
dimensions, review receipts and per-consumer verification in the accepted guide.
Keep keys, reference PNGs, raw responses and generated art outside Git.
