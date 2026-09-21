.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_equipment_layout
.thumb_func
ffta_equipment_layout:
    pop {r3}
    push {r0-r4,lr}
    movs r0,r1
    movs r1,r2
    mov r4,sp
    mov r2,sp
    lsrs r2,r2,#3
    lsls r2,r2,#3
    mov sp,r2
    bl ffta_axe_layout_guard
    mov sp,r4
    cmp r0,#0
    bne 1f
    ldr r4,[sp,#20]
    mov lr,r4
    pop {r0-r4}
    add sp,#4
    @ Displaced native CABA8 prologue, with the original return address.
    push {r4-r7,lr}
    mov r7,r9
    mov r6,r8
    push {r6,r7}
    sub sp,#24
    mov r9,r0
    push {r0}
    ldr r0,=0x080cabb5
    mov lr,r0
    pop {r0}
    bx lr
1:
    ldr r1,[sp,#4]
    ldr r2,[sp,#8]
    ldr r3,[sp,#12]
    ldr r4,[sp,#20]
    mov lr,r4
    ldr r4,[sp,#16]
    add sp,#24
    bx lr
.ltorg

.align 2
.global ffta_icon_draw_entry
.thumb_func
ffta_icon_draw_entry:
    mov r2,lr
    movs r3,r5
    push {r4-r6,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_equipment_icon_draw
    mov sp,r4
    pop {r4-r6}
    pop {r1}
    bx r1
.global ffta_icon_palette_entry
.thumb_func
ffta_icon_palette_entry:
    mov r1,lr
    movs r2,r5
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_equipment_icon_palette
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1

.align 2
.global ffta_equipment_weapon_class
.thumb_func
ffta_equipment_weapon_class:
    push {r2,r3,r4,lr}
    movs r0,r6
    mov r4,sp
    mov r2,sp
    lsrs r2,r2,#3
    lsls r2,r2,#3
    mov sp,r2
    bl ffta_native_is_weapon
    mov sp,r4
    movs r1,r0
    pop {r2,r3,r4}
    pop {r0}
    mov lr,r0
    ldr r0,=0x080cad13
    bx r0
.ltorg

.macro shield_jobs name, allowed, original
.align 2
.global \name
.thumb_func
\name:
    cmp r2,#117
    beq 1f
    cmp r2,#119
    beq 1f
    cmp r2,#125
    beq 1f
    @ Preserve the native condition flags for the original branch.
    subs r0,r2,#2
    lsls r0,r0,#24
    lsrs r0,r0,#24
    cmp r0,#1
    push {r0}
    ldr r0,=\original
    mov lr,r0
    pop {r0}
    bx lr
1:
    ldr r0,=\allowed
    bx r0
.ltorg
.endm
shield_jobs ffta_equipment_shield_jobs,0x080cad89,0x080cad5d
.align 2
.global ffta_equipment_twohand_jobs
.thumb_func
ffta_equipment_twohand_jobs:
    @ Hook starts at aligned CADC4, retaining the prior hand-count compare.
    bhi 2f
    cmp r2,#117
    beq 1f
    cmp r2,#119
    beq 1f
    cmp r2,#125
    beq 1f
    subs r0,r2,#2
    lsls r0,r0,#24
    lsrs r0,r0,#24
    push {r0}
    ldr r0,=0x080cadcd
    mov lr,r0
    pop {r0}
    bx lr
1:
    ldr r0,=0x080cadd5
    bx r0
2:
    ldr r0,=0x080cadff
    bx r0
.ltorg
