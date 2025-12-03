"""
Settings handlers - Profile editing, notifications, data download, account deletion.
"""

import json
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from keyboards import KeyboardBuilder
from services import UserService, ProfileService, HistoryService, DailyAnswerService
from states import SettingsState
from utils.constants import MESSAGES, EMOJI, AGE_RANGE
from utils.helpers import format_user_profile, validate_numeric_input
from config import settings

router = Router(name="settings")


# ==================== SETTINGS MENU ====================

@router.callback_query(F.data == "menu:settings")
async def show_settings(callback: CallbackQuery, state: FSMContext):
    """Show settings menu."""
    await state.clear()
    await callback.message.edit_text(
        MESSAGES["settings_menu"],
        reply_markup=KeyboardBuilder.settings_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "settings:main")
async def settings_main(callback: CallbackQuery, state: FSMContext):
    """Return to settings main menu."""
    await state.clear()
    await callback.message.edit_text(
        MESSAGES["settings_menu"],
        reply_markup=KeyboardBuilder.settings_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== EDIT PROFILE ====================

@router.callback_query(F.data == "settings:edit_profile")
async def edit_profile_menu(callback: CallbackQuery):
    """Show edit profile menu."""
    user_id = callback.from_user.id
    profile = await ProfileService.get_profile(user_id)
    
    profile_text = format_user_profile(profile)
    
    await callback.message.edit_text(
        f"✏️ **Edit Your Profile**\n\n"
        f"**Current Profile:**\n{profile_text}\n\n"
        f"Select a category to edit:",
        reply_markup=KeyboardBuilder.edit_profile_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "edit:demographics")
async def edit_demographics(callback: CallbackQuery):
    """Show demographics editing options."""
    await callback.message.edit_text(
        f"👤 **Edit Demographics**\n\n"
        f"Select what you want to change:",
        reply_markup=KeyboardBuilder.edit_demographics_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "edit:lifestyle")
async def edit_lifestyle(callback: CallbackQuery):
    """Show lifestyle editing options."""
    await callback.message.edit_text(
        f"🏃 **Edit Lifestyle**\n\n"
        f"Select what you want to change:",
        reply_markup=KeyboardBuilder.edit_lifestyle_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


# Individual field editing
@router.callback_query(F.data == "edit_field:age")
async def edit_age(callback: CallbackQuery, state: FSMContext):
    """Edit age."""
    await state.set_state(SettingsState.edit_age)
    
    await callback.message.edit_text(
        f"📅 **Edit Age**\n\n"
        f"Enter your new age ({AGE_RANGE[0]}-{AGE_RANGE[1]}):",
        reply_markup=KeyboardBuilder.back_cancel_buttons("edit:demographics", "settings:main"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(SettingsState.edit_age)
async def process_edit_age(message: Message, state: FSMContext):
    """Process age edit."""
    age = validate_numeric_input(message.text, AGE_RANGE[0], AGE_RANGE[1])
    
    if age is None:
        await message.answer(
            f"⚠️ Please enter a valid age between {AGE_RANGE[0]} and {AGE_RANGE[1]}."
        )
        return
    
    await ProfileService.update_profile_field(message.from_user.id, "age", age)
    await state.clear()
    
    await message.answer(
        f"✅ Age updated to {age}!",
        reply_markup=KeyboardBuilder.settings_menu(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "edit_field:gender")
async def edit_gender(callback: CallbackQuery, state: FSMContext):
    """Edit gender."""
    await state.set_state(SettingsState.edit_gender)
    
    await callback.message.edit_text(
        f"👤 **Edit Gender**\n\n"
        f"Select your gender:",
        reply_markup=KeyboardBuilder.gender_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(SettingsState.edit_gender, F.data.startswith("gender:"))
async def process_edit_gender(callback: CallbackQuery, state: FSMContext):
    """Process gender edit."""
    gender = callback.data.split(":")[1]
    await ProfileService.update_profile_field(callback.from_user.id, "gender", gender)
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Gender updated!",
        reply_markup=KeyboardBuilder.settings_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "edit_field:sleep_hours")
async def edit_sleep_hours(callback: CallbackQuery, state: FSMContext):
    """Edit sleep hours."""
    await state.set_state(SettingsState.edit_sleep_hours)
    
    await callback.message.edit_text(
        f"😴 **Edit Sleep Hours**\n\n"
        f"Select your typical sleep hours:",
        reply_markup=KeyboardBuilder.sleep_hours_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(SettingsState.edit_sleep_hours, F.data.startswith("sleep:"))
async def process_edit_sleep(callback: CallbackQuery, state: FSMContext):
    """Process sleep hours edit."""
    sleep = float(callback.data.split(":")[1])
    await ProfileService.update_profile_field(callback.from_user.id, "sleep_hours", sleep)
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Sleep hours updated to {sleep}!",
        reply_markup=KeyboardBuilder.settings_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "edit_field:physical_activity")
async def edit_physical_activity(callback: CallbackQuery, state: FSMContext):
    """Edit physical activity."""
    await state.set_state(SettingsState.edit_physical_activity)
    
    await callback.message.edit_text(
        f"🏃 **Edit Physical Activity**\n\n"
        f"Select your activity level:",
        reply_markup=KeyboardBuilder.physical_activity_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(SettingsState.edit_physical_activity, F.data.startswith("activity:"))
async def process_edit_activity(callback: CallbackQuery, state: FSMContext):
    """Process physical activity edit."""
    activity = callback.data.split(":")[1]
    await ProfileService.update_profile_field(callback.from_user.id, "physical_activity", activity)
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Physical activity updated!",
        reply_markup=KeyboardBuilder.settings_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== NOTIFICATIONS ====================

@router.callback_query(F.data == "settings:notifications")
async def notification_settings(callback: CallbackQuery):
    """Show notification settings."""
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    
    enabled = user.notifications_enabled if user else True
    
    status = "✅ Enabled" if enabled else "❌ Disabled"
    
    await callback.message.edit_text(
        f"🔔 **Notification Settings**\n\n"
        f"Weekly reminder notifications are currently: **{status}**\n\n"
        f"These reminders help you stay on track with your mental health check-ins.",
        reply_markup=KeyboardBuilder.notification_settings(enabled),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "notifications:enable")
async def enable_notifications(callback: CallbackQuery):
    """Enable notifications."""
    await UserService.update_user(callback.from_user.id, notifications_enabled=True)
    
    await callback.message.edit_text(
        f"✅ **Notifications Enabled**\n\n"
        f"You will receive weekly reminders for your mental health check-ins.",
        reply_markup=KeyboardBuilder.back_button("settings:main"),
        parse_mode="Markdown"
    )
    await callback.answer("Notifications enabled!")


@router.callback_query(F.data == "notifications:disable")
async def disable_notifications(callback: CallbackQuery):
    """Disable notifications."""
    await UserService.update_user(callback.from_user.id, notifications_enabled=False)
    
    await callback.message.edit_text(
        f"🔕 **Notifications Disabled**\n\n"
        f"You won't receive weekly reminders. You can always enable them again later.",
        reply_markup=KeyboardBuilder.back_button("settings:main"),
        parse_mode="Markdown"
    )
    await callback.answer("Notifications disabled!")


# ==================== DOWNLOAD DATA ====================

@router.callback_query(F.data == "settings:download")
async def download_data(callback: CallbackQuery):
    """Download user data."""
    user_id = callback.from_user.id
    
    # Get user data
    user = await UserService.get_user_with_profile(user_id)
    profile = await ProfileService.get_profile(user_id)
    daily_answers, _ = await DailyAnswerService.get_daily_answers(user_id, days=365)
    
    # Prepare data export
    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "user": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "registered_at": user.registered_at.isoformat() if user.registered_at else None,
            "is_onboarded": user.is_onboarded,
            "notifications_enabled": user.notifications_enabled
        } if user else None,
        "profile": {
            "age": profile.age,
            "gender": profile.gender,
            "occupation": profile.occupation,
            "family_status": profile.family_status,
            "sleep_hours": profile.sleep_hours,
            "physical_activity": profile.physical_activity,
            "diet_quality": profile.diet_quality,
            "alcohol_intake": profile.alcohol_intake,
            "caffeine_intake": profile.caffeine_intake,
            "smoking_habits": profile.smoking_habits,
            "baseline_stress_level": profile.baseline_stress_level,
            "baseline_anxiety_level": profile.baseline_anxiety_level
        } if profile else None,
        "daily_checkins": [
            {
                "date": answer.date.isoformat(),
                "stress_level": answer.stress_level,
                "anxiety_level": answer.anxiety_level,
                "heart_rate": answer.heart_rate,
                "breathing_rate": answer.breathing_rate,
                "sleep_hours": answer.sleep_hours,
                "caffeine_intake": answer.caffeine_intake,
                "alcohol_intake": answer.alcohol_intake
            }
            for answer in daily_answers
        ]
    }
    
    # Create JSON file
    json_bytes = json.dumps(export_data, indent=2).encode('utf-8')
    
    await callback.message.delete()
    await callback.message.answer_document(
        document=BufferedInputFile(json_bytes, filename=f"mental_health_data_{user_id}.json"),
        caption="📥 **Your Data Export**\n\nHere's all your data from the Mental Health Bot.",
        reply_markup=KeyboardBuilder.back_button("settings:main"),
        parse_mode="Markdown"
    )
    await callback.answer("Data exported!")


# ==================== DELETE ACCOUNT ====================

@router.callback_query(F.data == "settings:delete")
async def delete_account_prompt(callback: CallbackQuery):
    """Show delete account confirmation."""
    await callback.message.edit_text(
        f"⚠️ **Delete Account**\n\n"
        f"**Warning:** This action cannot be undone!\n\n"
        f"Deleting your account will permanently remove:\n"
        f"• Your profile information\n"
        f"• All check-in history\n"
        f"• All predictions and feedback\n\n"
        f"Are you sure you want to delete your account?",
        reply_markup=KeyboardBuilder.delete_account_confirm(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "delete:confirm")
async def delete_account_final_confirm(callback: CallbackQuery):
    """Show final delete confirmation."""
    await callback.message.edit_text(
        f"🚨 **FINAL WARNING**\n\n"
        f"You are about to **permanently delete** your account.\n\n"
        f"This action is **irreversible**.\n\n"
        f"Type 'DELETE' to confirm or go back.",
        reply_markup=KeyboardBuilder.delete_account_final(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "delete:final")
async def delete_account_execute(callback: CallbackQuery, state: FSMContext):
    """Execute account deletion."""
    user_id = callback.from_user.id
    
    # Delete user and all associated data
    success = await UserService.delete_user(user_id)
    
    await state.clear()
    
    if success:
        await callback.message.edit_text(
            f"👋 **Account Deleted**\n\n"
            f"Your account and all associated data have been permanently deleted.\n\n"
            f"Thank you for using Mental Health Bot. Take care of yourself!\n\n"
            f"If you change your mind, you can always start fresh with /start",
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            f"⚠️ **Error**\n\n"
            f"There was an error deleting your account. Please try again later.",
            reply_markup=KeyboardBuilder.back_button("settings:main"),
            parse_mode="Markdown"
        )
    
    await callback.answer()
