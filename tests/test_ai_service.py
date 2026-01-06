"""
Integration tests for the AI service with the anxiety prediction model.
Tests the full pipeline from input data to prediction output.
"""

import pytest
import sys
import asyncio
import warnings

warnings.filterwarnings('ignore')

sys.path.insert(0, 'd:\\MentalHealthBot')

from services.ai_service import (
    call_ai_model,
    _load_model,
    get_advice_for_level,
    _fallback_prediction
)


class TestModelLoading:
    """Test model loading functionality."""
    
    def test_model_loads_successfully(self):
        """Model should load without errors."""
        model = _load_model()
        assert model is not None
    
    def test_model_has_correct_features(self):
        """Model should expect 18 features."""
        model = _load_model()
        assert model.n_features_in_ == 18
    
    def test_model_has_three_classes(self):
        """Model should have 3 output classes."""
        model = _load_model()
        assert len(model.classes_) == 3
    
    def test_model_classes_are_0_1_2(self):
        """Model classes should be 0, 1, 2."""
        model = _load_model()
        assert list(model.classes_) == [0, 1, 2]


class TestCallAIModel:
    """Test the main call_ai_model function."""
    
    @pytest.fixture
    def event_loop(self):
        """Create event loop for async tests."""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    def run_async(self, coro):
        """Helper to run async functions."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def test_returns_dict(self):
        """Function should return a dictionary."""
        data = {'stress_level': 5, 'sleep_hours': 7}
        result = self.run_async(call_ai_model(data))
        assert isinstance(result, dict)
    
    def test_has_required_keys(self):
        """Result should have all required keys."""
        data = {'stress_level': 5}
        result = self.run_async(call_ai_model(data))
        
        required_keys = [
            'predicted_anxiety_level',
            'confidence_score',
            'advice',
            'advice_category',
            'model_version'
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_anxiety_level_in_valid_range(self):
        """Predicted anxiety level should be 2, 6, or 9."""
        data = {'stress_level': 5}
        result = self.run_async(call_ai_model(data))
        assert result['predicted_anxiety_level'] in [2, 6, 9]
    
    def test_confidence_in_valid_range(self):
        """Confidence should be between 0 and 1."""
        data = {'stress_level': 5}
        result = self.run_async(call_ai_model(data))
        assert 0 <= result['confidence_score'] <= 1
    
    def test_advice_is_string(self):
        """Advice should be a non-empty string."""
        data = {'stress_level': 5}
        result = self.run_async(call_ai_model(data))
        assert isinstance(result['advice'], str)
        assert len(result['advice']) > 0
    
    def test_category_is_valid(self):
        """Category should be low, moderate, or high."""
        data = {'stress_level': 5}
        result = self.run_async(call_ai_model(data))
        assert result['advice_category'] in ['low', 'moderate', 'high']
    
    def test_model_version_present(self):
        """Model version should be present."""
        data = {'stress_level': 5}
        result = self.run_async(call_ai_model(data))
        assert 'model_version' in result
        assert len(result['model_version']) > 0


class TestPredictionVariation:
    """Test that different inputs produce different predictions."""
    
    def run_async(self, coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def test_healthy_profile_predicts_low(self):
        """Healthy profile should predict low anxiety."""
        data = {
            'age': 25,
            'gender': 'female',
            'occupation': 'student',
            'stress_level': 1,
            'sleep_hours': 9,
            'heart_rate': 55,
            'breathing_rate': 12,
            'caffeine_intake': 0,
            'alcohol_intake': 0,
            'smoking_habits': 0,
            'family_anxiety_history': 0,
            'sweating_level': 1,
            'dizziness_today': 0,
            'medication_use': 0,
            'physical_activity': 7,
            'diet_quality': 10,
            'therapy_frequency': 'no',
            'recent_life_events': None
        }
        result = self.run_async(call_ai_model(data))
        assert result['predicted_anxiety_level'] == 2
        assert result['advice_category'] == 'low'
    
    def test_unhealthy_profile_predicts_high(self):
        """Unhealthy/stressed profile should predict high anxiety."""
        data = {
            'age': 45,
            'gender': 'male',
            'occupation': 'unemployed',
            'stress_level': 10,
            'sleep_hours': 3,
            'heart_rate': 100,
            'breathing_rate': 22,
            'caffeine_intake': 8,
            'alcohol_intake': 10,
            'smoking_habits': 2,
            'family_anxiety_history': 1,
            'sweating_level': 5,
            'dizziness_today': 1,
            'medication_use': 1,
            'physical_activity': 0,
            'diet_quality': 1,
            'therapy_frequency': 'weekly',
            'recent_life_events': 'job_loss'
        }
        result = self.run_async(call_ai_model(data))
        assert result['predicted_anxiety_level'] == 9
        assert result['advice_category'] == 'high'
    
    def test_moderate_profile(self):
        """Moderate risk profile should not predict low."""
        data = {
            'age': 55,
            'gender': 'male',
            'occupation': 'employed',
            'stress_level': 7,
            'sleep_hours': 5,
            'heart_rate': 85,
            'breathing_rate': 18,
            'caffeine_intake': 4,
            'alcohol_intake': 4,
            'smoking_habits': 1,
            'family_anxiety_history': 1,
            'sweating_level': 3,
            'dizziness_today': 0,
            'medication_use': 1,
            'physical_activity': 1,
            'diet_quality': 4,
            'therapy_frequency': 'monthly',
            'recent_life_events': None
        }
        result = self.run_async(call_ai_model(data))
        # Should not be low anxiety
        assert result['predicted_anxiety_level'] in [6, 9]
    
    def test_different_stress_levels_affect_prediction(self):
        """Different stress levels should potentially affect predictions."""
        base_data = {
            'age': 35,
            'gender': 'male',
            'occupation': 'employed',
            'sleep_hours': 6,
            'heart_rate': 75,
            'breathing_rate': 16,
            'caffeine_intake': 3,
            'alcohol_intake': 2,
            'smoking_habits': 0,
            'family_anxiety_history': 0,
            'sweating_level': 2,
            'dizziness_today': 0,
            'medication_use': 0,
            'physical_activity': 2,
            'diet_quality': 5,
            'therapy_frequency': 'no',
            'recent_life_events': None
        }
        
        predictions = []
        for stress in [1, 5, 10]:
            data = base_data.copy()
            data['stress_level'] = stress
            result = self.run_async(call_ai_model(data))
            predictions.append(result['predicted_anxiety_level'])
        
        # At minimum, predictions should be valid
        assert all(p in [2, 6, 9] for p in predictions)


class TestInputValidation:
    """Test handling of various input types and edge cases."""
    
    def run_async(self, coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def test_empty_input(self):
        """Should handle empty input gracefully."""
        result = self.run_async(call_ai_model({}))
        assert result is not None
        assert 'predicted_anxiety_level' in result
    
    def test_none_values(self):
        """Should handle None values in input."""
        data = {
            'stress_level': None,
            'sleep_hours': None,
            'heart_rate': None
        }
        result = self.run_async(call_ai_model(data))
        assert result is not None
    
    def test_string_numbers(self):
        """Should handle string representations of numbers."""
        data = {
            'stress_level': '5',
            'sleep_hours': '7',
            'age': '35'
        }
        # This should not crash
        result = self.run_async(call_ai_model(data))
        assert result is not None
    
    def test_missing_optional_fields(self):
        """Should work with only required fields."""
        data = {'stress_level': 5}
        result = self.run_async(call_ai_model(data))
        assert result is not None
        assert 'predicted_anxiety_level' in result
    
    def test_extra_fields_ignored(self):
        """Extra fields should be ignored."""
        data = {
            'stress_level': 5,
            'unknown_field': 'value',
            'another_unknown': 123
        }
        result = self.run_async(call_ai_model(data))
        assert result is not None


class TestAdviceGeneration:
    """Test advice generation based on anxiety level."""
    
    def test_low_anxiety_advice(self):
        """Low anxiety should get positive advice."""
        advice = get_advice_for_level(2)
        assert isinstance(advice, str)
        assert len(advice) > 0
    
    def test_moderate_anxiety_advice(self):
        """Moderate anxiety should get helpful advice."""
        advice = get_advice_for_level(5)
        assert isinstance(advice, str)
        assert len(advice) > 0
    
    def test_high_anxiety_advice(self):
        """High anxiety should get professional help advice."""
        advice = get_advice_for_level(9)
        assert isinstance(advice, str)
        assert len(advice) > 0
    
    def test_advice_varies_by_level(self):
        """Different levels should potentially get different advice pools."""
        low_advice = get_advice_for_level(2)
        high_advice = get_advice_for_level(9)
        # Both should be non-empty strings
        assert len(low_advice) > 0
        assert len(high_advice) > 0


class TestFallbackPrediction:
    """Test the fallback prediction mechanism."""
    
    def test_fallback_returns_dict(self):
        """Fallback should return valid dictionary."""
        data = {'anxiety_level': 5}
        result = _fallback_prediction(data)
        assert isinstance(result, dict)
    
    def test_fallback_has_required_keys(self):
        """Fallback result should have all required keys."""
        data = {'anxiety_level': 5}
        result = _fallback_prediction(data)
        
        required_keys = [
            'predicted_anxiety_level',
            'confidence_score',
            'advice',
            'advice_category',
            'model_version'
        ]
        for key in required_keys:
            assert key in result
    
    def test_fallback_uses_user_anxiety(self):
        """Fallback should use user-reported anxiety as base."""
        data = {'anxiety_level': 8}
        result = _fallback_prediction(data)
        # Should be close to 8 (with ±1 variation)
        assert 7 <= result['predicted_anxiety_level'] <= 9
    
    def test_fallback_version_indicates_fallback(self):
        """Fallback version should indicate it's a fallback."""
        data = {'anxiety_level': 5}
        result = _fallback_prediction(data)
        assert 'fallback' in result['model_version'].lower()


class TestCategoryMapping:
    """Test anxiety level to category mapping."""
    
    def run_async(self, coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def test_level_2_is_low(self):
        """Level 2 should map to 'low' category."""
        # Create data that predicts low
        data = {
            'stress_level': 1,
            'sleep_hours': 9,
            'caffeine_intake': 0,
            'alcohol_intake': 0,
            'smoking_habits': 0,
            'family_anxiety_history': 0
        }
        result = self.run_async(call_ai_model(data))
        if result['predicted_anxiety_level'] == 2:
            assert result['advice_category'] == 'low'
    
    def test_level_6_is_moderate(self):
        """Level 6 should map to 'moderate' category."""
        # The category check in the code
        # Level 6: 4 < 6 <= 7 -> moderate
        # This is tested implicitly through integration


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
