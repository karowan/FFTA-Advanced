.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_myk_fight_law_hook
.thumb_func
ffta_myk_fight_law_hook:
 pop {r3}
 mov r0,sp
 push {r0-r7,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 mov r1,r10
 bl ffta_myk_fight_law
 mov sp,r4
 cmp r0,#0
 blt 1f
 beq 2f
 ldr r0,=0x081349fd
 b 3f
2: ldr r0,=0x081344e3
3: str r0,[sp]
 pop {r0-r7}
 pop {r3}
 mov lr,r3
 bx r0
1: pop {r0-r7}
 pop {r3}
 mov lr,r3
 @ Original selector, including the loop's existing value index.
 ldr r1,[sp,#0x58]
 ldrb r0,[r1,#4]
 subs r0,#1
 cmp r0,#19
 bhi 4f
 ldr r3,=0x0813441d
 bx r3
4: ldr r3,=0x081349e3
 bx r3
.ltorg
