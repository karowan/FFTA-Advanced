# Failed Chop preview: bounded copy review

The invalid text pointer was not evidence that a unit name had been overwritten. The inventory reviewer established that the renderer object's flags selected the reaction-name branch. The parent then identified a seven-entry relocated racial ability pointer table where native monster species require all24 entries. This file records the independent copy evidence, rather than attributing that table-domain defect to AP ownership.

Frozen failing ROM: `dc02c7b68c950a503441735b1a0d168c847784cd`. Input captures are the disposable `build/expansion/probes/chop-game-lab` prepreview/frame000,003,010,020,030,600 snapshots.

`scripts/probe-chop-preview-copies.py` passed **803 checks**:

- Actor and recognized manager-copy name words were inspected in all seven snapshots. None contained `0902D094`, the relocated racial table pointer. The actor's original packed name was unchanged.
- The bad pointer appeared at IWRAM `03007DE0` in frame030, never in captured EWRAM. A stack occurrence by itself does not prove a stored unit-name mutation.
- Both the native IWRAM-copy dispatch and library-copy entry were replayed from prepreview, frame020 and frame030 RAM, with original native routines as comparators.
- Eight lengths (0,1,2,8,263,264,265,528), both stack residues, owned manager destinations and unowned scratch destinations retained the native return value, copied bytes and destination name word. The source stayed unchanged.
- Existing harness assertions verified preserved registers and balanced stacks.

Static review agrees: `owner_call` restores r0–r7/LR before native copy execution; `ffta_on_unit_copy` is guarded by exact264-byte length and storage format, then writes only a recognized destination's separately owned extra-AP/potion tail. No copy-return or unit-name corruption was reproduced.

This was not an instruction-by-instruction replay of every AP hook during the failed frame, so it is not universal exoneration of all future ownership changes. The confirmed causal fix is preservation of the native racial table's full domain, documented separately by the parent/inventory council.
