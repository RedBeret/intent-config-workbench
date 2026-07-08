[CmdletBinding()]
param(
    [switch]$Bootstrap,
    [switch]$UseDocker,
    [switch]$Demo
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Action = if ($Demo) { "demo" } else { "render" }

# Use splatting to avoid colon-syntax coercion issues with SwitchParameter on
# some PowerShell versions (the runtime may stringify $true as '+' when using
# -Flag:$SwitchValue, which lands as an unrecognised positional argument).
$params = @{ Action = $Action }
if ($Bootstrap) { $params['Bootstrap'] = $true }
if ($UseDocker) { $params['UseDocker'] = $true }

& (Join-Path $PSScriptRoot "Invoke-Workbench.ps1") @params
