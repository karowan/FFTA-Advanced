.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_reaction_queue_entry
.thumb_func
ffta_reaction_queue_entry:
 pop {r3}
 push {r0-r7,lr}
 mov r7,r12
 push {r7}
 mov r4,sp
 movs r0,r4
 adds r0,#40
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_action_bind_queue_frame
 movs r0,r4
 adds r0,#40
 bl ffta_reaction_queue_dispatch
 cmp r0,#0
 bne .Lcustom
 mov sp,r4
 ldr r7,[r4,#36]
 mov lr,r7
 pop {r7}
 mov r12,r7
 pop {r0-r7}
 add sp,#4
 ldr r2,[r4]
 cmp r2,#0
 beq .Lempty
 ldrb r0,[r4,#14]
 subs r0,#1
 push {r0,r1}
 ldr r0,=0x080a4ae9
 str r0,[sp,#4]
 pop {r0,pc}
.Lempty:
 push {r0,r1}
 ldr r0,=0x080a529d
 str r0,[sp,#4]
 pop {r0,pc}
.Lcustom:
 mov sp,r4
 ldr r7,[r4,#36]
 mov lr,r7
 pop {r7}
 mov r12,r7
 pop {r0-r7}
 add sp,#4
 push {r0,r1}
 ldr r0,=0x080a4c3b
 str r0,[sp,#4]
 pop {r0,pc}
.ltorg
