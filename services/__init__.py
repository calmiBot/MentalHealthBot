"""
Services package initialization.
"""

from services.ai_service import (
    call_ai_model,
    get_advice_for_level,
    get_personalized_recommendations,
    analyze_trends
)

from services.user_service import (
    UserService,
    ProfileService,
    DailyAnswerService,
    WeeklyAnswerService,
    HistoryService,
    PredictionService,
    FeedbackService,
    ReminderService
)

from services.analytics_service import AnalyticsService

__all__ = [
    # AI Service
    "call_ai_model",
    "get_advice_for_level",
    "get_personalized_recommendations",
    "analyze_trends",
    # User Services
    "UserService",
    "ProfileService",
    "DailyAnswerService",
    "WeeklyAnswerService",
    "HistoryService",
    "PredictionService",
    "FeedbackService",
    "ReminderService",
    # Analytics
    "AnalyticsService"
]
