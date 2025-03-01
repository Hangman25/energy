import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import StringIO

# API Endpoint
BASE_URL = "https://spotwx.io/api.php"

def fetch_cloud_data():
    """Fetches cloud/weather data from the SpotWX API (CSV format)."""
    params = {
        "key": st.secrets["API_KEY"],
        "lat": 46.4392,
        "lon": -63.8413,
        "model": "hrrr"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        if not response.text.strip():
            st.error("⚠ API returned an empty response.")
            return pd.DataFrame()

        # Convert CSV response to DataFrame
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        return df  # Return the DataFrame
    
    except requests.exceptions.RequestException as e:
        st.error(f"⚠ Error fetching cloud data: {e}")
        return pd.DataFrame()

def show_cloud():
    """Displays cloud/weather forecast in a structured and user-friendly format."""
    st.title("☁ Cloud & Weather Forecast")

    # Fetch cloud data
    df = fetch_cloud_data()

    if df.empty:
        st.warning("No cloud data available.")
        return

    # ✅ Define All Relevant Columns
    all_columns = [
        "DATETIME", "TMP", "DP", "RH", "WSPD", "WDIR", "GUST", "PRECIP_ttl", 
        "PRECIP_int", "RQP", "SQP", "FQP", "IQP", "CLOUD", "LCDC", "MCDC", 
        "HCDC", "HGT_CLOUDTOP", "HGT_CLOUDBASE"
    ]
    
    renamed_columns = {
        "DATETIME": "📅 Date & Time (UTC)",
        "TMP": "🌡 Temperature (°C)",
        "DP": "💨 Dew Point (°C)",
        "RH": "💧 Humidity (%)",
        "WSPD": "🌬 Wind Speed (km/h)",
        "WDIR": "🧭 Wind Direction (°)",
        "GUST": "💨 Wind Gust (km/h)",
        "PRECIP_ttl": "🌧 Total Precipitation (mm)",
        "PRECIP_int": "🌧 Precipitation Intensity (mm/hr)",
        "RQP": "🌧 Rain Probability (%)",
        "SQP": "🌧 Snow Probability (%)",
        "FQP": "🌧 Freezing Rain Probability (%)",
        "IQP": "🌧 Ice Pellets Probability (%)",
        "CLOUD": "☁ Avg Cloud Cover (%)",
        "LCDC": "☁ Low Cloud Cover (%)",
        "MCDC": "☁ Mid Cloud Cover (%)",
        "HCDC": "☁ High Cloud Cover (%)",
        "HGT_CLOUDTOP": "📏 Cloud Top Height (m)",
        "HGT_CLOUDBASE": "📏 Cloud Base Height (m)"
    }

   

    # ✅ Feature Selection for Graph (Moved Before Table)
    st.subheader("📊 Cloud Graph")
    available_features = list(df_filtered.columns)

   

    # ✅ Show Graph if Features are Selected
    if selected_features:
        plot_dynamic_graph(df_filtered, selected_features)

     # ✅ Allow Users to Select Which Columns to Display
    selected_columns = st.multiselect(
        "📋 Select Columns to Display in Table:",
        all_columns,
        default=["DATETIME", "TMP", "RH", "WSPD", "CLOUD"]
    )

    # ✅ Filter DataFrame Based on Selected Columns
    df_filtered = df[selected_columns].rename(columns=renamed_columns)

    # Convert wind speed & gust from knots to km/h
    if "🌬 Wind Speed (km/h)" in df_filtered.columns:
        df_filtered["🌬 Wind Speed (km/h)"] = df_filtered["🌬 Wind Speed (km/h)"] * 1.852

    if "💨 Wind Gust (km/h)" in df_filtered.columns:
        df_filtered["💨 Wind Gust (km/h)"] = df_filtered["💨 Wind Gust (km/h)"] * 1.852

    # ✅ Set "📅 Date & Time" as the Index if Selected
    if "📅 Date & Time (UTC)" in df_filtered.columns:
        df_filtered.set_index("📅 Date & Time (UTC)", inplace=True)

     # Multi-select for user to choose which features to plot
    selected_features = st.multiselect(
        "Select features to plot against Date & Time:",
        available_features,
        default=["☁ Avg Cloud Cover (%)"]
    )

    # Display Data Table (Moved Below Graph)
    with st.expander("🔍 View Full Cloud Forecast", expanded=True):
        st.data_editor(df_filtered, use_container_width=True, height=700)

def plot_dynamic_graph(df, selected_features):
    """Creates an interactive Plotly graph based on user-selected features."""
    st.subheader("📈 Interactive Weather Trends Over Time")

    # Convert index (Date & Time) to datetime format
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # Create Plotly figure
    fig = px.line(
        df,
        x=df.index,
        y=selected_features,
        title="Weather Trends Over Time",
        labels={"value": "Measurement", "index": "Date & Time (UTC)"},
        markers=True
    )

    # ✅ Add Interactive Features
    fig.update_layout(
        xaxis_title="Date & Time (UTC)",
        yaxis_title="Value",
        legend_title="Weather Variables",
        hovermode="x unified",
        template="plotly_white",
    )

    # ✅ Show the Plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)
