import joblib
import xgboost as xgb

def load_model():
    """Loads the trained XGBoost model and retrieves expected feature names."""
    model = joblib.load("model.pkl")  # Load model

    # Extract feature names
    expected_features = model.feature_names

    return model, expected_features  # Ensure two values are returned

def predict_power(model, expected_features, features_df):
    """Runs predictions using the XGBoost model."""

    # Ensure the DataFrame matches the model's expected feature order
    features_df = features_df[expected_features]

    # Check if tmaxGHI is 0
    if 'tmaxGHI' in features_df.columns and features_df['tmaxGHI'].iloc[0] == 0:
        return 0.0  # Ensure output is 0 when tmaxGHI is 0

    # Convert to DMatrix
    dmatrix_input = xgb.DMatrix(features_df, feature_names=expected_features)

    # Predict and return result
    prediction = model.predict(dmatrix_input)
    return max(0, prediction[0])  # Ensure power output is non-negative
