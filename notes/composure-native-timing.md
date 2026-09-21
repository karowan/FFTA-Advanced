# Composure native timing investigation

Historical investigation, September14,2026. The later implementation and
current acceptance are recorded in `turn-supports.md`; the earlier gaps and
observations below describe their original dated candidates.

The deterministic diagnostic `scripts/trace-samurai-move-state.py`, declared
in the expansion test plan, passes in `20260915T021101.620670Z` on private ROM
`c8b98986a406255ff8732fb9fdcfbb045517738f`. It loads a fresh generated battle,
sets the explicit starting formation, and then uses only normal Move, cancel,
and Wait inputs. It records complete RAM and emulator states at every boundary.
No delegated testing agent is involved.

Native getterC9540 and setterC9574 operate on the bit bank at02001F70
(literalC9568). Bit4 is false at turn start, true after moving Jona from1,14
to1,12, false after cancelling that Move, true after repeating the move, and
false after ending the turn. Selecting the original tile also leaves it false.
The diagnostic asserts all six movement-flag outcomes. UnitF6/F7 stay at the original position until turn
commit, while wrapper coordinates change during Move; comparing those fields
alone is insufficient as a general movement policy.

The player command context at `*(0200F438)` has the current unit at+18. Native
battle state at0200F4E8 holds the current wrapper at+4. These observations are
not yet a complete own-turn admission contract: enemy AI, forced actions,
reactions, Doublecast, action-start timing and independent evaluation copies
still need explicit handling. Do not grant Composure by matching a copied
unit's identity back to a live unit, or by testing only its current position.

Next implementation step: capture voluntary-action eligibility and the native
movement flag at the actual action boundary; pass that context through damage
and healing calculations. Combine Composure with other applicable factors
before final rounding. Item use, drain recovery, reactions and damage over time
remain excluded. Later movement must not retroactively change the snapshot.

## Native action-entry evidence

`scripts/trace-composure-action-entry.py` passed in
`20260915T052235.512931Z` on combined shared candidate
`02d4fee3f935e410e2c88d1d41ce91f7ff03fcbf`. Two deterministic actual Fight
routes stop at native A433C before any effect. Marche is the active turn owner
and the acting wrapper in both. An unmoved action retains Move=false through
entry (flags22 ->2A); Move then Fight retains Move=true (flags32 ->3A).
Thus the action-spent bit does not overwrite the Move bit at this boundary.
The script retains intermediate states, RAM, IWRAM and native registers.

This narrows the implementation requirement: capture the Move bit with exact
turn-owner provenance at entry, propagate it to owned evaluation copies, and
exclude reaction origin. Prospective AI movement and full healing/damage
integration still need implementation in the remaining Samurai sweep. The
diagnostic does not prove those behaviors or a completed Composure lesson.
