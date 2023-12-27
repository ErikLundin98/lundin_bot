import os
from typing import Any
from box import Box
from dotenv import load_dotenv
import yaml
from assistant.constants import HOME_LAT, HOME_LON
import requests
import pandas as pd
import datetime

from assistant.language_model.model import LanguageModel

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
    "spp": "percent_frozen_precipitation",  # -9 if none
    "pcat": "precipitation_type",
    "pmean": "mean_precipitation",
    "tcc_mean": "mean_cloud_coverage",
    "t": "temperature_celsius",
    "msl": "air_pressure",
    "vis": "horizontal_visiblity",
    "ws": "wind_speed_meters_per_second",
    "r": "relative_humidity_percent",
    "tstm": "thunder_probability",
    "gust": "wind_gust_speed_meters_per_second",
    "Wsymb2": "weather_symbol",
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

df = df[~df.name.isin(["lcc_mean", "mcc_mean", "hcc_mean", "wd", "pmax", "pmin", "pmedian"])]
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
weather = df.pivot(index="time", columns="name", values="values").reset_index()
datetimes = pd.to_datetime(weather["time"])
weather["date"] = datetimes.dt.date
weather["time"] = datetimes.dt.time


with open("config.yaml", "r") as file:
    config = Box(yaml.safe_load(file))

llm = LanguageModel(config)

system_prompt = f"""
You are a weather analyst who should formulate a weather sql query to answer the user's question. You have the following table
called "weather" at your disposal. Here is a sample of the table:

{weather.head()}

The column "precipitation_type" can be one of {", ".join(list(PRECIPITATION_CATEGORIES.values()))}

Note: When the user simply asks for the weather, it's most interesting to look at
* Temperature during the day
* If it will rain/snow/be clear
* Wind velocity
Your response should be a valid SQL query that can be used to fetch the data that answers the user's question.
No other columns than {weather.columns} are allowed.
The current date is {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
The forecast contains data for timestamps up until {weather.index.max()}

The SQL syntax should be supported by DuckDB. The only scalar functions you are allowed to use in the query are
 aggregate functions.
Only respond with a SQL query, nothing else.
"""
import duckdb
user_prompt = "Kan du beskriva dagens vädret i detalj för mig"
query = llm.answer_prompt(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    use_extra_instructions=False,
).content.replace("\n", " ")

print(query)

result = duckdb.query_df(df=weather, virtual_table_name="weather", sql_query=query).to_df()


system_prompt_with_table = f"""
You are a weather expert who should answer the user's question related to the weather in an easy 
to understand manner. You should use puns related to weather in your answer. 
You have the following data available to answer the question:

{result}

Answer the question in a short summary. 
If the result set is empty, it means thatyou cannot give a proper answer to the question
"""

answer = llm.answer_prompt(
    system_prompt=system_prompt_with_table,
    user_prompt=user_prompt,
).content

print(user_prompt)

print(result)
print(answer)
