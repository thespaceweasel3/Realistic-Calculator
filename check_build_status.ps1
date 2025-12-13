Set-Location 'C:\workspace'
Write-Host '== Build Status Check =='
$exe = Join-Path (Get-Location) 'dist\calculator.exe'
if (Test-Path $exe) {
  $f = Get-Item $exe
  Write-Host "EXE_FOUND: $($f.FullName)"
  Write-Host "Size: $($f.Length) bytes"
  Write-Host "MTime: $($f.LastWriteTime)"
} else {
  Write-Host 'EXE_NOT_FOUND'
}

$py = Get-Process -Name python -ErrorAction SilentlyContinue
if ($py) {
  Write-Host "Python processes running ($($py.Count)):"
  $py | Select-Object Id,ProcessName,StartTime | Format-Table -AutoSize
} else {
  Write-Host 'No python processes'
}

$log = Join-Path (Get-Location) 'build_pyinstaller.log'
if (Test-Path $log) {
  Write-Host '--- build_pyinstaller.log (tail 120 lines) ---'
  Get-Content -Path $log -Tail 120
} else {
  Write-Host 'No build_pyinstaller.log'
}

$warn = Join-Path (Get-Location) 'build\calculator\warn-calculator.txt'
if (Test-Path $warn) {
  Write-Host '--- build\calculator\warn-calculator.txt (tail 40 lines) ---'
  Get-Content -Path $warn -Tail 40
} else {
  Write-Host 'No PyInstaller warnings file found yet'
}
