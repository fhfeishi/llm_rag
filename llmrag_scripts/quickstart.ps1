param(
    [Parameter(Mandatory=$true)]
    [string]$File,
    [Parameter(Mandatory=$true)]
    [string]$Query,
    [string]$Model = "",
    [string]$Workspace = ".llmrag",
    [ValidateSet("json", "markdown", "html")]
    [string]$Output = "markdown",
    [switch]$SaveIndex,
    [switch]$NoSummarize
)

$ErrorActionPreference = "Stop"

$argsList = @(
    "-m", "llmrag.cli", "ask",
    "--file", $File,
    "--query", $Query,
    "--workspace", $Workspace,
    "--output", $Output
)

if ($Model) {
    $argsList += @("--model", $Model)
}
if ($SaveIndex) {
    $argsList += "--save-index"
}
if ($NoSummarize) {
    $argsList += "--no-summarize"
}

python -B @argsList
