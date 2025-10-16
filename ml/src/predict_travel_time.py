"""
Travel time prediction utilities using a trained Random Forest model.

- Loads a persisted estimator from `models/travel_time_rf_model.pkl` by default.
- Provides single and batch prediction helpers with validation.
- Compatible with Python 3.10+ and scikit-learn 1.7+.

Usage example:
    from predict_travel_time import predict_travel_time
    minutes = predict_travel_time({
        "distance_km": 120.0,
        "traffic_delay_min": 15.0,
        "weather_delay_min": 5.0,
        "risk_factor": 0.2,
    })
    print(minutes)
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Sequence

import logging

import joblib
import pandas as pd

# Expected feature columns in the model training order
FEATURE_COLUMNS: Sequence[str] = (
    "distance_km",
    "traffic_delay_min",
    "weather_delay_min",
    "risk_factor",
)

# Default relative path to the trained model (relative to repository root)
DEFAULT_MODEL_PATH = Path("ml/models/travel_time_rf_model.pkl")


def _coerce_numeric(value: Any, key: str) -> float:
    """Try converting a value to float with a helpful error if it fails."""
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Feature '{key}' must be numeric, got {value!r}") from exc


def _validate_and_prepare_single(route_features: Mapping[str, Any]) -> pd.DataFrame:
    """
    Validate a single route feature mapping and return a 1-row DataFrame
    with columns ordered as in FEATURE_COLUMNS.
    """
    if not isinstance(route_features, Mapping):
        raise TypeError("route_features must be a mapping/dict of feature_name -> value")

    provided_keys = set(route_features.keys())
    expected_keys = set(FEATURE_COLUMNS)

    missing = expected_keys - provided_keys
    extra = provided_keys - expected_keys

    if missing:
        raise KeyError(
            "Missing required feature(s): " + ", ".join(sorted(missing))
        )
    if extra:
        raise KeyError(
            "Unexpected feature name(s): "
            + ", ".join(sorted(extra))
            + ". Expected: "
            + ", ".join(FEATURE_COLUMNS)
        )

    # Coerce to float and preserve order
    ordered_values = [
        _coerce_numeric(route_features[name], name) for name in FEATURE_COLUMNS
    ]

    df = pd.DataFrame([ordered_values], columns=list(FEATURE_COLUMNS))
    return df


def _validate_and_prepare_batch(routes: Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    """Validate a batch of routes and return a DataFrame for prediction."""
    if routes is None:
        raise TypeError("routes must be an iterable of dict-like feature mappings")

    rows: List[List[float]] = []
    for idx, route in enumerate(routes):
        if not isinstance(route, Mapping):
            raise TypeError(f"Each route must be a mapping/dict. Index {idx} is {type(route).__name__}.")

        provided_keys = set(route.keys())
        expected_keys = set(FEATURE_COLUMNS)
        missing = expected_keys - provided_keys
        extra = provided_keys - expected_keys
        if missing:
            raise KeyError(
                f"Route #{idx}: missing required feature(s): " + ", ".join(sorted(missing))
            )
        if extra:
            raise KeyError(
                f"Route #{idx}: unexpected feature name(s): "
                + ", ".join(sorted(extra))
                + ". Expected: "
                + ", ".join(FEATURE_COLUMNS)
            )

        rows.append([_coerce_numeric(route[name], name) for name in FEATURE_COLUMNS])

    df = pd.DataFrame(rows, columns=list(FEATURE_COLUMNS))
    return df


@lru_cache(maxsize=1)
def _load_model(model_path: str | Path | None = None):
    """
    Load and cache the trained model. Uses DEFAULT_MODEL_PATH when None.
    Returns the estimator that implements scikit-learn's predict API.
    """
    path = Path(model_path) if model_path is not None else DEFAULT_MODEL_PATH

    # Resolve relative to this file's repository root if necessary
    if not path.is_absolute():
        # Try relative to this file's directory, then ascend to project root
        this_dir = Path(__file__).resolve().parent
        candidate = (this_dir / path).resolve()
        if candidate.exists():
            path = candidate
        else:
            # Fallback to CWD relative (useful when running from project root)
            path = path.resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Trained model not found at: {path}. Ensure the file exists at 'models/travel_time_rf_model.pkl'."
        )

    logging.debug(f"Loading travel time model from: {path}")
    model = joblib.load(path)
    return model


def predict_travel_time(route_features: Mapping[str, Any], *, model_path: str | Path | None = None) -> float:
    """
    Predict travel time (in minutes) for a single route.

    Parameters
    ----------
    route_features: dict-like
        A mapping with the following keys:
        - distance_km
        - traffic_delay_min
        - weather_delay_min
        - risk_factor
    model_path: str | Path | None
        Optional override for the model's path. Defaults to `models/travel_time_rf_model.pkl`.

    Returns
    -------
    float
        Predicted travel time in minutes.
    """
    df = _validate_and_prepare_single(route_features)
    model = _load_model(model_path)

    # Align to model's expected features if available
    if hasattr(model, "feature_names_in_"):
        model_cols = list(getattr(model, "feature_names_in_"))
        # Warn if few overlaps (indicates training used many other columns)
        overlap = set(df.columns) & set(model_cols)
        if len(overlap) < len(df.columns):
            logging.warning(
                "Provided features %s do not fully match model features. Overlap: %s. Missing will be filled with 0.",
                list(df.columns), sorted(overlap),
            )

        # Add missing columns with zeros
        for col in model_cols:
            if col not in df.columns:
                df[col] = 0.0
        # Restrict to model columns and order them
        df = df[model_cols]

    logging.debug("Prepared features for single prediction (aligned):\n%s", df)
    pred = model.predict(df)
    # Ensure scalar float
    return float(pred[0])


def predict_travel_time_batch(routes: Iterable[Mapping[str, Any]], *, model_path: str | Path | None = None) -> List[float]:
    """
    Batch predict travel times (in minutes) for multiple routes.

    Parameters
    ----------
    routes: iterable of dict-like
        Each mapping must include the same keys as in single prediction.
    model_path: str | Path | None
        Optional override for the model's path.

    Returns
    -------
    list[float]
        Predicted travel times in minutes for each input route, in order.
    """
    df = _validate_and_prepare_batch(routes)
    model = _load_model(model_path)

    # Align to model's expected features if available
    if hasattr(model, "feature_names_in_"):
        model_cols = list(getattr(model, "feature_names_in_"))
        overlap = set(df.columns) & set(model_cols)
        if len(overlap) < len(df.columns):
            logging.warning(
                "Provided features %s do not fully match model features. Overlap: %s. Missing will be filled with 0.",
                list(df.columns), sorted(overlap),
            )
        for col in model_cols:
            if col not in df.columns:
                df[col] = 0.0
        df = df[model_cols]

    logging.debug("Prepared features for batch prediction (aligned):\n%s", df)
    preds = model.predict(df)
    return [float(x) for x in preds]


if __name__ == "__main__":
    # Basic logging setup for demonstration/debugging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    example_route = {
        "distance_km": 150.0,
        "traffic_delay_min": 20.0,
        "weather_delay_min": 10.0,
        "risk_factor": 0.15,
    }

    try:
        minutes = predict_travel_time(example_route)
        logging.info("Predicted travel time (single): %.2f minutes", minutes)

        batch_minutes = predict_travel_time_batch([
            example_route,
            {
                "distance_km": 80.0,
                "traffic_delay_min": 5.0,
                "weather_delay_min": 0.0,
                "risk_factor": 0.05,
            },
        ])
        logging.info("Predicted travel times (batch): %s", ", ".join(f"{m:.2f}" for m in batch_minutes))
    except Exception as e:
        logging.error("Prediction failed: %s", e)
