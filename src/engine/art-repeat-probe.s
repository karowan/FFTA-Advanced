.syntax unified
.cpu arm7tdmi
.arm
.text
.align 2
.global ffta_art_repeat_probe
.type ffta_art_repeat_probe,%function
ffta_art_repeat_probe:
    stmdb sp!,{r4-r8,lr}
    mov r4,r0
    @640-byte image,40-byte leaf stack,512 interrupt bytes above03006D68.
    ldr r8,=0x03007210
    cmp sp,r8
    blo 3f
    ldr r8,=0x03008000
    cmp sp,r8
    bhi 3f
    sub sp,sp,#640
    mov r0,sp
    ldr r1,=ffta_art_repeat_probe_leaf
    mov r2,#40
1:
    ldmia r1!,{r3,r8,ip,lr}
    stmia r0!,{r3,r8,ip,lr}
    subs r2,r2,#1
    bne 1b
    mov r8,sp
    mov r0,r4
    adr lr,2f
    bx r8
2:
    add sp,sp,#640
    b 4f
3:
    mov r0,r4
    bl ffta_art_repeat_probe_leaf
4:
    ldmia sp!,{r4-r8,lr}
    bx lr
.size ffta_art_repeat_probe,.-ffta_art_repeat_probe
.ltorg
.align 2
.global ffta_art_repeat_probe_leaf
.type ffta_art_repeat_probe_leaf,%function
ffta_art_repeat_probe_leaf:
    stmdb sp!,{r4-r11,lr}
    sub sp,sp,#4
    str r0,[sp]
    ldr r4,[r0,#28]
    cmp r4,#2
    beq 4f
    ldr r9,[r0,#32]
    ldmia r0,{r0-r2}
    mov r3,#128
    mov r11,#0
1:
    ldr r5,[r0],#8
    ldrh r6,[r0,#-4]
    ldrb r10,[r9],#1
    and r7,r5,#0x300
    cmp r7,#0x200
    beq 11f
    and r7,r5,#0xc000
    cmp r7,#0xc000
    beq 8f
    cmp r10,#255
    beq 12f
    cmp r10,#10
    bhs 8f
    tst r5,#0xe100
    bne 8f
    mov r7,r5,lsr #30
    cmp r7,#2
    bne 8f
    mov r6,r6,lsr #12
    orr r6,r6,r10,lsl #4
    orr r6,r6,#0x4000
    mov r5,#0
    b 13f
11:
    mov r5,#0
    mov r6,#0x8000
    b 13f
12:
    tst r5,#0x2000
    bne 14f
    mov r6,r6,lsr #12
    orr r6,r6,#0x2000
    mov r5,#0
    b 13f
14:
    ldr r7,=0xf1fff3ff
    and r5,r5,r7
    bic r6,r6,#0xfc00
    bic r6,r6,#1
13:
    cmp r4,#1
    beq 15f
    ldr r7,[r1],#4
    ldrh r8,[r2],#2
    cmp r5,r7
    cmpeq r6,r8
    bne 8f
    b 16f
15:
    @ Preserve the tile footprint only when every8bpp geometry key is exact.
    ldrh r8,[r2]
    cmp r8,#0x2000
    cmphs r6,#0x2000
    bhs 17f
    ldr r7,[r1]
    cmp r5,r7
    cmpeq r6,r8
    movne r11,#1
17:
    str r5,[r1],#4
    strh r6,[r2],#2
16:
    subs r3,r3,#1
    bne 1b
    cmp r4,#1
    addeq r0,r11,#1
    beq 9f
4:
    ldr r4,[sp]
    ldr ip,[r4,#12]
    ldr r1,[r4,#16]
    ldr r10,[r4,#20]
    ldr r11,[r4,#24]
    cmp r11,#32
    bhi 8f
    cmp r11,#0
    beq 7f
5:
    ldrh r0,[r10],#2
    cmp r0,#512
    bhs 8f
    add r0,ip,r0,lsl #6
    .rept 4
    ldmia r0!,{r2-r5}
    ldmia r1!,{r6-r9}
    cmp r2,r6
    cmpeq r3,r7
    cmpeq r4,r8
    cmpeq r5,r9
    bne 8f
    .endr
    subs r11,r11,#1
    bne 5b
7:
    mov r0,#1
    b 9f
8:
    mov r0,#0
9:
    add sp,sp,#4
    ldmia sp!,{r4-r11,lr}
    bx lr
.ltorg
.org ffta_art_repeat_probe_leaf+640,0
.size ffta_art_repeat_probe_leaf,.-ffta_art_repeat_probe_leaf
