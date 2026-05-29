param(
    [string]$Message = "",
    [switch]$RunChecks
)

$ErrorActionPreference = "Stop"

function Stop-Deploy {
    param([string]$Text)
    Write-Error $Text
    exit 1
}

$insideRepo = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $insideRepo -ne "true") {
    Stop-Deploy "Run this script from inside the CloudPulse git repository."
}

$branch = git branch --show-current
if ($branch -ne "main") {
    Stop-Deploy "Current branch is '$branch'. Switch to 'main' before deploying."
}

$changes = git status --porcelain
if (-not $changes) {
    Write-Host "No changes found. Nothing to deploy."
    exit 0
}

if ($RunChecks) {
    Write-Host "Running backend tests..."
    Push-Location backend
    try {
        .\.venv\Scripts\python.exe -m pytest
    } finally {
        Pop-Location
    }

    Write-Host "Building frontend..."
    Push-Location frontend
    try {
        npm run build
    } finally {
        Pop-Location
    }
}

git add -A

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "Only ignored changes found. Nothing to commit."
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Message)) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    $Message = "Update project for Railway deploy ($timestamp)"
}

Write-Host "Creating commit: $Message"
git commit -m $Message

Write-Host "Pushing to origin/main. Railway will redeploy connected services automatically."
git push origin main

Write-Host "Done. Check Railway deployments for frontend/api status."
