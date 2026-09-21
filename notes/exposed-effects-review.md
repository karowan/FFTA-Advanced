# Exposed lifecycle and incoming damage review

This is an isolated development layer. Fell Cleave431 remains disabled in the
shared build. Do not infer full gameplay acceptance from lifecycle primitives.
The base frozen for these tests is combat69a844aee6a536f29e2b00959acce62de1658e27,
engineff193e511745d83c3c945cd819bd98687e925f35. The tests accept a frozen
ROM/manifest/engine/symbol snapshot so shared rebuilds cannot silently change it.

## Ownership and policy

The existing explicit owned byte has a coordinated packed layout: bit0 Exposed;
bits1..3 reserved for Centered T2/skip-current; bits4..7 reserved. Exposed gameplay
application sets bit0, checks mask bit0 and expiry clears only bit0. Full unit
destruction/construction clears the entire owned byte through the existing
storage/copy layer. Copies, native saves and explicit evaluated containers move
the entire byte. No new RAM reservation, identity lookup or pointer fallback.

Native Immunity support11 is an explicitly approved custom harmful-status policy:
it makes431 unavailable and rejects commitment before MP payment. Native
CD50C resolves the actual assigned support. This is not an alias to the native
effect whitelist at12D0BC. Inoculation never prevents this self-inflicted state;
no additional boss or all-status immunity is inferred.

## Verified lifecycle sites

| Event | Native boundary | Contract |
| --- | --- | --- |
| Paid commitment | A45C6..A45D4, before MP writeA45D2 | Replay native remaining-MP subtraction/check; SP+4C globalaction and SP+74 actorwrapper. Only431 sets bit0. Rejection goesA4968 before payment. ResumeA45D4, preserving its six external bypass branches. |
| Next own turn | 93022 | R0 selected wrapper returned by9F850. Clear before native turn-start MP+5 and turn-counter increment. Actual Wait/facing fixture selects Colette020005A8 and clears only her bit. |
| Native KO cleanup | 97298 | Native99BAC wrapper death cleanup, Doom snapshot9E37A and instantKO132B30 call this reset. Clear even if HPwrite follows cleanup (actor pending-cost pathA22F0). |
| Scripted KO | 1230F2 | Eventstatus0 directly zeros HP/MP at1230FA/FE and bypasses97298. R4event,R5wrapper. Clear only status0, then replay native writes; all44status fragments differential. |
| Petrify | CDDD0 andCD884 | Dedicated setter and generic status6 setter. Clear only nonzero u8value. CD92C independently reads E8bit6. |
| Job change | C8C3C | R4unit,R6newjob,oldunit+7 still available. Clear only a changed job. Native fullC8C24 original/new/same-job differential. |
| Battle end | 95214 | Clear36 canonical owners before original9A950(party,24) refresh. Continue95220, including its flag halfword read. Fragment differential through9522A. |
| Broad remedy | Effect79 callback3A8B64 | Action264 Cureall stage8B descriptor084F1700 originally invokes noop13353C. Repoint only callback; native status allow/cure masks stay native. Query flag10 prevents Exposed removal. |

Native global CT tick9E710 is not own-turn expiry. Global selected-unit setter
294E4 is reused by previews/menus and is not an acceptable turn-start hook.

The exact guarded patch spans and displaced instructions are in
scripts/patch-exposed-effects.mjs and src/engine/exposed-effects.s. C calls align
the stack for both SP residues0/4. No shared builder invokes this helper yet.
Application is an explicit opt-in argument;431data/availability is not enabled.

## Verification completed

`test-exposed-effects.py --snapshot <frozen-directory>` compiles only the new
files, uses the real current owned getter via an explicit Thumb thunk, verifies
unused private ROM space, and invokes the actual guarded patch helper. Native
comparisons cover all36 canonical owners, both stack residues, all44 status
bits, complete wrapper death cleanup with actual ally/enemy wrappers, complete
job change, native Cureall13388C (including no-native-ailment), battle-end and
scriptKO fragments, actual captured turn/payment frames, support11 admission and
all347 original action payment paths. It compares whole EWRAM and relevant ABI.

`test-exposed-expiry-in-game.py --base-sha <hash>` performs native Fight preview,
cancel and Wait/facing on a disposable same-layout fixture. All36 state bits
remain through preview/cancel; only Colette expires at her own turn start.
Inventory/AP/preferences and the3FF44guard remain unchanged. This is a private
hook diagnostic, not a fresh production431battle acceptance test.

The packed primitive change is separately exercised by
`test-gladiator-finishers.py`: all256 byte patterns across application, immunity,
events and signed/direct damage flags. The isolated suite passes20,386 checks;
bits1..7 remain unchanged by Exposed operations.

