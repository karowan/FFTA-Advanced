# Historical build inputs

These are authenticated source files needed by the gameplay rebuild. They are
data for the build driver, not a second editable engine tree. The index records
their original revisions and SHA-256 values. No old Git history, game images,
tools or generated code payloads are included. The source loader fails on changed
bytes. Update normal source under src/ and scripts/, not these snapshots.

Only gameplay bootstrap and its three source overrides are bundled. Older
campaign/evidence audits and historical diagnostic scripts still require the
private development history and reports; they are not fresh-checkout acceptance.
