"""
Handlers package initialization.
"""

from handlers.common import router as common_router
from handlers.onboarding import router as onboarding_router
from handlers.daily_check import router as daily_check_router
from handlers.weekly_check import router as weekly_check_router
from handlers.stats import router as stats_router
from handlers.settings import router as settings_router
from handlers.admin import router as admin_router

__all__ = [
    "common_router",
    "onboarding_router",
    "daily_check_router",
    "weekly_check_router",
    "stats_router",
    "settings_router",
    "admin_router"
]
