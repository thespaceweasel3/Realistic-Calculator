# build_fresh.ps1 - Clean build script for calculator.exe
# Removes previous build artifacts, ensures venv has pyinstaller/pillow, and runs a clean PyInstaller build.

Set-Location -LiteralPath "C:\workspace"
$ErrorActionPreference = 'Stop'
Write-Host "[fresh-build] Cleaning previous build artifacts..."
if (Test-Path .\dist) { Remove-Item -Recurse -Force .\dist }
if (Test-Path .\build) { Remove-Item -Recurse -Force .\build }
if (Test-Path .\calculator.spec) { Remove-Item -Force .\calculator.spec }

# Ensure venv exists
if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    Write-Host "[fresh-build] Creating virtual environment .venv..."
    python -m venv .venv
}

Write-Host "[fresh-build] Upgrading pip and installing PyInstaller+Pillow into venv..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install pyinstaller pillow --disable-pip-version-check -q

# Build with PyInstaller (clean)
Write-Host "[fresh-build] Running PyInstaller (clean, onefile, windowed)..."
.\.venv\Scripts\pyinstaller.exe --clean --onefile --windowed --add-data "click_snap.wav;." --add-data "click_thock.wav;." --add-data "click_balanced.wav;." calculator.py

if (Test-Path .\dist\calculator.exe) {
    $f = Get-Item .\dist\calculator.exe
    Write-Host "[fresh-build] SUCCESS: $($f.FullName)"
    Write-Host "[fresh-build] SIZE: $($f.Length)"
    Write-Host "[fresh-build] MTIME: $($f.LastWriteTime)"
    exit 0
} else {
    Write-Host "[fresh-build] Build finished but dist\calculator.exe not found. Check build\ and warn-calculator.txt"
    if (Test-Path .\build\calculator\warn-calculator.txt) { Write-Host "--- last 200 lines of warn-calculator.txt ---"; Get-Content .\build\calculator\warn-calculator.txt -Tail 200 }
    exit 2
}
