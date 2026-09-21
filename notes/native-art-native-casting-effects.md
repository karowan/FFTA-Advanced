# Native-palette casting, secondary commands and auxiliary effects

Full v0.7 engineering remains required; only final artwork/authored poses are
deferred. Candidate `a28b624bb13c8f2f2597a4d4bd3999b17c234b99` is unchanged.
E01 remains accepted. These checks add E02 evidence; E02-E05 remain open.
No installed game, source artwork, player save, launcher or ROM was changed.

## Casting and secondary commands

`test-connected-art-casting.py --native-entry` consumes the authenticated paired
entry report. Each branch loads its own ROM, state, RAM and IWRAM. The control
is the original renderer with the already verified Status shortcut, not a
bypass of the candidate's already-native compositor. Actual menu inputs perform
Move, primary/secondary selection, target confirmation, execution and next turn.

The existing Viking entry is reused. `test-art-native-palette-entry.py
--bangaa-job 119` selects Bangaa Dark Knight before deployment; it publishes
`build/art/native-palette-entry/bangaa-119.json` and preserves the default
`latest.json` used by E01. It passes 66 checks, including exact raw paired entry,
fresh class-resource allocation and idle palettes.

| Test | Checks | Both branch outcomes | Child report in build/art/connected/casting |
| --- | ---: | --- | --- |
| test-art-native-viking-thunder | 4091 | Damage 8; MP 94 | 20260919T074713.986119Z/report.json |
| test-art-native-viking-thundaga | 4159 | Damage 14; MP 80 | 20260919T074726.050562Z/report.json |
| test-art-native-secondary-thunder | 4087 | Damage 8; MP 94 | 20260919T074921.714001Z/report.json |

All three cases compare 450 samples per branch over 1800 frames: native action
mode, complete hardware OAM and palette bytes agree without phase alignment.
Complete native OAM is reconstructed from the actual composition boundary.
The caster's resource, bounded sequence and non-idle tile upload are verified.
Thunder displays mode 63; Thundaga displays modes 11 and 63. Thundaga also checks
native target bank 9 across repeated composition boundaries. AP/inventory stay
unchanged; MP is paid once; action roots retire and the following turn arrives.
Minimum sampled candidate heap is 33668 bytes, largest free block 28164.

Secondary Thunder uses an already allocated Dark Knight119, legal sword, sole
mastered Viking Thunder and declared secondary Reaving118. Neither effective
nor fallback body identity is rewritten. The first attempt stopped at the
command menu because the fixture set command byte +36 but omitted secondary
job cache +8. Native selection writes both (7DFD2..7DFE8, with resolver C9078);
see `job-ui-integration-review.md` and existing native secondary-selection
acceptance. Correcting those declared input fields resolves the fixture error.

Runner `20260919T074713.118518Z` passes both primary casts and secondary entry,
then fails secondary selection. Retained failure:
`build/art/connected/casting/20260919T074757.707687Z/failed.json`.
Runner `20260919T074920.831827Z` passes the affected secondary case only.

## Held axe, projectile and impact

Runner `20260919T080307.041530Z` passes:

| Test | Checks | Child report |
| --- | ---: | --- |
| test-art-queued-trail-upload | 26 | build/art/queued-trail-upload/20260919T080308.215166Z/report.json |
| test-art-native-held-weapon | 124140 | build/art/generated-actions/battle/20260919T080308.889227Z/report.json |
| test-art-native-projectile-impact | 9103 | build/art/generated-projectile/20260919T080358.267462Z/report.json |

Held acceptance observes both attachment-owned channels through native
Move/Fight/next turn. Each branch has 1226 captured observations. Both deal 14
damage and retain 47 HP/14 MP. The control changes only 17 declared axe item
resource fields from 276 to native128, retaining current body assets, renderer
and gameplay code. Its actual SHA-1 is
`a2a0cf9e38ebd1a3a501706e770f4c3fd2dda753`, recorded in report provenance.
The retained report's top-level `baseRomSha1` is inherited weapon-stage metadata,
not the executed control; future reports now distinguish those two fields.
That reporting-only correction did not require replaying the passed battle.

