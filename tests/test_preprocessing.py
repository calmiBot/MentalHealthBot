"""
Unit tests for the preprocessing module.
Tests feature scaling, encoding, and data preparation.
"""

import pytest
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, 'd:\\MentalHealthBot')

from model.preprocessing import (
    prepare_features_for_model,
    scale_features,
    map_prediction_to_anxiety,
    FEATURE_NAMES,
    SCALER_PARAMS,
    CLASS_MAPPING,
    GENDER_ENCODING,
    OCCUPATION_ENCODING
)


class TestFeatureNames:
    """Test that feature names are correctly defined."""
    
    def test_feature_names_count(self):
        """Model expects exactly 18 features."""
        assert len(FEATURE_NAMES) == 18
    
    def test_required_features_present(self):
        """All required features should be in the list."""
        required = [
            'Age', 'Gender', 'Occupation', 'Sleep Hours',
            'Stress Level (1-10)', 'Heart Rate (bpm)',
            'Caffeine Intake (mg/day)', 'Diet Quality (1-10)'
        ]
        for feature in required:
            assert feature in FEATURE_NAMES, f"Missing required feature: {feature}"


class TestScalerParams:
    """Test scaler parameters are correctly defined."""
    
    def test_all_features_have_params(self):
        """Every feature should have scaling parameters."""
        for feature in FEATURE_NAMES:
            assert feature in SCALER_PARAMS, f"Missing scaler params for: {feature}"
    
    def test_params_are_tuples(self):
        """Each param should be a (mean, std) tuple."""
        for feature, params in SCALER_PARAMS.items():
            assert isinstance(params, tuple), f"{feature} params should be tuple"
            assert len(params) == 2, f"{feature} should have (mean, std)"
    
    def test_std_is_positive(self):
        """Standard deviation should be positive."""
        for feature, (mean, std) in SCALER_PARAMS.items():
            assert std > 0, f"{feature} std should be positive"


class TestGenderEncoding:
    """Test gender encoding mappings."""
    
    def test_male_encoding(self):
        assert GENDER_ENCODING['male'] == 1
    
    def test_female_encoding(self):
        assert GENDER_ENCODING['female'] == 0
    
    def test_other_encoding(self):
        assert GENDER_ENCODING['other'] == 2
    
    def test_not_set_encoding(self):
        assert GENDER_ENCODING['not set'] == 2


class TestOccupationEncoding:
    """Test occupation encoding mappings."""
    
    def test_employed_encoding(self):
        assert OCCUPATION_ENCODING['employed'] == 0
    
    def test_student_encoding(self):
        assert OCCUPATION_ENCODING['student'] == 4
    
    def test_unemployed_encoding(self):
        assert OCCUPATION_ENCODING['unemployed'] == 5


class TestClassMapping:
    """Test class prediction mappings."""
    
    def test_class_0_is_high(self):
        """Class 0 should map to High anxiety (alphabetical order)."""
        assert CLASS_MAPPING[0]['name'] == 'High'
        assert CLASS_MAPPING[0]['level'] == 9
    
    def test_class_1_is_low(self):
        """Class 1 should map to Low anxiety."""
        assert CLASS_MAPPING[1]['name'] == 'Low'
        assert CLASS_MAPPING[1]['level'] == 2
    
    def test_class_2_is_medium(self):
        """Class 2 should map to Medium anxiety."""
        assert CLASS_MAPPING[2]['name'] == 'Medium'
        assert CLASS_MAPPING[2]['level'] == 6


class TestScaleFeatures:
    """Test the scale_features function."""
    
    def test_scaling_formula(self):
        """Test that scaling applies (x - mean) / std correctly."""
        # Create a simple dataframe with known values
        df = pd.DataFrame({
            'Age': [35.0],  # mean=35, std=12 -> should become 0
            'Stress Level (1-10)': [5.0],  # mean=5, std=2.5 -> should become 0
        })
        
        scaled = scale_features(df)
        
        # Values at the mean should scale to 0
        assert abs(scaled['Age'].values[0]) < 0.01
        assert abs(scaled['Stress Level (1-10)'].values[0]) < 0.01
    
    def test_scaling_above_mean(self):
        """Values above mean should scale to positive."""
        df = pd.DataFrame({
            'Age': [47.0],  # 35 + 12 = 47 -> should become +1
        })
        
        scaled = scale_features(df)
        assert abs(scaled['Age'].values[0] - 1.0) < 0.01
    
    def test_scaling_below_mean(self):
        """Values below mean should scale to negative."""
        df = pd.DataFrame({
            'Age': [23.0],  # 35 - 12 = 23 -> should become -1
        })
        
        scaled = scale_features(df)
        assert abs(scaled['Age'].values[0] - (-1.0)) < 0.01


