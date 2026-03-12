from __future__ import annotations

from pathlib import Path

from .diffing import diff_rendered_directories
from .health import run_health_checks
from .loader import WorkspaceValidationError, load_workspace
from .renderer import render_workspace
from .storage import initialize_database, record_render_run
from .utils import ensure_directory


def validate_workspace(workspace: Path, intent_overlays: list[Path] | None = None):
    return load_workspace(workspace, intent_overlays=intent_overlays)


def render_workspace_api(workspace: Path, output_dir: Path | None = None) -> dict[str, object]:
    bundle = load_workspace(workspace)
    render_dir = output_dir or (workspace / "rendered")
    artifacts = render_workspace(
        bundle,
        template_dir=workspace / "templates",
        output_dir=render_dir,
    )
    database_path = workspace / bundle.defaults.database_path
    initialize_database(
        database_path,
        attempts=bundle.defaults.retry_attempts,
        base_delay_seconds=bundle.defaults.retry_backoff_seconds,
    )
    run_id = record_render_run(
        database_path,
        artifacts,
        attempts=bundle.defaults.retry_attempts,
        base_delay_seconds=bundle.defaults.retry_backoff_seconds,
    )
    return {
        "devices": len(artifacts),
        "changed": sum(1 for artifact in artifacts if artifact.changed),
        "unchanged": sum(1 for artifact in artifacts if not artifact.changed),
        "output_dir": str(render_dir),
        "database_path": str(database_path),
        "run_id": run_id,
    }


def diff_workspace_api(
    workspace: Path,
    *,
    baseline_dir: Path | None = None,
    intent_overlays: list[Path] | None = None,
    candidate_dir: Path | None = None,
) -> dict[str, object]:
    baseline = baseline_dir or (workspace / "rendered")
    candidate = candidate_dir or (workspace / "artifacts" / "candidate")
    if not baseline.exists():
        raise FileNotFoundError(f"Baseline render directory does not exist: {baseline}")
    if not any(baseline.glob("*.cfg")):
        raise FileNotFoundError(f"Baseline render directory has no .cfg files: {baseline}")
    bundle = load_workspace(workspace, intent_overlays=intent_overlays)
    ensure_directory(candidate)
    render_workspace(
        bundle,
        template_dir=workspace / "templates",
        output_dir=candidate,
    )
    return diff_rendered_directories(
        baseline,
        candidate,
        json_output_path=workspace / "artifacts" / "diff-summary.json",
        patch_output_path=workspace / "artifacts" / "demo.patch",
    )


def run_demo(workspace: Path) -> dict[str, object]:
    render_summary = render_workspace_api(workspace)
    diff_summary = diff_workspace_api(
        workspace,
        baseline_dir=workspace / "rendered",
        intent_overlays=[workspace / "demo" / "intent"],
        candidate_dir=workspace / "artifacts" / "candidate",
    )
    return {"render": render_summary, "diff": diff_summary}


def health_workspace(workspace: Path) -> dict[str, object]:
    bundle = load_workspace(workspace)
    return run_health_checks(workspace, bundle.defaults)


__all__ = [
    "WorkspaceValidationError",
    "diff_workspace_api",
    "health_workspace",
    "render_workspace_api",
    "run_demo",
    "validate_workspace",
]
