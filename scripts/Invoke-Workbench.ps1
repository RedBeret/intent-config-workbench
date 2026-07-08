[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("validate", "health", "render", "demo", "pytest")]
    [string]$Action,

    [switch]$Bootstrap,
    [switch]$UseDocker
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPath = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [string[]]$Arguments = @()
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $FilePath $($Arguments -join ' ')"
    }
}

function Invoke-PreferredPython {
    param(
        [string[]]$Arguments = @(),
        [switch]$PreferVenv
    )

    if ($PreferVenv -and (Test-Path $VenvPython)) {
        Invoke-Native -FilePath $VenvPython -Arguments $Arguments
        return
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $py) {
        Invoke-Native -FilePath $py.Source -Arguments (@("-3.12") + $Arguments)
        return
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        Invoke-Native -FilePath $python.Source -Arguments $Arguments
        return
    }

    throw "Python 3.12 was not found. Install it locally or use -UseDocker."
}

function Ensure-Bootstrap {
    if ($UseDocker) {
        return
    }

    if ((-not $Bootstrap) -and (Test-Path $VenvPython)) {
        return
    }

    if (-not (Test-Path $VenvPython)) {
        Invoke-PreferredPython -Arguments @("-m", "venv", $VenvPath)
    }

    Push-Location $RepoRoot
    try {
        Invoke-Native -FilePath $VenvPython -Arguments @("-m", "pip", "install", "--upgrade", "pip")
        Invoke-Native -FilePath $VenvPython -Arguments @("-m", "pip", "install", "-e", ".[dev]")
    }
    finally {
        Pop-Location
    }
}

function Invoke-DockerAction {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DockerAction
    )

    Push-Location $RepoRoot
    try {
        switch ($DockerAction) {
            "validate" {
                Invoke-Native -FilePath "docker" -Arguments @("compose", "run", "--rm", "tooling", "python", "-m", "intent_config_workbench.cli", "validate", "--workspace", "/workspace")
            }
            "health" {
                Invoke-Native -FilePath "docker" -Arguments @("compose", "run", "--rm", "tooling", "python", "-m", "intent_config_workbench.cli", "health", "--workspace", "/workspace")
            }
            "render" {
                Invoke-Native -FilePath "docker" -Arguments @("compose", "run", "--rm", "tooling", "python", "-m", "intent_config_workbench.cli", "render", "--workspace", "/workspace")
            }
            "demo" {
                Invoke-Native -FilePath "docker" -Arguments @("compose", "run", "--rm", "tooling", "python", "-m", "intent_config_workbench.cli", "demo", "--workspace", "/workspace")
            }
            "pytest" {
                Invoke-Native -FilePath "docker" -Arguments @("compose", "run", "--rm", "tooling", "pytest")
            }
        }
    }
    finally {
        Pop-Location
    }
}

if ($UseDocker) {
    Invoke-DockerAction -DockerAction $Action
    exit 0
}

Ensure-Bootstrap

Push-Location $RepoRoot
try {
    switch ($Action) {
        "validate" {
            Invoke-PreferredPython -PreferVenv -Arguments @("-m", "intent_config_workbench.cli", "validate", "--workspace", $RepoRoot)
        }
        "health" {
            Invoke-PreferredPython -PreferVenv -Arguments @("-m", "intent_config_workbench.cli", "health", "--workspace", $RepoRoot)
        }
        "render" {
            Invoke-PreferredPython -PreferVenv -Arguments @("-m", "intent_config_workbench.cli", "render", "--workspace", $RepoRoot)
        }
        "demo" {
            Invoke-PreferredPython -PreferVenv -Arguments @("-m", "intent_config_workbench.cli", "demo", "--workspace", $RepoRoot)
        }
        "pytest" {
            Invoke-PreferredPython -PreferVenv -Arguments @("-m", "pytest")
        }
    }
}
finally {
    Pop-Location
}
