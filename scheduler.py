"""
APScheduler-based reminder service for weekly check-in notifications.
"""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from database.session import get_session
from database.models import User, Reminder
from sqlalchemy import select


scheduler = AsyncIOScheduler()

# Bot reference - set from main bot module
bot_instance = None


def set_bot(bot):
    """Set the bot instance for sending messages."""
    global bot_instance
    bot_instance = bot


async def send_weekly_reminders():
    """Send weekly check-in reminders to all users with notifications enabled."""
    if not bot_instance:
        logger.error("Bot instance not set for scheduler")
        return
    
    logger.info("Starting weekly reminder job")
    sent_count = 0
    error_count = 0
    
    try:
        async with get_session() as session:
            # Get all users with notifications enabled
            result = await session.execute(
                select(User).where(
                    User.is_active == True,
                    User.notifications_enabled == True,
                    User.is_onboarded == True
                )
            )
            users = result.scalars().all()
            
            for user in users:
                try:
                    await bot_instance.send_message(
                        chat_id=user.id,
                        text=(
                            "🔔 **Weekly Reminder**\n\n"
                            "It's time for your weekly mental health check-in!\n\n"
                            "Regular check-ins help you track your mental wellness "
                            "and identify patterns over time.\n\n"
                            "Use /start to access your check-ins."
                        ),
                        parse_mode="Markdown"
                    )
                    sent_count += 1
                    
                    # Create reminder record
                    reminder = Reminder(
                        user_id=user.id,
                        type="weekly",
                        scheduled_at=datetime.utcnow(),
                        sent_at=datetime.utcnow()
                    )
                    session.add(reminder)
                    
                    # Rate limiting - don't spam Telegram API
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Failed to send reminder to user {user.id}: {e}")
                    error_count += 1
            
            await session.commit()
    
    except Exception as e:
        logger.error(f"Error in weekly reminder job: {e}")
    
    logger.info(f"Weekly reminders sent: {sent_count}, errors: {error_count}")


async def send_daily_reminders():
    """Send daily check-in reminders (optional feature)."""
    if not bot_instance:
        logger.error("Bot instance not set for scheduler")
        return
    
    logger.info("Starting daily reminder job")
    sent_count = 0
    
    try:
        async with get_session() as session:
            # Get users who haven't completed daily check-in today
            today = datetime.utcnow().date()
            
            result = await session.execute(
                select(User).where(
                    User.is_active == True,
                    User.notifications_enabled == True,
                    User.is_onboarded == True
                )
            )
            users = result.scalars().all()
            
            for user in users:
                try:
                    # Check if user already completed today's check-in
                    from services import DailyAnswerService
                    today_checkin = await DailyAnswerService.get_today_answer(user.id)
                    
                    if not today_checkin:
                        await bot_instance.send_message(
                            chat_id=user.id,
                            text=(
                                "🌅 **Daily Check-in Reminder**\n\n"
                                "Don't forget to complete your daily mental health check-in!\n\n"
                                "It only takes a few minutes and helps track your wellness."
                            ),
                            parse_mode="Markdown"
                        )
                        sent_count += 1
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"Failed to send daily reminder to user {user.id}: {e}")
    
    except Exception as e:
        logger.error(f"Error in daily reminder job: {e}")
    
    logger.info(f"Daily reminders sent: {sent_count}")


def setup_scheduler():
    """Setup and configure the scheduler with jobs."""
    # Weekly reminder - every Sunday at 10:00 AM UTC
    scheduler.add_job(
        send_weekly_reminders,
        CronTrigger(day_of_week='sun', hour=10, minute=0),
        id='weekly_reminder',
        name='Weekly Check-in Reminder',
        replace_existing=True
    )
    
    # Optional: Daily reminder - every day at 9:00 PM UTC
    # Uncomment to enable daily reminders
    # scheduler.add_job(
    #     send_daily_reminders,
    #     CronTrigger(hour=21, minute=0),
    #     id='daily_reminder',
    #     name='Daily Check-in Reminder',
    #     replace_existing=True
    # )
    
    logger.info("Scheduler jobs configured")


def start_scheduler():
    """Start the APScheduler."""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    """Stop the APScheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


async def trigger_reminder(reminder_type: str = "weekly"):
    """Manually trigger a reminder (for testing/admin use)."""
    if reminder_type == "weekly":
        await send_weekly_reminders()
    elif reminder_type == "daily":
        await send_daily_reminders()
