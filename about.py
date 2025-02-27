import streamlit as st

def show_about():
    st.title("About CIRRUS")

    st.markdown(
        """
        ## CIRRUS - Cloud-based Intelligent Resource for Renewable Utility and Solar Prediction
        
        **CIRRUS** is a solar energy prediction model that uses real-time METAR-weather data from Charlotetown Airport
        to estimate the hourly solar power output for a given location. It integrates weather station 
        data and advanced machine learning models to enhance renewable energy efficiency.

        ### Key Features:
        - **Real-time Weather Data**: Fetches METAR data to incorporate dynamic environmental conditions.
        - **Machine Learning Predictions**: Uses an optimized XGBoost model for accurate solar power forecasts.
        - **Cloud Coverage Integration**: Accounts for low, mid, and high-level clouds affecting solar radiation.
        - **Solar Position Calculations**: Computes solar elevation and azimuth angles for better prediction accuracy.

        ---
        *© Developed by Yuvraj Gill for Design 2025. All rights reserved.*
        """
    )
