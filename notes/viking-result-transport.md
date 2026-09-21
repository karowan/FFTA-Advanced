# Native custom-result transport investigation

Work in progress; no upper result-mask bit is allocated or installed.

Static USA native boundary findings, inspected against the private Viking candidate over shared ce83f72:

- 0x08131DD4 writes one bit into context+0x10. It does not itself call a unit status setter. Native ailment callbacks call setters separately.
- The real result executor at 0x080A3460 copies exactly8 bytes from recipient row+0x14 to global context+0x10; 0x080A3478 copies them back after application. Rows have44 bytes, with HP fields beginning+0x1C and MP result+0x20. This result storage survives the action snapshot's retirement.
- Native harmful-status law kind16 at0x08134844 reads caller frame+0x54's committed mask and checks21 predefined native harmful IDs. Prediction instead invokes copied-unit status simulation.
- The native mask getter0x080A883C reads row+0x14+(status>>3) without a status bound. Wrapper0x080DD670 exposes this to native scripts. Direct BL references alone do not prove all script consumers.
- Native compatibility/removal loops0x08131C28,0x081339F0,0x08133A58 stop at status43, but those are application masks, not proof that every result consumer ignores44..63.
- Late wrappers0x0813522C and0x08135750 pass the committed mask pointer through their stack+8 to0x081343C8. A remaining Challenged/Inoculated record cannot prove a new zero-HP refresh landed: a miss may leave the same existing value. Automatic cures can remove a successfully applied status before late Judge, creating the opposite ambiguity.

The safe next step is either a fully audited reserved result field with bounded/sanitized native script getters, or an explicit owned result sidecar whose lifetime follows each native result object through late Judge. This investigation did not authorize a unit-status alias or a private RAM allocation. Root owns integration after this agent's handoff.

Tsunami uses already-native MP presentation fields, not the proposed custom status transport: row+C bit2 and signed row+0x20, established by native0x080A322C..0x080A3250 and0x080A2C64..0x080A2C92.
