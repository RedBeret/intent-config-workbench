# Security Policy

## Scope

This project is intentionally local-only and synthetic-only.

Please do not submit:

- real credentials
- customer data
- proprietary images
- real hostnames or real device outputs

## Supported versions

This is a small training repo, so security fixes are generally applied on the latest version on the default branch.

## Reporting a vulnerability

Please use GitHub Security Advisories for private reporting:

<https://github.com/RedBeret/intent-config-workbench/security/advisories/new>

If that link is not available yet because the repository has not been published under that exact path, open the advisory after publish or update this file with the final repo URL.

## What counts as a security issue here

- accidental inclusion of real secrets or customer data
- unsafe handling of local files that could overwrite unintended paths
- command execution behavior that breaks the repo's local-only expectations

## What does not count

- requests to support real devices or real credentials
- requests to turn the project into a remote execution system
