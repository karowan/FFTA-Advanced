"""Native completion-bit/town-key audit, including ordinary save and cold load.

The mission tests execute native decision blocks through the flag operation,
not full combat/reward or mission acceptance UI. No user saves are modified.
"""
import hashlib
import importlib.util
import json
import pathlib
import runpy
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
arm = runpy.run_path(str(ROOT / 'scripts/test-battle-inventory.py'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *

OUT = ROOT / 'build/expansion/probes'
VANILLA = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
RECORDS = [7, 13, 19]
NAMES = ['Twisted Flow', 'Pale Company', 'Desert Patrol']
TOWNS = {2: 'Cyril', 3: 'Sprohm', 4: 'Muscadet', 5: 'Cadoan', 6: 'Baguba Port'}
ACTIVE = 0x02007000
iwram = arm['native_iwram']()


def machine():
    m = arm['ARM'](iwram)
    m.put(0x08000000, VANILLA)
    return m


def block(m, start, stops, registers):
    for reg, value in registers.items(): m.u.reg_write(reg, value)
    m.u.reg_write(UC_ARM_REG_SP, 0x03007000)
    m.u.reg_write(UC_ARM_REG_LR, 0x08000101)
    def halt(u, address, size, data):
        if address in stops: u.emu_stop()
    hook = m.u.hook_add(UC_HOOK_CODE, halt)
    try: m.u.emu_start(start | 1, 0x08000100, count=100000)
    finally: m.u.hook_del(hook)
    pc = m.u.reg_read(UC_ARM_REG_PC)
    assert pc in stops, f'Native block escaped: {pc:x}'
    return pc


def gate(m, record): return m.call(0x080C9540, record + 0x2FF)


def battle_result(m, record, success):
    m.w16(ACTIVE, record)
    block(m, 0x080D1E70, [0x080D1EAC], {UC_ARM_REG_R0: ACTIVE, UC_ARM_REG_R1: success})


def dispatch_result(m, record, outcome, processed=True):
    payload = bytearray(8)
    payload[3] = 0x80 if processed else 0
    payload[4] = record & 255
    payload[5] = (outcome & 0xFE) | (record >> 8)
    m.put(ACTIVE, payload)
    block(m, 0x080D0F74, [0x080D0FC4, 0x080D11F8], {UC_ARM_REG_R0: ACTIVE})


def pub_excludes(m, record):
    pc = block(m, 0x080CFD44, [0x080CFD6E, 0x080CFD72],
               {UC_ARM_REG_R5: 0x0855AE4C + record * 70, UC_ARM_REG_R6: record})
    return pc == 0x080CFD6E


def gate_checks():
    cases = []
    for record, name in zip(RECORDS, NAMES):
        assert struct.unpack_from('<H', VANILLA, 0x55AE4C + record * 70)[0] == record
        assert not VANILLA[0x55AE4C + record * 70 + 0x41] & 8
        flag = record + 0x2FF
        for success in (0, 1, 0x100):
            m = machine()
            m.w16(ACTIVE, record)
            assert gate(m, record) == 0 and not pub_excludes(m, record)
            before = m.get(0x02001F70, 256)
            battle_result(m, record, success)
            assert gate(m, record) == int(success != 0)
            assert pub_excludes(m, record) == bool(success)
            expected = bytearray(before)
            if success: expected[flag // 8] |= 1 << (flag & 7)
            assert m.get(0x02001F70, 256) == expected
            # A later failure must not erase an already earned completion.
            battle_result(m, record, 0)
            assert gate(m, record) == int(success != 0)
        for outcome in (0, 2, 0xC6, 0xC8, 0xCA, 0xFE):
            for processed in (False, True):
                m = machine()
                dispatch_result(m, record, outcome, processed)
                expected = int(processed and outcome == 0xC8)
                assert gate(m, record) == expected
                assert pub_excludes(m, record) == bool(expected)
        cases.append({'record': record, 'name': name, 'flag': flag,
                      'address': 0x02001F70 + flag // 8, 'mask': 1 << (flag & 7),
                      'battleCases': 3, 'dispatchCases': 12})
    return cases


def town_checks():
    m = machine()
    # Place the five identities on arbitrary distinct grid positions. The
    # native inverse lookup must identify towns independently of placement.
    for key, tile in zip(TOWNS, (1, 2, 3, 4, 5)):
        m.put(0x02002C10 + 0xB3 + (key - 1) * 12, [tile])
        assert m.call(0x08036350, tile) == key
    result = []
    state = 0x02020000
    m.w32(0x0200F428, state)
    for key, tile in zip(TOWNS, (1, 2, 3, 4, 5)):
        m.put(0x02002E54, [tile | 0xE0])
        block(m, 0x08068CDC, [0x08068CF6], {})
        assert m.get(state + 0x4BFB, 1) == bytes([key])
        for tier in (0, 9, 10, 19, 20, 65535):
            m.w16(0x02001F6C, tier)
            block(m, 0x0806E2B6, [0x0806E2CE], {UC_ARM_REG_R4: 2})
            assert m.u.reg_read(UC_ARM_REG_R1) == 2
            assert m.u.reg_read(UC_ARM_REG_R2) == tier
            assert m.u.reg_read(UC_ARM_REG_R3) == key
            assert m.call(0x080CC8B4, tier) == (0 if tier <= 9 else 1 if tier <= 19 else 2)
        # Execute the native location-label lookup arithmetic used by world UI.
        # Context+0x1D contains the same canonical location identity.
        context = 0x02028000
        m.put(context + 0x1D, [key])
        block(m, 0x0803D2A2, [0x0803D2AE], {UC_ARM_REG_R2: context})
        pointer_slot = m.u.reg_read(UC_ARM_REG_R0)
        assert pointer_slot == 0x08526680 + (key + 0x2CD) * 4
        result.append({'key': key, 'town': TOWNS[key], 'namePointerSlot': pointer_slot,
                       'namePointer': m.r32(pointer_slot), 'specialStock': m.call(0x080CCCF0, key)})
    return result


def save_checks():
    spec = importlib.util.spec_from_file_location('harness', ROOT / 'scripts/emulator-test.py')
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    seed_path = ROOT / 'build/test-lab/early-town.sav'
    seed = seed_path.read_bytes()
    rom = ROOT / 'build/foundation/FFTA_vanillaplus_dev.gba'
    def tap(e, key, wait=40): e.run(8, key); e.run(wait)
    def cold(data):
        e = h.Emulator(rom)
        e.set_memory(0, data, 0)
        e.run(3600)
        for key, wait in [(8, 180), (256, 60), (256, 60), (256, 180)]: tap(e, key, wait)
        return e
    e = cold(seed)
    try:
        m = machine()
        m.put(0x02000000, e.memory())
        for record in RECORDS:
            m.call(0x080C9574, record + 0x2FF, 0)
            battle_result(m, record, 0)
            assert gate(m, record) == 0
            battle_result(m, record, 1)
            assert gate(m, record) == 1
        # Only transfer the native flag bank changed by native success code.
        expected = m.get(0x02001FD0, 3)
        e.set_memory(0x1FD0, expected)
        for key, wait in [(8, 40), (16, 40), (256, 40), (256, 60),
                          (256, 60), (64, 20), (256, 300)]: tap(e, key, wait)
        saved = e.memory(0)
        assert saved != seed
    finally: e.close()
    e = cold(saved)
    try:
        loaded = e.memory()
        assert loaded[0x1FD0:0x1FD3] == expected
        m.put(0x02000000, loaded)
        assert all(gate(m, record) == 1 for record in RECORDS)
    finally: e.close()
    assert seed_path.read_bytes() == seed
    return {'nativeSaveSha1': hashlib.sha1(saved).hexdigest(),
            'persistedBytes': expected.hex(), 'coldLoadPredicates': [1, 1, 1]}


def stock_checks(candidate=None):
    image = candidate if candidate is not None else (OUT / 'content-inventory.gba').read_bytes()
    binary = None
    if candidate is None:
        binary = (ROOT / 'build/expansion/engine.bin').read_bytes()
        content_manifest = json.loads((OUT / 'content-inventory.json').read_text())
        assert content_manifest['engineSha1'] == hashlib.sha1(binary).hexdigest(), 'Rebuild content probe for current engine'
    symbols = {line.split()[2]: int(line.split()[0], 16) for line in
               (ROOT / 'build/expansion/engine.symbols').read_text().splitlines() if len(line.split()) == 3}
    registry = json.loads((ROOT / 'build/expansion/registry.json').read_text())
    ledger = json.loads((ROOT / 'notes/equipment-acquisition.json').read_text())
    ids = {item['id']: item['romItemId'] for item in registry['items']}
    m, native = machine(), machine()
    m.put(0x08000000, image)
    # The matching manifest ensures native hook destinations and current
    # symbol addresses refer to the same compiled engine.
    if binary is not None: m.put(0x09100000, binary)
    destination = 0x0203C000
    turf_base = native.r32(0x080CED28)
    cases, maximum, duplicate_cases = 0, 0, 0
    maxima = {name: 0 for name in TOWNS.values()}
    for territory in (0, 7, 30):
        for n in range(30):
            for instance in (m, native): instance.put(turf_base + n * 12 + 1, [3 if n < territory else 0])
        assert m.call(0x080CECF4) == territory
        for town, name in TOWNS.items():
            for tier in (0, 10, 20):
                for tab in range(6):
                    old_count = native.call(0x080CBDC0, destination, tab, tier, town)
                    old_rows = native.get(destination, old_count * 4)
                    old_ids = list(struct.unpack('<' + 'HBB' * old_count, old_rows))[::3]
                    for gates in range(8):
                        for n, record in enumerate(RECORDS):
                            m.call(0x080C9574, record + 0x2FF, bool(gates & (1 << n)))
                        expected_ids = [ids[item['id']] for item in ledger['items']
                                        if tab == 2 and name in [item['primaryShop']] + item['additionalShops']
                                        and (item['stageId'] == 'S0' or gates & (1 << (int(item['stageId'][1:]) - 1)))]
                        expected_count = old_count + len(expected_ids)
                        m.put(destination, b'\xB7' * (460 * 4 + 32))
                        count = m.call(0x080CBDC0, destination, tab, tier, town)
                        assert count == expected_count, (name, tier, tab, territory, gates, count, expected_count)
                        assert m.get(destination, old_count * 4) == old_rows, 'Original stock changed'
                        actual_rows = m.get(destination + old_count * 4, len(expected_ids) * 4)
                        assert actual_rows == b''.join(struct.pack('<HBB', item, 0, 0) for item in expected_ids)
                        assert len(expected_ids) == len(set(expected_ids))
                        assert set(old_ids).isdisjoint(expected_ids)
                        duplicate_cases += int(len(old_ids) != len(set(old_ids)))
                        assert count <= 255, 'Native shop count at context+446D truncates to byte'
                        assert m.get(destination + count * 4, 32) == b'\xB7' * 32
                        maximum = max(maximum, count)
                        maxima[name] = max(maxima[name], count)
                        cases += 1
    # Type31 remains a bit-mask category in pricing, never an array index.
    price_cases, axe_discount_towns = 0, set()
    discount_table = m.r32(0x080CBC78)
    rank_address = m.r32(0x080CBC7C) + m.r32(0x080CBC80)
    items = m.r32(0x080CBC74)
    for rank in (0, 1, 5):
        m.put(rank_address, [rank])
        clan_discount = m.get(discount_table + rank * 10 + 8, 1)[0]
        for town in TOWNS:
            stock_mask = m.r32(m.call(0x080CCCF0, town))
            for item in registry['items']:
                item_id = item['romItemId']
                row = m.get(items + item_id * 32, 32)
                base, sell = struct.unpack_from('<HH', row, 4)
                assert base == item['basePriceGil']
                favored = bool(stock_mask & (1 << (row[8] - 1)))
                if row[8] == 31 and favored: axe_discount_towns.add(town)
                reduction = clan_discount + (10 if favored else 0)
                expected = max(sell, base * (100 - reduction) // 100) if row[12] & 8 else base
                assert m.call(0x080CBC14, town, item_id) == max(expected, 1)
                price_cases += 1
    # Native buy commit carries a u16 equipment ID directly to CA900. Exercise
    # that complete quantity/grant/gil block with the installed hooks; no quest
    # reward dispatcher or its >=376 namespace rule belongs in this path.
    state = 0x02020000
    m.w32(0x0200F428, state)
    selected_offset = m.r32(0x0806A948)
    quantity_offset = m.r32(0x0806A94C) + 0x79
    quest = bytes((n * 17 + 3) & 255 for n in range(120))
    buy_cases = 0
    for item in registry['items']:
        item_id = item['romItemId']
        for quantity in (1, 3):
            m.put(0x02001940, bytes(512))
            m.put(0x02002B08, quest)
            m.w16(state + selected_offset, item_id)
            m.put(state + quantity_offset, [quantity])
            m.w32(state + 0x4500, item['basePriceGil'] * quantity)
            m.w32(0x02001F64, 100000)
            block(m, 0x0806A8C2, [0x0806A900], {UC_ARM_REG_R6: 0x0200F428})
            expected = bytearray(512)
            expected[item_id] = quantity
            assert m.get(0x02001940, 512) == expected, (item_id, quantity,
                [(n, v) for n, v in enumerate(m.get(0x02001940, 512)) if v],
                m.get(0x02001E70, 12).hex())
            assert m.get(0x02002B08, 120) == quest
            assert m.r32(0x02001F64) == 100000 - item['basePriceGil'] * quantity
            buy_cases += 1
    return {'compiledFunction': symbols['ffta_shop_buy_list'], 'engineSha1': hashlib.sha1(binary).hexdigest() if binary is not None else None,
            'contentRomSha1': hashlib.sha1(image).hexdigest(), 'stockCases': cases,
            'maxCount': maximum, 'maxByTown': maxima,
            'casesContainingPreservedNativeDuplicates': duplicate_cases,
            'addedDuplicates': 0, 'priceCases': price_cases, 'nativeBuyCommitCases': buy_cases,
            'axeTownCategoryDiscounts': sorted(axe_discount_towns)}


if __name__ == '__main__':
    result = {'passed': True, 'nativeRomSha1': hashlib.sha1(VANILLA).hexdigest(),
              'gates': gate_checks(), 'towns': town_checks(), 'save': save_checks(), 'stock': stock_checks(),
              'limitations': ['Mission success/failure decision blocks are executed, not full battle/reward UI.',
                              'An active record alone and unprocessed dispatch do not satisfy completion; full acceptance UI is not exercised.',
                              'Town labels are independently decoded from the native pointer table in notes/acquisition-engine.md.']}
    (OUT / 'acquisition-gates.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
