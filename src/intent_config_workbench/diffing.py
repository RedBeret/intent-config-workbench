from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

from .utils import ensure_directory, json_dumps, write_text_if_changed


@dataclass
class DeviceDiff:
    hostname: str
    changed: bool
    added_lines: int
    removed_lines: int
    diff: str

    def to_dict(self) -> dict[str, object]:
        return {
            "hostname": self.hostname,
            "changed": self.changed,
            "added_lines": self.added_lines,
            "removed_lines": self.removed_lines,
        }


def _cfg_files(directory: Path) -> dict[str, Path]:
    return {path.stem: path for path in sorted(directory.glob("*.cfg"))}


def diff_rendered_directories(
    baseline_dir: Path,
    candidate_dir: Path,
    *,
    json_output_path: Path | None = None,
    patch_output_path: Path | None = None,
) -> dict[str, object]:
    baseline_files = _cfg_files(baseline_dir)
    candidate_files = _cfg_files(candidate_dir)
    hostnames = sorted(set(baseline_files) | set(candidate_files))

    device_diffs: list[DeviceDiff] = []
    patch_parts: list[str] = []
    for hostname in hostnames:
        baseline_text = baseline_files[hostname].read_text(encoding="utf-8").splitlines(keepends=True) if hostname in baseline_files else []
        candidate_text = candidate_files[hostname].read_text(encoding="utf-8").splitlines(keepends=True) if hostname in candidate_files else []
        unified = list(
            difflib.unified_diff(
                baseline_text,
                candidate_text,
                fromfile=f"{hostname}.cfg",
                tofile=f"{hostname}.cfg",
            )
        )
        diff_text = "".join(unified)
        added = sum(1 for line in unified if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in unified if line.startswith("-") and not line.startswith("---"))
        device_diff = DeviceDiff(
            hostname=hostname,
            changed=bool(diff_text),
            added_lines=added,
            removed_lines=removed,
            diff=diff_text,
        )
        device_diffs.append(device_diff)
        if diff_text:
            patch_parts.append(diff_text)

    summary: dict[str, object] = {
        "baseline_dir": str(baseline_dir),
        "candidate_dir": str(candidate_dir),
        "changed_devices": sum(1 for item in device_diffs if item.changed),
        "unchanged_devices": sum(1 for item in device_diffs if not item.changed),
        "devices": [item.to_dict() for item in device_diffs],
    }

    if json_output_path:
        ensure_directory(json_output_path.parent)
        write_text_if_changed(json_output_path, json_dumps(summary))
    if patch_output_path:
        ensure_directory(patch_output_path.parent)
        write_text_if_changed(patch_output_path, "".join(patch_parts))

    return summary
