.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.include "build/expansion/ability-ids.inc"
.macro tail address
    push {r0}
    ldr r0,=\address
    mov lr,r0
    pop {r0}
    bx lr
.endm
.align 2
.global ffta_physical_final_entry
.thumb_func
ffta_physical_final_entry:
    pop {r3}
    push {r0-r7,lr}
    movs r0,r5
    mov r1,r10
    mov r2,r8
    ldr r3,[sp,#60] @ original formula SP+18, evaluated defender
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_physical_final
    mov sp,r4
    str r0,[sp]
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    adds r5,r0,#0
    ldr r0,=-999
    cmp r5,r0
    bge 1f
    adds r5,r0,#0
1:  ldr r0,=999
    cmp r5,r0
    ble 2f
    adds r5,r0,#0
2:  tail 0x081300f3
.ltorg

.align 2
.global ffta_physical_eligibility_entry
.thumb_func
ffta_physical_eligibility_entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_physical_eligibility
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1

@ Descriptor callback ABI: native dispatchers enter with either stack residue.
.align 2
.global ffta_physical_magnitude_entry
.thumb_func
ffta_physical_magnitude_entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_physical_magnitude
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1

@ Native weapon drain has no action argument. Exclude enabled physical arts at
@ audited ordinary-action callers, whose frames expose the evaluated action.
@ Every other caller and original action replays the original entry exactly.
.align 2
.global ffta_weapon_drain_entry
.thumb_func
ffta_weapon_drain_entry:
    pop {r3}
    push {r0-r2}
    mov r1,lr
    ldr r0,=0x081300c1
    cmp r1,r0
    bne 3f
    mov r1,r10
    b 4f
3:  ldr r0,=0x080a30af
    cmp r1,r0
    bne 5f
    mov r1,r9
    ldrh r1,[r1,#16]
4:  ldr r0,=FFTA_SLD_AX_A1
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_SLD_AX_A2
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_SLD_AX_A3
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_SLD_AX_A4
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_GLD_AX_A1
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_GLD_AX_A2
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_DRK_A2
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_DRK_A3
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_GLD_AX_A4
    cmp r1,r0
    beq 8f
    ldr r0,=FFTA_GLD_AX_A3
    cmp r1,r0
    bne 5f
8:  pop {r0-r2}
    movs r0,#0
    bx lr
5:  pop {r0-r2}
    push {lr}
    lsls r0,r0,#16
    lsrs r0,r0,#16
    cmp r0,#0
    beq 6f
    tail 0x08130665
6:  tail 0x0813067f
.ltorg

@ Native effect3E runs again in the ordinary application postprocessor.
@ Returning here excludes all three observed callsites for enabled arts only.
.align 2
.global ffta_weapon_effect_entry
.thumb_func
ffta_weapon_effect_entry:
    pop {r3}
    push {r0}
    lsls r0,r1,#16
    lsrs r0,r0,#16
    push {r2}
    ldr r2,=FFTA_SLD_AX_A1
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_SLD_AX_A2
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_SLD_AX_A3
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_SLD_AX_A4
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_GLD_AX_A1
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_GLD_AX_A2
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_DRK_A2
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_DRK_A3
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_GLD_AX_A4
    cmp r0,r2
    beq 9f
    ldr r2,=FFTA_GLD_AX_A3
    cmp r0,r2
9:
    pop {r2}
    pop {r0}
    bne 7f
    bx lr
7:  push {r4,r5,lr}
    adds r4,r2,#0
    lsls r0,r0,#16
    lsrs r0,r0,#16
    adds r5,r0,#0
    lsls r1,r1,#16
    tail 0x08130695
.ltorg
