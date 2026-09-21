.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro callback entry,target
.align 2
.global \entry
.thumb_func
\entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl \target
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
.endm
callback ffta_drk_eligibility_entry,ffta_drk_eligibility
callback ffta_drk_healing_entry,ffta_drk_healing
.align 2
.global ffta_drk_usable_entry
.thumb_func
ffta_drk_usable_entry:
    pop {r3}
    b ffta_drk_usable_callback
callback ffta_drk_usable_callback,ffta_drk_usable
.align 2
.global ffta_drk_original_usable
.thumb_func
ffta_drk_original_usable:
    push {r4-r7,lr}
    mov r7,r8
    push {r7}
    sub sp,#4
    movs r5,r0
    lsls r1,r1,#16
    push {r0}
    ldr r0,=0x08133e25
    mov lr,r0
    pop {r0}
    bx lr
.ltorg

callback ffta_drk_last_resort_apply_entry,ffta_drk_last_resort_apply
callback ffta_drk_tbn_apply_entry,ffta_drk_tbn_apply

callback ffta_drk_zero_magnitude_entry,ffta_drk_zero_magnitude

.align 2
.global ffta_drk_mp_cost_entry
.thumb_func
ffta_drk_mp_cost_entry:
    pop {r3}
    b ffta_drk_mp_cost_callback
callback ffta_drk_mp_cost_callback,ffta_drk_mp_cost
.align 2
.global ffta_drk_original_mp_cost
.thumb_func
ffta_drk_original_mp_cost:
    push {r4,r5,lr}
    movs r5,r0
    lsls r1,r1,#16
    lsrs r0,r1,#16
    cmp r0,#0
    beq .Ldrk_zero_mp
    ldr r3,=0x0812eda9
    bx r3
.Ldrk_zero_mp:
    movs r0,#0
    pop {r4,r5}
    pop {r1}
    bx r1
.ltorg
