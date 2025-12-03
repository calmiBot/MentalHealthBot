"""
Middlewares for the Mental Health Bot.
Includes rate limiting, session timeout, and database middleware.
"""

from typing import Any, Awaitable, Callable, Dict
from datetime import datetime, timedelta
from collections import defaultdict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import settings


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting user requests."""
    
    def __init__(self, limit: int = None, period: int = None):
        """
        Initialize rate limiter.
        
        Args:
            limit: Maximum number of messages per period
            period: Time period in seconds
        """
        self.limit = limit or settings.rate_limit_messages
        self.period = period or settings.rate_limit_period
        self.user_requests: Dict[int, list] = defaultdict(list)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process the middleware."""
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=self.period)
            
            # Clean old requests
            self.user_requests[user_id] = [
                req_time for req_time in self.user_requests[user_id]
                if req_time > cutoff
            ]
            
            # Check rate limit
            if len(self.user_requests[user_id]) >= self.limit:
                # Rate limited - skip handler
                if isinstance(event, Message):
                    await event.answer(
                        "⚠️ You're sending messages too quickly. Please wait a moment."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "⚠️ Too many requests. Please slow down.",
                        show_alert=True
                    )
                return
            
            # Record this request
            self.user_requests[user_id].append(now)
        
        return await handler(event, data)


class SessionTimeoutMiddleware(BaseMiddleware):
    """Middleware for handling session timeouts in forms."""
    
    def __init__(self, timeout: int = None):
        """
        Initialize session timeout handler.
        
        Args:
            timeout: Session timeout in seconds
        """
        self.timeout = timeout or settings.session_timeout
        self.user_last_activity: Dict[int, datetime] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process the middleware."""
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id:
            now = datetime.utcnow()
            last_activity = self.user_last_activity.get(user_id)
            
            # Check for session timeout
            if last_activity:
                time_since_last = (now - last_activity).total_seconds()
                if time_since_last > self.timeout:
                    # Session timed out - clear FSM state
                    state = data.get("state")
                    if state:
                        current_state = await state.get_state()
                        if current_state:
                            await state.clear()
                            if isinstance(event, Message):
                                await event.answer(
                                    "⏰ Your session has timed out due to inactivity.\n"
                                    "Please start over with /start"
                                )
                            elif isinstance(event, CallbackQuery):
                                await event.answer(
                                    "Session timed out. Please start over.",
                                    show_alert=True
                                )
                            return
            
            # Update last activity
            self.user_last_activity[user_id] = now
        
        return await handler(event, data)


class UserActivityMiddleware(BaseMiddleware):
    """Middleware for tracking user activity."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process the middleware."""
        from services import UserService
        
        user_id = None
        username = None
        first_name = None
        last_name = None
        
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            username = event.from_user.username
            first_name = event.from_user.first_name
            last_name = event.from_user.last_name
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
            username = event.from_user.username
            first_name = event.from_user.first_name
            last_name = event.from_user.last_name
        
        if user_id:
            # Update user's last activity
            try:
                user = await UserService.get_or_create_user(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                data["user"] = user
            except Exception:
                pass
        
        return await handler(event, data)


class AdminCheckMiddleware(BaseMiddleware):
    """Middleware for checking admin permissions."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process the middleware."""
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id:
            data["is_admin"] = user_id in settings.admin_ids
        else:
            data["is_admin"] = False
        
        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user interactions."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process the middleware."""
        from loguru import logger
        
        user_id = None
        event_type = type(event).__name__
        
        if isinstance(event, Message):
            user_id = event.from_user.id
            logger.info(f"Message from user {user_id}: {event.text[:50] if event.text else 'No text'}...")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            logger.info(f"Callback from user {user_id}: {event.data}")
        
        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            logger.error(f"Error processing {event_type} from user {user_id}: {e}")
            raise
