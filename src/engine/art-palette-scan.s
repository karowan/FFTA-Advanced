.syntax unified
.cpu arm7tdmi
.arm
.text
.align 2
.global ffta_art_copy_words
.type ffta_art_copy_words,%function
@ Aligned buffers, nonzero word count divisible by8. Each palette bank is
@ exactly8 words. The same copy serves RAM and native32-bit palette writes.
ffta_art_copy_words:
    stmdb sp!,{r4-r10,lr}
1:
    ldmia r1!,{r3-r10}
    stmia r0!,{r3-r10}
    subs r2,r2,#8
    bne 1b
    ldmia sp!,{r4-r10,lr}
    bx lr
.size ffta_art_copy_words,.-ffta_art_copy_words
.align 2
.global ffta_art_span_has_bank_fast
.type ffta_art_span_has_bank_fast,%function
@ A scoped, bounded IWRAM copy. No persistent executable reservation, no cache.
@ Resident native code ends at03006d68; leave its entire range untouched.
@ The copied leaf uses28 stack bytes below its160-byte image. Keep a further
@ 512 bytes below that for nested native interrupt work; deep stacks fall back.
ffta_art_span_has_bank_fast:
    stmdb sp!,{r4-r8,lr}
    mov r4,r0
    mov r5,r1
    mov r6,r2
    ldr r7,=0x03007024 @ 6d68 +512 +160 +28, after wrapper register push
    cmp sp,r7
    blo 6f
    ldr r7,=0x03008000
    cmp sp,r7
    bhi 6f
    sub sp,sp,#160
    mov r0,sp
    ldr r1,=ffta_art_span_has_bank
    mov r2,#10
5:
    ldmia r1!,{r3,r7,r8,ip}
    stmia r0!,{r3,r7,r8,ip}
    subs r2,r2,#1
    bne 5b
    mov r7,sp
    mov r0,r4
    mov r1,r5
    mov r2,r6
    adr lr,7f
    bx r7
7:
    add sp,sp,#160
    b 8f
6:
    bl ffta_art_span_has_bank
8:
    ldmia sp!,{r4-r8,lr}
    bx lr
.size ffta_art_span_has_bank_fast,.-ffta_art_span_has_bank_fast
.ltorg
.ifdef FFTA_ART_RECT_CONFLICT
.align 2
.global ffta_art_rect_has_bank_fast
.type ffta_art_rect_has_bank_fast,%function
@ Same exact160-byte leaf, copied once for a bounded rectangle's row sequence.
@ Descriptor: first row, words per row, row count, byte stride, bank pattern.
@ Wrapper uses32 bytes. Post-push cutoff preserves the original leaf's28-byte
@ stack plus512 interrupt bytes and resident native code through03006d68.
ffta_art_rect_has_bank_fast:
    stmdb sp!,{r4-r10,lr}
    ldr r4,[r0]
    ldr r6,[r0,#4]
    ldr r7,[r0,#8]
    ldr r8,[r0,#12]
    ldr r5,[r0,#16]
    mov r10,#0
    ldr r9,=ffta_art_span_has_bank
    ldr r0,=0x03007024
    cmp sp,r0
    blo 2f
    ldr r0,=0x03008000
    cmp sp,r0
    bhi 2f
    sub sp,sp,#160
    mov r0,sp
    mov r1,r9
    .rept 10
    ldmia r1!,{r2,r3,ip,lr}
    stmia r0!,{r2,r3,ip,lr}
    .endr
    mov r9,sp
    mov r10,#160
2:
    mov r0,r4
    mov r1,r5
    mov r2,r6
    adr lr,3f
    bx r9
3:
    cmp r0,#0
    bne 4f
    subs r7,r7,#1
    add r4,r4,r8
    bne 2b
4:
    add sp,sp,r10
    ldmia sp!,{r4-r10,lr}
    bx lr
.size ffta_art_rect_has_bank_fast,.-ffta_art_rect_has_bank_fast
.ltorg
.endif
.balign 16
.global ffta_art_span_has_bank
.type ffta_art_span_has_bank,%function
@ r0: aligned tile span; r1: repeated nonzero palette-bank high nibble.
@ r2: nonzero word count divisible by16 (one or more whole tiles).
@ Exact any-byte-less-than16 predicate after XOR with the wanted high nibble.
@ Low nibbles need no masking. Combine all four words before the branch.
ffta_art_span_has_bank:
    stmdb sp!,{r4-r9,lr}
    mov r9,r2,lsr #2
    ldr r7,=0x10101010
    ldr r8,=0x80808080
1:
    ldmia r0!,{r2-r5}
    orr ip,r2,r3
    orr ip,ip,r4
    orrs ip,ip,r5
    beq 2f
    mov r6,#0
    .irp pixel,r2,r3,r4,r5
    eor \pixel,\pixel,r1
    sub ip,\pixel,r7
    bic ip,ip,\pixel
    orr r6,r6,ip
    .endr
    tst r6,r8
    bne 3f
2:
    subs r9,r9,#1
    bne 1b
    mov r0,#0
    b 4f
3:
    mov r0,#1
4:
    ldmia sp!,{r4-r9,lr}
    bx lr
.ltorg
@ A backward .org is an assembler error if the leaf outgrows its image.
.org ffta_art_span_has_bank+160
.global ffta_art_span_has_bank_end
ffta_art_span_has_bank_end:
.size ffta_art_span_has_bank,.-ffta_art_span_has_bank
