Set-Location 'C:\workspace'
Get-Process -Name 'calculator' -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
Remove-Item -LiteralPath .\dist\calculator.exe -Force -ErrorAction SilentlyContinue
$job = Start-Job -ScriptBlock {
  Set-Location 'C:\workspace'
  python -m PyInstaller --noconfirm --clean --onefile --windowed --icon calculator_multi.ico calculator.py > build_pyinstaller.log 2>&1
}
Write-Host "Started Job Id: $($job.Id)"
