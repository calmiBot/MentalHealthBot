#!/usr/bin/env python3

import warnings
warnings.filterwarnings('ignore')

import joblib
import pandas as pd
import numpy as np
from numpy import nan_to_num


def safe_transform(model, X):
    """Transform with improved NaN handling"""
    try:
        # Clean input first
        X_clean = X.copy()
        if isinstance(X_clean, pd.DataFrame):
            X_clean = X_clean.fillna(0)
        
        X_array = np.asarray(X_clean)
        X_array = np.nan_to_num(X_array, nan=0.0, posinf=1.0, neginf=-1.0)
        
        # Restore DataFrame if needed
        if isinstance(X_clean, pd.DataFrame):
            X_clean = pd.DataFrame(X_array, columns=X.columns)
        else:
            X_clean = X_array
        
        # Call original transform
        result = model._transform_original(X_clean)
        
        # Clean output
        result = np.asarray(result)
        result = np.nan_to_num(result, nan=0.0, posinf=1.0, neginf=-1.0)
        
        return result
    except Exception as e:
        print(f"Warning: Transform error: {e}")
        return np.zeros((X.shape[0], model.n_classes_))


def load_model():
    """Load the model and patch it for NaN handling."""
    print("Loading model from: d:\\MentalHealthBot\\model\\enn.pkl")
    model = joblib.load('d:\\MentalHealthBot\\model\\enn.pkl')
    
    # Patch the transform method
    model._transform_original = model.transform
    model.transform = lambda X: safe_transform(model, X)
    
    print("Model loaded successfully!")
    print(f"Model type: {type(model).__name__}")
    print(f"Number of features: {model.n_features_in_}")
    print(f"Classes: {model.classes_}")
    print(f"Feature names: {list(model.feature_names_in_)}\n")
    
    return model


def test_with_different_stress():
    """Test model with different stress levels using exact feature names."""
    model = load_model()
    
    print("="*80)
    print("TEST 1: Different Stress Levels")
    print("="*80)
    print("Testing with stress levels: 1, 3, 5, 7, 10\n")
    
    stress_levels = [1, 3, 5, 7, 10]
    class_names = {0: "Low", 1: "Medium", 2: "High"}
    
    for stress in stress_levels:
        # Create data with EXACT feature names the model expects
        data = {
            'Age': 35.0,
            'Gender': 1.0,  # Male
            'Occupation': 1.0,  # Employed
            'Sleep Hours': 7.0,
            'Physical Activity (hrs/week)': 3.0,
            'Caffeine Intake (mg/day)': 190.0,
            'Alcohol Consumption (drinks/week)': 2.0,
            'Smoking': 0.0,
            'Family History of Anxiety': 1.0,
            'Stress Level (1-10)': float(stress),
            'Heart Rate (bpm)': 75.0,
            'Breathing Rate (breaths/min)': 16.0,
            'Sweating Level (1-5)': 2.0,
            'Dizziness': 0.0,
            'Medication': 0.0,
            'Therapy Sessions (per month)': 1.0,
            'Recent Major Life Event': 0.0,
            'Diet Quality (1-10)': 6.0
        }
        
        df = pd.DataFrame([data])
        
        try:
            pred = model.predict(df)[0]
            proba = model.predict_proba(df)[0]
            
            # Map class to anxiety level
            class_to_level = {0: 2, 1: 6, 2: 9}
            anxiety = class_to_level[pred]
            confidence = proba[pred] * 100
            class_name = class_names[pred]
            
            print(f"Stress {stress:2d}/10 → Anxiety {anxiety}/10 ({class_name}, confidence {confidence:.1f}%)")
            
        except Exception as e:
            print(f"Stress {stress:2d}/10 → ERROR: {e}")
    
    print()


