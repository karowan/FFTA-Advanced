# Final Fantasy Tactics Advance Modding Guide

**Current project decision:** build our own expansion on vanilla USA FFTA, with the [approved vanilla+ foundation](VANILLA-PLUS-PACKAGE.md). No existing overhaul is our base. The mod comparisons and suggested sampling sequence below are earlier research, not instructions to replace this approved direction.

## Recommended starting point

For Windows, start with **standalone mGBA, a clean US game dump, and one mod per game file**. Use Rom Patcher JS to apply a downloaded patch, then open the resulting `.gba` file in mGBA. Keep your original game file and each playthrough's saves separate. The official mGBA download page currently lists **0.10.5**, including a Windows 64-bit portable edition.[^1][^2]

The most useful choices are:

| What you want | First choice | Main tradeoff |
|---|---|---|
| A substantial gameplay rebalance | **Maeson 1.2.1** | Changes the progression and combat systems considerably |
| Unusual playable characters and experimentation | **Secret Starters 3.3.8** | Designed around expanded options and power fantasy; many teams require discovery |
| Mostly the original game, without laws | **Anarchy** | A narrow change rather than a general improvement package |
| Fewer missable abilities and characters | **Minimalist Completionist** | Does not attempt to redesign the entire mission-item system |
| A monster-collecting campaign | **Final Fantasy Tactics Advanced Battle 1.3.1** | Replaces normal recruitment with a different party-building loop |
| A shuffled replay | **TojiKitten's FFTA Randomizer** | Settings and generated output need their own testing |

These recommendations are judgments based on the authors' documented designs, not a ranking established by comparative playtesting. Detailed evidence and limitations follow.[^3][^4][^5][^6][^7][^8]

**Suggested sequence:** play a few missions of Maeson to sample a modern overhaul; keep a separate Anarchy or unmodified game for comparison; then make one small custom edit in AIO. That gives you a concrete sense of what you want to change before committing to a large mod.

## 1. How FFTA mods work

This guide covers **Final Fantasy Tactics Advance for Game Boy Advance**. The tools and patches for Final Fantasy Tactics on PlayStation/PSP and Final Fantasy Tactics A2 on Nintendo DS are separate. In particular, the readily searchable FFTA2 Editor is not the editor needed here. The FFTA community maintains its own editor and mod indexes.[^9][^10]

A typical mod is distributed as a **patch**: a file describing changes to a particular original game image. Applying it produces a modified game image. A ROM is the game file; a patch is the set of changes; an emulator runs the resulting game; a save records your progress.

```text
Clean FFTA game dump + selected mod patch
                    |
              ROM patcher
                    |
          Modified FFTA .gba file
                    |
                  mGBA
                    |
         Separate playthrough saves
```

There is generally no universal FFTA mod manager that resolves conflicts between arbitrary patches. Treat every overhaul as a separate game build. Randomizers and editors are another route: they generate or modify the game file directly rather than merely applying a fixed downloaded patch.

Rom Patcher JS supports IPS, UPS, BPS, and several other formats, and can both apply and create patches. It also displays file hashes, which are fingerprints used to identify the exact input file.[^2]

Use a clean dump you are entitled to use. This guide links to patch distributions and tools; it does not supply the original game.

### The base game must match

The currently inspected Maeson, Secret Starters, and Advanced Battle release pages identify the same input fingerprints:[^3][^4][^7]

| Field | Expected value for those releases |
|---|---|
| Game/region | Final Fantasy Tactics Advance, USA; older naming also says USA, Australia |
| SHA-1 | `4AC05441F4DE70A4EC3DD932116346C61B8783D9` |
| CRC32 | `5645E56C` |

Data Crystal separately identifies the US game code as `AFXE`, the European code as `AFXP`, and the Japanese code as `AFXJ`; the original ROM is listed as 16 MiB. The code or filename alone is not sufficient to establish that the complete file matches.[^11]

On Windows, this read-only command checks the SHA-1 once your clean dump is at the example location:

```powershell
Get-FileHash -Algorithm SHA1 -LiteralPath 'roms/clean/FFTA_US_clean.gba'
```

