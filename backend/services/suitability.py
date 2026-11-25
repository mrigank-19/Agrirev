"""Loads the trained suitability model and ranks crops by predicted viability."""

import pickle
from pathlib import Path

import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "model" / "suitability_model.pkl"

with open(MODEL_PATH, "rb") as f:
    _bundle = pickle.load(f)

_model = _bundle["model"]
_features = _bundle["features"]


def get_viable_crops(soil_inputs: dict, top_n: int = 5) -> list[str]:
    """Return up to top_n crops ranked by predicted suitability for the given soil/climate inputs."""
    row = pd.DataFrame([[soil_inputs[f] for f in _features]], columns=_features)
    probabilities = _model.predict_proba(row)[0]
    ranked = sorted(zip(_model.classes_, probabilities), key=lambda pair: pair[1], reverse=True)
    return [crop for crop, _ in ranked[:top_n]]
