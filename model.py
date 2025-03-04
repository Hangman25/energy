import joblib
import xgboost as xgb
import pandas as pd

def load_model():
    """Loads the trained XGBoost model and retrieves expected feature names."""
    model = joblib.load("model.pkl")  # Directly loads an XGBoost Booster

    # ✅ Directly extract feature names
    expected_features = model.feature_names

    return model, expected_features  # Ensure two values are returned

def predict_power(model, expected_features, features_df):
    """Runs predictions using the XGBoost model."""

    # ✅ Ensure the DataFrame matches the model's expected feature order
    features_df = features_df[expected_features]

    # Check where tmaxGHI is 0 and initialize prediction results
    if 'tmaxGHI' in features_df.columns:
        mask = features_df['tmaxGHI'] == 0
    else:
        mask = pd.Series(False, index=features_df.index)  # Default to False if column is missing

    # Convert to DMatrix
    dmatrix_input = xgb.DMatrix(features_df, feature_names=expected_features)

    # Predict power output
    predictions = model.predict(dmatrix_input)

    # Apply mask: If tmaxGHI is 0, force prediction to be 0
    predictions[mask] = 0.0

    # Ensure non-negative output
    return predictions.clip(min=0)
