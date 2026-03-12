from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .models import DeviceConfig, GlobalDefaults, WorkspaceBundle
from .utils import ensure_directory, retry_with_backoff, run_with_timeout, sha256_text, write_text_if_changed

LOGGER = logging.getLogger(__name__)


@dataclass
class RenderedArtifact:
    hostname: str
    path: Path
    changed: bool
    checksum: str


def build_jinja_environment(template_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def render_device_config(
    device: DeviceConfig,
    defaults: GlobalDefaults,
    *,
    template_dir: Path,
    timeout_seconds: float,
) -> str:
    environment = build_jinja_environment(template_dir)
    template = environment.get_template("device_config.j2")
    return run_with_timeout(
        lambda: template.render(device=device.ordered(), defaults=defaults),
        timeout_seconds=timeout_seconds,
        description=f"render for {device.hostname}",
    )


def render_workspace(
    bundle: WorkspaceBundle,
    *,
    template_dir: Path,
    output_dir: Path,
) -> list[RenderedArtifact]:
    ensure_directory(output_dir)
    results: list[RenderedArtifact] = []
    for device in bundle.devices:
        rendered = render_device_config(
            device,
            bundle.defaults,
            template_dir=template_dir,
            timeout_seconds=bundle.defaults.render_timeout_seconds,
        )
        output_path = output_dir / f"{device.hostname}.cfg"

        changed = retry_with_backoff(
            lambda: write_text_if_changed(output_path, rendered),
            attempts=bundle.defaults.retry_attempts,
            base_delay_seconds=bundle.defaults.retry_backoff_seconds,
            retry_exceptions=(OSError,),
        )
        checksum = sha256_text(rendered)
        LOGGER.info(
            "render completed",
            extra={
                "hostname": device.hostname,
                "changed": changed,
                "path": str(output_path),
                "checksum": checksum,
            },
        )
        results.append(RenderedArtifact(device.hostname, output_path, changed, checksum))
    return results
