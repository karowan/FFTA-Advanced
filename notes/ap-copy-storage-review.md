# Council: AP copy owners and EWRAM allocation

2026-09-14. Native evidence uses clean US ROM SHA-1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`. Addresses are ROM offsets unless prefixed `020`/`030`. This is a bounded audit, not an exhaustive indirect-call proof. Engine and builder files were not edited by this reviewer. Probe ROMs and saves are isolated under `build/expansion/probes/ap-heap`.

## Decision and measured blocker

The expansion must not assume upper EWRAM is unused. Three native heap constructors clear and allocate through `02040000`. The opening name-entry screen uses the **battle constructor `227E8`**, so excluding only the separate `13C064` constructor does not avoid the opening allocation failure.

`scripts/probe-ap-copy-heap.py` patches the native clear bounds and heap bounds together, then boots mGBA through opening dialogue, name entry, confirmation and the populated Snowball scene. Heap blocks are decoded from the native linked-block headers, not estimated from nonzero bytes. At name entry the unmodified heap allocates 167,896 payload bytes and has only 5,532 free bytes. A 50,688-byte keyboard allocation fails when either 16 KiB or 24 KiB is reserved. The alphabet panel is blank in the resulting actual rendered frame. A 64 KiB reservation fails even the earlier scene.

| Reserved bytes | Heap end | Name-entry minimum free | Sampled frame comparison | Result |
|---|---|---:|---|---|
| 0 | `02040000` | 5,532 | reference | native baseline |
| 2,048 | `0203F800` | 3,484 | all 15 sampled frames equal | bounded opening test passes |
| 4,096 | `0203F000` | 1,436 | all 15 sampled frames equal | bounded opening test passes, little headroom |
| 16,384 | `0203C000` | misleading free 39,848 after failed allocation | name keyboard differs | rejected |
| 24,576 | `0203A000` | insufficient for keyboard request | name keyboard differs | rejected |

At the earlier populated opening scene the native heap uses 115,304 payload bytes, highest allocated end `02031CAC`, free 58,184. At the later sampled Snowball state it uses 112,956 payload bytes. Reserved-region canaries remain unchanged in the bounded 2/4 KiB experiments. Successful guard preservation alone does **not** prove safety: the failed 16/24 KiB experiments also preserve guards because allocations fail below them.

The format-only condition tested in `scripts/probe-conditional-heap.py` is also rejected. `FFTAEXP1` version1 already exists before the opening name screen. The current content-inventory probe initializes `020159D0..0203C000` and reproduces the missing keyboard. A fresh Python process reproduced it, excluding reused emulator-instance state as the explanation. The first six roster bytes +4/+5/+6/+7 also already equal the regular roster at title/name/Snowball: `[2,80,1,2]`, `[8,82,5,42]`, `[1,2,1,2]`, `[1,17,2,17]`, `[1,20,3,20]`, `[1,33,4,33]`. Marche character ID2/job2 is consequently not a valid phase gate either.

Preferred next integration candidate: globally reserve only 2 KiB for the 1,840-byte compatibility view, and borrow menu workspace only while party/equipment/shop contexts use their separate low heaps. Keep AP copies in explicitly enlarged native owner allocations. This removes the need to keep a global AP registry or reserve 16 KiB during the opening. The integrated relocated candidate still needs its own gameplay checks; the native-only 2 KiB experiment is not an approval of a future combined build.

## Native clear and allocator hooks

| Constructor | Start | Root global | Direct constructor caller | Exact limit instruction range |
|---|---|---|---|---|
| `227E8` | `020159D0` | `0200F434` | `23F28` | `227FC..22802` |
| `4CA00` | `0201F550` | `0201F53C` | `4C8DA` | `4CA14..4CA1A` |
| `13C064` | `0200F3C4` | `0200F3BC` | `13BF82` | `13C078..13C07E` |

Each original eight-byte sequence is `81 24 A4 04 64 1B 08 48`: set end `02040000`, subtract aligned base in r5, load clear-helper pointer `0836D4B8` into r0. A replacement must restore `r4=end-r5`, `r0=0836D4B8`, preserve r5 and saved-register ABI, then resume at `22804`, `4CA1C`, or `13C080`. These continuations clear the entire computed range before calling `070C8`; changing only `070C8` would leave the earlier clear able to erase reserved data. The exact end-construction pattern occurs only at these three sites in the scanned executable range `0..150000`.

Native `070C8` clears an eight-byte root, stores `(length-8)/4` at root+6, and creates the first free block at root+8. The linked physical block's next offset is a halfword at +2 in words relative to the heap root. Markers at +4 are `la` allocated and `ps` free. Allocated size at +6 includes its 12-byte header; free size excludes that header. The probe follows this list and validates markers/bounds.

Other direct heap initialization calls inspected: `5C16`, `A5FA`, `299AE`, `2B98C`, `30BFC`, `30C6E`, `31068`, `311B8`, `5C84E`, `710AE`, `710E2`, `7112C`, `71164`, `96BCC`, `96F10`, `97038`, `9708E`, `121E58`, `129E8A`, `137AB4`, `1479FE`. They initialize caller-provided/nested allocations or fixed lower EWRAM/IWRAM ranges. Verified fixed lower limits include `0200F390+C640=0201B9D0`, `0200F390+100D0=0201F460`, `0200F390+B880=0201AC10`, `0200F3C8+D000=0201C3C8`. `1479FE` is an IWRAM heap at `03003C68`, size `200`; its preceding clears are also IWRAM.

Party heap initialization `710AE`/`7112C` reads address from `03002778` and length from `03000E54`. Native `30BFC..30C14` explicitly allocates `C600` bytes from the `0200F390..0201B9D0` heap and publishes those globals. Actual cold-load world uses the fixed `F390..1F460` root; party/items use `F390..1B9D0`, with nested `F3A4..1B9A4` and `16604..16A04` roots. These global addresses overlap unrelated context fields in other scenes; a plausible pointer alone is not proof an old heap remains live. Likewise scanning stale root headers after a scene change does not establish a live allocation.

`13C064` has one direct caller `13BF82`, in the scene state machine `13BF5C`. It registers callbacks `13C0EC` and later `13DB34`, tears down through `13C0A8`, and can exit to scene5 via `38C8`. `13C0EC` requests a `CB70`-byte object from that heap at `13C13A`. A bounded direct-call scan of `13BF5C..140000` found no calls into the inventory getter/give/remove range `CA900..CB800`, or the reviewed item/equip/shop builders. This is evidence against a direct inventory workspace dependency in that scene, not proof about every indirect callback or linked-play path.

## AP ownership: battle snapshots

Native constructor `9DE94(snapshot,manager)` clears `E1C` bytes, stores manager at snapshot+`E18`, enumerates battle-unit pointers into snapshot+`D6C` through `99CDC`, stores count at +0, and sorts pointers by underlying unit byte+`104`. The original layout has thirteen 264-byte backup records at `snapshot+4+i*108`, ending exactly at +`D6C`. Do not change these native strides.

At `9DF42`, r0 is backup destination, r1 is exact original unit pointer (`*battleUnit`), r2 is `108`, r3 is the native copy helper. r8 retains snapshot, r4 is index, r5 is current backup. The AP hook can copy the source owner's 34 bytes into a dedicated appended slot for this exact backup pointer.

Four direct callers allocate the object through `22840`:

| Allocation call | Constructor call | Free call | Allocation-size literal |
|---|---|---|---|
| `9E874` | `9E87C` | `9E8E4` | `9E8B4` |
| `9F798` | `9F7A0` | `9F7DA` | `9F7E8` |
| `9F7FA` | `9F802` | `9F83C` | `9F848` |
| `9F85E` | `9F866` | `9F8C8` | `9F8DC` |

Each size literal is `E1C`. An appended thirteen-by-34 sidecar requires `E1C+1BA=FD6`, rounded to `FD8` for allocation. Initialize the appended tail explicitly because the unchanged constructor clears only `E1C`. Native snapshot fields after pointer list include arrays beginning `DA0` and `DD4`; their full semantics are not all mapped here. The restore path specifically copies snapshot+`DD4+4*i` back to battleUnit+`28` at `9F8A8`; do not repurpose that space.

Rollback copy at `9F89A`: destination r0 is the original `*battleUnit`, source r1 the exact backup record, r2=`108`; r6 retains snapshot, r8 index, r7 backup, r4 pointer-list entry. Restore the corresponding appended AP slot to the destination owner at the same transaction boundary. The wrapper later picks the result pointer then frees the object. The other three callers also require lifetime handling even if they never invoke this restore loop.

Owner lookup must establish that a backup pointer belongs to a currently live snapshot before computing an appended slot. Explicit active snapshot context or a scoped stack of snapshot owners is acceptable; guessing from character/job/name is not. If avoiding all fixed registry RAM, carry/derive owner from the actual snapshot call context or allocate linked owner metadata with the snapshot and keep an explicitly reserved small root. A tail allocation by itself does not solve the generic AP accessor's reverse lookup. Define and test that contract before enabling generic reads on arbitrary backup pointers.

## AP ownership: two battle temporary records

`9A9C0(manager,index)` returns `manager+40+index*108`; it does not allocate a new unit. `9A9F0` and `9AA10` recognize exactly two such pointers. Manager constructor `97000(heap)` allocates and clears `3B4` bytes, so inserting AP immediately after each native unit would overwrite another unit or live manager fields.

An exact-owner scheme can enlarge the manager allocation to `3F8` and use `manager+3B4+34*index` for the two sidecars. Parent heap construction `96ED4..96EFC` computes a fixed capacity from `22080(34)`, `14913C(1)`, constant`1668`, alignment and trailing `420`. Expanding the manager also requires explicitly budgeting its extra68 bytes in this enclosing allocation, or proving existing slack; do not assume the child heap can absorb it. Manager is published at `0200F4B0` by `96F1E`. Destructor `993F4` frees the exact manager at `99460` (`r0=heap,r1=manager`), returns its heap, and scene teardown releases the enclosing allocation at `96D48`. Clear/retire AP ownership before those frees.

The required content initialization sites are `C6D58` (null source: clear native108 bytes, also clear sidecar) and `C6D6E` (copy source to one of the exact manager slots, also copy source AP). Source comes from `context+64+4*index`; manager from context+60; index from context+78. `C6EA0` later obtains the same pointer for registration/action processing, rather than making another full-record copy. Other direct `9A9C0` callers at `2DBB8`, `2DE72`, `124666` manipulate/find these existing records; the inspected code does not make additional native full-record copies there.

## AP ownership: selection UI copy

`6529E..652A2` initializes task context[0] from `*0200F454`. The selected unit copy at `65114..65136` obtains source from this owner's pointer array at +`424`, destination at owner+`A4C`, and copies exactly `108` bytes. The copy call `6512E` is shared with a separate sixteen-byte selection case, so an unconditional unit-AP copy at that call is wrong. Limit the hook to length264 and the verified owner/destination relationship, or hook the unit-only branch before the shared call.

The owner is allocated at `64F16`: requested `E0<<6 = 3800` bytes, published at `0200F454`, clears `1704`, then initializes a nested heap of `20FC` bytes at owner+`1704`. These sum exactly to `3800`; no unused tail has been established. A safe transparent extension grows only the outer allocation to `3824`, leaves all native interior offsets and nested heap capacity unchanged, initializes the34-byte tail at +`3800`, and resolves AP only when unit pointer equals current owner+`A4C`. Owner free is `64F76`, followed by zeroing the global at `64F7C`. This gives a concrete lifetime and avoids matching a selected unit back to another record by content.

## Integration requirements still outstanding

- Re-run integrated 2 KiB reservation with relocated view/menu and verify actual shop, equip, save/cold-load, Throw/Draw and populated battle. Native-only probes establish a capacity floor, not complete compatibility.
- Restore AP with native snapshot rollback; copy-only sidecars without rollback would leak preview/simulation mutations.
- Make each appended AP tail discoverable by exact active owner. Container extension alone is insufficient if the generic accessor cannot identify its owner.
- Exercise repeated object reuse, nested snapshots, source/destination aliases, null-source clearing, and exit/free paths. Unknown owners must not borrow another unit's AP.
- Keep raw learned-byte semantics from `notes/ap-consumer-audit.md`, including equipment bit7. Deriving bit7 from a copy's gear does not replace low7 AP snapshot/restore.

## Integrated 2 KiB check and shop correction

Frozen content-inventory SHA-1 `a19ef933d927a33682af25059cfc32c535bafbd8` was tested after installing unconditional `0203F800` bounds in all three constructors and moving view to `0203F800`. Actual opening name keyboard renders correctly; name minimum free is 3,484; later Snowball sample free is 58,484. All208 guard bytes at `0203FF30..02040000` survive title, cold-load, party/items, shop, and fifteen opening/Snowball samples. Report: `build/expansion/probes/ap-heap/integrated-2k-report.json`. The separately existing `inventory-startup.gba` SHA-1 `8d6558505638d8d393585aec049661b8b9998d98` was stale, retained `02040000`, and erased that guard; its results must not be attributed to this integrated build.

**Shop borrowing was rejected by this check.** The actual shop also uses the `227E8` heap, not the party's fixed low heap. At sampled shop entry its free block begins `0202D564` and extends through `0203F800`; the temporary `0203C000` list address is inside this live allocator's free block. Snapshot used 74,052 allocated payload bytes and 97,424 free. Low usage is not ownership.

The exact safe owner extension is shop context `*0200F428`: allocation `68B06` requests `9C08` from literal`68B5C`, publishes it at`68B0A`, and clears that requested size at`68B12`. Free is`68BEC`, with global nulled at`68BF2`. Grow it by1840 to`A338` and locate list at context+`9C08`. Parent has undertaken this correction. Native literal reuse and remaining byte indices require the separate audit in `notes/shop-wide-index-review.md`; a larger list alone does not fix Sell navigation.
