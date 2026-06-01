import json
import os
from datetime import datetime, timezone
from pathlib import Path


def write_summary(
    summary_dir: str,
    input_file: str,
    total_rows: int,
    valid_rows: int,
    quarantine_count: int,
    inserted_rows: int,
    duration_seconds: float,
    status: str = "success",
) -> str:
    Path(summary_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"run_summary_{timestamp}.json"
    filepath = os.path.join(summary_dir, filename)

    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "input_file": input_file,
        "duration_seconds": round(duration_seconds, 3),
        "total_rows_read": total_rows,
        "valid_rows": valid_rows,
        "quarantine_count": quarantine_count,
        "inserted_rows": inserted_rows,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return filepath
