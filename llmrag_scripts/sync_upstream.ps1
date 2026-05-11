param(
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

git fetch upstream
$current = git branch --show-current
if ($current -ne $Branch) {
    Write-Host "Current branch is '$current'. Switch to '$Branch' before syncing upstream." -ForegroundColor Yellow
    exit 1
}

git merge "upstream/$Branch"
