# Review Questions

1. Why does this repo separate `inventory/`, `intent/`, and `defaults/` instead of using one large YAML file?
2. What makes the rendered output deterministic?
3. Why are RFC5737 addresses enforced here?
4. Why is `rendered/` not the source of truth?
5. What problem does the overlay in `demo/intent/edge-02.yaml` solve?
6. Which workflows in this repo are mutating, and how do you roll them back?
7. Why is idempotent file writing valuable for a training repo?
8. Why does the repo record render history in SQLite even though the primary artifact is text config?
9. What kinds of issues are caught by schema validation before Jinja2 runs?
10. Why is this repo a good precursor to Ansible rather than a replacement for it?
