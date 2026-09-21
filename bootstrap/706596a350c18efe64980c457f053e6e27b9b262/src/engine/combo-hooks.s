.syntax unified
.cpu arm7tdmi
.thumb
.section .text

.macro combo_entry name, target
.align 2
.global \name
.thumb_func
\name:
    pop {r3}
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl \target
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
.endm

.macro combo_tail address
    push {r0}
    ldr r0,=\address
    mov lr,r0
    pop {r0}
    bx lr
.endm

combo_entry ffta_combo_assigned_entry, ffta_combo_assigned
combo_entry ffta_combo_chance_entry, ffta_combo_chance
combo_entry ffta_combo_range_entry, ffta_combo_range
combo_entry ffta_combo_power_entry, ffta_combo_power

.align 2
.global ffta_original_combo_chance
.thumb_func
ffta_original_combo_chance:
    push {r4,r5,r6,lr}
    adds r5,r0,#0
    lsls r2,r2,#24
    lsrs r6,r2,#24
    ldr r3,=0x080c8299
    mov lr,r3
    .short 0xf800
    combo_tail 0x0812e13d
.ltorg

.align 2
.global ffta_original_combo_range
.thumb_func
ffta_original_combo_range:
    push {lr}
    ldrb r2,[r0,#6]
    adds r0,#0x3c
    ldrb r1,[r0]
    adds r0,r2,#0
    ldr r3,=0x080cd481
    mov lr,r3
    .short 0xf800
    combo_tail 0x0812e3bf
.ltorg

.align 2
.global ffta_original_combo_power
.thumb_func
ffta_original_combo_power:
    push {lr}
    ldrb r2,[r0,#6]
    adds r0,#0x3c
    ldrb r1,[r0]
    adds r0,r2,#0
    ldr r3,=0x080cd481
    mov lr,r3
    .short 0xf800
    combo_tail 0x081304ef
.ltorg
