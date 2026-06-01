import csv
import os
from pathlib import Path
from typing import Iterator


def find_csv_files(input_dir: str) -> list[Path]:
    directory = Path(input_dir)
    if not directory.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    files = sorted(directory.glob("*.csv"))
    return files


def read_csv(filepath: Path) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    fieldnames: list[str] = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            rows.append(dict(row))
    return rows, fieldnames
