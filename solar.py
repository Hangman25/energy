import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime

def visualize_csv(file_name):
    """
    Function to load a CSV file and create an interactive time series visualization in Streamlit.

    Features:
    - Toggle button to switch between Graph and CSV.
    - Button dynamically updates label ("To CSV" / "To Graph").
    - Solar Azimuth is default and prioritized on the primary Y-axis.
    - Users can add/remove parameters dynamically.
    - If Solar Azimuth is removed, other parameters move to the primary Y-axis.
    - If Solar Azimuth is added back, it moves to primary Y-axis, and others shift to secondary.
    - Users can select daily, weekly, monthly, etc.
    - Dynamic title showing selected date range.
    - **Legend aligned horizontally (left to right) above the graph**.
    """
    try:
        # Load CSV
        df = pd.read_csv(file_name)

        # Convert 'timestamp' to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Sidebar: Select Time Range
        time_range = st.sidebar.selectbox("Select Time Range", 
                                          ["Daily", "Weekly", "Monthly", "Quarterly", "6 Months", "9 Months", "12 Months"], 
                                          index=0)  # Default is Daily

        # Get Current Date
        today = datetime.datetime.today()

        # Determine the selected date range
        if time_range == "Daily":
            years = df["timestamp"].dt.year.unique()
            selected_year = st.sidebar.selectbox("Select Year", years, index=list(years).index(today.year))

            months = df[df["timestamp"].dt.year == selected_year]["timestamp"].dt.month.unique()
            selected_month = st.sidebar.selectbox("Select Month", months, format_func=lambda x: datetime.date(1900, x, 1).strftime('%B'))

            days = df[(df["timestamp"].dt.year == selected_year) & (df["timestamp"].dt.month == selected_month)]["timestamp"].dt.day.unique()
            selected_day = st.sidebar.selectbox("Select Day", days)

            start_date = datetime.datetime(selected_year, selected_month, selected_day)
            end_date = start_date + pd.DateOffset(days=1)
            title_text = f"Data shown for {start_date.strftime('%B %d, %Y')}"

        elif time_range == "Weekly":
            years = df["timestamp"].dt.year.unique()
            selected_year = st.sidebar.selectbox("Select Year", years, index=list(years).index(today.year))

            months = df[df["timestamp"].dt.year == selected_year]["timestamp"].dt.month.unique()
            selected_month = st.sidebar.selectbox("Select Month", months, format_func=lambda x: datetime.date(1900, x, 1).strftime('%B'))

            weeks = df[(df["timestamp"].dt.year == selected_year) & (df["timestamp"].dt.month == selected_month)]["timestamp"].dt.isocalendar().week.unique()
            selected_week = st.sidebar.selectbox("Select Week (Number)", weeks)

            start_date = df[(df["timestamp"].dt.year == selected_year) & 
                            (df["timestamp"].dt.month == selected_month) & 
                            (df["timestamp"].dt.isocalendar().week == selected_week)]["timestamp"].min()
            end_date = start_date + pd.DateOffset(weeks=1)
            title_text = f"Data shown for Week {selected_week}, {selected_year}"

        elif time_range == "Monthly":
            months = df["timestamp"].dt.strftime("%B %Y").unique()
            default_month = today.strftime("%B %Y") if today.strftime("%B %Y") in months else months[0]
            selected_period = st.sidebar.selectbox("Select Month", months, index=list(months).index(default_month))
            start_date = pd.to_datetime(selected_period)
            end_date = start_date + pd.DateOffset(months=1)
            title_text = f"Data shown for {selected_period}"

        elif time_range == "Quarterly":
            df["quarter"] = df["timestamp"].dt.to_period("Q").astype(str)
            quarters = df["quarter"].unique()
            selected_period = st.sidebar.selectbox("Select Quarter", quarters)
            start_date = pd.to_datetime(selected_period[:4] + "-" + str((int(selected_period[-1]) - 1) * 3 + 1))
            end_date = start_date + pd.DateOffset(months=3)
            title_text = f"Data shown for Quarter {selected_period[-1]}, {selected_period[:4]}"

        elif time_range == "6 Months":
            df["half_year"] = df["timestamp"].dt.to_period("2Q").astype(str)
            half_years = df["half_year"].unique()
            selected_period = st.sidebar.selectbox("Select 6-Month Period", half_years)
            start_date = pd.to_datetime(selected_period[:4] + "-01") if "Q1" in selected_period else pd.to_datetime(selected_period[:4] + "-07")
            end_date = start_date + pd.DateOffset(months=6)
            title_text = f"Data shown for 6-Month Period {selected_period[:4]} ({'Jan-Jun' if 'Q1' in selected_period else 'Jul-Dec'})"

        elif time_range == "9 Months":
            df["three_quarters"] = df["timestamp"].dt.to_period("3Q").astype(str)
            three_quarters = df["three_quarters"].unique()
            selected_period = st.sidebar.selectbox("Select 9-Month Period", three_quarters)
            start_date = pd.to_datetime(selected_period[:4] + "-01")
            end_date = start_date + pd.DateOffset(months=9)
            title_text = f"Data shown for 9-Month Period {selected_period[:4]}"

        else:  # 12 Months
            years = df["timestamp"].dt.year.unique()
            selected_period = st.sidebar.selectbox("Select Year", years)
            start_date = pd.to_datetime(str(selected_period) + "-01-01")
            end_date = start_date + pd.DateOffset(years=1)
            title_text = f"Data shown for {selected_period}"

        # Filter Data Based on Selected Period
        df_filtered = df[(df["timestamp"] >= start_date) & (df["timestamp"] < end_date)]

        # Session State for Toggle Button
        if "view_mode" not in st.session_state:
            st.session_state.view_mode = "Graph"

        # Show Graph View
        if st.session_state.view_mode == "Graph":
            st.subheader(title_text)  # Dynamic title
            all_y_options = ["solar_azimuthdegrees", "solar_elevationdegrees", "solar_declinationdegrees", "hour_angledegrees","tmaxGHI"]
            selected_y_axes = st.multiselect("Select Y-axis columns", all_y_options, default=["solar_azimuthdegrees"])

            primary_y = ["solar_azimuthdegrees"] if "solar_azimuthdegrees" in selected_y_axes else selected_y_axes
            secondary_y = [col for col in selected_y_axes if col != "solar_azimuthdegrees"] if "solar_azimuthdegrees" in selected_y_axes else []

            fig = go.Figure()
            for col in primary_y:
                fig.add_trace(go.Scatter(x=df_filtered["timestamp"], y=df_filtered[col], mode='lines', name=col, yaxis="y1"))
            for col in secondary_y:
                fig.add_trace(go.Scatter(x=df_filtered["timestamp"], y=df_filtered[col], mode='lines', name=col, yaxis="y2"))

            fig.update_layout(
                xaxis=dict(title="Time Stamp"),
                yaxis=dict(title="Degree", side="left", showgrid=False),
                yaxis2=dict(title="Degree", overlaying="y", side="right", showgrid=False) if secondary_y else None,
                legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5)  # Moves legend above the graph horizontally
            )

            st.plotly_chart(fig)
            if st.button("To CSV"):
                st.session_state.view_mode = "CSV"
                st.rerun()

        # Show CSV View
        else:
            st.subheader(title_text)  # Dynamic title
            df_filtered.set_index("timestamp", inplace=True)
            st.dataframe(df_filtered, use_container_width=True)

            if st.button("To Graph"):
                st.session_state.view_mode = "Graph"
                st.rerun()
                
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
