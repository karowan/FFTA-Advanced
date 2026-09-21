.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.include "build/expansion/ability-ids.inc"

@ Non-elemental means ignoring the primary element while keeping weapon-mode
@ scaling. Original12F8A4 receives actor/action/item in r0/r1/r2.
.align 2
.global ffta_dark_sword_element_entry
.thumb_func
ffta_dark_sword_element_entry:
    pop {r3}
    push {r0,r3}
    lsls r0,r1,#16
    lsrs r0,r0,#16
    ldr r3,=FFTA_DRK_A2
    cmp r0,r3
    beq 1f
    ldr r3,=FFTA_DRK_A3
    cmp r0,r3
    beq 1f
    pop {r0,r3}
    push {r4,r5,lr}
    lsls r1,r1,#16
    lsrs r0,r1,#16
    adds r5,r0,#0
    lsls r2,r2,#16
    lsrs r4,r2,#16
    push {r0}
    ldr r0,=0x0812f8b1
    mov lr,r0
    pop {r0}
    bx lr
1:  pop {r0,r3}
    movs r0,#0
    bx lr
.ltorg

@ Law kind10 enumerates weapons at13467A. New arts use only the primary,
@ including Double Sword on a legal secondary command. Offhand weapon laws
@ must not classify an unused second weapon as an attack component.
.align 2
.global ffta_dark_sword_law_weapon_entry
.thumb_func
ffta_dark_sword_law_weapon_entry:
    pop {r3}
    push {r1-r7,lr}
    ldr r0,[sp,#52]
    add r1,sp,#40
    ldr r2,[sp,#60]
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_dark_law_weapons
    mov sp,r4
    pop {r1-r7}
    pop {r3}
    adds r5,r0,#0
    cmp r5,#0
    ldr r3,=0x08134687
    bx r3
.ltorg

@ A315A..A3166: r6 is the result row, r9 the action object. Preserve every
@ caller register except native result r0; following native code consumes
@ only r0 until it reloads scratch registers. The first instruction of the
@ continuation explicitly sets N/Z/C, so C's flags are not observable.
.align 2
.global ffta_dark_sword_apply_entry
.thumb_func
ffta_dark_sword_apply_entry:
    pop {r3}
    push {r1-r7,lr}
    ldr r0,[r6]
    ldr r0,[r0]
    movs r3,#0x1e
    ldrsh r1,[r6,r3]
    mov r2,r9
    movs r3,r6
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_dark_sword_apply
    mov sp,r4
    pop {r1-r7}
    pop {r3}
    ldr r3,=0x080a3167
    bx r3
.ltorg
