.syntax unified
.cpu arm7tdmi
.thumb
.text
@ Result+12 remains the selected buff. Only presentation consumers receive
@ the real weapon; formulas and late Judge callbacks keep their operand.
.macro item source,destination
 push {r0-r7}
 movs r0,\source
 mov r4,sp
 mov r1,sp
 lsrs r1,r1,#3
 lsls r1,r1,#3
 mov sp,r1
 bl ffta_myk_visual_item
 str r0,[r4,#(4*\destination)]
 mov sp,r4
 pop {r0-r7}
.endm
.macro tail address
 push {r0}
 ldr r0,=\address
 mov lr,r0
 pop {r0}
 bx lr
.endm
.macro entry name
 .align 2
 .global ffta_myk_visual_\name
 .thumb_func
 ffta_myk_visual_\name:
 pop {r3}
.endm
entry category
 item r7,0
 cmp r0,#0
 bne 1f
 movs r4,#1
 b 2f
1: movs r1,#3
 ldr r3,=0x080ca7a5
 bl invoke
 movs r4,r0
2: tail 0x080a624d
.ltorg
entry direction
 item r7,1
 ldr r0,[r7]
 ldr r0,[r0]
 ldr r3,=0x0812eed1
 bl invoke
 lsls r0,r0,#24
 asrs r5,r0,#24
 tail 0x080a6421
.ltorg
entry projectile
 item r7,3
 ldr r1,[r7]
 movs r2,r4
 ldrb r0,[r7,#9]
 cmp r0,#3
 bne 3f
 movs r3,#0
3: str r5,[sp]
 tail 0x080a6435
.ltorg
entry actor
 item r7,3
 movs r2,#8
 ldrsb r2,[r7,r2]
 movs r0,r5
 bl actor_native
 tail 0x080a6639
.ltorg
entry impact
 item r5,1
 ldr r0,[r5]
 ldr r0,[r0]
 ldr r3,=0x0812ee99
 bl invoke
 lsls r0,r0,#24
 tail 0x080a573d
.ltorg
entry sound
 item r5,4
 cmp r4,#0
 bne 4f
 movs r0,#1
 negs r0,r0
 b 5f
4: movs r0,r4
 movs r1,#3
 ldr r3,=0x080ca7a5
 bl invoke
5: tail 0x080a58a1
.ltorg
entry magic_actor
 item r4,3
 ldr r0,[r4]
 movs r2,#8
 ldrsb r2,[r4,r2]
 movs r1,r5
 bl actor_native
 item r4,0
 strh r0,[r7]
 tail 0x080ddfe1
.ltorg
.thumb_func
invoke:
 bx r3
.thumb_func
actor_native:
 push {r4}
 ldr r4,=0x0809836d
 mov r12,r4
 pop {r4}
 bx r12
.ltorg
