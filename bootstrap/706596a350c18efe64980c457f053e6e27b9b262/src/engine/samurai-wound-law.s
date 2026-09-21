.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_higan_harmful_law_entry
.thumb_func
ffta_higan_harmful_law_entry:
    pop {r3}
    mov r1,r10
    cmp r1,#0
    bne deny
    ldr r2,[sp,#0x1c]
    cmp r2,#0
    beq deny
    push {r0}
    ldr r0,=355
    cmp r2,r0
    pop {r0}
    bne original
    mov r3,sp
    push {r0-r7,lr}
    mov r7,r12
    push {r7}
    movs r0,r3
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_higan_harmful_law
    mov sp,r4
    cmp r0,#0
    beq choose_deny
    ldr r0,=0x081349fd
    b chosen
choose_deny:
    ldr r0,=0x081344e3
chosen:
    str r0,[sp,#4]
    pop {r7}
    mov r12,r7
    pop {r0-r7}
    pop {r3}
    mov lr,r3
    bx r0
original:
    ldr r0,=0x08134845
    bx r0
deny:
    ldr r0,=0x081344e3
    bx r0
.ltorg
