# Runbook

## Purpose

Use this runbook to update intent safely, render deterministic outputs, and review candidate changes without touching real infrastructure.

## Workflow 1: bootstrap a Windows workstation

```powershell
pwsh -File .\scripts\Render-All.ps1 -Bootstrap
```

Checks:

- PowerShell 7 is available
- Python 3.12 is available
- A local `.venv` exists or is created

Rollback notes:

- Remove `.venv\` to discard the local environment.

## Workflow 2: validate current intent

```powershell
python -m intent_config_workbench.cli validate --workspace .
python -m intent_config_workbench.cli health --workspace .
```

Expected result:

- All three synthetic devices validate
- Health shows `pass` or a harmless `warn` for a database file that has not been created yet

Rollback notes:

- This workflow is non-mutating unless you choose to bootstrap first.

## Workflow 3: update intent safely

1. Edit the target file in `intent/`.
2. Keep the hostname, mgmt data, usernames, and addresses synthetic.
3. Run `validate`.
4. Run `render`.
5. Review the resulting diff.

Example:

```powershell
python -m intent_config_workbench.cli validate --workspace .
python -m intent_config_workbench.cli render --workspace .
```

Rollback notes:

- Restore the edited YAML file from the last known-good copy.
- Delete the newly rendered `rendered\*.cfg` files if you do not want to keep the artifacts.
- Delete `.workbench\workbench.db` if you want to remove the recorded render history for the discarded run.

## Workflow 4: run the demo overlay

```powershell
pwsh -File .\scripts\Render-All.ps1 -Bootstrap -Demo
```

What happens:

- Baseline configs render from `intent/`
- Candidate changes are merged from `demo/intent/`
- Candidate artifacts are written to `artifacts/candidate/`
- A unified diff patch and JSON summary are generated

Rollback notes:

- Delete `artifacts\candidate\`
- Delete `artifacts\diff-summary.json`
- Delete `artifacts\demo.patch`
- If you want to remove baseline render output too, delete `rendered\*.cfg` and `.workbench\workbench.db`

## Workflow 5: run tests

```powershell
pwsh -File .\scripts\Test-Intent.ps1 -Bootstrap
```

Test coverage includes:

- Golden file rendering
- Schema failures
- Deterministic rerender behavior
- Diff summary behavior

Rollback notes:

- Delete `.pytest_cache\`
- Keep or remove `.venv\` depending on whether you want to preserve the local toolchain

## Workflow 6: use WSL2 Ubuntu or Docker for Linux-only tooling

WSL2:

```bash
make install
make demo
```

Docker:

```powershell
docker compose build tooling
docker compose run --rm tooling make demo
```

Rollback notes:

- WSL2: remove `.venv/` and generated artifacts inside the repo if you want a clean workspace.
- Docker: remove local images or containers with normal Docker cleanup commands if you do not want to keep the cache.
