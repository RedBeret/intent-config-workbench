from __future__ import annotations

import json
from pathlib import Path

import typer

from .api import (
    WorkspaceValidationError,
    diff_workspace_api,
    health_workspace,
    render_workspace_api,
    run_demo,
    validate_workspace,
)
from .logging_utils import configure_logging

app = typer.Typer(add_completion=False, help="Synthetic deterministic intent rendering workbench.")


def _handle_validation_error(error: WorkspaceValidationError) -> None:
    for issue in error.issues:
        typer.echo(f"{issue['source']} -> {issue['field']}: {issue['message']}", err=True)
    raise typer.Exit(code=1)


def _handle_runtime_error(error: Exception) -> None:
    typer.echo(str(error), err=True)
    raise typer.Exit(code=1)


@app.callback()
def main_callback(log_level: str = typer.Option("INFO", "--log-level")) -> None:
    configure_logging(log_level)


@app.command("validate")
def validate_command(workspace: Path = typer.Option(Path("."), "--workspace", exists=True, file_okay=False)) -> None:
    try:
        bundle = validate_workspace(workspace.resolve())
    except WorkspaceValidationError as error:
        _handle_validation_error(error)
    except (FileNotFoundError, ValueError, TimeoutError) as error:
        _handle_runtime_error(error)
    typer.echo(f"Validated {len(bundle.devices)} devices from {workspace.resolve()}.")


@app.command("render")
def render_command(workspace: Path = typer.Option(Path("."), "--workspace", exists=True, file_okay=False)) -> None:
    try:
        summary = render_workspace_api(workspace.resolve())
    except WorkspaceValidationError as error:
        _handle_validation_error(error)
    except (FileNotFoundError, ValueError, TimeoutError, OSError) as error:
        _handle_runtime_error(error)
    typer.echo(
        f"Rendered {summary['devices']} devices to {summary['output_dir']} "
        f"({summary['changed']} changed, {summary['unchanged']} unchanged)."
    )
    typer.echo(f"Recorded run {summary['run_id']} in {summary['database_path']}.")


@app.command("diff")
def diff_command(
    workspace: Path = typer.Option(Path("."), "--workspace", exists=True, file_okay=False),
    overlay: list[Path] | None = typer.Option(None, "--overlay", exists=True, file_okay=True, dir_okay=True),
) -> None:
    overlay_paths = [item.resolve() for item in overlay] if overlay else [workspace.resolve() / "demo" / "intent"]
    try:
        summary = diff_workspace_api(
            workspace.resolve(),
            intent_overlays=overlay_paths,
            candidate_dir=workspace.resolve() / "artifacts" / "candidate",
        )
    except WorkspaceValidationError as error:
        _handle_validation_error(error)
    except (FileNotFoundError, ValueError, TimeoutError, OSError) as error:
        _handle_runtime_error(error)
    typer.echo(json.dumps(summary, indent=2, sort_keys=True))


@app.command("health")
def health_command(workspace: Path = typer.Option(Path("."), "--workspace", exists=True, file_okay=False)) -> None:
    try:
        summary = health_workspace(workspace.resolve())
    except WorkspaceValidationError as error:
        _handle_validation_error(error)
    except (FileNotFoundError, ValueError) as error:
        _handle_runtime_error(error)
    typer.echo(json.dumps(summary, indent=2, sort_keys=True))
    if summary["status"] == "fail":
        raise typer.Exit(code=1)


@app.command("demo")
def demo_command(workspace: Path = typer.Option(Path("."), "--workspace", exists=True, file_okay=False)) -> None:
    try:
        summary = run_demo(workspace.resolve())
    except WorkspaceValidationError as error:
        _handle_validation_error(error)
    except (FileNotFoundError, ValueError, TimeoutError, OSError) as error:
        _handle_runtime_error(error)
    typer.echo(json.dumps(summary, indent=2, sort_keys=True))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
