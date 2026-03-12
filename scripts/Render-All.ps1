[CmdletBinding()]
param(
    [switch]$Bootstrap,
    [switch]$UseDocker,
    [switch]$Demo
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Action = if ($Demo) { "demo" } else { "render" }
& (Join-Path $PSScriptRoot "Invoke-Workbench.ps1") -Action $Action -Bootstrap:$Bootstrap -UseDocker:$UseDocker
