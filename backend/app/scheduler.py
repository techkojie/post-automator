# scheduler.py
import schedule
import time
from main import run_post_cycle

def start_scheduler():
    """
    Runs the job every day at 9:00 AM
    """
    schedule.every().day.at("09:00").do(run_post_cycle)
    print("✅ Scheduler started. Waiting for next run...")

    while True:
        schedule.run_pending()
        time.sleep(60)