Hash the extracted `.gba`, not the ZIP containing it. If the hash differs, identify the difference before patching: another region, an existing patch, a modified dump, or a different revision can all matter. Renaming a file cannot change its contents.

The selected patch's own documentation takes precedence over this common baseline. For example, the Minor Tweak Pack mirror currently displays a CRC32 inconsistent with the US baseline and marks its hashes unverified. Do not copy that field into a build specification without reconciling it.[^12]

## 2. Installing and playing a mod on Windows

### Set up the emulator

Download the **Windows 64-bit portable** mGBA package from the official download page and extract it into a writable folder. A portable setup is convenient for keeping the emulator version alongside the modding project. You can also use the official installer; the important point is keeping games and saves somewhere writable.[^1][^13]

Open the clean game first. Confirm that you can reach gameplay, make a normal in-game save, close the emulator, reopen the game, and continue. This establishes a baseline before adding a mod.

mGBA provides a built-in BIOS implementation, remappable keyboard/gamepad controls, fast-forward, save states, and debugging support. A separate BIOS file is therefore not a general prerequisite for this starting workflow. Its documented default keys include **X for A**, **Z for B**, **Enter for Start**, **Backspace for Select**, **A/S for L/R**, and **Tab for fast-forward**; bindings can be changed.[^14]

### Apply the patch

1. Open the selected mod's original release page from the comparison section below.
2. Download its patch archive and extract it. Read the included instructions, version notes, required input hash, and any new-game requirement.
3. Open [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/).
4. In the ROM field, select your clean `.gba` file. Compare its displayed fingerprint with the mod's required input.
5. In the patch field, select the actual `.bps`, `.ups`, or `.ips` file from the archive.
6. Apply the patch and save the output with an explicit name, such as `FFTA_Maeson_1.2.1.gba`.
7. If the author supplies optional patches, follow that package's instructions for applying them to the main patched output. Record which options you choose.
8. Open the final `.gba` in mGBA. Start a new game for an overhaul unless the author explicitly supports the old save.
9. Complete an early battle, visit relevant menus, save normally, fully close mGBA, and verify that Continue works after reopening.

The patcher's supported formats and hash display are documented by its developer.[^2] The verification steps are a recommended workflow, not evidence that a particular mod has already passed them on this computer.

Although mGBA can load patches itself, producing a clearly named patched game file makes the exact build easier to identify and move between setups.[^14] Avoid accidentally applying the same patch again through an emulator's patch-loading feature.

### A concrete Maeson setup

Use the release page's **1.2.1** archive. Prefer its main BPS patch for the first build. Apply it to the clean US input above, then try the main mod before selecting optional variants. The author provides optional IPS patches and specifically added a no-laws option; use that included option if desired instead of importing an unrelated law-removal patch.[^3]

Suggested final names are `FFTA_Maeson_1.2.1.gba` and, if selected, `FFTA_Maeson_1.2.1_NoLaws.gba`. These are suggested filenames, not names guaranteed to appear in the download.

### Protect saves when trying several mods

Use a separate directory and filename for every mod/version/option combination. Keep ordinary in-game saves as well as occasional emulator save states. Treat save states as temporary checkpoints tied to a particular build; when switching game versions, use a fresh boot and follow the author's save-migration guidance.

Secret Starters explicitly warns against transferring older-version saves across major changes, using unsupported outside patches, and assuming original-game cheat codes are compatible.[^4] Apply the same conservative approach when experimenting with a mod that changes jobs, ability storage, or recruitment.

mGBA's FAQ identifies protected directories such as Program Files as a cause of saving problems. Store the games under this project or another normal user directory.[^13]

## 3. Choosing an existing mod

### Maeson: the first overhaul to evaluate

