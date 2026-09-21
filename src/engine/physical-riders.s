.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro rider_tail address
    push {r0}
    ldr r0,=\address
    mov lr,r0
    pop {r0}
    bx lr
.endm

@ Installer contract: raw12FEA8..12FEB0 is an eight-byte r0-scratch veneer.
@ Incoming r1=capped native WDef, r4=attack, r10=action. r0 is overwritten by
@ the displaced setup; every other live register and the original frame stays.
.align 2
.global ffta_physical_defense_entry
.thumb_func
ffta_physical_defense_entry:
    push {r0-r7,lr}
    movs r6,#0
    bvc 1f
    movs r6,#1
1:
    movs r0,r1
    mov r1,r10
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_physical_effective_defense
    mov sp,r4
    str r0,[sp,#4]
    @ The displaced shifts preserve V; C does not. Restore that one incoming
    @ flag before replaying shifts, which recompute native N/Z/C themselves.
    cmp r6,#0
    beq 2f
    movs r0,#1
    lsls r0,r0,#31
    subs r0,#1
2:
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    lsls r0,r4,#16
    asrs r0,r0,#16
    lsls r1,r1,#16
    asrs r1,r1,#16
    rider_tail 0x0812feb1
.ltorg

@ Installer contract: rawA3072..A307C is a ten-byte r3-preserving veneer.
@ Replays native magnitude BL, r5 assignment and stage comparison/branch.
.align 2
.global ffta_physical_success_entry
.thumb_func
ffta_physical_success_entry:
    pop {r3}
    push {r0-r7,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    ldr r0,=0x0200f3f0
    bl ffta_physical_before_hit
    mov sp,r4
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    ldr r0,=0x08131b21
    bl .Lrider_call_r0
    @ Native131B20 returns by POP r1 / BX r1, exposing its return address.
    @ Recreate the displaced native BL's r1 instead of leaking our trampoline.
    ldr r1,=0x080a3077
    adds r5,r0,#0
    cmp r4,#1
    bgt 1f
    rider_tail 0x080a307d
1:  rider_tail 0x080a3087
.Lrider_call_r0:
    bx r0
.ltorg

@ Native law simulation after eligibility, recipient and stage selection.
@ Installer raw13434C..134354: eight-byte r0-scratch veneer. r6/r7 encode
@ queried status; r8 is removal mode. Replays magnitude/cmp/branch.
.align 2
.global ffta_physical_law_entry
.thumb_func
ffta_physical_law_entry:
    push {r0-r7,lr}
    ldr r0,=0x0200f3f0
    mov r1,r8
    movs r2,r6
    movs r3,r7
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_physical_law_hit
    mov sp,r4
    str r0,[sp]
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    push {r0}
    ldr r0,=0x08131b21
    bl .Llaw_call_r0
    pop {r1}
    cmp r1,#0
    bne 1f
    ldr r1,=0x08134351
    cmp r0,#0
    bne 2f
    rider_tail 0x08134355
1:  rider_tail 0x08134383
2:  rider_tail 0x081343b7
.Llaw_call_r0:
    bx r0
.ltorg

@ C callable wrappers permit native callers with either stack residue.
.align 2
.global ffta_physical_rider_reference_entry
.thumb_func
ffta_physical_rider_reference_entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_physical_rider_reference
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1

.align 2
.global ffta_physical_before_hit_entry
.thumb_func
ffta_physical_before_hit_entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_physical_before_hit
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
