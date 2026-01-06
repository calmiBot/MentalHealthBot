"""
FSM States for the Mental Health Bot.
Defines all conversation states for wizards and forms.
"""

from aiogram.fsm.state import State, StatesGroup


class OnboardingState(StatesGroup):
    """States for the onboarding wizard."""
    
    # Welcome
    welcome = State()
    
    # Demographics
    age = State()
    gender = State()
    occupation = State()
    family_status = State()
    
    # Lifestyle Factors
    sleep_hours = State()
    physical_activity = State()
    diet_quality = State()
    alcohol_intake = State()
    caffeine_intake = State()
    smoking_habits = State()
    
    # Mental & Physical Indicators
    heart_rate = State()
    breathing_rate = State()
    stress_level = State()
    sweating_level = State()
    dizziness = State()
    
    # Mental Health History
    family_anxiety_history = State()
    medication_use = State()
    therapy_frequency = State()
    
    # Life Events
    recent_life_events = State()
    
    # Confirmation
    confirmation = State()


class DailyCheckState(StatesGroup):
    """States for daily mental health check-in."""
    
    # Essential questions (5-10)
    stress_level = State()
    heart_rate = State()
    breathing_rate = State()
    sleep_hours = State()
    caffeine_intake = State()
    alcohol_intake = State()
    
    # Extended questions (optional)
    show_extended = State()
    mood_rating = State()
    energy_level = State()
    sweating_level = State()
    dizziness_today = State()
    physical_activity_today = State()
    notes = State()
    
    # Confirmation
    confirmation = State()


class WeeklyCheckState(StatesGroup):
    """States for weekly comprehensive assessment."""
    
    # Weekly averages
    avg_stress_level = State()
    avg_anxiety_level = State()
    avg_sleep_hours = State()
    
    # Weekly totals
    total_caffeine = State()
    total_alcohol = State()
    
    # Weekly self-assessment
    overall_week_rating = State()
    significant_events = State()
    medication_adherence = State()
    therapy_attended = State()
    
    # Confirmation
    confirmation = State()


class SettingsState(StatesGroup):
    """States for settings menu."""
    
    main_menu = State()
    
    # Edit profile
    edit_profile_menu = State()
    edit_age = State()
    edit_gender = State()
    edit_occupation = State()
    edit_family_status = State()
    edit_sleep_hours = State()
    edit_physical_activity = State()
    edit_diet_quality = State()
    edit_alcohol_intake = State()
    edit_caffeine_intake = State()
    edit_smoking_habits = State()
    edit_heart_rate = State()
    edit_breathing_rate = State()
    edit_stress_level = State()
    edit_sweating_level = State()
    edit_dizziness = State()
    edit_family_anxiety_history = State()
    edit_medication_use = State()
    edit_therapy_frequency = State()
    edit_recent_life_events = State()
    edit_anxiety_level = State()
    
    # Notifications
    notification_settings = State()
    
    # Delete account
    delete_account_confirm = State()
    delete_account_final = State()


class FeedbackState(StatesGroup):
    """States for feedback collection."""
    
    reaction = State()
    detailed_feedback = State()
    confirmation = State()


class AdminState(StatesGroup):
    """States for admin panel."""
    
    main_menu = State()
    view_users = State()
    user_details = State()
    export_data = State()
    analytics = State()
