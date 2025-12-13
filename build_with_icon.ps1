Set-Location 'C:\workspace'
$ErrorActionPreference = 'Stop'
Write-Host '[icon-build] Generating calculator.ico...'
python .\generate_icon.py
if (-not (Test-Path .\calculator.ico)) { Write-Host '[icon-build] Failed to create calculator.ico'; exit 2 }

Write-Host '[icon-build] Creating clean build using calculator.ico'
# ensure venv and pyinstaller present
if (-not (Test-Path .\.venv\Scripts\pyinstaller.exe)) {
    Write-Host '[icon-build] Creating venv and installing pyinstaller/pillow...'
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install pyinstaller pillow
}

# Clean previous outputs
if (Test-Path .\dist) { Remove-Item -Recurse -Force .\dist }
if (Test-Path .\build) { Remove-Item -Recurse -Force .\build }
if (Test-Path .\calculator.spec) { Remove-Item -Force .\calculator.spec }

.\.venv\Scripts\pyinstaller.exe --clean --onefile --windowed --icon calculator.ico --add-data "click_snap.wav;." --add-data "click_thock.wav;." --add-data "click_balanced.wav;." calculator.py

if (Test-Path .\dist\calculator.exe) {
    $f = Get-Item .\dist\calculator.exe
    Write-Host '[icon-build] SUCCESS:' $f.FullName
    Write-Host '[icon-build] SIZE:' $f.Length
    Write-Host '[icon-build] MTIME:' $f.LastWriteTime
    exit 0
} else {
    Write-Host '[icon-build] Build finished but dist\calculator.exe not found'; exit 3
}
