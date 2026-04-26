"""Local JSONL analytics export adapter.

Writes one file per dataset under ANALYTICS_EXPORT_DIR (defaults to
./analytics_exports). Real BigQuery adapter will replace this once the
GCP service account is provisioned per refactor250426.md §8.
"""
import json
import logging
import os
import pathlib
from datetime import datetime, timezone
from typing import Iterable, Mapping

from ...domain.ports.analytics_export_port import AnalyticsExportPort

logger = logging.getLogger(__name__)


class JSONLAnalyticsExporter(AnalyticsExportPort):
    def __init__(self, base_dir: str | None = None) -> None:
        self._base_dir = pathlib.Path(
            base_dir or os.getenv("ANALYTICS_EXPORT_DIR", "analytics_exports")
        )

    def export(self, dataset: str, rows: Iterable[Mapping[str, object]]) -> int:
        try:
            self._base_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning("Cannot create export dir %s: %s", self._base_dir, e)
            return 0

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self._base_dir / f"{dataset}_{ts}.jsonl"
        count = 0
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(dict(row), default=str))
                f.write("\n")
                count += 1
        logger.info("Exported %d rows to %s", count, path)
        return count