class TestPrepareFeatures:
    """Test the prepare_features_for_model function."""
    
    def test_returns_dataframe(self):
        """Function should return a pandas DataFrame."""
        data = {'stress_level': 5, 'sleep_hours': 7}
        result = prepare_features_for_model(data)
        assert isinstance(result, pd.DataFrame)
    
    def test_correct_number_of_columns(self):
        """Output should have exactly 18 columns."""
        data = {'stress_level': 5}
        result = prepare_features_for_model(data)
        assert result.shape[1] == 18
    
    def test_correct_column_order(self):
        """Columns should be in the expected order."""
        data = {'stress_level': 5}
        result = prepare_features_for_model(data)
        assert list(result.columns) == FEATURE_NAMES
    
    def test_single_row_output(self):
        """Output should have exactly 1 row."""
        data = {'stress_level': 5}
        result = prepare_features_for_model(data)
        assert result.shape[0] == 1
    
    def test_no_nan_values(self):
        """Output should not contain NaN values."""
        data = {'stress_level': 5}
        result = prepare_features_for_model(data)
        assert result.isnull().sum().sum() == 0
    
    def test_no_inf_values(self):
        """Output should not contain infinite values."""
        data = {'stress_level': 5}
        result = prepare_features_for_model(data)
        assert not np.isinf(result.values).any()
    
    def test_gender_encoding_male(self):
        """Male gender should be encoded correctly."""
        data = {'gender': 'male', 'stress_level': 5}
        result = prepare_features_for_model(data)
        # After scaling: (1 - 0.5) / 0.5 = 1.0
        assert result['Gender'].values[0] == 1.0
    
    def test_gender_encoding_female(self):
        """Female gender should be encoded correctly."""
        data = {'gender': 'female', 'stress_level': 5}
        result = prepare_features_for_model(data)
        # After scaling: (0 - 0.5) / 0.5 = -1.0
        assert result['Gender'].values[0] == -1.0
    
    def test_caffeine_conversion(self):
        """Caffeine should be converted from cups to mg."""
        data = {'caffeine_intake': 2, 'stress_level': 5}  # 2 cups = 190mg
        result = prepare_features_for_model(data)
        # Raw: 190mg, scaled: (190 - 150) / 100 = 0.4
        expected = (2 * 95 - 150) / 100
        assert abs(result['Caffeine Intake (mg/day)'].values[0] - expected) < 0.01
    
    def test_therapy_frequency_mapping(self):
        """Therapy frequency strings should map to sessions/month."""
        test_cases = [
            ('no', 0),
            ('weekly', 4),
            ('monthly', 1),
            ('bi_weekly', 2),
        ]
        for freq, expected_sessions in test_cases:
            data = {'therapy_frequency': freq, 'stress_level': 5}
            result = prepare_features_for_model(data)
            # Check raw value before scaling
            raw_sessions = expected_sessions
            scaled = (raw_sessions - 0.5) / 1.0
            assert abs(result['Therapy Sessions (per month)'].values[0] - scaled) < 0.01
    
    def test_handles_none_values(self):
        """Function should handle None values gracefully."""
        data = {
            'stress_level': None,
            'sleep_hours': None,
            'heart_rate': None
        }
        result = prepare_features_for_model(data)
        assert result is not None
        assert result.isnull().sum().sum() == 0
    
    def test_handles_empty_dict(self):
        """Function should handle empty input dict."""
        result = prepare_features_for_model({})
        assert result is not None
        assert result.shape == (1, 18)


class TestMapPrediction:
    """Test the map_prediction_to_anxiety function."""
    
    def test_class_0_mapping(self):
        result = map_prediction_to_anxiety(0)
        assert result['name'] == 'High'
        assert result['level'] == 9
    
    def test_class_1_mapping(self):
        result = map_prediction_to_anxiety(1)
        assert result['name'] == 'Low'
        assert result['level'] == 2
    
    def test_class_2_mapping(self):
        result = map_prediction_to_anxiety(2)
        assert result['name'] == 'Medium'
        assert result['level'] == 6
    
    def test_invalid_class_fallback(self):
        """Invalid class should fall back to Medium."""
        result = map_prediction_to_anxiety(99)
        assert result['name'] == 'Medium'


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_extreme_stress_high(self):
        """Extreme high stress should scale correctly."""
        data = {'stress_level': 10}
        result = prepare_features_for_model(data)
        # (10 - 5) / 2.5 = 2.0
        assert abs(result['Stress Level (1-10)'].values[0] - 2.0) < 0.01
    
    def test_extreme_stress_low(self):
        """Extreme low stress should scale correctly."""
        data = {'stress_level': 1}
        result = prepare_features_for_model(data)
        # (1 - 5) / 2.5 = -1.6
        assert abs(result['Stress Level (1-10)'].values[0] - (-1.6)) < 0.01
    
    def test_very_old_age(self):
        """Very old age should scale correctly."""
        data = {'age': 80}
        result = prepare_features_for_model(data)
        # (80 - 35) / 12 = 3.75
        assert abs(result['Age'].values[0] - 3.75) < 0.01
    
    def test_very_young_age(self):
        """Very young age should scale correctly."""
        data = {'age': 18}
        result = prepare_features_for_model(data)
        # (18 - 35) / 12 = -1.417
        assert abs(result['Age'].values[0] - (-1.417)) < 0.01
    
    def test_zero_sleep(self):
        """Zero sleep hours should scale correctly."""
        data = {'sleep_hours': 0}
        result = prepare_features_for_model(data)
        # (0 - 7) / 1.5 = -4.67
        assert abs(result['Sleep Hours'].values[0] - (-4.67)) < 0.01
    
    def test_high_caffeine(self):
        """High caffeine intake should scale correctly."""
        data = {'caffeine_intake': 10}  # 10 cups = 950mg
        result = prepare_features_for_model(data)
        # (950 - 150) / 100 = 8.0
        assert abs(result['Caffeine Intake (mg/day)'].values[0] - 8.0) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
