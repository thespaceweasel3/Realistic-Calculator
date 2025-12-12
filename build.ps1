<#
build.ps1

Usage:
  .\build.ps1                # builds exe without icon
  .\build.ps1 -IconPath path\to\icon.ico
<#
build.ps1

Usage:
  .\build.ps1                # builds exe without icon
  .\build.ps1 -IconPath path\to\icon.ico

This script:
 - creates and activates a venv at .venv
 - installs requirements from requirements.txt
 - runs PyInstaller in --onefile --windowed mode
 - embeds the generated click WAVs into the bundle
#>
param(
    [string]$IconPath = ''
)

$ErrorActionPreference = 'Stop'
Write-Host "[build] Creating virtual environment..."
python -m venv .venv
Write-Host "[build] Activating venv..."
# Activate the venv for the remainder of the script
& .\.venv\Scripts\Activate.ps1
Write-Host "[build] Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
if (Test-Path requirements.txt) {
    pip install -r requirements.txt
} else {
    pip install pyinstaller pillow
}

# Prepare add-data arguments for PyInstaller (PowerShell + Windows: use SRC;DEST)
$addData = @(
    "click_snap.wav;.",
    "click_thock.wav;.",
    "click_balanced.wav;."
)
$addArgs = @()
foreach ($a in $addData) { $addArgs += "--add-data"; $addArgs += $a }

$script = 'calculator.py'
$argsList = @('--onefile','--windowed') + $addArgs
if ($IconPath -and (Test-Path $IconPath)) {
    $argsList += '--icon'
    $argsList += $IconPath
}
$argsList += $script

Write-Host "[build] Running PyInstaller..."
Write-Host "pyinstaller $($argsList -join ' ')"
& pyinstaller @argsList

if (Test-Path dist\calculator.exe) {
    Write-Host "[build] Build complete: dist\calculator.exe"
} else {
    Write-Host "[build] Build finished - check dist folder for output (or look at the PyInstaller log)."
}
    Write-Host "pyinstaller $($argsList -join ' ')"
