Set-Location 'C:\workspace'
if (Test-Path '.\dist\calculator.exe') {
  $f = Get-Item '.\dist\calculator.exe'
  Write-Host 'FOUND'
  Write-Host 'Path:' $f.FullName
  Write-Host 'Size:' $f.Length
  Write-Host 'MTime:' $f.LastWriteTime
  $p = Start-Process -FilePath $f.FullName -PassThru
  Start-Sleep -Seconds 5
  try {
    $proc = Get-Process -Id $p.Id -ErrorAction Stop
    Write-Host '[run] Still running -> killing'
    Stop-Process -Id $p.Id -Force
    Write-Host '[run] KILLED'
  } catch {
    Write-Host '[run] Exited'
  }
} else {
  Write-Host 'NOT_FOUND'
}
