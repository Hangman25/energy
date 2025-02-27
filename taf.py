import streamlit as st
import requests
from datetime import datetime
import pytz
from dateutil import parser
from dotenv import dotenv_values
config = dotenv_values(".env")

url2 = config["TAF_URL"]
loc = config["LOC"]
key = config["KEY"]

def fetch_taf_data():
    """Fetches TAF data from the CheckWX API."""
    url = f"{url2}/{loc}/decoded"
    headers = {"X-API-Key": key}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                return data['data'][0]
            else:
                st.error("No TAF data found for CYYG.")
                return None
        else:
            st.error(f"⚠ Failed to fetch TAF data. HTTP Status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"⚠ Error fetching TAF data: {e}")
        return None

def convert_to_pei_time(utc_time_str):
    """Converts UTC time string to PEI local time datetime object."""
    utc_time = parser.parse(utc_time_str)
    pei_tz = pytz.timezone("America/Halifax")
    pei_time = utc_time.astimezone(pei_tz)
    return pei_time  # Return as datetime object, not string

def translate_weather_code(code):
    """Translate METAR/TAF weather codes into human-readable text."""
    code_map = {
        "-SN": "Light Snow",
        "+SN": "Heavy Snow",
        "SN": "Snow",
        "-RA": "Light Rain",
        "+RA": "Heavy Rain",
        "RA": "Rain",
        "-FZRA": "Light Freezing Rain",
        "+FZRA": "Heavy Freezing Rain",
        "FZRA": "Freezing Rain",
        "-SNPL": "Light Snow Pellets",
        "BR": "Mist",
        "FG": "Fog",
        "TS": "Thunderstorm",
        "DZ": "Drizzle",
    }
    return code_map.get(code, code)

def show_taf():
    """Displays TAF data in a dashboard format with forecast timings."""
    # Fetch TAF data
    taf_data = fetch_taf_data()
    if not taf_data:
        return

    # Extract primary information
    location = taf_data.get('station', {}).get('location', 'Unknown Location')
    raw_text = taf_data.get('raw_text', 'N/A')
    issued_time = taf_data.get('timestamp', {}).get('issued', 'N/A')
    valid_from = taf_data.get('timestamp', {}).get('from', 'N/A')
    valid_to = taf_data.get('timestamp', {}).get('to', 'N/A')

    # Convert times to PEI time
    issued_time_pei = convert_to_pei_time(issued_time)
    valid_from_pei = convert_to_pei_time(valid_from)
    valid_to_pei = convert_to_pei_time(valid_to)

    # Get current PEI time
    pei_tz = pytz.timezone("America/Halifax")
    current_time = datetime.now(pei_tz).strftime("%Y-%m-%d %I:%M %p")

    # Forecast details
    forecasts = taf_data.get('forecast', [])

    # Dashboard Header
    st.markdown("<h1 style='text-align: center; color: white; background-color: #1F2937; padding: 20px;'>🌤️ TAF Weather Forecast</h1>", unsafe_allow_html=True)

    # Time and Location Info
    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.info(f"🕓 **Current Time (PEI):** {current_time}")
    with info_col2:
        st.info(f"🗓️ **Issued Date (PEI Time):** {issued_time_pei}")
    with info_col3:
        st.info(f"📍 **Location:** {location}")

    # Weather Details (Forecast Timeline)
    st.markdown("---")

    if forecasts:
        for idx, forecast in enumerate(forecasts):
            # Extract timing info for each forecast
            forecast_from = forecast.get('timestamp', {}).get('from', 'N/A')
            forecast_to = forecast.get('timestamp', {}).get('to', 'N/A')
            forecast_from_pei = convert_to_pei_time(forecast_from)
            forecast_to_pei = convert_to_pei_time(forecast_to)

            # Create a collapsible section for each forecast
            with st.expander(f"🕒 Forecast #{idx+1} | Valid: {forecast_from_pei} → {forecast_to_pei}", expanded=(idx == 0)):
                wind = forecast.get('wind', {})
                visibility = forecast.get('visibility', {})
                clouds = forecast.get('clouds', [])

                # Weather Description
                weather_description = ', '.join(translate_weather_code(code.get('text', 'Unknown')) for code in clouds) or "Clear"

                # Display weather conditions
                st.write(f"**🌤️ Weather:** {weather_description}")

                # Row 1: Wind & Visibility
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="🌬️ Wind Speed (mph)", value=wind.get('speed_mph', 'N/A'))
                with col2:
                    st.metric(label="🌪️ Wind Gust (mph)", value=wind.get('gust_mph', 'N/A'))
                with col3:
                    st.metric(label="🧭 Wind Direction (°)", value=wind.get('degrees', 'N/A'))

                # Row 2: Visibility & Forecast Type
                col4, col5 = st.columns(2)
                with col4:
                    st.metric(label="👁️ Visibility (m)", value=visibility.get('meters_float', 'N/A'))
                with col5:
                    forecast_type = forecast.get('change', {}).get('indicator', {}).get('text', 'Standard')
                    st.metric(label="📍 Forecast Type", value=forecast_type)

                # Row 3: Cloud Coverage Details
                cloud_descriptions = []
                for cloud in clouds:
                    coverage = cloud.get("text", "Unknown")
                    altitude = cloud.get("base_feet_agl", "N/A")
                    cloud_descriptions.append(f"{coverage} at {altitude} ft AGL")

                cloud_cover = ", ".join(cloud_descriptions) if cloud_descriptions else "Clear Skies"
                st.write(f"**☁️ Cloud Coverage:** {cloud_cover}")

            st.markdown("---")

    # Raw TAF Text
    st.subheader("📄 Raw TAF Report")
    st.code(raw_text, language="plaintext")

    # Optional: Expand raw JSON data
    with st.expander("🔍 View Full TAF Report"):
        st.json(taf_data, expanded=False)