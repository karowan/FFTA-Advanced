.syntax unified
.cpu arm7tdmi
.thumb
.section .text
@ Only the owned 0x2660-byte workspace callsite uses this allocation policy.
.align 2
.global ffta_art_workspace_allocate
.thumb_func
ffta_art_workspace_allocate:
    push {r4,lr}
    lsrs r1,r0,#2
    ldr r0,=0x0200f434
    ldr r0,[r0]
    bl ffta_art_workspace_native_allocate
    cmp r0,#0
    beq 1f
    adds r0,#12
1:
    pop {r4}
    pop {r1}
    bx r1
.ltorg
.align 2
.thumb_func
ffta_art_workspace_native_allocate:
    @ Exact native 08006EC0 prologue, with only its free-block selector replaced.
    push {r4-r7,lr}
    mov r7,r8
    push {r7}
    sub sp,#8
    mov r8,r0
    lsls r1,r1,#16
    lsrs r5,r1,#16
    add r3,sp,#4
    movs r1,r5
    mov r2,sp
    bl ffta_art_workspace_find
    ldr r3,=0x08006ed9
    bx r3
.ltorg
