"""
Preprocessing module for the anxiety prediction model.

This module provides feature scaling and encoding to match the training data preprocessing.
The model (enn.pkl) was trained with StandardScaler-normalized numeric features and 
LabelEncoder-encoded categorical features.

Since the original scaler wasn't saved with the model, we use approximate scaling 
parameters based on typical population data ranges for mental health surveys.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

# Feature names in the exact order expected by the model
FEATURE_NAMES = [
    'Age',
    'Gender',
    'Occupation',
    'Sleep Hours',
    'Physical Activity (hrs/week)',
    'Caffeine Intake (mg/day)',
    'Alcohol Consumption (drinks/week)',
    'Smoking',
    'Family History of Anxiety',
    'Stress Level (1-10)',
    'Heart Rate (bpm)',
    'Breathing Rate (breaths/min)',
    'Sweating Level (1-5)',
    'Dizziness',
    'Medication',
    'Therapy Sessions (per month)',
    'Recent Major Life Event',
    'Diet Quality (1-10)'
]

# Approximate StandardScaler parameters (mean, std) for each feature
# Based on typical population data distributions for mental health surveys
# Format: feature_name: (mean, std)
SCALER_PARAMS = {
    'Age': (35.0, 12.0),                           # Adult population: mean ~35, std ~12
    'Gender': (0.5, 0.5),                          # Binary/ternary encoded: ~uniform
    'Occupation': (1.5, 1.2),                      # Encoded 0-4: mean ~1.5
    'Sleep Hours': (7.0, 1.5),                     # Typical sleep: 7h ± 1.5h
    'Physical Activity (hrs/week)': (4.0, 3.0),   # Average activity: 4h/week
    'Caffeine Intake (mg/day)': (150.0, 100.0),   # 1-2 cups coffee avg
    'Alcohol Consumption (drinks/week)': (3.0, 4.0),  # Light-moderate drinking
    'Smoking': (0.3, 0.5),                         # Mostly non-smokers
    'Family History of Anxiety': (0.3, 0.45),     # ~30% have family history
    'Stress Level (1-10)': (5.0, 2.5),            # Mid-range stress
    'Heart Rate (bpm)': (72.0, 12.0),             # Normal resting HR
    'Breathing Rate (breaths/min)': (16.0, 3.0), # Normal breathing
    'Sweating Level (1-5)': (2.0, 1.0),           # Low-moderate sweating
    'Dizziness': (0.2, 0.4),                       # Mostly no dizziness
    'Medication': (0.2, 0.4),                      # Mostly no medication
    'Therapy Sessions (per month)': (0.5, 1.0),  # Most don't have regular therapy
    'Recent Major Life Event': (0.25, 0.43),      # ~25% have recent events
    'Diet Quality (1-10)': (6.0, 2.0)             # Slightly above average diet
}

# Class mapping for predictions
# Model outputs: 0 = Low, 1 = Medium, 2 = High (based on LabelEncoder alphabetical order)
CLASS_MAPPING = {
    0: {'name': 'High', 'level': 9, 'description': 'High Anxiety'},    # 'High' comes first alphabetically
    1: {'name': 'Low', 'level': 2, 'description': 'Low Anxiety'},      # 'Low' comes second
    2: {'name': 'Medium', 'level': 6, 'description': 'Medium Anxiety'} # 'Medium' comes third
}

# Gender encoding (matches LabelEncoder alphabetical order)
GENDER_ENCODING = {
    'female': 0,
    'male': 1,
    'other': 2,
    'not set': 2
}

# Occupation encoding (matches typical LabelEncoder order)
OCCUPATION_ENCODING = {
    'employed': 0,
    'other': 1,
    'retired': 2,
    'self employed': 3,
    'self-employed': 3,
    'student': 4,
    'unemployed': 5,
    'not set': 1
}


def scale_features(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply StandardScaler transformation to features.
    
    Uses approximate scaling parameters to match the training data preprocessing.
    Formula: z = (x - mean) / std
    
    Args:
        features_df: DataFrame with raw feature values
        
    Returns:
        DataFrame with scaled feature values
    """
    scaled_df = features_df.copy()
    
    for col in scaled_df.columns:
        if col in SCALER_PARAMS:
            mean, std = SCALER_PARAMS[col]
            if std > 0:
                scaled_df[col] = (scaled_df[col] - mean) / std
            else:
                scaled_df[col] = 0.0
    
    return scaled_df


