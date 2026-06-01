import time
from pathlib import Path

from pipeline.ingest import find_csv_files, read_csv
from pipeline.validate import validate_rows
from pipeline.transform import normalise_rows
from pipeline.load import load_rows
from pipeline.report import write_summary


def run_pipeline(config: dict) -> list[str]:
    cfg = config["pipeline"]
    schema = config["schema"]["columns"]
    input_dir = cfg["input_dir"]
    quarantine_path = cfg["quarantine_file"]
    summary_dir = cfg["summary_dir"]
    db_path = cfg["db_path"]
    table_name = cfg["table_name"]

    csv_files = find_csv_files(input_dir)
    if not csv_files:
        print(f"[pipeline] No CSV files found in '{input_dir}'")
        return []

    summaries: list[str] = []

    for filepath in csv_files:
        print(f"[pipeline] Processing {filepath.name}")
        start = time.monotonic()

        rows, _ = read_csv(filepath)
        total_rows = len(rows)

        valid_rows, quarantine_count = validate_rows(rows, schema, quarantine_path)

        normalised = normalise_rows(valid_rows, schema)

        inserted = load_rows(normalised, schema, db_path, table_name)

        duration = time.monotonic() - start

        summary_path = write_summary(
            summary_dir=summary_dir,
            input_file=str(filepath),
            total_rows=total_rows,
            valid_rows=len(valid_rows),
            quarantine_count=quarantine_count,
            inserted_rows=inserted,
            duration_seconds=duration,
        )
        summaries.append(summary_path)
        print(
            f"[pipeline] Done — "
            f"total={total_rows} valid={len(valid_rows)} "
            f"quarantined={quarantine_count} inserted={inserted} "
            f"duration={duration:.3f}s"
        )
        print(f"[pipeline] Summary written to {summary_path}")

    return summaries
