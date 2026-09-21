.syntax unified
.cpu arm7tdmi
.thumb
.section .text

/* Whole-entry hook at080A0014..080A0020. The installed absolute jump saves
 * r3; pop it before capturing the original four register/four stack arguments.
 * Both native incoming stack residues are supported. */
.align 2
.global ffta_combat_geometry_entry
.thumb_func
ffta_combat_geometry_entry:
    pop {r3}
    push {r4-r7,lr}
    mov r4,sp
    mov r5,sp
    subs r5,#16
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    ldr r5,[r4,#20]      @ original SP+0: target_y
    str r5,[sp]
    ldr r5,[r4,#24]      @ original SP+4: action
    str r5,[sp,#4]
    ldr r5,[r4,#28]      @ original SP+8: item
    str r5,[sp,#8]
    ldr r5,[r4,#32]      @ original SP+12: mode
    str r5,[sp,#12]
    bl ffta_combat_geometry
    mov sp,r4
    pop {r4-r7}
    pop {r1}
    bx r1

.align 2
.global ffta_original_combat_geometry
.thumb_func
ffta_original_combat_geometry:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    sub sp,#24
    push {r0}
    ldr r0,=0x080a0021
    mov lr,r0
    pop {r0}
    bx lr
.ltorg
