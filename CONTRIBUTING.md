# Contributing

Thanks for taking a look at `intent-config-workbench`.

This repo is meant to stay small, practical, and safe. If you contribute, please keep the shape of the project intact.

## Ground rules

- Keep the repo local-only and synthetic-only
- Keep Windows PowerShell as the primary entrypoint
- Put Linux-only workflows in WSL2 Ubuntu or Docker
- Do not add real hostnames, real credentials, customer data, or proprietary images
- Use RFC5737 example IP ranges for all examples and fixtures
- Keep generated output deterministic

## Development workflow

Windows:

```powershell
pwsh -File .\scripts\Render-All.ps1 -Bootstrap
pwsh -File .\scripts\Test-Intent.ps1 -Bootstrap
```

WSL2 Ubuntu:

```bash
make install
make demo
pytest
```

## Pull request checklist

- Validation still passes
- Golden file tests still pass
- Repeated renders are deterministic
- README and docs still match the actual workflow
- Rollback notes are updated if a mutating workflow changes
- Any new sample data is still clearly synthetic

## Style notes

- Prefer explicit validation over silent coercion
- Prefer deterministic ordering over convenience ordering
- Prefer small, reviewable changes
- Avoid cleverness in templates
- Use plain language in docs
- Do not use long dashes in the docs or README

## Good contribution ideas

- Add more synthetic device patterns
- Add more schema validation coverage
- Add safer diff or reporting behavior
- Improve the study material without bloating the repo

## Bad contribution ideas

- Adding real vendor credentials or real hostnames
- Turning the repo into a remote execution tool
- Replacing the Windows-first path with a Linux-only default
- Adding proprietary images or device artifacts
