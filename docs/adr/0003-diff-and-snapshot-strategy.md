# ADR 0003: Text artifacts first, SQLite history second

## Status

Accepted

## Context

The main teaching goal is deterministic config generation and safe diff review. The repo still benefits from a lightweight local history of render activity.

## Decision

- Render text configs to `rendered/`
- Generate unified diffs plus JSON summaries for review
- Record render history locally in SQLite
- Keep everything local and disposable

## Consequences

- The text output remains the primary artifact for learning and review
- SQLite adds observability without adding external dependencies
- Rollback is straightforward because both rendered text and local history are disposable
