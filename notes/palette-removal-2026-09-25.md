# Retiring the art palette engine

Status: accepted as a stage of release 0.7.3. The released game is the
[memory-fixes](memory-fixes-2026-09-25.md) candidate built on this stage, from
`scripts/memory-fixes-test-plan.json`. The first local package
(`0.7.3-palette-removal`, game `6b87ebac…`, run `20260925T073131.545678Z`)
predates the audit corrections below and is superseded. Released in v0.7.3.

## Problem

Pressing R on a unit during pre-battle deployment showed a screen of repeated
garbage tiles, and closing it could leave a permanent black screen. This has
affected every release since v0.7.0.

The cause was a live palette engine that the art integration added (September
18–19). Project rules forbid custom palette systems. The artwork was later
converted to native shared palettes, and the engine's 29 palette, render and
fade hooks were restored (`notes/native-art-shared-palettes.md`). The rest of
the engine stayed installed:

- a 12 KiB EWRAM reservation `0x0203C000..0x0203F000`, made by lowering the
  native heap end;
- one heap-setup hook that still initialized palette state there;
- workarounds for the lost memory: a borrowed battle heap, and a compact
  "read-only" Status context.

In deployment the native unit Info screen needs roughly 51.8 KB of heap. Only
39.6 KB remained, so its 10 KiB display buffer allocation failed. The screen
then drew garbage, and freeing the NULL buffer corrupted the heap. The pre-art
build shows the same screen correctly.

The compact Status context was designed for the in-battle Status screen only.
The deployment Info screen uses the same entry (`08070688`), and from there
Equip Items can open a list of up to 461 owned items. With every item owned,
that list overflowed the compact 376-entry area by about 1.3 KB into the
context's AP/status/job-copy tail.

## Change

[build-palette-removal.py](../scripts/build-palette-removal.py) is a bounded
patch on the help-pages candidate. Every site is authenticated against its
expected bytes.

- **Heap end:** the literals at `0x1103DC4/DE0/DFC` go back to `0x0203F000`,
  returning the 12 KiB to the native heap.
- **Heap-setup hook:** the hook at `0x11D0714` keeps its endpoint check. Its
  single call now resets only the party-heap record, instead of calling the
  palette reset (which used to reset that record as part of its work).
- **Art heap helpers that stay:** the shared party heap and the low-address
  battle workspace placement. Their limits are raised from `0x0203C000` to
  `0x0203F000`, and their 16-byte record moves from `0x0203EFF0` (now heap) to
  the unused `0x0203F200`. That is past Passing Step (`0x0203F000..F15B`) and
  outside the diagnostics window `0x0203F220..0x0203F3FF` (an earlier candidate
  used `0x0203F3E0`, inside that window).
- **Compact Status retired:** the native party constructor entries at
  `70688/71138/711CC` are restored. Every party context uses the full `0x9980`
  context with the list tail at `+0x7280`. The mode-1 display buffer shrinks
  from `0x2800` to `0x1E00` bytes. The measured peak is 5,920 bytes, reached by
  the Equip Items list with every item owned; battle Status peaks at 2,592.
  With that buffer, the full Info screen fits the deployment heap with about
  1.1 KB to spare.
- **Code removal:** a reachability pass starts from all live references
  (pointer literals, Thumb and ARM branches, and libgcc helpers). It overwrites
  every unreachable function in the old engine reservation
  `0x1F90000..0x1FD0000` with `0xFF`: 145 functions, 155,788 bytes, including
  the whole palette engine and the compact-Status code. The code that stays is
  the party heap, workspace placement, the status-iterator speedup, Auto-Potion,
  and libgcc. Removal stops at the end of the compiled code segment
  (`0x1FB595C`); the artwork data after it is unchanged. An earlier candidate
  also erased 4,088 bytes of sprite layouts there that about 870 frames point
  at.
- **AI workspace:** the upstream inventory hack replaced every word equal to
  `0x4504` with `0x9C08`, including the AI evaluation workspace size at
  `0xBDB14`/`0xBDBC0`. Each AI evaluation then needed 39,944 contiguous bytes
  instead of 17,668. Both are restored to the native `0x4504`. This was the
  root cause of the September battle stall that the art work had patched
  around.

Artwork data and all gameplay code are unchanged. The engine's C sources remain
in `src/engine/art-palette-*` only as provenance for the historical art stages;
no current stage installs them.

## Evidence

The first 14 steps of `scripts/memory-fixes-test-plan.json` rebuild the chain
(teaching rows → equipment revision → enchant weapons → help pages → palette
removal) and rerun the 0.7.2 checks. Release acceptance is recorded in the
[memory-fixes note](memory-fixes-2026-09-25.md).

- [Static test](../scripts/test-palette-removal.py), 212 checks:
  - every changed byte is a declared patch or a removed function;
  - the AI workspace size is native, and the artwork data after the code is
    unchanged;
  - heap end and native entries are restored;
  - no palette-engine function remains;
  - no live code branches into, points at, or addresses the old reservation.
- [Real core](../scripts/test-palette-removal-ui.py), 20 checks, on a generated
  Giza battle:
  - **Deployment R Info:** at least 250 distinct screen tiles, against 103 on
    the broken screen; a valid heap with room to spare; the list at
    `+0x7280`.
  - **With every item owned ×99:** all five Equip Items lists open and scroll
    without touching the context tail. The Pick Abilities lists render.
  - **Closing Info:** the heap is restored exactly and the deployment screen
    renders.
  - **Battle start:** Start, then Yes, then the intro reach a battle turn.
  - **In-battle Status:** both panels, inspection and help work, and closing
    restores the heap.
- Teaching rows native (1,864 checks) and real core (28) pass on the final ROM.

Not covered: the larger art capacity scenarios (13 on-screen actors), campaign
playthrough and physical hardware. With 12 KiB more heap those only gain
headroom, but they were not rerun.
