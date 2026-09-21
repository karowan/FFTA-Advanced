# Final battle scene bridge

Selected runtime IDs: `verify-integrated-assembly-prerequisites` and
`test-final-battle-scene-bridge`. The missing behavior is the original event26
(Royal Valley) dispatch through final deployment, battle exits and result
scenes into101. Reuse the accepted101→105/credits/save suffix; stop when101
begins. No broad integration selection is justified for this one missing path.

Initial event26 dispatch is declared once from the authenticated ordinary
disposable save. Party slots receive999 current/maximum HP before deployment.
After native deployment, hostile-combatant HP zero is a controlled
exit precondition. This is not evidence of earned final-mission eligibility,
winning combat, or earlier territory placement. Native deployment, battle
exit detection, result dialogs and scene transitions remain active. Inputs
and bounds are deterministic; original ranges and all source hashes are kept.

## Accepted bridge

Run `20260917T111935.650782Z` passes assembly verification and
`test-final-battle-scene-bridge-resume`:19 checks in20.9seconds. Scenes follow
93→95→96→97→98→100→101. The original three battle-start opcodes occur at
`0x089B644B`, `0x089B6B63` and `0x089B6ED5`. Every battle constructs actual
native deployment actors. The controlled exit targets6,3,3 hostile actors,
respectively, using native allegiance byte0x29 bit7. All party, judge, guest
and story actor records remain unchanged by that input. Native victory
detection, result scenes and scene100 queue101 without another substitution.
Flash and the reusable source save remain unchanged. Root reviewed the final
deployment and scene100/101 images.

Private report beside the candidate:
`final-battle-bridge-20260917T111936.326292Z/report.json`, SHA1
`ac0a0981e8ce9cf8ad4598e5c4c442b577e89644`. Script SHA1:
`763049f0c565c38d307128259e5fa6aaca8d93b7`. Instrumented image SHA1:
`d415c5a6956cdc6edd79289d68777c1312b109b5`. The pinned helper is the accepted
ending-scenes test; only the initial event dispatch and battle-start observer
are changed in this private image. Shipping ROM stays
`1b070824a8dad4995434eee3ab40fa08187a6120`.

The accepted run resumes an authenticated native Royal Valley deployment
checkpoint from the original failed prefix. Report SHA1
`474e54fd9b39a8ef293b7835da5bdc25e2a8503a` pins that prefix. Its complete input
sequence and image are retained; checkpoint file hashes and the image identity
are checked before restoration. A full reproduction is available as
`test-final-battle-scene-bridge`; the tested suffix selection is:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-final-battle-scene-bridge-resume
```

## Failures and limits

- Run111322 reached the real deployment, then lost the level-one source
  Marche before the player-turn oracle. Run111521 applied999 HP but still
  lost him during native enemy turns before that oracle. Both remain failed.
- Run111746 passed its assertions, but root review found an invalid setup:
  it zeroed every non-party actor, including judges and story actors. That
  pass is **superseded and excluded from acceptance**. The corrected selected
  run above filters actual hostile allegiance and asserts every other actor
  is unchanged.
- Initial event26 is explicitly dispatched; earned mission eligibility and
  the natural world selection that invokes it are not established. No claim
  is made about mission26's receipt/reward association in this isolated setup.
- Combat victory is a controlled precondition. Intermediate combat-triggered
  scenes94/99 are not exercised; combat balance, attack mechanics and a complete
  campaign are not proved by this bridge. The101-ending suffix is reused as
  separate applicable evidence, not presented as one continuous playthrough.

No shipping edits, broad integration run, player-save changes or visible game
launch occurred. A01/V06, final R02 review/acceptance and R03 delivery stay open.
