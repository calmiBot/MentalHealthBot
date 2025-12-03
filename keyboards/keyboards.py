"""
Keyboard builders for the Mental Health Bot.
Provides inline keyboards, reply keyboards, and pagination.
"""

from typing import List, Tuple, Optional, Any
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from utils.constants import (
    GENDER_OPTIONS, FAMILY_STATUS_OPTIONS, PHYSICAL_ACTIVITY_OPTIONS,
    DIET_QUALITY_OPTIONS, SMOKING_HABITS_OPTIONS, DIZZINESS_OPTIONS,
    THERAPY_FREQUENCY_OPTIONS, MEDICATION_ADHERENCE_OPTIONS,
    STRESS_LEVEL_SCALE, ANXIETY_LEVEL_SCALE, MOOD_RATING_SCALE,
    ENERGY_LEVEL_SCALE, SWEATING_LEVEL_SCALE, WEEK_RATING_SCALE,
    COMMON_OCCUPATIONS, EMOJI
)


class KeyboardBuilder:
    """Unified keyboard builder for the bot."""
    
    # ==================== NAVIGATION KEYBOARDS ====================
    
    @staticmethod
    def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
        """Build main menu keyboard."""
        builder = InlineKeyboardBuilder()
        
        # User options
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['check']} Daily Check-in", callback_data="menu:checkin"),
            InlineKeyboardButton(text=f"{EMOJI['calendar']} Weekly Assessment", callback_data="menu:weekly")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['chart']} My Statistics", callback_data="menu:stats"),
            InlineKeyboardButton(text=f"{EMOJI['folder']} History", callback_data="menu:history")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['settings']} Settings", callback_data="menu:settings"),
            InlineKeyboardButton(text=f"{EMOJI['help']} Help", callback_data="menu:help")
        )
        
        # Admin option
        if is_admin:
            builder.row(
                InlineKeyboardButton(text=f"{EMOJI['admin']} Admin Panel", callback_data="menu:admin")
            )
        
        return builder.as_markup()
    
    @staticmethod
    def back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
        """Build a simple back button."""
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data=callback_data))
        return builder.as_markup()
    
    @staticmethod
    def back_cancel_buttons(back_data: str = "back", cancel_data: str = "cancel") -> InlineKeyboardMarkup:
        """Build back and cancel buttons."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data=back_data),
            InlineKeyboardButton(text=f"{EMOJI['cross']} Cancel", callback_data=cancel_data)
        )
        return builder.as_markup()
    
    @staticmethod
    def confirm_cancel(confirm_data: str = "confirm", cancel_data: str = "cancel") -> InlineKeyboardMarkup:
        """Build confirm and cancel buttons."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['check']} Confirm", callback_data=confirm_data),
            InlineKeyboardButton(text=f"{EMOJI['cross']} Cancel", callback_data=cancel_data)
        )
        return builder.as_markup()
    
    @staticmethod
    def yes_no(yes_data: str = "yes", no_data: str = "no") -> InlineKeyboardMarkup:
        """Build yes/no buttons."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['check']} Yes", callback_data=yes_data),
            InlineKeyboardButton(text=f"{EMOJI['cross']} No", callback_data=no_data)
        )
        return builder.as_markup()
    
    # ==================== ONBOARDING KEYBOARDS ====================
    
    @staticmethod
    def start_onboarding() -> InlineKeyboardMarkup:
        """Build start onboarding keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['rocket']} Let's Begin!", callback_data="onboarding:start")
        )
        return builder.as_markup()
    
    @staticmethod
    def gender_options() -> InlineKeyboardMarkup:
        """Build gender selection keyboard."""
        builder = InlineKeyboardBuilder()
        for label, value in GENDER_OPTIONS:
            builder.row(InlineKeyboardButton(text=label, callback_data=f"gender:{value}"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def family_status_options() -> InlineKeyboardMarkup:
        """Build family status selection keyboard."""
        builder = InlineKeyboardBuilder()
        for label, value in FAMILY_STATUS_OPTIONS:
            builder.row(InlineKeyboardButton(text=label, callback_data=f"family_status:{value}"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def physical_activity_options() -> InlineKeyboardMarkup:
        """Build physical activity selection keyboard."""
        builder = InlineKeyboardBuilder()
        for label, value in PHYSICAL_ACTIVITY_OPTIONS:
            builder.row(InlineKeyboardButton(text=label, callback_data=f"activity:{value}"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def diet_quality_options() -> InlineKeyboardMarkup:
        """Build diet quality selection keyboard."""
        builder = InlineKeyboardBuilder()
        for label, value in DIET_QUALITY_OPTIONS:
            builder.row(InlineKeyboardButton(text=label, callback_data=f"diet:{value}"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def smoking_options() -> InlineKeyboardMarkup:
        """Build smoking habits selection keyboard."""
        builder = InlineKeyboardBuilder()
        for label, value in SMOKING_HABITS_OPTIONS:
            builder.row(InlineKeyboardButton(text=label, callback_data=f"smoking:{value}"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def dizziness_options() -> InlineKeyboardMarkup:
        """Build dizziness frequency selection keyboard."""
        builder = InlineKeyboardBuilder()
        for label, value in DIZZINESS_OPTIONS:
            builder.row(InlineKeyboardButton(text=label, callback_data=f"dizziness:{value}"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def therapy_frequency_options() -> InlineKeyboardMarkup:
        """Build therapy frequency selection keyboard."""
        builder = InlineKeyboardBuilder()
        for label, value in THERAPY_FREQUENCY_OPTIONS:
            builder.row(InlineKeyboardButton(text=label, callback_data=f"therapy:{value}"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def medication_options() -> InlineKeyboardMarkup:
        """Build medication options keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="💊 Yes, currently taking", callback_data="medication:yes"))
        builder.row(InlineKeyboardButton(text="❌ No medication", callback_data="medication:no"))
        builder.row(InlineKeyboardButton(text="📋 Prefer not to say", callback_data="medication:prefer_not"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def family_anxiety_history() -> InlineKeyboardMarkup:
        """Build family anxiety history keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="✅ Yes", callback_data="family_history:yes"))
        builder.row(InlineKeyboardButton(text="❌ No", callback_data="family_history:no"))
        builder.row(InlineKeyboardButton(text="❓ Not sure", callback_data="family_history:unsure"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def occupation_options() -> InlineKeyboardMarkup:
        """Build occupation selection keyboard."""
        builder = InlineKeyboardBuilder()
        for occupation in COMMON_OCCUPATIONS:
            builder.row(InlineKeyboardButton(text=occupation, callback_data=f"occupation:{occupation}"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    # ==================== NUMERIC SCALE KEYBOARDS ====================
    
    @staticmethod
    def numeric_scale(min_val: int, max_val: int, prefix: str, 
                      scale_dict: Optional[dict] = None, cols: int = 5) -> InlineKeyboardMarkup:
        """Build a numeric scale keyboard with optional explanations."""
        builder = InlineKeyboardBuilder()
        
        buttons = []
        for i in range(min_val, max_val + 1):
            if scale_dict and i in scale_dict:
                # Extract emoji from scale description
                emoji = scale_dict[i].split()[0] if scale_dict[i] else str(i)
                text = emoji if len(emoji) <= 4 else str(i)
            else:
                text = str(i)
            buttons.append(InlineKeyboardButton(text=text, callback_data=f"{prefix}:{i}"))
        
        # Arrange in rows
        for i in range(0, len(buttons), cols):
            builder.row(*buttons[i:i+cols])
        
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def stress_level_keyboard() -> InlineKeyboardMarkup:
        """Build stress level selection keyboard (1-10)."""
        return KeyboardBuilder.numeric_scale(1, 10, "stress", STRESS_LEVEL_SCALE)
    
    @staticmethod
    def anxiety_level_keyboard() -> InlineKeyboardMarkup:
        """Build anxiety level selection keyboard (1-10)."""
        return KeyboardBuilder.numeric_scale(1, 10, "anxiety", ANXIETY_LEVEL_SCALE)
    
    @staticmethod
    def mood_rating_keyboard() -> InlineKeyboardMarkup:
        """Build mood rating selection keyboard (1-10)."""
        return KeyboardBuilder.numeric_scale(1, 10, "mood", MOOD_RATING_SCALE)
    
    @staticmethod
    def energy_level_keyboard() -> InlineKeyboardMarkup:
        """Build energy level selection keyboard (1-10)."""
        return KeyboardBuilder.numeric_scale(1, 10, "energy", ENERGY_LEVEL_SCALE)
    
    @staticmethod
    def sweating_level_keyboard() -> InlineKeyboardMarkup:
        """Build sweating level selection keyboard (1-5)."""
        return KeyboardBuilder.numeric_scale(1, 5, "sweating", SWEATING_LEVEL_SCALE)
    
    @staticmethod
    def week_rating_keyboard() -> InlineKeyboardMarkup:
        """Build week rating selection keyboard (1-10)."""
        return KeyboardBuilder.numeric_scale(1, 10, "week_rating", WEEK_RATING_SCALE)
    
    @staticmethod
    def alcohol_intake_keyboard() -> InlineKeyboardMarkup:
        """Build alcohol intake selection keyboard (0-19 drinks)."""
        builder = InlineKeyboardBuilder()
        
        # Row 1: 0-4
        builder.row(*[InlineKeyboardButton(text=str(i), callback_data=f"alcohol:{i}") for i in range(0, 5)])
        # Row 2: 5-9
        builder.row(*[InlineKeyboardButton(text=str(i), callback_data=f"alcohol:{i}") for i in range(5, 10)])
        # Row 3: 10-14
        builder.row(*[InlineKeyboardButton(text=str(i), callback_data=f"alcohol:{i}") for i in range(10, 15)])
        # Row 4: 15-19
        builder.row(*[InlineKeyboardButton(text=str(i), callback_data=f"alcohol:{i}") for i in range(15, 20)])
        
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def caffeine_intake_keyboard() -> InlineKeyboardMarkup:
        """Build caffeine intake selection keyboard (0-15 cups)."""
        builder = InlineKeyboardBuilder()
        
        # Row 1: 0-4
        builder.row(*[InlineKeyboardButton(text=f"☕ {i}", callback_data=f"caffeine:{i}") for i in range(0, 5)])
        # Row 2: 5-9
        builder.row(*[InlineKeyboardButton(text=f"☕ {i}", callback_data=f"caffeine:{i}") for i in range(5, 10)])
        # Row 3: 10-15
        builder.row(*[InlineKeyboardButton(text=f"☕ {i}", callback_data=f"caffeine:{i}") for i in range(10, 16)])
        
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def sleep_hours_keyboard() -> InlineKeyboardMarkup:
        """Build sleep hours selection keyboard (0-16 hours)."""
        builder = InlineKeyboardBuilder()
        
        # Common sleep hours
        common_hours = [4, 5, 6, 7, 8, 9, 10]
        builder.row(*[InlineKeyboardButton(text=f"😴 {h}h", callback_data=f"sleep:{h}") for h in common_hours[:4]])
        builder.row(*[InlineKeyboardButton(text=f"😴 {h}h", callback_data=f"sleep:{h}") for h in common_hours[4:]])
        
        # More options
        builder.row(
            InlineKeyboardButton(text="< 4h", callback_data="sleep:3"),
            InlineKeyboardButton(text="10-12h", callback_data="sleep:11"),
            InlineKeyboardButton(text="> 12h", callback_data="sleep:13")
        )
        
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def heart_rate_keyboard() -> InlineKeyboardMarkup:
        """Build heart rate selection keyboard with common ranges."""
        builder = InlineKeyboardBuilder()
        
        # Common heart rate ranges
        builder.row(
            InlineKeyboardButton(text="💓 < 60", callback_data="hr:55"),
            InlineKeyboardButton(text="💓 60-70", callback_data="hr:65"),
            InlineKeyboardButton(text="💓 70-80", callback_data="hr:75")
        )
        builder.row(
            InlineKeyboardButton(text="💓 80-90", callback_data="hr:85"),
            InlineKeyboardButton(text="💓 90-100", callback_data="hr:95"),
            InlineKeyboardButton(text="💓 > 100", callback_data="hr:105")
        )
        builder.row(
            InlineKeyboardButton(text="📝 Enter manually", callback_data="hr:manual"),
            InlineKeyboardButton(text="❓ Don't know", callback_data="hr:skip")
        )
        
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    @staticmethod
    def breathing_rate_keyboard() -> InlineKeyboardMarkup:
        """Build breathing rate selection keyboard."""
        builder = InlineKeyboardBuilder()
        
        # Common breathing rate ranges
        builder.row(
            InlineKeyboardButton(text="🌬️ 8-12", callback_data="br:10"),
            InlineKeyboardButton(text="🌬️ 12-16", callback_data="br:14"),
            InlineKeyboardButton(text="🌬️ 16-20", callback_data="br:18")
        )
        builder.row(
            InlineKeyboardButton(text="🌬️ 20-25", callback_data="br:22"),
            InlineKeyboardButton(text="🌬️ > 25", callback_data="br:28")
        )
        builder.row(
            InlineKeyboardButton(text="📝 Enter manually", callback_data="br:manual"),
            InlineKeyboardButton(text="❓ Don't know", callback_data="br:skip")
        )
        
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="onboarding:back"))
        return builder.as_markup()
    
    # ==================== DAILY CHECK-IN KEYBOARDS ====================
    
    @staticmethod
    def daily_check_start() -> InlineKeyboardMarkup:
        """Build daily check-in start keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['check']} Start Check-in", callback_data="daily:start")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back to Menu", callback_data="menu:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def extended_form_prompt() -> InlineKeyboardMarkup:
        """Build extended form prompt keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="📝 Show All Questions", callback_data="daily:extended"),
            InlineKeyboardButton(text="✅ Complete Now", callback_data="daily:complete")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="daily:back")
        )
        return builder.as_markup()
    
    @staticmethod
    def dizziness_today() -> InlineKeyboardMarkup:
        """Build dizziness today keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="✅ Yes", callback_data="dizziness_today:yes"),
            InlineKeyboardButton(text="❌ No", callback_data="dizziness_today:no")
        )
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="daily:back"))
        return builder.as_markup()
    
    # ==================== SETTINGS KEYBOARDS ====================
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Build settings menu keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['edit']} Edit Profile", callback_data="settings:edit_profile")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['bell']} Notifications", callback_data="settings:notifications")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['download']} Download My Data", callback_data="settings:download")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['delete']} Delete Account", callback_data="settings:delete")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back to Menu", callback_data="menu:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def edit_profile_menu() -> InlineKeyboardMarkup:
        """Build edit profile menu keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="👤 Demographics", callback_data="edit:demographics"),
            InlineKeyboardButton(text="🏃 Lifestyle", callback_data="edit:lifestyle")
        )
        builder.row(
            InlineKeyboardButton(text="💊 Health", callback_data="edit:health"),
            InlineKeyboardButton(text="🧠 Mental Health", callback_data="edit:mental_health")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="settings:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def edit_demographics_menu() -> InlineKeyboardMarkup:
        """Build edit demographics menu keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="📅 Age", callback_data="edit_field:age"))
        builder.row(InlineKeyboardButton(text="👤 Gender", callback_data="edit_field:gender"))
        builder.row(InlineKeyboardButton(text="💼 Occupation", callback_data="edit_field:occupation"))
        builder.row(InlineKeyboardButton(text="💑 Family Status", callback_data="edit_field:family_status"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="settings:edit_profile"))
        return builder.as_markup()
    
    @staticmethod
    def edit_lifestyle_menu() -> InlineKeyboardMarkup:
        """Build edit lifestyle menu keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="😴 Sleep Hours", callback_data="edit_field:sleep_hours"))
        builder.row(InlineKeyboardButton(text="🏃 Physical Activity", callback_data="edit_field:physical_activity"))
        builder.row(InlineKeyboardButton(text="🥗 Diet Quality", callback_data="edit_field:diet_quality"))
        builder.row(InlineKeyboardButton(text="🍷 Alcohol Intake", callback_data="edit_field:alcohol_intake"))
        builder.row(InlineKeyboardButton(text="☕ Caffeine Intake", callback_data="edit_field:caffeine_intake"))
        builder.row(InlineKeyboardButton(text="🚬 Smoking Habits", callback_data="edit_field:smoking_habits"))
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="settings:edit_profile"))
        return builder.as_markup()
    
    @staticmethod
    def notification_settings(enabled: bool) -> InlineKeyboardMarkup:
        """Build notification settings keyboard."""
        builder = InlineKeyboardBuilder()
        
        if enabled:
            builder.row(
                InlineKeyboardButton(text=f"{EMOJI['mute']} Disable Notifications", callback_data="notifications:disable")
            )
        else:
            builder.row(
                InlineKeyboardButton(text=f"{EMOJI['bell']} Enable Notifications", callback_data="notifications:enable")
            )
        
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="settings:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def delete_account_confirm() -> InlineKeyboardMarkup:
        """Build delete account confirmation keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"⚠️ Yes, Delete My Account", callback_data="delete:confirm")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} No, Go Back", callback_data="settings:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def delete_account_final() -> InlineKeyboardMarkup:
        """Build final delete account confirmation keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"🗑️ DELETE PERMANENTLY", callback_data="delete:final")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Cancel", callback_data="settings:main")
        )
        return builder.as_markup()
    
    # ==================== FEEDBACK KEYBOARDS ====================
    
    @staticmethod
    def feedback_reaction(prediction_id: int) -> InlineKeyboardMarkup:
        """Build feedback reaction keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['thumbs_up']} Helpful", callback_data=f"feedback:{prediction_id}:helpful"),
            InlineKeyboardButton(text=f"{EMOJI['thumbs_down']} Not Accurate", callback_data=f"feedback:{prediction_id}:not_accurate")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['speech']} Tell Us More", callback_data=f"feedback:{prediction_id}:detailed")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['cross']} Skip", callback_data="feedback:skip")
        )
        return builder.as_markup()
    
    # ==================== ADMIN KEYBOARDS ====================
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Build admin menu keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['chart']} Overview Stats", callback_data="admin:stats"),
            InlineKeyboardButton(text=f"📈 Charts", callback_data="admin:charts")
        )
        builder.row(
            InlineKeyboardButton(text=f"👥 User List", callback_data="admin:users"),
            InlineKeyboardButton(text=f"{EMOJI['download']} Export Data", callback_data="admin:export")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back to Menu", callback_data="menu:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def admin_export_options() -> InlineKeyboardMarkup:
        """Build admin export options keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="📊 All Users", callback_data="export:users"),
            InlineKeyboardButton(text="📝 All Check-ins", callback_data="export:checkins")
        )
        builder.row(
            InlineKeyboardButton(text="💭 Feedback", callback_data="export:feedback"),
            InlineKeyboardButton(text="🔮 Predictions", callback_data="export:predictions")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data="admin:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def pagination(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        """Build pagination keyboard."""
        builder = InlineKeyboardBuilder()
        
        buttons = []
        
        # Previous button
        if current_page > 1:
            buttons.append(InlineKeyboardButton(text="◀️ Prev", callback_data=f"{prefix}:page:{current_page - 1}"))
        
        # Page indicator
        buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop"))
        
        # Next button
        if current_page < total_pages:
            buttons.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"{prefix}:page:{current_page + 1}"))
        
        builder.row(*buttons)
        builder.row(InlineKeyboardButton(text=f"{EMOJI['back']} Back", callback_data=f"{prefix}:back"))
        
        return builder.as_markup()
    
    @staticmethod
    def user_details(user_id: int) -> InlineKeyboardMarkup:
        """Build user details keyboard for admin."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="📊 View Stats", callback_data=f"admin_user:{user_id}:stats"),
            InlineKeyboardButton(text="📝 View History", callback_data=f"admin_user:{user_id}:history")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back to List", callback_data="admin:users")
        )
        return builder.as_markup()
    
    # ==================== HISTORY & STATS KEYBOARDS ====================
    
    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """Build stats menu keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="📈 Anxiety Chart", callback_data="stats:anxiety_chart"),
            InlineKeyboardButton(text="📊 Stress Chart", callback_data="stats:stress_chart")
        )
        builder.row(
            InlineKeyboardButton(text="😴 Sleep Chart", callback_data="stats:sleep_chart"),
            InlineKeyboardButton(text="📉 Combined View", callback_data="stats:combined_chart")
        )
        builder.row(
            InlineKeyboardButton(text="📋 Summary", callback_data="stats:summary")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back to Menu", callback_data="menu:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def history_menu() -> InlineKeyboardMarkup:
        """Build history menu keyboard."""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="📅 Daily Check-ins", callback_data="history:daily"),
            InlineKeyboardButton(text="📆 Weekly Assessments", callback_data="history:weekly")
        )
        builder.row(
            InlineKeyboardButton(text="🔮 Predictions", callback_data="history:predictions"),
            InlineKeyboardButton(text="💬 Feedback", callback_data="history:feedback")
        )
        builder.row(
            InlineKeyboardButton(text=f"{EMOJI['back']} Back to Menu", callback_data="menu:main")
        )
        return builder.as_markup()
