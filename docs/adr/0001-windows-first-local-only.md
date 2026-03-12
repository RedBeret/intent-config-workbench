# ADR 0001: Windows-first and local-only

## Status

Accepted

## Context

The host environment is Windows, but some users may still want WSL2 Ubuntu or Docker for Linux-only tooling. The training repo must stay local, synthetic, and safe.

## Decision

- PowerShell 7 wrappers are the primary entrypoint
- WSL2 Ubuntu and Docker are supported for Linux-only tooling
- No real devices, customer data, credentials, or proprietary images are allowed
- Sample data uses synthetic hostnames, fake serials, fake usernames, and RFC5737 example IPs

## Consequences

- The repo is approachable for Windows users
- Training remains portable and safe
- Documentation must call out which workflows belong in PowerShell versus WSL2 or Docker
