"""
AI Service - Local model integration using joblib.
This module handles loading and inference with the local Stacking Ensemble model.
"""

import sys
import warnings
from typing import Dict, Any, Optional, List
import joblib
import os
import random
import logging
import numpy as np
import pandas as pd
from pathlib import Path

# Suppress sklearn warnings about feature names and semi-supervised NaN issues
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', message='.*invalid value encountered in divide.*')

# Ensure the parent directory is in the path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.constants import PLACEHOLDER_ADVICE, PROFESSIONAL_HELP_WARNING, ADVICE_CATEGORIES
from model.preprocessing import (
    prepare_features_for_model,
    map_prediction_to_anxiety,
    CLASS_MAPPING as PREPROCESSING_CLASS_MAPPING
)

logger = logging.getLogger(__name__)

# Class mapping: model class -> (anxiety_level, class_name, description)
# Note: The model uses LabelEncoder which sorts classes alphabetically: High=0, Low=1, Medium=2
CLASS_MAPPING = {
    0: (9, 'High', 'High Anxiety'),    # 'High' is first alphabetically
    1: (2, 'Low', 'Low Anxiety'),      # 'Low' is second
    2: (6, 'Medium', 'Medium Anxiety') # 'Medium' is third
}

# Global model instance
_model = None
_model_loaded = False


def _load_model():
    """
    Load the Stacking Ensemble model from disk using joblib.
    Patches the model to handle NaN values that may occur in intermediate estimators.
    Called once at startup.
    """
    global _model, _model_loaded
    
    if _model_loaded:
        return _model
    
    try:
        model_path = Path(__file__).parent.parent / "model" / "enn.pkl"
        
        if not model_path.exists():
            logger.error(f"Model file not found at {model_path}")
            _model = None
            _model_loaded = True
            return None
        
        model = joblib.load(model_path)
        
        # Store original transform
        original_transform = model.transform
        
        def safe_transform(X):
            """
            Wrapper for transform that safely handles NaN and inf values.
            The semi-supervised estimators (LabelSpreading, LabelPropagation) in the
            stacking ensemble can produce NaN during division operations.
            """
            try:
                # First, ensure input is clean (no NaN, inf)
                X_clean = X.copy()
                X_clean = X_clean.fillna(0)
                X_array = np.asarray(X_clean)
                X_array = np.nan_to_num(X_array, nan=0.0, posinf=1.0, neginf=-1.0)
                
                # Convert back to DataFrame to preserve column names if needed
                if isinstance(X, pd.DataFrame):
                    X_clean = pd.DataFrame(X_array, columns=X.columns)
                
                # Call original transform
                result = original_transform(X_clean)
                
                # Clean output: replace any NaN/inf that occurred during transform
                result = np.asarray(result)
                result = np.nan_to_num(result, nan=0.0, posinf=1.0, neginf=-1.0)
                
                return result
                
            except Exception as e:
                logger.warning(f"Error in safe_transform: {e}. Returning zeros.")
                return np.zeros((X.shape[0], model.n_classes_))
        
        model.transform = safe_transform
        _model = model
        
        logger.info(f"Successfully loaded Stacking Ensemble model from {model_path}")
        logger.info(f"Model classes: {model.classes_}, Features: {model.n_features_in_}")
        _model_loaded = True
        return _model
    
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        _model = None
        _model_loaded = True
        return None


