# Study Guide

## Core idea

The source of truth is the intent model, not the rendered config. A rendered artifact is a deterministic product of validated input plus a template.

## Mental model

- `inventory/` tells you what the synthetic device is
- `intent/` tells you what you want it to become
- `defaults/` tells you what is shared
- `rendered/` shows the deterministic result

## Why this is useful before Ansible

Ansible is excellent at transport and execution. This repo teaches the step before that: how to define desired state cleanly and render it reproducibly. If that step is weak, transport automation amplifies bad assumptions faster.

## Questions to answer while studying

- Which values belong in inventory versus intent?
- Why should validation happen before rendering?
- Why are rendered files disposable artifacts?
- Why does stable ordering matter for diffs?
- Why are overlays safer for demos than editing the baseline intent in place?

## Suggested exercises

1. Change one VLAN name in `intent/edge-01.yaml`, then render and inspect the diff.
2. Add a new synthetic user to `edge-02`, then validate and rerender.
3. Break an interface mode on purpose and read the field-level validation failure.
4. Compare the source YAML to the generated CLI-like output and explain every rendered stanza.

## Common misconception

If a config file looks right, that does not prove the model is good. A good model stays consistent when you add devices, change ordering, or rerender repeatedly.

## Rollback notes

- Exercise edits in `intent/`
  Rollback: undo the YAML change and rerun `validate`.
- Exercise renders in `rendered/`
  Rollback: delete the rendered file and rerun from the restored intent.
