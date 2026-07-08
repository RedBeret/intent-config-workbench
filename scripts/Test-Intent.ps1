[CmdletBinding()]
param(
    [switch]$Bootstrap,
    [switch]$UseDocker
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Helper = Join-Path $PSScriptRoot "Invoke-Workbench.ps1"

# Use splatting to avoid colon-syntax coercion issues with SwitchParameter on
# some PowerShell versions (the runtime may stringify $true as '+' when using
# -Flag:$SwitchValue, which lands as an unrecognised positional argument).

$validateParams = @{ Action = "validate" }
if ($Bootstrap) { $validateParams['Bootstrap'] = $true }
if ($UseDocker) { $validateParams['UseDocker'] = $true }
& $Helper @validateParams

$sharedParams = @{}
if ($UseDocker) { $sharedParams['UseDocker'] = $true }
& $Helper -Action "health" @sharedParams
& $Helper -Action "pytest" @sharedParams
