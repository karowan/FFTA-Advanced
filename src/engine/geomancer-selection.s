.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_geo_center_entry
.thumb_func
ffta_geo_center_entry:
    pop {r3}
    push {r4,r5,lr}
    mov r4,sp
    mov r5,sp
    subs r5,#16
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    ldr r5,[r4,#12] @ fifth native argument at the original SP
    str r5,[sp]
    mov r5,r8
    str r5,[sp,#4] @ exact native selection object for the two player callers
    ldr r5,[r4,#8]
    str r5,[sp,#8] @ native caller return address
    bl ffta_geo_center
    mov sp,r4
    pop {r4,r5}
    pop {r1}
    bx r1
.align 2
.global ffta_geo_original_center
.thumb_func
ffta_geo_original_center:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    sub sp,#12
    push {r0}
    ldr r0,=0x080b592d
    mov lr,r0
    pop {r0}
    bx lr
.ltorg
