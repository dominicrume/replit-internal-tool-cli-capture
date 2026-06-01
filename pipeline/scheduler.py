from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


def start_scheduler(config: dict, run_fn) -> None:
    cron_expr = config.get("schedule", {}).get("cron", "0 0 * * *")
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: '{cron_expr}' (expected 5 fields)")

    minute, hour, day, month, day_of_week = parts
    trigger = CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
    )

    scheduler = BlockingScheduler()
    scheduler.add_job(run_fn, trigger=trigger, args=[config])
    print(f"[scheduler] Starting — cron: {cron_expr}")
    print("[scheduler] Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[scheduler] Stopped.")
