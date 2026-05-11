param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8000,
    [string]$Workspace = ".llmrag_api"
)

$ErrorActionPreference = "Stop"
$env:LLMRAG_WORKSPACE = $Workspace

python -B -c "import fastapi, uvicorn, multipart" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Missing API dependencies. Run:" -ForegroundColor Yellow
    Write-Host ".\llmrag_scripts\install_llmrag_deps.ps1" -ForegroundColor Yellow
    exit 1
}

python -B -m uvicorn llmrag.server:app --host $HostName --port $Port --reload
