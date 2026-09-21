.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_viking_compatibility_entry
.thumb_func
ffta_viking_compatibility_entry:
    pop {r3}
    push {r4-r5,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_viking_compatibility
    mov sp,r4
    pop {r4-r5}
    pop {r1}
    bx r1
.align 2
.global ffta_original_viking_compatibility
.thumb_func
ffta_original_viking_compatibility:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    adds r4,r0,#0
    push {r0}
    ldr r0,=0x08133a65
    mov lr,r0
    pop {r0}
    bx lr
.ltorg

.macro callback name
.align 2
.global \name\()_entry
.thumb_func
\name\()_entry:
    push {r4-r5,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl \name
    mov sp,r4
    pop {r4-r5}
    pop {r1}
    bx r1
.endm
callback ffta_viking_theft_eligibility
callback ffta_viking_theft_accuracy
callback ffta_viking_theft_accessory
callback ffta_viking_theft_armor
callback ffta_viking_theft_apply
callback ffta_viking_war_cry_apply
callback ffta_viking_challenged_apply
callback ffta_viking_tsunami_apply
callback ffta_viking_zero_magnitude
callback ffta_viking_gil_reaction_apply

.align 2
.global ffta_viking_status_accuracy_entry
.thumb_func
ffta_viking_status_accuracy_entry:
    pop {r3}
    push {r4-r5,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_viking_status_accuracy
    mov sp,r4
    pop {r4-r5}
    pop {r1}
    bx r1

.align 2
.global ffta_original_viking_status_accuracy
.thumb_func
ffta_original_viking_status_accuracy:
    push {r4-r5,lr}
    adds r4,r0,#0
    ldr r0,[r4]
    ldr r1,[r4,#4]
    ldr r2,[r4,#0x30]
    ldrb r2,[r2,#1]
    push {r3}
    ldr r3,=0x0813122d
    mov lr,r3
    pop {r3}
    bx lr
.ltorg
