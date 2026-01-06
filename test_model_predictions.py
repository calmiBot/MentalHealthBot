#!/usr/bin/env python3
"""
Manual test script for the anxiety prediction model.
Allows testing different input combinations to verify model behavior.
"""

import sys
import asyncio
sys.path.insert(0, 'd:\\MentalHealthBot')

from services.ai_service import call_ai_model
from services.ai_service import _prepare_features
import pandas as pd


def create_test_profile(name: str, **kwargs):
    """Create a test profile with default values."""
    defaults = {
        'user_id': 999,
        'age': 35,
        'gender': 'Male',
        'occupation': 'Employed',
        'stress_level': 5,
        'sleep_hours': 7,
        'heart_rate': 70,
        'breathing_rate': 16,
        'caffeine_intake': 2,
        'alcohol_intake': 1,
        'mood_rating': 5,
        'energy_level': 5,
        'sweating_level': 1,
        'dizziness_today': 0,
        'physical_activity': 3,
        'diet_quality': 5,
        'smoking_habits': 0,
        'family_anxiety_history': 0,
        'medication_use': 0,
        'therapy_frequency': 'monthly',
        'recent_life_events': None
    }
    
    # Override with provided kwargs
    defaults.update(kwargs)
    defaults['_profile_name'] = name
    return defaults


def print_profile(profile: dict):
    """Print a test profile in readable format."""
    name = profile.pop('_profile_name')
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    
    # Group by category
    categories = {
        'Demographics': ['age', 'gender', 'occupation'],
        'Sleep & Activity': ['sleep_hours', 'physical_activity', 'caffeine_intake', 'alcohol_intake'],
        'Current State': ['stress_level', 'heart_rate', 'breathing_rate', 'mood_rating', 'energy_level', 'sweating_level', 'dizziness_today'],
        'Health History': ['smoking_habits', 'family_anxiety_history', 'medication_use', 'therapy_frequency', 'diet_quality'],
        'Life Events': ['recent_life_events']
    }
    
    for category, keys in categories.items():
        print(f"\n{category}:")
        for key in keys:
            if key in profile:
                val = profile[key]
                if val is None:
                    val = "None"
                print(f"  {key}: {val}")


