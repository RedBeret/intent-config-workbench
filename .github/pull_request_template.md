## Summary

Describe the change in plain language.

## Why

Explain the problem this change solves.

## Validation

- [ ] `pwsh -File .\scripts\Render-All.ps1 -Bootstrap`
- [ ] `pwsh -File .\scripts\Test-Intent.ps1 -Bootstrap`
- [ ] Docs still match actual behavior

## Checklist

- [ ] All examples are synthetic
- [ ] Windows remains the primary path
- [ ] Output stays deterministic
- [ ] Rollback notes were updated if a mutating workflow changed
