import joblib
import xgboost as xgb

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

    # Convert to DMatrix
    dmatrix_input = xgb.DMatrix(features_df, feature_names=expected_features)

    # Predict and return result
    prediction = model.predict(dmatrix_input)
    return max(0, prediction[0])  # Ensure power output is non-negative
