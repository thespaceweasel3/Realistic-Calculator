Set-Location 'C:\workspace'
if ($env:GITHUB_TOKEN) { Write-Host 'GITHUB_TOKEN_PRESENT' }
elseif ($env:GH_TOKEN) { Write-Host 'GH_TOKEN_PRESENT' }
else { Write-Host 'NO_TOKEN' }