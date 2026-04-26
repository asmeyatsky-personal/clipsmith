from typing import Iterable, Mapping, Protocol


class AnalyticsExportPort(Protocol):
    """Phase 6.3 — push aggregated analytics to a warehouse for cohort
    analysis. The local placeholder writes JSONL; the production adapter
    will stream into BigQuery / DuckDB / Clickhouse via its native client.
    """

    def export(self, dataset: str, rows: Iterable[Mapping[str, object]]) -> int:
        """Write `rows` into the named `dataset`. Returns row count written."""
        ...
