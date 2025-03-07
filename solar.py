import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime

def visualize_csv(file_name):
    try:
        # Load CSV
        df = pd.read_csv(file_name)

        # Convert 'timestamp' to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Sidebar: Select Time Range
        time_range = st.sidebar.selectbox("Select Time Range", 
                                          ["Daily", "Weekly", "Monthly", "Quarterly", "6 Months", "9 Months", "12 Months"], 
                                          index=0)  

        # Get Current Date
        today = datetime.datetime.today()

        # Year selection
        years = df["timestamp"].dt.year.unique()
        selected_year = st.sidebar.selectbox("Select Year", years, index=list(years).index(today.year))

        # Date range filtering
        start_date = pd.to_datetime(str(selected_year) + "-01-01")
        end_date = start_date + pd.DateOffset(years=1)
        title_text = f"Data shown for {selected_year}"

        # Filter Data Based on Selected Period
        df_filtered = df[(df["timestamp"] >= start_date) & (df["timestamp"] < end_date)]

        # Session State for Toggle Button
        if "view_mode" not in st.session_state:
            st.session_state.view_mode = "Graph"

        # Show Graph View
        if st.session_state.view_mode == "Graph":
            st.subheader(title_text)  # Dynamic title
            all_y_options = ["solar_azimuthdegrees", "solar_elevationdegrees", "solar_declinationdegrees", "hour_angledegrees", "tmaxGHI"]
            selected_y_axes = st.multiselect("Select Y-axis columns", all_y_options, default=["tmaxGHI"])

            primary_y = ["solar_azimuthdegrees"] if "solar_azimuthdegrees" in selected_y_axes else selected_y_axes
            secondary_y = [col for col in selected_y_axes if col != "solar_azimuthdegrees"] if "solar_azimuthdegrees" in selected_y_axes else []

            # Determine primary Y-axis label
            if "tmaxGHI" in primary_y and len(primary_y) == 1:
                primary_y_label = "Wh/m²"
            elif "tmaxGHI" in primary_y:
                primary_y_label = "Wh/m² & Degrees"
            else:
                primary_y_label = "Degree"

            secondary_y_label = "Degree" if secondary_y else None

            fig = go.Figure()
            for col in primary_y:
                fig.add_trace(go.Scatter(x=df_filtered["timestamp"], y=df_filtered[col], mode='lines', name=col, yaxis="y1"))
            for col in secondary_y:
                fig.add_trace(go.Scatter(x=df_filtered["timestamp"], y=df_filtered[col], mode='lines', name=col, yaxis="y2"))

            fig.update_layout(
                xaxis=dict(title="Time Stamp"),
                yaxis=dict(title=primary_y_label, side="left", showgrid=False),
                yaxis2=dict(title=secondary_y_label, overlaying="y", side="right", showgrid=False) if secondary_y else None,
                legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5)
            )

            st.plotly_chart(fig)
            if st.button("To CSV"):
                st.session_state.view_mode = "CSV"
                st.rerun()

    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
