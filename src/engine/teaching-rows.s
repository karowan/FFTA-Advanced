.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_teaching_row_group
.thumb_func
ffta_teaching_row_group:
    @ Replaces C8DC0..C8DE3 after the native lesson lookup (r3). Live:
    @ r4=entry*2, r5=&job, r6=set+2, r7=rows, r8=entry, sb=set, sl=row.
    mov r0,sl
    cmp r0,#3
    bhs 9f
    ldrh r0,[r7]
    adds r0,#1
    strh r0,[r7]
    mov r0,sl
    lsls r2,r0,#3
    adds r1,r7,r2
    ldrh r0,[r3]
    strh r0,[r1,#4]
    push {r2}
    mov r0,sb
    mov r1,r8
    bl ffta_teaching_group_size
    pop {r3}
    @ Native handlers: one entry, two entries or three entries per row.
    cmp r0,#2
    beq 2f
    cmp r0,#3
    beq 3f
    ldr r0,=0x080c8e8d
    bx r0
2:
    ldr r0,=0x080c8e35
    bx r0
3:
    ldr r0,=0x080c8e61
    bx r0
9:
    @ The native buffers hold three rows; ignore any later entries.
    ldr r0,=0x080c8ead
    bx r0
.ltorg

@ Each compare hook replaces "row job == entry job" and the match preamble
@ before the native race call. Rows are {name,count,jobs[4]}; entry is
@ {job,lesson}. The scratch register is dead on both continuations.
.macro row_match scratch, matched, next
    bl ffta_teaching_row_match
    pop {r1-r3}
    cmp r0,#0
    beq 1f
    ldrb r1,[r1]
    adds r0,r1,#0
    movs r2,#1
    ldr \scratch,=\matched
    bx \scratch
1:
    ldr \scratch,=\next
    bx \scratch
.ltorg
.endm

.align 2
.global ffta_party_info_row_match
.thumb_func
ffta_party_info_row_match:
    @ 808C842: r0=row-4, r1=entry, r3 free; match resumes at 808C850.
    push {r1-r3}
    adds r0,r0,#4
    row_match r3,0x0808c851,0x0808c909

.align 2
.global ffta_shop_info_row_match
.thumb_func
ffta_shop_info_row_match:
    @ 806FC8C: r0=row-4, r1=entry, r3 free; match resumes at 806FC9A.
    push {r1-r3}
    adds r0,r0,#4
    row_match r3,0x0806fc9b,0x0806fcf5

.align 2
.global ffta_shop_row_match
.thumb_func
ffta_shop_row_match:
    @ 8067236: r3=&row job, r1=entry, r6 free; match resumes at 8067244.
    push {r1-r3}
    subs r0,r3,#4
    row_match r6,0x08067245,0x080672bd

.align 2
.global ffta_party_info_type
.thumb_func
ffta_party_info_type:
    @ 808C8A8 draws the type icon after every row; keep only row zero's.
    @ r7=matched lesson, sb=row*8. Resumes at the native loop end 808C914.
    mov r0,sb
    cmp r0,#0
    bne 1f
    ldrb r0,[r7,#6]
    ldr r1,=0x0808c53d
    bl 2f
1:
    ldr r0,=0x0808c915
    bx r0
2:
    bx r1
.ltorg

.align 2
.global ffta_shop_info_type
.thumb_func
ffta_shop_info_type:
    @ 806FD10 uses the last matched lesson ([sp+3C]); rows are at sp+0C and
    @ r6 is the item's set. Leave r3=lesson, r0=type as the native code does.
    add r0,sp,#0xc
    push {r1,r2}
    adds r1,r6,#0
    ldr r2,[sp,#0x44]
    bl ffta_teaching_first_lesson
    adds r3,r0,#0
    ldrb r0,[r3,#6]
    pop {r1,r2}
    @ Replaced "cmp r0,#2; beq 806FD50". ARMv4T pop {pc} stays in Thumb.
    sub sp,#4
    push {r1}
    ldr r1,=0x0806fd19
    cmp r0,#2
    bne 3f
    ldr r1,=0x0806fd51
3:
    str r1,[sp,#4]
    pop {r1}
    pop {pc}
.ltorg