**Verified listing:** version **1.2.1**, released **June 5, 2026**. [Original release page](https://www.romhacking.net/hacks/9373/).

Its design emphasizes useful abilities, equipment choices, and job variety. Major changes include JP-based ability purchasing, revised job growths, equipment organized around story progression, reworked enemy formations, and enemy levels tied to your strongest unit. Dispatch progression is reorganized, and access to the later story no longer requires all 300 numbered quests. Laws are revised; an included optional patch removes them.[^3]

**Recommendation:** choose it if you want to reconsider your builds throughout a full campaign. Because enemies scale, grinding one overleveled carry is a poor fit for the author's intended experience. The practical appeal is its coherent set of changes, rather than having to assemble a stack of separate patches.

### Secret Starters: characters, secrets, and experimentation

**Verified listing:** version **3.3.8**, released **August 22, 2026**. [Original release page](https://www.romhacking.net/hacks/9062/).

This is much more than replacing the initial party. It includes playable story characters, JP purchases, no laws/judges, altered abilities, hybrid jobs, and skipped opening tutorials. The author describes 100 starters across 17 teams, with most requiring discovery; not all are available immediately. The optional Mission Cleanup changes quest-item progression. Hard Mode is described as unfinished.[^4]

**Recommendation:** choose it for novelty and a powerful, unusual clan. It is the most direct fit if the excitement is playing with characters who normally cannot join. Preserve the discovery aspect unless you actively want spoilers. Use only its included patches, and start a separate save for the selected release.

### Anarchy: a focused law-removal patch

[Original author thread and attachment](https://ffhacktics.com/smf/index.php?topic=8620.0).

Eternal's original post describes a deliberately small patch removing the laws. This is the clearest starting point if that single system is what stops you enjoying the original game.[^5]

Do not assume this also enables permanent death, installs a new job system, or implements the behavior of another mod with judge removal. Leonarth's separate engine configuration explicitly treats judge removal and its permanent-death options independently.[^16]

### Completion-focused options

| Patch | What it addresses | Why the distinction matters |
|---|---|---|
| [Minimalist Completionist](https://ffhacktics.com/smf/index.php?topic=11972.0) | Selected recruitment lockouts, disappearing monster ability sources, and access to certain ability-bearing equipment | A narrow way to preserve access to content |
| [Mission Item Fix 1.0a](https://ffhacktics.com/smf/index.php?topic=10721.0) | Removes many surplus quest items, adjusts mission rewards, adds missable equipment, and increases story AP rewards | More extensive changes to rewards and progression |
| [Minor Tweak Pack](https://romhackplaza.org/romhacks/ffta-minor-tweak-pack-game-boy-advance/) | Alternate initial party, different starting jobs for Marche, and a Missing Items component | A selection of small changes, not automatically a single required bundle |

The first two descriptions come from their authors; the third is Chronosplit's listing.[^6][^17][^12] The Minor Tweak Pack page currently has contradictory hash metadata and its text view says no download files were found, so the original package still needs to be located and checked before choosing it.

For a mostly original campaign, evaluate **one** completion patch first. Combining all three would duplicate or overlap changes. Neither a small file size nor the label “quality of life” establishes compatibility.

### Advanced Battle: a different party-building game

**Verified listing:** version **1.3.1**, release date **August 16, 2020**. [Original release page](https://www.romhacking.net/hacks/4438/).

Leonarth's mod makes monster taming central: Capture Orbs recruit monsters as active party members, humanoid recruitment is restricted, and monsters learn abilities using JP. Later updates added starting monsters, nicknames, and fixes. The author reports full completion became possible from version 1.1.[^7]

**Recommendation:** choose it when you want the largest change in how a clan is assembled. Keep a fresh save and learn its progression rules from the included readme rather than applying vanilla recruitment advice.

### Grim Grimoire: an older, ambitious rebalance

**Verified author thread:** **Beta 0.993**, with the first post last edited **August 31, 2015**. [Original thread](https://ffhacktics.com/smf/index.php?topic=9817.0).

It features fixed laws per encounter, scaling enemies, reduced AP requirements, six replacement jobs, tougher monsters/bosses, and postgame rematches. The author flags inaccurate tooltips and provides an external ability guide.[^18]

**Recommendation:** an interesting later comparison, but not the default first choice when getting a clean Windows setup working. The thread still labels it beta. Old claims that it is the most extensive FFTA mod should not be treated as a current comparison against 2026 releases.

### A Shattered Dream: promising, with a release trap

[Author thread and current download instructions](https://ffhacktics.com/smf/index.php?topic=13029.0).

The overhaul changes jobs, abilities, enemy formations, mission chains, and the level cap. However, the author specifically says **not to use the attached 1.022 ZIP**, because it has bugs and cannot be fully cleared, and instead points to a corrected Dropbox distribution. The thread title still says 1.022. Follow the release post, not the title.[^19]

The author also lists crashes in Delta, Pizzaboy, MyBoy, and JohnGBA and recommends RetroArch for affected users. This does **not** identify a tested Windows core/version, nor prove that current standalone mGBA can finish the corrected release. The exact corrected package version and Windows completion compatibility remain to be verified.[^19]

### Randomizers and other experiments

[TojiKitten's randomizer releases](https://github.com/TojiKitten/FFTA-randomizer/releases) list **3.2.6** as latest. Release notes document party/race, ability, equipment, enemy, and mission-related options across versions, plus recommended Nuzlocke settings.[^8] Save the tool version, settings export, seed if available, and output hash with each run. Generate from the supported clean base; do not assume it can randomize a separate overhaul safely.

The older community index also points to **Long Night**, **FFTA+**, **Final Fantasy TicTacs Advance**, and a separate FFT-like death patch. These are additional leads, not independently validated recommendations here. Its “current” index was last edited in November 2024 and omits newer releases discussed above.[^10]

## 4. Which tools to use for making mods

### Start with existing-data editing

**Darthatron's FFTA All In One (AIO)** is the main starting editor. Its original thread is titled v0.7, but its first post was updated on **May 22, 2026** to restore attachments: `FFTA_AIO_2020.zip`, `FFTA_Logic.zip`, and `FFTA_AIO_Source.zip`. The note says these were the latest files posted to Discord in 2023; the reattachment date is not evidence of a newly developed 2026 version.[^15]

The thread confirms A-ability editing and discusses job, race, item, and formation editing. It provides a more approachable entry into changing existing records than writing machine code. Download the package and inspect its included instructions before deciding whether companion files are required. Successful launch and editing on this Windows machine remain untested.

### Tool selection by task

| Desired change | Tool/resource | Practical starting scope |
|---|---|---|
| Item stats, job data, ability properties, formations | [FFTA AIO](https://ffhacktics.com/smf/index.php?topic=9764.0) | Edit one existing record in a clean copy |
| Data fields covered by specialized modules | [FlamingZelda's updated Nightmare modules](https://ffhacktics.com/smf/index.php?topic=13028) and the [editor index](https://ffhacktics.com/smf/index.php?topic=11996.0) | Use a module only after checking its target layout |
| Names, descriptions, other text | [Victotem's text editing toolkit](https://ffhacktics.com/smf/index.php?topic=12963.0) | One short string, then confirm all affected screens |
| JP learning, job/race changes, sorting, death rules | [Leonarth's Engine Hacks](https://github.com/LeonarthCG/FFTA_Engine_Hacks) | A controlled build with explicitly chosen options |
| Custom title screen | [SpeedySnail's Title Screen Injector](https://ffhacktics.com/smf/index.php?topic=13409.0) | A 240×160 image and a verified free-space location |
| Maps, map data, compression experiments | [spiiin's FFTAUtils](https://github.com/spiiin/FFTAUtils) | Research tools requiring separate practical evaluation |
| Understanding runtime behavior | [mGBA](https://github.com/mgba-emu/mgba), [FlamingZelda's notes](https://ffhacktics.com/smf/index.php?topic=13028) | Reproduce a single behavior, inspect, change, retest |
| Exporting a distributable patch | [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) | Compare the original game with the finished modified game |

Sources establish the tools' existence and advertised scope; they do not establish that every combination is compatible.[^2][^9][^14][^15][^20][^21][^22][^23][^24]

**Graphics and music are separate workflows.** The editor index links to Tile Molester, sprite limitations, and a music-change guide. A sprite is not just a single picture: battle poses, animation expectations, palettes, and data placement matter. Treat replacing an existing asset as an earlier milestone than adding a wholly new animated job.[^9]

The title-screen tool is unusually approachable. Its author advertises image conversion, preview, automatic pointer updates, and output to a patched copy. But its default storage offset is a placeholder. Do not accept an overwrite warning without locating suitable space; “creates a copy” protects the original file, not the correctness of the output.[^22]

## 5. A realistic first custom mod

The following is a recommended exercise, not an already implemented patch.

**Goal:** change one early weapon's displayed attack statistic by a small amount, while retaining every other aspect of the original game.

1. Copy the verified clean game to a work-in-progress folder.
2. Open that copy in AIO and locate the weapon in its item editor.
3. Record the original numeric value and the specific field name.
4. Increase it modestly, for example by two, and save to a new output file.
5. Open the output in mGBA, obtain/equip the item, and confirm the displayed change.
6. Exercise it in battle. Do not require damage to rise by exactly two: the relationship depends on the game's calculation and target defenses.
7. Make a normal save, restart, and verify that the item and the save still behave correctly.
8. Compare original and modified files, record the changed ranges, and create a BPS patch.
9. Apply that patch to another fresh clean copy and confirm the rebuilt output has exactly the same SHA-256 as the tested modified file.

Use vanilla for this exercise. A mod that changes damage formulas may deliberately stop using the field you are trying to learn about. A successful edit therefore requires a visible and behavioral check, not merely the editor saying it saved.

Once that works, select one bounded next project: reduce AP cost for a particular ability; change a single starting unit; adjust one early formation; or improve a description to reflect changed mechanics. Avoid combining several changes before understanding which one produced the observed result.

### Designing a personal rebalance

Write a small specification before editing. For each change, record the problem, the intended player behavior, the smallest alteration that could produce it, and a test that might disprove your assumption.

For example, “this job feels useless” is too broad. “This job should contribute a useful action in the first two turns of an early battle” is testable. A lower MP cost, different starting equipment, or altered range may solve that without increasing all its stats.

A useful first release has three to five related changes and a short changelog. If each change cannot be explained independently, the experiment is probably too large to diagnose comfortably.

## 6. Building deeper engine modifications

Leonarth's project provides assembly sources, precompiled components, and Event Assembler installation files. Its documented procedure is to obtain Event Assembler and the linked ColorzCore, replace the assembler's core as instructed, place a clean US ROM named `FFTA_clean.gba` at the project root, configure `ROM Buildfile.event`, and build `FFTA_hack.gba`. Job/race customization is a required foundation of this project, not an optional standalone toggle.[^21]

The actual script is named **`MAKE HACK.cmd`**, with a space, although the README refers to `MAKE_HACK.cmd`. It copies the clean input, calls the assembler, and then runs an optional UPS generation step. The script invokes Event Assembler in `FE8` mode; that is the project's actual assembler command, not an instruction to supply a Fire Emblem ROM.[^25]

### Configuration details that matter

The inspected buildfile enables JP learning, movement abilities, quick start, and several other changes by default. Movement abilities replace combos. The one-bit ability option changes ability storage and depends on JP learning; custom naming depends on that storage option. Judge removal is separate from permanent-death settings.[^16]

Consequently, “compile the project with defaults” is already a gameplay decision. Review every active option before creating a campaign. Start fresh when experimenting with altered save representations, and do not reuse ordinary saves as evidence of correctness.

The repository has open reports about building and about shop glitches/hangs with default configuration. These are unresolved reports, not proof that every build fails, but they make a local acceptance test essential before investing in a playthrough.[^26]

### A reproducible build arrangement

Keep the original input, selected upstream revision, tool versions, your changes, and generated output identifiable. Rebuild from the same clean input each time. The diagram below is a recommended architecture; exact editor/export support determines the implementation.

```text
Verified clean game
       |
Documented data edits / exported data
       |
Selected engine modules and settings
       |
Text and graphics insertion with reserved storage
       |
Final game image -> gameplay checks -> release patch
```

**Do not edit an engine-modified game with an old editor on faith.** If an engine hack relocates a table, changes its size, or repurposes bits, an editor that assumes vanilla locations can write the wrong place. Verify a no-change open/save first, then inspect the differences from one deliberate edit. Unexpected broad changes need explanation before proceeding.

Record all inserted data ranges. A free-space address appropriate for a clean game may already be occupied by another patch. Patch size is not a measure of conflict risk: a tiny change to a shared routine can conflict with a large overhaul.

## 7. New stories, maps, and smarter enemies

Changing numbers and existing encounters is substantially more accessible than authoring a whole new campaign. Do not interpret that as “story editing is impossible.” FlamingZelda's September 2025 event research documents an event opcode reader, 114 opcodes, and initial documentation for about 15% of them. That is real progress, but it is not a complete, friendly campaign editor.[^20]

The appropriate first event project is a very small alteration to an understood existing event, with a reproducible test. A new campaign also needs mission prerequisites, flags, battle setup, dialogue, transitions, rewards, and recovery from unusual player behavior. A script that runs once is not yet a robust campaign.

FFTAUtils contains map editing, rendering, and compression-related projects. Its existence supports deeper exploration; it does not by itself prove that a polished end-to-end custom-map workflow is ready for a beginner.[^23]

For enemy behavior, distinguish changing ability selection priorities from replacing the tactical decision-making code. FlamingZelda's notes describe weighted ability priorities, including the Fight value exposed as Aggressiveness in AIO. Raising one number does not translate directly into that percentage of turns using a skill.[^20] First adjust a single encounter and observe repeated decisions; only then decide whether assembly changes are necessary.

## 8. Compatibility and testing

### Patch combinations

| Combination | Default decision |
|---|---|
| Main mod plus that release's documented optional patches | Follow the author's prescribed order and exclusions |
| Maeson plus Secret Starters | Separate games; no compatibility established |
| An overhaul plus an unrelated “small fix” | Inspect overlap and behavior before combining |
| Randomizer plus another engine overhaul | Separate builds unless specifically supported |
| Several mods that alter quest rewards | Expect overlap; choose one or integrate the changes deliberately |
| New version plus old save | Follow the author's migration instructions; otherwise begin fresh |

BPS includes checksums for source, target, and patch. IPS is less protective about matching the input. A patch refusing an input can reveal a real mismatch; a patch accepting it does not guarantee that the result is a compatible combination.[^27]

If two independent patches both expect the clean game's bytes, neither ordering should be presumed valid. Proper integration may mean reconstructing both changes in one source build and distributing one final patch.

### Minimum checks before a serious playthrough

- Verify the input hash and record the mod version and selected options.
- Confirm the expected early changes are visible.
- Complete a battle using physical attacks, spells, and items.
- Open equipment, job, ability, shop, and mission menus.
- Change jobs and test any new ability-learning system.
- Save normally, close the emulator, and continue after reopening.
- Keep backups at meaningful progression milestones.

For a public custom mod, broaden this to representative early/middle/late battles, bosses, recruitment, death/revival, dispatch conditions, inventory limits, ending, and postgame. Test the content you changed especially closely. State exactly which emulator versions and portions of the campaign passed; do not label a mod fully compatible based on reaching its title screen.

### Troubleshooting

| Symptom | First useful checks |
|---|---|
| Patch reports wrong checksum | Extracted input hash, region, prior patches, selected patch version |
| Patched game looks unchanged | Opened the wrong output, change occurs later, existing save retains starting data |
| Save does not persist | Writable folder, save location, cold restart test |
| Crash after an update | New-game test, old save/state reuse, outside patches, cheat codes |
| Shop or ability menu hangs after a custom build | Clean baseline build, selected modules, inserted data ranges, upstream reports |
| Graphical corruption after new assets | Pointers, occupied storage, compression, palettes, required animation frames |
| Enemy behaves oddly after editing a skill | Valid targets, range, MP availability, selection priorities, animation compatibility |

mGBA offers debug facilities and a built-in bug-report tool. Useful reports identify the exact game build, emulator version, reproduction steps, and the earliest relevant save.[^13][^14] Share a patch and instructions rather than bundling the complete game.

## 9. Project organization and first milestones

The following layout is a proposal for the next setup stage. The research guide does not include downloaded game files, installed editors, or a tested mod build.

```text
<repository>/
  FFTA-MODDING-GUIDE.md
  tools\
  roms\
    clean\
    maeson-1.2.1\
    secret-starters-3.3.8\
    experiments\
  patches\
  saves\
  source\
  builds\
  notes\
```

Keep original patch archives and readmes under `patches`, editor/engine modifications under `source`, generated outputs under `builds`, and dated test results under `notes`. If version control is introduced, exclude game dumps, personal saves, and generated game images. Track your own scripts, documentation, and permitted source modifications instead.

| Milestone | Completion condition |
|---|---|
| Establish the base | Exact clean-game hash known; unmodified game saves and resumes |
| Play an existing mod | One selected release patched; early gameplay and saving verified |
| Define the personal change | A short, testable behavior specification |
| Make the first edit | One visible change passes a targeted test |
| Package it | Patch reconstructs exactly the tested output from the documented input |
| Expand carefully | Each new change has an identified purpose and relevant gameplay evidence |

**Recommended next action:** identify the clean US dump, set up mGBA, and create one Maeson build. If character novelty matters more than rebalancing, substitute Secret Starters. AIO installation and the first single-record experiment follow once the play setup is reliable.

## Sources and verification scope

Release pages and documentation were checked on **September 13, 2026, Pacific time**. Dates above refer to the specific listings or posts, not assumed file compilation dates. “Verified listing” means the author's published information was inspected; the archives, executable behavior, patch application, and complete campaigns have not been locally validated. Features and compatibility statements remain author claims until reproduced.

The old forum indexes are useful discovery maps, but their edit dates limit their completeness. Direct release posts are more authoritative for current versions. Search-result snippets and community recommendations were used to locate projects; the substantive recommendations above rely on original release pages, author threads, and tool repositories.

[^1]: mGBA project. [Downloads](https://mgba.io/downloads.html). Current page lists 0.10.5 and Windows distribution choices.
[^2]: Marc Robledo. [Rom Patcher JS repository](https://github.com/marcrobledo/RomPatcher.js) and [patcher interface](https://www.marcrobledo.com/RomPatcher.js/). Supported formats, patch creation, and displayed hashes; undated live documentation.
[^3]: Maeson. [Final Fantasy Tactics Advance: Maeson](https://www.romhacking.net/hacks/9373/). Version 1.2.1, June 5, 2026. Gameplay scope, optional patches, and input fingerprints.
[^4]: SpeedySnail. [Final Fantasy Tactics Advance — Secret Starters](https://www.romhacking.net/hacks/9062/). Version 3.3.8, August 22, 2026. Features, unlocks, optional patches, and explicit save/patch restrictions.
[^5]: Eternal. [Final Fantasy Tactics Advance: Anarchy](https://ffhacktics.com/smf/index.php?topic=8620.0). Original release thread, March 19, 2012. Law-removal scope and patch attachment.
[^6]: Taelia. [FFTA: Minimalist Completionist](https://ffhacktics.com/smf/index.php?topic=11972.0). April 10, 2018. Exact mission, monster, recruitment, and equipment changes.
[^7]: LeonarthCG. [Final Fantasy Tactics Advanced Battle](https://www.romhacking.net/hacks/4438/). Version 1.3.1, listed release August 16, 2020; page separately lists last modification August 15. Features, completion claim, and input fingerprints.
[^8]: TojiKitten/FFTA-randomizer maintainers. [Releases](https://github.com/TojiKitten/FFTA-randomizer/releases) and [3.2.6](https://github.com/TojiKitten/FFTA-randomizer/releases/tag/v3.2.6). Version and option history. The inspected text did not expose an unambiguous full release date, so none is asserted.
[^9]: Zeke_Aileron. [Current List of FFTA Editors and Modules](https://ffhacktics.com/smf/index.php?topic=11996.0). Last edited September 25, 2025. Tool discovery, graphics, music, and specialized resources.
[^10]: Zeke_Aileron. [Current Final Fantasy Tactics Advance Mods](https://ffhacktics.com/smf/index.php?topic=11997.0). Last edited November 17, 2024. Historical index and additional mod leads.
[^11]: Data Crystal contributors. [Final Fantasy Tactics Advance](https://datacrystal.tcrf.net/wiki/Final_Fantasy_Tactics_Advance). ROM identifiers, size, and regional CRC32 values; live reference.
[^12]: Chronosplit. [FFTA Minor Tweak Pack](https://romhackplaza.org/romhacks/ffta-minor-tweak-pack-game-boy-advance/). Version 1.00, listed release December 12, 2017; mirror entry posted December 5, 2024. Features and unresolved mirror metadata/download availability.
[^13]: mGBA project. [FAQs](https://mgba.io/faq.html). Windows saving, portable settings, libretro distinction, and reporting bugs; live documentation.
[^14]: mGBA project. [Repository README](https://github.com/mgba-emu/mgba). BIOS implementation, controls, patch support, and debugger capabilities; live documentation.
[^15]: Darthatron; restoration note by RetroTypes. [FFTA EDITOR: All In One v0.7 is now out!!](https://ffhacktics.com/smf/index.php?topic=9764.0). Original thread June 2, 2013; first post updated May 22, 2026. Editor scope and restored file attachments.
[^16]: LeonarthCG. [ROM Buildfile.event](https://github.com/LeonarthCG/FFTA_Engine_Hacks/blob/master/ROM%20Buildfile.event). Active configuration, option dependencies, movement/combo tradeoff, and separate law/death switches; inspected master branch.
[^17]: rrs_kai. [FFTA: Mission Item Fix 1.0a](https://ffhacktics.com/smf/index.php?topic=10721.0). Original post November 23, 2014; first post last edited December 19, 2018. Current opening-post scope and US input instruction.
[^18]: Eternal. [Final Fantasy Tactics Advance: Grim Grimoire](https://ffhacktics.com/smf/index.php?topic=9817.0). Beta 0.993; first post edited August 31, 2015. Features, patching directions, and incorrect-tooltip warning.
[^19]: FlamingZelda. [FFTA: A Shattered Dream](https://ffhacktics.com/smf/index.php?topic=13029.0). Opening/release posts updated February 28, 2026. Warning against attached 1.022, corrected external download, and emulator limitations.
[^20]: FlamingZelda. [FlamingZelda's Stuff](https://ffhacktics.com/smf/index.php?topic=13028). Updated modules and mechanics notes; AI post August 21, 2024, and event notes revised September 24, 2025. Original community reverse-engineering research.
[^21]: LeonarthCG. [FFTA Engine Hacks README](https://github.com/LeonarthCG/FFTA_Engine_Hacks). Build dependencies, required job/race foundation, and source availability; inspected master branch.
[^22]: SpeedySnail. [FFTA Title Screen Injector v1.0](https://ffhacktics.com/smf/index.php?topic=13409.0). June 20, 2026. Windows image conversion, pointer updates, image dimensions, and storage-offset caveat.
[^23]: spiiin. [FFTAUtils](https://github.com/spiiin/FFTAUtils). Repository inventory of map, rendering, and compression projects; no current usability guarantee inferred.
[^24]: Victotem. [FFTA Text editing toolkit for dummies](https://ffhacktics.com/smf/index.php?topic=12963.0). September 26, 2022. Toolkit attachment and subsequent use report by FlamingZelda.
[^25]: LeonarthCG. [MAKE HACK.cmd](https://github.com/LeonarthCG/FFTA_Engine_Hacks/blob/master/MAKE%20HACK.cmd). Actual script filename and assembler/UPS invocation; inspected master branch.
[^26]: LeonarthCG/FFTA_Engine_Hacks contributors. [Open issues](https://github.com/LeonarthCG/FFTA_Engine_Hacks/issues). Includes 2025 shop/default-build report and older build report; unresolved reports, not reproduced findings.
[^27]: Floating IPS repository. [BPS specification](https://github.com/Sir-Walrus/Flips/blob/master/bps_spec.md) and [patcher documentation](https://github.com/Sir-Walrus/Flips). BPS checksums and patch-format context; repository is archived.