async def test_model_predictions():
    """Test the model with various input profiles."""
    
    test_cases = [
        # Baseline: Medium stress, normal lifestyle
        create_test_profile(
            "BASELINE: Moderate stress, normal lifestyle",
            stress_level=5,
            sleep_hours=7,
            caffeine_intake=2,
            alcohol_intake=1,
            mood_rating=5,
            physical_activity=3
        ),
        
        # Very stressed person
        create_test_profile(
            "HIGH STRESS: Maximum stress, poor sleep",
            stress_level=10,
            sleep_hours=4,
            caffeine_intake=5,
            alcohol_intake=5,
            mood_rating=2,
            heart_rate=90,
            breathing_rate=18,
            sweating_level=4,
            dizziness_today=1,
            recent_life_events="Work crisis"
        ),
        
        # Very relaxed person
        create_test_profile(
            "LOW STRESS: Minimal stress, healthy lifestyle",
            stress_level=1,
            sleep_hours=9,
            caffeine_intake=0,
            alcohol_intake=0,
            mood_rating=9,
            energy_level=9,
            heart_rate=60,
            breathing_rate=14,
            sweating_level=0,
            physical_activity=5,
            diet_quality=9
        ),
        
        # Poor lifestyle habits
        create_test_profile(
            "POOR LIFESTYLE: Bad diet, no exercise, heavy caffeine",
            stress_level=6,
            sleep_hours=5,
            caffeine_intake=6,
            alcohol_intake=7,
            physical_activity=0,
            diet_quality=2,
            smoking_habits=2,
            family_anxiety_history=1
        ),
        
        # Good lifestyle habits
        create_test_profile(
            "GOOD LIFESTYLE: Healthy diet, exercise, no stimulants",
            stress_level=4,
            sleep_hours=8,
            caffeine_intake=0,
            alcohol_intake=0,
            physical_activity=5,
            diet_quality=9,
            smoking_habits=0,
            family_anxiety_history=0,
            medication_use=0
        ),
        
        # Young, healthy person
        create_test_profile(
            "YOUNG & HEALTHY: 25 years old, no health issues",
            age=25,
            stress_level=3,
            sleep_hours=8,
            caffeine_intake=1,
            alcohol_intake=1,
            heart_rate=55,
            breathing_rate=13,
            mood_rating=8,
            physical_activity=5,
            family_anxiety_history=0
        ),
        
        # Older person with health concerns
        create_test_profile(
            "OLDER WITH ISSUES: 60 years old, multiple health concerns",
            age=60,
            stress_level=7,
            sleep_hours=6,
            caffeine_intake=3,
            alcohol_intake=3,
            heart_rate=85,
            breathing_rate=17,
            mood_rating=4,
            energy_level=3,
            sweating_level=2,
            smoking_habits=1,
            family_anxiety_history=1,
            medication_use=1,
            diet_quality=4
        ),
        
        # Extreme high stress case
        create_test_profile(
            "EXTREME STRESS: All negative indicators",
            age=40,
            stress_level=10,
            sleep_hours=3,
            heart_rate=100,
            breathing_rate=20,
            caffeine_intake=8,
            alcohol_intake=10,
            mood_rating=1,
            energy_level=1,
            sweating_level=5,
            dizziness_today=1,
            physical_activity=0,
            diet_quality=1,
            smoking_habits=2,
            family_anxiety_history=1,
            medication_use=1,
            therapy_frequency='weekly',
            recent_life_events="Major life crisis"
        ),
        
        # Extreme low stress case
        create_test_profile(
            "MINIMAL STRESS: All positive indicators",
            age=30,
            stress_level=1,
            sleep_hours=10,
            heart_rate=50,
            breathing_rate=12,
            caffeine_intake=0,
            alcohol_intake=0,
            mood_rating=10,
            energy_level=10,
            sweating_level=0,
            dizziness_today=0,
            physical_activity=7,
            diet_quality=10,
            smoking_habits=0,
            family_anxiety_history=0,
            medication_use=0,
            therapy_frequency='no'
        ),
    ]
    
    results = []
    
    for profile in test_cases:
        profile_copy = profile.copy()
        name = profile_copy.pop('_profile_name')
        
        print_profile(profile)
        
        try:
            # Test feature preparation
            df = _prepare_features(profile_copy)
            if df is None:
                print("\nERROR: Feature preparation failed")
                continue
            
            # Call the model
            result = await call_ai_model(profile_copy)
            
            if result:
                anxiety_level = result.get('predicted_anxiety_level')
                confidence = result.get('confidence_score', 0)
                advice = result.get('advice')
                category = result.get('advice_category')
                
                print(f"\nRESULT:")
                print(f"  Predicted Anxiety Level: {anxiety_level}/10")
                print(f"  Confidence: {confidence*100:.1f}%")
                print(f"  Category: {category}")
                print(f"  Advice: {advice[:80]}..." if len(advice) > 80 else f"  Advice: {advice}")
                
                results.append({
                    'Profile': name,
                    'Anxiety': anxiety_level,
                    'Confidence': f"{confidence*100:.1f}%"
                })
            else:
                print("\nERROR: Model returned None")
                
        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary table
    print(f"\n\n{'='*80}")
    print("SUMMARY TABLE")
    print(f"{'='*80}\n")
    
    if results:
        df_results = pd.DataFrame(results)
        print(df_results.to_string(index=False))
        
        # Analysis
        anxiety_levels = [r['Anxiety'] for r in results]
        unique_levels = set(anxiety_levels)
        
        print(f"\n\nANALYSIS:")
        print(f"  Total tests: {len(results)}")
        print(f"  Unique anxiety predictions: {len(unique_levels)}")
        print(f"  Predictions: {sorted(unique_levels)}")
        
        if len(unique_levels) == 1:
            print(f"\n  ⚠️  WARNING: All predictions are {anxiety_levels[0]}/10")
            print(f"      The model appears to be predicting the same value regardless of input.")
            print(f"      This could indicate:")
            print(f"      1. The model was trained with highly imbalanced data")
            print(f"      2. The features have low variance in the training data")
            print(f"      3. The ensemble is biased toward one class")
        else:
            print(f"\n  ✓ Model is producing varied predictions")
            for level in sorted(unique_levels):
                count = anxiety_levels.count(level)
                print(f"    - Level {level}/10: {count} test(s)")


