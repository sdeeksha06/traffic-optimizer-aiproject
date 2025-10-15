# src/train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from math import sqrt

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "travel_time_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "travel_time_rf_model.pkl")

# --- Ensure model directory exists ---
if not os.path.exists(MODEL_DIR):
    try:
        os.makedirs(MODEL_DIR)
        print(f"Created folder: {MODEL_DIR}")
    except PermissionError:
        print(f"Permission denied: Cannot create {MODEL_DIR}. Please check folder permissions.")
        exit(1)

# src/train_model.py

import sys
import os
from typing import List

# Guard imports so we can give a helpful message when dependencies are missing.
try:
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    import joblib
except Exception as e:
    print("Error importing required Python packages:", e)
    print("Please install the requirements for the ml component. Example:")
    print("    pip install -r ../requirements.txt")
    print("Or install directly: pip install pandas scikit-learn joblib")
    sys.exit(1)


# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "travel_time_dataset.csv"))
MODEL_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "models"))
MODEL_PATH = os.path.join(MODEL_DIR, "travel_time_rf_model.pkl")


def load_dataset(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at {path}")
    return pd.read_csv(path)


def prepare_features_target(df: pd.DataFrame, target_col: str = "travel_time_minutes"):
    if target_col not in df.columns:
        raise KeyError(f"Expected target column '{target_col}' not found in dataset. Columns: {df.columns.tolist()}")
    feature_cols: List[str] = [c for c in df.columns if c != target_col]
    if len(feature_cols) == 0:
        raise ValueError("No feature columns found in dataset.")
    X = df[feature_cols]
    y = df[target_col]
    return X, y


def ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except PermissionError:
        print(f"Permission denied: Cannot create {path}. Please check folder permissions.")
        sys.exit(1)


def train_and_save_model(X, y, model_path: str):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")

    print("Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)
    # rmse = mean_squared_error(y_test, y_pred, squared=False)
    rmse = sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print(f"Model evaluation:\nRMSE: {rmse:.2f} minutes\nR^2 Score: {r2:.3f}")

    joblib.dump(rf_model, model_path)
    print(f"Trained model saved at: {model_path}")


def main():
    ensure_dir(MODEL_DIR)

    try:
        df = load_dataset(DATA_PATH)
        print("Dataset loaded successfully.")
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print("Failed to load dataset:", e)
        sys.exit(1)

    try:
        X, y = prepare_features_target(df)
    except Exception as e:
        print(e)
        sys.exit(1)

    train_and_save_model(X, y, MODEL_PATH)


if __name__ == "__main__":
    main()
