Set-Location 'C:\workspace'
if (Test-Path .\dist\calculator.exe) {
    $f = Get-Item .\dist\calculator.exe
    Write-Host 'FOUND'
    Write-Host 'Path:' $f.FullName
    Write-Host 'Size:' $f.Length
    Write-Host 'MTime:' $f.LastWriteTime
    Write-Host '[run] Launching EXE for 6s...'
    $p = Start-Process -FilePath $f.FullName -PassThru
    Start-Sleep -Seconds 6
    $p.Refresh()
    if (-not $p.HasExited) {
        Write-Host '[run] Still running -> stopping process'
        Stop-Process -Id $p.Id -Force
        Write-Host '[run] KILLED'
    } else {
        Write-Host '[run] Exited code:' $p.ExitCode
    }
} else {
    Write-Host 'NOT_FOUND'
}
