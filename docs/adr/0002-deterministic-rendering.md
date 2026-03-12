# ADR 0002: Deterministic rendering over convenience ordering

## Status

Accepted

## Context

Intent data often arrives in human-authored YAML where ordering can drift over time. If output ordering changes unpredictably, diffs become noisy and training value drops.

## Decision

- Validate data before rendering
- Sort devices, users, interfaces, VLANs, and static routes before template execution
- Emit LF line endings consistently
- Only rewrite files when content changes

## Consequences

- Repeated renders of the same intent produce the same output
- Diffs stay meaningful
- Contributors have to preserve stable ordering logic when changing the model or template
