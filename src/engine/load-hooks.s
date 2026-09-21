.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2

/* These sites run only after a successful gameplay load has decoded staging,
 * before CpuSet commits it to live state. Slot previews do not migrate. A
 * rejected format therefore cannot replace the currently loaded game. r3 is
 * dead here; the remaining registers reproduce the displaced setup bytes. */
.global ffta_load_normal
.thumb_func
ffta_load_normal:
    push {r0-r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    movs r0,r5
    bl ffta_migrate_inventory
    cmp r0,#0
    blt normal_failed
    mov sp,r4
    pop {r0-r4}
    pop {r3}
    mov lr,r3
    ldr r4,=0x02000000
    ldr r2,=0x1e54
    movs r0,r5
    movs r1,r4
    ldr r3,=0x0813aa51
    bx r3
normal_failed:
    mov sp,r4
    pop {r0-r4}
    pop {r3}
    mov lr,r3
    ldr r3,=0x0813aa31
    bx r3

.align 2
.global ffta_load_suspend
.thumb_func
ffta_load_suspend:
    push {r0-r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    movs r0,r5
    bl ffta_migrate_inventory
    cmp r0,#0
    blt suspend_failed
    mov sp,r4
    pop {r0-r4}
    pop {r3}
    mov lr,r3
    ldr r4,=0x02000000
    ldr r2,=0x1e54
    movs r0,r5
    movs r1,r4
    ldr r3,=0x0813aae1
    bx r3
suspend_failed:
    mov sp,r4
    pop {r0-r4}
    pop {r3}
    mov lr,r3
    ldr r3,=0x0813aacb
    bx r3
.ltorg

/* Ability-enabled probe: migrate and publish expanded counts in staging only
 * after a successful native load. Rejected formats never touch live state. */
.macro ability_load name, continuation, failure
.align 2
.global \name
.thumb_func
\name:
    push {r0-r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    movs r0,r5
    bl ffta_load_migrate_abilities
    cmp r0,#0
    blt 1f
    mov sp,r4
    pop {r0-r4}
    pop {r3}
    mov lr,r3
    ldr r4,=0x02000000
    ldr r2,=0x1e54
    movs r0,r5
    movs r1,r4
    ldr r3,=\continuation
    bx r3
1:
    mov sp,r4
    pop {r0-r4}
    pop {r3}
    mov lr,r3
    ldr r3,=\failure
    bx r3
.ltorg
.endm
ability_load ffta_load_abilities_normal,0x0813aa51,0x0813aa31
ability_load ffta_load_abilities_suspend,0x0813aae1,0x0813aacb
