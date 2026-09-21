# Directional arc AI and launch review

The native directional search already retains an explicit facing. The integration must carry that value into the actual actor wrapper before shared action launch. Reconstructing direction from the selected diagonal recipient loses the selected north/south arc when the center tile is unavailable.

## Verified source and lifetime

The native AI manager is the structure at **020101F8**, not a pointer stored there. C1514 loads that literal, adds54BE, and reads the selected action directly. The directional search node is manager+5290 = **02015488**. Its fields are:

| Node offset | Meaning |
| --- | --- |
| 0 / 4 | Actor / target wrapper pointers |
| 8 / A | Action / item or extra halfwords |
| 1AC / 1AD | Evaluated actor X / Y |
| 1AE / 1AF | Selected target X / Y |
| 1B0 | Explicit selected attack facing,0..3 |
| 1B1 | Successful candidate flag |
| 204 / 214 | Area buffer / movement map pointers |

C01D0 constructs this node; C09B0 calls it. BFDB0 runs the directional search. C0138 reads the chosen facing from local SP+14 and C013A publishes it at node+1B0. The node stays in the manager. C0A08/C0A18 release working allocations referenced by the node, not the manager or its chosen scalar fields.

The later publication block copies node coordinates to manager54B4/54B5 (actor) and54B2/54B3 (target), action to54BE, and extra to54C0. It initially copies the facing to54BA, but **C0BC8 calls BE9F0 and C0BCC overwrites54BA**. This is intentional: BE9F0 chooses the end-turn facing toward another eligible unit, with native random fallback. C1500 reads54BA; its only caller93758 uses it for the end-turn facing event. Therefore54BA is not a stable attack-direction source. The original attack facing remains at **manager5440 = node1B0**. Preserve the native end-turn behavior.

## Native inverse search evidence

BFDB0 uses four rotations from native08394658. Its BFEBC call to B4A1C (return address080BFEC1) generates possible attacker positions around the target using the opposite direction. BFF32 andC0028 then generate the forward area from each candidate origin; nativeB7EA0 tests whether the actual recipient is included. This remains correct for both flanks when the front-center tile is invalid, too high, or has a blocking native flag.

`scripts/test-arc-ai-direction.py` executes BFDB0 and the actual native map readers, installed arc lists, action metadata and membership checker. On combat **d658e596e13febd725a0c312c204f844d2b92e62**, **512 fixtures /5,632 checks pass**: both426/429, all four directions, two evaluated origins, both diagonal flanks, clear/invalid/high/flagged centers, stale stored actor coordinates, and both stack residues. It confirms explicit facing/actor/target publication, four inverse rotations, restored actorF8, unchanged actor/target/grid, and area buffer guards. Native BFDB0..C01D0 is byte-identical to clean ROM.

Compatibility, actor permission, path permission and scoring providers are controlled fixtures. Scoring rewards only the chosen evaluated origin/facing to isolate the search contract. This is native search/list evidence, not a claim that a complete autonomous AI turn was exercised. Results and a frozen ROM are under `build/expansion/probes/arc-ai-direction/<hash>/`.

## Required carry points

The actual AI action setup starts93994, obtains the selected action throughC1514 at9399C, and stores it into the battle manager(r8)+A6. It copies selected target coordinates throughC14D8 at93A1E. At93A66..93A70 it schedules the shared actor action: wrapper `[r8+4]` is copied to `[r8+8]`, then the event state becomes13. This is a suitable AI-only carry point. For426/429, validate node actor wrapper, action, success and direction, then copy node1B0 into the actual wrapper+1F. No extra RAM or global direction override is needed.

The parent integration additionally guards the player confirmation atB6FB6..B6FC0, shared pre-action facing animation96A40..96A4C, and action object direction afterA3AB8. The shared launch site matters because native96A3C calls9D6BC and then9D3A8 updates wrapper1F before animation. A constructor-only override can otherwise preserve the already-wrong wrapper direction.

The constructor atA39F8 initializes object+0 atA3A5A and action+10 atA3A5E before the proposedA3ABA hook. Reading those fields there is valid. NativeA3AB4 derives direction andA3AB8 stores object+8. The narrow hook changes only object+8 for the two arcs, then replays native flag setup and both branches. Original actions retain their derivation.

C13AE is not the primary AI action launch. Its9D6BC call belongs toC127C, reached throughC156C fromBAD32, an auxiliary presentation constructor. Do not patch that call as the AI carry point, and do not globally replace9D6BC.

## Hook verification

`scripts/test-arc-facing-hooks.py` freezes and compiles the current area source independently, installs only the facing veneers over native code, and compares each native continuation. Original action IDs0..346 must preserve registers, flags, stack and caller-visible memory. Arc oracles change only the intended facing; null wrappers, invalid facing and mismatched/unsuccessful AI nodes keep native results. C entry alignment and the exact permitted write locations are hard assertions. This is a fragment/ABI test; rendered player and full AI lifecycle tests remain separate evidence.

### Installed regression,69a844

Combat **69a844aee6a536f29e2b00959acce62de1658e27**, engine **ff193e511745d83c3c945cd819bd98687e925f35**, passes **1,146,112 checks** using `test-arc-facing-hooks.py --current`. All four installed entry pointers are verified against the current engine symbols. The matrix includes every C/V combination and both native SP residues,347 original actions, all four valid facing values, invalid4/255, null wrapper, AI owner/action mismatch and unsuccessful node. Exact native continuation registers, flags, caller frame, object storage, unchanged node and permitted writes pass.

The AI search test now also follows each of its512 results through the actual native publication blockC0B46..C0BCE, installedAI setup93A66, installed shared launch96A40 and the realA39F8 constructor throughA3AC8. **12,800 checks pass** on the same ROM. For this chain, controlledBE9F0 returns a different end-turn facing:54BA changes as native expects while5440 remains the selected attack facing. The selected facing reaches actual wrapper1F, launch manager88 and constructor object8; action and wrapper identity are correct. Constructor metadata is exercised from its true entry, not pre-seeded. The outer score/path providers remain controlled, so this does not claim a complete autonomous AI turn.
