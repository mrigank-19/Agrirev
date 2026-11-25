"""Loads the trained suitability model and ranks crops by predicted viability."""

import pickle
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = ROOT / "model" / "suitability_model.pkl"
TRAINING_DATA_PATH = ROOT / "data" / "Crop_recommendation.csv"

with open(MODEL_PATH, "rb") as f:
    _bundle = pickle.load(f)

_model = _bundle["model"]
_features = _bundle["features"]

_training_df = pd.read_csv(TRAINING_DATA_PATH)
_crop_means = _training_df.groupby("label")[_features].mean()
_crop_stds = _training_df.groupby("label")[_features].std().replace(0, 1e-6)

FEATURE_LABELS = {
    "N": "nitrogen levels",
    "P": "phosphorus levels",
    "K": "potassium levels",
    "temperature": "temperature",
    "humidity": "humidity",
    "ph": "soil pH",
    "rainfall": "rainfall",
}


def get_viable_crops(soil_inputs: dict, top_n: int = 5) -> list[str]:
    """Return up to top_n crops ranked by predicted suitability for the given soil/climate inputs."""
    row = pd.DataFrame([[soil_inputs[f] for f in _features]], columns=_features)
    probabilities = _model.predict_proba(row)[0]
    ranked = sorted(zip(_model.classes_, probabilities), key=lambda pair: pair[1], reverse=True)
    return [crop for crop, _ in ranked[:top_n]]


def explain_viability(crop: str, soil_inputs: dict) -> str:
    """Return the soil/climate factor whose value is closest to this crop's typical range."""
    if crop not in _crop_means.index:
        return "your soil and climate inputs"

    best_feature, best_z = None, None
    for feature in _features:
        mean = _crop_means.loc[crop, feature]
        std = _crop_stds.loc[crop, feature]
        z = abs(soil_inputs[feature] - mean) / std
        if best_z is None or z < best_z:
            best_feature, best_z = feature, z

    return FEATURE_LABELS.get(best_feature, best_feature)
