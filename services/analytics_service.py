"""
Analytics Service - Statistics and data analysis.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, UserProfile, DailyAnswer, WeeklyAnswer, Prediction, Feedback
from database.session import get_session


class AnalyticsService:
    """Service for analytics and statistics."""
    
    @staticmethod
    async def get_user_statistics(user_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a user."""
        async with get_session() as session:
            # Get total check-ins
            checkin_count = await session.execute(
                select(func.count()).select_from(DailyAnswer).where(DailyAnswer.user_id == user_id)
            )
            total_checkins = checkin_count.scalar()
            
            # Get average anxiety
            avg_anxiety_result = await session.execute(
                select(func.avg(DailyAnswer.anxiety_level)).where(
                    and_(
                        DailyAnswer.user_id == user_id,
                        DailyAnswer.anxiety_level.isnot(None)
                    )
                )
            )
            avg_anxiety = avg_anxiety_result.scalar() or 0
            
            # Get average stress
            avg_stress_result = await session.execute(
                select(func.avg(DailyAnswer.stress_level)).where(
                    and_(
                        DailyAnswer.user_id == user_id,
                        DailyAnswer.stress_level.isnot(None)
                    )
                )
            )
            avg_stress = avg_stress_result.scalar() or 0
            
            # Get average sleep
            avg_sleep_result = await session.execute(
                select(func.avg(DailyAnswer.sleep_hours)).where(
                    and_(
                        DailyAnswer.user_id == user_id,
                        DailyAnswer.sleep_hours.isnot(None)
                    )
                )
            )
            avg_sleep = avg_sleep_result.scalar() or 0
            
            # Get streak (consecutive days)
            streak = await AnalyticsService._calculate_streak(session, user_id)
            
            # Get last check-in date
            last_checkin_result = await session.execute(
                select(DailyAnswer.date)
                .where(DailyAnswer.user_id == user_id)
                .order_by(DailyAnswer.date.desc())
                .limit(1)
            )
            last_checkin = last_checkin_result.scalar()
            
            return {
                "total_checkins": total_checkins,
                "avg_anxiety": round(avg_anxiety, 1) if avg_anxiety else 0,
                "avg_stress": round(avg_stress, 1) if avg_stress else 0,
                "avg_sleep": round(avg_sleep, 1) if avg_sleep else 0,
                "streak": streak,
                "last_checkin": last_checkin.strftime("%Y-%m-%d") if last_checkin else "Never"
            }
    
    @staticmethod
    async def _calculate_streak(session: AsyncSession, user_id: int) -> int:
        """Calculate consecutive check-in days."""
        result = await session.execute(
            select(DailyAnswer.date)
            .where(DailyAnswer.user_id == user_id)
            .order_by(DailyAnswer.date.desc())
        )
        dates = [row[0].date() for row in result.all()]
        
        if not dates:
            return 0
        
        streak = 0
        today = datetime.utcnow().date()
        expected_date = today
        
        for date in dates:
            if date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            elif date == expected_date + timedelta(days=1):
                # Account for today not yet checked in
                streak += 1
                expected_date = date - timedelta(days=1)
            else:
                break
        
        return streak
    
    @staticmethod
    async def get_anxiety_data_for_chart(user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get anxiety data for charting."""
        async with get_session() as session:
            since = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(DailyAnswer.date, DailyAnswer.anxiety_level)
                .where(
                    and_(
                        DailyAnswer.user_id == user_id,
                        DailyAnswer.date >= since,
                        DailyAnswer.anxiety_level.isnot(None)
                    )
                )
                .order_by(DailyAnswer.date.asc())
            )
            
            return [
                {"date": row[0], "anxiety_level": row[1]}
                for row in result.all()
            ]
    
    @staticmethod
    async def get_stress_data_for_chart(user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get stress data for charting."""
        async with get_session() as session:
            since = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(DailyAnswer.date, DailyAnswer.stress_level)
                .where(
                    and_(
                        DailyAnswer.user_id == user_id,
                        DailyAnswer.date >= since,
                        DailyAnswer.stress_level.isnot(None)
                    )
                )
                .order_by(DailyAnswer.date.asc())
            )
            
            return [
                {"date": row[0], "stress_level": row[1]}
                for row in result.all()
            ]
    
    @staticmethod
    async def get_combined_data_for_chart(user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get combined anxiety and stress data for charting."""
        async with get_session() as session:
            since = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(DailyAnswer.date, DailyAnswer.anxiety_level, DailyAnswer.stress_level)
                .where(
                    and_(
                        DailyAnswer.user_id == user_id,
                        DailyAnswer.date >= since
                    )
                )
                .order_by(DailyAnswer.date.asc())
            )
            
            return [
                {
                    "date": row[0],
                    "anxiety_level": row[1] or 0,
                    "stress_level": row[2] or 0
                }
                for row in result.all()
            ]
    
    @staticmethod
    async def get_sleep_data_for_chart(user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get sleep data for charting."""
        async with get_session() as session:
            since = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(DailyAnswer.date, DailyAnswer.sleep_hours)
                .where(
                    and_(
                        DailyAnswer.user_id == user_id,
                        DailyAnswer.date >= since,
                        DailyAnswer.sleep_hours.isnot(None)
                    )
                )
                .order_by(DailyAnswer.date.asc())
            )
            
            return [
                {"date": row[0], "sleep_hours": row[1]}
                for row in result.all()
            ]
    
    @staticmethod
    async def get_admin_statistics() -> Dict[str, Any]:
        """Get comprehensive admin statistics."""
        async with get_session() as session:
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Total users
            total_users_result = await session.execute(
                select(func.count()).select_from(User)
            )
            total_users = total_users_result.scalar()
            
            # Active users (7 days)
            active_7d_result = await session.execute(
                select(func.count()).select_from(User).where(User.last_active_at >= week_ago)
            )
            active_7d = active_7d_result.scalar()
            
            # Active users (30 days)
            active_30d_result = await session.execute(
                select(func.count()).select_from(User).where(User.last_active_at >= month_ago)
            )
            active_30d = active_30d_result.scalar()
            
            # Average anxiety (all users)
            avg_anxiety_result = await session.execute(
                select(func.avg(DailyAnswer.anxiety_level)).where(DailyAnswer.anxiety_level.isnot(None))
            )
            avg_anxiety = avg_anxiety_result.scalar() or 0
            
            # Total check-ins
            total_checkins_result = await session.execute(
                select(func.count()).select_from(DailyAnswer)
            )
            total_checkins = total_checkins_result.scalar()
            
            # New users today
            new_today_result = await session.execute(
                select(func.count()).select_from(User).where(User.registered_at >= today_start)
            )
            new_users_today = new_today_result.scalar()
            
            # New users this week
            new_week_result = await session.execute(
                select(func.count()).select_from(User).where(User.registered_at >= week_ago)
            )
            new_users_week = new_week_result.scalar()
            
            # Anxiety distribution
            anxiety_dist = await AnalyticsService._get_anxiety_distribution(session)
            
            # New users trend (last 7 days)
            new_users_trend = await AnalyticsService._get_new_users_trend(session, 7)
            
            return {
                "total_users": total_users,
                "active_7d": active_7d,
                "active_30d": active_30d,
                "avg_anxiety": round(avg_anxiety, 1) if avg_anxiety else 0,
                "total_checkins": total_checkins,
                "new_users_today": new_users_today,
                "new_users_week": new_users_week,
                "anxiety_distribution": anxiety_dist,
                "new_users_trend": new_users_trend
            }
    
    @staticmethod
    async def _get_anxiety_distribution(session: AsyncSession) -> Dict[str, int]:
        """Get distribution of anxiety levels."""
        result = await session.execute(
            select(DailyAnswer.anxiety_level, func.count())
            .where(DailyAnswer.anxiety_level.isnot(None))
            .group_by(DailyAnswer.anxiety_level)
        )
        
        return {str(row[0]): row[1] for row in result.all()}
    
    @staticmethod
    async def _get_new_users_trend(session: AsyncSession, days: int) -> List[Dict[str, Any]]:
        """Get new users trend over the past N days."""
        trend = []
        today = datetime.utcnow().date()
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            
            result = await session.execute(
                select(func.count()).select_from(User).where(
                    and_(User.registered_at >= start, User.registered_at <= end)
                )
            )
            count = result.scalar()
            trend.append({"date": date, "count": count})
        
        return trend
    
    @staticmethod
    async def export_users_csv() -> str:
        """Export users data as CSV string."""
        async with get_session() as session:
            result = await session.execute(
                select(User).order_by(User.registered_at.desc())
            )
            users = result.scalars().all()
            
            lines = ["id,username,first_name,last_name,registered_at,last_active_at,is_onboarded,notifications_enabled"]
            
            for user in users:
                lines.append(
                    f"{user.id},{user.username or ''},{user.first_name or ''},{user.last_name or ''},"
                    f"{user.registered_at},{user.last_active_at},{user.is_onboarded},{user.notifications_enabled}"
                )
            
            return "\n".join(lines)
    
    @staticmethod
    async def export_checkins_csv() -> str:
        """Export all check-ins as CSV string."""
        async with get_session() as session:
            result = await session.execute(
                select(DailyAnswer).order_by(DailyAnswer.date.desc())
            )
            answers = result.scalars().all()
            
            lines = ["id,user_id,date,stress_level,anxiety_level,heart_rate,breathing_rate,sleep_hours,caffeine_intake,alcohol_intake"]
            
            for answer in answers:
                lines.append(
                    f"{answer.id},{answer.user_id},{answer.date},"
                    f"{answer.stress_level or ''},{answer.anxiety_level or ''},"
                    f"{answer.heart_rate or ''},{answer.breathing_rate or ''},"
                    f"{answer.sleep_hours or ''},{answer.caffeine_intake or ''},{answer.alcohol_intake or ''}"
                )
            
            return "\n".join(lines)
    
    @staticmethod
    async def export_feedback_csv() -> str:
        """Export all feedback as CSV string."""
        async with get_session() as session:
            result = await session.execute(
                select(Feedback).order_by(Feedback.created_at.desc())
            )
            feedback_list = result.scalars().all()
            
            lines = ["id,user_id,prediction_id,feedback_type,target_type,rating,feedback_text,created_at"]
            
            for feedback in feedback_list:
                text = (feedback.feedback_text or "").replace(",", ";").replace("\n", " ")
                lines.append(
                    f"{feedback.id},{feedback.user_id},{feedback.prediction_id or ''},"
                    f"{feedback.feedback_type},{feedback.target_type},{feedback.rating or ''},{text},{feedback.created_at}"
                )
            
            return "\n".join(lines)
    
    @staticmethod
    async def export_predictions_csv() -> str:
        """Export all predictions as CSV string."""
        async with get_session() as session:
            result = await session.execute(
                select(Prediction).order_by(Prediction.created_at.desc())
            )
            predictions = result.scalars().all()
            
            lines = ["id,user_id,predicted_anxiety_level,confidence_score,advice_category,model_version,created_at"]
            
            for prediction in predictions:
                lines.append(
                    f"{prediction.id},{prediction.user_id},{prediction.predicted_anxiety_level},"
                    f"{prediction.confidence_score or ''},{prediction.advice_category or ''},"
                    f"{prediction.model_version or ''},{prediction.created_at}"
                )
            
            return "\n".join(lines)
