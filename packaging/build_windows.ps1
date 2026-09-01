# Build the standalone Windows desktop app.
#
# Prereqs (once):  pip install -r packaging/requirements.txt
# Run from anywhere:  powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
# Output:  "dist\LeetCode Gym.exe"   (double-click to run)
$ErrorActionPreference = "Stop"

# Repo root = parent of this script's folder.
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

# Keep PyInstaller's deep work tree in a SHORT temp path — the repo may sit in a
# Dropbox folder (sync locks) and/or exceed Windows' 260-char MAX_PATH.
$work = Join-Path $env:TEMP "gym-build"

pyinstaller --noconfirm --clean --distpath dist --workpath $work `
    packaging\LeetCodeGym.spec

Write-Host ""
Write-Host "Built: $repo\dist\LeetCode Gym.exe"
