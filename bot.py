"""
Mental Health Bot - Main Entry Point

A Telegram bot for mental health monitoring with daily/weekly check-ins,
analytics, and AI-powered predictions.
"""

import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config import settings
from database import init_db
from handlers import (
    common_router,
    onboarding_router,
    daily_check_router,
    weekly_check_router,
    stats_router,
    settings_router,
    admin_router
)
from middlewares import (
    RateLimitMiddleware,
    SessionTimeoutMiddleware,
    UserActivityMiddleware,
    AdminCheckMiddleware,
    LoggingMiddleware
)
from scheduler import set_bot, setup_scheduler, start_scheduler, stop_scheduler


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/bot_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    """Actions to perform on bot startup."""
    logger.info("Starting Mental Health Bot...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Set bot reference for scheduler
    set_bot(bot)
    
    # Setup and start scheduler
    setup_scheduler()
    start_scheduler()
    logger.info("Scheduler started")
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username}")


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    """Actions to perform on bot shutdown."""
    logger.info("Shutting down Mental Health Bot...")
    
    # Stop scheduler
    stop_scheduler()
    
    # Close bot session
    await bot.session.close()
    
    logger.info("Bot stopped")


def register_routers(dp: Dispatcher):
    """Register all routers with the dispatcher."""
    # Common handlers first (start, help, cancel, menu)
    dp.include_router(common_router)
    
    # Feature routers
    dp.include_router(onboarding_router)
    dp.include_router(daily_check_router)
    dp.include_router(weekly_check_router)
    dp.include_router(stats_router)
    dp.include_router(settings_router)
    dp.include_router(admin_router)
    
    logger.info("All routers registered")


def register_middlewares(dp: Dispatcher):
    """Register all middlewares with the dispatcher."""
    # Order matters - first registered = first executed
    
    # Logging middleware (logs all updates)
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Rate limiting (protect from spam)
    dp.message.middleware(RateLimitMiddleware())
    
    # Session timeout (auto-clear old FSM states)
    dp.message.middleware(SessionTimeoutMiddleware())
    dp.callback_query.middleware(SessionTimeoutMiddleware())
    
    # User activity tracking
    dp.message.middleware(UserActivityMiddleware())
    dp.callback_query.middleware(UserActivityMiddleware())
    
    # Admin check (adds is_admin flag to handler data)
    dp.message.middleware(AdminCheckMiddleware())
    dp.callback_query.middleware(AdminCheckMiddleware())
    
    logger.info("All middlewares registered")


async def main():
    """Main entry point."""
    # Validate configuration
    if not settings.bot_token:
        logger.error("BOT_TOKEN is not set in environment variables!")
        sys.exit(1)
    
    # Initialize bot with default properties
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Initialize dispatcher with memory storage
    # For production, consider using Redis storage for FSM
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Register middlewares and routers
    register_middlewares(dp)
    register_routers(dp)
    
    # Start polling
    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",
                "callback_query",
                "chat_member"
            ]
        )
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
