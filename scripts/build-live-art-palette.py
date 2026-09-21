"""Private Dark Knight palette integration with owned RAM and native hooks.

Uses an existing built-in-imagegen draft; repeated poses are transport assets.
Does not replace any current package, launcher, ROM selection or player save.
"""
import argparse, datetime, hashlib, json, struct, subprocess
from pathlib import Path
from PIL import Image
from native_art import ROOT, TILES, OAM, sha, layout, tile_image, pack_tiles
from art_palette_build import write_pixel_banks

START, END = 0x1f90000, 0x1fd0000
PARENT = ROOT / 'build/art/generated-actions/refined-samurai-current.json'

def build(history_slots=10,all_classes=False,workspace_low_address=False,trace_target=False,provisional_history=False,fast_rotation=False,separate_menu_ram=False,owned_menu_buffer=False,shared_battle_menu_heap=False,compact_us_keyboard=False,compact_battle_status=False,art_overrides=None,publish_current=True,fast_bank_scan=False,dma_tile_cache=False,fast_oam_plan=False,arm_oam_scan=False,repeat_frame=False,scoped_frame=False,native_oam_prefix=False,native_owner_producer=False,fused_compose=False,fused_word_reads=False,compact_leaves=False,unrolled_copy=False,packed_plan=False,block_scan=False,burst_scan=False,fast_confirm=False,joined_rows=False,prepared_preference=False,rect_conflict=False,opposing_palettes=False,native_reference_from_rom=False,palette_groups=None):
    assert history_slots in (10,20)
    assert not all_classes or history_slots==20, 'All classes require the larger history reservation'
    assert not workspace_low_address or all_classes
    assert not trace_target or workspace_low_address
    assert not provisional_history or workspace_low_address
    assert not owned_menu_buffer or (workspace_low_address and not separate_menu_ram)
    assert not shared_battle_menu_heap or (owned_menu_buffer and not trace_target)
    assert not compact_battle_status or shared_battle_menu_heap
    assert not fast_bank_scan or not publish_current, 'Rejected scanner experiment must remain private'
    assert not dma_tile_cache or (not publish_current and not fast_bank_scan), 'Writer-cache experiment must remain private and separate'
    assert not fast_oam_plan or (not publish_current and not dma_tile_cache and (not fast_bank_scan or arm_oam_scan)), 'OAM traversal candidate remains private; paired ARM loops require explicit selection'
    assert not arm_oam_scan or fast_oam_plan, 'ARM scan uses the private full-plan traversal option'
    assert not repeat_frame or (all_classes and provisional_history and not publish_current and not dma_tile_cache), 'Repeated-frame experiment requires exact pixels and private twenty-history layout'
    assert not scoped_frame or (all_classes and not publish_current and not repeat_frame and not dma_tile_cache), 'Scoped frame experiment remains private without repeated-frame reuse'
    assert not native_oam_prefix or (all_classes and not publish_current and not repeat_frame and not dma_tile_cache), 'Native prefix proof is private until accepted'
    assert not opposing_palettes or (all_classes and not publish_current), 'Opposing palette support remains private pending acceptance'
    assert not native_owner_producer or (native_oam_prefix and scoped_frame), 'Native ownership requires authenticated prefix producer and scoped leaves'
    assert not fused_word_reads or fused_compose
    assert not rect_conflict or (prepared_preference and not publish_current), 'Rectangle conflict requires private prepared preference'
    assert not prepared_preference or (fused_compose and not dma_tile_cache and not publish_current), 'Prepared preference requires same-invocation classification'
    assert not joined_rows or (fast_confirm and not dma_tile_cache and not publish_current), 'Joined rows require private exact-byte scanning'
    assert not fast_confirm or (history_slots==20 and provisional_history and not publish_current), 'Fast confirmation requires private twenty-history state'
    assert not burst_scan or block_scan, 'Burst scanner requires the private block scanner'
    assert not block_scan or (fast_bank_scan and not publish_current), 'Block scanner remains private until acceptance'
    assert not packed_plan or (fused_compose and history_slots==20 and not publish_current), 'Packed plan requires private twenty-history fused composition'
    assert not unrolled_copy or (fused_compose and not compact_leaves and not publish_current), 'Unrolled copy remains private until response acceptance'
    assert not compact_leaves or (fused_compose and not fused_word_reads and not publish_current), 'Compact code experiment requires private scalar fused composition'
    assert not fused_compose or (native_owner_producer and arm_oam_scan and fast_bank_scan), 'Fused composition requires the exact native-owner/ARM planner contract'
    ram_base=0x0203d000 if history_slots==10 else 0x0203c000
    ram_limit=0x0203f000
    if separate_menu_ram:
        assert history_slots==20 and workspace_low_address
        # Party item/ability lists already own C000..F000. Lowering the heap
        # alone does not move those fixed native consumers.
        ram_base,ram_limit=0x02039000,0x0203c000
    ram_bytes=ram_limit-ram_base
    parent = json.loads(PARENT.read_text()); original = Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest() == parent['romSha1'] == '0fa7d1707e2d85fb2a8602f061b5eb4479ff3211'
    if native_oam_prefix:assert sha(original[0x12bc:0x14c8])=='9b66e36f26b094d61539c4790834bd83d102e90433cf5b7e443c268cabbf8c64', 'Native OAM prefix producer changed'
    rom = bytearray(original)
    assert rom[START:END] == b'\xff' * (END - START)
    work = ROOT / 'build/art/live-palette/compile' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    work.mkdir(parents=True)
    converted = ROOT / 'build/art/imagegen/human-dark-knight/march-v2-own-palette'
    art = json.loads((converted / 'manifest.json').read_text())
    colors = (converted / 'palette.bin').read_bytes()
    assert sha(colors) == '4803df6e40ba73159e547a5a387eccf7db897170a4934d87e43ef25f21401a53'
    # All source/conversion inputs are authenticated; this does not accept art.
    source = Path(art['source']); assert sha(source.read_bytes()) == art['sourceSha256']
    words = [0] * 160; words[16:32] = struct.unpack('<16H', colors)
    native_words = [0] * 160
    opposing_words = [0] * 160; opposing_inputs=[]
    native_words[16:32] = struct.unpack_from('<16H', original, 0x419d60)
    class_art={117:(converted,art)};art_inputs=[]
    overrides={};override_proof=None
    if art_overrides:
        assert all_classes, 'Art overrides require all-class palette ownership'
        override_path=Path(art_overrides);override_raw=override_path.read_bytes()
        override_spec=json.loads(override_raw);assert override_spec['schema']==1
        for row in override_spec['jobs']:
            job=row['job'];assert type(job) is int and 116<=job<=125 and job not in overrides
            manifest_path=ROOT/row['conversionManifest']
            assert sha(manifest_path.read_bytes())==row['conversionManifestSha256']
            overrides[job]=row
        assert overrides
        override_proof=dict(path=str(override_path),sha256=sha(override_raw),jobs=sorted(overrides))
    if all_classes:
        catalog_path=ROOT/'src/art/imagegen/catalog.json'
        catalog=json.loads(catalog_path.read_text())
        if native_reference_from_rom:
            # A source-only rebuild derives references from the authenticated
            # native job table; no old generated class manifest is an input.
            job_table=struct.unpack_from('<I',original,0xc8598)[0]-0x08000000
            references=[]
            for job in range(116,126):
                p=0x419d60+32*(original[job_table+52*job+11]&15)
                references.append(dict(job=job,nativePaletteReference=p,nativePaletteSha256=sha(original[p:p+32])))
            classes=dict(jobs=references)
        else:
            class_path=ROOT/'build/art/generated-classes/595782ba32f4a20ff2053218f8722ab5e491112d/manifest.json'
            assert sha(class_path.read_bytes())=='9c30db597818297809590dbf2c2e08b3ed060466815c4964de83fabf872368d5'
            classes=json.loads(class_path.read_text())
        assert [j['job'] for j in classes['jobs']]==[j['job'] for j in catalog['jobs']]==list(range(116,126))
        for reference,draft in zip(classes['jobs'],catalog['jobs']):
            job=draft['job'];owner=job-116
            if job in overrides:
                row=overrides[job];draft=dict(draft,privateSource=row['source'],sourceSha256=row['sourceSha256'],technicalConversion=row['conversionManifest'])
            replacement=job in overrides
            manifest=ROOT/draft['technicalConversion'] if job!=117 or replacement else converted/'manifest.json'
            proof=json.loads(manifest.read_text());palette=(manifest.parent/'palette.bin').read_bytes()
            assert len(palette)==32 and sha(palette)==proof['paletteSha256']
            image_source=ROOT/draft['privateSource'] if job!=117 or replacement else source
            assert sha(image_source.read_bytes())==proof['sourceSha256']
            if job!=117 or replacement: assert proof['sourceSha256']==draft['sourceSha256']
            if job==117 and replacement:converted,art,colors,source=manifest.parent,proof,palette,image_source
            p=reference['nativePaletteReference'];native=original[p:p+32]
            assert sha(native)==reference['nativePaletteSha256']
            words[owner*16:owner*16+16]=struct.unpack('<16H',palette)
            native_words[owner*16:owner*16+16]=struct.unpack('<16H',native)
            if opposing_palettes:
                job_table=struct.unpack_from('<I',original,0xc8598)[0]-0x08000000
                selector=original[job_table+52*job+11]>>4
                offset=0x419d60+32*selector;opposite=original[offset:offset+32]
                opposing_words[owner*16:owner*16+16]=struct.unpack('<16H',opposite)
                opposing_inputs.append(dict(job=job,selector=selector,offset=offset,sha256=sha(opposite)))
            class_art[job]=(manifest.parent,proof)
            art_inputs.append(dict(job=job,source=str(image_source),sourceSha256=sha(image_source.read_bytes()),
                conversionManifest=str(manifest),conversionManifestSha256=sha(manifest.read_bytes()),
                paletteSha256=sha(palette),nativePaletteReference=p,nativePaletteSha256=sha(native)))
    config = work / 'colors.c'
    group_proof=None;custom_mask=1023 if all_classes else 2
    if palette_groups:
        assert all_classes and art_overrides and not publish_current and set(overrides)==set(range(116,126)), 'Grouped palette experiment requires private complete movement overrides'
        group_path=Path(palette_groups);group_spec=json.loads(group_path.read_text());groups=group_spec['groups']
        assert sorted(j for g in groups for j in g)==list(range(116,126)) and 1<=len(groups)<=10
        group_map=[next(i for i,g in enumerate(groups) if j in g) for j in range(116,126)]
        packed_words=[0]*160;reference_words=[0]*160
        for i,group in enumerate(groups):
            colors_i=words[(group[0]-116)*16:(group[0]-115)*16]
            assert all(words[(j-116)*16:(j-115)*16]==colors_i for j in group),'Grouped pixel indices require identical palettes'
            packed_words[i*16:i*16+16]=colors_i
            reference_words[i*16:i*16+16]=struct.unpack_from('<16H',original,0x419d60)
        words,native_words,opposing_words=packed_words,reference_words,reference_words.copy()
        custom_mask=(1<<len(groups))-1
        group_proof=dict(path=str(group_path),sha256=sha(group_path.read_bytes()),groups=groups,ownerMap=group_map,
                         scope='Private grouped-palette experiment; no full-animation or performance acceptance')
    config.write_text('#include <stdint.h>\nconst unsigned ffta_art_custom_mask='+str(custom_mask)+';\nconst uint16_t ffta_art_custom_colors[160]={' + ','.join(hex(v) for v in words) + '};\nconst uint16_t ffta_art_native_reference[160]={' + ','.join(hex(v) for v in native_words) + '};\n')
    if group_proof:
        with config.open('a') as f:f.write('const unsigned char ffta_art_palette_group[10]={'+','.join(map(str,group_map))+'};\n')
    if opposing_palettes:
        with config.open('a') as f:f.write('const uint16_t ffta_art_native_opposing_reference[160]={'+','.join(hex(v) for v in opposing_words)+'};\n')
    prefix = str(ROOT / 'tools/arm-gnu/bin/arm-none-eabi-')
    elf, binary = work / 'live.elf', work / 'live.bin'
    sources = ['src/engine/art-palette-live.c', 'src/engine/art-palette-live-hooks.s', 'src/engine/art-palette-owners.c', 'src/engine/art-palette-plan.c', 'src/engine/art-palette-scan.s', 'src/engine/art-palette-fade.c', 'src/engine/art-palette-binding.c', 'src/engine/art-palette-variants.c', 'src/engine/status-iterator-fast.s']
    if workspace_low_address:sources.extend(['src/engine/art-workspace-hooks.s','src/engine/art-workspace-allocation.c'])
    if provisional_history:sources.append('src/engine/art-palette-provisional.c')
    if shared_battle_menu_heap:sources.extend(['src/engine/art-party-heap.c','src/engine/art-party-heap.s'])
    if owned_menu_buffer:
        sources.extend(['src/engine/chemist-preference.c','src/engine/chemist-preference.s'])
        bindings=work/'party-bindings.s'
        bindings.write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n.align 2\n.global ffta_job_potion\n.thumb_func\nffta_job_potion:\n ldr r3,=0x091d0321\n bx r3\n.ltorg\n')
        sources.append(str(bindings))
    lookup, lookup_bytes = write_pixel_banks(work)
    if fast_bank_scan:sources.append('src/engine/art-palette-bank-scan.s')
    if dma_tile_cache:sources.extend(['src/engine/art-palette-dirty.c','src/engine/art-palette-dirty-hooks.s'])
    if arm_oam_scan:sources.append('src/engine/art-oam-demands.s')
    if repeat_frame:sources.extend(['src/engine/art-repeat-frame.c','src/engine/art-repeat-probe.s'])
    scoped_proof=None
    if scoped_frame:
        from art_scoped_build import build_scoped
        scoped_asm,scoped_proof=build_scoped(work,history_slots,native_owner_producer,fused_compose,fused_word_reads,compact_leaves,unrolled_copy)
        sources.append(str(scoped_asm))
    command = [prefix + 'gcc.exe', '-mcpu=arm7tdmi', '-mthumb', '-O2', '-ffreestanding', '-fno-builtin', '-nostdlib', '-Wall', '-Wextra', '-Werror', '-Wl,-Ttext=' + hex(0x08000000 + START), '-Wl,-e,ffta_art_live_begin', '-Wl,--defsym,ffta_art_clear_continue=0x091d071d', '-Wl,--defsym,ffta_art_original_status_next_entry=0x091e631d', '-Wl,--defsym,ffta_art_original_native_copy=0x091046c9', *sources, str(config), str(lookup), '-o', str(elf)]
    command[1:1]=['-DFFTA_ART_HISTORY_SLOTS='+str(history_slots),
        '-DFFTA_ART_LIVE_BASE='+hex(ram_base)+'u','-DFFTA_ART_LIVE_BYTES='+str(ram_bytes),
        '-Wl,--defsym,ffta_art_live_base='+hex(ram_base)]
    if opposing_palettes:command[1:1]=['-DFFTA_ART_OPPOSING_PALETTES=1']
    if group_proof:command[1:1]=['-DFFTA_ART_GROUPED_PALETTES=1']
    if rect_conflict:command[1:1]=['-DFFTA_ART_RECT_CONFLICT=1','-Wa,--defsym,FFTA_ART_RECT_CONFLICT=1']
    if prepared_preference:command[1:1]=['-DFFTA_ART_PREPARED_PREFERENCE=1']
    if joined_rows:command[1:1]=['-DFFTA_ART_JOINED_ROWS=1']
    if fast_confirm:command[1:1]=['-DFFTA_ART_FAST_CONFIRM=1']
    if burst_scan:command[1:1]=['-Wa,--defsym,FFTA_ART_BURST_SCAN=1']
    if block_scan:command[1:1]=['-Wa,--defsym,FFTA_ART_BLOCK_SCAN=1']
    if packed_plan:command[1:1]=['-DFFTA_ART_PACKED_PLAN=1']
    if fused_compose:command[1:1]=['-DFFTA_ART_FUSED_COMPOSE=1']
    if fused_word_reads:command[1:1]=['-DFFTA_ART_FUSED_WORD_READS=1']
    if native_owner_producer:command[1:1]=['-DFFTA_ART_NATIVE_OWNER_PRODUCER=1']
    if native_oam_prefix:command[1:1]=['-DFFTA_ART_NATIVE_OAM_PREFIX=1']
    if scoped_frame:command[1:1]=['-DFFTA_ART_SCOPED_FRAME=1']
    if trace_target:command[1:1]=['-DFFTA_ART_TRACE_TARGET=1']
    if provisional_history:command[1:1]=['-DFFTA_ART_PROVISIONAL_HISTORY=1']
    if fast_rotation:command[1:1]=['-DFFTA_ART_FAST_ROTATION=1']
    if fast_bank_scan:command[1:1]=['-DFFTA_ART_FAST_BANK_SCAN=1']
    if dma_tile_cache:command[1:1]=['-DFFTA_ART_DMA_TILE_CACHE=1']
    if fast_oam_plan:command[1:1]=['-DFFTA_ART_FAST_OAM_PLAN=1']
    if arm_oam_scan:command[1:1]=['-DFFTA_ART_ARM_OAM_SCAN=1']
    if repeat_frame:command[1:1]=['-DFFTA_ART_REPEAT_FRAME=1']
    if shared_battle_menu_heap:command[1:1]=['-DFFTA_ART_PARTY_ROOT='+hex(ram_limit-16)+'u']
    if compact_battle_status:command[1:1]=['-DFFTA_ART_COMPACT_STATUS=1','-Wa,--defsym,FFTA_ART_COMPACT_STATUS_ASM=1']
    if owned_menu_buffer:
        command[1:1]=['-DFFTA_PARTY_LIST_OFFSET=0x7280','-Wl,--defsym,ffta_potion_preference_labels=0x09281a90']
        command.append('-lgcc')
    compiled = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (work / 'compile.log').write_text(compiled.stdout + compiled.stderr); compiled.check_returncode()
    subprocess.run([prefix + 'objcopy.exe', '-O', 'binary', str(elf), str(binary)], check=True, capture_output=True)
    symbols = {v[2]: int(v[0], 16) for line in subprocess.check_output([prefix + 'nm.exe', str(elf)], text=True).splitlines() if len(v := line.split()) == 3}
    assert '__ffta_art_original_native_copy_from_thumb' not in symbols, 'ARMv4T requires BX interworking for the absolute Thumb copy target'
    code = binary.read_bytes(); assert len(code) < 0x30000
    cursor = START; segments = []; changes = []
    def add(raw, kind):
        nonlocal cursor
        cursor = (cursor + 3) & ~3; p = cursor; cursor += len(raw); assert cursor <= END
        rom[p:cursor] = raw; segments.append(dict(offset=p, bytes=len(raw), sha256=sha(raw), kind=kind)); return p
    add(code, 'compiled-palette-hooks')
    def patch(offset, before, after, purpose):
        assert bytes(rom[offset:offset + len(before)]) == before, (hex(offset), purpose)
        assert len(before) == len(after)
        rom[offset:offset + len(after)] = after
        changes.append(dict(offset=offset, bytes=len(after), before=before.hex(), after=after.hex(), purpose=purpose))
    if group_proof:
        group_job_table=struct.unpack_from('<I',original,0xc8598)[0]-0x08000000
        for job in range(116,126):
            at=group_job_table+job*52+11
            patch(at,original[at:at+1],bytes(1),'Grouped custom bodies share native transform source '+str(job))
    if compact_us_keyboard:
        # The authenticated US initializer builds pages 0/1; both shoulder-key
        # paths wrap at 1. Each native glyph page is exactly 0x2100 bytes.
        for at, expected in ((0x12a26e, '012801d9'), (0x12ac36, '012801dd'),
                             (0x12ac9a, '01202070')):
            assert rom[at:at+4].hex()==expected, ('US keyboard page bound',hex(at))
        patch(0x12a15e,bytes.fromhex('c6200002'),bytes.fromhex('42200002'),
              'US name keyboard reserves exactly two native 0x2100-byte glyph pages')
    if dma_tile_cache:
        # r3 is the live DMA channel; the displaced r0 value is dead here.
        patch(0x820,bytes.fromhex('1160a0685060e068'),bytes.fromhex('00480047')+struct.pack('<I',symbols['ffta_art_queued_obj_write']|1),
              'Private exact native queued OBJ write notification before DMA start')
    if workspace_low_address:
        patch(0x13078c4,struct.pack('<I',0x08022841),struct.pack('<I',symbols['ffta_art_workspace_allocate']|1),'Use a low-address native free block for the persistent expansion battle workspace')
    if owned_menu_buffer:
        # 0x230 header + 460*20-byte rows fits 0x2700 bytes. Preserve the
        # existing 0x7280-byte owner, including AP/status/job-copy tails.
        for at in (0x71118,0x711f8):
            patch(at,struct.pack('<I',0x7280),struct.pack('<I',0x9980),'Party owner includes expanded list tail')
        patch(0x71228,struct.pack('<I',0x2cc48),struct.pack('<I',0x7280),'Native party list belongs to its allocated context')
        for at in ((0x30c06,0x30c78) if shared_battle_menu_heap else (0x24644,0x30c06,0x30c78)):
            patch(at,bytes.fromhex('c624'),bytes.fromhex('ed24'),'Battle/world party scene parent allocation includes list tail')
        for at in (0x30c34,0x30c9c):
            patch(at,struct.pack('<I',0xc640),struct.pack('<I',0xed40),'World party scene outer heap includes list tail')
        for at,old,name in ((0x7d974,0x09280235,'ffta_potion_roster_entry'),(0x7e00c,0x0928026d,'ffta_potion_confirm_entry')):
            patch(at,struct.pack('<I',old),struct.pack('<I',symbols[name]|1),'Auto-Potion preference uses context-owned list')
    if shared_battle_menu_heap:
        for at,before,name in (
            (0x24642,'094dc6242402201cfef7f9f8286006480460','ffta_art_party_parent_entry'),
            (0x24684,'fef7e6f800202060','ffta_art_party_parent_free_entry'),
            (0x70c8,'70b50c1c061c114d','ffta_art_party_heap_init_entry'),
            (0x718c,'00b503490a680421','ffta_art_party_heap_close_entry')):
            jump=(bytes.fromhex('c046') if at%4 else b'')+bytes.fromhex('004b1847')+struct.pack('<I',symbols[name]|1)
            jump+=bytes.fromhex('c046')*((len(bytes.fromhex(before))-len(jump))//2)
            patch(at,bytes.fromhex(before),jump,'Share battle heap through exact native party lifecycle: '+name)
    if compact_battle_status:
        # Restrict the smaller context to the actual read-only Status caller;
        # mode1 alone also occurs in world menus and is not sufficient.
        for at,before,name in (
            (0x70688,'2c49ff200870012000f004fd','ffta_art_party_readonly_entry'),
            (0x71138,'95f7feff011c2960','ffta_art_party_context_entry'),
            (0x711cc,'15494218154bc118','ffta_art_party_list_entry')):
            jump=bytes.fromhex('004b1847')+struct.pack('<I',symbols[name]|1)
            jump+=bytes.fromhex('c046')*((len(bytes.fromhex(before))-8)//2)
            patch(at,bytes.fromhex(before),jump,'Read-only battle Status keeps its native list area: '+name)
    assert original[0x9dd52:0x9dd62].hex() == '08b4004b18471d631e09c046c046c046'
    patch(0x9dd58, struct.pack('<I', 0x091e631d), struct.pack('<I', symbols['ffta_art_status_next_entry'] | 1), 'status iterator unconditional native-key advance')
    patch(0x36d4bc,struct.pack('<I',0x091046c9),struct.pack('<I',symbols['ffta_art_native_copy_entry']|1),'native OBJ palette reload notification preserving existing copy handler')
    for offset, old, name in [(0x6d0, '80b56f460b488021', 'begin'), (0x788, '80b56f4609480a49', 'end'), (0x1194, '70b5214d214c2078', 'reset'), (0x12bc, 'f0b557464e464546', 'compose'), (0x216f8, 'f0b557464e464546', 'render'), (0x8f1f4, 'f0b557464e464546', 'battle_render')]:
        patch(offset, bytes.fromhex(old), bytes.fromhex('004b1847') + struct.pack('<I', symbols['ffta_art_live_' + name] | 1), 'native palette ' + name)
    assert original[0x148738:0x148740].hex()=='7047000070470000', 'Native task handles are identity helpers'
    for offset, old, name in [(0x146864, 'f0b557464e464546', 'rotate'),
                              (0x146bb0, 'f0b5041c231c0c33', 'cycle'),
                              (0x146dc8, 'f0b50004060c0904', 'cancel'),
                              (0x148498, '00b500f04df9011c', 'delete'),
                              (0x1484cc, '10b5041c002c1dd0', 'collect'),
                              (0x148540, '10b509484468002c', 'delete_all'),
                              (0x146e54, 'f0b557464e464546e0b486b00004000c', 'setup'),
                              (0x147a7c, '70b50004040c0904', 'black'),
                              (0x147ad0, '70b50004040c0904', 'white'),
                              (0x147b28, 'f0b557464e464546', 'gray'),
                              (0x147ba4, 'f0b557464e464546', 'tint'),
                              (0x147c2c, 'f0b557464e464546e0b481b0099c0a9d', 'rgb'),
                              (0x147cc0, 'f0b5059c069d0004060c0904090c1204', 'solid'),
                              (0x147d94, 'f0b557464e464546e0b481b0099c0a9d', 'blend'),
                              (0x147ec8, 'f0b557464e464546e0b481b00004070c', 'brighten'),
                              (0x147f50, 'f0b557464e464546e0b481b00004070c', 'darken'),
                              (0x14731c, 'f0b557464e464546e0b481b00004000c', 'exposure'),
                              (0x1473e4, 'f0b557464e464546e0b483b00b9c0c9d', 'exposure_rgb'),
                              (0x1474bc, 'f0b557464e464546e0b483b001930b9b', 'table_exposure'),
                              (0x147e28, 'f0b557464e464546e0b482b001930a9b', 'table_blend'),
                              (0x147d2c, 'f0b51f1c0004050c0904090c1204120c', 'table'),
                              (0x148740, '00b5031c59882020', 'tick')]:
        suffix = '_entry' if name in {'rotate','cycle'} else ''
        target = struct.pack('<I', symbols['ffta_art_live_fade_' + name + suffix] | 1)
        if name in {'setup','table','rgb','solid','blend','brighten','darken','exposure','exposure_rgb','table_exposure','table_blend'}:
            assert len(old)==32, name+' requires the r3-preserving16-byte entry'
        # Four-argument entries must not use r3 as a destructive branch register.
        jump = bytes.fromhex('08b4024b9c4608bc6047c046') + target if len(old) == 32 else bytes.fromhex('004b1847') + target
        patch(offset, bytes.fromhex(old), jump, 'native fade ' + name)
    # The three authenticated heap-limit veneers already reserve through F000.
    for start in (0x1103db4, 0x1103dd0, 0x1103dec):
        assert original[start:start + 16].hex() == '034c641b034801b40348864601bc7047'
        patch(start + 16, struct.pack('<I', 0x0203f000), struct.pack('<I', ram_base), 'reserve transient palette pages')
    patch(0x11d0714, bytes.fromhex('204b214a3b409342'), bytes.fromhex('004b1847') + struct.pack('<I', symbols['ffta_art_clear_endpoint'] | 1), 'preserve clear owner reset for new heap endpoint')

    job_poses={};action_plans={}
    for job,(directory,proof) in class_art.items():
        poses=[]
        for i,frame in enumerate(proof['frames']):
            with Image.open(directory/f'frame-{i:02}.png') as image: pose=image.copy()
            assert pose.size==(32,32) and pose.mode=='P' and sha(pack_tiles(pose,16))==frame['tileSha256']
            poses.append(pose)
        assert len(poses) in (4,6,8)
        job_poses[job]=poses
        if job in overrides and 'actionPlan' in overrides[job]:
            from live_action_plan import LiveActionPlan
            row=overrides[job];plan_path=ROOT/row['actionPlan']
            assert sha(plan_path.read_bytes())==row['actionPlanSha256'],'Action plan identity'
            action_plans[job]=LiveActionPlan(plan_path,job,original,parent['resources'],(directory/'palette.bin').read_bytes())
    rgb = [i * 16 for i in range(16) for _ in range(3)]
    tiles, layouts, assignments, sequences = {}, {}, [], {}
    for resource in parent['resources']:
        if resource['job'] not in class_art: continue
        poses=job_poses[resource['job']]
        descriptors = resource['descriptors']
        for slot in range(resource['slots']):
            pointer = struct.unpack_from('<I', original, descriptors + slot * 12)[0]
            if not pointer: continue
            q = pointer - 0x08000000; count = struct.unpack_from('<I', original, q)[0]
            seq = bytearray(original[q:q + 4 + count * 20]); frames = []
            for f in range(count):
                t, o = struct.unpack_from('<II', seq, 4 + f * 20)
                objects, _ = layout(original, OAM + o)
                assert len(objects) == 1 and objects[0]['width'] == objects[0]['height'] == 32 and objects[0]['tile'] == 0
                old = tile_image(original[TILES + t:TILES + t + 512], rgb, 32)
                old_bottom = Image.frombytes('L', old.size, old.tobytes()).getbbox()[3] + objects[0]['y']
                phase = (0, 1, 2, 1)[f % 4] + (3 if slot % 2 else 0)
                if len(poses)!=6:
                    phases=(0,4,2,6) if len(poses)==8 else (0,0,2,2)
                    phase=phases[(2 if slot%2 else 0)+f%2]
                pose = poses[phase].copy();explicit=None
                if resource['job'] in action_plans:
                    override=action_plans[resource['job']].frame(resource['id'],slot,f)
                    if override is not None:pose,explicit=override
                if resource['lifetime'] == 'water' and explicit is None:
                    cropped = Image.new('P', (32, 32)); cropped.putpalette(pose.getpalette())
                    cropped.paste(pose.crop((0, 0, 32, 20)), (0, 0)); pose = cropped
                bottom = Image.frombytes('L', pose.size, pose.tobytes()).getbbox()[3]
                dy = old_bottom - bottom; assert -128 <= dy < 128
                raw = pack_tiles(pose, 16)
                obj = struct.pack('<4H', 1, dy & 255, objects[0]['attributes'][1], 0)
                if raw not in tiles: tiles[raw] = add(raw, 'existing-imagegen-draft-tiles')
                if obj not in layouts: layouts[obj] = add(obj, 'aligned-draft-layout')
                struct.pack_into('<II', seq, 4 + f * 20, tiles[raw] - TILES, layouts[obj] - OAM)
                frames.append(dict(phase=phase, tile=tiles[raw], tileSha256=sha(raw), oam=layouts[obj], y=dy))
                if explicit is not None:frames[-1]['explicitAction']=explicit
            if all_classes:
                key=bytes(seq)
                if key not in sequences: sequences[key]=add(seq,'generated-class-draft-sequence')
                new=sequences[key]
            else: new = add(seq, 'dark-knight-draft-sequence')
            patch(descriptors + slot * 12, struct.pack('<I', pointer), struct.pack('<I', new + 0x08000000), 'Class '+str(resource['job'])+' custom-palette sequence' if all_classes else 'Dark Knight custom-palette sequence')
            assignments.append(dict(resource=resource['id'], lifetime=resource['lifetime'], slot=slot, source=q, sequence=new, frames=frames))
    allowed = set(range(START, cursor))
    for change in changes: allowed.update(range(change['offset'], change['offset'] + change['bytes']))
    assert len(rom) == len(original) and all(a == b or i in allowed for i, (a, b) in enumerate(zip(original, rom)))
    digest = hashlib.sha1(rom).hexdigest(); out = ROOT / 'build/art/live-palette' / digest; out.mkdir(parents=True, exist_ok=True)
    path = out / 'FFTA_Live_Palette_POC.gba'; path.write_bytes(rom)
    result = dict(path=str(path), romSha1=digest, source=parent['path'], baseRomSha1=parent['romSha1'], releaseSource=parent['releaseSource'],
                  reservation=[START, END], used=[START, cursor], ramReservation=[ram_base, ram_limit], heapEnd=ram_base,
                  symbols=symbols, changes=changes, segments=segments, assignments=assignments, compileDirectory=str(work),
                  sources={name: sha((ROOT / name).read_bytes()) for name in sources + ['src/engine/art-palette-plan.h', 'src/engine/art-palette-owners.h', 'src/engine/art-palette-fade.h', 'src/engine/art-palette-binding.h', 'src/engine/art-palette-variants.h', 'src/engine/art-palette-limits.h', 'scripts/art_palette_build.py', 'scripts/build-live-art-palette.py']},
                  pixelBankLookupSha256=sha(lookup_bytes), pixelBankLookupBytes=len(lookup_bytes), transientStateBytes=8096, bindingOffset=2740, bindingEntryBytes=252, visibleColorsOffset=5608, profileOffset=8052, refusalOffset=8060, variantOffset=8076,
                  generatedSource=str(source), generatedSourceSha256=sha(source.read_bytes()), conversionManifest=str(converted / 'manifest.json'), conversionManifestSha256=sha((converted / 'manifest.json').read_bytes()), paletteSha256=sha(colors),
                  scope='Private live palette hook and owned RAM integration; existing unaccepted Dark Knight draft repeated through land/water action timing. Consult separately pinned runtime evidence for fade/variant coverage and remaining timing, color-mode, consumer and lifetime failures. This build manifest alone does not establish runtime or final-art acceptance. Not installed or packaged.')
    result.update(historySlots=history_slots,allClasses=all_classes,artInputs=art_inputs,bindingCounterOffset=2840,tagOffset=2608,
        displayOffset=2736,fadeCommandOffset=5592,emittedOffset=5596,composePhaseOffset=5604)
    if all_classes:
        result.update(catalogSha256=sha(catalog_path.read_bytes()),classManifest=None if native_reference_from_rom else str(class_path),classManifestSha256=None if native_reference_from_rom else sha(class_path.read_bytes()),nativeReferenceFromRom=native_reference_from_rom,
            scope='Private ten-class live custom-palette transport with20 histories and12KiB owned RAM. Authenticated existing unaccepted imagegen drafts repeated through all land/water action slots; complete animation metadata retained. Per-class native palette references and generated colors remain separate. This manifest alone does not establish mixed-class coexistence, worst-case heap capacity, timing or final-art acceptance. Not installed or packaged.')
    if history_slots!=10:
        names=('transientStateBytes','bindingOffset','visibleColorsOffset','profileOffset',
            'refusalOffset','variantOffset','tagOffset','displayOffset','fadeCommandOffset',
            'emittedOffset','composePhaseOffset','bindingCounterOffset')
        values=struct.unpack_from('<12I',rom,symbols['ffta_art_live_layout']-0x08000000)
        result.update(zip(names,values))
        assert result['transientStateBytes']<=ram_bytes and result['bindingCounterOffset']==history_slots*284
    result['workspaceLowAddress']=workspace_low_address
    if history_slots==20:
        result['nativeHighlightOffset']=struct.unpack_from('<I',rom,symbols['ffta_art_live_layout']-0x08000000+(52 if provisional_history else 48))[0]
        result['sources']['src/engine/art-palette-highlight.h']=sha((ROOT/'src/engine/art-palette-highlight.h').read_bytes())
    result['traceTarget']=trace_target
    result['provisionalHistory']=provisional_history
    result['fastRotation']=fast_rotation
    result['fastBankScan']=fast_bank_scan
    result['dmaTileCache']=dma_tile_cache
    result['fastOamPlan']=fast_oam_plan
    result['armOamScan']=arm_oam_scan
    result['fusedCompose']=fused_compose
    if compact_leaves:result['compactLeaves']=True
    if opposing_palettes:result.update(opposingPalettes=True,opposingPaletteInputs=opposing_inputs)
    if rect_conflict:result['rectConflict']=True
    if prepared_preference:result['preparedPreference']=True
    if joined_rows:result['joinedRows']=True
    if fast_confirm:result['fastConfirm']=True
    if burst_scan:result['burstScan']=True
    if block_scan:result['blockScan']=True
    if packed_plan:result['packedPlan']=True
    if unrolled_copy:result['unrolledCopy']=True
    result['fusedWordReads']=fused_word_reads
    result['nativeOwnerProducer']=native_owner_producer
    result['nativeOamPrefix']=native_oam_prefix
    result['scopedFrame']=scoped_proof
    if scoped_proof:result['sources'].update(scoped_proof['sources'])
    result['repeatFrame']=repeat_frame
    if repeat_frame:
        result['repeatKeyVersion']=2
        result['repeatOffset'],result['repeatBytes']=struct.unpack_from('<2I',rom,symbols['ffta_art_repeat_layout']-0x08000000)
        result['sources']['src/engine/art-repeat-frame.h']=sha((ROOT/'src/engine/art-repeat-frame.h').read_bytes())
    if dma_tile_cache:
        result['sources']['src/engine/art-palette-dirty.h']=sha((ROOT/'src/engine/art-palette-dirty.h').read_bytes())
        result['scope']='Private queue-only tile-cache prototype; direct CPU/BIOS and other writer coverage is incomplete. Do not package. '+result['scope']
    result['separateMenuRam']=separate_menu_ram
    result['ownedMenuBuffer']=owned_menu_buffer
    result['compactUsKeyboard']=compact_us_keyboard
    result['compactBattleStatus']=compact_battle_status
    result['sharedBattleMenuHeap']=shared_battle_menu_heap
    if shared_battle_menu_heap:
        assert ram_base+result['transientStateBytes']<=ram_limit-16
        result['partyHeapRoot']=ram_limit-16
    if owned_menu_buffer:result['partyList']=dict(offset=0x7280,bytes=0x2700,ownerBytes=0x9980,parentBytes=0xed00)
    if compact_battle_status:result['readonlyPartyList']=dict(offset=0x4340,bytes=0x1780,ownerBytes=0x7280,entry=0x08070688,magic=0x50485232)
    if separate_menu_ram:result['menuRamReservation']=[0x0203c000,0x0203f000]
    if provisional_history:
        result['confirmedOffset']=struct.unpack_from('<I',rom,symbols['ffta_art_live_layout']-0x08000000+48)[0]
        result['sources']['src/engine/art-palette-provisional.h']=sha((ROOT/'src/engine/art-palette-provisional.h').read_bytes())
    if override_proof:result['artOverrides']=override_proof
    if group_proof:result['paletteGroups']=group_proof
    if action_plans:
        result['actionPlans']=[plan.report() for plan in action_plans.values()]
        result['sources']['scripts/live_action_plan.py']=sha((ROOT/'scripts/live_action_plan.py').read_bytes())
    if trace_target:result['scope']='Diagnostic only: halt on first unmapped explicit palette target; never install or package. '+result['scope']
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    index='status-current.json' if compact_battle_status else 'keyboard-current.json' if compact_us_keyboard else 'shared-menu-current.json' if shared_battle_menu_heap else 'owned-menu-current.json' if owned_menu_buffer else 'menu-safe-current.json' if separate_menu_ram else 'target-trace-current.json' if trace_target else 'all-classes-workspace-current.json' if workspace_low_address else 'all-classes-current.json' if all_classes else 'poc.json' if history_slots==10 else 'history-current.json'
    if publish_current:(ROOT/'build/art/live-palette'/index).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(romSha1=digest, bytes=cursor - START, manifest=str(out / 'manifest.json'))))
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--history-slots',type=int,choices=(10,20),default=10)
    parser.add_argument('--all-classes',action='store_true')
    parser.add_argument('--workspace-low-address',action='store_true')
    parser.add_argument('--trace-target',action='store_true')
    parser.add_argument('--provisional-history',action='store_true')
    parser.add_argument('--fast-rotation',action='store_true')
    parser.add_argument('--separate-menu-ram',action='store_true')
    parser.add_argument('--owned-menu-buffer',action='store_true')
    parser.add_argument('--shared-battle-menu-heap',action='store_true')
    parser.add_argument('--compact-us-keyboard',action='store_true')
    parser.add_argument('--compact-battle-status',action='store_true')
    args=parser.parse_args();build(args.history_slots,args.all_classes,args.workspace_low_address,args.trace_target,args.provisional_history,args.fast_rotation,args.separate_menu_ram,args.owned_menu_buffer,args.shared_battle_menu_heap,args.compact_us_keyboard,args.compact_battle_status)
