#!/usr/bin/env python3
"""
Test script for the anxiety prediction model WITH proper preprocessing.
This script tests the model using the preprocessing module that applies
StandardScaler transformation to match the training data.
"""

import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.insert(0, 'd:\\MentalHealthBot')

import joblib
import numpy as np
from model.preprocessing import (
    prepare_features_for_model,
    scale_features,
    map_prediction_to_anxiety,
    SCALER_PARAMS,
    FEATURE_NAMES
)


def safe_transform(model, X):
    """Transform with improved NaN handling"""
    try:
        X_array = np.asarray(X)
        X_array = np.nan_to_num(X_array, nan=0.0, posinf=1.0, neginf=-1.0)
        result = model._transform_original(X_array)
        result = np.asarray(result)
        result = np.nan_to_num(result, nan=0.0, posinf=1.0, neginf=-1.0)
        return result
    except Exception as e:
        print(f"Warning: Transform error: {e}")
        return np.zeros((X.shape[0], model.n_classes_))


def load_model():
    """Load the model and patch it for NaN handling."""
    model = joblib.load('d:\\MentalHealthBot\\model\\enn.pkl')
    model._transform_original = model.transform
    model.transform = lambda X: safe_transform(model, X)
    return model


def test_with_preprocessing():
    """Test model with proper preprocessing (scaling)."""
    print("="*80)
    print("TESTING MODEL WITH PROPER PREPROCESSING")
    print("="*80)
    print("\nLoading model...")
    model = load_model()
    print(f"Model type: {type(model).__name__}")
    print(f"Classes: {model.classes_}")
    
    # Class names: LabelEncoder alphabetical order
    class_names = {0: "High", 1: "Low", 2: "Medium"}
    
    print("\n" + "-"*80)
    print("TEST 1: Different Stress Levels (with scaling)")
    print("-"*80)
    
    stress_levels = [1, 3, 5, 7, 10]
    
    for stress in stress_levels:
        # Create input data as it comes from the bot
        data = {
            'age': 35,
            'gender': 'male',
            'occupation': 'employed',
            'sleep_hours': 7,
            'physical_activity': 3,
            'caffeine_intake': 2,  # cups
            'alcohol_intake': 2,
            'smoking_habits': 0,
            'family_anxiety_history': 0,
            'stress_level': stress,
            'heart_rate': 75,
            'breathing_rate': 16,
            'sweating_level': 2,
            'dizziness_today': 0,
            'medication_use': 0,
            'therapy_frequency': 'monthly',
            'recent_life_events': None,
            'diet_quality': 6
        }
        
        # Use preprocessing module
        scaled_df = prepare_features_for_model(data)
        
        try:
            pred = model.predict(scaled_df)[0]
            proba = model.predict_proba(scaled_df)[0]
            
            mapping = map_prediction_to_anxiety(pred)
            anxiety = mapping['level']
            class_name = mapping['name']
            confidence = proba[pred] * 100
            
            print(f"Stress {stress:2d}/10 → Anxiety {anxiety}/10 ({class_name}, confidence {confidence:.1f}%)")
            
        except Exception as e:
            print(f"Stress {stress:2d}/10 → ERROR: {e}")
    
    print("\n" + "-"*80)
    print("TEST 2: Extreme Cases")
    print("-"*80)
    
    # Very healthy person
    healthy = {
        'age': 25,
        'gender': 'female',
        'occupation': 'student',
        'sleep_hours': 9,
        'physical_activity': 7,
        'caffeine_intake': 0,
        'alcohol_intake': 0,
        'smoking_habits': 0,
        'family_anxiety_history': 0,
        'stress_level': 1,
        'heart_rate': 55,
        'breathing_rate': 12,
        'sweating_level': 1,
        'dizziness_today': 0,
        'medication_use': 0,
        'therapy_frequency': 'no',
        'recent_life_events': None,
        'diet_quality': 10
    }
    
    scaled_df = prepare_features_for_model(healthy)
    pred = model.predict(scaled_df)[0]
    proba = model.predict_proba(scaled_df)[0]
    mapping = map_prediction_to_anxiety(pred)
    print(f"\nHEALTHY PERSON:")
    print(f"  Predicted: {mapping['name']} (Level {mapping['level']}/10)")
    print(f"  Confidence: {proba[pred]*100:.1f}%")
    print(f"  Probabilities: High={proba[0]:.3f}, Low={proba[1]:.3f}, Medium={proba[2]:.3f}")
    
    # Very unhealthy/anxious person
    unhealthy = {
        'age': 45,
        'gender': 'male',
        'occupation': 'unemployed',
        'sleep_hours': 3,
        'physical_activity': 0,
        'caffeine_intake': 8,
        'alcohol_intake': 10,
        'smoking_habits': 2,
        'family_anxiety_history': 1,
        'stress_level': 10,
        'heart_rate': 100,
        'breathing_rate': 22,
        'sweating_level': 5,
        'dizziness_today': 1,
        'medication_use': 1,
        'therapy_frequency': 'weekly',
        'recent_life_events': 'job_loss',
        'diet_quality': 2
    }
    
    scaled_df = prepare_features_for_model(unhealthy)
    pred = model.predict(scaled_df)[0]
    proba = model.predict_proba(scaled_df)[0]
    mapping = map_prediction_to_anxiety(pred)
    print(f"\nUNHEALTHY/ANXIOUS PERSON:")
    print(f"  Predicted: {mapping['name']} (Level {mapping['level']}/10)")
    print(f"  Confidence: {proba[pred]*100:.1f}%")
    print(f"  Probabilities: High={proba[0]:.3f}, Low={proba[1]:.3f}, Medium={proba[2]:.3f}")
    
    print("\n" + "-"*80)
    print("TEST 3: Verify Scaling is Working")
    print("-"*80)
    
    # Show what the scaled values look like
    sample_data = {
        'age': 35,
        'gender': 'male',
        'occupation': 'employed',
        'sleep_hours': 7,
        'physical_activity': 3,
        'caffeine_intake': 2,
        'alcohol_intake': 2,
        'smoking_habits': 0,
        'family_anxiety_history': 0,
        'stress_level': 5,
        'heart_rate': 72,
        'breathing_rate': 16,
        'sweating_level': 2,
        'dizziness_today': 0,
        'medication_use': 0,
        'therapy_frequency': 'no',
        'recent_life_events': None,
        'diet_quality': 6
    }
    
    scaled_df = prepare_features_for_model(sample_data)
    print("\nScaled feature values (should be near 0 for average person):")
    for col in scaled_df.columns:
        val = scaled_df[col].values[0]
        print(f"  {col}: {val:+.3f}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_with_preprocessing()
