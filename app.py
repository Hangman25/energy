import streamlit as st
import schedule
import time
from scripts.prediction import show_prediction
from scripts.about import show_about
from scripts.metar import show_metar
from scripts.taf import show_taf
from scripts.cloud import show_cloud
from scripts.solar import visualize_csv
from scripts.location import show_location_predictions
from scripts.send_email_job import send_email_job

st.set_page_config(layout="wide", page_title="🌤️ Energy Prediction Dashboard")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["About", "Prediction", "METAR", "TAF", "Cloud Forecast", "Solar Parameters", "Location"])

if page == "About":
    show_about()
elif page == "Prediction":
    show_prediction()
elif page == "METAR":
    show_metar()
elif page == "Cloud Forecast":
    show_cloud()
elif page == "TAF":
    show_taf()
elif page == "Solar Parameters":
    visualize_csv("csv/solar_2025.csv")
elif page == "Location":
    show_location_predictions()

schedule.every().day.at("7:01").do(send_email_job)
schedule.every().day.at("11:01").do(send_email_job)
schedule.every().day.at("15:01").do(send_email_job)

while True:
    schedule.run_pending()
    time.sleep(1)