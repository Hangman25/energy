import streamlit as st
import requests
from config import BASE_URL, LOCATION, TOKEN
from datetime import datetime
import pytz
from dateutil import parser


def fetch_metar_data():
    """Fetches raw METAR JSON data from the API."""
    url = f"{BASE_URL}/{LOCATION}?token={TOKEN}&format=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("⚠ Failed to fetch METAR data.")
            return {}
    except Exception as e:
        st.error(f"⚠ Error fetching METAR data: {e}")
        return {}

def safe_get(data, key, nested_key=None, default=0):
    """Safely retrieves values from nested dictionaries with a numeric-safe fallback."""
    value = data.get(key, default)
    if nested_key and isinstance(value, dict):
        value = value.get(nested_key, default)
    return value if value is not None else default

def convert_to_pei_time(utc_time_str):
    """Converts UTC time string to Charlottetown PEI time."""
    try:
        # Parse the UTC time string
        utc_time = parser.isoparse(utc_time_str)

        # Convert to PEI (Atlantic) time
        pei_tz = pytz.timezone("America/Halifax")
        pei_time = utc_time.astimezone(pei_tz)

        # Format the date and time
        return pei_time.strftime("%Y-%m-%d %I:%M %p")
    except Exception as e:
        return f"Unavailable"

def show_metar():
    """Displays selected weather details in a dashboard-like format."""
    # Fetch data
    data = fetch_metar_data()
    if not data:
        st.warning("No METAR data available.")
        return

    # Extract selected metrics
    temperature = safe_get(data, "temperature", "value")
    dewpoint_c = safe_get(data, "dewpoint", "value")
    humidity = round(safe_get(data, "relative_humidity") * 100, 1)
    wind_speed_mph = round(safe_get(data, "wind_speed", "value", 0) * 1.15078, 1)  # knots to mph
    wind_gust_mph = round(safe_get(data, "wind_gust", "value", 0) * 1.15078, 1)
    wind_direction = safe_get(data, "wind_direction", "value")
    visibility_meters = safe_get(data, "visibility", "value")
    altimeter_hpa = round(safe_get(data, "altimeter", "value", 1013.25) * 33.8639, 1)

    # Cloud coverage info
    clouds = safe_get(data, "clouds", default=[])
    low_cloud = next((c['type'] for c in clouds if c.get("altitude", 0) <= 2000), "None")
    mid_cloud = next((c['type'] for c in clouds if 2000 < c.get("altitude", 0) <= 6000), "None")
    high_cloud = next((c['type'] for c in clouds if c.get("altitude", 0) > 6000), "None")

    # Get API observation time and convert to PEI time
    api_time_utc = data.get("meta", {}).get("timestamp", "N/A")
    pei_time = convert_to_pei_time(api_time_utc)

    # Dashboard Header
    st.markdown("<h1 style='text-align: center; color: white; background-color: #1F2937; padding: 20px;'>🌤️ Real-Time Weather Dashboard (Valid 1 hr)</h1>", unsafe_allow_html=True)

    # Time and Location Info
    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.info(f"🗓️ **Date (PEI Time):** {pei_time.split(' ')[0] if pei_time != 'Unavailable' else 'Unavailable'}")
    with info_col2:
        st.info(f"🕒 **Time (PEI Time):** {pei_time.split(' ')[1] + ' ' + pei_time.split(' ')[2] if pei_time != 'Unavailable' else 'Unavailable'}")
    with info_col3:
        st.info(f"📍 **Location:** {data.get('station', LOCATION)}")

    # Weather Details (in 3 rows)
    st.markdown("---")

    # Row 1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🌡️ Temperature (°C)", value=temperature)
    with col2:
        st.metric(label="💦 Dew Point (°C)", value=dewpoint_c)
    with col3:
        st.metric(label="💧 Humidity (%)", value=humidity)

    # Row 2
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label="🌬️ Wind Speed (mph)", value=wind_speed_mph)
    with col5:
        st.metric(label="🌪️ Wind Gust (mph)", value=wind_gust_mph)
    with col6:
        st.metric(label="🧭 Wind Direction (°)", value=wind_direction)

    # Row 3
    col7, col8, col9 = st.columns(3)
    with col7:
        st.metric(label="👁️ Visibility (m)", value=visibility_meters)
    with col8:
        st.metric(label="🛬 Altimeter (hPa)", value=altimeter_hpa)
    with col9:
        st.metric(label="☁️ Low/Mid/High Cloud Coverage", value=f"{low_cloud}/{mid_cloud}/{high_cloud}")

    # Optional: Expand raw JSON data
    with st.expander("🔍 View Full METAR Report"):
        st.json(data, expanded=False)