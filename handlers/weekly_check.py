"""
Weekly assessment handlers.
"""

from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import KeyboardBuilder
from services import (
    WeeklyAnswerService, PredictionService, HistoryService,
    call_ai_model, ProfileService
)
from states import WeeklyCheckState
from utils.constants import (
    MESSAGES, EMOJI, STRESS_LEVEL_SCALE,
    WEEK_RATING_SCALE, MEDICATION_ADHERENCE_OPTIONS
)
from utils.helpers import format_scale_explanation, calculate_week_dates, get_anxiety_category

router = Router(name="weekly_check")


# ==================== HELPER FUNCTIONS ====================

def _convert_diet_quality(diet_str: str) -> int:
    """Convert diet quality string to numeric scale."""
    mapping = {'poor': 1, 'fair': 2, 'average': 3, 'good': 4, 'excellent': 5}
    return mapping.get(str(diet_str).lower(), 3)


def _convert_smoking(smoking_str: str) -> int:
    """Convert smoking habit string to cigarettes per day estimate."""
    mapping = {'none': 0, 'occasionally': 5, 'regularly': 15, 'heavily': 25}
    return mapping.get(str(smoking_str).lower(), 0)


# ==================== START WEEKLY ASSESSMENT ====================

@router.callback_query(F.data == "menu:weekly")
async def start_weekly_assessment(callback: CallbackQuery, state: FSMContext):
    """Start weekly assessment from menu."""
    await callback.message.edit_text(
        MESSAGES["weekly_check_intro"],
        reply_markup=KeyboardBuilder.confirm_cancel("weekly:start", "menu:main"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "weekly:start")
async def weekly_start(callback: CallbackQuery, state: FSMContext):
    """Begin weekly assessment questions."""
    await state.set_state(WeeklyCheckState.avg_stress_level)
    
    explanation = format_scale_explanation(STRESS_LEVEL_SCALE, "Average Stress Level")
    
    await callback.message.edit_text(
        f"📊 **Question 1/8: Average Stress**\n\n"
        f"Looking back at the past week, what was your average stress level?\n\n"
        f"{explanation}",
        reply_markup=KeyboardBuilder.stress_level_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(WeeklyCheckState.avg_stress_level, F.data.startswith("stress:"))
async def process_weekly_stress(callback: CallbackQuery, state: FSMContext):
    """Process weekly average stress."""
    stress = int(callback.data.split(":")[1])
    await state.update_data(avg_stress_level=float(stress))
    await state.set_state(WeeklyCheckState.avg_sleep_hours)
    
    await callback.message.edit_text(
        f"😴 **Question 2/8: Average Sleep**\n\n"
        f"How many hours of sleep did you get on average this week?",
        reply_markup=KeyboardBuilder.sleep_hours_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(WeeklyCheckState.avg_sleep_hours, F.data.startswith("sleep:"))
async def process_weekly_sleep(callback: CallbackQuery, state: FSMContext):
    """Process weekly average sleep."""
    sleep = float(callback.data.split(":")[1])
    await state.update_data(avg_sleep_hours=sleep)
    await state.set_state(WeeklyCheckState.total_caffeine)
    
    await callback.message.edit_text(
        f"☕ **Question 3/8: Total Caffeine**\n\n"
        f"How many caffeinated drinks did you have in total this week?\n\n"
        f"_Think about your daily average and multiply by 7_",
        reply_markup=KeyboardBuilder.numeric_scale(0, 50, "weekly_caffeine", cols=10),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(WeeklyCheckState.total_caffeine, F.data.startswith("weekly_caffeine:"))
async def process_weekly_caffeine(callback: CallbackQuery, state: FSMContext):
    """Process weekly total caffeine."""
    caffeine = int(callback.data.split(":")[1])
    await state.update_data(total_caffeine=caffeine)
    await state.set_state(WeeklyCheckState.total_alcohol)
    
    await callback.message.edit_text(
        f"🍷 **Question 4/8: Total Alcohol**\n\n"
        f"How many alcoholic drinks did you have in total this week?",
        reply_markup=KeyboardBuilder.alcohol_intake_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(WeeklyCheckState.total_alcohol, F.data.startswith("alcohol:"))
async def process_weekly_alcohol(callback: CallbackQuery, state: FSMContext):
    """Process weekly total alcohol."""
    alcohol = int(callback.data.split(":")[1])
    await state.update_data(total_alcohol=alcohol)
    await state.set_state(WeeklyCheckState.overall_week_rating)
    
    explanation = format_scale_explanation(WEEK_RATING_SCALE, "Week Rating")
    
    await callback.message.edit_text(
        f"📅 **Question 5/8: Overall Week Rating**\n\n"
        f"How would you rate your overall week?\n\n"
        f"{explanation}",
        reply_markup=KeyboardBuilder.week_rating_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(WeeklyCheckState.overall_week_rating, F.data.startswith("week_rating:"))
async def process_week_rating(callback: CallbackQuery, state: FSMContext):
    """Process overall week rating."""
    rating = int(callback.data.split(":")[1])
    await state.update_data(overall_week_rating=rating)
    await state.set_state(WeeklyCheckState.significant_events)
    
    await callback.message.edit_text(
        f"📋 **Question 6/8: Significant Events**\n\n"
        f"Were there any significant events this week that affected your mental health?\n\n"
        f"Type your answer or type 'none' if nothing significant happened:",
        reply_markup=KeyboardBuilder.back_cancel_buttons("weekly:back", "cancel"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(WeeklyCheckState.significant_events)
async def process_significant_events(message: Message, state: FSMContext):
    """Process significant events."""
    events = message.text if message.text.lower() not in ["none", "skip", "no"] else None
    await state.update_data(significant_events=events)
    await state.set_state(WeeklyCheckState.therapy_attended)
    
    await message.answer(
        f"🛋️ **Question 7/8: Therapy**\n\n"
        f"Did you attend any therapy sessions this week?",
        reply_markup=KeyboardBuilder.yes_no("therapy:yes", "therapy:no"),
        parse_mode="Markdown"
    )


@router.callback_query(WeeklyCheckState.therapy_attended, F.data.startswith("therapy:"))
async def process_therapy_attended(callback: CallbackQuery, state: FSMContext):
    """Process therapy attendance and complete assessment."""
    user_id = callback.from_user.id
    attended = callback.data.split(":")[1] == "yes"
    await state.update_data(therapy_attended=attended)
    
    data = await state.get_data()
    
    # Calculate week dates
    week_start, week_end = calculate_week_dates()
    
    # Save weekly answer
    weekly_answer = await WeeklyAnswerService.create_weekly_answer(
        user_id=user_id,
        week_start=week_start,
        week_end=week_end,
        avg_stress_level=data.get('avg_stress_level'),
        avg_anxiety_level=data.get('avg_anxiety_level'),
        avg_sleep_hours=data.get('avg_sleep_hours'),
        total_caffeine=data.get('total_caffeine'),
        total_alcohol=data.get('total_alcohol'),
        overall_week_rating=data.get('overall_week_rating'),
        significant_events=data.get('significant_events'),
        therapy_attended=data.get('therapy_attended')
    )
    
    # Get user profile to merge with check-in data for better predictions
    profile = await ProfileService.get_profile(user_id)
    
    # Build complete data for AI model (merge profile + weekly check-in)
    ai_input = {
        # From weekly check-in
        'stress_level': data.get('avg_stress_level'),
        'sleep_hours': data.get('avg_sleep_hours'),
        'caffeine_intake': (data.get('total_caffeine', 0) or 0) // 7,  # Daily average
        'alcohol_intake': data.get('total_alcohol', 0),
    }
    
    # Add profile data if available
    if profile:
        ai_input.update({
            'age': profile.age,
            'gender': profile.gender,
            'occupation': profile.occupation,
            'physical_activity': profile.physical_activity,
            'diet_quality': _convert_diet_quality(profile.diet_quality),
            'smoking_habits': _convert_smoking(profile.smoking_habits),
            'family_anxiety_history': 1 if profile.family_anxiety_history else 0,
            'medication_use': 1 if profile.medication_use else 0,
            'therapy_frequency': profile.therapy_frequency,
            'recent_life_events': data.get('significant_events') or profile.recent_life_events,
            'heart_rate': profile.baseline_heart_rate,
            'breathing_rate': profile.baseline_breathing_rate,
            'sweating_level': profile.sweating_level,
            'dizziness_today': 1 if profile.dizziness_frequency in ['sometimes', 'often'] else 0,
        })
    
    # Get AI prediction
    ai_result = await call_ai_model(ai_input)
    
    # Save prediction
    prediction = await PredictionService.create_prediction(
        user_id=user_id,
        predicted_anxiety_level=ai_result['predicted_anxiety_level'],
        advice=ai_result['advice'],
        advice_category=ai_result['advice_category'],
        confidence_score=ai_result.get('confidence_score'),
        model_version=ai_result.get('model_version'),
        weekly_answer_id=weekly_answer.id
    )
    
    # Add history entry
    await HistoryService.add_history_entry(
        user_id=user_id,
        event_type="weekly_check",
        event_data={
            "weekly_answer_id": weekly_answer.id,
            "prediction_id": prediction.id,
            "anxiety_level": ai_result['predicted_anxiety_level']
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
    
    # Get class name for display (Low, Medium, High)
    class_name = ai_result.get('anxiety_class_name', 'Medium')
    
    # Escape special markdown characters in advice
    advice_text = ai_result['advice'].replace('*', '\\*').replace('_', '\\_').replace('`', '\\`').replace('[', '\\[')
    
    response = (
        f"✅ *Weekly Assessment Complete!*\n\n"
        f"*📊 Week Summary:*\n"
        f"• Average Stress: {data.get('avg_stress_level')}/10\n"
        f"• Average Sleep: {data.get('avg_sleep_hours')} hours\n"
        f"• Week Rating: {data.get('overall_week_rating')}/10\n\n"
        f"{emoji} *Predicted Anxiety Level:* {class_name}\n\n"
        f"*💡 Advice:*\n{advice_text}"
    )
    
    await callback.message.edit_text(
        response,
        reply_markup=KeyboardBuilder.feedback_reaction(prediction.id),
        parse_mode="Markdown"
    )
    await callback.answer("Weekly assessment saved! 🎉")


# Back button handler
@router.callback_query(F.data == "weekly:back")
async def weekly_back(callback: CallbackQuery, state: FSMContext):
    """Handle back during weekly assessment."""
    await callback.answer("Please complete the assessment or use /cancel to exit.")
