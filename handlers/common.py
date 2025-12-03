"""
Common handlers - Start command and main menu.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from keyboards import KeyboardBuilder
from services import UserService
from states import OnboardingState
from utils.constants import MESSAGES, EMOJI
from config import settings

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, is_admin: bool = False):
    """Handle /start command."""
    user_id = message.from_user.id
    
    # Clear any existing state
    await state.clear()
    
    # Check if user is onboarded
    is_onboarded = await UserService.is_user_onboarded(user_id)
    
    if is_onboarded:
        # Show main menu for returning users
        await message.answer(
            f"👋 **Welcome back, {message.from_user.first_name or 'there'}!**\n\n"
            f"Good to see you again. What would you like to do today?",
            reply_markup=KeyboardBuilder.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )
    else:
        # Start onboarding for new users
        await message.answer(
            MESSAGES["welcome"],
            parse_mode="Markdown"
        )
        await message.answer(
            MESSAGES["onboarding_intro"],
            reply_markup=KeyboardBuilder.start_onboarding(),
            parse_mode="Markdown"
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(
        MESSAGES["help_message"],
        parse_mode="Markdown"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Handle /cancel command."""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("Nothing to cancel.")
        return
    
    await state.clear()
    await message.answer(
        MESSAGES["cancel_message"],
        reply_markup=KeyboardBuilder.main_menu(),
        parse_mode="Markdown"
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext, is_admin: bool = False):
    """Handle /menu command."""
    await state.clear()
    await message.answer(
        f"{EMOJI['home']} **Main Menu**\n\nSelect an option:",
        reply_markup=KeyboardBuilder.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )


# Callback handlers for main menu
@router.callback_query(F.data == "menu:main")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext, is_admin: bool = False):
    """Handle main menu callback."""
    await state.clear()
    await callback.message.edit_text(
        f"{EMOJI['home']} **Main Menu**\n\nSelect an option:",
        reply_markup=KeyboardBuilder.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:help")
async def callback_help(callback: CallbackQuery):
    """Handle help callback."""
    await callback.message.edit_text(
        MESSAGES["help_message"],
        reply_markup=KeyboardBuilder.back_button("menu:main"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext, is_admin: bool = False):
    """Handle cancel callback."""
    await state.clear()
    await callback.message.edit_text(
        MESSAGES["cancel_message"],
        reply_markup=KeyboardBuilder.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery):
    """Handle no-operation callback (for pagination display)."""
    await callback.answer()
