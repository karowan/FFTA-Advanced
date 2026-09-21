.syntax unified
.cpu arm7tdmi
.arm
.text
.align 2
.global ffta_art_oam_demands
.type ffta_art_oam_demands,%function
@ r0 frame, r1 scratch {occupied,requested,count,byte indices[128]}, r2 limit.
@ No persistent executable RAM. Keep512 interrupt bytes below the320-byte leaf
@ and its40-byte stack, above native resident code ending03006D68.
ffta_art_oam_demands:
    stmdb sp!,{r4-r8,lr}
    mov r4,r0
    mov r5,r1
    mov r6,r2
    ldr r8,=0x030070d0
    cmp sp,r8
    blo 3f
    ldr r8,=0x03008000
    cmp sp,r8
    bhi 3f
    sub sp,sp,#320
    mov r0,sp
    ldr r1,=ffta_art_oam_demands_leaf
    mov r2,#20
1:
    ldmia r1!,{r3,r8,ip,lr}
    stmia r0!,{r3,r8,ip,lr}
    subs r2,r2,#1
    bne 1b
    mov r8,sp
    mov r0,r4
    mov r1,r5
    mov r2,r6
    adr lr,2f
    bx r8
2:
    add sp,sp,#320
    b 4f
3:
    mov r0,r4
    mov r1,r5
    mov r2,r6
    bl ffta_art_oam_demands_leaf
4:
    ldmia sp!,{r4-r8,lr}
    bx lr
.size ffta_art_oam_demands,.-ffta_art_oam_demands
.ltorg
.align 2
.global ffta_art_oam_demands_leaf
.type ffta_art_oam_demands_leaf,%function
ffta_art_oam_demands_leaf:
    cmp r2,#128
    movhi r0,#0
    bxhi lr
    stmdb sp!,{r4-r11,lr}
    str r2,[sp,#-4]!
    ldr r4,[r0]
    ldr r5,[r0,#8]
    mov r6,r1
    ldr r7,[r0,#28]
    mov r8,#0
    mov r9,#0
    mov r10,#0
    mov r11,#0
    cmp r2,#0
    beq 7f
1:
    ldrh r0,[r4]
    ldrh r3,[r4,#2]
    orr r0,r0,r3,lsl #16
    ldrh r1,[r4,#4]
    add r4,r4,#8
    ldrb r2,[r5],#1
    and r3,r0,#0x300
    cmp r3,#0x200
    beq 6f
    and r3,r0,#0xc000
    cmp r3,#0xc000
    beq 8f
    cmp r2,#255
    beq 4f
    cmp r2,r7
    bhs 8f
    tst r0,#0xe100
    bne 8f
    mov r3,r0,lsr #30
    cmp r3,#2
    bne 8f
    mov r3,#1
    orr r9,r9,r3,lsl r2
    b 6f
4:
    tst r0,#0x2000
    bne 5f
    mov r2,r1,lsr #12
    mov r3,#1
    orr r8,r8,r3,lsl r2
    b 6f
5:
    add r3,r6,#12
    strb r11,[r3,r10]
    add r10,r10,#1
6:
    add r11,r11,#1
    ldr r3,[sp]
    cmp r11,r3
    blo 1b
7:
    stmia r6,{r8-r10}
    mov r0,#1
    b 9f
8:
    mov r0,#0
9:
    add sp,sp,#4
    ldmia sp!,{r4-r11,lr}
    bx lr
.org ffta_art_oam_demands_leaf+320,0
.size ffta_art_oam_demands_leaf,.-ffta_art_oam_demands_leaf
