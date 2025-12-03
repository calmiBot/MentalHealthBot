"""
Utilities package initialization.
"""

from utils.constants import (
    STRESS_LEVEL_SCALE, ANXIETY_LEVEL_SCALE, MOOD_RATING_SCALE,
    ENERGY_LEVEL_SCALE, SWEATING_LEVEL_SCALE, WEEK_RATING_SCALE,
    GENDER_OPTIONS, FAMILY_STATUS_OPTIONS, PHYSICAL_ACTIVITY_OPTIONS,
    DIET_QUALITY_OPTIONS, SMOKING_HABITS_OPTIONS, DIZZINESS_OPTIONS,
    THERAPY_FREQUENCY_OPTIONS, MEDICATION_ADHERENCE_OPTIONS,
    ALCOHOL_INTAKE_RANGE, CAFFEINE_INTAKE_RANGE, SLEEP_HOURS_RANGE,
    HEART_RATE_RANGE, BREATHING_RATE_RANGE, AGE_RANGE,
    COMMON_OCCUPATIONS, LIFE_EVENTS_EXAMPLES, ADVICE_CATEGORIES,
    PROFESSIONAL_HELP_WARNING, PLACEHOLDER_ADVICE, EMOJI, MESSAGES,
    ADMIN_MESSAGES
)

from utils.helpers import (
    format_scale_explanation, format_user_profile, format_daily_answer,
    format_statistics, format_admin_stats, calculate_week_dates,
    validate_numeric_input, validate_float_input, get_anxiety_category,
    truncate_text, safe_json_loads, format_datetime, parse_callback_data,
    create_callback_data, paginate_list, format_user_list_item
)

from utils.charts import (
    create_anxiety_chart, create_stress_chart, create_combined_chart,
    create_sleep_chart, create_distribution_chart, create_weekly_comparison_chart,
    create_pie_chart, create_admin_overview_chart
)

__all__ = [
    # Constants
    "STRESS_LEVEL_SCALE", "ANXIETY_LEVEL_SCALE", "MOOD_RATING_SCALE",
    "ENERGY_LEVEL_SCALE", "SWEATING_LEVEL_SCALE", "WEEK_RATING_SCALE",
    "GENDER_OPTIONS", "FAMILY_STATUS_OPTIONS", "PHYSICAL_ACTIVITY_OPTIONS",
    "DIET_QUALITY_OPTIONS", "SMOKING_HABITS_OPTIONS", "DIZZINESS_OPTIONS",
    "THERAPY_FREQUENCY_OPTIONS", "MEDICATION_ADHERENCE_OPTIONS",
    "ALCOHOL_INTAKE_RANGE", "CAFFEINE_INTAKE_RANGE", "SLEEP_HOURS_RANGE",
    "HEART_RATE_RANGE", "BREATHING_RATE_RANGE", "AGE_RANGE",
    "COMMON_OCCUPATIONS", "LIFE_EVENTS_EXAMPLES", "ADVICE_CATEGORIES",
    "PROFESSIONAL_HELP_WARNING", "PLACEHOLDER_ADVICE", "EMOJI", "MESSAGES",
    "ADMIN_MESSAGES",
    # Helpers
    "format_scale_explanation", "format_user_profile", "format_daily_answer",
    "format_statistics", "format_admin_stats", "calculate_week_dates",
    "validate_numeric_input", "validate_float_input", "get_anxiety_category",
    "truncate_text", "safe_json_loads", "format_datetime", "parse_callback_data",
    "create_callback_data", "paginate_list", "format_user_list_item",
    # Charts
    "create_anxiety_chart", "create_stress_chart", "create_combined_chart",
    "create_sleep_chart", "create_distribution_chart", "create_weekly_comparison_chart",
    "create_pie_chart", "create_admin_overview_chart"
]
