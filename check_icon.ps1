Set-Location 'C:\workspace'
$exe = Join-Path (Get-Location) 'dist\calculator.exe'
$ico = Join-Path (Get-Location) 'calculator.ico'
if (-not (Test-Path $exe)) { Write-Host 'ERROR: EXE_NOT_FOUND'; exit 0 }
Add-Type -AssemblyName System.Drawing
try {
  $icon = [System.Drawing.Icon]::ExtractAssociatedIcon($exe)
  $bmp = $icon.ToBitmap()
  $out1 = Join-Path (Get-Location) 'extracted_from_exe.png'
  $bmp.Save($out1, [System.Drawing.Imaging.ImageFormat]::Png)
  Write-Host "WROTE $out1"
} catch {
  Write-Host 'ERROR: Failed to extract icon from EXE:' $_.Exception.Message
}
if (-not (Test-Path $ico)) {
  Write-Host 'WARNING: calculator.ico not found'
} else {
  try {
    $icon2 = New-Object System.Drawing.Icon($ico)
    $bmp2 = $icon2.ToBitmap()
    $out2 = Join-Path (Get-Location) 'generated_icon.png'
    $bmp2.Save($out2, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host "WROTE $out2"
  } catch {
    Write-Host 'ERROR: Failed to convert ICO to PNG:' $_.Exception.Message
  }
}
if (Test-Path 'extracted_from_exe.png') { Get-FileHash -Algorithm SHA256 'extracted_from_exe.png' | Select-Object Hash, Path } else { Write-Host 'No extracted PNG to hash' }
if (Test-Path 'generated_icon.png') { Get-FileHash -Algorithm SHA256 'generated_icon.png' | Select-Object Hash, Path } else { Write-Host 'No generated PNG to hash' }
