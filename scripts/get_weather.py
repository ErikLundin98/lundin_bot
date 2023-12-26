import os
from typing import Any
from dotenv import load_dotenv
from assistant.constants import HOME_LAT, HOME_LON
import requests
import pandas as pd

load_dotenv()

lat = round(float(os.getenv(HOME_LAT)), 6)
lon = round(float(os.getenv(HOME_LON)), 6)
url = f"http://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"

response = requests.get(url).json()
time_series = response["timeSeries"]

data = []
for entry in time_series:
    for param in entry["parameters"]:
        data.append(
            {
                "time": entry["validTime"],
            }
            | param
        )

df = pd.DataFrame(data)
df["values"] = df["values"].apply(lambda value_list: value_list[0])

name_mapping = {
    "spp": "Percent of precipitation in frozen form",  # -9 if none
    "pcat": "Precipitation category",
    "pmin": "Minimum precipitation intensity",
    "pmean": "Mean precipitation intensity",
    "pmax": "Maximum precipitation intensity",
    "pmedian": "Median precipitation intensity",
    "tcc_mean": "Mean cloud coverage",
    "lcc_mean": "Mean value of low level cloud cover",
    "mcc_mean": "Mean value of medium level cloud cover",
    "hcc_mean": "Mean value of high level cloud cover",
    "t": "Air temperature",
    "msl": "Air pressure",
    "vis": "Horizontal visibility",
    "wd": "Wind direction",
    "ws": "Wind speed",
    "r": "Relative humidity",
    "tstm": "Thunder probability",
    "gust": "Wind gust speed",
    "Wsymb2": "Weather symbol",
}
PRECIPITATION_CATEGORIES = {
    0: "No precipitation",
    1: "Snow",
    2: "Snow and rain",
    3: "Rain",
    4: "Drizzle",
    5: "Freezing rain",
    6: "Freezing drizzle",
}
ZERO_TO_EIGHT_SCALE = {i: str(i/8*100) + "%" for i in range(0, 9, 1)}
WEATHER_SYMBOLS = {
    1:	"Clear sky",
    2:	"Nearly clear sky",
    3:	"Variable cloudiness",
    4:	"Halfclear sky",
    5:	"Cloudy sky",
    6:	"Overcast",
    7:	"Fog",
    8:	"Light rain showers",
    9:	"Moderate rain showers",
    10:	"Heavy rain showers",
    11:	"Thunderstorm",
    12: "Light sleet showers",
    13:	"Moderate sleet showers",
    14:	"Heavy sleet showers",
    15:	"Light snow showers",
    16:	"Moderate snow showers",
    17:	"Heavy snow showers",
    18:	"Light rain",
    19:	"Moderate rain",
    20:	"Heavy rain",
    21:	"Thunder",
    22:	"Light sleet",
    23:	"Moderate sleet",
    24:	"Heavy sleet",
    25:	"Light snowfall",
    26:	"Moderate snowfall",
    27:	"Heavy snowfall",
}
def map_value(name: str, value: Any) -> Any:
    """Map values to something more sensible based on name."""
    match name:
        case "spp":
            return max(value, 0)
        case "pcat":
            value_cat = int(value)
            return PRECIPITATION_CATEGORIES[value_cat]
        case "pmin":
            return value
        case "pmean":
            return value
        case "pmax":
            return value
        case "pmedian": 
            return value
        case "tcc_mean":
            return ZERO_TO_EIGHT_SCALE[int(value)]
        case "lcc_mean":
            return ZERO_TO_EIGHT_SCALE[int(value)]
        case "mcc_mean":
            return ZERO_TO_EIGHT_SCALE[int(value)]
        case "hcc_mean":
            return ZERO_TO_EIGHT_SCALE[int(value)]
        case "t":
            return value
        case "msl":
            return value
        case "vis":
            return value
        case "wd":
            return value
        case "ws": 
            return value
        case "r": 
            return value
        case "tstm":
            return value
        case "gust":
            return value
        case "Wsymb2":
            return WEATHER_SYMBOLS[value]
        case _:
            raise ValueError()

df["values"] = df[["name", "values"]].apply(
    lambda data: map_value(name=data["name"], value=data["values"]),
    axis=1,
)
df["name"] = df["name"].apply(lambda name: name_mapping[name])
df["name"] = df["name"] + " (" + df["unit"] + ")"
df = df.pivot(index="time", columns="name", values="values")
print(df)