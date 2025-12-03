"""
Admin panel handlers.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import KeyboardBuilder
from services import UserService, AnalyticsService
from states import AdminState
from utils.constants import ADMIN_MESSAGES, EMOJI
from utils.helpers import format_admin_stats, paginate_list, format_user_list_item
from utils.charts import create_admin_overview_chart
from config import settings

router = Router(name="admin")


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in settings.admin_ids


# ==================== ADMIN MENU ====================

@router.callback_query(F.data == "menu:admin")
async def show_admin_panel(callback: CallbackQuery, is_admin: bool = False):
    """Show admin panel."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    await callback.message.edit_text(
        ADMIN_MESSAGES["stats_header"],
        reply_markup=KeyboardBuilder.admin_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:main")
async def admin_main(callback: CallbackQuery, is_admin: bool = False):
    """Return to admin main menu."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    await callback.message.edit_text(
        ADMIN_MESSAGES["stats_header"],
        reply_markup=KeyboardBuilder.admin_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== ADMIN STATS ====================

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery, is_admin: bool = False):
    """Show admin statistics."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    stats = await AnalyticsService.get_admin_statistics()
    summary = format_admin_stats(stats)
    
    await callback.message.edit_text(
        summary,
        reply_markup=KeyboardBuilder.back_button("admin:main"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:charts")
async def admin_charts(callback: CallbackQuery, is_admin: bool = False):
    """Show admin charts."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    stats = await AnalyticsService.get_admin_statistics()
    chart_bytes = create_admin_overview_chart(stats)
    
    if chart_bytes:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=BufferedInputFile(chart_bytes, filename="admin_overview.png"),
            caption="📊 **Admin Overview Dashboard**",
            reply_markup=KeyboardBuilder.back_button("admin:main"),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "Unable to generate charts. Not enough data.",
            reply_markup=KeyboardBuilder.back_button("admin:main")
        )
    
    await callback.answer()


# ==================== USER LIST ====================

@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery, state: FSMContext, is_admin: bool = False):
    """Show user list."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    await state.update_data(admin_page=1)
    await display_user_list(callback, 1)


@router.callback_query(F.data.startswith("admin:users:page:"))
async def paginate_users(callback: CallbackQuery, is_admin: bool = False):
    """Paginate user list."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    page = int(callback.data.split(":")[-1])
    await display_user_list(callback, page)


async def display_user_list(callback: CallbackQuery, page: int):
    """Display user list with pagination."""
    users, total = await UserService.get_all_users(page=page, per_page=10)
    
    if not users:
        await callback.message.edit_text(
            f"👥 **User List**\n\nNo users found.",
            reply_markup=KeyboardBuilder.back_button("admin:main"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    total_pages = (total + 9) // 10
    start = (page - 1) * 10 + 1
    end = min(page * 10, total)
    
    text = f"👥 **User List**\n\n"
    text += f"Showing {start}-{end} of {total} users:\n\n"
    
    for i, user in enumerate(users, start=start):
        status = "✅" if user.is_active else "❌"
        onboarded = "📋" if user.is_onboarded else "🆕"
        name = user.first_name or user.username or f"User"
        text += f"{i}. {status}{onboarded} {name} (ID: `{user.id}`)\n"
    
    text += f"\n_Page {page} of {total_pages}_"
    
    await callback.message.edit_text(
        text,
        reply_markup=KeyboardBuilder.pagination(page, total_pages, "admin:users"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:users:back")
async def users_back(callback: CallbackQuery, is_admin: bool = False):
    """Go back from user list."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    await callback.message.edit_text(
        ADMIN_MESSAGES["stats_header"],
        reply_markup=KeyboardBuilder.admin_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== EXPORT DATA ====================

@router.callback_query(F.data == "admin:export")
async def admin_export(callback: CallbackQuery, is_admin: bool = False):
    """Show export options."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    await callback.message.edit_text(
        f"📥 **Export Data**\n\n"
        f"Select what data you want to export:",
        reply_markup=KeyboardBuilder.admin_export_options(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "export:users")
async def export_users(callback: CallbackQuery, is_admin: bool = False):
    """Export all users as CSV."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    csv_data = await AnalyticsService.export_users_csv()
    
    await callback.message.delete()
    await callback.message.answer_document(
        document=BufferedInputFile(csv_data.encode('utf-8'), filename="users_export.csv"),
        caption="📊 **Users Export**\n\nAll users have been exported.",
        reply_markup=KeyboardBuilder.back_button("admin:export"),
        parse_mode="Markdown"
    )
    await callback.answer("Users exported!")


@router.callback_query(F.data == "export:checkins")
async def export_checkins(callback: CallbackQuery, is_admin: bool = False):
    """Export all check-ins as CSV."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    csv_data = await AnalyticsService.export_checkins_csv()
    
    await callback.message.delete()
    await callback.message.answer_document(
        document=BufferedInputFile(csv_data.encode('utf-8'), filename="checkins_export.csv"),
        caption="📝 **Check-ins Export**\n\nAll check-ins have been exported.",
        reply_markup=KeyboardBuilder.back_button("admin:export"),
        parse_mode="Markdown"
    )
    await callback.answer("Check-ins exported!")


@router.callback_query(F.data == "export:feedback")
async def export_feedback(callback: CallbackQuery, is_admin: bool = False):
    """Export all feedback as CSV."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    csv_data = await AnalyticsService.export_feedback_csv()
    
    await callback.message.delete()
    await callback.message.answer_document(
        document=BufferedInputFile(csv_data.encode('utf-8'), filename="feedback_export.csv"),
        caption="💬 **Feedback Export**\n\nAll feedback has been exported.",
        reply_markup=KeyboardBuilder.back_button("admin:export"),
        parse_mode="Markdown"
    )
    await callback.answer("Feedback exported!")


@router.callback_query(F.data == "export:predictions")
async def export_predictions(callback: CallbackQuery, is_admin: bool = False):
    """Export all predictions as CSV."""
    if not is_admin:
        await callback.answer(ADMIN_MESSAGES["no_permission"], show_alert=True)
        return
    
    csv_data = await AnalyticsService.export_predictions_csv()
    
    await callback.message.delete()
    await callback.message.answer_document(
        document=BufferedInputFile(csv_data.encode('utf-8'), filename="predictions_export.csv"),
        caption="🔮 **Predictions Export**\n\nAll predictions have been exported.",
        reply_markup=KeyboardBuilder.back_button("admin:export"),
        parse_mode="Markdown"
    )
    await callback.answer("Predictions exported!")
