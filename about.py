import streamlit as st

def show_about():
    st.title("About CIRRUS")

    st.markdown(
        """
        ## CIRRUS - Cloud-based Intelligent Resource for Renewable Utility and Solar Prediction
        
        **CIRRUS** is a solar energy prediction model that uses real-time METAR and forecased TAF-weather data from Charlotetown Airport
        to estimate the hourly solar power output for Slemon Park, Summerside, PE. It integrates weather station 
        data from Environment Canada and advanced machine learning model to provide 4-Hr solar power prediction.

        ### Key Features:
        - **Real-time Weather Data**: Fetches METAR and TAF data to incorporate dynamic environmental conditions.
        - **Machine Learning Predictions**: Uses an optimized XGBoost model for accurate solar power forecasts.
        - **Cloud Coverage Integration**: Accounts for low, mid, and high-level clouds affecting solar radiation.
        - **Solar Position Calculations**: Computes solar elevation and azimuth angles for better prediction accuracy.

        """
    )
    
    st.markdown(
         """### What is on: """
    )

    with st.expander("Predictions Page?"):
          st.markdown(
               """
                - **4-Hour Solar Energy Prediction**: This page displays a CSV file containing four hours of solar energy predictions, starting from the time the website is loaded.  
                - **METAR**: The first predicted solar energy value is based on the current METAR input, along with solar parameters such as *Solar Elevation*, *Solar Azimuth*, etc.  
                - **TAF**: The following three rows are predicted using the forecasted TAF and the corresponding solar parameters for each hour.  
                - **Handling Missing Values**: If any information is missing in the TAF, the previous values from METAR are used to fill in the gaps.  
                - **Assumptions**: Since the altimeter is only present in METAR (measured at the current time), it is assumed to remain constant for subsequent hours during the predictions.  
                
               """
          )
    
    with st.expander("METAR Page?"):
         st.markdown(
              '''
                - **What is METAR?**: METAR is a standardized format for reporting weather information. It is primarily used by aircraft pilots and meteorologists, who analyze aggregated METAR data to aid in weather forecasting.  
                - **Validity**: Since a METAR report is based on current weather conditions, it is only valid for one hour.  
                - **Location**: This program uses a predefined location (Charlottetown, PE) and retrieves the METAR report from the area's airport.  

              '''
         )
    
    with st.expander("TAF Page?"):
         st.markdown(
              """
              - Add more  
              """
         )
    with st.expander ("Solar Page?"):
         st.markdown(
              """
                - **Solar Elevation**: Sun's height above the horizon. Measured in degrees.
                - **Solar Azimuthd**: Sun's direction along the horizon. Measured in degrees.
                - **Solar Declination**: Sun's angle relative to the Earth's equatorial plane. Measured in degrees.
                - **Hour Angle: Sun's position relative to solar noon. Measured in degrees.
              """
         )

    st.markdown (
        """
        ---
        *© Developed by Yuvraj Gill for Design 2025. All rights reserved.*
        """
    )      
