.syntax unified
.cpu arm7tdmi
.thumb
.section .text

/* Whole-entry hook at 080B42E4..080B42F0: native targeting range mode word
 * (action, item). The installed absolute jump saves r3; restore it first. */
.align 2
.global ffta_myk_target_mode_entry
.thumb_func
ffta_myk_target_mode_entry:
    pop {r3}
    push {r4,lr}
    bl ffta_myk_target_mode
    pop {r4}
    pop {r1}
    bx r1

/* Replays the displaced native prologue and continues at 080B42F0. */
.align 2
.global ffta_original_target_mode
.thumb_func
ffta_original_target_mode:
    push {r4-r7,lr}
    lsls r0,r0,#16
    lsrs r5,r0,#16
    adds r7,r5,#0
    lsls r1,r1,#16
    lsrs r0,r1,#16
    push {r0}
    ldr r0,=0x080b42f1
    mov lr,r0
    pop {r0}
    bx lr
.ltorg