def test_with_different_sleep():
    """Test model with different sleep hours."""
    model = load_model()
    
    print("="*80)
    print("TEST 2: Different Sleep Hours")
    print("="*80)
    print("Testing with sleep hours: 3, 5, 7, 9, 11\n")
    
    sleep_hours = [3, 5, 7, 9, 11]
    class_names = {0: "Low", 1: "Medium", 2: "High"}
    
    for sleep in sleep_hours:
        data = {
            'Age': 35.0,
            'Gender': 1.0,
            'Occupation': 1.0,
            'Sleep Hours': float(sleep),
            'Physical Activity (hrs/week)': 3.0,
            'Caffeine Intake (mg/day)': 190.0,
            'Alcohol Consumption (drinks/week)': 2.0,
            'Smoking': 0.0,
            'Family History of Anxiety': 1.0,
            'Stress Level (1-10)': 5.0,
            'Heart Rate (bpm)': 75.0,
            'Breathing Rate (breaths/min)': 16.0,
            'Sweating Level (1-5)': 2.0,
            'Dizziness': 0.0,
            'Medication': 0.0,
            'Therapy Sessions (per month)': 1.0,
            'Recent Major Life Event': 0.0,
            'Diet Quality (1-10)': 6.0
        }
        
        df = pd.DataFrame([data])
        
        try:
            pred = model.predict(df)[0]
            proba = model.predict_proba(df)[0]
            
            class_to_level = {0: 2, 1: 6, 2: 9}
            anxiety = class_to_level[pred]
            confidence = proba[pred] * 100
            class_name = class_names[pred]
            
            print(f"Sleep {sleep:2d}h → Anxiety {anxiety}/10 ({class_name}, confidence {confidence:.1f}%)")
            
        except Exception as e:
            print(f"Sleep {sleep:2d}h → ERROR: {e}")
    
    print()


def test_extreme_cases():
    """Test extreme cases: very healthy vs very unhealthy."""
    model = load_model()
    
    print("="*80)
    print("TEST 3: Extreme Cases")
    print("="*80)
    print()
    
    class_names = {0: "Low", 1: "Medium", 2: "High"}
    
    # Very healthy person
    healthy = {
        'Age': 25.0,
        'Gender': 1.0,
        'Occupation': 1.0,
        'Sleep Hours': 9.0,
        'Physical Activity (hrs/week)': 7.0,
        'Caffeine Intake (mg/day)': 0.0,
        'Alcohol Consumption (drinks/week)': 0.0,
        'Smoking': 0.0,
        'Family History of Anxiety': 0.0,
        'Stress Level (1-10)': 1.0,
        'Heart Rate (bpm)': 55.0,
        'Breathing Rate (breaths/min)': 13.0,
        'Sweating Level (1-5)': 0.0,
        'Dizziness': 0.0,
        'Medication': 0.0,
        'Therapy Sessions (per month)': 0.0,
        'Recent Major Life Event': 0.0,
        'Diet Quality (1-10)': 10.0
    }
    
    # Very unhealthy person
    unhealthy = {
        'Age': 55.0,
        'Gender': 0.0,
        'Occupation': 2.0,
        'Sleep Hours': 4.0,
        'Physical Activity (hrs/week)': 0.0,
        'Caffeine Intake (mg/day)': 800.0,
        'Alcohol Consumption (drinks/week)': 14.0,
        'Smoking': 2.0,
        'Family History of Anxiety': 1.0,
        'Stress Level (1-10)': 10.0,
        'Heart Rate (bpm)': 100.0,
        'Breathing Rate (breaths/min)': 20.0,
        'Sweating Level (1-5)': 5.0,
        'Dizziness': 1.0,
        'Medication': 1.0,
        'Therapy Sessions (per month)': 4.0,
        'Recent Major Life Event': 1.0,
        'Diet Quality (1-10)': 1.0
    }
    
    class_to_level = {0: 2, 1: 6, 2: 9}
    
    for name, data in [("HEALTHY PERSON", healthy), ("UNHEALTHY PERSON", unhealthy)]:
        df = pd.DataFrame([data])
        
        try:
            pred = model.predict(df)[0]
            proba = model.predict_proba(df)[0]
            anxiety = class_to_level[pred]
            confidence = proba[pred] * 100
            class_name = class_names[pred]
            
            print(f"{name}:")
            print(f"  Predicted Anxiety: {anxiety}/10 ({class_name})")
            print(f"  Confidence: {confidence:.1f}%")
            print(f"  Probabilities: Low={proba[0]:.3f}, Medium={proba[1]:.3f}, High={proba[2]:.3f}")
            print()
            
        except Exception as e:
            print(f"{name}: ERROR: {e}\n")


