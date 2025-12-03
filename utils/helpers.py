"""
Helper functions for formatting and data processing.
"""

from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List
import json


def format_scale_explanation(scale: Dict[int, str], title: str) -> str:
    """Format a scale dictionary into a readable message."""
    lines = [f"📊 **{title}**\n"]
    for value, description in sorted(scale.items()):
        lines.append(f"{value} - {description}")
    return "\n".join(lines)


def format_user_profile(profile: Any) -> str:
    """Format user profile data for display."""
    if not profile:
        return "No profile data available."
    
    sections = []
    
    # Demographics
    demographics = []
    if profile.age:
        demographics.append(f"• Age: {profile.age}")
    if profile.gender:
        demographics.append(f"• Gender: {profile.gender.replace('_', ' ').title()}")
    if profile.occupation:
        demographics.append(f"• Occupation: {profile.occupation}")
    if profile.family_status:
        demographics.append(f"• Family Status: {profile.family_status.replace('_', ' ').title()}")
    
    if demographics:
        sections.append("👤 **Demographics**\n" + "\n".join(demographics))
    
    # Lifestyle
    lifestyle = []
    if profile.sleep_hours is not None:
        lifestyle.append(f"• Sleep: {profile.sleep_hours} hours")
    if profile.physical_activity:
        lifestyle.append(f"• Physical Activity: {profile.physical_activity.title()}")
    if profile.diet_quality:
        lifestyle.append(f"• Diet Quality: {profile.diet_quality.title()}")
    if profile.alcohol_intake is not None:
        lifestyle.append(f"• Alcohol: {profile.alcohol_intake} drinks/week")
    if profile.caffeine_intake is not None:
        lifestyle.append(f"• Caffeine: {profile.caffeine_intake} cups/day")
    if profile.smoking_habits:
        lifestyle.append(f"• Smoking: {profile.smoking_habits.title()}")
    
    if lifestyle:
        sections.append("🏃 **Lifestyle**\n" + "\n".join(lifestyle))
    
    # Health Indicators
    health = []
    if profile.baseline_heart_rate:
        health.append(f"• Heart Rate: {profile.baseline_heart_rate} bpm")
    if profile.baseline_breathing_rate:
        health.append(f"• Breathing Rate: {profile.baseline_breathing_rate}/min")
    if profile.baseline_stress_level:
        health.append(f"• Stress Level: {profile.baseline_stress_level}/10")
    if profile.baseline_anxiety_level:
        health.append(f"• Anxiety Level: {profile.baseline_anxiety_level}/10")
    
    if health:
        sections.append("💊 **Health Indicators**\n" + "\n".join(health))
    
    return "\n\n".join(sections) if sections else "No profile data available."


def format_daily_answer(answer: Any) -> str:
    """Format daily answer for display."""
    if not answer:
        return "No data available."
    
    lines = [f"📅 **{answer.date.strftime('%B %d, %Y')}**\n"]
    
    if answer.stress_level is not None:
        lines.append(f"• Stress Level: {answer.stress_level}/10")
    if answer.anxiety_level is not None:
        lines.append(f"• Anxiety Level: {answer.anxiety_level}/10")
    if answer.heart_rate:
        lines.append(f"• Heart Rate: {answer.heart_rate} bpm")
    if answer.breathing_rate:
        lines.append(f"• Breathing Rate: {answer.breathing_rate}/min")
    if answer.sleep_hours is not None:
        lines.append(f"• Sleep: {answer.sleep_hours} hours")
    if answer.caffeine_intake is not None:
        lines.append(f"• Caffeine: {answer.caffeine_intake} cups")
    if answer.alcohol_intake is not None:
        lines.append(f"• Alcohol: {answer.alcohol_intake} drinks")
    
    if answer.is_extended:
        if answer.mood_rating is not None:
            lines.append(f"• Mood: {answer.mood_rating}/10")
        if answer.energy_level is not None:
            lines.append(f"• Energy: {answer.energy_level}/10")
    
    return "\n".join(lines)


