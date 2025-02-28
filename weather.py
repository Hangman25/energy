import requests
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import pytz
import pandas as pd
from taf import fetch_taf_data, convert_to_pei_time
from cloud import fetch_cloud_data

solar_data = pd.read_csv('csv/solar_2025.csv') 
solar_data['timestamp'] = pd.to_datetime(solar_data['timestamp'])

base = st.secrets["BASE_URL"]
location = st.secrets["LOCATION"]
token = st.secrets["TOKEN"]

def fetch_weather_data():
    url = f"{base}/{location}?token={token}&format=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("⚠ Failed to fetch weather data.")
    except Exception as e:
        st.error(f"⚠ Error fetching data: {e}")
    return {}

def get_weather_value(weather_data, key, default=None):
    if isinstance(weather_data, dict) and key in weather_data:
        value = weather_data[key]
        if isinstance(value, dict) and 'value' in value:
            return value['value']
        elif isinstance(value, (float, int)):
            return value
    return default

def get_cloud_coverage_metar(metar_data):
    cloud_map = {'SKC': 0.0, 'FEW': 17.5, 'SCT': 37.5, 'BKN': 67.5, 'OVC': 92.5, 'VV': 100.0}
    cloud_layers = []
    if 'clouds' in metar_data and isinstance(metar_data['clouds'], list):
        for cloud in metar_data['clouds']:
            cloud_type = cloud.get('type', '')
            cloud_layers.append(cloud_map.get(cloud_type, 0.0))
    return (
        cloud_layers[0] if len(cloud_layers) > 0 else 0.0,
        cloud_layers[1] if len(cloud_layers) > 1 else 0.0,
        cloud_layers[2] if len(cloud_layers) > 2 else 0.0
    )

def get_cloud_coverage_taf(forecast):
    cloud_map = {'SKC': 0.0, 'FEW': 17.5, 'SCT': 37.5, 'BKN': 67.5, 'OVC': 92.5, 'VV': 100.0}
    cloud_layers = []
    if 'clouds' in forecast and isinstance(forecast['clouds'], list):
        for cloud in forecast['clouds']:
            cloud_type = cloud.get('code', '')
            cloud_layers.append(cloud_map.get(cloud_type, 0.0))
    return (
        cloud_layers[0] if len(cloud_layers) > 0 else 0.0,
        cloud_layers[1] if len(cloud_layers) > 1 else 0.0,
        cloud_layers[2] if len(cloud_layers) > 2 else 0.0
    )

def get_solar_params(current_time):
    match = solar_data[(solar_data['timestamp'].dt.date == current_time.date()) &
                       (solar_data['timestamp'].dt.hour == current_time.hour)]
    if not match.empty:
        return (match['solar_elevationdegrees'].values[0],
                match['solar_azimuthdegrees'].values[0],
                match['solar_declinationdegrees'].values[0],
                match['hour_angledegrees'].values[0])
    else:
        return 0.0, 0.0, 0.0, 0.0

def extract_weather_features_for_hours():
    taf_data = fetch_taf_data()
    metar_data = fetch_weather_data()
    cloud_data = fetch_cloud_data()
    cloud_data['DATETIME'] = pd.to_datetime(cloud_data['DATETIME'], errors='coerce').dt.tz_localize('UTC').dt.tz_convert('America/Halifax')

    if taf_data is None and metar_data is None:
        return []

    features_list = []
    current_time = datetime.now(pytz.timezone("America/Halifax"))

    low_cloud, mid_cloud, high_cloud = get_cloud_coverage_metar(metar_data)
    solar_elevation, solar_azimuth, solar_declination, hour_angle = get_solar_params(current_time)

    base_features = {
        'temperature_celsius': get_weather_value(metar_data, 'temperature', 0.0),
        'humidity_percent': round(get_weather_value(metar_data, 'relative_humidity', 0.0) * 100),
        'wind_speed_kmph': get_weather_value(metar_data, 'wind_speed', 5) * 1.852,
        'wind_gust_kmph': get_weather_value(metar_data, 'wind_gust', 0) * 1.852,
        'wind_direction_degrees': get_weather_value(metar_data, 'wind_direction', 0.0),
        'visibility_meters_float': get_weather_value(metar_data, 'visibility', 10) * 1609.34,
        'altimeter_hpa': get_weather_value(metar_data, 'altimeter', 29.92) * 33.8639,
        'low_cloud_coverage': low_cloud,
        'mid_cloud_coverage': mid_cloud,
        'high_cloud_coverage': high_cloud,
        'solar_elevationdegrees': solar_elevation,
        'solar_azimuthdegrees': solar_azimuth,
        'solar_declinationdegrees': solar_declination,
        'hour_angledegrees': hour_angle,
        'timehr': current_time.hour,
        'tmaxGHI': 800.0
    }
    features_list.append(base_features)

    forecasts = taf_data.get('forecast', [])
    unique_forecasts = list(forecasts[:3])

    prev_features = base_features.copy()
    for i, forecast in enumerate(unique_forecasts, start=1):
        next_time = current_time + timedelta(hours=i)
        next_time = next_time.astimezone(pytz.timezone('America/Halifax'))

        low_cloud, mid_cloud, high_cloud = get_cloud_coverage_taf(forecast)
        wind_speed = forecast.get('wind', {}).get('speed_kph', prev_features['wind_speed_kmph'])
        wind_gust = forecast.get('wind', {}).get('gust_kph', prev_features['wind_gust_kmph'])
        wind_direction = forecast.get('wind', {}).get('degrees', prev_features['wind_direction_degrees'])
        visibility = forecast.get('visibility', {}).get('meters', prev_features['visibility_meters_float'])
        altimeter = prev_features['altimeter_hpa']

        closest_row = cloud_data.iloc[(cloud_data['DATETIME'] - next_time).abs().argsort()[:1]]
        temp = closest_row['TMP'].values[0] if not closest_row.empty else prev_features['temperature_celsius']
        humidity = closest_row['RH'].values[0] if not closest_row.empty else prev_features['humidity_percent']

        solar_elevation, solar_azimuth, solar_declination, hour_angle = get_solar_params(next_time)

        taf_features = {
            'temperature_celsius': temp,
            'humidity_percent': humidity,
            'wind_speed_kmph': wind_speed,
            'wind_gust_kmph': wind_gust,
            'wind_direction_degrees': wind_direction,
            'visibility_meters_float': visibility,
            'altimeter_hpa': altimeter,
            'low_cloud_coverage': low_cloud,
            'mid_cloud_coverage': mid_cloud,
            'high_cloud_coverage': high_cloud,
            'solar_elevationdegrees': solar_elevation,
            'solar_azimuthdegrees': solar_azimuth,
            'solar_declinationdegrees': solar_declination,
            'hour_angledegrees': hour_angle,
            'timehr': next_time.hour,
            'tmaxGHI': 800.0
        }
        features_list.append(taf_features)
        prev_features = taf_features

    return features_list