def interactive_test():
    """Interactive mode: Let user input custom values."""
    print("\n" + "="*80)
    print("INTERACTIVE TEST MODE")
    print("="*80)
    print("\nEnter values for each parameter (or press Enter for default):")
    
    profile = {
        'user_id': 999,
        'age': 35,
        'gender': 'Male',
        'occupation': 'Employed',
        'stress_level': 5,
        'sleep_hours': 7,
        'heart_rate': 70,
        'breathing_rate': 16,
        'caffeine_intake': 2,
        'alcohol_intake': 1,
        'mood_rating': 5,
        'energy_level': 5,
        'sweating_level': 1,
        'dizziness_today': 0,
        'physical_activity': 3,
        'diet_quality': 5,
        'smoking_habits': 0,
        'family_anxiety_history': 0,
        'medication_use': 0,
        'therapy_frequency': 'monthly',
        'recent_life_events': None
    }
    
    numeric_fields = {
        'age': ('Age', 18, 100),
        'stress_level': ('Stress Level (1-10)', 1, 10),
        'sleep_hours': ('Sleep Hours', 0, 12),
        'heart_rate': ('Heart Rate (bpm)', 40, 150),
        'caffeine_intake': ('Caffeine (cups)', 0, 10),
        'alcohol_intake': ('Alcohol (drinks/week)', 0, 20),
        'mood_rating': ('Mood (1-10)', 1, 10),
        'energy_level': ('Energy (1-10)', 1, 10),
        'physical_activity': ('Physical Activity (hrs/week)', 0, 20),
        'diet_quality': ('Diet Quality (1-10)', 1, 10),
    }
    
    for field, (label, min_val, max_val) in numeric_fields.items():
        try:
            val = input(f"{label} (default {profile[field]}): ").strip()
            if val:
                profile[field] = float(val)
        except ValueError:
            print(f"  Invalid input, using default: {profile[field]}")
    
    print("\n" + "="*80)
    asyncio.run(test_single_profile(profile))


async def test_single_profile(profile):
    """Test a single profile."""
    print(f"\nTesting profile...")
    print(f"Stress Level: {profile['stress_level']}/10")
    print(f"Sleep Hours: {profile['sleep_hours']}")
    print(f"Heart Rate: {profile['heart_rate']} bpm")
    print(f"Caffeine: {profile['caffeine_intake']} cups")
    print(f"Alcohol: {profile['alcohol_intake']} drinks/week")
    print(f"Mood: {profile['mood_rating']}/10")
    print(f"Energy: {profile['energy_level']}/10")
    
    try:
        result = await call_ai_model(profile)
        if result:
            print(f"\n✓ RESULT:")
            print(f"  Anxiety Level: {result['predicted_anxiety_level']}/10")
            print(f"  Confidence: {result['confidence_score']*100:.1f}%")
            print(f"  Advice: {result['advice']}")
        else:
            print("\n✗ Model returned None")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the anxiety prediction model')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive mode')
    parser.add_argument('--stress', type=int, default=None,
                       help='Override stress level for quick test')
    parser.add_argument('--sleep', type=float, default=None,
                       help='Override sleep hours for quick test')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_test()
    elif args.stress is not None or args.sleep is not None:
        # Quick test with overrides
        profile = create_test_profile(
            "CUSTOM TEST",
            stress_level=args.stress or 5,
            sleep_hours=args.sleep or 7
        )
        profile.pop('_profile_name')
        asyncio.run(test_single_profile(profile))
    else:
        # Run all predefined tests
        print("\n" + "="*80)
        print("RUNNING ALL TEST CASES")
        print("="*80)
        print("\nThis will test the model with various input combinations to verify")
        print("that different inputs produce different anxiety predictions.\n")
        asyncio.run(test_model_predictions())
