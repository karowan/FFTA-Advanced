ENTRY(ffta_storage_format)
SECTIONS
{
    . = 0x09100000;
    .text : { *(.text*) *(.rodata*) }
    .data : { *(.data*) }
    .bss : { *(.bss*) *(COMMON) }
    /DISCARD/ : { *(.comment) *(.ARM.attributes) }
}
ASSERT(SIZEOF(.data) == 0, "ROM module cannot contain mutable data")
ASSERT(SIZEOF(.bss) == 0, "ROM module cannot contain implicit BSS")
