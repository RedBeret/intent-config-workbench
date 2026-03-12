from __future__ import annotations

from pathlib import Path

from .models import GlobalDefaults


def run_health_checks(workspace: Path, defaults: GlobalDefaults) -> dict[str, object]:
    checks = [
        {
            "name": "defaults_file",
            "status": "pass" if (workspace / "defaults" / "global.yaml").exists() else "fail",
            "path": str(workspace / "defaults" / "global.yaml"),
        },
        {
            "name": "inventory_file",
            "status": "pass" if (workspace / "inventory" / "devices.yaml").exists() else "fail",
            "path": str(workspace / "inventory" / "devices.yaml"),
        },
        {
            "name": "intent_directory",
            "status": "pass" if (workspace / "intent").exists() else "fail",
            "path": str(workspace / "intent"),
        },
        {
            "name": "template_file",
            "status": "pass" if (workspace / "templates" / "device_config.j2").exists() else "fail",
            "path": str(workspace / "templates" / "device_config.j2"),
        },
        {
            "name": "render_output_parent",
            "status": "pass" if (workspace / "rendered").exists() else "warn",
            "path": str(workspace / "rendered"),
        },
        {
            "name": "database_parent",
            "status": "pass" if (workspace / Path(defaults.database_path)).parent.exists() else "fail",
            "path": str((workspace / Path(defaults.database_path)).parent),
        },
        {
            "name": "database_file",
            "status": "pass" if (workspace / Path(defaults.database_path)).exists() else "warn",
            "path": str(workspace / Path(defaults.database_path)),
        },
    ]
    overall_status = "pass"
    if any(check["status"] == "fail" for check in checks):
        overall_status = "fail"
    elif any(check["status"] == "warn" for check in checks):
        overall_status = "warn"
    return {"status": overall_status, "checks": checks}