def format_statistics(stats: Dict[str, Any]) -> str:
    """Format user statistics for display."""
    lines = ["📊 **Your Statistics**\n"]
    
    if "total_checkins" in stats:
        lines.append(f"• Total Check-ins: {stats['total_checkins']}")
    
    if "avg_anxiety" in stats:
        lines.append(f"• Average Anxiety: {stats['avg_anxiety']:.1f}/10")
    
    if "avg_stress" in stats:
        lines.append(f"• Average Stress: {stats['avg_stress']:.1f}/10")
    
    if "avg_sleep" in stats:
        lines.append(f"• Average Sleep: {stats['avg_sleep']:.1f} hours")
    
    if "streak" in stats:
        lines.append(f"• Current Streak: {stats['streak']} days 🔥")
    
    if "last_checkin" in stats:
        lines.append(f"• Last Check-in: {stats['last_checkin']}")
    
    return "\n".join(lines)


def format_admin_stats(stats: Dict[str, Any]) -> str:
    """Format admin statistics for display."""
    lines = ["📊 **Admin Dashboard**\n"]
    lines.append("**Overall Statistics:**\n")
    
    if "total_users" in stats:
        lines.append(f"👥 Total Users: {stats['total_users']}")
    
    if "active_7d" in stats:
        lines.append(f"📈 Active (7 days): {stats['active_7d']}")
    
    if "active_30d" in stats:
        lines.append(f"📅 Active (30 days): {stats['active_30d']}")
    
    if "avg_anxiety" in stats:
        lines.append(f"😰 Avg Anxiety: {stats['avg_anxiety']:.1f}/10")
    
    if "total_checkins" in stats:
        lines.append(f"📝 Total Check-ins: {stats['total_checkins']}")
    
    if "new_users_today" in stats:
        lines.append(f"🆕 New Today: {stats['new_users_today']}")
    
    if "new_users_week" in stats:
        lines.append(f"📆 New This Week: {stats['new_users_week']}")
    
    return "\n".join(lines)


def calculate_week_dates() -> tuple:
    """Calculate the start and end dates of the current week."""
    today = datetime.utcnow()
    start = today - timedelta(days=today.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start, end


def validate_numeric_input(value: str, min_val: int, max_val: int) -> Optional[int]:
    """Validate and parse numeric input."""
    try:
        num = int(value)
        if min_val <= num <= max_val:
            return num
        return None
    except ValueError:
        return None


def validate_float_input(value: str, min_val: float, max_val: float) -> Optional[float]:
    """Validate and parse float input."""
    try:
        num = float(value)
        if min_val <= num <= max_val:
            return num
        return None
    except ValueError:
        return None


def get_anxiety_category(level: int) -> str:
    """Get anxiety category based on level."""
    if level <= 3:
        return "low"
    elif level <= 6:
        return "moderate"
    else:
        return "high"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def safe_json_loads(data: str) -> Optional[Dict]:
    """Safely parse JSON string."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime to string."""
    if not dt:
        return "N/A"
    return dt.strftime(format_str)


def parse_callback_data(data: str) -> Dict[str, str]:
    """Parse callback data in format 'action:param1:param2'."""
    parts = data.split(":")
    result = {"action": parts[0]}
    for i, part in enumerate(parts[1:], 1):
        result[f"param{i}"] = part
    return result


def create_callback_data(*args) -> str:
    """Create callback data string from parts."""
    return ":".join(str(arg) for arg in args)


def paginate_list(items: List[Any], page: int, per_page: int = 10) -> tuple:
    """Paginate a list of items."""
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total, total_pages


def format_user_list_item(user: Any, index: int) -> str:
    """Format a user item for list display."""
    name = user.first_name or user.username or f"User {user.id}"
    status = "✅" if user.is_active else "❌"
    return f"{index}. {status} {name} (ID: {user.id})"
