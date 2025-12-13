Set-Location 'C:\workspace'
$exe = 'C:\workspace\dist\calculator.exe'
Write-Host "[lock-check] Looking for processes using $exe"
$procs = Get-CimInstance Win32_Process | Where-Object { ($_.ExecutablePath -ne $null -and $_.ExecutablePath -ieq $exe) -or ($_.CommandLine -and $_.CommandLine -like '*calculator.exe*') }
if ($procs -and $procs.Count -gt 0) {
    Write-Host "[lock-check] Found processes:"
    $procs | Select-Object ProcessId,ExecutablePath,CommandLine | Format-List
    foreach ($p in $procs) {
        try {
            Write-Host "[lock-check] Stopping pid $($p.ProcessId)"
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Host "[lock-check] Failed to stop pid $($p.ProcessId)"
        }
    }
} else {
    Write-Host '[lock-check] No matching processes found'
}
