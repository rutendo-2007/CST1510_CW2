"""
fetch_data.py - Week 8: get data from an API and save it as DATA/raw.csv.

Run it:  python fetch_data.py
"""

from pathlib import Path

import pandas as pd
import requests

"""the code before the functions are the settings : the lines built from step 2 to 5 in the lab notebook"""

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"     # <- CHANGED to my choice from Step 1
PARAMS = {"format": "geojson", "minmagnitude": 2.5, "limit": 500}
RECORDS_KEY = "features"                 # the key that holds the list of records (None if the reply is already a list)
RENAME = {"properties_mag": "threat_mag",
    "properties_place": "target_zone",
    "properties_alert": "alert_status",
    "properties_time": "event_time",
    "properties_sig": "threat_level"
}
KEEP = ["target_zone", "threat_mag", "event_time", "depth_km", "threat_level"] #my columns
MUST_HAVE = ["target_zone", "threat_mag"]

RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


# ---- The functions ---


def get_data(url, params):
    """Ask the API for data. Returns the JSON reply, or None if something went wrong."""
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()          # turns 404, 500 ... into an error
        return response.json()
    except requests.RequestException as error:
        print("Could not get the data:", error)
        return None


def make_table(data, records_key):
    """Turn the JSON reply into a pandas table."""
    records = data[records_key] if records_key else data
    return pd.json_normalize(records, sep="_")      # nested {"a": {"b": 1}} becomes column a_b


def tidy_data(df):
    """Rename, keep and clean the columns."""
    df = df.rename(columns=RENAME)
    df["depth_km"] = df["geometry_coordinates"].apply(lambda coords: coords[2])#extracting the depth in km from geometry coordinates
    df["event_time"] = pd.to_datetime(df["event_time"], unit="ms").dt.strftime("%Y-%m-%d %H:%M:%S")#converting to date and time format
    df = df[KEEP]
    df = df.dropna(subset=MUST_HAVE)
    return df


def save_data(df, path):
    """Save the table as a CSV file."""
    path.parent.mkdir(exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    data = get_data(URL, PARAMS)
    if data is not None:
        table = make_table(data, RECORDS_KEY)
        table = tidy_data(table)
        print(table.head())
        save_data(table, RAW_FILE)
