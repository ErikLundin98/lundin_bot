import datetime
from typing import Any
import duckdb
import pandas as pd
import requests
from assistant.constants import HOME_LAT, HOME_LON
from assistant.language_model.model import LanguageModel
from assistant.language_model.utils import render_prompt
import os
import logging

NAME_MAPPING = {
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
ZERO_TO_EIGHT_SCALE = {i: str(i / 8 * 100) + "%" for i in range(0, 9, 1)}
WEATHER_SYMBOLS = {
    1: "Clear sky",
    2: "Nearly clear sky",
    3: "Variable cloudiness",
    4: "Halfclear sky",
    5: "Cloudy sky",
    6: "Overcast",
    7: "Fog",
    8: "Light rain showers",
    9: "Moderate rain showers",
    10: "Heavy rain showers",
    11: "Thunderstorm",
    12: "Light sleet showers",
    13: "Moderate sleet showers",
    14: "Heavy sleet showers",
    15: "Light snow showers",
    16: "Moderate snow showers",
    17: "Heavy snow showers",
    18: "Light rain",
    19: "Moderate rain",
    20: "Heavy rain",
    21: "Thunder",
    22: "Light sleet",
    23: "Moderate sleet",
    24: "Heavy sleet",
    25: "Light snowfall",
    26: "Moderate snowfall",
    27: "Heavy snowfall",
}


_log = logging.getLogger(__name__)
NAME = "get_weather"


def main(
    query: str,
    llm: LanguageModel,
) -> str:
    """Get weather info"""
    weather = get_weather_data()
    query_prompt = render_prompt(
        prompt_name=NAME,
        prompt_key="query",
        data_sample=weather.head(),
        precipitation_categories=list(PRECIPITATION_CATEGORIES.values()),
        columns=weather.columns,
        current_datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        max_datetime=str(weather["date"].max()) + " " + str(weather["time"].max()),
    )
    query = llm.answer_prompt(
        system_prompt=query_prompt,
        user_prompt=query,
        use_extra_instructions=False,
    ).content

    _log.info(f"Using query {query} on weather data.")
    result = duckdb.query_df(
        df=weather, virtual_table_name="weather", sql_query=query
    ).to_df()
    weather_prompt = render_prompt(
        prompt_name=NAME,
        weather_data=result,
        query_used=query
    )
    answer = llm.answer_prompt(
        system_prompt=weather_prompt,
        user_prompt=query,
    ).content
    _log.info(f"Returning weather answer '{answer}'")

    return answer


def get_weather_data() -> pd.DataFrame:
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
    df = df[
        ~df.name.isin(
            ["lcc_mean", "mcc_mean", "hcc_mean", "wd", "pmax", "pmin", "pmedian"]
        )
    ]
    df["values"] = df[["name", "values"]].apply(
        lambda data: map_value(name=data["name"], value=data["values"]),
        axis=1,
    )
    df["name"] = df["name"].apply(lambda name: NAME_MAPPING[name])
    weather = df.pivot(index="time", columns="name", values="values").reset_index()
    datetimes = pd.to_datetime(weather["time"])
    weather["date"] = datetimes.dt.date
    weather["time"] = datetimes.dt.time

    return weather


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
