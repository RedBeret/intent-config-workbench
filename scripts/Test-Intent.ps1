[CmdletBinding()]
param(
    [switch]$Bootstrap,
    [switch]$UseDocker
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Helper = Join-Path $PSScriptRoot "Invoke-Workbench.ps1"

& $Helper -Action "validate" -Bootstrap:$Bootstrap -UseDocker:$UseDocker
& $Helper -Action "health" -Bootstrap:$false -UseDocker:$UseDocker
& $Helper -Action "pytest" -Bootstrap:$false -UseDocker:$UseDocker
