.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_original_recruit
.thumb_func
ffta_original_recruit:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    ldr r3,=0x080d2425
    bx r3
.ltorg

@ Native entry can arrive with either stack residue; C always gets alignment8.
.align 2
.global ffta_quin_candidate_entry
.thumb_func
ffta_quin_candidate_entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_quin_candidate
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1

.macro observe
    push {r0-r7,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    ldr r0,=0x02000000
    bl ffta_quin_observe
    mov sp,r4
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
.endm
.align 2
.global ffta_quin_accept_entry
.thumb_func
ffta_quin_accept_entry:
    observe
    ldr r3,=0x080d2f2d
    bl 1f
    ldr r0,[r5]
    adds r0,r0,r4
    ldr r3,=0x080807dd
    bx r3
1:  bx r3
.ltorg

.align 2
.global ffta_quin_swap_entry
.thumb_func
ffta_quin_swap_entry:
    adds r0,r7,#0
    ldr r3,=0x080ca1bd
    bl 1f
    str r0,[r7]
    observe
    movs r6,#0x2b
    movs r4,#0x2e
    ldr r3,=0x08062011
    bx r3
1:  bx r3
.ltorg
