.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_job_save_entry
.thumb_func
ffta_job_save_entry:
 pop {r3}
 push {r4,lr}
 mov r4,sp
 mov r3,sp
 lsrs r3,r3,#3
 lsls r3,r3,#3
 mov sp,r3
 bl ffta_job_save
 mov sp,r4
 pop {r4}
 pop {r3}
 bx r3
.align 2
.global ffta_job_original_save
.thumb_func
ffta_job_original_save:
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 sub sp,#0x34
 ldr r3,=0x0813b2b5
 bx r3
.ltorg
