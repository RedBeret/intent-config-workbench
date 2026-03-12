from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")


def timestamp_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text_if_changed(path: Path, content: str) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing == content:
        return False
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    return True


def retry_with_backoff(
    operation: Callable[[], T],
    *,
    attempts: int,
    base_delay_seconds: float,
    retry_exceptions: tuple[type[BaseException], ...],
) -> T:
    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except retry_exceptions as error:
            last_error = error
            if attempt == attempts:
                break
            time.sleep(base_delay_seconds * (2 ** (attempt - 1)))
    assert last_error is not None
    raise last_error


def run_with_timeout(operation: Callable[[], T], *, timeout_seconds: float, description: str) -> T:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(operation)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError as error:
            future.cancel()
            raise TimeoutError(f"{description} timed out after {timeout_seconds} seconds") from error


def deep_merge(base: Any, overlay: Any) -> Any:
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = dict(base)
        for key, value in overlay.items():
            if key in merged:
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    return overlay


def json_dumps(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def sorted_yaml_files(directory: Path) -> Iterable[Path]:
    return sorted(list(directory.glob("*.yaml")) + list(directory.glob("*.yml")))