## Incoming modifier investigation and remaining integration

12FE38 is shared physical/magical formula code, not proof of physical damage.
Native CCD50(action,29), actionrecord+10bit18, selects the physical stat/support
class when true (12FD62..78,12F4A4). Fire/Cure arefalse, Rush/WildSwing true.
Throw148/Hurl211 use dedicated magnitude selectors36/38 and native weapon modes
1/2 despite that bit beingfalse; their physical inclusion is explicit.

Native131B20 resolves the magnitude callback, effect sign133988, cancellation
and result. Native1318D4 doubles P,131A98 triples,131AC0 halves and131AF0 quarters
after12FE38. Putting Exposed into P itself would round too early for original
callbacks. Prefer a final native stage hook, plus separate Fight-preview and
Combo boundaries. New custom physical coefficients must join Exposed6/5 in
their existing rational product once; skip the later native multiplier for them.

`probe-exposed-damage-domain.py` catalogs all46 native magnitude selectors and
all347 original action stages with effect kind/support-class bit. Kind1 is HP;
kind2 is MP; kind3 splits a scalar between HP/MP; kind4 is JP. Backdraft/BodySlam
selector42 is a reflected self-cost and must not be scaled. Recovery selectors
18/35 must not receive a second multiplier. Native fixed/percentage actions
currently have neutral/nonphysical native support classification; do not import
outgoing-support exclusions or classify them solely by their names.

## Installed private final boundaries and acceptance

The optional `incoming:true` patch installs131B4A (after native callback, sign
and kind),130200 (only Fight0 scales at this outer boundary) and130454 (Combo).
The native stage classifier follows the catalog above and skips custom rational
coefficients. `ffta_exposed_incoming_numerator(damage,recipient)` returns6or5;
custom shared finalizers must combine that numerator/5 before their one division.
It returns5 for zero/negative values, leaving healing and absorption unchanged.
No cost/MP/tick path is hooked. Native cancellation remains after stage scaling.

Current private ROM6d0a51385101e1b1391d4d988f578ba265469408 passes:

-18,720 native lifecycle/commit comparisons.
-23,680 native stage/Fight/Combo, packed-sign and explicit-owned-copy checks.
  Scoped evaluator copy retains its independent byte after canonical source
  changes; an unregistered same-content copy and a retired scope are unowned.
-357 complete nativeA433C executor comparisons (347 originals plus10 current
  custom IDs), with inactiveExposed and other packed bits retained; no skips.
 774 observed successful magnitude boundaries have context+4==context+8.
-Actual mGBA Fight preview/Doit/execution: valid Bangaa Jona+6race2/+5,+7job17,
 original equipment215/303, same native seed2 and target250HP. Normal24damage
 gives226HP; Exposed28damage gives222HP. Animation returns control. All saved
 inventory/AP/preferences,36 packed bytes and3FF44guard are unchanged.
-Actual preview/cancel preserves state; Wait/facing expires only the next actor.

The old private payment spanA45CE..A45DA was rejected by live comparison.
A4552/58/5C/60/64/6A branch directly toA45D4; the long-jump literal overwritten
there made nativeFight stall before its executor. Parent engine council found
the same defect independently through fullA433C comparison. The corrected
14-byteA45C6..A45D4 span preserves that incoming landing. A mid-block test alone
was insufficient; `test-exposed-native-executor.py` now captures its own entry
fixture and exercises the complete function.

Recipient ownership is explicit: committedA2F08/A2F12 andA306A/A306E select the
same R6recipient-object unit for context+4/+8. Law134320/134340 usesR4 for both;
preview13026A/13029A usesR8 for both. No flag merging or identity lookup needed.

Composition inputs: compile exposed-effects.c/.s, then call guarded
patchExposedEffects with lifecycle plus optional incoming. Application remains
separately opt-in; do not enable431 until availability invokes
ffta_exposed_can_apply and custom damage combines the returned numerator once.
The paid site must be shared with the Centered layer, not patched twice.
ffta_exposed_expire calls optional weakffta_centered_event(unit,event):1 ownturn,
2KO,3Petrify,4battleend,5jobchange,6broadremedy. Each layer owns its mask; Centered
ignores1/6 and uses its own nativeendturn expiry site.

Outstanding before production431: custom rational-factor integration, native
availability admission, and actual431hit/miss/retaliation/MP16 acceptance;
actualKO/Petrify/battleend/remedy with431; copiedAI/law and cold suspend on the
fully composed ROM. Current state-storage/copy persistence has separate earlier
acceptance, but this note does not claim the full composed431 lifecycle yet.
