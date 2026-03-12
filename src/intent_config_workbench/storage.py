from __future__ import annotations

import sqlite3
from pathlib import Path

from .renderer import RenderedArtifact
from .utils import ensure_directory, retry_with_backoff, timestamp_utc


def initialize_database(database_path: Path, *, attempts: int, base_delay_seconds: float) -> None:
    ensure_directory(database_path.parent)

    def operation() -> None:
        with sqlite3.connect(database_path, timeout=3) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS render_runs (
                    run_id TEXT NOT NULL,
                    hostname TEXT NOT NULL,
                    rendered_path TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    changed INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    retry_with_backoff(
        operation,
        attempts=attempts,
        base_delay_seconds=base_delay_seconds,
        retry_exceptions=(sqlite3.OperationalError, OSError),
    )


def record_render_run(
    database_path: Path,
    artifacts: list[RenderedArtifact],
    *,
    attempts: int,
    base_delay_seconds: float,
) -> str:
    run_id = timestamp_utc()

    def operation() -> None:
        with sqlite3.connect(database_path, timeout=3) as connection:
            connection.executemany(
                """
                INSERT INTO render_runs (
                    run_id,
                    hostname,
                    rendered_path,
                    checksum,
                    changed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        artifact.hostname,
                        str(artifact.path),
                        artifact.checksum,
                        int(artifact.changed),
                        run_id,
                    )
                    for artifact in artifacts
                ],
            )
            connection.commit()

    retry_with_backoff(
        operation,
        attempts=attempts,
        base_delay_seconds=base_delay_seconds,
        retry_exceptions=(sqlite3.OperationalError, OSError),
    )
    return run_id
