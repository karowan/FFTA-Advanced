.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2

/* 74C34 consumes the two byte-sized stack name IDs used by the native
 * Pick Abilities renderer. Only the ten appended commands need a full
 * descriptor name ID. Keep original commands' exact byte behavior.
 * Entry: r0=native byte name ID, r4=0/1 command slot, r5=other-text bank,
 * r7=unit. r3 is dead here and is set to zero at74CC2 before the next call.
 * Exit: native r0=pointer-table slot, r2=text pointer; other live registers
 * and SP unchanged. No C call, global scratch or extra persistent state. */
.global ffta_party_command_label_entry
.type ffta_party_command_label_entry,%function
.thumb_func
ffta_party_command_label_entry:
    push {r1}
    movs r2,r7
    adds r2,#0x35
    adds r2,r2,r4
    ldrb r2,[r2]
    cmp r2,#116
    blo 1f
    cmp r2,#125
    bhi 1f
    lsls r2,r2,#2
    ldr r1,=0x08074c0c
    ldr r1,[r1]
    adds r2,r2,r1
    ldrh r0,[r2]
1:  lsls r0,r0,#2
    adds r0,r0,r5
    ldr r2,[r0]
    pop {r1}
    ldr r3,=0x08074cbd
    bx r3
.size ffta_party_command_label_entry,.-ffta_party_command_label_entry
.ltorg
