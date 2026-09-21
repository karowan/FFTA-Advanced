# Native palette reloads — September 18, 2026

Follow-up to `0602e80`. Current private candidate is
`ae167efa50ffc03a656f624f143fc00d81c13159`, resolved through
`build/art/live-palette/poc.json`. Stage157524 bytes, transient state8096 in the
existing8KiB reservation. No package, player save, launcher or running-session
change. Built-in imagegen only; final sprite refinement remains deferred.

## Implementation and boundary

The authenticated copy callback at ROM036D4BC now dispatches OBJ palette-shadow
intersections through a wrapper, preserving the existing091046C9 copy and unit
notification handler. Other copies take a short assembly fast path. The native
epilogue returns its caller continuation in r0; the wrapper preserves that value.

For an existing authenticated class/bank binding, a complete normal or native
19/32 dim bank reload updates generated current colors and its baseline. Active
fade targets, errors, remaining count and task identity survive exactly as they
do for the original native copy. The displayed-color latch changes only at the
next real palette DMA. Partial/unknown displayed copies explicitly refuse and
retire ownership. An unused historical binding retires without claiming a
visible failure; future appearance still requires full native authentication.

This does not reconstruct a fade that began before a binding existed, support
arbitrary partial palettes or prove every native copy mechanism. Ten-slot
capacity, other assets and scene/heap/stack lifetimes remain separate gates.

## Passing evidence

| Candidate / runner | Test | Checks and scope |
| --- | --- | --- |
| ae167 /20260918T083804.004392Z | test-live-art-palette-native |1140; exact rebuild, installed entry and reservation checks. |
| ae167 /same | test-native-art-palette-reload |229; ARMv4T actual copy, normal/dim, completed/active fades, both stack alignments, independent original-engine generated-color continuation, unchanged latch and unrelated unit/BG/RAM copies. Includes displayed refusal, dormant retirement and future unknown appearance rejection. |
| ae167 /same | test-live-art-palette-deployment-variants |587; actual deployment,65 consecutive simultaneous normal/dim observations and no refusal through entry. |
|22d8a2f64c1060f4be4927ea60790f9c27da7bdf /20260918T083142.234965Z | test-live-art-palette-reload |694; actual callback/hardware playback for four normal/dim completed/active reload cases. |
|22d8 /20260918T083307.982358Z | test-live-art-palette-transitions |2933; existing bounded571-frame menu/roster/world route. |

Current reports:
`build/art/live-palette/native/20260918T083804.573124Z/report.json`,
`build/art/palette-reload/20260918T083826.374751Z/report.json`, and
`build/art/live-palette/battle/20260918T083807.258350Z/observed.json`.
Hardware reload report:
`build/art/live-palette/fades/20260918T083145.370718Z/report.json`.
Its normal/dim final screenshots were visually inspected. They remain transport
drafts, not accepted artwork. The22d8 reload/transition evidence is reused for
unchanged recognized-color behavior; ae167 changes only dormant refusal counting.

## Retained failures and corrections

1. Candidate352fd11173b30cbd7c6a835454c7e845f1aab820 failed component return-r0
   comparison (runner20260918T082220.597215Z). Corrected by preserving caller LR.
2. Candidate1ee4c46b4c91acd9c6b34dba8d73d2e8096ea175 passed226 component checks
   with Unicorn's default newer CPU, but actual mGBA black-screened before the
   menu (runner20260918T082644.109991Z). This is a real rejected ROM, not a pass.
   `test-native-copy-stall` reproduced its exact retained RAM/IWRAM and exposed
   ARM execution at a Thumb target. Diagnostic report:
   `build/art/copy-stall/20260918T082930.380988Z/report.json`.
   An untyped linker absolute symbol emitted an ARM LDR-PC veneer requiring
   newer interworking behavior. An explicit Thumb function pointer fixes it;
   the builder rejects that veneer. The component now selects TI925T ARMv4T
   before mapping memory and requires this bad ROM to fail its entry-mode control.
3. Setting that CPU model after mapping memory caused UC_ERR_ARG in runner
   20260918T083142.234965Z. Moving selection before maps corrected the harness;
   runner20260918T083232.376853Z passed227 before the two dormant checks were added.
4.22d8 battle status-control still FAILED strict native-color phase comparison:
   `build/art/live-palette/battle/20260918T083414.348077Z/failed.json` plus
   `trace-audit.json`. All1205 generated overlays were exact, maxdisplay205,
   zero allocation/wrap failures. Move47 frames matched the status-only control;
   response remained two/four frames later. Unsupported count was1 at ready and
   return. The entry trace identified an unknown reload of an already-unused dim
   binding, fixed by ae167's dormant retirement. The passing current deployment
   and ARMv4T tests cover that correction; no new whole-battle acceptance is claimed.

All failed logs and private binaries remain ignored. G01–G04 remain open.
Next: late appearance during active effects, remaining native color/copy and
asset consumers, scene/heap/stack lifetimes, response/phase acceptance, and
reproducible playable packaging. No broad integration run was justified here.
