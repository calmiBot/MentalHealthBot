"""
Onboarding handlers - Multi-step registration wizard.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import KeyboardBuilder
from services import UserService, ProfileService, HistoryService
from states import OnboardingState
from utils.constants import (
    MESSAGES, EMOJI, STRESS_LEVEL_SCALE,
    SWEATING_LEVEL_SCALE, AGE_RANGE, HEART_RATE_RANGE, BREATHING_RATE_RANGE
)
from utils.helpers import format_scale_explanation, validate_numeric_input

router = Router(name="onboarding")


# ==================== START ONBOARDING ====================

@router.callback_query(F.data == "onboarding:start")
async def start_onboarding(callback: CallbackQuery, state: FSMContext):
    """Start the onboarding process."""
    await state.set_state(OnboardingState.age)
    
    await callback.message.edit_text(
        f"📅 **Step 1/15: Your Age**\n\n"
        f"Please enter your age (between {AGE_RANGE[0]} and {AGE_RANGE[1]}):",
        reply_markup=KeyboardBuilder.back_cancel_buttons("menu:main", "cancel"),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== DEMOGRAPHICS ====================

@router.message(OnboardingState.age)
async def process_age(message: Message, state: FSMContext):
    """Process age input."""
    age = validate_numeric_input(message.text, AGE_RANGE[0], AGE_RANGE[1])
    
    if age is None:
        await message.answer(
            f"⚠️ Please enter a valid age between {AGE_RANGE[0]} and {AGE_RANGE[1]}.",
            reply_markup=KeyboardBuilder.back_cancel_buttons("menu:main", "cancel")
        )
        return
    
    await state.update_data(age=age)
    await state.set_state(OnboardingState.gender)
    
    await message.answer(
        f"👤 **Step 2/15: Gender**\n\nPlease select your gender:",
        reply_markup=KeyboardBuilder.gender_options(),
        parse_mode="Markdown"
    )


@router.callback_query(OnboardingState.gender, F.data.startswith("gender:"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Process gender selection."""
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    await state.set_state(OnboardingState.occupation)
    
    await callback.message.edit_text(
        f"💼 **Step 3/15: Occupation**\n\nWhat's your occupation?",
        reply_markup=KeyboardBuilder.occupation_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.occupation, F.data.startswith("occupation:"))
async def process_occupation(callback: CallbackQuery, state: FSMContext):
    """Process occupation selection."""
    occupation = callback.data.split(":")[1]
    await state.update_data(occupation=occupation)
    await state.set_state(OnboardingState.family_status)
    
    await callback.message.edit_text(
        f"💑 **Step 4/15: Family Status**\n\nWhat's your family status?",
        reply_markup=KeyboardBuilder.family_status_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.family_status, F.data.startswith("family_status:"))