def _prepare_features(data: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Prepare features for the model in the correct format.
    The Stacking Ensemble model expects a pandas DataFrame with specific feature names.
    
    Model expects 18 features in this exact order:
    ['Age', 'Gender', 'Occupation', 'Sleep Hours', 'Physical Activity (hrs/week)',
     'Caffeine Intake (mg/day)', 'Alcohol Consumption (drinks/week)', 'Smoking',
     'Family History of Anxiety', 'Stress Level (1-10)', 'Heart Rate (bpm)',
     'Breathing Rate (breaths/min)', 'Sweating Level (1-5)', 'Dizziness',
     'Medication', 'Therapy Sessions (per month)', 'Recent Major Life Event',
     'Diet Quality (1-10)']
    
    Args:
        data: Raw input data from user check-in (daily or weekly check)
    
    Returns:
        DataFrame with features in the order expected by the model, or None if data is invalid
    """
    try:
        # Extract and convert user inputs to model features
        # User profile data
        age = float(data.get('age', 30) or 30)
        
        # Encode Gender as numeric: male=0, female=1, other=2
        gender_str = str(data.get('gender', '')).lower()
        gender_map = {'male': 0, 'female': 1, 'other': 2, 'not set': 2}
        gender = float(gender_map.get(gender_str, 2))
        
        # Encode Occupation as numeric: student=0, employed=1, unemployed=2, retired=3, other=4
        occupation_str = str(data.get('occupation', '')).lower().replace('_', ' ')
        occupation_map = {
            'student': 0, 'employed': 1, 'unemployed': 2, 
            'retired': 3, 'self employed': 1, 'other': 4, 'not set': 4
        }
        occupation = float(occupation_map.get(occupation_str, 4))
        
        # Lifestyle metrics
        sleep = float(data.get('sleep_hours', 7) or 7)  # Hours
        physical_activity = float(data.get('physical_activity', 0) or 0)  # Convert to hrs/week (0=sedentary, 1=light, 2=moderate, 3=vigorous)
        caffeine = float(data.get('caffeine_intake', 0) or 0)  # Convert cups to mg/day (assume 1 cup = 95mg)
        caffeine_mg = caffeine * 95
        alcohol = float(data.get('alcohol_intake', 0) or 0)  # Already in drinks/week
        
        # Smoking (from profile, 0=never, 1=former, 2=current)
        smoking = float(data.get('smoking_habits', 0) or 0)
        
        # Mental health history
        family_anxiety = float(data.get('family_anxiety_history', 0) or 0)  # 0 or 1
        
        # Current metrics from check-in
        stress = float(data.get('stress_level', 5) or 5)  # 1-10 scale
        heart_rate = float(data.get('heart_rate', 70) or 70)  # BPM
        breathing = float(data.get('breathing_rate', 16) or 16)  # Breaths per minute
        sweating = float(data.get('sweating_level', 1) or 1)  # 1-5 scale
        dizziness = float(data.get('dizziness_today', 0) or 0)  # Binary or scale
        
        # Medical info
        medication = float(data.get('medication_use', 0) or 0)  # 0=no, 1=yes
        
        # Therapy frequency: Map string values to sessions/month
        therapy_freq_raw = data.get('therapy_frequency', 'no')
        therapy_map = {'no': 0, 'rarely': 0.25, 'monthly': 1, 'bi_weekly': 2, 'weekly': 4}
        therapy_sessions = float(therapy_map.get(str(therapy_freq_raw).lower(), 0))  # Default to 0
        
        # Life events
        recent_life_event = 1 if data.get('recent_life_events') else 0  # Binary: has significant event
        
        # Diet quality
        diet_quality = float(data.get('diet_quality', 2) or 2)  # 1-10 scale
        
        # Create DataFrame with EXACT feature names expected by model
        feature_dict = {
            'Age': age,
            'Gender': gender,
            'Occupation': occupation,
            'Sleep Hours': sleep,
            'Physical Activity (hrs/week)': physical_activity,
            'Caffeine Intake (mg/day)': caffeine_mg,
            'Alcohol Consumption (drinks/week)': alcohol,
            'Smoking': smoking,
            'Family History of Anxiety': family_anxiety,
            'Stress Level (1-10)': stress,
            'Heart Rate (bpm)': heart_rate,
            'Breathing Rate (breaths/min)': breathing,
            'Sweating Level (1-5)': sweating,
            'Dizziness': dizziness,
            'Medication': medication,
            'Therapy Sessions (per month)': therapy_sessions,
            'Recent Major Life Event': recent_life_event,
            'Diet Quality (1-10)': diet_quality
        }
        
        # Create DataFrame and ensure all values are valid (no NaN, inf)
        df = pd.DataFrame([feature_dict])
        
        # Clean the DataFrame: replace any NaN/inf with safe defaults
        df = df.fillna(5.0)  # Fill NaN with neutral value
        df = df.replace([np.inf, -np.inf], 5.0)  # Replace inf with neutral value
        
        # Ensure all values are finite and reasonable
        for col in df.columns:
            if df[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
                df[col] = np.where(np.isfinite(df[col]), df[col], 5.0)
        
        logger.debug(f"Prepared features shape: {df.shape}, Clean: {df.isnull().sum().sum() == 0}")
        
        return df
    
    except (ValueError, TypeError) as e:
        logger.error(f"Error preparing features: {e}")
        return None


async def call_ai_model(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the local Stacking Ensemble model with user data.
    
    The model was trained on the enhanced anxiety dataset with 3 classes:
    - Class 0: High anxiety (LabelEncoder alphabetical order)
    - Class 1: Low anxiety
    - Class 2: Medium anxiety
    
    Args:
        data: Dictionary containing user's mental health data including:
            - stress_level: int (1-10)
            - anxiety_level: int (1-10)
            - sleep_hours: float
            - heart_rate: int
            - breathing_rate: int
            - caffeine_intake: int
            - alcohol_intake: int
            - mood_rating: int (1-10)
            - energy_level: int (1-10)
            - sweating_level: int (1-5)
            - dizziness_today: int/bool
    
    Returns:
        Dictionary containing:
            - predicted_anxiety_level: int (1-10)
            - confidence_score: float (0-1)
            - advice: str
            - advice_category: str (low, moderate, high)
            - model_version: str
    """
    # Load model if not already loaded
    model = _load_model()
    
    # If model failed to load, fallback to rule-based predictions
    if model is None:
        logger.warning("Using fallback rule-based prediction (model unavailable)")
        return _fallback_prediction(data)
    
    # Prepare and scale features using the preprocessing module
    features_df = prepare_features_for_model(data)
    if features_df is None:
        logger.warning("Invalid features, using fallback prediction")
        return _fallback_prediction(data)
    
    try:
        # Predict with the patched model that handles NaN values
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            prediction = model.predict(features_df)
        
        predicted_class = int(prediction[0])
        
        # Map model output classes to anxiety levels (1-10 scale)
        # Model classes use LabelEncoder alphabetical order: 0=High, 1=Low, 2=Medium
        mapping = map_prediction_to_anxiety(predicted_class)
        predicted_anxiety = mapping["level"]
        class_name = mapping["name"]
        class_description = mapping["description"]
        
        # Determine category based on predicted anxiety level
        if predicted_anxiety <= 4:
            category = "low"
        elif predicted_anxiety <= 7:
            category = "moderate"
        else:
            category = "high"
        
        # Get appropriate advice based on the predicted level
        advice = get_advice_for_level(predicted_anxiety)
        
        # Calculate confidence score from model probabilities
        confidence = _calculate_confidence(model, features_df, predicted_anxiety)
        
        logger.info(f"Model prediction: class={predicted_class} ({class_name}), anxiety_level={predicted_anxiety}, confidence={confidence:.2%}")
        
        return {
            "predicted_anxiety_level": predicted_anxiety,
            "anxiety_class_name": class_name,  # 'Low', 'Medium', 'High'
            "anxiety_class_description": class_description,  # Full description
            "confidence_score": confidence,
            "advice": advice,
            "advice_category": category,
            "model_version": "stacking_ensemble_v1.0"
        }
    
    except Exception as e:
        logger.error(f"Error during model inference: {type(e).__name__}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return _fallback_prediction(data)


def _calculate_confidence(model, features: np.ndarray, prediction: float) -> float:
    """
    Calculate confidence score for the prediction.
    
    Args:
        model: The trained model
        features: Input features array
        prediction: The predicted value
    
    Returns:
        Confidence score between 0 and 1
    """
    try:
        # Try to use decision_function if available (for some models)
        if hasattr(model, 'decision_function'):
            decision = model.decision_function(features)
            # Normalize to 0-1 range
            confidence = float(1 / (1 + np.exp(-decision[0])))
        
        # Try to use predict_proba if available
        elif hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)
            confidence = float(np.max(proba))
        
        # Default confidence
        else:
            confidence = 0.75
        
        return max(0.0, min(1.0, confidence))
    
    except:
        return 0.75


def _fallback_prediction(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback rule-based prediction when model is unavailable.
    Uses user-reported anxiety level with slight variation.
    
    Args:
        data: User health data
    
    Returns:
        Prediction dictionary
    """
    # Use the user's self-reported anxiety level with slight variation
    user_anxiety = data.get('anxiety_level', 5)
    
    # Add some random variation for demonstration
    predicted_anxiety = max(1, min(10, user_anxiety + random.randint(-1, 1)))
    
    # Determine advice category
    if predicted_anxiety <= 3:
        category = "low"
    elif predicted_anxiety <= 6:
        category = "moderate"
    else:
        category = "high"
    
    # Get appropriate advice
    advice = get_advice_for_level(predicted_anxiety)
    
    return {
        "predicted_anxiety_level": predicted_anxiety,
        "confidence_score": 0.65,
        "advice": advice,
        "advice_category": category,
        "model_version": "fallback_v1.0"
    }


def get_advice_for_level(anxiety_level: int) -> str:
    """
    Get appropriate advice based on anxiety level.
    
    Args:
        anxiety_level: The anxiety level (1-10)
    
    Returns:
        Advice string with appropriate recommendations
    """
    if anxiety_level <= 3:
        advice_list = PLACEHOLDER_ADVICE["low"]
        base_advice = random.choice(advice_list)
    elif anxiety_level <= 6:
        advice_list = PLACEHOLDER_ADVICE["moderate"]
        base_advice = random.choice(advice_list)
    else:
        advice_list = PLACEHOLDER_ADVICE["high"]
        base_advice = random.choice(advice_list)
        # Add professional help warning for high anxiety
        base_advice += "\n\n" + PROFESSIONAL_HELP_WARNING
    
    return base_advice


async def get_personalized_recommendations(user_profile: Dict[str, Any], 
                                           recent_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get personalized recommendations based on user profile and recent data.
    
    Placeholder function for future AI integration.
    
    Args:
        user_profile: User's profile data
        recent_data: Recent check-in data
    
    Returns:
        Dictionary containing personalized recommendations
    """
    # Placeholder implementation
    recommendations = {
        "lifestyle": [],
        "mental_health": [],
        "immediate_actions": []
    }
    
    # Basic rule-based recommendations (placeholder)
    sleep_hours = recent_data.get('sleep_hours', 7)
    if sleep_hours < 6:
        recommendations["lifestyle"].append(
            "💤 Consider improving your sleep schedule. Aim for 7-8 hours per night."
        )
    
    caffeine = recent_data.get('caffeine_intake', 0)
    if caffeine > 4:
        recommendations["lifestyle"].append(
            "☕ Your caffeine intake is high. Consider reducing to improve sleep quality."
        )
    
    stress_level = recent_data.get('stress_level', 5)
    if stress_level > 6:
        recommendations["mental_health"].append(
            "🧘 High stress detected. Try deep breathing exercises or meditation."
        )
    
    recommendations["immediate_actions"].append(
        "🚶 Take a 10-minute walk to clear your mind."
    )
    
    return recommendations


async def analyze_trends(historical_data: list) -> Dict[str, Any]:
    """
    Analyze trends in user's historical data.
    
    Placeholder function for future AI integration.
    
    Args:
        historical_data: List of historical check-in data
    
    Returns:
        Dictionary containing trend analysis
    """
    if not historical_data:
        return {
            "trend_direction": "neutral",
            "summary": "Not enough data for trend analysis."
        }
    
    # Placeholder trend analysis
    anxiety_levels = [d.get('anxiety_level', 5) for d in historical_data if d.get('anxiety_level')]
    
    if len(anxiety_levels) < 2:
        return {
            "trend_direction": "neutral",
            "summary": "Not enough data points for trend analysis."
        }
    
    # Simple trend calculation
    recent_avg = sum(anxiety_levels[-3:]) / min(len(anxiety_levels), 3)
    older_avg = sum(anxiety_levels[:-3]) / max(len(anxiety_levels) - 3, 1)
    
    if recent_avg > older_avg + 0.5:
        trend = "increasing"
        summary = "📈 Your anxiety levels have been increasing recently. Consider taking steps to manage stress."
    elif recent_avg < older_avg - 0.5:
        trend = "decreasing"
        summary = "📉 Great news! Your anxiety levels have been decreasing. Keep up the good work!"
    else:
        trend = "stable"
        summary = "➡️ Your anxiety levels have been stable. Continue monitoring and maintaining your routine."
    
    return {
        "trend_direction": trend,
        "recent_average": round(recent_avg, 1),
        "overall_average": round(sum(anxiety_levels) / len(anxiety_levels), 1),
        "summary": summary
    }
