.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_art_queued_obj_write
.thumb_func
ffta_art_queued_obj_write:
    @ Displaced native stores/setups at08000820..08000827.
    str r1,[r2]
    ldr r0,[r4,#8]
    str r0,[r2,#4]
    ldr r0,[r4,#12]
    push {r0-r3,r7,lr}
    mov r0,r12
    push {r0}
    mov r7,sp
    mov r0,sp
    movs r1,#4
    bics r0,r1
    mov sp,r0
    movs r0,r4
    bl ffta_art_live_obj_write
    mov sp,r7
    pop {r0}
    mov r12,r0
    ldr r0,[sp,#20]
    mov lr,r0
    ldr r0,=0x08000829
    str r0,[sp,#20]
    pop {r0-r3,r7,pc}
.ltorg
