import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
from weather import extract_weather_features_for_hours
from model import load_model, predict_power
from io import BytesIO
import plotly.express as px
from datetime import datetime
from csv_email import send_email

def plot_interactive_graphs(data):
    # Graph 1: Predicted Power (Interactive)
    fig_power = px.line(data, x='Validity', y='Predicted Power (kW)', title='Predicted Power vs Time',
                        markers=True, labels={'Predicted Power (kW)': 'Power (kW)'})
    fig_power.update_xaxes(tickangle=45)
    st.plotly_chart(fig_power, use_container_width=True)

    # Weather parameters selection using multiselect
    weather_columns = ['low_cloud_coverage', 'temperature_celsius', 'humidity_percent', 
                       'wind_speed_kmph', 'wind_gust_kmph', 'visibility_meters_float']

    selected_features = st.multiselect(
        "🌦️ **Select Weather Parameters to Display in the Weather Graph:**",
        options=weather_columns,
        default=['low_cloud_coverage']
    )

    if selected_features:
        fig_weather = px.line(data, x='Validity', y=selected_features, title='Weather Parameters vs Time',
                              markers=True)
        fig_weather.update_xaxes(tickangle=45)
        fig_weather.update_yaxes(title='Values')
        st.plotly_chart(fig_weather, use_container_width=True)
    else:
        st.warning("Please select at least one weather parameter to display.")

def show_prediction():
    model, expected_features = load_model()
    features_list = extract_weather_features_for_hours()

    if not features_list:
        st.error("No weather data available for predictions.")
        return

    predictions = []
    for idx, features in enumerate(features_list, start=1):
        features_df = pd.DataFrame([features])
        prediction = predict_power(model, expected_features, features_df)
        predictions.append({
            'Validity': f"{features['timehr']:02d}00 - {(features['timehr']+1)%24:02d}00",
            'Predicted Power (kW)': round(prediction, 2),
            **features
        })

    combined_df = pd.DataFrame(predictions)
    combined_df = combined_df.drop(columns=['Hour'], errors='ignore')

    #st.success("All predictions displayed below!")
    st.write("### Next 4 Hour Predictions:")

    st.data_editor(
        combined_df,
        hide_index=True,
        column_config={
            "Validity": st.column_config.Column(width="medium", pinned="left")
        }
    )

    # Convert DataFrame to CSV and store in memory
    csv_buffer = BytesIO()
    filename = datetime.now().strftime("%Y-%m-%d") + "_4hr_Energy_Predictions.csv"
    combined_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Column Buttons
    left, middle, right = st.columns(3)
    if left.button("📧 Send Email", use_container_width=True):
        csv_buffer.seek(0)
        send_email(st.secrets["EMAIL_TO"], csv_buffer, filename)
        left.markdown("Email Sent.")

    if middle.download_button(label="💾 Download Locally",
                              data=csv_buffer,
                              file_name=filename,
                              mime="text/csv",
                              use_container_width=True):
        middle.markdown("File Downloaded.")

    if right.button("Extra button", icon=":material/mood:", use_container_width=True):
        right.markdown("You clicked the Material button.")

    # Plot interactive graphs
    st.write("### Prediction Graphs:")
    plot_interactive_graphs(combined_df)
