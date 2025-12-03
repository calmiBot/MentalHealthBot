"""
Daily check-in handlers.
"""

from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import KeyboardBuilder
from services import (
    DailyAnswerService, PredictionService, HistoryService,
    call_ai_model
)
from states import DailyCheckState, FeedbackState
from utils.constants import (
    MESSAGES, EMOJI, STRESS_LEVEL_SCALE, ANXIETY_LEVEL_SCALE,
    MOOD_RATING_SCALE, ENERGY_LEVEL_SCALE, SWEATING_LEVEL_SCALE,
    PROFESSIONAL_HELP_WARNING
)
from utils.helpers import format_scale_explanation, validate_numeric_input, get_anxiety_category

router = Router(name="daily_check")


# ==================== START DAILY CHECK-IN ====================

@router.callback_query(F.data == "menu:checkin")
async def start_daily_checkin(callback: CallbackQuery, state: FSMContext):
    """Start daily check-in from menu."""
    user_id = callback.from_user.id
    
    # Check if already checked in today
    has_checked = await DailyAnswerService.has_checked_in_today(user_id)
    
    if has_checked:
        await callback.message.edit_text(
            f"✅ **You've already completed today's check-in!**\n\n"
            f"Come back tomorrow for your next check-in.\n\n"
            f"In the meantime, you can view your statistics or history.",
            reply_markup=KeyboardBuilder.back_button("menu:main"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        MESSAGES["daily_check_intro"],
        reply_markup=KeyboardBuilder.daily_check_start(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "daily:start")
async def daily_start(callback: CallbackQuery, state: FSMContext):
    """Begin daily check-in questions."""
    await state.set_state(DailyCheckState.stress_level)
    await state.update_data(is_extended=False)
    
    explanation = format_scale_explanation(STRESS_LEVEL_SCALE, "Stress Level")
    
    await callback.message.edit_text(
        f"😰 **Question 1/7: Stress Level**\n\n"
        f"How stressed are you feeling right now?\n\n"
        f"{explanation}",
        reply_markup=KeyboardBuilder.stress_level_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== ESSENTIAL QUESTIONS (1-7) ====================

@router.callback_query(DailyCheckState.stress_level, F.data.startswith("stress:"))
async def process_daily_stress(callback: CallbackQuery, state: FSMContext):
    """Process stress level."""
    stress = int(callback.data.split(":")[1])
    await state.update_data(stress_level=stress)
    await state.set_state(DailyCheckState.sleep_hours)
    
    await callback.message.edit_text(
        f"😴 **Question 2/7: Sleep**\n\n"
        f"How many hours did you sleep last night?",
        reply_markup=KeyboardBuilder.sleep_hours_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DailyCheckState.sleep_hours, F.data.startswith("sleep:"))
async def process_daily_sleep(callback: CallbackQuery, state: FSMContext):
    """Process sleep hours."""
    sleep = float(callback.data.split(":")[1])
    await state.update_data(sleep_hours=sleep)
    await state.set_state(DailyCheckState.heart_rate)
    
    await callback.message.edit_text(
        f"💓 **Question 3/7: Heart Rate**\n\n"
        f"What's your approximate heart rate (bpm)?\n\n"
        f"_You can measure this by counting your pulse for 15 seconds and multiplying by 4._",
        reply_markup=KeyboardBuilder.heart_rate_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DailyCheckState.heart_rate, F.data.startswith("hr:"))
async def process_daily_heart_rate(callback: CallbackQuery, state: FSMContext):
    """Process heart rate."""
    hr_value = callback.data.split(":")[1]
    
    if hr_value == "manual":
        await callback.message.edit_text(
            f"💓 **Enter Heart Rate**\n\n"
            f"Please type your heart rate (40-200 bpm):",
            reply_markup=KeyboardBuilder.back_cancel_buttons("daily:back", "cancel"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    elif hr_value == "skip":
        await state.update_data(heart_rate=None)
    else:
        await state.update_data(heart_rate=int(hr_value))
    
    await state.set_state(DailyCheckState.breathing_rate)
    
    await callback.message.edit_text(
        f"🌬️ **Question 4/7: Breathing Rate**\n\n"
        f"What's your breathing rate (breaths per minute)?\n\n"
        f"_Normal range is 12-20 breaths per minute._",
        reply_markup=KeyboardBuilder.breathing_rate_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(DailyCheckState.heart_rate)
async def process_manual_heart_rate(message: Message, state: FSMContext):
    """Process manually entered heart rate."""
    hr = validate_numeric_input(message.text, 40, 200)
    
    if hr is None:
        await message.answer(
            "⚠️ Please enter a valid heart rate between 40 and 200 bpm.",
            reply_markup=KeyboardBuilder.back_cancel_buttons("daily:back", "cancel")
        )
        return
    
    await state.update_data(heart_rate=hr)
    await state.set_state(DailyCheckState.breathing_rate)
    
    await message.answer(
        f"🌬️ **Question 4/7: Breathing Rate**\n\n"
        f"What's your breathing rate (breaths per minute)?",
        reply_markup=KeyboardBuilder.breathing_rate_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(DailyCheckState.breathing_rate, F.data.startswith("br:"))
async def process_daily_breathing_rate(callback: CallbackQuery, state: FSMContext):
    """Process breathing rate."""
    br_value = callback.data.split(":")[1]
    
    if br_value == "manual":
        await callback.message.edit_text(
            f"🌬️ **Enter Breathing Rate**\n\n"
            f"Please type your breathing rate (8-30 breaths/min):",
            reply_markup=KeyboardBuilder.back_cancel_buttons("daily:back", "cancel"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    elif br_value == "skip":
        await state.update_data(breathing_rate=None)
    else:
        await state.update_data(breathing_rate=int(br_value))
    
    await state.set_state(DailyCheckState.caffeine_intake)
    
    await callback.message.edit_text(
        f"☕ **Question 5/7: Caffeine Today**\n\n"
        f"How many caffeinated drinks have you had today?",
        reply_markup=KeyboardBuilder.caffeine_intake_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(DailyCheckState.breathing_rate)
async def process_manual_breathing_rate(message: Message, state: FSMContext):
    """Process manually entered breathing rate."""
    br = validate_numeric_input(message.text, 8, 30)
    
    if br is None:
        await message.answer(
            "⚠️ Please enter a valid breathing rate between 8 and 30 breaths/min."
        )
        return
    
    await state.update_data(breathing_rate=br)
    await state.set_state(DailyCheckState.caffeine_intake)
    
    await message.answer(
        f"☕ **Question 5/7: Caffeine Today**\n\n"
        f"How many caffeinated drinks have you had today?",
        reply_markup=KeyboardBuilder.caffeine_intake_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(DailyCheckState.caffeine_intake, F.data.startswith("caffeine:"))
async def process_daily_caffeine(callback: CallbackQuery, state: FSMContext):
    """Process caffeine intake."""
    caffeine = int(callback.data.split(":")[1])
    await state.update_data(caffeine_intake=caffeine)
    await state.set_state(DailyCheckState.alcohol_intake)
    
    await callback.message.edit_text(
        f"🍷 **Question 6/7: Alcohol Today**\n\n"
        f"How many alcoholic drinks have you had today?",
        reply_markup=KeyboardBuilder.alcohol_intake_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DailyCheckState.alcohol_intake, F.data.startswith("alcohol:"))
async def process_daily_alcohol(callback: CallbackQuery, state: FSMContext):
    """Process alcohol intake."""
    alcohol = int(callback.data.split(":")[1])
    await state.update_data(alcohol_intake=alcohol)
    await state.set_state(DailyCheckState.anxiety_level)
    
    explanation = format_scale_explanation(ANXIETY_LEVEL_SCALE, "Anxiety Level")
    
    await callback.message.edit_text(
        f"😟 **Question 7/7: Anxiety Level**\n\n"
        f"Rate your current anxiety level:\n\n"
        f"{explanation}",
        reply_markup=KeyboardBuilder.anxiety_level_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DailyCheckState.anxiety_level, F.data.startswith("anxiety:"))
async def process_daily_anxiety(callback: CallbackQuery, state: FSMContext):
    """Process anxiety level and offer extended questions."""
    anxiety = int(callback.data.split(":")[1])
    await state.update_data(anxiety_level=anxiety)
    await state.set_state(DailyCheckState.show_extended)
    
    await callback.message.edit_text(
        MESSAGES["extended_form_prompt"] + "\n\n"
        f"💡 _For the highest accuracy, we recommend completing all questions._",
        reply_markup=KeyboardBuilder.extended_form_prompt(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== EXTENDED QUESTIONS ====================

@router.callback_query(DailyCheckState.show_extended, F.data == "daily:extended")
async def start_extended_questions(callback: CallbackQuery, state: FSMContext):
    """Start extended questions."""
    await state.update_data(is_extended=True)
    await state.set_state(DailyCheckState.mood_rating)
    
    explanation = format_scale_explanation(MOOD_RATING_SCALE, "Mood Rating")
    
    await callback.message.edit_text(
        f"😊 **Extended Question 1/5: Mood**\n\n"
        f"How would you rate your overall mood today?\n\n"
        f"{explanation}",
        reply_markup=KeyboardBuilder.mood_rating_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DailyCheckState.mood_rating, F.data.startswith("mood:"))
async def process_mood_rating(callback: CallbackQuery, state: FSMContext):
    """Process mood rating."""
    mood = int(callback.data.split(":")[1])
    await state.update_data(mood_rating=mood)
    await state.set_state(DailyCheckState.energy_level)
    
    explanation = format_scale_explanation(ENERGY_LEVEL_SCALE, "Energy Level")
    
    await callback.message.edit_text(
        f"⚡ **Extended Question 2/5: Energy**\n\n"
        f"How would you rate your energy level today?\n\n"
        f"{explanation}",
        reply_markup=KeyboardBuilder.energy_level_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DailyCheckState.energy_level, F.data.startswith("energy:"))
async def process_energy_level(callback: CallbackQuery, state: FSMContext):
    """Process energy level."""
    energy = int(callback.data.split(":")[1])
    await state.update_data(energy_level=energy)
    await state.set_state(DailyCheckState.sweating_level)
    
    explanation = format_scale_explanation(SWEATING_LEVEL_SCALE, "Sweating Level")
    
    await callback.message.edit_text(
        f"💧 **Extended Question 3/5: Sweating**\n\n"
        f"How much have you been sweating today (not from exercise)?\n\n"
        f"{explanation}",
        reply_markup=KeyboardBuilder.sweating_level_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DailyCheckState.sweating_level, F.data.startswith("sweating:"))
async def process_sweating_level(callback: CallbackQuery, state: FSMContext):
    """Process sweating level."""
    sweating = int(callback.data.split(":")[1])
    await state.update_data(sweating_level=sweating)
    await state.set_state(DailyCheckState.dizziness_today)
    
    await callback.message.edit_text(
        f"😵 **Extended Question 4/5: Dizziness**\n\n"
        f"Have you experienced any dizziness today?",
        reply_markup=KeyboardBuilder.dizziness_today(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DailyCheckState.dizziness_today, F.data.startswith("dizziness_today:"))
async def process_dizziness_today(callback: CallbackQuery, state: FSMContext):
    """Process dizziness today."""
    dizziness = callback.data.split(":")[1] == "yes"
    await state.update_data(dizziness_today=dizziness)
    await state.set_state(DailyCheckState.notes)
    
    await callback.message.edit_text(
        f"📝 **Extended Question 5/5: Notes**\n\n"
        f"Any additional notes about how you're feeling today?\n\n"
        f"Type your notes or type 'skip' to continue:",
        reply_markup=KeyboardBuilder.back_cancel_buttons("daily:back", "cancel"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(DailyCheckState.notes)
async def process_notes(message: Message, state: FSMContext):
    """Process notes and complete check-in."""
    notes = message.text if message.text.lower() != "skip" else None
    await state.update_data(notes=notes)
    
    # Complete the check-in
    await complete_daily_checkin(message, state)


# ==================== COMPLETE CHECK-IN ====================

@router.callback_query(DailyCheckState.show_extended, F.data == "daily:complete")
async def complete_without_extended(callback: CallbackQuery, state: FSMContext):
    """Complete check-in without extended questions."""
    await complete_daily_checkin(callback, state, is_callback=True)


async def complete_daily_checkin(event, state: FSMContext, is_callback: bool = False):
    """Complete the daily check-in and save data."""
    user_id = event.from_user.id
    data = await state.get_data()
    
    # Save daily answer
    daily_answer = await DailyAnswerService.create_daily_answer(
        user_id=user_id,
        stress_level=data.get('stress_level'),
        heart_rate=data.get('heart_rate'),
        breathing_rate=data.get('breathing_rate'),
        sleep_hours=data.get('sleep_hours'),
        caffeine_intake=data.get('caffeine_intake'),
        alcohol_intake=data.get('alcohol_intake'),
        anxiety_level=data.get('anxiety_level'),
        mood_rating=data.get('mood_rating'),
        energy_level=data.get('energy_level'),
        sweating_level=data.get('sweating_level'),
        dizziness_today=data.get('dizziness_today'),
        notes=data.get('notes'),
        is_extended=data.get('is_extended', False)
    )
    
    # Get AI prediction
    ai_result = await call_ai_model(data)
    
    # Save prediction
    prediction = await PredictionService.create_prediction(
        user_id=user_id,
        predicted_anxiety_level=ai_result['predicted_anxiety_level'],
        advice=ai_result['advice'],
        advice_category=ai_result['advice_category'],
        confidence_score=ai_result.get('confidence_score'),
        model_version=ai_result.get('model_version'),
        daily_answer_id=daily_answer.id
    )
    
    # Add history entry
    await HistoryService.add_history_entry(
        user_id=user_id,
        event_type="daily_check",
        event_data={
            "daily_answer_id": daily_answer.id,
            "prediction_id": prediction.id,
            "anxiety_level": data.get('anxiety_level'),
            "is_extended": data.get('is_extended', False)
        }
    )
    
    # Clear state
    await state.clear()
    
    # Prepare response
    anxiety_level = ai_result['predicted_anxiety_level']
    category = get_anxiety_category(anxiety_level)
    
    if category == "low":
        emoji = "💚"
    elif category == "moderate":
        emoji = "💛"
    else:
        emoji = "❤️"
    
    response = (
        f"✅ **Check-in Complete!**\n\n"
        f"{emoji} **Predicted Anxiety Level:** {anxiety_level}/10\n\n"
        f"**💡 Advice:**\n{ai_result['advice']}"
    )
    
    # Send response
    if is_callback:
        await event.message.edit_text(
            response,
            reply_markup=KeyboardBuilder.feedback_reaction(prediction.id),
            parse_mode="Markdown"
        )
        await event.answer("Check-in saved! 🎉")
    else:
        await event.answer(
            response,
            reply_markup=KeyboardBuilder.feedback_reaction(prediction.id),
            parse_mode="Markdown"
        )


# ==================== FEEDBACK HANDLERS ====================

@router.callback_query(F.data.startswith("feedback:"))
async def process_feedback(callback: CallbackQuery, state: FSMContext):
    """Process feedback on prediction."""
    from services import FeedbackService
    
    parts = callback.data.split(":")
    
    if parts[1] == "skip":
        from config import settings
        is_admin = callback.from_user.id in settings.admin_ids
        
        await callback.message.edit_text(
            f"✅ **Check-in saved!**\n\n"
            f"Thank you for completing your daily check-in. "
            f"See you tomorrow! 👋",
            reply_markup=KeyboardBuilder.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    prediction_id = int(parts[1])
    feedback_type = parts[2]
    
    if feedback_type == "detailed":
        # Ask for detailed feedback
        await state.set_state(FeedbackState.detailed_feedback)
        await state.update_data(prediction_id=prediction_id)
        
        await callback.message.edit_text(
            f"💬 **Tell Us More**\n\n"
            f"Please share your thoughts about the prediction and advice.\n"
            f"Your feedback helps us improve!\n\n"
            f"Type your feedback:",
            reply_markup=KeyboardBuilder.back_cancel_buttons("menu:main", "cancel"),
            parse_mode="Markdown"
        )
    else:
        # Quick feedback (helpful or not_accurate)
        await FeedbackService.create_feedback(
            user_id=callback.from_user.id,
            feedback_type=feedback_type,
            target_type="prediction",
            prediction_id=prediction_id
        )
        
        from config import settings
        is_admin = callback.from_user.id in settings.admin_ids
        
        await callback.message.edit_text(
            f"🙏 **Thank you for your feedback!**\n\n"
            f"Your input helps us improve our predictions.",
            reply_markup=KeyboardBuilder.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )
    
    await callback.answer()


@router.message(FeedbackState.detailed_feedback)
async def process_detailed_feedback(message: Message, state: FSMContext):
    """Process detailed feedback text."""
    from services import FeedbackService
    from config import settings
    
    data = await state.get_data()
    prediction_id = data.get('prediction_id')
    
    await FeedbackService.create_feedback(
        user_id=message.from_user.id,
        feedback_type="detailed",
        target_type="prediction",
        prediction_id=prediction_id,
        feedback_text=message.text
    )
    
    await state.clear()
    
    is_admin = message.from_user.id in settings.admin_ids
    
    await message.answer(
        f"🙏 **Thank you for your detailed feedback!**\n\n"
        f"We really appreciate you taking the time to help us improve.",
        reply_markup=KeyboardBuilder.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )


# Back button handler
@router.callback_query(F.data == "daily:back")
async def daily_back(callback: CallbackQuery, state: FSMContext):
    """Handle back during daily check-in."""
    await callback.answer("Please complete the check-in or use /cancel to exit.")
