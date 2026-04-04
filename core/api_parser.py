import os
import sys


base_path = os.path.dirname(os.path.dirname(__file__))

if base_path not in sys.path:
    sys.path.append(base_path)

import pandas as pd
import numpy as np
from data.data_class.weatherData import *
from data.weather import get_area_weather

def parse_api(lat, long, start, end):
    weather_data = get_area_weather(lat, long, start, end)

    data_list = []

    for area, weather_list in weather_data.items():
        for weather in weather_list:
            data = pd.DataFrame({
                'ds': [weather.date],
                'temp': [np.mean([weather.temperature_min, weather.temperature_max])],
                'humidity': [weather.humidity],
                'precip': [0.0],
                'snow': [0.0],
                'windspeed': [weather.wind_speed],
                'preciptype_rain': [0.0],
                'preciptype_snow': [0.0]
            })

            data['ds'] = pd.to_datetime(data['ds'])

            data_list.append(data)
        
    return data_list

# date_viitor = pd.DataFrame({
#         'ds': ['2026-05-10'],    
#         'temp': [22.5], 
#         'humidity': [50.0],
#         'precip': [0.0],
#         'snow': [0.0],
#         'windspeed': [15.2],
#         'preciptype_rain': [0.0], 
#         'preciptype_snow': [0.0]
#         })

if __name__ == "__main__":
    parse_api(45.6427, 25.5887, "2026-04-01", "2026-04-05")