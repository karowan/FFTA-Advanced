.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_chemist_status_entry
.thumb_func
ffta_chemist_status_entry:
 pop {r3}
 push {r0-r7,lr}
 mov r7,r12
 push {r7}
 mov r4,sp
 ldr r2,[r4,#36]
 movs r3,r4
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_chemist_status_gate
 cmp r0,#0
 bne .Lblocked
 mov sp,r4
 ldr r7,[r4,#36]
 mov lr,r7
 pop {r7}
 mov r12,r7
 pop {r0-r7}
 add sp,#4
 @ Complete original131DD4..131DE8, with identical register/flag results.
 adds r0,#0x10
 asrs r3,r1,#3
 movs r2,#7
 ands r2,r1
 adds r0,r0,r3
 movs r1,#1
 lsls r1,r2
 ldrb r2,[r0]
 orrs r1,r2
 strb r1,[r0]
 bx lr
.Lblocked:
 mov sp,r4
 ldr r7,[r4,#36]
 mov lr,r7
 pop {r7}
 mov r12,r7
 pop {r0-r7}
 add sp,#4
 bx lr