def prepare_features_for_model(data: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Prepare and scale features for the anxiety prediction model.
    
    This function:
    1. Extracts raw values from input data
    2. Encodes categorical features (Gender, Occupation)
    3. Applies StandardScaler transformation
    
    Args:
        data: Dictionary containing user's mental health data
        
    Returns:
        DataFrame with scaled features ready for model prediction, or None if invalid
    """
    try:
        # Helper to get value with proper None handling (0 is valid)
        def get_value(key, default):
            val = data.get(key)
            return default if val is None else val
        
        # Extract and convert user inputs to model features
        
        # Demographics
        age = float(get_value('age', 35))
        
        # Encode Gender
        gender_str = str(data.get('gender', '')).lower().strip()
        gender = float(GENDER_ENCODING.get(gender_str, 2))
        
        # Encode Occupation
        occupation_str = str(data.get('occupation', '')).lower().replace('_', ' ').strip()
        occupation = float(OCCUPATION_ENCODING.get(occupation_str, 1))
        
        # Sleep and lifestyle (0 is valid for sleep_hours)
        sleep = float(get_value('sleep_hours', 7))
        
        # Physical activity: convert from categorical to hours/week if needed
        physical_raw = get_value('physical_activity', 3)
        if isinstance(physical_raw, str):
            activity_map = {'sedentary': 0, 'light': 2, 'moderate': 4, 'vigorous': 7}
            physical_activity = float(activity_map.get(physical_raw.lower(), 3))
        else:
            physical_activity = float(physical_raw if physical_raw is not None else 3)
        
        # Caffeine: convert cups to mg/day (1 cup ≈ 95mg)
        caffeine_raw = get_value('caffeine_intake', 2)
        caffeine_mg = float(caffeine_raw) * 95
        
        # Alcohol (0 is valid)
        alcohol = float(get_value('alcohol_intake', 0))
        
        # Smoking (0=never, 1=former, 2=current)
        smoking = float(get_value('smoking_habits', 0))
        
        # Family history (0 is valid)
        family_anxiety = float(get_value('family_anxiety_history', 0))
        
        # Current state metrics (0 is valid for some)
        stress = float(get_value('stress_level', 5))
        heart_rate = float(get_value('heart_rate', 72))
        breathing = float(get_value('breathing_rate', 16))
        sweating = float(get_value('sweating_level', 2))
        dizziness = float(get_value('dizziness_today', 0))
        
        # Medical (0 is valid)
        medication = float(get_value('medication_use', 0))
        
        # Therapy frequency: map to sessions/month
        therapy_freq = data.get('therapy_frequency', 'no')
        therapy_map = {'no': 0, 'rarely': 0.25, 'monthly': 1, 'bi_weekly': 2, 'weekly': 4}
        therapy_sessions = float(therapy_map.get(str(therapy_freq).lower() if therapy_freq else 'no', 0))
        
        # Life events
        recent_event_raw = data.get('recent_life_events')
        recent_life_event = 1.0 if recent_event_raw else 0.0
        
        # Diet quality
        diet_quality = float(get_value('diet_quality', 6))
        
        # Create DataFrame with exact feature names
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
        
        # Create DataFrame
        df = pd.DataFrame([feature_dict])
        
        # Ensure column order matches model's expected order
        df = df[FEATURE_NAMES]
        
        # Clean data: replace NaN/inf with neutral values
        df = df.fillna(0.0)
        df = df.replace([np.inf, -np.inf], 0.0)
        
        # Apply scaling
        scaled_df = scale_features(df)
        
        return scaled_df
        
    except (ValueError, TypeError, KeyError) as e:
        import logging
        logging.getLogger(__name__).error(f"Error preparing features: {e}")
        return None


def map_prediction_to_anxiety(predicted_class: int) -> Dict[str, Any]:
    """
    Map model prediction class to anxiety level and description.
    
    Args:
        predicted_class: Model output (0, 1, or 2)
        
    Returns:
        Dictionary with anxiety level, name, and description
    """
    return CLASS_MAPPING.get(predicted_class, CLASS_MAPPING[2])
