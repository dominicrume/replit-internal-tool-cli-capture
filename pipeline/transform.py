def normalise_rows(rows: list[dict], schema: list[dict]) -> list[dict]:
    col_types = {col["name"]: col.get("type", "string") for col in schema}
    normalised: list[dict] = []
    for row in rows:
        new_row: dict = {}
        for key, value in row.items():
            col_type = col_types.get(key, "string")
            raw = str(value).strip() if value is not None else ""
            if col_type == "string":
                new_row[key] = raw.lower()
            elif col_type == "numeric":
                try:
                    new_row[key] = round(float(raw), 2)
                except (ValueError, TypeError):
                    new_row[key] = None
            else:
                new_row[key] = raw
        normalised.append(new_row)
    return normalised
