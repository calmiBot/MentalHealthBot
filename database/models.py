"""
Database models for the Mental Health Bot.
Uses SQLAlchemy 2.0 async with full type annotations.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Text, ForeignKey,
    BigInteger, JSON
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""
    pass


class User(Base):
    """Main user table storing Telegram user information."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user ID
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Registration and activity tracking
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Notification preferences
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    anonymous_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    daily_answers: Mapped[List["DailyAnswer"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    weekly_answers: Mapped[List["WeeklyAnswer"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    history: Mapped[List["History"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feedback: Mapped[List["Feedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reminders: Mapped[List["Reminder"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    """User profile with demographics and stable health information."""
    __tablename__ = "user_profile"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Demographics
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    family_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Lifestyle Factors
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    physical_activity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # none, light, moderate, intense
    diet_quality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # poor, fair, good, excellent
    alcohol_intake: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-19 drinks per week
    caffeine_intake: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # cups per day
    smoking_habits: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # never, former, current
    
    # Mental & Physical Indicators (baseline)
    baseline_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    baseline_breathing_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    baseline_stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    sweating_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    dizziness_frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # never, rarely, sometimes, often
    
    # Mental Health History
    family_anxiety_history: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    medication_use: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    therapy_frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # never, past, current_monthly, current_weekly
    
    # Life Events
    recent_life_events: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Target Variable (baseline)
    baseline_anxiety_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="profile")


class DailyAnswer(Base):
    """Daily mental health check-in answers."""
    __tablename__ = "daily_answers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Date of the check-in
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Essential daily metrics
    stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    breathing_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    caffeine_intake: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    alcohol_intake: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    anxiety_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    
    # Extended metrics (optional)
    mood_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    energy_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    sweating_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    dizziness_today: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    physical_activity_today: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Form completion
    is_extended: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="daily_answers")


class WeeklyAnswer(Base):
    """Weekly comprehensive mental health assessment."""
    __tablename__ = "weekly_answers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Week information
    week_start: Mapped[datetime] = mapped_column(DateTime)
    week_end: Mapped[datetime] = mapped_column(DateTime)
    
    # Weekly averages
    avg_stress_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_anxiety_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Weekly totals
    total_caffeine: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_alcohol: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Weekly self-assessment
    overall_week_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    significant_events: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medication_adherence: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # full, partial, none
    therapy_attended: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Final anxiety assessment
    anxiety_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="weekly_answers")


class History(Base):
    """Complete history of user interactions and assessments."""
    __tablename__ = "history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Event type
    event_type: Mapped[str] = mapped_column(String(50))  # onboarding, daily_check, weekly_check, profile_update, etc.
    
    # Event data (JSON for flexibility)
    event_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="history")


class AdminUser(Base):
    """Admin users with elevated privileges."""
    __tablename__ = "admin_users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)  # Telegram user ID
    
    # Admin info
    added_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Permissions (for future granular control)
    can_view_users: Mapped[bool] = mapped_column(Boolean, default=True)
    can_export_data: Mapped[bool] = mapped_column(Boolean, default=True)
    can_manage_admins: Mapped[bool] = mapped_column(Boolean, default=False)


class Feedback(Base):
    """User feedback on predictions and advice."""
    __tablename__ = "feedback"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    prediction_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("predictions.id", ondelete="SET NULL"), nullable=True)
    
    # Feedback type
    feedback_type: Mapped[str] = mapped_column(String(50))  # helpful, not_accurate, detailed
    
    # Rating (for quick feedback)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 stars
    
    # Detailed feedback
    feedback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # What was being rated
    target_type: Mapped[str] = mapped_column(String(50))  # prediction, advice
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="feedback")
    prediction: Mapped[Optional["Prediction"]] = relationship(back_populates="feedback")


class Reminder(Base):
    """User reminder settings and history."""
    __tablename__ = "reminders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Reminder type
    reminder_type: Mapped[str] = mapped_column(String(50))  # daily, weekly, custom
    
    # Schedule
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0=Monday, 6=Sunday
    hour: Mapped[int] = mapped_column(Integer, default=10)
    minute: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="reminders")


class Prediction(Base):
    """AI model predictions and advice."""
    __tablename__ = "predictions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Input data reference
    daily_answer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("daily_answers.id", ondelete="SET NULL"), nullable=True)
    weekly_answer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("weekly_answers.id", ondelete="SET NULL"), nullable=True)
    
    # Prediction results
    predicted_anxiety_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Advice generated
    advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    advice_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # general, moderate, high_alert
    
    # Model info (for tracking)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    api_response_raw: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="predictions")
    feedback: Mapped[List["Feedback"]] = relationship(back_populates="prediction")
