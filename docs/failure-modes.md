# Failure Modes

## Invalid synthetic address

Symptom:

- Validation fails on `mgmt.ipv4`, `routing.router_id`, or `static_routes`

Likely cause:

- A non-RFC5737 address such as `10.0.0.5/24` was used

Recovery:

- Replace it with an example address in `192.0.2.0/24`, `198.51.100.0/24`, or `203.0.113.0/24`

## Intent file missing for an inventory device

Symptom:

- Validation reports `missing intent file`

Likely cause:

- A device exists in `inventory/devices.yaml` but does not have a matching `intent/<hostname>.yaml`

Recovery:

- Add the missing file or remove the inventory entry

## Overlay hostname mismatch

Symptom:

- The loader rejects a demo or overlay file

Likely cause:

- The file name and the `hostname` field do not match

Recovery:

- Rename the file or fix the hostname field

## Non-deterministic output drift

Symptom:

- Golden file tests fail even though device intent did not change

Likely cause:

- Sorting logic was changed, template iteration order shifted, or a list is no longer normalized

Recovery:

- Restore stable ordering, rerun tests, and regenerate outputs only after the cause is understood

## File lock or SQLite lock

Symptom:

- Rendering or database recording fails intermittently

Likely cause:

- Another local process is holding a file handle

Recovery:

- Retry after the lock clears; the repo already backs off and retries for transient write failures

## PowerShell wrapper cannot find Python 3.12

Symptom:

- `Render-All.ps1` or `Test-Intent.ps1` fails before validation

Likely cause:

- Python 3.12 is not installed or not available to `py` / `python`

Recovery:

- Install Python 3.12 locally or use WSL2 / Docker instead

## Docker or WSL path confusion

Symptom:

- Tooling works in one environment but not another

Likely cause:

- The repo was invoked from the wrong shell for the workflow

Recovery:

- Use PowerShell wrappers on Windows
- Use `make` only inside WSL2 Ubuntu or a Docker container

## Rollback notes

- Failed render artifacts
  Rollback: delete `rendered\*.cfg` and rerun from validated intent.
- Failed demo artifacts
  Rollback: delete `artifacts\candidate\`, `artifacts\diff-summary.json`, and `artifacts\demo.patch`.
- Failed local environment bootstrap
  Rollback: remove `.venv\`.