async def process_family_status(callback: CallbackQuery, state: FSMContext):
    """Process family status selection."""
    family_status = callback.data.split(":")[1]
    await state.update_data(family_status=family_status)
    await state.set_state(OnboardingState.sleep_hours)
    
    await callback.message.edit_text(
        f"😴 **Step 5/15: Sleep Hours**\n\n"
        f"How many hours of sleep do you typically get per night?",
        reply_markup=KeyboardBuilder.sleep_hours_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== LIFESTYLE FACTORS ====================

@router.callback_query(OnboardingState.sleep_hours, F.data.startswith("sleep:"))
async def process_sleep_hours(callback: CallbackQuery, state: FSMContext):
    """Process sleep hours selection."""
    sleep = float(callback.data.split(":")[1])
    await state.update_data(sleep_hours=sleep)
    await state.set_state(OnboardingState.physical_activity)
    
    await callback.message.edit_text(
        f"🏃 **Step 6/15: Physical Activity**\n\n"
        f"How would you describe your typical physical activity level?",
        reply_markup=KeyboardBuilder.physical_activity_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.physical_activity, F.data.startswith("activity:"))
async def process_physical_activity(callback: CallbackQuery, state: FSMContext):
    """Process physical activity selection."""
    activity = callback.data.split(":")[1]
    await state.update_data(physical_activity=activity)
    await state.set_state(OnboardingState.diet_quality)
    
    await callback.message.edit_text(
        f"🥗 **Step 7/15: Diet Quality**\n\n"
        f"How would you rate your overall diet quality?",
        reply_markup=KeyboardBuilder.diet_quality_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.diet_quality, F.data.startswith("diet:"))
async def process_diet_quality(callback: CallbackQuery, state: FSMContext):
    """Process diet quality selection."""
    diet = callback.data.split(":")[1]
    await state.update_data(diet_quality=diet)
    await state.set_state(OnboardingState.alcohol_intake)
    
    await callback.message.edit_text(
        f"🍷 **Step 8/15: Alcohol Intake**\n\n"
        f"How many alcoholic drinks do you consume per week? (0-19)\n\n"
        f"_1 drink = 1 beer, 1 glass of wine, or 1 shot of spirits_",
        reply_markup=KeyboardBuilder.alcohol_intake_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.alcohol_intake, F.data.startswith("alcohol:"))
async def process_alcohol_intake(callback: CallbackQuery, state: FSMContext):
    """Process alcohol intake selection."""
    alcohol = int(callback.data.split(":")[1])
    await state.update_data(alcohol_intake=alcohol)
    await state.set_state(OnboardingState.caffeine_intake)
    
    await callback.message.edit_text(
        f"☕ **Step 9/15: Caffeine Intake**\n\n"
        f"How many cups of coffee/caffeinated drinks per day?\n\n"
        f"_Include coffee, tea, energy drinks, etc._",
        reply_markup=KeyboardBuilder.caffeine_intake_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.caffeine_intake, F.data.startswith("caffeine:"))
async def process_caffeine_intake(callback: CallbackQuery, state: FSMContext):
    """Process caffeine intake selection."""
    caffeine = int(callback.data.split(":")[1])
    await state.update_data(caffeine_intake=caffeine)
    await state.set_state(OnboardingState.smoking_habits)
    
    await callback.message.edit_text(
        f"🚬 **Step 10/15: Smoking Habits**\n\n"
        f"What are your smoking habits?",
        reply_markup=KeyboardBuilder.smoking_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.smoking_habits, F.data.startswith("smoking:"))
async def process_smoking_habits(callback: CallbackQuery, state: FSMContext):
    """Process smoking habits selection."""
    smoking = callback.data.split(":")[1]
    await state.update_data(smoking_habits=smoking)
    await state.set_state(OnboardingState.stress_level)
    
    explanation = format_scale_explanation(STRESS_LEVEL_SCALE, "Stress Level Scale")
    
    await callback.message.edit_text(
        f"😰 **Step 11/15: Baseline Stress Level**\n\n"
        f"Rate your typical stress level (1-10):\n\n"
        f"{explanation}",
        reply_markup=KeyboardBuilder.stress_level_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== MENTAL & PHYSICAL INDICATORS ====================

@router.callback_query(OnboardingState.stress_level, F.data.startswith("stress:"))
async def process_stress_level(callback: CallbackQuery, state: FSMContext):
    """Process stress level selection."""
    stress = int(callback.data.split(":")[1])
    await state.update_data(baseline_stress_level=stress)
    await state.set_state(OnboardingState.family_anxiety_history)
    
    await callback.message.edit_text(
        f"🧬 **Step 12/15: Family History**\n\n"
        f"Does your family have a history of anxiety disorders?",
        reply_markup=KeyboardBuilder.family_anxiety_history(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.family_anxiety_history, F.data.startswith("family_history:"))
async def process_family_history(callback: CallbackQuery, state: FSMContext):
    """Process family anxiety history selection."""
    history = callback.data.split(":")[1]
    family_history = True if history == "yes" else (False if history == "no" else None)
    await state.update_data(family_anxiety_history=family_history)
    await state.set_state(OnboardingState.therapy_frequency)
    
    await callback.message.edit_text(
        f"🛋️ **Step 13/15: Therapy**\n\n"
        f"Have you ever been or are you currently in therapy?",
        reply_markup=KeyboardBuilder.therapy_frequency_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingState.therapy_frequency, F.data.startswith("therapy:"))
async def process_therapy_frequency(callback: CallbackQuery, state: FSMContext):
    """Process therapy frequency selection."""
    therapy = callback.data.split(":")[1]
    await state.update_data(therapy_frequency=therapy)
    await state.set_state(OnboardingState.recent_life_events)
    
    await callback.message.edit_text(
        f"📋 **Step 14/15: Recent Life Events**\n\n"
        f"Have you experienced any significant life events recently?\n\n"
        f"Please type your answer or type 'skip' if none:",
        reply_markup=KeyboardBuilder.back_cancel_buttons("onboarding:back", "cancel"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(OnboardingState.recent_life_events)
async def process_life_events(message: Message, state: FSMContext):
    """Process life events input and show confirmation."""
    life_events = message.text if message.text.lower() != "skip" else None
    await state.update_data(recent_life_events=life_events)
    
    # Get all collected data for confirmation
    data = await state.get_data()


    # Format confirmation summary
    data = await state.get_data()
    
    # Format summary
    summary = (
        f"📋 **Profile Summary**\n\n"
        f"**Demographics:**\n"
        f"• Age: {data.get('age')}\n"
        f"• Gender: {data.get('gender', 'Not set').replace('_', ' ').title()}\n"
        f"• Occupation: {data.get('occupation')}\n"
        f"• Family Status: {data.get('family_status', 'Not set').replace('_', ' ').title()}\n\n"
        f"**Lifestyle:**\n"
        f"• Sleep: {data.get('sleep_hours')} hours\n"
        f"• Activity: {data.get('physical_activity', 'Not set').title()}\n"
        f"• Diet: {data.get('diet_quality', 'Not set').title()}\n"
        f"• Alcohol: {data.get('alcohol_intake')} drinks/week\n"
        f"• Caffeine: {data.get('caffeine_intake')} cups/day\n"
        f"• Smoking: {data.get('smoking_habits', 'Not set').title()}\n\n"
        f"**Health Indicators:**\n"
        f"• Stress Level: {data.get('baseline_stress_level')}/10\n\n"
        f"Is this information correct?"
    )
    
    await state.set_state(OnboardingState.confirmation)
    
    await message.answer(
        summary,
        reply_markup=KeyboardBuilder.confirm_cancel("onboarding:confirm", "onboarding:restart"),
        parse_mode="Markdown"
    )


@router.callback_query(OnboardingState.confirmation, F.data == "onboarding:confirm")
async def confirm_onboarding(callback: CallbackQuery, state: FSMContext):
    """Confirm and save onboarding data."""
    user_id = callback.from_user.id
    data = await state.get_data()
    
    # Save profile to database
    await ProfileService.create_or_update_profile(
        user_id=user_id,
        age=data.get('age'),
        gender=data.get('gender'),
        occupation=data.get('occupation'),
        family_status=data.get('family_status'),
        sleep_hours=data.get('sleep_hours'),
        physical_activity=data.get('physical_activity'),
        diet_quality=data.get('diet_quality'),
        alcohol_intake=data.get('alcohol_intake'),
        caffeine_intake=data.get('caffeine_intake'),
        smoking_habits=data.get('smoking_habits'),
        baseline_stress_level=data.get('baseline_stress_level'),
        family_anxiety_history=data.get('family_anxiety_history'),
        therapy_frequency=data.get('therapy_frequency'),
        recent_life_events=data.get('recent_life_events')
    )
    
    # Mark user as onboarded
    await UserService.mark_user_onboarded(user_id)
    
    # Add history entry
    await HistoryService.add_history_entry(
        user_id=user_id,
        event_type="onboarding_complete",
        event_data=data
    )
    
    # Clear state
    await state.clear()
    
    # Check if admin
    from config import settings
    is_admin = user_id in settings.admin_ids
    
    await callback.message.edit_text(
        MESSAGES["onboarding_complete"],
        reply_markup=KeyboardBuilder.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )
    await callback.answer("Profile saved successfully! 🎉")


@router.callback_query(OnboardingState.confirmation, F.data == "onboarding:restart")
async def restart_onboarding(callback: CallbackQuery, state: FSMContext):
    """Restart onboarding process."""
    await state.clear()
    await state.set_state(OnboardingState.age)
    
    await callback.message.edit_text(
        f"📅 **Step 1/15: Your Age**\n\n"
        f"Please enter your age (between {AGE_RANGE[0]} and {AGE_RANGE[1]}):",
        reply_markup=KeyboardBuilder.back_cancel_buttons("menu:main", "cancel"),
        parse_mode="Markdown"
    )
    await callback.answer()


# Handle back button during onboarding
@router.callback_query(F.data == "onboarding:back")
async def onboarding_back(callback: CallbackQuery, state: FSMContext):
    """Handle back button during onboarding."""
    current_state = await state.get_state()
    
    # Define state order for back navigation
    state_order = [
        OnboardingState.age,
        OnboardingState.gender,
        OnboardingState.occupation,
        OnboardingState.family_status,
        OnboardingState.sleep_hours,
        OnboardingState.physical_activity,
        OnboardingState.diet_quality,
        OnboardingState.alcohol_intake,
        OnboardingState.caffeine_intake,
        OnboardingState.smoking_habits,
        OnboardingState.stress_level,
        OnboardingState.family_anxiety_history,
        OnboardingState.therapy_frequency,
        OnboardingState.recent_life_events,
        OnboardingState.confirmation
    ]
    
    # Find current state index
    current_index = -1
    for i, s in enumerate(state_order):
        if current_state == s.state:
            current_index = i
            break
    
    if current_index <= 0:
        # At the beginning, go back to welcome
        await state.clear()
        await callback.message.edit_text(
            MESSAGES["onboarding_intro"],
            reply_markup=KeyboardBuilder.start_onboarding(),
            parse_mode="Markdown"
        )
    else:
        # Go to previous state - this is simplified, in production would need more logic
        await callback.answer("Use /start to restart the onboarding process.")
    
    await callback.answer()
