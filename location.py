import streamlit as st
import pandas as pd

def show_location_predictions():
    """Displays location-based power predictions in a Streamlit application."""

    st.title("📍 Location-based Power Prediction")

    # Streamlit UI: File Uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        # Load DataFrame
        df = pd.read_csv(uploaded_file)

        # Drop Irrelevant Columns Efficiently
        columns_to_remove = [
            "temperature_celsius", "humidity_percent", "wind_speed_kmph",
            "wind_gust_kmph", "wind_direction_degrees", "visibility_meters_float",
            "altimeter_hpa", "low_cloud_coverage", "mid_cloud_coverage",
            "high_cloud_coverage", "solar_elevationdegrees", "solar_azimuthdegrees",
            "solar_declinationdegrees", "hour_angledegrees", "timehr", "tmaxGHI"
        ]
        df.drop(columns=[col for col in columns_to_remove if col in df.columns], inplace=True)

        # Ensure 'Predicted Power (kW)' Column Exists
        if "Predicted Power (kW)" not in df.columns:
            st.error("❌ The uploaded CSV does not contain the required 'Predicted Power (kW)' column.")
        else:
            # Convert Predicted Power to List
            preds_list = df["Predicted Power (kW)"].tolist()

            # Sidebar User Inputs for Power Calculation
            st.sidebar.header("Settings")
            slemonpark_capacity = st.sidebar.number_input("Slemonpark Capacity (kW)", value=12500)
            brackly_capacity = st.sidebar.number_input("Brackly Capacity (kW)", value=1000)
            loc = st.sidebar.text_input("Enter Location Name", value="Brackly")

            # Calculate Percentages for Location Power
            percent_slemonpark = [power / slemonpark_capacity for power in preds_list]
            percent_brackly = [power * brackly_capacity for power in percent_slemonpark]

            # Add New Column to DataFrame
            df[f'Predicted Power in {loc} (kW)'] = percent_brackly

            # Display Data
            st.success("✅ Data processed successfully!")
            st.dataframe(df)

            # Allow Download of Processed Data
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Processed CSV", data=csv, file_name="processed_location_data.csv", mime="text/csv")
    else:
        st.info("📂 Please upload a CSV file to proceed.")
