"""
Model package for the Mental Health Bot.

Contains the trained anxiety prediction model and preprocessing utilities.
"""

from .preprocessing import (
    prepare_features_for_model,
    scale_features,
    map_prediction_to_anxiety,
    FEATURE_NAMES,
    SCALER_PARAMS,
    CLASS_MAPPING,
    GENDER_ENCODING,
    OCCUPATION_ENCODING
)

__all__ = [
    'prepare_features_for_model',
    'scale_features',
    'map_prediction_to_anxiety',
    'FEATURE_NAMES',
    'SCALER_PARAMS',
    'CLASS_MAPPING',
    'GENDER_ENCODING',
    'OCCUPATION_ENCODING'
]
