Set-Location 'C:\workspace'
Write-Host 'Stopping any running calculator processes...'
Get-Process -Name 'calculator' -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }

Write-Host 'Removing dist, build, spec if present...'
Remove-Item -LiteralPath .\dist -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath .\build -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath .\calculator.spec -Force -ErrorAction SilentlyContinue

Write-Host 'Running PyInstaller (this may take a few minutes)...'
python -m PyInstaller --noconfirm --clean --onefile --windowed --icon calculator_multi.ico calculator.py

if (Test-Path '.\dist\calculator.exe') {
  Write-Host 'Build succeeded, extracting EXE icon to extracted_from_exe.png'
  Add-Type -AssemblyName System.Drawing
  try {
    $icon = [System.Drawing.Icon]::ExtractAssociatedIcon((Resolve-Path '.\dist\calculator.exe').Path)
    $bmp = $icon.ToBitmap()
    $out = Join-Path (Get-Location) 'extracted_from_exe.png'
    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host "WROTE $out"
  } catch {
    Write-Host 'ERROR extracting EXE icon:' $_.Exception.Message
  }
  
  if (Test-Path 'calculator_multi.ico') {
    Write-Host 'Converting calculator_multi.ico to generated_multi.png via Python'
    python .\convert_multi.py
  } else {
    Write-Host 'calculator_multi.ico not found'
  }

  if (Test-Path 'extracted_from_exe.png' -and Test-Path 'generated_multi.png') {
    Write-Host 'SHA256 hashes:'
    Get-FileHash -Algorithm SHA256 'extracted_from_exe.png','generated_multi.png' | Select-Object Hash,Path
  } else {
    Write-Host 'Missing images for hash comparison'
  }
} else {
  Write-Host 'BUILD_FAILED_OR_EXE_MISSING'
}
