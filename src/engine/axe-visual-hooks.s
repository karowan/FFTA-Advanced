.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro tail address
    push {r0}
    ldr r0,=\address
    mov lr,r0
    pop {r0}
    bx lr
.endm
.macro axe_case name,source,table,continuation,fallback,add_table=1
.align 2
.global \name
.thumb_func
\name:
    pop {r3}
.ifc \source,r5
    movs r0,r5
    @ Mystic Knight adds sabers to Viera, whose native sprite has no saber
    @ swing. Use its supported rapier pose, preserving the real item/type
    @ for damage, teaching, laws, sounds and every other native consumer.
    cmp r0,#3
    bne 6f
    ldr r1,[r6]
    cmp r1,#0
    beq 6f
    ldrb r1,[r1,#6]
    cmp r1,#4
    bne 6f
    ldr r1,[r6]
    ldrb r1,[r1,#5]
    cmp r1,#125
    bne 6f
    movs r0,#8
    b 3f
6:
    @ Newly permitted knives use supported donor poses: Nu Mou Chemist's
    @ staff swing and Viera Dancer's rapier thrust. Blade poses are missing.
    @ r6 is the evaluated actor wrapper, whose first word is its unit.
    cmp r0,#7
    bne 3f
    ldr r0,[r6]
    cmp r0,#0
    beq 4f
    ldrb r1,[r0,#6]
    cmp r1,#3
    bne 5f
    ldrb r1,[r0,#5]
    cmp r1,#120
    bne 4f
    movs r0,#12
    b 3f
5:  cmp r1,#4
    bne 4f
    ldrb r1,[r0,#5]
    cmp r1,#124
    bne 4f
    movs r0,#8
    b 3f
4:  movs r0,#7
3:
.endif
    cmp r0,#31
    bne 1f
    movs r0,#5 @ Barong's existing heavy-blade visual family
1:  subs r0,#1
    cmp r0,#18
    bhi 2f
    lsls r0,r0,#2
    ldr r1,=\table
.if \add_table
    adds r0,r0,r1
.endif
    tail \continuation
2:  tail \fallback
.ltorg
.endm
@ Only the visual switch input changes; the true type/item and all native
@ case bodies retain their original data and behavior.
axe_case ffta_axe_actor_visual,r5,0x080986f0,0x080986e7,0x08098759
axe_case ffta_axe_hit_sound,r0,0x080a58b4,0x080a58ad,0x080a597d
axe_case ffta_axe_swing_sound,r0,0x080a7ef0,0x080a7ee9,0x080a7fb9
axe_case ffta_axe_effect_visual,r0,0x080b3c7c,0x080b3c71,0x080b3d89,0
