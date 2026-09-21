.syntax unified
.cpu arm7tdmi
.thumb
.section .text

@ Interior stubs save r3 before the absolute jump. Helpers preserve every
@ other native register except the explicit r0 result. No iterator storage.
.macro begin_iter name, saved=1
.align 2
.global \name
.thumb_func
\name:
.if \saved
    pop {r3}
.endif
    push {r0-r7,lr}
.endm
.macro call_iter target
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl \target
    mov sp,r4
    str r0,[sp]
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
.endm
.macro tail address
    push {r0}
    ldr r0,=\address
    mov lr,r0
    pop {r0}
    bx lr
.endm
.macro battle_owner
    ldr r0,=0x0200f438
    ldr r0,[r0]
    ldr r0,[r0,#0x18]
.endm
.macro low_result
    lsls r0,r0,#16
    lsrs r0,r0,#16
.endm

begin_iter ffta_ordinary_init
    movs r0,r6
    movs r1,#0
    call_iter ffta_descriptor_successor
    cmp r0,#0
    beq 1f
    low_result
    mov r10,r0
    movs r0,#0
    strb r0,[r6,#8]
    mov r9,r0
    tail 0x08026d6b
1:  movs r0,#0
    strb r0,[r6,#8]
    ldrb r1,[r6,#4]
    mov r10,r1
    mov r9,r0
    ldrb r2,[r6,#5]
    cmp r10,r2
    ble 2f
    tail 0x08026f79
2:  tail 0x08026d6b
.ltorg

begin_iter ffta_ordinary_next
    movs r0,r6
    mov r1,r10
    call_iter ffta_descriptor_successor
    cmp r0,#0
    beq 1f
    low_result
    cmp r0,#255
    bhs 3f
    mov r10,r0
    tail 0x08026d6f
1:  movs r2,#1
    add r10,r2
    ldrb r0,[r6,#5]
    cmp r10,r0
    bgt 3f
    tail 0x08026d6f
3:  tail 0x08026f79
.ltorg

begin_iter ffta_restricted_init
    movs r0,r4
    movs r1,#0
    call_iter ffta_descriptor_successor
    cmp r0,#0
    beq 1f
    low_result
    movs r7,r0
    movs r0,#0
    strb r0,[r4,#8]
    mov r10,r0
    tail 0x08026fbf
1:  movs r0,#0
    strb r0,[r4,#8]
    ldrb r7,[r4,#4]
    mov r10,r0
    ldrb r1,[r4,#5]
    cmp r7,r1
    bgt 3f
    tail 0x08026fbf
3:  tail 0x080270a5
.ltorg

@ Exactly eight displaced bytes. r3 is dead: neither continuation reads it
@ before a native function call overwrites this caller-saved register.
begin_iter ffta_restricted_next,0
    movs r0,r4
    movs r1,r7
    call_iter ffta_descriptor_successor
    cmp r0,#0
    beq 1f
    low_result
    cmp r0,#255
    bhs 3f
    movs r7,r0
    tail 0x08026fbf
1:  adds r7,#1
    ldrb r2,[r4,#5]
    cmp r7,r2
    ble 2f
3:  tail 0x080270a5
2:  tail 0x08026fbf
.ltorg

begin_iter ffta_second_init
    battle_owner
    ldr r1,[sp,#56] @ original SP+14: this command's slot
    movs r2,#0
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    movs r6,r0
    b 2f
1:  mov r0,r8
    ldrb r6,[r0,#4]
    ldrb r1,[r0,#5]
    cmp r6,r1
    bgt 3f
2:  lsls r1,r6,#3
    ldr r0,[sp]
    adds r4,r0,r1
    tail 0x08027a0b
3:  tail 0x08027abf
.ltorg

begin_iter ffta_second_next,0
    battle_owner
    ldr r1,[sp,#56]
    movs r2,r6
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    cmp r0,#255
    bhs 3f
    movs r6,r0
    b 2f
1:  adds r6,#1
    mov r1,r8
    ldrb r1,[r1,#5]
    cmp r6,r1
    ble 2f
3:  tail 0x08027abf
2:  lsls r1,r6,#3
    ldr r0,[sp]
    adds r4,r0,r1
    tail 0x08027a0b
.ltorg

begin_iter ffta_ai_init
    movs r0,r6
    ldr r1,[sp,#48] @ original SP+C: this command's slot
    movs r2,#0
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    movs r4,r0
    lsls r0,r0,#3
    adds r5,r2,r0 @ native bank r2 preserved across helper
    tail 0x08133ff9
1:  mov r0,sp
    ldrb r1,[r0]
    lsls r0,r1,#3
    adds r5,r2,r0
    movs r4,r1
    mov r1,r8
    ldrb r1,[r1]
    cmp r4,r1
    bgt 3f
    tail 0x08133ff9
3:  tail 0x0813407b
.ltorg

begin_iter ffta_ai_next
    movs r0,r6
    ldr r1,[sp,#48]
    movs r2,r4
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    cmp r0,#255
    bhs 3f
    subs r0,r0,r4
    adds r4,r4,r0
    lsls r0,r0,#3
    adds r5,r5,r0
    tail 0x08134001
1:  adds r4,#1
    adds r5,#8
    mov r0,r8
    ldrb r0,[r0]
    cmp r4,r0
    ble 2f
3:  tail 0x0813407b
2:  tail 0x08134001
.ltorg

.macro party_preview slot
    ldr r0,=0x03002818
    ldr r0,[r0]
    ldr r1,=0x1be4
    adds r0,r0,r1
    movs r1,#\slot
.endm
.macro party_selected
    ldr r0,=0x03002818
    ldr r0,[r0]
    ldr r1,=0xbf9
    adds r1,r0,r1
    ldrb r1,[r1]
    ldr r2,=0x1d0c
    adds r0,r0,r2
    ldr r0,[r0]
.endm

begin_iter ffta_party_list_init
    party_selected
    movs r2,#0
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    movs r6,r0
    b 2f
1:  ldrb r6,[r4]
    ldrb r5,[r5]
    cmp r6,r5
    bgt 3f
2:  lsls r0,r6,#3
    adds r5,r0,r1
    tail 0x0807b99d
3:  tail 0x0807ba0d
.ltorg

begin_iter ffta_party_list_next
    party_selected
    movs r2,r6
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    cmp r0,#255
    bhs 3f
    subs r0,r0,r6
    adds r6,r6,r0
    lsls r0,r0,#3
    adds r5,r5,r0
    tail 0x0807b9a1
1:  adds r5,#8
    adds r6,#1
    ldr r0,=0x201
    add r0,sp
    ldrb r0,[r0]
    cmp r6,r0
    ble 2f
3:  tail 0x0807ba0d
2:  tail 0x0807b9a1
.ltorg

begin_iter ffta_primary_init
    party_preview 1
    movs r2,#0
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    movs r6,r0
    b 2f
1:  ldrb r6,[r4]
    ldrb r5,[r5]
    cmp r6,r5
    bgt 3f
2:  mov r3,r9
    tail 0x0807c345
3:  tail 0x0807c6c3
.ltorg

begin_iter ffta_primary_next
    party_preview 1
    movs r2,r6
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    cmp r0,#255
    bhs 3f
    subs r0,r0,r6
    adds r6,r6,r0
    lsls r0,r0,#3
    adds r5,r5,r0
    tail 0x0807c35d
1:  adds r5,#8
    adds r6,#1
    ldr r0,=0x201
    add r0,sp
    ldrb r0,[r0]
    cmp r6,r0
    ble 2f
3:  tail 0x0807c6c3
2:  tail 0x0807c35d
.ltorg

begin_iter ffta_secondary_init
    party_preview 2
    movs r2,#0
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    movs r6,r0
    b 2f
1:  ldrb r6,[r4]
    ldrb r5,[r5]
    cmp r6,r5
    bgt 3f
2:  movs r2,#0
    mov r9,r2
    tail 0x0807c483
3:  tail 0x0807c549
.ltorg

begin_iter ffta_secondary_next
    party_preview 2
    movs r2,r6
    call_iter ffta_command_successor
    cmp r0,#0
    beq 1f
    low_result
    cmp r0,#255
    bhs 3f
    subs r0,r0,r6
    adds r6,r6,r0
    lsls r0,r0,#3
    adds r5,r5,r0
    tail 0x0807c48f
1:  adds r5,#8
    adds r6,#1
    ldr r0,=0x201
    add r0,sp
    ldrb r0,[r0]
    cmp r6,r0
    ble 2f
3:  tail 0x0807c549
2:  tail 0x0807c48f
.ltorg
