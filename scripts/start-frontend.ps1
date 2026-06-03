param(
    [switch]$Install
)

$ErrorActionPreference = 'Stop'

$npmCmd = 'C:\Program Files\nodejs\npm.cmd'
if (-not (Test-Path $npmCmd)) {
    throw "npm.cmd was not found at $npmCmd. Install Node.js LTS first."
}

$frontendDir = Join-Path $PSScriptRoot '..\frontend'
Push-Location $frontendDir
try {
    if ($Install -or -not (Test-Path 'node_modules')) {
        & $npmCmd install
    }

    & $npmCmd run dev
}
finally {
    Pop-Location
}