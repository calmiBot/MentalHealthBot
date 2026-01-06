"""
Statistics and history handlers.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import KeyboardBuilder
from services import AnalyticsService, DailyAnswerService, WeeklyAnswerService, PredictionService
from utils.helpers import format_statistics, format_daily_answer, paginate_list
from utils.charts import (
    create_anxiety_chart, create_stress_chart, create_combined_chart,
    create_sleep_chart
)
from config import settings

router = Router(name="stats")


# ==================== STATISTICS ====================

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Handle /stats command."""
    await show_stats_menu(message)


@router.callback_query(F.data == "menu:stats")
async def menu_stats(callback: CallbackQuery):
    """Show stats menu from main menu."""
    try:
        # Try to edit the message (works for text messages)
        await callback.message.edit_text(
            f"📊 **Your Statistics**\n\n"
            f"What would you like to see?",
            reply_markup=KeyboardBuilder.stats_menu(),
            parse_mode="Markdown"
        )
    except Exception:
        # If message is a photo or has no text, delete and send new
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            f"📊 **Your Statistics**\n\n"
            f"What would you like to see?",
            reply_markup=KeyboardBuilder.stats_menu(),
            parse_mode="Markdown"
        )
    
    await callback.answer()


async def show_stats_menu(message: Message):
    """Show statistics menu."""
    await message.answer(
        f"📊 **Your Statistics**\n\n"
        f"What would you like to see?",
        reply_markup=KeyboardBuilder.stats_menu(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "stats:summary")
async def show_stats_summary(callback: CallbackQuery):
    """Show statistics summary."""
    user_id = callback.from_user.id
    
    stats = await AnalyticsService.get_user_statistics(user_id)
    
    summary = format_statistics(stats)
    
    try:
        await callback.message.edit_text(
            summary,
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
    except Exception:
        # If message is a photo or has no text, delete and send new
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            summary,
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
    
    await callback.answer()


@router.callback_query(F.data == "stats:anxiety_chart")
async def show_anxiety_chart(callback: CallbackQuery):
    """Show anxiety level chart."""
    user_id = callback.from_user.id
    
    data = await AnalyticsService.get_anxiety_data_for_chart(user_id, days=30)
    
    if not data:
        await callback.message.edit_text(
            f"📊 **Anxiety Chart**\n\n"
            f"Not enough data to generate a chart. "
            f"Complete a few more check-ins first!",
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    chart_bytes = create_anxiety_chart(data, "Your Anxiety Levels (Last 30 Days)")
    
    if chart_bytes:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=BufferedInputFile(chart_bytes, filename="anxiety_chart.png"),
            caption="📈 **Anxiety Levels Over Time**\n\nGreen line: Low anxiety (≤3)\nRed line: High anxiety (≥7)",
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "Unable to generate chart. Please try again later.",
            reply_markup=KeyboardBuilder.back_button("menu:stats")
        )
    
    await callback.answer()


@router.callback_query(F.data == "stats:stress_chart")
async def show_stress_chart(callback: CallbackQuery):
    """Show stress level chart."""
    user_id = callback.from_user.id
    
    data = await AnalyticsService.get_stress_data_for_chart(user_id, days=30)
    
    if not data:
        await callback.message.edit_text(
            f"📊 **Stress Chart**\n\n"
            f"Not enough data to generate a chart. "
            f"Complete a few more check-ins first!",
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    chart_bytes = create_stress_chart(data, "Your Stress Levels (Last 30 Days)")
    
    if chart_bytes:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=BufferedInputFile(chart_bytes, filename="stress_chart.png"),
            caption="📊 **Stress Levels Over Time**",
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "Unable to generate chart. Please try again later.",
            reply_markup=KeyboardBuilder.back_button("menu:stats")
        )
    
    await callback.answer()


@router.callback_query(F.data == "stats:combined_chart")
async def show_combined_chart(callback: CallbackQuery):
    """Show combined anxiety and stress chart."""
    user_id = callback.from_user.id
    
    data = await AnalyticsService.get_combined_data_for_chart(user_id, days=30)
    
    if not data:
        await callback.message.edit_text(
            f"📊 **Combined Chart**\n\n"
            f"Not enough data to generate a chart. "
            f"Complete a few more check-ins first!",
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    chart_bytes = create_combined_chart(data, "Mental Health Overview (Last 30 Days)")
    
    if chart_bytes:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=BufferedInputFile(chart_bytes, filename="combined_chart.png"),
            caption="📉 **Mental Health Overview**\n\nRed: Anxiety | Teal: Stress",
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "Unable to generate chart. Please try again later.",
            reply_markup=KeyboardBuilder.back_button("menu:stats")
        )
    
    await callback.answer()


@router.callback_query(F.data == "stats:sleep_chart")
async def show_sleep_chart(callback: CallbackQuery):
    """Show sleep chart."""
    user_id = callback.from_user.id
    
    data = await AnalyticsService.get_sleep_data_for_chart(user_id, days=14)
    
    if not data:
        await callback.message.edit_text(
            f"📊 **Sleep Chart**\n\n"
            f"Not enough data to generate a chart. "
            f"Complete a few more check-ins first!",
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    chart_bytes = create_sleep_chart(data, "Your Sleep (Last 14 Days)")
    
    if chart_bytes:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=BufferedInputFile(chart_bytes, filename="sleep_chart.png"),
            caption="😴 **Sleep Hours**\n\nGreen: 7+ hours | Red: Below 7 hours",
            reply_markup=KeyboardBuilder.back_button("menu:stats"),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "Unable to generate chart. Please try again later.",
            reply_markup=KeyboardBuilder.back_button("menu:stats")
        )
    
    await callback.answer()


# ==================== HISTORY ====================

@router.message(Command("history"))
async def cmd_history(message: Message):
    """Handle /history command."""
    await message.answer(
        f"📂 **Your History**\n\n"
        f"What would you like to view?",
        reply_markup=KeyboardBuilder.history_menu(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "menu:history")
async def menu_history(callback: CallbackQuery):
    """Show history menu from main menu."""
    await callback.message.edit_text(
        f"📂 **Your History**\n\n"
        f"What would you like to view?",
        reply_markup=KeyboardBuilder.history_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "history:daily")
async def show_daily_history(callback: CallbackQuery, state: FSMContext):
    """Show daily check-in history."""
    await state.update_data(history_page=1)
    await display_daily_history(callback, 1)


@router.callback_query(F.data.startswith("history:daily:page:"))
async def paginate_daily_history(callback: CallbackQuery):
    """Paginate daily history."""
    page = int(callback.data.split(":")[-1])
    await display_daily_history(callback, page)


async def display_daily_history(callback: CallbackQuery, page: int):
    """Display daily check-in history with pagination."""
    user_id = callback.from_user.id
    
    answers, total = await DailyAnswerService.get_daily_answers(
        user_id=user_id,
        days=90,
        page=page,
        per_page=5
    )
    
    if not answers:
        await callback.message.edit_text(
            f"📅 **Daily Check-in History**\n\n"
            f"No check-ins found. Start by doing a daily check-in!",
            reply_markup=KeyboardBuilder.back_button("menu:history"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    total_pages = (total + 4) // 5
    
    text = f"📅 **Daily Check-in History**\n\n"
    
    for answer in answers:
        text += format_daily_answer(answer) + "\n\n"
    
    text += f"_Showing page {page} of {total_pages}_"
    
    await callback.message.edit_text(
        text,
        reply_markup=KeyboardBuilder.pagination(page, total_pages, "history:daily"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "history:daily:back")
async def daily_history_back(callback: CallbackQuery):
    """Go back from daily history."""
    await callback.message.edit_text(
        f"📂 **Your History**\n\n"
        f"What would you like to view?",
        reply_markup=KeyboardBuilder.history_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "history:weekly")
async def show_weekly_history(callback: CallbackQuery, state: FSMContext):
    """Show weekly assessment history."""
    await state.update_data(history_page=1)
    await display_weekly_history(callback, 1)


@router.callback_query(F.data.startswith("history:weekly:page:"))
async def paginate_weekly_history(callback: CallbackQuery):
    """Paginate weekly history."""
    page = int(callback.data.split(":")[-1])
    await display_weekly_history(callback, page)


async def display_weekly_history(callback: CallbackQuery, page: int):
    """Display weekly assessment history with pagination."""
    user_id = callback.from_user.id
    
    answers, total = await WeeklyAnswerService.get_weekly_answers(
        user_id=user_id,
        weeks=52,
        page=page,
        per_page=5
    )
    
    if not answers:
        await callback.message.edit_text(
            f"📆 **Weekly Assessment History**\n\n"
            f"No assessments found. Complete a weekly assessment first!",
            reply_markup=KeyboardBuilder.back_button("menu:history"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    total_pages = (total + 4) // 5
    
    text = f"📆 **Weekly Assessment History**\n\n"
    
    for answer in answers:
        text += (
            f"📅 **Week of {answer.week_start.strftime('%B %d, %Y')}**\n"
            f"• Average Stress: {answer.avg_stress_level or 'N/A'}/10\n"
            f"• Anxiety Level: {answer.anxiety_level or 'N/A'}/10\n"
            f"• Week Rating: {answer.overall_week_rating or 'N/A'}/10\n\n"
        )
    
    text += f"_Showing page {page} of {total_pages}_"
    
    await callback.message.edit_text(
        text,
        reply_markup=KeyboardBuilder.pagination(page, total_pages, "history:weekly"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "history:weekly:back")
async def weekly_history_back(callback: CallbackQuery):
    """Go back from weekly history."""
    await callback.message.edit_text(
        f"📂 **Your History**\n\n"
        f"What would you like to view?",
        reply_markup=KeyboardBuilder.history_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "history:predictions")
async def show_predictions_history(callback: CallbackQuery):
    """Show prediction history."""
    user_id = callback.from_user.id
    
    predictions, total = await PredictionService.get_user_predictions(user_id, page=1, per_page=5)
    
    if not predictions:
        await callback.message.edit_text(
            f"🔮 **Prediction History**\n\n"
            f"No predictions found. Complete a check-in to get predictions!",
            reply_markup=KeyboardBuilder.back_button("menu:history"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    text = f"🔮 **Prediction History**\n\n"
    
    for pred in predictions:
        category_emoji = "💚" if pred.advice_category == "low" else ("💛" if pred.advice_category == "moderate" else "❤️")
        # Map numeric level to class name
        if pred.predicted_anxiety_level <= 4:
            class_name = "Low"
        elif pred.predicted_anxiety_level <= 7:
            class_name = "Medium"
        else:
            class_name = "High"
        text += (
            f"{category_emoji} **{pred.created_at.strftime('%B %d, %Y')}**\n"
            f"• Predicted Anxiety: {class_name}\n"
            f"• Confidence: {int(pred.confidence_score * 100) if pred.confidence_score else 'N/A'}%\n\n"
        )
    
    await callback.message.edit_text(
        text,
        reply_markup=KeyboardBuilder.back_button("menu:history"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "history:feedback")
async def show_feedback_history(callback: CallbackQuery):
    """Show feedback history."""
    from services import FeedbackService
    
    await callback.message.edit_text(
        f"💬 **Your Feedback**\n\n"
        f"Thank you for all your feedback! "
        f"Your input helps us improve our predictions and advice.\n\n"
        f"You can always provide feedback after each check-in.",
        reply_markup=KeyboardBuilder.back_button("menu:history"),
        parse_mode="Markdown"
    )
    await callback.answer()
