import streamlit as st
import pandas as pd
from scripts.weather import extract_weather_features_for_hours
from scripts.model import load_model, predict_power
from io import BytesIO
from datetime import datetime
from scripts.csv_email import send_email


def send_email_job():
    """
    Sends email containing the upcoming 4-hour prediction.

    Returns
    -------
    None

    See Also
    --------
    This method is intended to be used as a scheduled job.
    Using schedule <https://github.com/dbader/schedule> package.
    """
    model, expected_features = load_model()
    features_list = extract_weather_features_for_hours()

    if not features_list:
        return

    predictions = []
    for idx, features in enumerate(features_list, start=1):
        features_df = pd.DataFrame([features])
        prediction = predict_power(model, expected_features, features_df)
        predictions.append({
            'Validity': f"{features['timehr']:02d}00 - {(features['timehr'] + 1) % 24:02d}00",
            'Predicted Power (kW)': round(prediction, 2),
            **features
        })

    combined_df = pd.DataFrame(predictions)
    combined_df = combined_df.drop(columns=['Hour'], errors='ignore')

    # Convert DataFrame to CSV and store in memory
    csv_buffer = BytesIO()
    filename = datetime.now().strftime("%Y-%m-%d") + "_4hr_Energy_Predictions.csv"
    combined_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    send_email(st.secrets["EMAIL_TO"], csv_buffer, filename)
