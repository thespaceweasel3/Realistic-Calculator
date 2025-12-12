<#
init_repo.ps1

Usage:
  .\init_repo.ps1 -RepoName "Seven-Segment-Calculator" -Public

This script will:
 - initialize a git repository (if not already)
 - add all files and make an initial commit
 - if `gh` CLI is available and authenticated, create a GitHub repo and push
 - otherwise prints the commands you can run manually to push
#>
param(
    [string]$RepoName = 'Seven-Segment-Calculator',
    [switch]$Public
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path .git)) {
    Write-Host "[git] Initializing repository..."
    git init
} else {
    Write-Host "[git] Repository already initialized."
}

Write-Host "[git] Adding files and committing..."
git add .
try {
    git commit -m "Initial commit - Seven Segment Calculator"
} catch {
    Write-Host "[git] Commit may have failed (nothing to commit or author not configured)."
}

# If gh is available, try to create and push the repo
try {
    $ghPath = (Get-Command gh -ErrorAction Stop).Source
    Write-Host "[gh] gh CLI detected: $ghPath"
    $vis = 'public'
    if ($Public) { $vis = 'public' } else { $vis = 'private' }
    Write-Host "[gh] Creating repo '$RepoName' ($vis) and pushing..."
    # create and push in one command
    gh repo create "$RepoName" --$vis --source=. --remote=origin --push
    Write-Host "[gh] Repo created and pushed to GitHub."
} catch {
    Write-Host "[gh] gh CLI not found or failed. To create and push the repo manually, run the following commands:"
    Write-Host ""
    Write-Host "git remote add origin https://github.com/<your-user>/$RepoName.git"
    Write-Host "git branch -M main"
    Write-Host "git push -u origin main"
}