def test_random_variations():
    """Test with random but valid variations."""
    model = load_model()
    
    print("="*80)
    print("TEST 4: Random Variations (10 random profiles)")
    print("="*80)
    print()
    
    np.random.seed(42)
    class_to_level = {0: 2, 1: 6, 2: 9}
    class_names = {0: "Low", 1: "Medium", 2: "High"}
    
    results = []
    
    for i in range(10):
        data = {
            'Age': np.random.uniform(20, 70),
            'Gender': np.random.choice([0.0, 1.0, 2.0]),
            'Occupation': np.random.choice([0.0, 1.0, 2.0, 3.0]),
            'Sleep Hours': np.random.uniform(3, 10),
            'Physical Activity (hrs/week)': np.random.uniform(0, 10),
            'Caffeine Intake (mg/day)': np.random.uniform(0, 500),
            'Alcohol Consumption (drinks/week)': np.random.uniform(0, 15),
            'Smoking': np.random.choice([0.0, 1.0, 2.0]),
            'Family History of Anxiety': np.random.choice([0.0, 1.0]),
            'Stress Level (1-10)': np.random.uniform(1, 10),
            'Heart Rate (bpm)': np.random.uniform(50, 110),
            'Breathing Rate (breaths/min)': np.random.uniform(12, 25),
            'Sweating Level (1-5)': np.random.uniform(0, 5),
            'Dizziness': np.random.choice([0.0, 1.0]),
            'Medication': np.random.choice([0.0, 1.0]),
            'Therapy Sessions (per month)': np.random.choice([0.0, 0.25, 1.0, 2.0, 4.0]),
            'Recent Major Life Event': np.random.choice([0.0, 1.0]),
            'Diet Quality (1-10)': np.random.uniform(1, 10)
        }
        
        df = pd.DataFrame([data])
        
        try:
            pred = model.predict(df)[0]
            proba = model.predict_proba(df)[0]
            anxiety = class_to_level[pred]
            confidence = proba[pred]
            class_name = class_names[pred]
            
            stress = data['Stress Level (1-10)']
            sleep = data['Sleep Hours']
            
            results.append(anxiety)
            
            print(f"Profile {i+1:2d}: Stress={stress:5.1f}, Sleep={sleep:4.1f} → Anxiety {anxiety}/10 ({class_name}, {confidence*100:5.1f}%)")
            
        except Exception as e:
            print(f"Profile {i+1:2d}: ERROR: {e}")
    
    print()
    if results:
        unique = set(results)
        print(f"Summary: {len(results)} profiles tested")
        print(f"Unique anxiety predictions: {sorted(unique)}")
        print(f"Prediction distribution: {[(l, results.count(l)) for l in sorted(unique)]}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("DIRECT MODEL TEST - Testing enn.pkl without ai_service.py")
    print("="*80)
    print()
    
    try:
        test_with_different_stress()
        test_with_different_sleep()
        test_extreme_cases()
        test_random_variations()
        
        print("="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("\nIf all tests above show ONLY one anxiety level (e.g., all return 6/10),")
        print("then the problem is with the MODEL itself (training/learned behavior).")
        print("\nIf tests show DIFFERENT anxiety levels based on inputs,")
        print("then the problem might be with feature preparation in ai_service.py")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
