"""Quick sanity check: load the saved model and run one sample prediction."""

import pickle
from pathlib import Path

import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "suitability_model.pkl"

# Typical rice-growing conditions (N, P, K, temperature, humidity, ph, rainfall)
SAMPLE = [90, 42, 43, 20.9, 82.0, 6.5, 202.9]


def main():
    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)

    model = bundle["model"]
    features = bundle["features"]

    sample_df = pd.DataFrame([SAMPLE], columns=features)
    prediction = model.predict(sample_df)[0]
    print(f"Input ({', '.join(features)}): {SAMPLE}")
    print(f"Predicted crop: {prediction}")


if __name__ == "__main__":
    main()
