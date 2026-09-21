.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_help_pointer
.thumb_func
ffta_help_pointer:
    @ Hook at13EA2 saves r3 before its aligned absolute jump. Preserve the
    @ ordinary text loader for every bank except the repointed help bank13.
    pop {r3}
    ldr r5,[sp,#0x14]
    ldr r4,[sp,#0x18]
    lsls r3,r3,#16
    lsrs r3,r3,#15
    ldr r0,=0x0836d6c4
    ldr r0,[r0]
    cmp r1,r0
    bne 1f
    lsls r0,r3,#1
    ldr r2,[r1,r0]
    b 2f
1:
    adds r2,r1,r3
    ldrh r0,[r2]
    adds r2,r1,r0
2:
    ldr r0,=0x08013eb1
    bx r0
.ltorg

.align 2
.global ffta_item_teaching_index
.thumb_func
ffta_item_teaching_index:
    @ CA7A4 selector18 dispatch has already saved r4/r5/LR. The packed
    @ teaching set begins at an odd address: two byte loads are ARM7-safe.
    ldrb r0,[r4,#29]
    ldrb r1,[r4,#30]
    lsls r1,r1,#8
    orrs r0,r1
    pop {r4,r5}
    pop {r1}
    bx r1

.macro wide_set name, continuation, table=0, destination=r0
.align 2
.global \name
.thumb_func
\name:
    ldrb r1,[r0,#29]
    ldrb r0,[r0,#30]
    lsls r0,r0,#8
    orrs r1,r0
    lsls r0,r1,#2
    adds r0,r0,r1
    lsls r0,r0,#2
.if \table
    ldr r1,=\table
    ldr r1,[r1]
    adds \destination,r0,r1
.endif
    @ Each parent saved LR in its prologue. Preserve every live data register;
    @ the parent returns through that original stack frame.
    push {r2}
    ldr r2,=\continuation
    mov lr,r2
    pop {r2}
    bx lr
.ltorg
.endm

wide_set ffta_results_teaching,0x08049005
wide_set ffta_shop_teaching,0x08067187,0x080672ac,r0
wide_set ffta_shop_info_teaching,0x0806fc65
wide_set ffta_party_info_teaching,0x0808c82f,0x0808c8fc,r5
