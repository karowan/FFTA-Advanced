param(
    [switch]$SkipTests,
    [string]$Python = ''
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'scripts/resolve-python.ps1')
$Python = Resolve-FftaPython -Python $Python
$fftaRoot=$PSScriptRoot
Push-Location -LiteralPath $fftaRoot
try {
    node scripts/generate-expansion-registry.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Registry generation failed' }
    & $Python scripts/generate-status-glyphs.py
    if ($LASTEXITCODE -ne 0) { throw 'Status glyph generation failed' }
    $fftaCompiler=Join-Path $fftaRoot 'tools/arm-gnu/bin/arm-none-eabi-gcc.exe'
    & $fftaCompiler -mcpu=arm7tdmi -mthumb -Os -std=c11 -ffreestanding -fno-builtin -fno-common -Wall -Wextra -Werror -I build/expansion -nostdlib '-Wl,-T,src/engine/expansion.ld,-Map,build/expansion/engine.map' src/engine/persistent.c src/engine/battle-state.c src/engine/blade-wound.c src/engine/evaluated-units.c src/engine/inventory.c src/engine/inventory-menus.c src/engine/equipment.c src/engine/abilities.c src/engine/ability-counts.c src/engine/quin-history.c src/engine/quin-history.s src/engine/recruit-prerequisites.c src/engine/recruit-prerequisites.s src/engine/command-lists.c src/engine/job-wheel.c src/engine/combat.c src/engine/exposed-effects.c src/engine/exposed-effects.s src/engine/status-display.c src/engine/status-display.s src/engine/samurai-state.c src/engine/dark-sword.c src/engine/mobility-supports.c src/engine/physical-riders.c src/engine/gladiator-finishers.c src/engine/combos.c src/engine/combat-geometry.c src/engine/combat-area.c src/engine/projectile-los.c src/engine/unit-copies.c src/engine/runtime.c src/engine/load-hooks.s src/engine/inventory-hooks.s src/engine/text-hooks.s src/engine/equipment-hooks.s src/engine/ability-hooks.s src/engine/command-hooks.s src/engine/job-hooks.s src/engine/axe-visual-hooks.s src/engine/combat-hooks.s src/engine/dark-sword-hooks.s src/engine/mobility-supports.s src/engine/physical-riders.s src/engine/gladiator-finishers.s src/engine/command-label-hooks.s src/engine/combo-hooks.s src/engine/combat-geometry.s src/engine/combat-area.s src/engine/evaluated-units.s -lgcc -o build/expansion/engine.elf
    if ($LASTEXITCODE -ne 0) { throw 'ARM engine compilation failed' }
    & './tools/arm-gnu/bin/arm-none-eabi-objcopy.exe' -O binary build/expansion/engine.elf build/expansion/engine.bin
    if ($LASTEXITCODE -ne 0) { throw 'Binary extraction failed' }
    & './tools/arm-gnu/bin/arm-none-eabi-nm.exe' --defined-only -n build/expansion/engine.elf | Set-Content -LiteralPath build/expansion/engine.symbols
    if ($LASTEXITCODE -ne 0) { throw 'Symbol extraction failed' }
    node scripts/build-job-data-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Job data build failed' }
    node scripts/build-content-data-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Content data build failed' }
    node scripts/build-storage-probe.mjs --content --inventory-core --menus
    if ($LASTEXITCODE -ne 0) { throw 'Content inventory integration build failed' }
    node scripts/build-ability-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Ability core probe build failed' }
    node scripts/build-command-data-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Command descriptor probe build failed' }
    node scripts/build-command-core-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Command predicate probe build failed' }
    node scripts/build-action-data-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Action data integration build failed' }
    node scripts/build-job-ui-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Job wheel integration build failed' }
    node scripts/build-axe-visual-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Axe visual integration build failed' }
    node scripts/build-command-label-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Command label integration build failed' }
    node scripts/build-combo-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Combo integration build failed' }
    node scripts/build-combat-probe.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Combat integration build failed' }
    node scripts/test-hook-continuations.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Hook continuation check failed' }
    if (-not $SkipTests) {
        & './Test Expansion.ps1' -Suite full -Python $Python
    }
} finally { Pop-Location }
