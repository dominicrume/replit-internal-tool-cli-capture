import csv
from pathlib import Path
from typing import Any


SUPPORTED_TYPES = {"string", "numeric"}


def _coerce(value: str, col_type: str) -> tuple[bool, Any]:
    if col_type == "string":
        return True, value
    if col_type == "numeric":
        try:
            return True, float(value)
        except (ValueError, TypeError):
            return False, None
    return False, None


def validate_rows(
    rows: list[dict],
    schema: list[dict],
    quarantine_path: str,
) -> tuple[list[dict], int]:
    valid: list[dict] = []
    invalid: list[dict] = []

    for row in rows:
        errors: list[str] = []
        for col in schema:
            name = col["name"]
            col_type = col.get("type", "string")
            required = col.get("required", False)
            value = row.get(name, "")

            if required and (value is None or str(value).strip() == ""):
                errors.append(f"missing required column '{name}'")
                continue

            if value is not None and str(value).strip() != "":
                ok, _ = _coerce(str(value).strip(), col_type)
                if not ok:
                    errors.append(f"column '{name}' cannot be coerced to {col_type}")

        if errors:
            row["_validation_errors"] = "; ".join(errors)
            invalid.append(row)
        else:
            valid.append(row)

    _write_quarantine(invalid, quarantine_path)
    return valid, len(invalid)


def _write_quarantine(rows: list[dict], path: str) -> None:
    if not rows:
        return
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    existing = dest.exists()
    fieldnames = list(rows[0].keys())
    with open(dest, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not existing:
            writer.writeheader()
        writer.writerows(rows)
