# Shared interpreter selection for developer entry points. Does not install tools.
function Resolve-FftaPython {
    param([string]$Python = '')
    if (-not $Python) { $Python = $env:FFTA_PYTHON }
    if ($Python) {
        $fftaCommand = Get-Command $Python -CommandType Application -ErrorAction SilentlyContinue
        if (-not $fftaCommand) { throw 'Python was not found. Set FFTA_PYTHON to a Python 3.11+ executable.' }
        return $fftaCommand.Source
    }
    foreach ($fftaName in @('python', 'python3')) {
        $fftaCommand = Get-Command $fftaName -CommandType Application -ErrorAction SilentlyContinue
        # The Windows Store alias is not an installed Python interpreter.
        if ($fftaCommand -and $fftaCommand.Source -notmatch '[\\/]WindowsApps[\\/]') {
            return $fftaCommand.Source
        }
    }
    # Optional compatibility with the original local authoring environment.
    if ($env:USERPROFILE) {
        $fftaBundled = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
        if (Test-Path -LiteralPath $fftaBundled -PathType Leaf) { return $fftaBundled }
    }
    throw 'Python was not found. Install Python 3.11+ or set FFTA_PYTHON to its executable.'
}