Projectile acceptance uses native Soldier Tomahawk, original/generated icon
control, four generic new-class allies and the same generated impact in both
branches. All three impact poses, moving projectile, native palette cycling,
disjoint effect/body banks and next turn pass. Both branches deal 18 damage,
pay 4 MP (12 remaining) and earn 8 EXP. Sampling remains every four frames.

`native_shared_palette_evidence.py` associates actual wrappers/body tile spans
with native party/opposing baseline or dim colors. It excludes the exact native
unused-OAM sentinel and distinguishes allocated versus on-screen owners.
Named story characters keep their native appearance even when their fallback
gameplay job is new. Inactive custom tags/counters are not used as evidence.
This helper does not accept arbitrary transformed colors or independently
prove body pixel content; the respective body/effect observers do that work.

## Preserved failed attempts and the queued upload proof

1. Runner `20260919T075210.339258Z` fails held ready observation because the new
   palette observer incorrectly includes named story profiles. Capture:
   `build/art/generated-actions/battle/20260919T075211.235512Z`.
2. Runner `20260919T075305.997124Z` fails ready palette comparison because the
   inherited old weapon-stage control still runs custom composition. Capture:
   `build/art/generated-actions/battle/20260919T075306.888734Z`.
   The current resource-only control replaces that mismatched baseline.
3. Runner `20260919T075500.462756Z` completes both actions with identical
   outcomes but fails one original trail display at attack57. Capture:
   `build/art/generated-actions/battle/20260919T075501.346555Z`.
   Entry3's five tiles, queued through opcode0 entry4, have just arrived while
   entry5's seven tiles are newly pending. The older observer checked a direct
   predecessor or an entirely unchanged anchor and could not prove this case.
4. `native_queued_upload.py` accepts only the exact preceding observed command,
   one video frame later, same resource/mode/allocation/channel, both pending
   flags, exact source/layout/command progression, and its uploaded pixels plus
   unchanged complete allocation tail. Unknown controls, stale state, different
   channels, altered source/phase and changed pixels/tail are rejected.
5. Proof runners `20260919T080059.345286Z` and `20260919T080151.526196Z` fail
   native actor reproduction. They incorrectly reused the null queue argument
   from an older opcode0 proof. Graphics opcode1 needs a transfer context;
   with null it defers the new transfer and retains the old queued layout.
   The second run retains the exact two differing actor bytes.
6. The final proof supplies a declared available transfer queue on a detached
   clone. Original 21290 reproduces all 72 captured actor bytes at both stack
   residues and enqueues one transfer. This is controlled native execution,
   not reconstruction of the entire previous machine/queue state. The final
   live held run uses the new proof exactly once, original attack57.

The first three failed held runners skip the later projectile step. The two
failed proof runners do not supply held/projectile acceptance. All are retained
and pinned with the final passes in `native-art-native-casting-effects-evidence.json`;
the exact queued-trail inputs are in `native-art-queued-trail-inputs.json`.
The passed proof directory also retains the exact input-index bytes it used;
the committed source index uses LF newlines. Future runs archive that input
index directly, so Git newline conversion cannot obscure recorded provenance.

## Remaining acceptance

Reuse the accepted E01 evidence, all-ten graph/water contracts, 20 Fight weapon
combinations, 19 Combo initiations and current new-body Combo participation.
The 19 performance pins and 18 Combo pins remain exact after this work. Do not
repeat those checks solely for these new observers or documentation changes.

Complete E02's final consumer/dependency review, including remaining UI and
effect-family coverage. These representative cases do not establish every
spell combination or unsampled frame. E03 still needs demanding reachable
encounter/lifetime acceptance; original formation23 is the documented next
capacity lead. E04 campaign/ending/postgame and save/cold-load relevance, and
E05 clean full rebuild, review and independent-save delivery remain open.
