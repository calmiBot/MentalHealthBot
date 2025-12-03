"""
User Service - Database operations for users and profiles.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import User, UserProfile, DailyAnswer, WeeklyAnswer, History, Prediction, Feedback, Reminder
from database.session import get_session


class UserService:
    """Service for user-related database operations."""
    
    @staticmethod
    async def get_or_create_user(
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None
    ) -> User:
        """Get existing user or create a new one."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Update last active time
                user.last_active_at = datetime.utcnow()
                if username:
                    user.username = username
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                await session.commit()
                return user
            
            # Create new user
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def get_user(user_id: int) -> Optional[User]:
        """Get user by ID."""
        async with get_session() as session:
            result = await session.execute(
                select(User).options(selectinload(User.profile)).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_with_profile(user_id: int) -> Optional[User]:
        """Get user with profile data."""
        async with get_session() as session:
            result = await session.execute(
                select(User).options(selectinload(User.profile)).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                await session.commit()
                await session.refresh(user)
            
            return user
    
    @staticmethod
    async def mark_user_onboarded(user_id: int) -> None:
        """Mark user as onboarded."""
        async with get_session() as session:
            await session.execute(
                update(User).where(User.id == user_id).values(is_onboarded=True)
            )
            await session.commit()
    
    @staticmethod
    async def is_user_onboarded(user_id: int) -> bool:
        """Check if user has completed onboarding."""
        async with get_session() as session:
            result = await session.execute(
                select(User.is_onboarded).where(User.id == user_id)
            )
            is_onboarded = result.scalar_one_or_none()
            return bool(is_onboarded)
    
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """Delete user and all associated data."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                await session.delete(user)
                await session.commit()
                return True
            return False
    
    @staticmethod
    async def get_all_users(
        page: int = 1,
        per_page: int = 10,
        active_only: bool = False
    ) -> tuple[List[User], int]:
        """Get paginated list of users."""
        async with get_session() as session:
            query = select(User)
            
            if active_only:
                query = query.where(User.is_active == True)
            
            # Get total count
            count_query = select(func.count()).select_from(User)
            if active_only:
                count_query = count_query.where(User.is_active == True)
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.order_by(User.registered_at.desc())
            query = query.offset((page - 1) * per_page).limit(per_page)
            
            result = await session.execute(query)
            users = result.scalars().all()
            
            return list(users), total


class ProfileService:
    """Service for user profile operations."""
    
    @staticmethod
    async def create_or_update_profile(user_id: int, **kwargs) -> UserProfile:
        """Create or update user profile."""
        async with get_session() as session:
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if profile:
                for key, value in kwargs.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                profile.updated_at = datetime.utcnow()
            else:
                profile = UserProfile(user_id=user_id, **kwargs)
                session.add(profile)
            
            await session.commit()
            await session.refresh(profile)
            return profile
    
    @staticmethod
    async def get_profile(user_id: int) -> Optional[UserProfile]:
        """Get user profile."""
        async with get_session() as session:
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def update_profile_field(user_id: int, field: str, value: Any) -> bool:
        """Update a single profile field."""
        async with get_session() as session:
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if profile and hasattr(profile, field):
                setattr(profile, field, value)
                profile.updated_at = datetime.utcnow()
                await session.commit()
                return True
            return False


class DailyAnswerService:
    """Service for daily check-in operations."""
    
    @staticmethod
    async def create_daily_answer(user_id: int, **kwargs) -> DailyAnswer:
        """Create a daily answer record."""
        async with get_session() as session:
            answer = DailyAnswer(user_id=user_id, **kwargs)
            session.add(answer)
            await session.commit()
            await session.refresh(answer)
            return answer
    
    @staticmethod
    async def get_daily_answers(
        user_id: int,
        days: int = 30,
        page: int = 1,
        per_page: int = 10
    ) -> tuple[List[DailyAnswer], int]:
        """Get user's daily answers."""
        async with get_session() as session:
            since = datetime.utcnow() - timedelta(days=days)
            
            query = select(DailyAnswer).where(
                and_(
                    DailyAnswer.user_id == user_id,
                    DailyAnswer.date >= since
                )
            ).order_by(DailyAnswer.date.desc())
            
            # Get total count
            count_query = select(func.count()).select_from(DailyAnswer).where(
                and_(
                    DailyAnswer.user_id == user_id,
                    DailyAnswer.date >= since
                )
            )
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            answers = result.scalars().all()
            
            return list(answers), total
    
    @staticmethod
    async def get_latest_daily_answer(user_id: int) -> Optional[DailyAnswer]:
        """Get the most recent daily answer."""
        async with get_session() as session:
            result = await session.execute(
                select(DailyAnswer)
                .where(DailyAnswer.user_id == user_id)
                .order_by(DailyAnswer.date.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def has_checked_in_today(user_id: int) -> bool:
        """Check if user has already checked in today."""
        async with get_session() as session:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            result = await session.execute(
                select(func.count()).select_from(DailyAnswer).where(
                    and_(
                        DailyAnswer.user_id == user_id,
                        DailyAnswer.date >= today_start
                    )
                )
            )
            count = result.scalar()
            return count > 0


class WeeklyAnswerService:
    """Service for weekly assessment operations."""
    
    @staticmethod
    async def create_weekly_answer(user_id: int, week_start: datetime, week_end: datetime, **kwargs) -> WeeklyAnswer:
        """Create a weekly answer record."""
        async with get_session() as session:
            answer = WeeklyAnswer(
                user_id=user_id,
                week_start=week_start,
                week_end=week_end,
                **kwargs
            )
            session.add(answer)
            await session.commit()
            await session.refresh(answer)
            return answer
    
    @staticmethod
    async def get_weekly_answers(
        user_id: int,
        weeks: int = 12,
        page: int = 1,
        per_page: int = 10
    ) -> tuple[List[WeeklyAnswer], int]:
        """Get user's weekly answers."""
        async with get_session() as session:
            since = datetime.utcnow() - timedelta(weeks=weeks)
            
            query = select(WeeklyAnswer).where(
                and_(
                    WeeklyAnswer.user_id == user_id,
                    WeeklyAnswer.week_start >= since
                )
            ).order_by(WeeklyAnswer.week_start.desc())
            
            # Get total count
            count_query = select(func.count()).select_from(WeeklyAnswer).where(
                and_(
                    WeeklyAnswer.user_id == user_id,
                    WeeklyAnswer.week_start >= since
                )
            )
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            answers = result.scalars().all()
            
            return list(answers), total


class HistoryService:
    """Service for history tracking."""
    
    @staticmethod
    async def add_history_entry(user_id: int, event_type: str, event_data: Optional[Dict] = None) -> History:
        """Add a history entry."""
        async with get_session() as session:
            entry = History(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            return entry
    
    @staticmethod
    async def get_user_history(
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[History], int]:
        """Get user's history."""
        async with get_session() as session:
            query = select(History).where(History.user_id == user_id).order_by(History.created_at.desc())
            
            # Get total count
            count_query = select(func.count()).select_from(History).where(History.user_id == user_id)
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            entries = result.scalars().all()
            
            return list(entries), total


class PredictionService:
    """Service for prediction operations."""
    
    @staticmethod
    async def create_prediction(
        user_id: int,
        predicted_anxiety_level: int,
        advice: str,
        advice_category: str,
        confidence_score: Optional[float] = None,
        model_version: Optional[str] = None,
        daily_answer_id: Optional[int] = None,
        weekly_answer_id: Optional[int] = None,
        api_response_raw: Optional[Dict] = None
    ) -> Prediction:
        """Create a prediction record."""
        async with get_session() as session:
            prediction = Prediction(
                user_id=user_id,
                predicted_anxiety_level=predicted_anxiety_level,
                advice=advice,
                advice_category=advice_category,
                confidence_score=confidence_score,
                model_version=model_version,
                daily_answer_id=daily_answer_id,
                weekly_answer_id=weekly_answer_id,
                api_response_raw=api_response_raw
            )
            session.add(prediction)
            await session.commit()
            await session.refresh(prediction)
            return prediction
    
    @staticmethod
    async def get_user_predictions(
        user_id: int,
        page: int = 1,
        per_page: int = 10
    ) -> tuple[List[Prediction], int]:
        """Get user's predictions."""
        async with get_session() as session:
            query = select(Prediction).where(Prediction.user_id == user_id).order_by(Prediction.created_at.desc())
            
            # Get total count
            count_query = select(func.count()).select_from(Prediction).where(Prediction.user_id == user_id)
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            predictions = result.scalars().all()
            
            return list(predictions), total


class FeedbackService:
    """Service for feedback operations."""
    
    @staticmethod
    async def create_feedback(
        user_id: int,
        feedback_type: str,
        target_type: str,
        prediction_id: Optional[int] = None,
        rating: Optional[int] = None,
        feedback_text: Optional[str] = None
    ) -> Feedback:
        """Create a feedback record."""
        async with get_session() as session:
            feedback = Feedback(
                user_id=user_id,
                feedback_type=feedback_type,
                target_type=target_type,
                prediction_id=prediction_id,
                rating=rating,
                feedback_text=feedback_text
            )
            session.add(feedback)
            await session.commit()
            await session.refresh(feedback)
            return feedback
    
    @staticmethod
    async def get_all_feedback(
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[Feedback], int]:
        """Get all feedback (for admin)."""
        async with get_session() as session:
            query = select(Feedback).order_by(Feedback.created_at.desc())
            
            # Get total count
            count_query = select(func.count()).select_from(Feedback)
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            feedback_list = result.scalars().all()
            
            return list(feedback_list), total


class ReminderService:
    """Service for reminder operations."""
    
    @staticmethod
    async def create_or_update_reminder(
        user_id: int,
        reminder_type: str,
        hour: int = 10,
        minute: int = 0,
        day_of_week: Optional[int] = None
    ) -> Reminder:
        """Create or update a reminder."""
        async with get_session() as session:
            result = await session.execute(
                select(Reminder).where(
                    and_(
                        Reminder.user_id == user_id,
                        Reminder.reminder_type == reminder_type
                    )
                )
            )
            reminder = result.scalar_one_or_none()
            
            if reminder:
                reminder.hour = hour
                reminder.minute = minute
                reminder.day_of_week = day_of_week
            else:
                reminder = Reminder(
                    user_id=user_id,
                    reminder_type=reminder_type,
                    hour=hour,
                    minute=minute,
                    day_of_week=day_of_week
                )
                session.add(reminder)
            
            await session.commit()
            await session.refresh(reminder)
            return reminder
    
    @staticmethod
    async def get_users_for_reminder(reminder_type: str, day_of_week: Optional[int] = None) -> List[int]:
        """Get user IDs that should receive reminders."""
        async with get_session() as session:
            query = select(User.id).join(Reminder).where(
                and_(
                    Reminder.reminder_type == reminder_type,
                    Reminder.is_active == True,
                    User.notifications_enabled == True,
                    User.is_active == True
                )
            )
            
            if day_of_week is not None:
                query = query.where(Reminder.day_of_week == day_of_week)
            
            result = await session.execute(query)
            return [row[0] for row in result.all()]
    
    @staticmethod
    async def mark_reminder_sent(user_id: int, reminder_type: str) -> None:
        """Mark reminder as sent."""
        async with get_session() as session:
            await session.execute(
                update(Reminder)
                .where(
                    and_(
                        Reminder.user_id == user_id,
                        Reminder.reminder_type == reminder_type
                    )
                )
                .values(last_sent_at=datetime.utcnow())
            )
            await session.commit()
