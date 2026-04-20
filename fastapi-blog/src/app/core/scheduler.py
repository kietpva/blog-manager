from apscheduler.schedulers.background import BackgroundScheduler

from src.app.db.session import SessionLocal
from src.app.modules.notifications.repository import NotificationRepository
from src.app.modules.notifications.service import NotificationService

scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")


def job():
    """
    Scheduled APScheduler job to generate and send daily report notifications.

    This function is intended to be called by the background scheduler.
    It creates a new DB session, invokes the NotificationService to generate
    and push a daily report notification to all admins, and ensures the DB session
    is properly closed after execution.
    """
    db = SessionLocal()
    try:
        NotificationService(NotificationRepository(db)).create_daily_report()
    finally:
        db.close()


def start_scheduler():
    """
    Starts the background APScheduler if it is not already running.

    Registers the `job` to run every day at 16:10 Asia/Ho_Chi_Minh time
    using a cron trigger. Ensures the scheduler is started only once.
    """
    if not scheduler.running:
        scheduler.add_job(job, "cron", hour=16, minute=39)
        scheduler.start()


def stop_scheduler():
    """
    Stops the background APScheduler if it is currently running.

    This will shut down the scheduler and halt all future scheduled jobs.
    """
    if scheduler.running:
        scheduler.shutdown()
