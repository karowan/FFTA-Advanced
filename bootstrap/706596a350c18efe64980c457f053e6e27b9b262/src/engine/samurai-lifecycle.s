.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro aligned_entry name, function, veneer=0
.align 2
.global \name
.thumb_func
\name:
.if \veneer
    pop {r3}
.endif
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl \function
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
.endm
aligned_entry ffta_centered_equipment_entry,ffta_centered_equipment,1
aligned_entry ffta_centered_equipment_quiet_entry,ffta_centered_equipment_quiet,1
aligned_entry ffta_centered_dispel_entry,ffta_centered_dispel
.macro original_equipment name, destination
.align 2
.global \name
.thumb_func
\name:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    sub sp,#8
    ldr r3,=\destination
    bx r3
.ltorg
.endm
original_equipment ffta_original_centered_equipment,0x080caf85
original_equipment ffta_original_centered_equipment_quiet,0x080cb0e5
