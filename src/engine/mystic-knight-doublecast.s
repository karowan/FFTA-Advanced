.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_myk_doublecast_construct_hook
.thumb_func
ffta_myk_doublecast_construct_hook:
 pop {r3}
 push {r4-r7,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 sub sp,#24
 ldr r5,[r4,#20]
 str r5,[sp]
 ldr r5,[r4,#24]
 str r5,[sp,#4]
 ldr r5,[r4,#28]
 str r5,[sp,#8]
 mov r5,r8
 str r5,[sp,#12]
 ldr r5,[r4,#16]
 str r5,[sp,#16]
 bl ffta_myk_doublecast_construct
 mov sp,r4
 pop {r4-r7}
 pop {r1}
 bx r1
.align 2
.global ffta_original_doublecast_construct
.thumb_func
ffta_original_doublecast_construct:
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 sub sp,#0x20
 ldr r4,=0x080a81a1
 bx r4
.ltorg
.align 2
.global ffta_myk_doublecast_finish_hook
.thumb_func
ffta_myk_doublecast_finish_hook:
 pop {r3}
 push {r0-r7,lr}
 mov r0,r12
 push {r0}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 mov r0,r8
 bl ffta_myk_doublecast_finish
 mov sp,r4
 pop {r0}
 mov r12,r0
 ldr r0,[sp,#32]
 mov lr,r0
 pop {r0-r7}
 add sp,#4
 movs r0,#0x3e
 strh r0,[r7]
 movs r0,#0x0d
 push {r3}
 ldr r3,=0x080c95a9
 bl .Ldoublecast_call
 pop {r3}
 push {r1}
 ldr r1,=0x08095d71
 mov lr,r1
 pop {r1}
 lsls r0,r0,#24
 push {r0,r1}
 ldr r0,=0x08095d73
 str r0,[sp,#4]
 pop {r0,pc}
.Ldoublecast_call:
 bx r3
.ltorg
