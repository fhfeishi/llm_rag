param(
    [Parameter(Mandatory=$true)]
    [string]$LlamaServerExe,
    [Parameter(Mandatory=$true)]
    [string]$ModelPath,
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8080,
    [int]$ContextSize = 8192,
    [int]$Threads = 8
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $LlamaServerExe)) {
    throw "llama-server executable not found: $LlamaServerExe"
}
if (!(Test-Path $ModelPath)) {
    throw "Model file not found: $ModelPath"
}

& $LlamaServerExe `
    -m $ModelPath `
    --host $HostName `
    --port $Port `
    -c $ContextSize `
    -t $Threads
