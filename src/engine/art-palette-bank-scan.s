.syntax unified
.cpu arm7tdmi
.arm
.text
.align 2
.global ffta_art_bank_span_fast
.type ffta_art_bank_span_fast,%function
@ Validate every cached byte before reuse; no persistent executable RAM.
@ r0 descriptor: source, words per row, row count, stride, optional cache.
ffta_art_bank_span_fast:
    stmdb sp!,{r4-r8,lr}
    mov r4,r0
    @ Native resident code through 6d68, 512 interrupt bytes, 512 code
    @ bytes, and 40 leaf stack bytes must all fit below SP.
.ifdef FFTA_ART_BURST_SCAN
    @ Burst leaf retains stride in eight extra stack bytes (48 total).
    ldr r8,=0x03007198
.else
    ldr r8,=0x03007190
.endif
    cmp sp,r8
    blo 3f
    ldr r8,=0x03008000
    cmp sp,r8
    bhi 3f
    sub sp,sp,#512
    mov r0,sp
    ldr r1,=ffta_art_bank_span
.ifdef FFTA_ART_BLOCK_SCAN
    @ Same512-byte scoped copy, without per-block loop branches.
    .rept 32
    ldmia r1!,{r3,r8,ip,lr}
    stmia r0!,{r3,r8,ip,lr}
    .endr
.else
    mov r2,#32
1:
    ldmia r1!,{r3,r8,ip,lr}
    stmia r0!,{r3,r8,ip,lr}
    subs r2,r2,#1
    bne 1b
.endif
    mov r8,sp
    mov r0,r4
    adr lr,2f
    bx r8
2:
    add sp,sp,#512
    b 4f
3:
    mov r0,r4
    bl ffta_art_bank_span
4:
    ldmia sp!,{r4-r8,lr}
    bx lr
.size ffta_art_bank_span_fast,.-ffta_art_bank_span_fast
.ltorg
.align 2
.global ffta_art_bank_span
.type ffta_art_bank_span,%function
ffta_art_bank_span:
    stmdb sp!,{r4-r11,lr}
.ifdef FFTA_ART_BURST_SCAN
    sub sp,sp,#12
.else
    sub sp,sp,#4
.endif
    ldmia r0,{r4-r7}
.ifdef FFTA_ART_BURST_SCAN
    str r7,[sp,#4]
.endif
    ldr r9,[r0,#16]
    mov r5,r5,lsr #4
    mov r8,#0
    mov r10,#0
    str r4,[sp]
    cmp r5,#0
    cmpne r6,#0
    beq 9f
1:
    mov r11,r5
2:
    cmp r9,#0
    cmpne r10,#32
    bhs 4f
    beq 4f
    ldr r0,[r9,#2120]
    mov r1,#1
    tst r0,r1,lsl r10
    beq 4f
    mov r0,r4
    add r1,r9,r10,lsl #6
    mov r2,#16
3:
.ifdef FFTA_ART_BURST_SCAN
    @ Two source/cache words per burst; still branch on each word mismatch.
    .rept 2
    ldmia r0!,{r3,ip}
    ldmia r1!,{r7,lr}
    cmp r3,r7
    bne 4f
    cmp ip,lr
    bne 4f
    .endr
    subs r2,r2,#4
.else
.ifdef FFTA_ART_BLOCK_SCAN
    @ Compare all64 current tile bytes. Any mismatch still rescans the
    @ original tile start; only the comparison scratch pointers advance.
    .rept 4
    ldr r3,[r0],#4
    ldr ip,[r1],#4
    cmp r3,ip
    bne 4f
    .endr
    subs r2,r2,#4
.else
    ldr r3,[r0],#4
    ldr ip,[r1],#4
    cmp r3,ip
    bne 4f
    subs r2,r2,#1
.endif
.endif
    bne 3b
    add r1,r9,#2048
    add r1,r1,r10,lsl #1
    ldrh r0,[r1]
    orr r8,r8,r0
    add r4,r4,#64
    b 8f
4:
    mov r1,#16
    mov r2,#1
    mov r3,#0
5:
    ldr ip,[r4],#4
    cmp ip,#0
    beq 6f
    .rept 4
    ands lr,ip,#255
    movne lr,lr,lsr #4
    orrne r3,r3,r2,lsl lr
    mov ip,ip,lsr #8
    .endr
6:
    subs r1,r1,#1
    bne 5b
    orr r8,r8,r3
    cmp r9,#0
    cmpne r10,#32
    bhs 8f
    beq 8f
    add r1,r9,#2048
    add r1,r1,r10,lsl #1
    strh r3,[r1]
    ldr r0,[r9,#2120]
    orr r0,r0,r2,lsl r10
    str r0,[r9,#2120]
    sub r0,r4,#64
    add r1,r9,r10,lsl #6
.ifdef FFTA_ART_BURST_SCAN
    mov lr,#4
.else
    mov r3,#16
.endif
7:
.ifdef FFTA_ART_BURST_SCAN
    ldmia r0!,{r2,r3,r7,ip}
    stmia r1!,{r2,r3,r7,ip}
    subs lr,lr,#1
.else
.ifdef FFTA_ART_BLOCK_SCAN
    @ Copy four exact words per loop using only caller-scratch registers.
    .rept 2
    ldmia r0!,{r2,ip}
    stmia r1!,{r2,ip}
    .endr
    subs r3,r3,#4
.else
    ldr r2,[r0],#4
    str r2,[r1],#4
    subs r3,r3,#1
.endif
.endif
    bne 7b
8:
    add r10,r10,#1
    subs r11,r11,#1
    bne 2b
    ldr r4,[sp]
.ifdef FFTA_ART_BURST_SCAN
    ldr r7,[sp,#4]
.endif
    add r4,r4,r7
    str r4,[sp]
    subs r6,r6,#1
    bne 1b
9:
    mov r0,r8
.ifdef FFTA_ART_BURST_SCAN
    add sp,sp,#12
.else
    add sp,sp,#4
.endif
    ldmia sp!,{r4-r11,lr}
    bx lr
.org ffta_art_bank_span+512
.global ffta_art_bank_span_end
ffta_art_bank_span_end:
.size ffta_art_bank_span,.-ffta_art_bank_span
