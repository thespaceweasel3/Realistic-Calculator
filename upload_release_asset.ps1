# Uploads dist\calculator.exe to a GitHub release (replaces existing asset with same name)
# Usage (PowerShell):
#   $env:GITHUB_TOKEN = '<your-personal-access-token-with-repos>'
#   .\upload_release_asset.ps1 -Owner 'thespaceweasel3' -Repo 'Realistic-Calculator' -Tag 'v1.0.0'

param(
  [string]$Owner = 'thespaceweasel3',
  [string]$Repo = 'Realistic-Calculator',
  [string]$Tag = 'v1.0.0',
  [string]$AssetPath = '.\\dist\\calculator.exe',
  [string]$AssetName = 'calculator.exe'
)

if (-not (Test-Path $AssetPath)) {
  Write-Error "Asset file not found: $AssetPath"
  exit 2
}

$token = $env:GITHUB_TOKEN
if (-not $token) {
  Write-Error 'GITHUB_TOKEN environment variable is not set. Set it before running this script.'
  Write-Host "Example: `$env:GITHUB_TOKEN = '<your-token>' ; .\\upload_release_asset.ps1 -Owner '$Owner' -Repo '$Repo' -Tag '$Tag'"
  exit 3
}

$baseApi = "https://api.github.com/repos/$Owner/$Repo"
$headers = @{
  Authorization = "Bearer $token"
  Accept = 'application/vnd.github+json'
  'User-Agent' = 'upload-release-asset-script'
}

Write-Host "Fetching release for tag '$Tag'..."
try {
  $release = Invoke-RestMethod -Uri "$baseApi/releases/tags/$Tag" -Headers $headers -Method Get -ErrorAction Stop
} catch {
  Write-Error "Failed to fetch release for tag $Tag: $($_.Exception.Message)"
  exit 4
}

$releaseId = $release.id
Write-Host "Found release id: $releaseId (name: $($release.name))"

# Check for existing asset with same name
Write-Host 'Checking existing assets...'
$assets = Invoke-RestMethod -Uri "$baseApi/releases/$releaseId/assets" -Headers $headers -Method Get
$existing = $assets | Where-Object { $_.name -eq $AssetName }
if ($existing) {
  Write-Host "Found existing asset '$AssetName' (id: $($existing.id)). Deleting..."
  try {
    Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/releases/assets/$($existing.id)" -Headers $headers -Method Delete -ErrorAction Stop
    Write-Host 'Deleted existing asset.'
  } catch {
    Write-Error "Failed to delete existing asset: $($_.Exception.Message)"
    exit 5
  }
} else {
  Write-Host 'No existing asset with that name.'
}

# Upload the new asset
Write-Host "Uploading new asset: $AssetPath"
$uploadUrl = "https://uploads.github.com/repos/$Owner/$Repo/releases/$releaseId/assets?name=$AssetName"
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $AssetPath))
$headersUpload = @{
  Authorization = "Bearer $token"
  Accept = 'application/vnd.github+json'
  'User-Agent' = 'upload-release-asset-script'
  'Content-Type' = 'application/octet-stream'
}

try {
  $resp = Invoke-RestMethod -Uri $uploadUrl -Headers $headersUpload -Method Post -Body $bytes -ErrorAction Stop
  Write-Host "Upload complete. Asset URL: $($resp.browser_download_url)"
} catch {
  Write-Error "Upload failed: $($_.Exception.Message)"
  if ($_.Exception.Response) {
    try { $errText = (New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())).ReadToEnd(); Write-Host 'Response:'; Write-Host $errText } catch { }
  }
  exit 6
}
