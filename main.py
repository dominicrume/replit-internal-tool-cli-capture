#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

import yaml


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        print(f"[error] Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def cmd_run(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    from pipeline.runner import run_pipeline
    run_pipeline(config)


def cmd_schedule(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    from pipeline.runner import run_pipeline
    from pipeline.scheduler import start_scheduler
    start_scheduler(config, run_pipeline)


def cmd_validate_config(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    required_keys = ["pipeline", "schema", "schedule"]
    missing = [k for k in required_keys if k not in config]
    if missing:
        print(f"[error] Config missing keys: {missing}", file=sys.stderr)
        sys.exit(1)
    col_names = [c["name"] for c in config["schema"]["columns"]]
    print(f"[config] Valid — columns: {col_names}")
    print(f"[config] Input dir: {config['pipeline']['input_dir']}")
    print(f"[config] DB: {config['pipeline']['db_path']}")
    print(f"[config] Cron: {config['schedule']['cron']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="data_pipeline",
        description="ETL pipeline: ingest CSV → validate → normalise → load SQLite",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        metavar="PATH",
        help="Path to YAML config file (default: config.yaml)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run the pipeline once immediately")
    run_parser.set_defaults(func=cmd_run)

    sched_parser = sub.add_parser("schedule", help="Start the daily scheduler")
    sched_parser.set_defaults(func=cmd_schedule)

    check_parser = sub.add_parser("check-config", help="Validate the config file")
    check_parser.set_defaults(func=cmd_validate_config)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
